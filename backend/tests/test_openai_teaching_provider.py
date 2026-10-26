import json

import httpx
import pytest

from app.models.learning import LessonGenerationRequest, LessonQuestionRequest
from app.services.mock_teaching_provider import MockTeachingProvider
from app.services.openai_teaching_provider import OpenAITeachingProvider
from app.services.teaching_engine import (
    ProviderOutputError,
    TeachingEngine,
    create_teaching_engine,
    teaching_engine,
)
from app.services.teaching_provider import (
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
)


def generation_request() -> LessonGenerationRequest:
    return LessonGenerationRequest(
        topic="Bayes' theorem",
        subject="mathematics",
        learner_level="intermediate",
        learning_objective="Interpret conditional probability",
        preferred_explanation_style="worked numerical examples",
    )


def question_request(
    with_context: bool = True,
) -> LessonQuestionRequest:
    context = (
        {
            "lesson_title": "Conditional probability",
            "learning_objective": "Interpret conditional probability",
            "current_step": {
                "step_id": "step-2",
                "title": "Update a probability",
                "explanation": "Revise an estimate after new evidence.",
                "key_concepts": ["prior", "evidence", "posterior"],
            },
        }
        if with_context
        else None
    )
    return LessonQuestionRequest(
        question="What does the new evidence change?",
        topic="Bayes' theorem",
        learner_level="intermediate",
        preferred_explanation_style="worked numerical examples",
        lesson_context=context,
    )


def provider_with_response(
    response_content: str,
    captured_requests: list[httpx.Request] | None = None,
) -> OpenAITeachingProvider:
    def handle_request(request: httpx.Request) -> httpx.Response:
        if captured_requests is not None:
            captured_requests.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": response_content}},
                ],
            },
        )

    return OpenAITeachingProvider(
        api_key="test-only-key",
        transport=httpx.MockTransport(handle_request),
    )


def generated_lesson_content() -> str:
    output = MockTeachingProvider().generate_lesson(generation_request())
    output["generation_status"] = "generated"
    output["message"] = "This response is verified and researched."
    event = output["steps"][0]["visualization_events"][0]
    event["parameters"] = [
        {"key": "focus", "value": "topic"},
        {"key": "progress", "value": 2},
    ]
    event["expected_state"] = [
        {"key": "highlighted", "value": True},
        {"key": "caption", "value": "Bayes' theorem"},
    ]
    return json.dumps(output)


def _assert_strict_objects_are_closed(schema: object) -> None:
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            assert schema.get("additionalProperties") is False
            assert set(schema.get("required", [])) == set(
                schema.get("properties", {})
            )
        assert not isinstance(schema.get("additionalProperties"), dict)
        for value in schema.values():
            _assert_strict_objects_are_closed(value)
    elif isinstance(schema, list):
        for value in schema:
            _assert_strict_objects_are_closed(value)


def test_openai_provider_requests_strict_lesson_schema_and_validates_output():
    captured_requests: list[httpx.Request] = []
    provider = provider_with_response(
        generated_lesson_content(),
        captured_requests,
    )

    lesson = TeachingEngine(provider).generate_lesson(generation_request())

    assert lesson.generation_status == "generated"
    assert lesson.research_status == "not_researched"
    assert "not independently verified" in lesson.message
    assert lesson.topic.category == "mathematics"
    assert lesson.steps[0].visualization_events[0].event_type == "highlight"
    assert all(not step.references for step in lesson.steps)
    assert lesson.steps[0].visualization_events[0].parameters == {
        "focus": "topic",
        "progress": 2,
    }
    assert lesson.steps[0].visualization_events[0].expected_state == {
        "highlighted": True,
        "caption": "Bayes' theorem",
    }
    request = captured_requests[0]
    assert request.headers["Authorization"] == "Bearer test-only-key"
    payload = json.loads(request.content)
    assert payload["model"] == "gpt-4o-mini"
    assert payload["response_format"]["type"] == "json_schema"
    assert payload["response_format"]["json_schema"]["strict"] is True
    strict_schema = payload["response_format"]["json_schema"]["schema"]
    _assert_strict_objects_are_closed(strict_schema)
    event_schema = strict_schema["$defs"]["VisualizationEvent"]
    assert event_schema["properties"]["parameters"]["type"] == "array"
    expected_state_object = event_schema["properties"]["expected_state"]["anyOf"][0]
    assert expected_state_object["type"] == "array"
    assert event_schema["properties"]["parameters"]["items"]["required"] == [
        "key",
        "value",
    ]
    assert event_schema["properties"]["parameters"]["items"][
        "additionalProperties"
    ] is False
    assert "substantive, step-by-step" in payload["messages"][0]["content"]
    user_content = json.loads(payload["messages"][1]["content"])
    assert user_content["topic"] == "Bayes' theorem"
    assert user_content["learning_objective"] == (
        "Interpret conditional probability"
    )
    assert user_content["preferred_explanation_style"] == (
        "worked numerical examples"
    )
    assert "Do not invent citations" in payload["messages"][0]["content"]


def test_openai_provider_supplies_question_context_but_does_not_claim_sources():
    answer = {
        "status": "generated",
        "answer": (
            "In the supplied step, evidence updates the earlier estimate. "
            "The lesson context does not provide a numerical example."
        ),
        "disclaimer": (
            "Model-generated answer; not independently verified or researched."
        ),
        "references": [],
    }
    captured_requests: list[httpx.Request] = []
    provider = provider_with_response(json.dumps(answer), captured_requests)

    result = TeachingEngine(provider).answer_question(question_request())

    assert result.status == "generated"
    assert result.references == []
    assert "not independently verified" in result.disclaimer
    payload = json.loads(captured_requests[0].content)
    user_content = json.loads(payload["messages"][1]["content"])
    assert user_content["lesson_context"]["current_step"]["step_id"] == "step-2"
    assert "when it is present" in payload["messages"][0]["content"]


def test_question_prompt_distinguishes_absent_lesson_context():
    captured_requests: list[httpx.Request] = []
    answer = {
        "status": "generated",
        "answer": "A general explanation of the topic.",
        "disclaimer": "Model-generated; not independently verified.",
        "references": [],
    }
    provider = provider_with_response(json.dumps(answer), captured_requests)

    TeachingEngine(provider).answer_question(question_request(with_context=False))

    payload = json.loads(captured_requests[0].content)
    user_content = json.loads(payload["messages"][1]["content"])
    assert user_content["lesson_context"] is None
    assert "context that is absent" in payload["messages"][0]["content"]


def test_openai_malformed_structured_output_is_rejected_by_engine():
    provider = provider_with_response('{"lesson_id": "incomplete"}')

    with pytest.raises(ProviderOutputError, match="invalid lesson"):
        TeachingEngine(provider).generate_lesson(generation_request())


@pytest.mark.parametrize(
    "response_body",
    [
        {"choices": [{"message": {"content": "{not valid JSON"}}]},
        {"unexpected": []},
        {"choices": []},
        {"choices": [{"message": {"content": None}}]},
    ],
)
def test_invalid_json_and_malformed_response_envelopes_are_sanitized(
    response_body: dict[str, object],
):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=response_body)
    )
    provider = OpenAITeachingProvider(
        api_key="test-only-key",
        transport=transport,
    )

    with pytest.raises(ProviderResponseError):
        provider.generate_lesson(generation_request())


@pytest.mark.parametrize(
    ("status_code", "exception_type"),
    [
        (429, ProviderRateLimitError),
        (500, ProviderResponseError),
    ],
)
def test_provider_http_errors_are_sanitized(status_code, exception_type):
    secret_response = "provider error with a private token"
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status_code, text=secret_response)
    )
    provider = OpenAITeachingProvider(
        api_key="test-only-key",
        transport=transport,
    )

    with pytest.raises(exception_type) as error:
        provider.generate_lesson(generation_request())

    assert secret_response not in str(error.value)
    assert "test-only-key" not in str(error.value)


def test_provider_timeout_is_sanitized():
    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("private timeout detail", request=request)

    provider = OpenAITeachingProvider(
        api_key="test-only-key",
        transport=httpx.MockTransport(timeout),
    )

    with pytest.raises(ProviderTimeoutError) as error:
        provider.generate_lesson(generation_request())

    assert "private timeout detail" not in str(error.value)
    assert "test-only-key" not in str(error.value)


def test_missing_provider_key_is_reported_without_network_access():
    provider = OpenAITeachingProvider(
        api_key=None,
        transport=httpx.MockTransport(
            lambda request: pytest.fail("request must not be sent")
        ),
    )

    with pytest.raises(ProviderConfigurationError):
        provider.generate_lesson(generation_request())


def test_provider_factory_defaults_to_mock(monkeypatch):
    monkeypatch.delenv("TEACHING_PROVIDER", raising=False)
    engine = create_teaching_engine()

    assert engine.provider.generation_status == "mock"


def test_provider_factory_selects_openai_from_backend_environment(monkeypatch):
    monkeypatch.setenv("TEACHING_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    engine = create_teaching_engine()

    assert engine.provider.generation_status == "generated"
    assert isinstance(engine.provider, OpenAITeachingProvider)
    assert engine.provider.api_key == "test-only-key"
    assert engine.provider.model == "test-model"


def test_remote_http_provider_endpoint_is_rejected_before_sending_key():
    provider = OpenAITeachingProvider(
        api_key="test-only-key",
        base_url="http://provider.example/v1",
        transport=httpx.MockTransport(
            lambda request: pytest.fail("request must not be sent")
        ),
    )

    with pytest.raises(ProviderConfigurationError):
        provider.generate_lesson(generation_request())


@pytest.mark.parametrize(
    ("provider_error", "expected_status"),
    [
        (ProviderRateLimitError("private provider detail"), 429),
        (ProviderTimeoutError("private provider detail"), 504),
        (ProviderResponseError("private provider detail"), 502),
        (ProviderConfigurationError("private provider detail"), 503),
    ],
)
def test_api_maps_provider_failures_to_sanitized_http_errors(
    client,
    monkeypatch,
    provider_error,
    expected_status,
):
    class FailingProvider:
        generation_status = "generated"

        def generate_lesson(self, request):
            raise provider_error

        def answer_question(self, request):
            raise provider_error

    monkeypatch.setattr(teaching_engine, "provider", FailingProvider())

    response = client.post(
        "/api/v1/teaching/lessons",
        json=generation_request().model_dump(),
    )

    assert response.status_code == expected_status
    assert "private provider detail" not in response.text

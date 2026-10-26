import pytest

from app.models.learning import (
    LessonGenerationRequest,
    LessonQuestionRequest,
)
from app.services.teaching_engine import teaching_engine


def lesson_request(
    topic: str = "A learner-selected topic",
    subject: str | None = None,
) -> LessonGenerationRequest:
    return LessonGenerationRequest(
        topic=topic,
        learner_level="beginner",
        learning_objective="Explain the central idea",
        preferred_explanation_style="clear examples",
        subject=subject,
    )


@pytest.mark.parametrize(
    ("topic", "subject"),
    [
        ("Variables and values", "programming"),
        ("Fractions", "mathematics"),
        ("Service boundaries", "system design"),
        ("Phishing awareness", "cybersecurity"),
        ("The water cycle", "science"),
        ("A historical trade route", "history"),
        ("Small business planning", "business"),
    ],
)
def test_mock_provider_generates_generic_structured_lessons(client, topic, subject):
    response = client.post(
        "/api/v1/teaching/lessons",
        json={
            "topic": topic,
            "subject": subject,
            "learner_level": "beginner",
            "learning_objective": "Explain the central idea",
            "preferred_explanation_style": "clear examples",
        },
    )

    assert response.status_code == 200
    lesson = response.json()
    assert lesson["topic"]["title"] == topic
    assert lesson["topic"]["category"] == subject
    assert lesson["objectives"] == ["Explain the central idea"]
    assert [step["title"] for step in lesson["steps"]] == [
        "Build a mental model",
        "Apply the idea",
    ]
    assert lesson["generation_status"] == "mock"
    assert lesson["research_status"] == "not_researched"
    assert "not AI-generated" in lesson["message"]
    assert lesson["steps"][0]["visualization_events"][0]["event_type"] == "highlight"
    assert lesson["steps"][1]["knowledge_checks"][0]["feedback_guidance"]
    assert lesson["steps"][0]["code_snippets"] == []
    assert lesson["steps"][0]["formulas"] == []
    assert lesson["steps"][0]["references"] == []


def test_mock_generation_is_deterministic():
    first = teaching_engine.generate_lesson(lesson_request())
    second = teaching_engine.generate_lesson(lesson_request())

    assert first.model_dump() == second.model_dump()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "topic": "   ",
            "learner_level": "beginner",
            "learning_objective": "Understand it",
            "preferred_explanation_style": "examples",
        },
        {
            "topic": "Fractions",
            "learner_level": "beginner",
            "learning_objective": "Understand them",
            "preferred_explanation_style": "examples",
            "api_key": "must-not-be-accepted",
        },
    ],
)
def test_generation_rejects_invalid_or_secret_bearing_requests(client, payload):
    response = client.post("/api/v1/teaching/lessons", json=payload)

    assert response.status_code == 422


def test_generation_rejects_oversized_inputs(client):
    response = client.post(
        "/api/v1/teaching/lessons",
        json={
            "topic": "x" * 201,
            "learner_level": "beginner",
            "learning_objective": "Understand the topic",
            "preferred_explanation_style": "examples",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "invalid_output",
    [
        None,
        {"lesson_id": "incomplete"},
        {
            "lesson_id": "invalid-parameters",
            "title": "Invalid",
            "topic": {
                "topic_id": "invalid",
                "title": "Invalid",
                "description": "Invalid provider output.",
                "category": "Test",
                "difficulty": "beginner",
                "goal": "Test validation",
            },
            "objectives": ["Test"],
            "steps": [
                {
                    "step_id": "step",
                    "title": "Step",
                    "visualization_events": [
                        {
                            "event_id": "unsafe-parameters",
                            "event_type": "set_state",
                            "parameters": {"state": {"execute": "code"}},
                        }
                    ],
                }
            ],
            "estimated_duration_minutes": 10,
            "teaching_strategy": "test",
            "research_status": "not_researched",
            "generation_status": "mock",
            "message": "test",
        },
        {
            "lesson_id": "invalid-event",
            "title": "Invalid",
            "topic": {
                "topic_id": "invalid",
                "title": "Invalid",
                "description": "Invalid provider output.",
                "category": "Test",
                "difficulty": "beginner",
                "goal": "Test validation",
            },
            "objectives": ["Test"],
            "steps": [
                {
                    "step_id": "step",
                    "title": "Step",
                    "visualization_events": [
                        {
                            "event_id": "unsafe",
                            "event_type": "execute_javascript",
                        }
                    ],
                }
            ],
            "estimated_duration_minutes": 10,
            "teaching_strategy": "test",
            "research_status": "not_researched",
            "generation_status": "mock",
            "message": "test",
        },
    ],
)
def test_malformed_provider_output_returns_sanitized_502(
    client,
    monkeypatch,
    invalid_output,
):
    class MalformedProvider:
        generation_status = "mock"

        def generate_lesson(self, request):
            return invalid_output

        def answer_question(self, request):
            return invalid_output

    monkeypatch.setattr(teaching_engine, "provider", MalformedProvider())
    response = client.post(
        "/api/v1/teaching/lessons",
        json=lesson_request().model_dump(),
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Teaching provider returned an invalid lesson response."
    }


def test_provider_cannot_claim_research_or_add_unverified_references(
    client,
    monkeypatch,
):
    class UnverifiedProvider:
        def __init__(self, provider):
            self.provider = provider
            self.generation_status = provider.generation_status

        def generate_lesson(self, request):
            return _unverified_lesson_output(
                self.provider.generate_lesson(request)
            )

        def answer_question(self, request):
            return self.provider.answer_question(request)

    monkeypatch.setattr(
        teaching_engine,
        "provider",
        UnverifiedProvider(teaching_engine.provider),
    )

    response = client.post(
        "/api/v1/teaching/lessons",
        json=lesson_request().model_dump(),
    )

    assert response.status_code == 502
    assert "invalid lesson response" in response.json()["detail"]


def _unverified_lesson_output(output: dict[str, object]) -> dict[str, object]:
    output["steps"][0]["references"] = [
        {
            "title": "Unverified source",
            "url": "https://example.invalid/source",
        }
    ]
    return output


def test_question_endpoint_returns_explicit_mock_answer(client):
    response = client.post(
        "/api/v1/teaching/questions",
        json={
            "question": "How does this idea apply to my example?",
            "topic": "A learner-selected topic",
            "learner_level": "beginner",
            "preferred_explanation_style": "an analogy",
            "lesson_context": {
                "lesson_title": "Learning about a learner-selected topic",
                "learning_objective": "Explain the central idea",
                "current_step": {
                    "step_id": "step-one",
                    "title": "Build a mental model",
                    "explanation": "Start from the stated objective.",
                },
            },
        },
    )

    assert response.status_code == 200
    answer = response.json()
    assert answer["status"] == "mock"
    assert "not generated through AI reasoning" in answer["disclaimer"]
    assert "not researched" in answer["disclaimer"]
    assert "Learning about a learner-selected topic" in answer["answer"]
    assert "does not interpret the provided lesson context" in answer["answer"]
    assert answer["references"] == []


def test_question_endpoint_rejects_invalid_and_secret_bearing_requests(client):
    missing_fields = client.post(
        "/api/v1/teaching/questions",
        json={"question": "Explain this"},
    )
    secret_field = client.post(
        "/api/v1/teaching/questions",
        json={
            "question": "Explain this",
            "topic": "Mathematics",
            "api_key": "must-not-be-accepted",
        },
    )

    assert missing_fields.status_code == 422
    assert secret_field.status_code == 422


def test_question_endpoint_rejects_oversized_nested_lesson_context(client):
    response = client.post(
        "/api/v1/teaching/questions",
        json={
            "question": "Explain this step",
            "topic": "Mathematics",
            "lesson_context": {
                "current_step": {
                    "step_id": "step-one",
                    "title": "Large step",
                    "explanation": "x" * 2001,
                }
            },
        },
    )

    assert response.status_code == 422


def test_question_endpoint_rejects_oversized_lesson_context_concepts(client):
    response = client.post(
        "/api/v1/teaching/questions",
        json={
            "question": "Explain this step",
            "topic": "Mathematics",
            "lesson_context": {
                "current_step": {
                    "step_id": "step-one",
                    "title": "Step",
                    "key_concepts": ["x" * 201],
                }
            },
        },
    )

    assert response.status_code == 422


def test_malformed_question_provider_output_returns_sanitized_502(
    client,
    monkeypatch,
):
    class MalformedProvider:
        generation_status = "mock"

        def generate_lesson(self, request):
            return {}

        def answer_question(self, request):
            return {"status": "invented"}

    monkeypatch.setattr(teaching_engine, "provider", MalformedProvider())
    response = client.post(
        "/api/v1/teaching/questions",
        json={"question": "Why?", "topic": "Algebra"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Teaching provider returned an invalid answer response."
    }


def test_question_provider_cannot_return_unverified_sources(client, monkeypatch):
    class UnverifiedProvider:
        generation_status = "mock"

        def generate_lesson(self, request):
            return {}

        def answer_question(self, request):
            return {
                "status": "mock",
                "answer": "An answer",
                "disclaimer": "A disclaimer",
                "references": [
                    {
                        "title": "Invented",
                        "url": "https://example.invalid",
                    }
                ],
            }

    monkeypatch.setattr(teaching_engine, "provider", UnverifiedProvider())
    response = client.post(
        "/api/v1/teaching/questions",
        json={"question": "Why?", "topic": "History"},
    )

    assert response.status_code == 502

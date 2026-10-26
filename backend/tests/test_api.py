from app.data.demo_lessons import DEMONSTRATION_LESSONS
from app.models.learning import (
    AssessmentAnswerKey,
    LearningTopic,
    TeachingStep,
)
from app.services.assessment import evaluate_answer


def test_health_response_is_preserved(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "application": "LearnSphere AI",
    }


def test_topic_catalog_is_non_exhaustive_and_covers_three_subjects(client):
    response = client.get("/api/v1/topics")

    assert response.status_code == 200
    body = response.json()
    assert body["examples_are_exhaustive"] is False
    assert {topic["topic_id"] for topic in body["demonstration_topics"]} == {
        "python-for-loops",
        "web-application-architecture",
        "meta-business-model",
    }


def test_learning_plan_accepts_learner_defined_topic(client):
    response = client.post(
        "/api/v1/learning-plans",
        json={
            "topic": "How coral reefs support marine life",
            "current_knowledge_level": "beginner",
            "learning_goal": "Understand reef ecosystems",
            "preferred_teaching_style": "diagrams and examples",
            "duration_minutes": 25,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["topic"]["title"] == "How coral reefs support marine life"
    assert body["estimated_duration_minutes"] == 25
    assert body["generation_status"] == "not_configured"
    assert "No AI-generated" in body["message"]
    assert len(body["steps"]) == 1


def test_learning_plan_validation_rejects_missing_goal(client):
    response = client.post(
        "/api/v1/learning-plans",
        json={
            "topic": "Algebra",
            "current_knowledge_level": "beginner",
        },
    )

    assert response.status_code == 422


def test_learning_plan_validation_rejects_unreasonable_duration(client):
    response = client.post(
        "/api/v1/learning-plans",
        json={
            "topic": "Algebra",
            "current_knowledge_level": "beginner",
            "learning_goal": "Solve linear equations",
            "duration_minutes": 0,
        },
    )

    assert response.status_code == 422


def test_learning_plan_validation_rejects_whitespace_only_topic(client):
    response = client.post(
        "/api/v1/learning-plans",
        json={
            "topic": "   ",
            "current_knowledge_level": "beginner",
            "learning_goal": "Understand the topic",
        },
    )

    assert response.status_code == 422


def test_demonstration_lessons_support_different_subject_shapes(client):
    for lesson_id, expected_title in (
        ("python-for-loops", "Understanding Python for loops"),
        (
            "web-application-architecture",
            "Understanding a web application's architecture",
        ),
        ("meta-business-model", "Understanding Meta's business model"),
    ):
        response = client.get(f"/api/v1/lessons/{lesson_id}")
        assert response.status_code == 200
        assert response.json()["title"] == expected_title
        assert response.json()["generation_status"] == "demonstration"

    python_lesson = client.get("/api/v1/lessons/python-for-loops").json()
    architecture_lesson = client.get(
        "/api/v1/lessons/web-application-architecture"
    ).json()
    meta_lesson = client.get("/api/v1/lessons/meta-business-model").json()
    assert python_lesson["steps"][1]["code_snippets"]
    assert architecture_lesson["steps"][0]["diagrams"]
    assert not architecture_lesson["steps"][0]["code_snippets"]
    assert meta_lesson["research_status"] == "not_researched"
    assert not meta_lesson["steps"][0]["code_snippets"]


def test_python_lesson_contains_ordered_animation_and_code_output(client):
    lesson = client.get("/api/v1/lessons/python-for-loops").json()
    steps = lesson["steps"]

    assert [step["step_id"] for step in steps] == [
        "loop-analogy",
        "loop-code-trace",
        "loop-check",
    ]
    assert steps[1]["code_snippets"][0]["expected_output"].count(
        "Delivering to"
    ) == 3
    assert steps[1]["visualization_events"][0]["code_line_numbers"] == [2, 3]


def test_architecture_visualization_references_valid_components(client):
    lesson = client.get(
        "/api/v1/lessons/web-application-architecture"
    ).json()
    step = lesson["steps"][0]
    diagram = step["diagrams"][0]
    component_ids = {component["component_id"] for component in diagram["components"]}

    for relationship in diagram["relationships"]:
        assert relationship["source_component_id"] in component_ids
        assert relationship["target_component_id"] in component_ids
    for event in step["visualization_events"]:
        assert set(event["target_ids"]).issubset(component_ids)


def test_meta_demo_is_qualified_and_has_no_fabricated_references(client):
    lesson = client.get("/api/v1/lessons/meta-business-model").json()

    assert lesson["research_status"] == "not_researched"
    assert "No live research was conducted" in lesson["message"]
    assert lesson["steps"][0]["references"] == []
    assert lesson["steps"][0]["visualization_events"][0]["parameters"][
        "illustrative_only"
    ] is True


def test_lesson_step_retrieval_returns_stable_step_identifier(client):
    response = client.get("/api/v1/lessons/python-for-loops/steps/2")

    assert response.status_code == 200
    assert response.json()["lesson_id"] == "python-for-loops"
    assert response.json()["step_number"] == 2
    assert response.json()["step"]["step_id"] == "loop-code-trace"


def test_nonexistent_lesson_and_step_return_404(client):
    assert client.get("/api/v1/lessons/missing-lesson").status_code == 404
    assert (
        client.get("/api/v1/lessons/python-for-loops/steps/99").status_code
        == 404
    )


def test_session_can_be_created_from_demo_lesson(client):
    response = client.post(
        "/api/v1/learning-sessions",
        json={"lesson_id": "python-for-loops"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == "lesson"
    assert body["current_step_id"] == "loop-analogy"
    assert body["current_step_number"] == 1


def test_session_can_be_created_from_valid_plan(client):
    plan = client.post(
        "/api/v1/learning-plans",
        json={
            "topic": "Photosynthesis",
            "current_knowledge_level": "beginner",
            "learning_goal": "Describe how plants use light",
        },
    ).json()

    response = client.post(
        "/api/v1/learning-sessions",
        json={"plan": plan},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == "learning_plan"
    assert body["plan_id"] == plan["plan_id"]
    assert body["current_step_id"] == plan["steps"][0]["step_id"]


def test_session_creation_requires_exactly_one_source(client):
    assert client.post("/api/v1/learning-sessions", json={}).status_code == 422
    assert (
        client.post(
            "/api/v1/learning-sessions",
            json={
                "lesson_id": "python-for-loops",
                "plan": {
                    "plan_id": "plan",
                    "topic": {},
                    "objectives": [],
                    "steps": [],
                    "estimated_duration_minutes": 10,
                    "teaching_strategy": "demo",
                    "generation_status": "demonstration",
                    "message": "demo",
                },
            },
        ).status_code
        == 422
    )


def test_unknown_lesson_cannot_create_session(client):
    response = client.post(
        "/api/v1/learning-sessions",
        json={"lesson_id": "unknown"},
    )

    assert response.status_code == 404


def test_session_question_returns_explicit_not_configured_response(client):
    session = client.post(
        "/api/v1/learning-sessions",
        json={"lesson_id": "python-for-loops"},
    ).json()

    response = client.post(
        f"/api/v1/learning-sessions/{session['session_id']}/questions",
        json={
            "question": "Why does the loop visit every house?",
            "topic": "Python loops",
            "step_id": "loop-code-trace",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "not_configured"
    assert response.json()["answer"] is None
    assert "No answer was generated" in response.json()["message"]


def test_question_rejects_step_outside_the_session(client):
    session = client.post(
        "/api/v1/learning-sessions",
        json={"lesson_id": "python-for-loops"},
    ).json()
    response = client.post(
        f"/api/v1/learning-sessions/{session['session_id']}/questions",
        json={
            "question": "Explain the database diagram",
            "topic": "System design",
            "step_id": "architecture-components",
        },
    )

    assert response.status_code == 404


def test_invalid_session_returns_404(client):
    response = client.post(
        "/api/v1/learning-sessions/unknown-session/questions",
        json={"question": "Explain this", "topic": "Algebra"},
    )

    assert response.status_code == 404


def test_question_validation_rejects_empty_fields(client):
    session = client.post(
        "/api/v1/learning-sessions",
        json={"lesson_id": "python-for-loops"},
    ).json()

    response = client.post(
        f"/api/v1/learning-sessions/{session['session_id']}/questions",
        json={"question": "", "topic": ""},
    )

    assert response.status_code == 422


def test_question_validation_rejects_whitespace_only_context(client):
    session = client.post(
        "/api/v1/learning-sessions",
        json={"lesson_id": "python-for-loops"},
    ).json()
    response = client.post(
        f"/api/v1/learning-sessions/{session['session_id']}/questions",
        json={"question": "Why? ", "topic": "   "},
    )

    assert response.status_code == 422


def test_assessment_evaluation_keeps_answer_key_out_of_public_question():
    question = DEMONSTRATION_LESSONS["python-for-loops"].steps[0].knowledge_checks[0]
    answer_key = AssessmentAnswerKey(
        assessment_id=question.assessment_id,
        accepted_answers=["Visit the next stop"],
        explanation="The route proceeds to its next listed stop.",
        correct_feedback="Correct.",
        incorrect_feedback="Try again using the route list.",
    )

    assert "accepted_answers" not in question.model_dump()
    result = evaluate_answer(answer_key, " visit the next stop ", 2)
    assert result.is_correct is True
    assert result.attempts_remaining == 1


def test_incorrect_assessment_answer_has_feedback_and_retry_count():
    answer_key = AssessmentAnswerKey(
        assessment_id="sample-check",
        accepted_answers=["3"],
        explanation="There are three items.",
        correct_feedback="Correct.",
        incorrect_feedback="Count the items again.",
    )

    result = evaluate_answer(answer_key, "2", 1)

    assert result.is_correct is False
    assert result.feedback == "Count the items again."
    assert result.attempts_remaining == 0


def test_topic_and_step_models_allow_subjects_without_code_or_images():
    topic = LearningTopic(
        topic_id="poetry",
        title="Poetry",
        description="Explore imagery in poetry.",
        category="Humanities",
        difficulty="beginner",
        goal="Identify imagery",
    )
    step = TeachingStep(
        step_id="read-poem",
        title="Read a short poem",
        explanation="Notice the images suggested by the words.",
    )

    assert topic.estimated_duration_minutes is None
    assert step.code_snippets == []
    assert step.visual_assets == []
    assert step.formulas == []
    assert step.narration is None


def test_cors_allows_only_explicit_local_frontend_origins(client):
    allowed = client.options(
        "/api/v1/topics",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    denied = client.options(
        "/api/v1/topics",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert (
        allowed.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )
    assert "access-control-allow-origin" not in denied.headers

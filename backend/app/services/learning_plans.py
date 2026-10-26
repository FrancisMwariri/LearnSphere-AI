from uuid import uuid4

from app.models.learning import (
    LearningPlan,
    LearningPlanRequest,
    LearningTopic,
    Lesson,
    TeachingStep,
)


def create_demonstration_plan(request: LearningPlanRequest) -> LearningPlan:
    duration = request.duration_minutes or 20
    topic = LearningTopic(
        topic_id=f"learner-topic-{uuid4().hex}",
        title=request.topic.strip(),
        description=(
            "Learner-provided topic. This demonstration plan has not been "
            "generated or researched by an AI service."
        ),
        category="Learner-defined topic",
        difficulty="unspecified",
        goal=request.learning_goal.strip(),
        estimated_duration_minutes=duration,
    )
    step = TeachingStep(
        step_id="demonstration-introduction",
        title=f"Introduction to {request.topic.strip()}",
        explanation=(
            "This is a demonstration placeholder. Lesson content generation "
            "is not configured yet."
        ),
        narration=None,
    )
    return LearningPlan(
        plan_id=f"demo-plan-{uuid4().hex}",
        topic=topic,
        objectives=[
            f"Clarify the learner's goal: {request.learning_goal.strip()}"
        ],
        steps=[step],
        estimated_duration_minutes=duration,
        teaching_strategy=(
            request.preferred_teaching_style
            or "A topic-independent explanation followed by learner practice"
        ),
        activities=["Reflect on prior knowledge related to the selected topic"],
        assessment_methods=["A future knowledge check, not yet configured"],
        generation_status="not_configured",
        message=(
            "This is a structural demonstration only. No AI-generated or "
            "researched lesson content is being represented."
        ),
    )


def plan_from_lesson(lesson: Lesson) -> LearningPlan:
    return LearningPlan(
        plan_id=lesson.lesson_id,
        topic=lesson.topic,
        objectives=lesson.objectives,
        steps=lesson.steps,
        estimated_duration_minutes=lesson.estimated_duration_minutes,
        teaching_strategy=lesson.teaching_strategy,
        activities=lesson.activities,
        assessment_methods=lesson.assessment_methods,
        generation_status="demonstration",
        message=lesson.message,
    )

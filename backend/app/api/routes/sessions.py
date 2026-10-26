from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.data.demo_lessons import DEMONSTRATION_LESSONS
from app.models.learning import (
    LearnerQuestionRequest,
    LearningSession,
    LearningSessionCreateRequest,
    QuestionResponse,
)
from app.services.learning_plans import plan_from_lesson
from app.services.session_store import SessionRecord, session_store

router = APIRouter(prefix="/learning-sessions", tags=["learning sessions"])


@router.post("", response_model=LearningSession, status_code=201)
def create_learning_session(
    request: LearningSessionCreateRequest,
) -> LearningSession:
    if request.lesson_id is not None:
        lesson = DEMONSTRATION_LESSONS.get(request.lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        plan = plan_from_lesson(lesson)
        lesson_id = lesson.lesson_id
    else:
        plan = request.plan
        lesson_id = None

    if plan is None:
        raise HTTPException(status_code=422, detail="A plan or lesson is required")

    first_step = plan.steps[0] if plan.steps else None
    session = LearningSession(
        session_id=str(uuid4()),
        source_type="lesson" if lesson_id else "learning_plan",
        lesson_id=lesson_id,
        plan_id=plan.plan_id,
        current_step_id=first_step.step_id if first_step else None,
        current_step_number=1 if first_step else None,
        state="ready",
    )
    session_store[session.session_id] = SessionRecord(
        session=session,
        step_ids={step.step_id for step in plan.steps},
    )
    return session


@router.post(
    "/{session_id}/questions",
    response_model=QuestionResponse,
)
def ask_question(
    session_id: str,
    request: LearnerQuestionRequest,
) -> QuestionResponse:
    record = session_store.get(session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Learning session not found")
    if request.step_id is not None and request.step_id not in record.step_ids:
        raise HTTPException(
            status_code=404,
            detail="Lesson step is not part of this session",
        )

    return QuestionResponse(
        status="not_configured",
        answer=None,
        message=(
            "AI tutoring is not configured. No answer was generated; "
            "the supplied question has not been processed."
        ),
        session_id=record.session.session_id,
    )

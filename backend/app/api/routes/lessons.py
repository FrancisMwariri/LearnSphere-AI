from fastapi import APIRouter, HTTPException

from app.data.demo_lessons import DEMONSTRATION_LESSONS
from app.models.learning import Lesson, LessonStepResponse

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=Lesson)
def get_lesson(lesson_id: str) -> Lesson:
    lesson = DEMONSTRATION_LESSONS.get(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get(
    "/{lesson_id}/steps/{step_number}",
    response_model=LessonStepResponse,
)
def get_lesson_step(lesson_id: str, step_number: int) -> LessonStepResponse:
    lesson = DEMONSTRATION_LESSONS.get(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if step_number < 1 or step_number > len(lesson.steps):
        raise HTTPException(status_code=404, detail="Lesson step not found")
    return LessonStepResponse(
        lesson_id=lesson.lesson_id,
        step_number=step_number,
        step=lesson.steps[step_number - 1],
    )

from fastapi import APIRouter, HTTPException

from app.models.learning import (
    Lesson,
    LessonGenerationRequest,
    LessonQuestionRequest,
    TeachingAnswer,
)
from app.services.teaching_engine import ProviderOutputError, teaching_engine

router = APIRouter(prefix="/teaching", tags=["AI teaching engine"])


@router.post("/lessons", response_model=Lesson)
def generate_lesson(request: LessonGenerationRequest) -> Lesson:
    try:
        return teaching_engine.generate_lesson(request)
    except ProviderOutputError as error:
        raise HTTPException(
            status_code=502,
            detail="Teaching provider returned an invalid lesson response.",
        ) from error


@router.post("/questions", response_model=TeachingAnswer)
def answer_lesson_question(request: LessonQuestionRequest) -> TeachingAnswer:
    try:
        return teaching_engine.answer_question(request)
    except ProviderOutputError as error:
        raise HTTPException(
            status_code=502,
            detail="Teaching provider returned an invalid answer response.",
        ) from error

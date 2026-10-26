from fastapi import APIRouter, HTTPException

from app.models.learning import (
    Lesson,
    LessonGenerationRequest,
    LessonQuestionRequest,
    TeachingAnswer,
)
from app.services.teaching_engine import ProviderOutputError, teaching_engine
from app.services.teaching_provider import (
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
)

router = APIRouter(prefix="/teaching", tags=["AI teaching engine"])


@router.post("/lessons", response_model=Lesson)
def generate_lesson(request: LessonGenerationRequest) -> Lesson:
    try:
        return teaching_engine.generate_lesson(request)
    except ProviderOutputError:
        raise HTTPException(
            status_code=502,
            detail="Teaching provider returned an invalid lesson response.",
        ) from None
    except ProviderConfigurationError:
        raise HTTPException(
            status_code=503,
            detail="Teaching provider is not configured.",
        ) from None
    except ProviderRateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Teaching provider is temporarily rate limited.",
        ) from None
    except ProviderTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Teaching provider request timed out.",
        ) from None
    except ProviderResponseError:
        raise HTTPException(
            status_code=502,
            detail="Teaching provider request failed.",
        ) from None


@router.post("/questions", response_model=TeachingAnswer)
def answer_lesson_question(request: LessonQuestionRequest) -> TeachingAnswer:
    try:
        return teaching_engine.answer_question(request)
    except ProviderOutputError:
        raise HTTPException(
            status_code=502,
            detail="Teaching provider returned an invalid answer response.",
        ) from None
    except ProviderConfigurationError:
        raise HTTPException(
            status_code=503,
            detail="Teaching provider is not configured.",
        ) from None
    except ProviderRateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Teaching provider is temporarily rate limited.",
        ) from None
    except ProviderTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Teaching provider request timed out.",
        ) from None
    except ProviderResponseError:
        raise HTTPException(
            status_code=502,
            detail="Teaching provider request failed.",
        ) from None

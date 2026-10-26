from pydantic import ValidationError

from app.models.learning import (
    Lesson,
    LessonGenerationRequest,
    LessonQuestionRequest,
    TeachingAnswer,
)
from app.core.config import get_teaching_provider_settings
from app.services.mock_teaching_provider import MockTeachingProvider
from app.services.openai_teaching_provider import OpenAITeachingProvider
from app.services.teaching_provider import TeachingProvider


class ProviderOutputError(Exception):
    """Raised when a teaching provider returns data outside the API schema."""


class TeachingEngine:
    def __init__(self, provider: TeachingProvider) -> None:
        self.provider = provider

    def _provider_generation_status(self) -> str:
        status = getattr(self.provider, "generation_status", None)
        if status not in {"mock", "generated"}:
            raise ProviderOutputError(
                "Teaching provider has an unsupported generation status."
            )
        return status

    def generate_lesson(self, request: LessonGenerationRequest) -> Lesson:
        provider_status = self._provider_generation_status()
        output = self.provider.generate_lesson(request)
        try:
            lesson = Lesson.model_validate(output)
        except ValidationError as error:
            raise ProviderOutputError(
                "Teaching provider returned an invalid lesson."
            ) from error
        if lesson.generation_status != provider_status:
            raise ProviderOutputError(
                "Teaching provider returned inconsistent provenance."
            )
        if lesson.research_status != "not_researched" or any(
            step.references for step in lesson.steps
        ):
            raise ProviderOutputError(
                "Teaching provider returned unsupported research provenance."
            )
        if provider_status == "generated":
            lesson.message = (
                "Model-generated content; not independently verified or "
                "researched."
            )
        return lesson

    def answer_question(self, request: LessonQuestionRequest) -> TeachingAnswer:
        provider_status = self._provider_generation_status()
        output = self.provider.answer_question(request)
        try:
            answer = TeachingAnswer.model_validate(output)
        except ValidationError as error:
            raise ProviderOutputError(
                "Teaching provider returned an invalid answer."
            ) from error
        if answer.status != provider_status or answer.references:
            raise ProviderOutputError(
                "Teaching provider returned unsupported answer provenance."
            )
        if provider_status == "generated":
            answer.disclaimer = (
                "Model-generated answer; not independently verified or "
                "researched."
            )
        return answer


def create_teaching_engine() -> TeachingEngine:
    provider_name, base_url, model, api_key = get_teaching_provider_settings()
    if provider_name == "mock":
        return TeachingEngine(provider=MockTeachingProvider())
    if provider_name == "openai":
        return TeachingEngine(
            provider=OpenAITeachingProvider(
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
        )
    raise ValueError(
        "TEACHING_PROVIDER must be either 'mock' or 'openai'."
    )


teaching_engine = create_teaching_engine()

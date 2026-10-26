from typing import Literal, Protocol

from app.models.learning import LessonGenerationRequest, LessonQuestionRequest


class TeachingProviderError(Exception):
    """Base class for safe, user-facing provider failures."""


class ProviderConfigurationError(TeachingProviderError):
    """Raised when a selected provider is not configured."""


class ProviderRateLimitError(TeachingProviderError):
    """Raised when the model provider rate-limits a request."""


class ProviderTimeoutError(TeachingProviderError):
    """Raised when a model-provider request times out."""


class ProviderResponseError(TeachingProviderError):
    """Raised when the provider response cannot be safely consumed."""


class TeachingProvider(Protocol):
    generation_status: Literal["mock", "generated"]

    def generate_lesson(self, request: LessonGenerationRequest) -> object:
        """Return untrusted lesson data for validation by the teaching engine."""

    def answer_question(self, request: LessonQuestionRequest) -> object:
        """Return untrusted answer data for validation by the teaching engine."""

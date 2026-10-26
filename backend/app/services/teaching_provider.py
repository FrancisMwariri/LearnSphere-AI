from typing import Literal, Protocol

from app.models.learning import LessonGenerationRequest, LessonQuestionRequest


class TeachingProvider(Protocol):
    generation_status: Literal["mock", "generated"]

    def generate_lesson(self, request: LessonGenerationRequest) -> object:
        """Return untrusted lesson data for validation by the teaching engine."""

    def answer_question(self, request: LessonQuestionRequest) -> object:
        """Return untrusted answer data for validation by the teaching engine."""

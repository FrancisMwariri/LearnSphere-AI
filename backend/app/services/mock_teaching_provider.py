import hashlib
import json
from typing import Literal

from app.models.learning import LessonGenerationRequest, LessonQuestionRequest


class MockTeachingProvider:
    generation_status: Literal["mock"] = "mock"

    def generate_lesson(self, request: LessonGenerationRequest) -> dict[str, object]:
        request_data = json.dumps(
            request.model_dump(mode="json"),
            ensure_ascii=True,
            sort_keys=True,
        )
        lesson_key = hashlib.sha256(request_data.encode("utf-8")).hexdigest()[:12]
        level = request.learner_level.casefold()
        difficulty: Literal[
            "beginner", "intermediate", "advanced", "unspecified"
        ] = (
            level
            if level in {"beginner", "intermediate", "advanced"}
            else "unspecified"
        )
        topic_title = request.topic
        subject = request.subject or "Learner-defined topic"
        objective = request.learning_objective
        mental_model_id = f"mental-model-{lesson_key}"
        application_id = f"application-{lesson_key}"

        return {
            "lesson_id": f"mock-lesson-{lesson_key}",
            "title": f"Learning about {topic_title}",
            "topic": {
                "topic_id": f"topic-{lesson_key}",
                "title": topic_title,
                "description": (
                    "A deterministic teaching-engine demonstration. "
                    "This content has not been researched."
                ),
                "category": subject,
                "difficulty": difficulty,
                "goal": objective,
            },
            "objectives": [objective],
            "steps": [
                {
                    "step_id": mental_model_id,
                    "title": "Build a mental model",
                    "explanation": (
                        f"Begin with your objective: {objective} Use the "
                        f"explanation style '{request.preferred_explanation_style}' "
                        "to connect the topic to ideas you already know. This "
                        "is teaching scaffolding, not a researched explanation."
                    ),
                    "key_concepts": [topic_title, objective],
                    "examples": [
                        {
                            "title": "Learner-selected connection",
                            "description": (
                                f"Think of an example from a context familiar "
                                f"to you that illustrates {topic_title}. The "
                                "mock provider does not assert a factual example."
                            ),
                        }
                    ],
                    "visualization_events": [
                        {
                            "event_id": f"highlight-topic-{lesson_key}",
                            "event_type": "highlight",
                            "target_ids": [mental_model_id],
                            "parameters": {"focus": "topic"},
                            "narration": (
                                f"Focus on the learner-selected topic: {topic_title}."
                            ),
                            "caption": topic_title,
                        }
                    ],
                    "narration": (
                        f"Let's explore {topic_title} in a way suited to "
                        f"{request.learner_level} learners."
                    ),
                    "captions": [f"Topic: {topic_title}", f"Goal: {objective}"],
                },
                {
                    "step_id": application_id,
                    "title": "Apply the idea",
                    "explanation": (
                        "Explain the topic in your own words, then check whether "
                        "your explanation addresses the stated learning objective."
                    ),
                    "knowledge_checks": [
                        {
                            "assessment_id": f"practice-{lesson_key}",
                            "question_type": "short_answer",
                            "prompt": (
                                f"How would you explain {topic_title} in relation "
                                f"to this goal: {objective}"
                            ),
                            "hints": [
                                "Use the key idea from the previous step.",
                                "Connect your response to the learning objective.",
                            ],
                            "feedback_guidance": (
                                "Give feedback on whether the response addresses "
                                "the stated objective; do not infer facts that "
                                "are not present in the lesson."
                            ),
                            "max_attempts": 2,
                        }
                    ],
                    "activities": [
                        {
                            "activity_id": f"reflect-{lesson_key}",
                            "activity_type": "reflection",
                            "instructions": (
                                "Write one question that would help you check "
                                "your understanding of this topic."
                            ),
                        }
                    ],
                },
            ],
            "estimated_duration_minutes": 10,
            "teaching_strategy": (
                f"Deterministic mock outline using the requested style: "
                f"{request.preferred_explanation_style}"
            ),
            "activities": ["Reflect on the topic and learning objective"],
            "assessment_methods": ["Short-answer self-check"],
            "research_status": "not_researched",
            "generation_status": "mock",
            "message": (
                "Deterministic mock-provider demonstration. This is not "
                "AI-generated, fact-checked, or researched content."
            ),
        }

    def answer_question(self, request: LessonQuestionRequest) -> dict[str, object]:
        context_title = (
            request.lesson_context.lesson_title
            if request.lesson_context is not None
            else None
        )
        context = (
            f" for the lesson titled '{context_title}'"
            if context_title
            else f" about '{request.topic}'"
        )
        return {
            "status": "mock",
            "answer": (
                f"A question was submitted{context}. This local mock does "
                "not interpret the provided lesson context or answer the "
                "question. Connect a teaching provider in a future milestone "
                "for context-aware tutoring."
            ),
            "disclaimer": (
                "This response is deterministic demonstration text. It was "
                "not generated through AI reasoning, verified, or researched; "
                "this response is not researched."
            ),
            "references": [],
        }

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)

ScalarValue = StrictStr | StrictInt | StrictFloat | StrictBool | None


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        normalized = value.copy()
        for field_name, field_value in normalized.items():
            if isinstance(field_value, str):
                field_value = field_value.strip()
                if not field_value:
                    raise ValueError(f"{field_name} must not be blank")
                normalized[field_name] = field_value
        return normalized


class LearningTopic(StrictModel):
    topic_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=120)
    difficulty: Literal["beginner", "intermediate", "advanced", "unspecified"]
    goal: str = Field(min_length=1, max_length=1000)
    prerequisites: list[str] = Field(default_factory=list)
    estimated_duration_minutes: int | None = Field(default=None, ge=1, le=600)


class TopicCatalog(StrictModel):
    examples_are_exhaustive: Literal[False] = False
    categories: list[str]
    demonstration_topics: list[LearningTopic]


class LearningPlanRequest(StrictModel):
    topic: str = Field(min_length=1, max_length=200)
    current_knowledge_level: str = Field(min_length=1, max_length=120)
    learning_goal: str = Field(min_length=1, max_length=1000)
    preferred_teaching_style: str | None = Field(default=None, max_length=200)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)


class RealWorldExample(StrictModel):
    title: str
    description: str


class VisualAsset(StrictModel):
    asset_id: str
    asset_type: Literal["image", "illustration", "diagram", "chart", "simulation"]
    description: str
    url: HttpUrl | None = None


class DiagramComponent(StrictModel):
    component_id: str
    label: str
    component_type: str
    description: str | None = None


class DiagramRelationship(StrictModel):
    source_component_id: str
    target_component_id: str
    label: str | None = None


class DiagramDescription(StrictModel):
    diagram_id: str
    title: str
    description: str
    components: list[DiagramComponent] = Field(default_factory=list)
    relationships: list[DiagramRelationship] = Field(default_factory=list)


class VisualizationEvent(StrictModel):
    event_id: str
    event_type: Literal[
        "highlight",
        "reveal",
        "move",
        "update_value",
        "draw_connection",
        "show_output",
        "set_state",
    ]
    target_ids: list[str] = Field(default_factory=list)
    parameters: dict[str, ScalarValue] = Field(default_factory=dict)
    code_line_numbers: list[int] = Field(default_factory=list)
    narration: str | None = None
    caption: str | None = None
    expected_state: dict[str, ScalarValue] | None = None


class CodeSnippet(StrictModel):
    language: str
    code: str
    expected_output: str | None = None


class Formula(StrictModel):
    formula_id: str
    expression: str
    description: str | None = None


class LearningActivity(StrictModel):
    activity_id: str
    activity_type: Literal[
        "exercise",
        "simulation",
        "reflection",
        "discussion",
        "practice",
    ]
    instructions: str
    interactive: bool = False


class AssessmentChoice(StrictModel):
    choice_id: str
    text: str


class AssessmentQuestion(StrictModel):
    assessment_id: str
    question_type: Literal["multiple_choice", "short_answer", "practical"]
    prompt: str
    choices: list[AssessmentChoice] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    feedback_guidance: str | None = None
    max_attempts: int = Field(default=2, ge=1, le=10)


class AssessmentAnswerKey(StrictModel):
    assessment_id: str
    accepted_answers: list[str] = Field(min_length=1)
    explanation: str
    correct_feedback: str
    incorrect_feedback: str


class AssessmentResult(StrictModel):
    assessment_id: str
    is_correct: bool
    feedback: str
    explanation: str
    attempts_remaining: int = Field(ge=0)


class ResearchReference(StrictModel):
    title: str
    url: HttpUrl
    publisher: str | None = None
    publication_date: date | None = None
    retrieved_at: datetime | None = None


class TeachingStep(StrictModel):
    step_id: str
    title: str
    explanation: str | None = None
    key_concepts: list[str] = Field(default_factory=list)
    examples: list[RealWorldExample] = Field(default_factory=list)
    visual_assets: list[VisualAsset] = Field(default_factory=list)
    diagrams: list[DiagramDescription] = Field(default_factory=list)
    visualization_events: list[VisualizationEvent] = Field(default_factory=list)
    code_snippets: list[CodeSnippet] = Field(default_factory=list)
    formulas: list[Formula] = Field(default_factory=list)
    highlighted_elements: list[str] = Field(default_factory=list)
    narration: str | None = None
    captions: list[str] = Field(default_factory=list)
    activities: list[LearningActivity] = Field(default_factory=list)
    knowledge_checks: list[AssessmentQuestion] = Field(default_factory=list)
    references: list[ResearchReference] = Field(default_factory=list)


class LearningPlan(StrictModel):
    plan_id: str
    topic: LearningTopic
    objectives: list[str]
    steps: list[TeachingStep] = Field(min_length=1)
    estimated_duration_minutes: int = Field(ge=1, le=600)
    teaching_strategy: str
    activities: list[str] = Field(default_factory=list)
    assessment_methods: list[str] = Field(default_factory=list)
    generation_status: Literal["demonstration", "not_configured"]
    message: str


class Lesson(StrictModel):
    lesson_id: str
    title: str
    topic: LearningTopic
    objectives: list[str]
    steps: list[TeachingStep] = Field(min_length=1)
    estimated_duration_minutes: int = Field(ge=1, le=600)
    teaching_strategy: str
    activities: list[str] = Field(default_factory=list)
    assessment_methods: list[str] = Field(default_factory=list)
    research_status: Literal["not_researched", "demonstration_only"]
    generation_status: Literal["demonstration", "mock", "generated"] = (
        "demonstration"
    )
    message: str


class LessonGenerationRequest(StrictModel):
    topic: str = Field(min_length=1, max_length=200)
    learner_level: str = Field(min_length=1, max_length=120)
    learning_objective: str = Field(min_length=1, max_length=1000)
    preferred_explanation_style: str = Field(min_length=1, max_length=200)
    subject: str | None = Field(default=None, max_length=120)


class LessonQuestionStepContext(StrictModel):
    step_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    explanation: str | None = Field(default=None, max_length=2000)
    key_concepts: list[Annotated[str, Field(min_length=1, max_length=200)]] = (
        Field(default_factory=list, max_length=20)
    )


class LessonQuestionContext(StrictModel):
    lesson_title: str | None = Field(default=None, max_length=200)
    learning_objective: str | None = Field(default=None, max_length=1000)
    current_step: LessonQuestionStepContext | None = None


class LessonQuestionRequest(StrictModel):
    question: str = Field(min_length=1, max_length=2000)
    topic: str = Field(min_length=1, max_length=200)
    learner_level: str | None = Field(default=None, max_length=120)
    preferred_explanation_style: str | None = Field(default=None, max_length=200)
    lesson_context: LessonQuestionContext | None = None


class TeachingAnswer(StrictModel):
    status: Literal["mock", "generated"]
    answer: str
    disclaimer: str
    references: list[ResearchReference] = Field(default_factory=list)


class LessonStepResponse(StrictModel):
    lesson_id: str
    step_number: int = Field(ge=1)
    step: TeachingStep


class LearningSessionCreateRequest(StrictModel):
    plan: LearningPlan | None = None
    lesson_id: str | None = None

    @model_validator(mode="after")
    def require_one_source(self) -> "LearningSessionCreateRequest":
        if (self.plan is None) == (self.lesson_id is None):
            raise ValueError("Provide exactly one of plan or lesson_id")
        return self


class LearningSession(StrictModel):
    session_id: str
    source_type: Literal["learning_plan", "lesson"]
    lesson_id: str | None = None
    plan_id: str
    current_step_id: str | None = None
    current_step_number: int | None = Field(default=None, ge=1)
    state: Literal["ready"] = "ready"


class LearnerQuestionRequest(StrictModel):
    question: str = Field(min_length=1, max_length=2000)
    topic: str = Field(min_length=1, max_length=200)
    step_id: str | None = Field(default=None, min_length=1, max_length=120)


class QuestionResponse(StrictModel):
    status: Literal["not_configured"]
    answer: None = None
    message: str
    session_id: str

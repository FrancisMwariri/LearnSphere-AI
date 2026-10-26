from dataclasses import dataclass

from app.models.learning import LearningSession


@dataclass
class SessionRecord:
    session: LearningSession
    step_ids: set[str]


session_store: dict[str, SessionRecord] = {}

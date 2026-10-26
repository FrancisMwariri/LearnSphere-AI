from fastapi import APIRouter

from app.data.demo_lessons import DEMONSTRATION_TOPICS
from app.models.learning import TopicCatalog

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=TopicCatalog)
def list_topics() -> TopicCatalog:
    return TopicCatalog(
        examples_are_exhaustive=False,
        categories=[
            "Programming and technology",
            "Mathematics and science",
            "Business and companies",
            "Humanities and professional skills",
            "Learner-defined topics",
        ],
        demonstration_topics=DEMONSTRATION_TOPICS,
    )

from fastapi import APIRouter

from app.models.learning import LearningPlan, LearningPlanRequest
from app.services.learning_plans import create_demonstration_plan

router = APIRouter(prefix="/learning-plans", tags=["learning plans"])


@router.post("", response_model=LearningPlan)
def create_learning_plan(request: LearningPlanRequest) -> LearningPlan:
    return create_demonstration_plan(request)

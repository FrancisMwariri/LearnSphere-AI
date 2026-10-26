from fastapi import APIRouter

from app.api.routes.lessons import router as lessons_router
from app.api.routes.plans import router as plans_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.teaching import router as teaching_router
from app.api.routes.topics import router as topics_router

api_router = APIRouter()
api_router.include_router(topics_router)
api_router.include_router(plans_router)
api_router.include_router(lessons_router)
api_router.include_router(sessions_router)
api_router.include_router(teaching_router)

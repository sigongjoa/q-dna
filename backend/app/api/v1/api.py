from fastapi import APIRouter
from app.api.v1.endpoints import questions, curriculum, tags, analytics, diagrams, cms, reports

api_router = APIRouter()
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(curriculum.router, prefix="/curriculum", tags=["curriculum"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(diagrams.router, prefix="/diagrams", tags=["diagrams"])
api_router.include_router(cms.router, prefix="/cms", tags=["cms"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

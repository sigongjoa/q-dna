from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.attempt import AttemptLog
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

router = APIRouter()

class AttemptSubmit(BaseModel):
    user_id: UUID
    question_id: UUID
    response_data: dict
    is_correct: bool
    score: float
    time_taken_ms: int

@router.post("/attempt")
async def submit_attempt(
    attempt: AttemptSubmit,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Submit a question attempt and trigger BKT update.
    """
    # 1. Save Log
    log = AttemptLog(
        user_id=attempt.user_id,
        question_id=attempt.question_id,
        response_data=attempt.response_data,
        is_correct=attempt.is_correct,
        score=attempt.score,
        time_taken_ms=attempt.time_taken_ms
    )
    db.add(log)
    await db.commit()
    
    # 2. Trigger BKT Analysis (Async in real world)
    from app.services.analytics_service import analytics_service
    # Assuming question maps to a single skill for simplicity in this MVP
    # In real app, we query QuestionTags to find skills.
    skill_id = "Math.Algebra.Quadratics" # Mock resolution
    
    new_mastery = analytics_service.update_bkt(
        str(attempt.user_id), 
        skill_id, 
        attempt.is_correct
    )
    
    return {"status": "recorded", "new_mastery_estimate": new_mastery}

@router.get("/report/{user_id}")
async def get_user_report(user_id: UUID) -> Any:
    """
    Get aggregated user analytics report.
    """
    return {
        "user_id": user_id,
        "mastery_map": {
            "Math.Algebra": 0.85,
            "Math.Geometry": 0.65
        },
        "recent_activity": []
    }

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
    Submit a question attempt and trigger real BKT update.
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

    # 2. Get skill from question tags (real implementation)
    from app.services.analytics_service import analytics_service
    from app.models.question import Question, QuestionTag
    from app.models.tag import Tag
    from sqlalchemy import select

    # Find skill tags for this question
    stmt = select(Tag).join(QuestionTag).where(
        QuestionTag.question_id == attempt.question_id,
        Tag.tag_type.in_(["concept", "subject"])
    ).limit(1)

    result = await db.execute(stmt)
    skill_tag = result.scalars().first()

    if skill_tag:
        skill_id = skill_tag.name
    else:
        skill_id = "General.Unknown"

    # 3. Update BKT with real DB integration
    new_mastery = await analytics_service.update_bkt(
        db=db,
        user_id=attempt.user_id,
        skill_id=skill_id,
        is_correct=attempt.is_correct
    )

    return {
        "status": "recorded",
        "skill_analyzed": skill_id,
        "new_mastery_estimate": round(new_mastery, 3)
    }

@router.get("/report/{user_id}")
async def get_user_report(
    user_id: UUID,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Get real aggregated user analytics report.
    """
    from app.services.analytics_service import analytics_service
    from sqlalchemy import select, func
    from app.models.attempt import AttemptLog

    # Get mastery map
    mastery_map = await analytics_service.get_user_mastery_map(db, user_id)

    # Get recent activity
    stmt = select(AttemptLog).where(
        AttemptLog.user_id == user_id
    ).order_by(AttemptLog.attempted_at.desc()).limit(10)

    result = await db.execute(stmt)
    recent_logs = result.scalars().all()

    recent_activity = [
        {
            "question_id": str(log.question_id),
            "is_correct": log.is_correct,
            "score": log.score,
            "time_ms": log.time_taken_ms,
            "attempted_at": log.attempted_at.isoformat() if log.attempted_at else None
        }
        for log in recent_logs
    ]

    # Calculate stats
    total_attempts = len(recent_activity)
    correct_attempts = sum(1 for a in recent_activity if a["is_correct"])

    return {
        "user_id": str(user_id),
        "mastery_map": mastery_map,
        "recent_activity": recent_activity,
        "stats": {
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "accuracy": round(correct_attempts / total_attempts, 3) if total_attempts > 0 else 0
        }
    }

@router.get("/recommend/{user_id}")
async def recommend_questions(
    user_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    count: int = 5
) -> Any:
    """
    Get personalized question recommendations based on mastery.
    """
    from app.services.analytics_service import analytics_service

    recommended_ids = await analytics_service.recommend_next_questions(
        db=db,
        user_id=user_id
    )

    return {
        "user_id": str(user_id),
        "recommended_question_ids": [str(qid) for qid in recommended_ids[:count]]
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.api import deps
from app.schemas.bulk import BulkSubmitRequest, BulkSubmitResponse
from app.models.attempt import AttemptLog
# Assuming we might need question validation, but skipping for speed in MVP

router = APIRouter()

@router.post("/bulk-submit", response_model=BulkSubmitResponse)
async def bulk_submit_attempts(
    request: BulkSubmitRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Submit multiple student attempts in a single transaction.
    """
    success_count = 0
    failed_items = []

    for item in request.items:
        try:
            # Create attempt record
            # Note: score is strictly 100.0 (correct) or 0.0 (incorrect) for MVP generic logic
            score = 100.0 if item.is_correct else 0.0
            
            db_attempt = AttemptLog(
                user_id=item.student_id,
                question_id=item.question_id,
                response_data={"notes": item.notes} if item.notes else {},
                is_correct=item.is_correct,
                score=score,
                time_taken_ms=item.time_taken_seconds * 1000 if item.time_taken_seconds else None,
                attempted_at=datetime.now()
            )
            db.add(db_attempt)
            success_count += 1
        except Exception as e:
            failed_items.append({
                "student_id": str(item.student_id),
                "question_id": str(item.question_id),
                "error": str(e)
            })

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        # If commit fails, all fail
        return BulkSubmitResponse(
            success_count=0,
            failed_count=len(request.items),
            failed_items=[{"error": "Transaction commit failed: " + str(e)}]
        )

    return BulkSubmitResponse(
        success_count=success_count,
        failed_count=len(failed_items),
        failed_items=failed_items
    )

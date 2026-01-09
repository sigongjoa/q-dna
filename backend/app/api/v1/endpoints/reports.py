from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, timedelta

from app.api import deps
from app.services.report_service import report_service
from app.services.analytics_service import analytics_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/generate/{student_id}")
async def generate_report(
    student_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Generate a PDF report for a specific student.
    Returns the PDF content directly for MVP testing.
    """
    try:
        # Fetch real data
        report_data = await analytics_service.get_student_report_data(db, student_id)

        # We need a student name, fetch from DB or use placeholder
        # student = db.query(User).get(student_id)
        # student_name = student.full_name if student else "Unknown Student"
        student_name = "Student " + str(student_id)[:8]

        pdf_bytes = report_service.generate_report(student_name, report_data)
        
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=report_{student_id}.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.question import Question as QuestionModel
from app.schemas.question import Question, QuestionCreate

router = APIRouter()

@router.post("/", response_model=Question)
async def create_question(
    *,
    db: AsyncSession = Depends(deps.get_db),
    question_in: QuestionCreate
) -> Any:
    """
    Create new question.
    """
    db_obj = QuestionModel(
        question_type=question_in.question_type,
        content_stem=question_in.content_stem,
        content_metadata=question_in.content_metadata,
        answer_key=question_in.answer_key,
        difficulty_index=question_in.difficulty_index,
        created_by=question_in.create_by,  # In real app, get from current_user
        status=question_in.status
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[Question])
async def read_questions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve questions.
    """
    result = await db.execute(select(QuestionModel).offset(skip).limit(limit))
    questions = result.scalars().all()
    return questions

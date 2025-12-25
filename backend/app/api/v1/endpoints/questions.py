from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
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
        content_metadata=question_in.content_metadata.model_dump(),
        answer_key=question_in.answer_key,
        difficulty_index=question_in.difficulty_index,
        created_by=question_in.create_by,  # In real app, get from current_user
        status=question_in.status
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    print(f"DEBUG: Created Question {db_obj.question_id}")
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

@router.get("/{question_id}", response_model=Question)
async def read_question(
    *,
    db: AsyncSession = Depends(deps.get_db),
    question_id: str,
) -> Any:
    """
    Get question by ID.
    """
    import uuid
    try:
        # Check if analyze or other paths are caught (though method diff saves us)
        # Better safe than sorry if we add GET /something later
        uuid_obj = uuid.UUID(question_id)
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid UUID format")
         
    result = await db.execute(select(QuestionModel).where(QuestionModel.question_id == uuid_obj))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.post("/analyze", response_model=Any)
async def analyze_question_content(
    *,
    content_stem: str = Body(..., embed=True),
) -> Any:
    """
    [Advanced Math] Analyze question content to extract metadata (Grade, Domain, Difficulty).
    """
    from app.services.math_advanced_service import math_advanced_service
    metadata = await math_advanced_service.analyze_question_metadata(content_stem)
    return metadata

@router.post("/{question_id}/twin", response_model=Question)
async def generate_twin_question(
    *,
    db: AsyncSession = Depends(deps.get_db),
    question_id: str,
) -> Any:
    """
    [Advanced Math] Generate a TWIN problem based on the given question ID.
    The generated question is saved to DB immediately.
    """
    from app.services.math_advanced_service import math_advanced_service
    import uuid
    
    # 1. Fetch Original Question
    print(f"DEBUG: Searching for Question ID {question_id}")
    stmt = select(QuestionModel).where(QuestionModel.question_id == uuid.UUID(question_id))
    result = await db.execute(stmt)
    original_q = result.scalar_one_or_none()
    
    if not original_q:
        raise HTTPException(status_code=404, detail="Question not found")

    # 2. Generate Twin (Mock AI Call)
    # We need to convert DB model to Pydantic for the service
    # In a real app, strict TypeAdapter usage is better, but here we do simple pass
    # Caution: created_by might be needed from auth context
    
    # Re-construct Pydantic schema from DB model for service input if needed, 
    # but our service currently takes the DB model or Pydantic model. 
    # Let's assume service takes the DB model and handles it, or we map it.
    # Ideally, we map to Schema.
    
    # Simple mapping for now
    q_schema = Question.model_validate(original_q)
    
    twin_create_data = await math_advanced_service.generate_twin_question(q_schema)
    
    # 3. Save to DB
    db_obj = QuestionModel(
        question_type=twin_create_data.question_type,
        content_stem=twin_create_data.content_stem,
        content_metadata=twin_create_data.content_metadata.model_dump(), # JSONB serialization
        answer_key=twin_create_data.answer_key,
        difficulty_index=twin_create_data.difficulty_index,
        created_by=original_q.created_by, # Inherit owner for now
        status="generated"
    )
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    
    return db_obj

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Response
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

@router.post("/{question_id}/erroneous-solution")
async def generate_error_worksheet(
    *,
    db: AsyncSession = Depends(deps.get_db),
    question_id: str,
    error_types: List[str] = Query(default=None),
    output_format: str = Query(default="pdf")
):
    """
    오답 풀이 워크시트 생성 (프린트용)
    """
    import uuid
    from app.services.error_solution_service import error_solution_service
    from app.services.report_service import report_service

    # 1. 문제 조회
    try:
        uuid_obj = uuid.UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    stmt = select(QuestionModel).where(QuestionModel.question_id == uuid_obj)
    result = await db.execute(stmt)
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # 2. 오류 유형 파싱
    from app.schemas.error_solution import ErrorType
    selected_errors = None
    if error_types:
        try:
            selected_errors = [ErrorType(et) for et in error_types]
        except ValueError:
            # Ignore invalid types or raise error? Let's ignore or just pass strings 
            # if we wanted strict we would ensure frontend sends valid ones.
            # But converting to Enum helps service validation.
            pass

    # 3. LLM으로 오답/정답 풀이 생성
    # Handling potential missing answer key
    correct_ans = question.answer_key.get("answer", "") if question.answer_key else ""
    
    erroneous_data = await error_solution_service.generate_erroneous_solution(
        question_content=question.content_stem,
        correct_answer=correct_ans,
        error_types=selected_errors
    )

    correct_data = await error_solution_service.generate_correct_solution(
        question_content=question.content_stem,
        correct_answer=correct_ans
    )

    # 4. PDF 생성
    if output_format == "pdf":
        template_data = {
            "question_content": question.content_stem,
            "erroneous_steps": erroneous_data["steps"],
            "correct_steps": correct_data["steps"],
            "wrong_answer": erroneous_data.get("final_wrong_answer", ""),
            "correct_answer": correct_ans
        }

        # filename setting
        filename = f"error_worksheet_{question_id}.pdf"
        
        try:
            pdf_bytes = report_service.generate_error_worksheet(template_data)
        except Exception as e:
            print(f"PDF Generation Error: {e}")
            raise HTTPException(status_code=500, detail="PDF Generation Failed. Ensure WeasyPrint/GTK is installed.")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        # JSON 응답
        return {
            "erroneous_solution": erroneous_data,
            "correct_solution": correct_data
        }


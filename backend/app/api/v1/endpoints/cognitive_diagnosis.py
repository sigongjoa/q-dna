"""
인지 진단 API 엔드포인트 (Node2 - Q-DNA)

LLM 기반 생성형 인지 진단 (BKT/IRT 대체)
Node0를 통해 Node4에서 호출됨
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnosis", tags=["Cognitive Diagnosis"])


# ============== Pydantic Schemas ==============

class DiagnoseRequest(BaseModel):
    """진단 요청 스키마"""
    student_id: str = Field(..., description="학생 ID")
    question_content: str = Field(..., description="문제 내용")
    student_answer: str = Field(..., description="학생 답안 (OCR 텍스트 포함)")
    correct_answer: Optional[str] = Field(None, description="정답 (선택사항)")
    question_id: Optional[str] = Field(None, description="문제 ID")
    subject: str = Field(default="수학", description="과목명")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_123",
                "question_content": "x^2 + 2x + 1을 인수분해하시오",
                "student_answer": "(x+1)(x-1)",
                "correct_answer": "(x+1)^2",
                "question_id": "q_001",
                "subject": "수학"
            }
        }


class BatchDiagnoseRequest(BaseModel):
    """일괄 진단 요청 스키마"""
    student_id: str
    subject: str = "수학"
    attempts: List[Dict[str, str]] = Field(
        ...,
        description="[{question, student_answer, correct_answer}]"
    )


class RubricEvaluationRequest(BaseModel):
    """루브릭 평가 요청 스키마"""
    question_content: str
    student_answer: str
    subject: str = "수학"
    rubric: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="평가 루브릭",
        json_schema_extra={
            "example": {
                "개념이해": {"max_score": 5, "description": "핵심 개념 이해도"},
                "논리전개": {"max_score": 5, "description": "풀이 과정의 논리성"}
            }
        }
    )


class KGOperationResponse(BaseModel):
    """지식 그래프 연산 응답"""
    operation: str
    relation: str
    concept: str
    strength: float
    evidence: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """진단 결과 응답 스키마"""
    student_id: str
    question_id: Optional[str]
    is_correct: bool
    error_type: Optional[str]
    reasoning_trace: str
    error_location: Optional[str]
    feedback: str
    recommendation: str
    concepts_involved: List[str]
    kg_operations: List[KGOperationResponse]
    confidence: float
    timestamp: str


class StudentProfileResponse(BaseModel):
    """학생 프로필 응답 스키마"""
    student_id: str
    total_attempts: int
    total_correct: int
    overall_accuracy: float
    weak_concepts: List[str]
    strong_concepts: List[str]
    misconception_concepts: List[str]
    concepts: Dict[str, Any]
    graph_data: Dict[str, Any]


# ============== Service Dependency ==============

_diagnosis_service = None


def get_diagnosis_service():
    """인지 진단 서비스 의존성 주입"""
    global _diagnosis_service

    if _diagnosis_service is None:
        try:
            from mathesis_core.diagnosis import CognitiveDiagnosisService
            from mathesis_core.llm.clients import create_ollama_client

            llm_client = create_ollama_client(
                base_url="http://localhost:11434",
                model="llama3"
            )
            _diagnosis_service = CognitiveDiagnosisService(
                llm_client=llm_client,
                subject="수학"
            )
            logger.info("CognitiveDiagnosisService initialized with Ollama")
        except Exception as e:
            logger.warning(f"Failed to initialize with Ollama: {e}")
            # Mock 서비스 생성
            _diagnosis_service = MockDiagnosisService()
            logger.info("Using MockDiagnosisService")

    return _diagnosis_service


class MockDiagnosisService:
    """테스트용 Mock 진단 서비스"""

    def __init__(self):
        self._profiles = {}

    def diagnose(self, **kwargs):
        from mathesis_core.diagnosis.models import (
            DiagnosisResult,
            ErrorType,
            KnowledgeGraphOperation,
            RelationType
        )

        student_id = kwargs.get("student_id", "unknown")
        question_content = kwargs.get("question_content", "")
        student_answer = kwargs.get("student_answer", "")
        correct_answer = kwargs.get("correct_answer", "")

        # 간단한 정답 비교
        is_correct = (
            student_answer.replace(" ", "").lower() ==
            correct_answer.replace(" ", "").lower()
        ) if correct_answer else False

        return DiagnosisResult(
            student_id=student_id,
            question_id=kwargs.get("question_id"),
            question_content=question_content,
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            error_type=None if is_correct else ErrorType.KNOWLEDGE_GAP,
            reasoning_trace="[Mock] 자동 진단 결과",
            error_location=None if is_correct else "답안 전체",
            feedback="정답입니다!" if is_correct else "다시 확인해보세요.",
            recommendation="" if is_correct else "관련 개념 복습 필요",
            kg_operations=[
                KnowledgeGraphOperation(
                    operation="update",
                    relation=RelationType.MASTERED if is_correct else RelationType.STRUGGLES_WITH,
                    concept="일반개념",
                    strength=0.8 if is_correct else 0.4
                )
            ],
            confidence=0.5,
            concepts_involved=["일반개념"]
        )

    def get_student_profile(self, student_id: str):
        from mathesis_core.diagnosis.models import StudentKnowledgeProfile
        if student_id not in self._profiles:
            self._profiles[student_id] = StudentKnowledgeProfile(student_id=student_id)
        return self._profiles[student_id]

    def get_weak_concepts(self, student_id: str, threshold: float = 0.5):
        return self.get_student_profile(student_id).weak_concepts

    def get_recommendations(self, student_id: str):
        return ["복습 추천"]

    def diagnose_batch(self, student_id: str, attempts: list):
        return {
            "individual_results": [],
            "pattern_analysis": {"weak_concepts": []},
            "overall_diagnosis": "[Mock] 일괄 진단"
        }

    def evaluate_with_rubric(self, **kwargs):
        return {"total_score": 0, "feedback": "[Mock] 루브릭 평가"}


# ============== API Endpoints ==============

@router.post("/analyze", response_model=DiagnosisResponse)
async def analyze_student_answer(
    request: DiagnoseRequest,
    service=Depends(get_diagnosis_service)
):
    """
    학생 답안 인지 진단

    LLM을 사용하여 학생의 답안을 분석하고 오개념을 진단합니다.
    BKT/IRT와 달리 Zero-shot으로 즉시 진단이 가능합니다.
    """
    try:
        result = service.diagnose(
            student_id=request.student_id,
            question_content=request.question_content,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer,
            question_id=request.question_id
        )

        return DiagnosisResponse(
            student_id=result.student_id,
            question_id=result.question_id,
            is_correct=result.is_correct,
            error_type=result.error_type.value if result.error_type else None,
            reasoning_trace=result.reasoning_trace,
            error_location=result.error_location,
            feedback=result.feedback,
            recommendation=result.recommendation,
            concepts_involved=result.concepts_involved,
            kg_operations=[
                KGOperationResponse(
                    operation=op.operation,
                    relation=op.relation.value,
                    concept=op.concept,
                    strength=op.strength,
                    evidence=op.evidence
                )
                for op in result.kg_operations
            ],
            confidence=result.confidence,
            timestamp=result.timestamp.isoformat()
        )

    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/batch")
async def analyze_batch(
    request: BatchDiagnoseRequest,
    service=Depends(get_diagnosis_service)
):
    """
    여러 문제에 대한 일괄 진단

    여러 문제의 풀이를 한 번에 분석하여 패턴을 파악합니다.
    """
    try:
        result = service.diagnose_batch(
            student_id=request.student_id,
            attempts=request.attempts
        )
        return result
    except Exception as e:
        logger.error(f"Batch diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate/rubric")
async def evaluate_with_rubric(
    request: RubricEvaluationRequest,
    service=Depends(get_diagnosis_service)
):
    """
    루브릭 기반 평가

    정의된 평가 기준(루브릭)에 따라 학생 답안을 평가합니다.
    """
    try:
        result = service.evaluate_with_rubric(
            question_content=request.question_content,
            student_answer=request.student_answer,
            rubric=request.rubric
        )
        return result
    except Exception as e:
        logger.error(f"Rubric evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{student_id}", response_model=StudentProfileResponse)
async def get_student_profile(
    student_id: str,
    service=Depends(get_diagnosis_service)
):
    """
    학생 지식 프로필 조회

    Personal Knowledge Graph (PKG) 기반의 학생 지식 상태를 반환합니다.
    """
    try:
        profile = service.get_student_profile(student_id)

        return StudentProfileResponse(
            student_id=profile.student_id,
            total_attempts=profile.total_attempts,
            total_correct=profile.total_correct,
            overall_accuracy=profile.overall_accuracy,
            weak_concepts=profile.weak_concepts,
            strong_concepts=profile.strong_concepts,
            misconception_concepts=profile.misconception_concepts,
            concepts=profile.to_dict()["concepts"],
            graph_data=profile.to_graph_data()
        )

    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weak-concepts/{student_id}")
async def get_weak_concepts(
    student_id: str,
    threshold: float = 0.5,
    service=Depends(get_diagnosis_service)
):
    """
    약점 개념 조회

    학생이 어려워하는 개념 목록을 반환합니다.
    """
    try:
        weak = service.get_weak_concepts(student_id, threshold)
        return {"student_id": student_id, "weak_concepts": weak}
    except Exception as e:
        logger.error(f"Failed to get weak concepts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{student_id}")
async def get_recommendations(
    student_id: str,
    service=Depends(get_diagnosis_service)
):
    """
    학습 추천 조회

    학생의 현재 지식 상태에 기반한 학습 추천을 반환합니다.
    """
    try:
        recommendations = service.get_recommendations(student_id)
        return {"student_id": student_id, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(service=Depends(get_diagnosis_service)):
    """
    진단 서비스 상태 확인
    """
    is_mock = isinstance(service, MockDiagnosisService)
    return {
        "status": "healthy",
        "service_type": "mock" if is_mock else "ollama",
        "message": "Cognitive Diagnosis API is running (Node2 Q-DNA)"
    }

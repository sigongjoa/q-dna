from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

class ErrorType(str, Enum):
    ARITHMETIC_ERROR = "arithmetic_error"           # 연산 실수
    CONCEPT_MISAPPLICATION = "concept_misapplication"  # 개념 오적용 (fallback for general concepts)
    FORMULA_CONFUSION = "formula_confusion"         # 공식 혼동
    CONDITION_OMISSION = "condition_omission"       # 조건 누락
    LOGIC_LEAP = "logic_leap"                       # 논리적 비약
    SIGN_ERROR = "sign_error"                       # 부호 실수
    FRACTION_ADDITION_ERROR = "fraction_addition_error"  # 분모끼리 더하기
    ORDER_CONFUSION = "order_confusion"             # 순서/우선순위 착각
    DISTRIBUTIVE_LAW_ERROR = "distributive_law_error" # 분배법칙 (added from prompts)
    UNIT_CONVERSION_ERROR = "unit_conversion_error" # 단위 변환 (added from prompts)


class SolutionStep(BaseModel):
    step_number: int
    description: str = "" # content in prompt, mapping to description
    content: Optional[str] = None # Added content field to match service implementation
    formula: Optional[str] = None
    is_error: bool = False
    error_type: Optional[str] = None 
    error_explanation: Optional[str] = None

class ErroneousSolution(BaseModel):
    question_id: UUID
    original_question: str
    correct_answer: str
    erroneous_steps: List[SolutionStep]
    correct_steps: List[SolutionStep]
    error_types_used: List[ErrorType]
    metadata: Dict[str, Any] = {}

from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

# --- Metadata Schemas ---
class ExamSourceInfo(BaseModel):
    name: str = Field(..., description="Exam name e.g. 'KMC', 'HME'")
    year: Optional[int] = None
    session: Optional[str] = None
    grade: Optional[int] = None
    number: Optional[int] = None

class MathDomainInfo(BaseModel):
    major_domain: Optional[Literal["Number", "Geometry", "Measurement", "Regularity", "Data"]] = None
    advanced_topic: Optional[str] = None

class DifficultyMetrics(BaseModel):
    estimated_level: int = Field(default=1, ge=1, le=5)
    required_skills: List[str] = []

class QuestionMetadata(BaseModel):
    source: Optional[ExamSourceInfo] = None
    domain: Optional[MathDomainInfo] = None
    difficulty: Optional[DifficultyMetrics] = None
    is_twin_generated: bool = False
    original_question_id: Optional[str] = None

# Shared properties
class QuestionBase(BaseModel):
    question_type: str
    content_stem: str
    # metadata can be loose dict or structured, but we prefer structured
    content_metadata: QuestionMetadata = Field(default_factory=QuestionMetadata)
    answer_key: Dict[str, Any]
    difficulty_index: Optional[float] = 0.5
    status: Optional[str] = "draft"

# Properties to receive on Question creation
class QuestionCreate(QuestionBase):
    create_by: Optional[UUID] = None

# Properties to receive on Question update
class QuestionUpdate(QuestionBase):
    question_type: Optional[str] = None
    content_stem: Optional[str] = None
    answer_key: Optional[Dict[str, Any]] = None
    version: Optional[int] = None

# Properties shared by models stored in DB
class QuestionInDBBase(QuestionBase):
    question_id: UUID
    version: int
    created_by: Optional[UUID] = None # Added field, Nullable
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Question(QuestionInDBBase):
    pass

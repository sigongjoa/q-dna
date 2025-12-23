from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

# Shared properties
class QuestionBase(BaseModel):
    question_type: str
    content_stem: str
    content_metadata: Dict[str, Any] = {}
    answer_key: Dict[str, Any]
    difficulty_index: Optional[float] = 0.5
    status: Optional[str] = "draft"

# Properties to receive on Question creation
class QuestionCreate(QuestionBase):
    create_by: UUID

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
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Question(QuestionInDBBase):
    pass

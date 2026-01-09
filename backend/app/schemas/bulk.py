from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class BulkAttemptItem(BaseModel):
    student_id: UUID
    question_id: UUID
    is_correct: bool
    time_taken_seconds: Optional[int] = None
    notes: Optional[str] = None

class BulkSubmitRequest(BaseModel):
    items: List[BulkAttemptItem]

class BulkSubmitResponse(BaseModel):
    success_count: int
    failed_count: int
    failed_items: List[Dict[str, Any]]

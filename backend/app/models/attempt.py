from typing import Optional
from sqlalchemy import Integer, Float, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class AttemptLog(Base):
    __tablename__ = "attempt_logs"
    
    # We use composite PK in DB (log_id, attempted_at) for partitioning, 
    # but SQLAlchemy needs a primary key defined.
    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.question_id"), nullable=True)
    quiz_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    response_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    time_taken_ms: Mapped[Optional[int]] = mapped_column(Integer)
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    attempted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), primary_key=True)

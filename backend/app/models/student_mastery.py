from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class StudentMastery(Base):
    """
    Stores BKT (Bayesian Knowledge Tracing) state for each student-skill pair.
    This enables personalized learning tracking.
    """
    __tablename__ = "student_mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    skill_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)  # e.g., "Math.Algebra.Quadratics"

    # BKT Parameters
    p_mastery: Mapped[float] = mapped_column(Float, default=0.1)  # P(L) - Current mastery probability
    p_transit: Mapped[float] = mapped_column(Float, default=0.1)  # P(T) - Learning rate
    p_slip: Mapped[float] = mapped_column(Float, default=0.1)     # P(S) - Slip probability
    p_guess: Mapped[float] = mapped_column(Float, default=0.2)    # P(G) - Guess probability

    # Tracking
    attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Ensure one record per user-skill pair
        {"schema": None},
    )

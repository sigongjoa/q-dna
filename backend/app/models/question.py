from typing import List, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Text, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.core.database import Base

# Association Tables
class QuestionTag(Base):
    __tablename__ = "question_tags"
    
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.question_id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    auto_tagged: Mapped[bool] = mapped_column(Boolean, default=False)

class QuestionCurriculum(Base):
    __tablename__ = "question_curriculum"
    
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.question_id", ondelete="CASCADE"), primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("curriculum_nodes.node_id", ondelete="CASCADE"), primary_key=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)

class Question(Base):
    __tablename__ = "questions"

    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_type: Mapped[str] = mapped_column(String(50)) # mcq, short_answer, essay, matching
    content_stem: Mapped[str] = mapped_column(Text)
    content_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    answer_key: Mapped[dict] = mapped_column(JSONB)
    difficulty_index: Mapped[float] = mapped_column(Float, default=0.5)
    discrimination: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="draft") # draft, active, archived
    
    # Audit
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True) 
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tags = relationship("Tag", secondary="question_tags", back_populates="questions")
    curriculum_nodes = relationship("CurriculumNode", secondary="question_curriculum", back_populates="questions")

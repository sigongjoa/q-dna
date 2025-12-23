from typing import List, Optional
from sqlalchemy import Integer, String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_type: Mapped[str] = mapped_column(String(50), nullable=False) # concept, skill, etc
    parent_tag_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tags.tag_id"), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default={})

    # Relationships
    parent = relationship("Tag", remote_side=[tag_id], backref="children")
    questions = relationship("Question", secondary="question_tags", back_populates="tags")

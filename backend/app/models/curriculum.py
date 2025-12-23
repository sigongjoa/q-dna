from typing import List, Optional
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

# Note: We are using String for ltree path for now in Python. 
# In a real scenario with sqlalchemy-utils, we could use LtreeType.
class CurriculumNode(Base):
    __tablename__ = "curriculum_nodes"

    node_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True) # mapped as string but is ltree in DB
    standard_code: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    questions = relationship("Question", secondary="question_curriculum", back_populates="curriculum_nodes")

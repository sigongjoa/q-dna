from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from app.models.question import Question, QuestionCurriculum, QuestionTag
from app.models.curriculum import CurriculumNode
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.services.tagging_service import tagging_service
from app.models.tag import Tag

class QuestionService:
    async def create_question_with_ai(
        self, db: AsyncSession, question_in: QuestionCreate, auto_tag: bool = True
    ) -> Question:
        """
        Creates a question and optionally runs AI auto-tagging and curriculum mapping.
        Transactions are handled atomicaly.
        """
        # 1. Create Question Record
        db_question = Question(
            created_by=question_in.create_by,
            question_type=question_in.question_type,
            content_stem=question_in.content_stem,
            answer_key=question_in.answer_key,
            content_metadata=question_in.content_metadata,
            status="draft" # Starts as draft until AI review
        )
        db.add(db_question)
        await db.flush() # Flush to get UUID
        
        if auto_tag:
            # 2. AI Auto-Tagging
            # Call the AI service (Phase 4)
            recommendations = await tagging_service.get_tag_recommendations(question_in.content_stem)
            
            # 3. Apply Concepts/Tags
            for rec in recommendations:
                # Find or Create Tag (Simplistic implementation)
                stmt = select(Tag).where(Tag.name == rec["tag"], Tag.tag_type == rec["type"])
                result = await db.execute(stmt)
                tag_obj = result.scalars().first()
                
                if not tag_obj:
                    tag_obj = Tag(name=rec["tag"], tag_type=rec["type"])
                    db.add(tag_obj)
                    await db.flush()
                
                # Link Tag
                q_tag = QuestionTag(
                    question_id=db_question.question_id,
                    tag_id=tag_obj.tag_id,
                    confidence=rec["confidence"],
                    auto_tagged=True
                )
                db.add(q_tag)

            # 4. Map Curriculum (Mock logic based on AI output)
            # In real system, AI would return 'Math.Algebra.Quadratics'
            # We then find the Ltree node and link it.
            # Here we just assume a node exists for demo or skip if not found.
            pass 

            # Update status to 'review_pending' after AI processing
            db_question.status = "review_pending"
            db.add(db_question)

        await db.commit()
        await db.refresh(db_question)
        return db_question

    async def get_questions_by_curriculum(
        self, db: AsyncSession, path_query: str
    ) -> List[Question]:
        """
        Complex Query: Get all questions belonging to a curriculum subtree.
        Uses PostgreSQL ltree operator '<@' (is descendant of).
        """
        # Raw SQL might be needed if SQLAlchemy Ltree support isn't perfectly configured with async
        stmt = text("""
            SELECT q.* 
            FROM questions q
            JOIN question_curriculum qc ON q.question_id = qc.question_id
            JOIN curriculum_nodes cn ON qc.node_id = cn.node_id
            WHERE cn.path <@ :path
        """)
        result = await db.execute(stmt, {"path": path_query})
        return result.fetchall()

    async def update_question_content(
        self, db: AsyncSession, question_id: uuid.UUID, updates: QuestionUpdate
    ) -> Question:
        """
        Updates question content. The DB Trigger 'update_question_version' 
        will automatically increment version and update timestamp.
        """
        stmt = select(Question).where(Question.question_id == question_id)
        result = await db.execute(stmt)
        q = result.scalars().first()
        if not q:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(q, field, value)
            
        db.add(q)
        await db.commit()
        await db.refresh(q)
        return q

question_service = QuestionService()

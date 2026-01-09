import asyncio
from sqlalchemy import select
from app.models.question import Question, QuestionCurriculum
from app.models.curriculum import CurriculumNode
from app.core.database import SessionLocal
import random
# Imports for referencing
import app.models.tag

async def seed_links():
    async with SessionLocal() as db:
        try:
            questions = (await db.execute(select(Question))).scalars().all()
            nodes = (await db.execute(select(CurriculumNode))).scalars().all()
            
            if not questions:
                print("No questions found.")
                return
            if not nodes:
                print("No curriculum nodes found.")
                return

            # Check if links exist
            existing_links = (await db.execute(select(QuestionCurriculum))).scalars().first()
            if existing_links:
                print("Links already seeded.")
                # We can choose to return or add more. Let's return to avoid dupes.
                return

            for q in questions:
                # Assign 1-2 random nodes to each question
                selected_nodes = random.sample(nodes, k=random.randint(1, 2))
                for node in selected_nodes:
                    link = QuestionCurriculum(question_id=q.question_id, node_id=node.node_id)
                    db.add(link)
            
            await db.commit()
            print(f"Linked {len(questions)} questions to curriculum nodes.")

        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_links())

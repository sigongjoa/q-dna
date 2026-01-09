import asyncio
from sqlalchemy import select
# Ensure all models are imported for registry
import app.models.tag
import app.models.question
import app.models.curriculum
from app.models.question import Question, QuestionCurriculum
from app.models.curriculum import CurriculumNode
from app.core.database import SessionLocal
import sys

async def get_demo_data():
    async with SessionLocal() as db:
        # Find Algebra Questions
        stmt_alg = select(Question.question_id, CurriculumNode.name)\
            .join(QuestionCurriculum, Question.question_id == QuestionCurriculum.question_id)\
            .join(CurriculumNode, QuestionCurriculum.node_id == CurriculumNode.node_id)\
            .where(CurriculumNode.path.like("Math.Algebra%"))\
            .limit(5)
            
        # Find Geometry Questions
        stmt_geo = select(Question.question_id, CurriculumNode.name)\
            .join(QuestionCurriculum, Question.question_id == QuestionCurriculum.question_id)\
            .join(CurriculumNode, QuestionCurriculum.node_id == CurriculumNode.node_id)\
            .where(CurriculumNode.path.like("Math.Geometry%"))\
            .limit(5)

        res_alg_list = (await db.execute(stmt_alg)).all()
        res_geo_list = (await db.execute(stmt_geo)).all()
        
        print("---DEMO DATA---")
        for q in res_alg_list:
             print(f"ALGEBRA: {q.question_id} ({q.name})")
        
        for q in res_geo_list:
             print(f"GEOMETRY: {q.question_id} ({q.name})")
        print("---END DEMO DATA---")

if __name__ == "__main__":
    asyncio.run(get_demo_data())

import asyncio
from sqlalchemy import select
# Import all models to ensure registry is populated
import app.models.tag
import app.models.question 
from app.models.curriculum import CurriculumNode
from app.core.database import SessionLocal
import sys

async def seed_curriculum():
    async with SessionLocal() as db:
        try:
            # Check if already seeded
            result = await db.execute(select(CurriculumNode))
            if result.scalars().first():
                print("Curriculum already seeded.")
                return

            nodes = [
                {"name": "수학", "path": "Math"},
                {"name": "대수", "path": "Math.Algebra"},
                {"name": "방정식", "path": "Math.Algebra.Equations"},
                {"name": "이차방정식", "path": "Math.Algebra.Equations.Quadratic"},
                {"name": "부등식", "path": "Math.Algebra.Inequalities"},
                {"name": "함수", "path": "Math.Functions"},
                {"name": "일차함수", "path": "Math.Functions.Linear"},
                {"name": "이차함수", "path": "Math.Functions.Quadratic"},
                {"name": "기하", "path": "Math.Geometry"},
                {"name": "평면도형", "path": "Math.Geometry.Plane"},
                {"name": "삼각형", "path": "Math.Geometry.Plane.Triangles"},
                {"name": "원", "path": "Math.Geometry.Plane.Circles"},
            ]
            
            for node_data in nodes:
                node = CurriculumNode(**node_data)
                db.add(node)
            
            await db.commit()
            print("Curriculum seeded successfully.")
        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_curriculum())

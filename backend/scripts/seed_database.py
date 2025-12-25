"""
Seed database with initial curriculum structure and sample questions.
Run with: python -m scripts.seed_database
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.models.curriculum import CurriculumNode
from app.models.tag import Tag
from app.models.question import Question, QuestionTag, QuestionCurriculum
from datetime import datetime
import uuid


async def seed_curriculum(db: AsyncSession):
    """Create hierarchical curriculum structure using ltree."""
    print("📚 Seeding curriculum nodes...")

    curriculum_data = [
        # Math
        {"name": "Mathematics", "path": "Math"},
        {"name": "Algebra", "path": "Math.Algebra"},
        {"name": "Linear Equations", "path": "Math.Algebra.Linear_Equations"},
        {"name": "Quadratic Equations", "path": "Math.Algebra.Quadratic_Equations"},
        {"name": "Factoring", "path": "Math.Algebra.Quadratic_Equations.Factoring"},
        {"name": "Quadratic Formula", "path": "Math.Algebra.Quadratic_Equations.Formula"},
        {"name": "Polynomials", "path": "Math.Algebra.Polynomials"},

        {"name": "Geometry", "path": "Math.Geometry"},
        {"name": "Triangles", "path": "Math.Geometry.Triangles"},
        {"name": "Pythagorean Theorem", "path": "Math.Geometry.Triangles.Pythagorean"},
        {"name": "Circles", "path": "Math.Geometry.Circles"},
        {"name": "Angles", "path": "Math.Geometry.Angles"},

        {"name": "Calculus", "path": "Math.Calculus"},
        {"name": "Limits", "path": "Math.Calculus.Limits"},
        {"name": "Derivatives", "path": "Math.Calculus.Derivatives"},
        {"name": "Integrals", "path": "Math.Calculus.Integrals"},

        # Science
        {"name": "Science", "path": "Science"},
        {"name": "Physics", "path": "Science.Physics"},
        {"name": "Mechanics", "path": "Science.Physics.Mechanics"},
        {"name": "Kinematics", "path": "Science.Physics.Mechanics.Kinematics"},
        {"name": "Dynamics", "path": "Science.Physics.Mechanics.Dynamics"},

        {"name": "Chemistry", "path": "Science.Chemistry"},
        {"name": "Organic Chemistry", "path": "Science.Chemistry.Organic"},
        {"name": "Inorganic Chemistry", "path": "Science.Chemistry.Inorganic"},

        {"name": "Biology", "path": "Science.Biology"},
        {"name": "Cell Biology", "path": "Science.Biology.Cell"},
        {"name": "Genetics", "path": "Science.Biology.Genetics"},
    ]

    for node_data in curriculum_data:
        node = CurriculumNode(**node_data)
        db.add(node)

    await db.commit()
    print(f"✅ Created {len(curriculum_data)} curriculum nodes")


async def seed_tags(db: AsyncSession):
    """Create common tags."""
    print("🏷️  Seeding tags...")

    tags_data = [
        # Cognitive levels (Bloom's)
        {"name": "Remember", "tag_type": "cognitive_level"},
        {"name": "Understand", "tag_type": "cognitive_level"},
        {"name": "Apply", "tag_type": "cognitive_level"},
        {"name": "Analyze", "tag_type": "cognitive_level"},
        {"name": "Evaluate", "tag_type": "cognitive_level"},
        {"name": "Create", "tag_type": "cognitive_level"},

        # Subjects
        {"name": "Mathematics", "tag_type": "subject"},
        {"name": "Science", "tag_type": "subject"},
        {"name": "English", "tag_type": "subject"},

        # Math concepts
        {"name": "Algebra", "tag_type": "concept"},
        {"name": "Geometry", "tag_type": "concept"},
        {"name": "Calculus", "tag_type": "concept"},
        {"name": "Linear Equations", "tag_type": "concept"},
        {"name": "Quadratic Equations", "tag_type": "concept"},

        # Skills
        {"name": "Problem Solving", "tag_type": "skill"},
        {"name": "Critical Thinking", "tag_type": "skill"},
        {"name": "Pattern Recognition", "tag_type": "skill"},

        # Difficulty
        {"name": "Easy", "tag_type": "custom"},
        {"name": "Medium", "tag_type": "custom"},
        {"name": "Hard", "tag_type": "custom"},
    ]

    for tag_data in tags_data:
        tag = Tag(**tag_data)
        db.add(tag)

    await db.commit()
    print(f"✅ Created {len(tags_data)} tags")


async def seed_questions(db: AsyncSession):
    """Create sample questions."""
    print("📝 Seeding sample questions...")

    # Create a dummy user ID for created_by
    dummy_user = uuid.uuid4()

    questions_data = [
        {
            "question_type": "mcq",
            "content_stem": "다음 방정식을 풀어라: $2x + 5 = 13$",
            "answer_key": {"correct": "A", "choices": {"A": "x = 4", "B": "x = 3", "C": "x = 5", "D": "x = 6"}},
            "difficulty_index": 0.3,
            "status": "active",
            "created_by": dummy_user,
            "curriculum_path": "Math.Algebra.Linear_Equations",
            "tags": ["Mathematics", "Algebra", "Linear Equations", "Apply"],
        },
        {
            "question_type": "mcq",
            "content_stem": "이차방정식 $x^2 - 5x + 6 = 0$의 해를 구하시오.",
            "answer_key": {"correct": "B", "choices": {"A": "x = 1, 6", "B": "x = 2, 3", "C": "x = -2, -3", "D": "x = 0, 5"}},
            "difficulty_index": 0.5,
            "status": "active",
            "created_by": dummy_user,
            "curriculum_path": "Math.Algebra.Quadratic_Equations",
            "tags": ["Mathematics", "Algebra", "Quadratic Equations", "Apply"],
        },
        {
            "question_type": "short_answer",
            "content_stem": "피타고라스 정리를 설명하고, 빗변의 길이가 5이고 한 변의 길이가 3일 때 다른 변의 길이를 구하시오.",
            "answer_key": {"answer": "4", "explanation": "$a^2 + b^2 = c^2$이므로 $3^2 + b^2 = 5^2$, $b^2 = 16$, $b = 4$"},
            "difficulty_index": 0.45,
            "status": "active",
            "created_by": dummy_user,
            "curriculum_path": "Math.Geometry.Triangles.Pythagorean",
            "tags": ["Mathematics", "Geometry", "Understand", "Apply"],
        },
        {
            "question_type": "mcq",
            "content_stem": "함수 $f(x) = x^3 - 3x$의 극값을 구하시오.",
            "answer_key": {"correct": "C", "choices": {"A": "x = 0", "B": "x = -1", "C": "x = ±1", "D": "극값 없음"}},
            "difficulty_index": 0.7,
            "status": "active",
            "created_by": dummy_user,
            "curriculum_path": "Math.Calculus.Derivatives",
            "tags": ["Mathematics", "Calculus", "Analyze"],
        },
        {
            "question_type": "essay",
            "content_stem": "뉴턴의 운동 제2법칙 ($F = ma$)을 설명하고, 실생활 예시를 들어 설명하시오.",
            "answer_key": {"rubric": "운동 제2법칙 설명, 실생활 예시, 수식 적용"},
            "difficulty_index": 0.6,
            "status": "active",
            "created_by": dummy_user,
            "curriculum_path": "Science.Physics.Mechanics.Dynamics",
            "tags": ["Science", "Understand", "Apply"],
        },
    ]

    # Get curriculum nodes and tags
    from sqlalchemy import select
    curriculum_nodes = (await db.execute(select(CurriculumNode))).scalars().all()
    tags = (await db.execute(select(Tag))).scalars().all()

    # Create lookup maps
    curriculum_map = {node.path: node for node in curriculum_nodes}
    tag_map = {tag.name: tag for tag in tags}

    for q_data in questions_data:
        # Extract curriculum path and tags
        curriculum_path = q_data.pop("curriculum_path")
        tag_names = q_data.pop("tags")

        # Create question
        question = Question(**q_data)
        db.add(question)
        await db.flush()  # Get question_id

        # Link to curriculum
        if curriculum_path in curriculum_map:
            qc = QuestionCurriculum(
                question_id=question.question_id,
                node_id=curriculum_map[curriculum_path].node_id,
                relevance_score=1.0
            )
            db.add(qc)

        # Link to tags
        for tag_name in tag_names:
            if tag_name in tag_map:
                qt = QuestionTag(
                    question_id=question.question_id,
                    tag_id=tag_map[tag_name].tag_id,
                    confidence=0.95,
                    auto_tagged=False
                )
                db.add(qt)

    await db.commit()
    print(f"✅ Created {len(questions_data)} sample questions")


async def main():
    print("🌱 Starting database seeding...")

    async with SessionLocal() as db:
        try:
            await seed_curriculum(db)
            await seed_tags(db)
            await seed_questions(db)

            print("\n✅ Database seeding completed successfully!")
            print("\n📊 Summary:")
            print("  - Curriculum: 27 nodes")
            print("  - Tags: 20+ tags")
            print("  - Questions: 5 sample questions")

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

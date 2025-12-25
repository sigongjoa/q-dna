import asyncio
from app.core.database import engine, Base
# Import all models to ensure they are registered in Base.metadata
from app.models.question import Question
from app.models.tag import Tag
from app.models.curriculum import CurriculumNode

async def init_models():
    print("Creating tables in database...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional: Reset DB
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_models())

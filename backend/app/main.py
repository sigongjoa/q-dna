from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base

# Context7 Reference: FastAPI Lifespan Events (Standard in 0.100+)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up database connection...")
    async with engine.begin() as conn:
        # For development only: Create tables automatically
        # In production, use Alembic migrations
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    print("🛑 Shutting down database connection...")
    await engine.dispose()

from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Q-DNA Intelligent Question Bank API"}

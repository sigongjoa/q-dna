from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# Context7 Reference: FastAPI Lifespan Events (Standard in 0.100+)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up Q-DNA API...")
    print(f"📦 Ollama URL: {settings.OLLAMA_BASE_URL}")
    print(f"🧠 Vision Model: {settings.OLLAMA_VISION_MODEL}")
    print(f"💬 Text Model: {settings.OLLAMA_TEXT_MODEL}")

    # Check Ollama health
    from app.services.ollama_service import ollama_service
    ollama_healthy = await ollama_service.health_check()
    if ollama_healthy:
        print("✅ Ollama service is running")
    else:
        print("⚠️  Warning: Ollama service not accessible. AI features will fail.")

    async with engine.begin() as conn:
        # For development only: Create tables automatically
        # In production, use Alembic migrations
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database connected")

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Q-DNA Intelligent Question Bank API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.ollama_service import ollama_service

    ollama_status = await ollama_service.health_check()

    return {
        "status": "healthy",
        "database": "connected",
        "ollama": "connected" if ollama_status else "disconnected"
    }

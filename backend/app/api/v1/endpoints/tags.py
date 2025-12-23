from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.tag import Tag
from pydantic import BaseModel

router = APIRouter()

class TagSchema(BaseModel):
    tag_id: int
    name: str
    tag_type: str

class TagCreate(BaseModel):
    name: str
    tag_type: str

@router.get("/", response_model=List[TagSchema])
async def read_tags(
    skip: int = 0,
    limit: int = 100,
    type: str | None = None,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve tags.
    """
    query = select(Tag).offset(skip).limit(limit)
    if type:
        query = query.where(Tag.tag_type == type)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=TagSchema)
async def create_tag(
    tag_in: TagCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Create new tag.
    """
    tag = Tag(name=tag_in.name, tag_type=tag_in.tag_type)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag

@router.get("/suggest")
async def suggest_tags(
    text: str,
) -> Any:
    """
    AI Tag Suggestion Endpoint (Phase 4.2).
    """
    from app.services.tagging_service import tagging_service
    return await tagging_service.get_tag_recommendations(text)

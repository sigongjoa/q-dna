from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.curriculum import CurriculumNode
from pydantic import BaseModel

router = APIRouter()

class CurriculumNodeSchema(BaseModel):
    node_id: int
    name: str
    path: str
    description: str | None = None
    children: List['CurriculumNodeSchema'] = []

@router.get("/tree", response_model=List[CurriculumNodeSchema])
async def get_curriculum_tree(
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Get full curriculum tree.
    Fetches flat list from DB and reconstructs tree in memory.
    """
    result = await db.execute(select(CurriculumNode).order_by(CurriculumNode.path))
    nodes = result.scalars().all()

    # Convert to dictionary for O(1) access
    node_map = {node.path: CurriculumNodeSchema(
        node_id=node.node_id,
        name=node.name,
        path=node.path,
        description=node.description,
        children=[]
    ) for node in nodes}

    root_nodes = []

    for node in nodes:
        if "." in node.path:
            parent_path = node.path.rsplit(".", 1)[0]
            if parent_path in node_map:
                node_map[parent_path].children.append(node_map[node.path])
            else:
                # Parent missing or it's a root-like node in a sub-query context
                root_nodes.append(node_map[node.path])
        else:
            root_nodes.append(node_map[node.path])

    return root_nodes

@router.post("/", response_model=CurriculumNodeSchema)
async def create_node(
    name: str,
    path: str,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    node = CurriculumNode(name=name, path=path)
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return CurriculumNodeSchema(
        node_id=node.node_id, 
        name=node.name, 
        path=node.path, 
        description=node.description
    )

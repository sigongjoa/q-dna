from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.diagram_service import diagram_service

router = APIRouter()

class DiagramRequest(BaseModel):
    description: str

class DiagramResponse(BaseModel):
    image_url: str

@router.post("/generate", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    try:
        if not request.description:
            raise HTTPException(status_code=400, detail="Description is required")
            
        image_url = await diagram_service.generate_diagram(request.description)
        return DiagramResponse(image_url=image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

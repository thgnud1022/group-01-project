from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])

class StandardizeRequest(BaseModel):
    raw_text: str

@router.post("/standardize-pr")
def standardize_pr(req: StandardizeRequest):
    if not req.raw_text:
        raise HTTPException(status_code=400, detail="Nội dung văn bản thô không được để trống.")
    return AIService.standardize_pr(req.raw_text)

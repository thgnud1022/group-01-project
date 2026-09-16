from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/quotations", tags=["Quotations & AI Compare"])

class CompareRequest(BaseModel):
    purchaseRequestId: str
    files: List[str]

@router.post("/compare")
def compare_quotations(payload: CompareRequest):
    return {
        "purchaseRequestId": payload.purchaseRequestId,
        "comparisons": AIService.compare_quotations(payload.purchaseRequestId, payload.files)
    }

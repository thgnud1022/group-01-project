from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.procurement_service import ProcurementService, db

router = APIRouter(prefix="/api/po", tags=["Purchase Order"])

class CreatePOSchema(BaseModel):
    purchaseRequestId: str
    quotationId: Optional[str] = None
    creatorId: str = "procurement@company.com"
    # Optional fields for backward-compatibility or client attempts to send extra data
    quotation: Optional[Dict[str, Any]] = None
    totalAmount: Optional[float] = None
    quantity: Optional[int] = None

@router.post("")
def create_po(payload: CreatePOSchema):
    # REQ-BR-12: Resolve quotationId server-side; NEVER trust client payload for prices or quantities
    quotation_id = payload.quotationId
    if not quotation_id and payload.quotation:
        quotation_id = payload.quotation.get("quotation_id") or payload.quotation.get("id")

    if not quotation_id:
        raise HTTPException(status_code=400, detail="quotationId là bắt buộc để tạo Purchase Order")

    try:
        return ProcurementService.create_po(
            pr_id=payload.purchaseRequestId,
            quotation_id=quotation_id,
            creator_id=payload.creatorId,
            quotation=payload.quotation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_pos():
    return list(db.pos.values())


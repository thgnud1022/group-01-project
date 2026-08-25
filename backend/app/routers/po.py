from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.procurement_service import ProcurementService, db

router = APIRouter(prefix="/api/po", tags=["Purchase Order"])

class CreatePOSchema(BaseModel):
    purchaseRequestId: str
    quotation: Dict[str, Any]
    creatorId: str = "procurement@company.com"

@router.post("")
def create_po(payload: CreatePOSchema):
    try:
        return ProcurementService.create_po(
            pr_id=payload.purchaseRequestId,
            quotation=payload.quotation,
            creator_id=payload.creatorId
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_pos():
    return list(db.pos.values())

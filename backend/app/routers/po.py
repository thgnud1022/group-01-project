from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.procurement_service import ProcurementService
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.dependencies.rbac import RoleChecker

router = APIRouter(prefix="/api/po", tags=["Purchase Order"])

class CreatePOSchema(BaseModel):
    purchaseRequestId: str
    quotationId: Optional[str] = None
    creatorId: Optional[str] = "procurement@company.com"  # Retained for schema compatibility, overwritten by server
    # Optional fields for backward-compatibility or client attempts to send extra data
    quotation: Optional[Dict[str, Any]] = None
    totalAmount: Optional[float] = None
    quantity: Optional[int] = None

@router.post("")
async def create_po(
    payload: CreatePOSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["PROCUREMENT", "ADMIN"])
    ),
):
    # REQ-BR-12: Resolve quotationId server-side; NEVER trust client payload for prices or quantities
    quotation_id = payload.quotationId
    if not quotation_id and payload.quotation:
        quotation_id = payload.quotation.get("quotation_id") or payload.quotation.get("id")

    if not quotation_id:
        raise HTTPException(status_code=400, detail="quotationId là bắt buộc để tạo Purchase Order")

    try:
        # HD-02 / HD-12: creatorId is derived directly from verified JWT identity
        return await ProcurementService.create_po_prisma(
            pr_id=payload.purchaseRequestId,
            quotation_id=quotation_id,
            creator_user_id=current_user.id,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
async def list_pos(
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    try:
        return await ProcurementService.list_pos_prisma()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn danh sách PO: {str(e)}")

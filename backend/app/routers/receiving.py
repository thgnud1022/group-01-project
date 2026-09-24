from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.procurement_service import ProcurementService
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.dependencies.rbac import RoleChecker

router = APIRouter(prefix="/api/receiving", tags=["Goods Receipt"])

class ReceivingSchema(BaseModel):
    purchaseOrderId: str
    receivedQty: int
    fileUrl: str = "https://example.com/bien-ban-giao-nhan.pdf"
    receivedItems: Optional[str] = None

@router.post("")
async def receive_goods(
    payload: ReceivingSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["PROCUREMENT", "ADMIN"])
    ),
):
    """
    Record goods receipt in Supabase PostgreSQL (REQ-BR-04, US-09).
    Human Decision K-3: Restricted to PROCUREMENT and ADMIN roles.
    """
    try:
        return await ProcurementService.receive_goods_prisma(
            po_id=payload.purchaseOrderId,
            received_qty=payload.receivedQty,
            file_url=payload.fileUrl,
            received_items=payload.receivedItems,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
async def list_receivings(
    purchaseOrderId: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    List receivings from Supabase PostgreSQL.
    Human Decision K-1: Accessible to all authenticated users.
    """
    try:
        return await ProcurementService.list_receivings_prisma(purchaseOrderId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn phiếu nhận hàng: {str(e)}")

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.procurement_service import ProcurementService

router = APIRouter(prefix="/api/receiving", tags=["Goods Receipt"])

class ReceivingSchema(BaseModel):
    purchaseOrderId: str
    receivedQty: int
    fileUrl: str = "https://example.com/bien-ban-giao-nhan.pdf"
    receivedItems: Optional[str] = None

@router.post("")
async def receive_goods(payload: ReceivingSchema):
    try:
        return await ProcurementService.receive_goods_prisma(
            po_id=payload.purchaseOrderId,
            received_qty=payload.receivedQty,
            file_url=payload.fileUrl,
            received_items=payload.receivedItems,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
async def list_receivings(purchaseOrderId: Optional[str] = None):
    try:
        return await ProcurementService.list_receivings_prisma(purchaseOrderId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn phiếu nhận hàng: {str(e)}")

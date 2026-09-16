from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.procurement_service import ProcurementService

router = APIRouter(prefix="/api/receiving", tags=["Goods Receipt"])

class ReceivingSchema(BaseModel):
    purchaseOrderId: str
    receivedQty: int
    fileUrl: str = "https://example.com/ biên-bản-giao-nhận.pdf"

@router.post("")
def receive_goods(payload: ReceivingSchema):
    try:
        return ProcurementService.receive_goods(
            po_id=payload.purchaseOrderId,
            received_qty=payload.receivedQty,
            file_url=payload.fileUrl
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

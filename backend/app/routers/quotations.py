from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
from app.services.procurement_service import ProcurementService
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.dependencies.rbac import RoleChecker

router = APIRouter(prefix="/api/quotations", tags=["Quotations & Comparison"])
pr_quotations_router = APIRouter(prefix="/api/purchase-requests", tags=["Purchase Request Quotations"])

class QuotationCreateSchema(BaseModel):
    purchaseRequestId: str
    supplierId: str
    totalAmount: float
    quantity: int
    deliveryDays: int = 3
    warrantyTerms: Optional[str] = None
    fileUrl: str = "quotes/default.pdf"

class CompareRequest(BaseModel):
    purchaseRequestId: str
    files: Optional[List[str]] = None

@router.post("")
async def create_quotation(
    payload: QuotationCreateSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["PROCUREMENT", "ADMIN"])
    ),
):
    """
    Create and persist a new Quotation directly in Supabase PostgreSQL (T-052 / T-053).
    Enforces:
    - Role: PROCUREMENT, ADMIN
    - PR exists and status == APPROVED (T-052 Guard)
    - Supplier exists (T-053 Integrity)
    - quantity > 0, totalAmount > 0
    - Derived Decimal unitPrice
    """
    try:
        return await ProcurementService.create_quotation_prisma(
            purchase_request_id=payload.purchaseRequestId,
            supplier_id=payload.supplierId,
            total_amount=payload.totalAmount,
            quantity=payload.quantity,
            delivery_days=payload.deliveryDays,
            warranty_terms=payload.warrantyTerms,
            file_url=payload.fileUrl,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
async def list_quotations(
    purchaseRequestId: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """List all quotations from PostgreSQL, optionally filtered by purchaseRequestId."""
    try:
        return await ProcurementService.list_quotations_prisma(purchaseRequestId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn báo giá: {str(e)}")

@router.get("/{quotation_id}")
async def get_quotation(
    quotation_id: str,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """Retrieve quotation by ID from PostgreSQL, including derived unitPrice and supplier details."""
    try:
        return await ProcurementService.get_quotation_prisma(quotation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@pr_quotations_router.get("/{pr_id}/quotations")
async def list_quotations_for_pr(
    pr_id: str,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """Retrieve all quotations for a specific PR from PostgreSQL (T-061)."""
    try:
        return await ProcurementService.list_quotations_by_pr_prisma(pr_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/compare")
async def compare_quotations(
    payload: CompareRequest,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    Compare quotations for a PR reading directly from Supabase PostgreSQL (T-061).
    Zero MockDB read/write, zero external LLM dependencies.
    Human Decision K-2: Accessible to all authenticated users.
    """
    try:
        comparisons = await ProcurementService.compare_quotations_prisma(payload.purchaseRequestId)
        return {
            "purchaseRequestId": payload.purchaseRequestId,
            "comparisons": comparisons
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
AI Assistant Router (TASK-009 / US-01 / US-07).
Provides PR Standardization and Quotation Recommendation endpoints.
Secured by Server-Side JWT Authentication (HD-12 / HD-13 Policy K-1).
"""
from fastapi import APIRouter, HTTPException, Depends
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.schemas.ai import (
    StandardizeRequest,
    StandardizeResponseSchema,
    QuotationRecommendationRequest,
    QuotationRecommendationResponse,
    QuotationInputItem,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/standardize-pr", response_model=StandardizeResponseSchema)
async def standardize_pr(
    req: StandardizeRequest,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    Standardize raw user input into structured Purchase Request items using Real LLM (Gemini)
    or Fast Deterministic Fallback Parser (HD-03).
    Accessible to all authenticated users (HD-13 Policy K-1).
    """
    if not req.raw_text or not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="Nội dung văn bản thô không được để trống.")
    return await AIService.standardize_pr_async(req.raw_text.strip())


@router.post("/recommend-quotations", response_model=QuotationRecommendationResponse)
async def recommend_quotations(
    req: QuotationRecommendationRequest,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    Generate AI-driven comparative recommendation and ranking across candidate quotations (US-07 / REQ-FR-14).
    Pure decision support — does NOT write to database, select supplier, or bypass approval rules.
    Accessible to all authenticated users (HD-13 Policy K-1).
    """
    # Enforce PostgreSQL data authority if purchase_request_id exists in DB
    if req.purchase_request_id and req.purchase_request_id.strip():
        try:
            from app.services.procurement_service import ProcurementService
            db_comparisons = await ProcurementService.compare_quotations_prisma(req.purchase_request_id.strip())
            if db_comparisons and len(db_comparisons) >= 2:
                req.quotations = [
                    QuotationInputItem(
                        quotation_id=q["id"],
                        supplier_name=q.get("supplierName") or (q.get("supplier", {}).get("name") if isinstance(q.get("supplier"), dict) else "Nhà cung cấp"),
                        total_amount=float(q["totalAmount"]),
                        unit_price=float(q["unitPrice"]),
                        quantity=int(q.get("quantity", 1)),
                        delivery_days=int(q.get("deliveryDays", 0)),
                        warranty_terms=q.get("warrantyTerms"),
                        valid_until=q.get("validUntil").isoformat() if hasattr(q.get("validUntil"), "isoformat") else (str(q.get("validUntil")) if q.get("validUntil") else None),
                        is_anomaly=bool(q.get("isAnomaly", False)),
                        anomaly_reason=q.get("anomalyReason"),
                        is_expired=bool(q.get("isExpired", False)),
                    )
                    for q in db_comparisons
                ]
        except Exception:
            # Fall back to client-provided quotations if PR is not in DB or error
            pass

    if not req.quotations:
        raise HTTPException(status_code=400, detail="Danh sách báo giá không được rỗng.")
    return await AIService.recommend_quotations_async(req)

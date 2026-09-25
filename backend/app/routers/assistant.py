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
    if not req.quotations:
        raise HTTPException(status_code=400, detail="Danh sách báo giá không được rỗng.")
    return await AIService.recommend_quotations_async(req)

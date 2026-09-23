from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.procurement_service import ProcurementService, db

router = APIRouter(prefix="/api/pr", tags=["Purchase Request"])

class PRItemSchema(BaseModel):
    itemName: str
    quantity: int
    estimatedUnitPrice: float

class CreatePRSchema(BaseModel):
    departmentId: str
    creatorId: str
    title: str
    items: List[PRItemSchema]

class ApprovePRSchema(BaseModel):
    approverEmail: str
    comments: Optional[str] = "Phê duyệt PR"

@router.post("")
async def create_pr(payload: CreatePRSchema):
    try:
        items_dict = [item.model_dump() for item in payload.items]
        return await ProcurementService.create_pr_prisma(
            dept_id=payload.departmentId,
            creator_id=payload.creatorId,
            title=payload.title,
            items=items_dict
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_prs():
    return list(db.prs.values())

@router.post("/{pr_id}/approve")
async def approve_pr(pr_id: str, payload: ApprovePRSchema):
    try:
        return await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email=payload.approverEmail,
            comments=payload.comments
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{pr_id}/close")
def close_pr(pr_id: str, finance_user: str = "finance@company.com"):
    try:
        return ProcurementService.close_pr(pr_id, finance_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{pr_id}/quotations")
async def list_pr_quotations(pr_id: str):
    """Retrieve all quotations for a specific PR from PostgreSQL (T-061)."""
    try:
        return await ProcurementService.list_quotations_by_pr_prisma(pr_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


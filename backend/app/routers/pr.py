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
    approverRole: str
    approverName: str
    comments: Optional[str] = "Phê duyệt PR"

@router.post("")
def create_pr(payload: CreatePRSchema):
    try:
        items_dict = [item.model_dump() for item in payload.items]
        return ProcurementService.create_pr(
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
def approve_pr(pr_id: str, payload: ApprovePRSchema):
    try:
        return ProcurementService.approve_pr(
            pr_id=pr_id,
            approver_role=payload.approverRole,
            approver_name=payload.approverName,
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

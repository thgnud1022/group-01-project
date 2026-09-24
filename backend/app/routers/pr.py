from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.procurement_service import ProcurementService, db
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.dependencies.rbac import RoleChecker

router = APIRouter(prefix="/api/pr", tags=["Purchase Request"])

class PRItemSchema(BaseModel):
    itemName: str
    quantity: int
    estimatedUnitPrice: float

class CreatePRSchema(BaseModel):
    departmentId: str
    creatorId: Optional[str] = None  # Retained for schema compatibility, overwritten by server
    title: str
    items: List[PRItemSchema]

class ApprovePRSchema(BaseModel):
    approverEmail: Optional[str] = None  # Retained for schema compatibility, overwritten by server
    comments: Optional[str] = "Phê duyệt PR"

@router.post("")
async def create_pr(
    payload: CreatePRSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["EMPLOYEE", "MANAGER", "PROCUREMENT", "FINANCE", "ADMIN"])
    ),
):
    try:
        items_dict = [item.model_dump() for item in payload.items]
        # HD-02 / HD-12: creatorId is derived directly from verified JWT identity
        return await ProcurementService.create_pr_prisma(
            dept_id=payload.departmentId,
            creator_user_id=current_user.id,
            title=payload.title,
            items=items_dict,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_prs(
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    return list(db.prs.values())

@router.post("/{pr_id}/approve")
async def approve_pr(
    pr_id: str,
    payload: Optional[ApprovePRSchema] = None,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["MANAGER", "FINANCE", "ADMIN"])
    ),
):
    try:
        comments = payload.comments if (payload and payload.comments) else "Phê duyệt PR"
        # HD-12: Acting approver identity is derived directly from verified JWT current_user
        return await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            current_user=current_user,
            comments=comments,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{pr_id}/close")
async def close_pr(
    pr_id: str,
    finance_user: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(RoleChecker(["FINANCE", "ADMIN"])),
):
    try:
        # HD-12: Actor identity derived from verified JWT current_user.id
        return await ProcurementService.close_pr_prisma(
            pr_id=pr_id,
            actor_user_id=current_user.id,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{pr_id}/quotations")
async def list_pr_quotations(
    pr_id: str,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """Retrieve all quotations for a specific PR from PostgreSQL (T-061)."""
    try:
        return await ProcurementService.list_quotations_by_pr_prisma(pr_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

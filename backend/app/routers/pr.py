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
async def list_prs(
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    try:
        from app.services.db import get_prisma, connect_db
        await connect_db()
        prisma = get_prisma()
        prs = await prisma.purchaserequest.find_many(
            include={"items": True, "department": True, "creator": True, "approvals": True, "quotations": True},
            order={"created_at": "desc"}
        )
        res = []
        for p in prs:
            created_val = getattr(p, 'created_at', getattr(p, 'createdAt', None))
            linked_quotes_count = len(getattr(p, 'quotations', []) or [])
            res.append({
                "id": p.id,
                "title": p.title,
                "departmentId": p.departmentId,
                "deptId": p.departmentId,
                "departmentName": p.department.name if p.department else p.departmentId,
                "creatorId": p.creatorId,
                "creatorName": p.creator.name if (p.creator and hasattr(p.creator, 'name')) else (getattr(p.creator, 'fullName', p.creatorId) if p.creator else p.creatorId),
                "estimatedValue": float(p.estimatedValue),
                "status": p.status,
                "linkedQuotes": linked_quotes_count,
                "quotations": [
                    {
                        "id": q.id,
                        "supplierId": q.supplierId,
                        "totalAmount": float(q.totalAmount),
                        "unitPrice": round(float(q.totalAmount) / max(1, q.quantity), 2),
                        "quantity": q.quantity,
                        "deliveryDays": q.deliveryDays,
                    }
                    for q in (getattr(p, 'quotations', []) or [])
                ],
                "createdAt": created_val.isoformat() if created_val else None,
                "items": [
                    {
                        "id": it.id,
                        "itemName": it.itemName,
                        "quantity": it.quantity,
                        "estimatedUnitPrice": float(it.estimatedUnitPrice),
                    }
                    for it in (p.items or [])
                ],
                "approvals": [
                    {
                        "id": a.id,
                        "approverId": a.approverId,
                        "stage": getattr(a, 'stage', getattr(a, 'decision', 'APPROVAL')),
                        "action": getattr(a, 'action', getattr(a, 'decision', 'APPROVED')),
                        "decision": getattr(a, 'decision', getattr(a, 'action', 'APPROVED')),
                        "comments": a.comments,
                        "timestamp": getattr(a, 'timestamp', getattr(a, 'created_at', None)).isoformat() if getattr(a, 'timestamp', getattr(a, 'created_at', None)) else None,
                    }
                    for a in (p.approvals or [])
                ]
            })
        return res
    except Exception as e:
        import traceback
        print(f"[list_prs ERROR] {e}\n{traceback.format_exc()}")
        return list(db.prs.values())

@router.get("/{pr_id}")
async def get_pr(
    pr_id: str,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    try:
        from app.services.db import get_prisma, connect_db
        await connect_db()
        prisma = get_prisma()
        p = await prisma.purchaserequest.find_unique(
            where={"id": pr_id},
            include={"items": True, "department": True, "creator": True, "approvals": True}
        )
        if p:
            created_val = getattr(p, 'createdAt', getattr(p, 'created_at', None))
            return {
                "id": p.id,
                "title": p.title,
                "departmentId": p.departmentId,
                "deptId": p.departmentId,
                "departmentName": p.department.name if p.department else p.departmentId,
                "creatorId": p.creatorId,
                "creatorName": p.creator.name if (p.creator and hasattr(p.creator, 'name')) else (getattr(p.creator, 'fullName', p.creatorId) if p.creator else p.creatorId),
                "estimatedValue": float(p.estimatedValue),
                "status": p.status,
                "createdAt": created_val.isoformat() if created_val else None,
                "items": [
                    {
                        "id": it.id,
                        "itemName": it.itemName,
                        "quantity": it.quantity,
                        "estimatedUnitPrice": float(it.estimatedUnitPrice),
                    }
                    for it in (p.items or [])
                ],
                "approvals": [
                    {
                        "id": a.id,
                        "approverId": a.approverId,
                        "stage": getattr(a, 'stage', getattr(a, 'decision', 'APPROVAL')),
                        "action": getattr(a, 'action', getattr(a, 'decision', 'APPROVED')),
                        "decision": getattr(a, 'decision', getattr(a, 'action', 'APPROVED')),
                        "comments": a.comments,
                        "timestamp": getattr(a, 'timestamp', getattr(a, 'created_at', None)).isoformat() if getattr(a, 'timestamp', getattr(a, 'created_at', None)) else None,
                    }
                    for a in (p.approvals or [])
                ]
            }
    except Exception as e:
        pass
    if pr_id in db.prs:
        return db.prs[pr_id]
    raise HTTPException(status_code=404, detail=f"Không tìm thấy Purchase Request {pr_id}")

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

class RejectPRSchema(BaseModel):
    comments: str  # Mandatory rejection reason per US-04 AC2

class RevisionPRSchema(BaseModel):
    comments: str  # Mandatory revision comment/reason per US-04 AC2 / HD-16

class ResubmitItemSchema(BaseModel):
    itemName: str
    quantity: int
    estimatedUnitPrice: float

class ResubmitPRSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    items: Optional[List[ResubmitItemSchema]] = None
    comments: Optional[str] = None

@router.post("/{pr_id}/revision")
async def request_revision(
    pr_id: str,
    payload: RevisionPRSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["MANAGER", "FINANCE", "ADMIN"])
    ),
):
    """
    Request Revision endpoint (HD-16 / REQ-FR-06 / US-03 AC3 / US-04 AC2).
    Authorized roles: MANAGER, FINANCE, ADMIN.
    Rejects EMPLOYEE, PROCUREMENT with 403.
    Enforces GOV-01 No Self-Action.
    """
    try:
        return await ProcurementService.request_revision_prisma(
            pr_id=pr_id,
            current_user=current_user,
            comments=payload.comments,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{pr_id}/resubmit")
async def resubmit_pr(
    pr_id: str,
    payload: Optional[ResubmitPRSchema] = None,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    Resubmit PR endpoint (HD-16).
    Authorized actor: Verified PR creator or ADMIN.
    Requires PR.status == REVISION_REQUIRED.
    Re-validates data, recalculates budget, transitions to PENDING_MANAGER_APPROVAL.
    """
    try:
        items_dict = [it.dict() for it in payload.items] if (payload and payload.items is not None) else None
        title = payload.title if payload else None
        description = payload.description if payload else None
        comments = payload.comments if payload else None

        return await ProcurementService.resubmit_pr_prisma(
            pr_id=pr_id,
            current_user=current_user,
            title=title,
            description=description,
            items=items_dict,
            comments=comments,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{pr_id}/reject")
async def reject_pr(
    pr_id: str,
    payload: RejectPRSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["MANAGER", "FINANCE", "ADMIN"])
    ),
):
    try:
        # HD-12: Acting approver identity is derived directly from verified JWT current_user
        return await ProcurementService.reject_pr_prisma(
            pr_id=pr_id,
            current_user=current_user,
            comments=payload.comments,
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

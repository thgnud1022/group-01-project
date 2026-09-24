from fastapi import APIRouter, HTTPException, Depends
from app.services.procurement_service import ProcurementService, db
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.dependencies.rbac import RoleChecker

router = APIRouter(prefix="/api/budget", tags=["Department Budget"])

@router.get("/{dept_id}")
def get_department_budget(
    dept_id: str,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    Get budget for a specific department.
    Accessible to all authenticated users (US-04, US-05).
    """
    try:
        return ProcurementService.get_budget(dept_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
def list_budgets(
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["FINANCE", "ADMIN"])
    ),
):
    """
    List all departmental budgets.
    Restricted to FINANCE and ADMIN roles.
    """
    return [ProcurementService.get_budget(d) for d in db.budgets]

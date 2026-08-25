from fastapi import APIRouter, HTTPException
from app.services.procurement_service import ProcurementService, db

router = APIRouter(prefix="/api/budget", tags=["Department Budget"])

@router.get("/{dept_id}")
def get_department_budget(dept_id: str):
    try:
        return ProcurementService.get_budget(dept_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
def list_budgets():
    return [ProcurementService.get_budget(d) for d in db.budgets]

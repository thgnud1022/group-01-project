from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.procurement_service import ProcurementService
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.dependencies.rbac import RoleChecker

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

class SupplierCreateSchema(BaseModel):
    name: str
    taxCode: Optional[str] = None
    contact: Optional[str] = None

class SupplierResponseSchema(BaseModel):
    id: str
    name: str
    taxCode: Optional[str] = None
    contact: Optional[str] = None

@router.post("", response_model=SupplierResponseSchema)
async def create_supplier(
    payload: SupplierCreateSchema,
    current_user: AuthenticatedUser = Depends(
        RoleChecker(["PROCUREMENT", "ADMIN"])
    ),
):
    """
    Create a new Supplier in Supabase PostgreSQL (US-06, T-17).
    Restricted to PROCUREMENT and ADMIN roles.
    """
    try:
        return await ProcurementService.create_supplier_prisma(
            name=payload.name,
            tax_code=payload.taxCode,
            contact=payload.contact,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[SupplierResponseSchema])
async def list_suppliers(
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    List all Suppliers from Supabase PostgreSQL.
    Human Decision K-1: Accessible to all authenticated users.
    """
    try:
        return await ProcurementService.list_suppliers_prisma()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn nhà cung cấp: {str(e)}")

@router.get("/{supplier_id}", response_model=SupplierResponseSchema)
async def get_supplier(
    supplier_id: str,
    current_user: AuthenticatedUser = Depends(get_current_identity),
):
    """
    Get Supplier details by ID from Supabase PostgreSQL.
    Human Decision K-1: Accessible to all authenticated users.
    """
    try:
        return await ProcurementService.get_supplier_prisma(supplier_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

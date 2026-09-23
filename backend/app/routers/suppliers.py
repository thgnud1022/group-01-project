from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.procurement_service import ProcurementService

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
async def create_supplier(payload: SupplierCreateSchema):
    """Create a new Supplier in Supabase PostgreSQL."""
    try:
        return await ProcurementService.create_supplier_prisma(
            name=payload.name,
            tax_code=payload.taxCode,
            contact=payload.contact,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[SupplierResponseSchema])
async def list_suppliers():
    """List all Suppliers from Supabase PostgreSQL."""
    try:
        return await ProcurementService.list_suppliers_prisma()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn nhà cung cấp: {str(e)}")

@router.get("/{supplier_id}", response_model=SupplierResponseSchema)
async def get_supplier(supplier_id: str):
    """Get Supplier details by ID from Supabase PostgreSQL."""
    try:
        return await ProcurementService.get_supplier_prisma(supplier_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

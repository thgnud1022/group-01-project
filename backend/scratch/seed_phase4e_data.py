"""
Seed fresh test data in PostgreSQL for Phase 4E Browser E2E.
Creates:
1. Fresh APPROVED PR: '2026 MacBook Pro upgrade for design team'
2. Two valid Quotations for comparison (SUP-01 & SUP-02)
Zero side effects on existing production data.
"""

import asyncio
import json
import uuid
from decimal import Decimal
from prisma import Prisma

async def main():
    prisma = Prisma()
    await prisma.connect()
    
    # 1. Look up employee creator & department
    emp = await prisma.user.find_unique(where={"email": "employee@company.com"})
    if not emp:
        raise ValueError("User employee@company.com not found")
        
    dept = await prisma.department.find_first()
    dept_id = dept.id if dept else "DEPT-IT"

    # Ensure SUP-01 and SUP-02 exist
    sup1 = await prisma.supplier.find_unique(where={"name": "TechSource Distribution"})
    if not sup1:
        sup1 = await prisma.supplier.create(
            data={"name": "TechSource Distribution", "taxCode": "TAX-TECHSOURCE", "contact": "sales@techsource.com"}
        )

    sup2 = await prisma.supplier.find_unique(where={"name": "Global Tech Solutions"})
    if not sup2:
        sup2 = await prisma.supplier.create(
            data={"name": "Global Tech Solutions", "taxCode": "TAX-GLOBALTECH", "contact": "sales@globaltech.com"}
        )

    # 2. Create fresh APPROVED PR
    pr_id = f"PR-4E-{uuid.uuid4().hex[:6].upper()}"
    pr = await prisma.purchaserequest.create(
        data={
            "id": pr_id,
            "title": "2026 MacBook Pro upgrade for design team",
            "description": "Replenishment for engineering & design team",
            "status": "APPROVED",
            "creatorId": emp.id,
            "departmentId": dept_id,
            "estimatedValue": Decimal("20000000.00"),
            "items": {
                "create": [
                    {
                        "itemName": "MacBook Pro M3 Max",
                        "quantity": 2,
                        "estimatedUnitPrice": Decimal("10000000.00")
                    }
                ]
            }
        }
    )

    # 3. Create Quotation 1 (TechSource)
    q1 = await prisma.quotation.create(
        data={
            "purchaseRequestId": pr.id,
            "supplierId": sup1.id,
            "totalAmount": Decimal("18000000.00"),
            "quantity": 2,
            "deliveryDays": 3,
            "warrantyTerms": "24 months manufacturer warranty",
            "fileUrl": "https://company.storage/quotes/techsource_macbook.pdf"
        }
    )

    # 4. Create Quotation 2 (Global Tech)
    q2 = await prisma.quotation.create(
        data={
            "purchaseRequestId": pr.id,
            "supplierId": sup2.id,
            "totalAmount": Decimal("19500000.00"),
            "quantity": 2,
            "deliveryDays": 5,
            "warrantyTerms": "12 months warranty",
            "fileUrl": "https://company.storage/quotes/globaltech_macbook.pdf"
        }
    )

    await prisma.disconnect()

    result = {
        "prId": pr.id,
        "prTitle": pr.title,
        "q1Id": q1.id,
        "q1Supplier": sup1.name,
        "q1Amount": float(q1.totalAmount),
        "q2Id": q2.id,
        "q2Supplier": sup2.name,
        "q2Amount": float(q2.totalAmount),
    }
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(main())

"""
Seed script for Phase 4F Browser E2E testing.
Creates:
- A fresh PR with 1 item (quantity: 5, unitPrice: 2,000,000)
- PR status: APPROVED
- 1 Quotation (supplier: TechSource Distribution, totalAmount: 10,000,000, quantity: 5)
- 1 Purchase Order (status: SENT, quantity: 5, totalAmount: 10,000,000)
"""

import sys
import asyncio
import json
import uuid
from decimal import Decimal

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from prisma import Prisma

async def seed_data():
    prisma = Prisma()
    await prisma.connect()

    suffix = uuid.uuid4().hex[:6].upper()
    pr_id = f"PR-4F-{suffix}"

    # 1. Fetch or create Department
    dept = await prisma.department.find_first(where={"id": "DEPT-IT"})
    if not dept:
        dept = await prisma.department.create(
            data={"id": "DEPT-IT", "name": "Information Technology"}
        )

    # 2. Fetch employee user
    creator = await prisma.user.find_first(where={"email": "employee@company.com"})
    if not creator:
        creator = await prisma.user.create(
            data={
                "id": str(uuid.uuid4()),
                "email": "employee@company.com",
                "fullName": "Nguyen Van A",
                "departmentId": dept.id,
                "role": "EMPLOYEE",
            }
        )

    # 3. Create PR
    pr = await prisma.purchaserequest.create(
        data={
            "id": pr_id,
            "title": f"4K Monitors for Design Team ({suffix})",
            "departmentId": dept.id,
            "creatorId": creator.id,
            "estimatedValue": Decimal("10000000.00"),
            "status": "APPROVED",
        }
    )

    # Add item
    await prisma.pritem.create(
        data={
            "purchaseRequestId": pr.id,
            "itemName": "4K Ultra-Sharp Monitor",
            "quantity": 5,
            "estimatedUnitPrice": Decimal("2000000.00"),
        }
    )

    # 4. Fetch or create Supplier
    supplier = await prisma.supplier.find_first(where={"name": "TechSource Distribution"})
    if not supplier:
        supplier = await prisma.supplier.create(
            data={
                "id": str(uuid.uuid4()),
                "name": "TechSource Distribution",
                "contact": "sales@techsource.com",
            }
        )

    # 5. Create Quotation
    quote = await prisma.quotation.create(
        data={
            "id": str(uuid.uuid4()),
            "purchaseRequestId": pr.id,
            "supplierId": supplier.id,
            "totalAmount": Decimal("10000000.00"),
            "quantity": 5,
            "deliveryDays": 3,
            "warrantyTerms": "24 months manufacturer warranty",
            "fileUrl": "https://company.storage/quotes/techsource_4k.pdf",
            "isAnomaly": False,
        }
    )

    # 6. Fetch procurement user for PO
    proc_user = await prisma.user.find_first(where={"email": "procurement@company.com"})
    if not proc_user:
        proc_user = await prisma.user.create(
            data={
                "id": str(uuid.uuid4()),
                "email": "procurement@company.com",
                "fullName": "Le Thi C",
                "departmentId": dept.id,
                "role": "PROCUREMENT",
            }
        )

    po_num = f"PO-NUM-2026-4F-{suffix}"
    po = await prisma.purchaseorder.create(
        data={
            "id": str(uuid.uuid4()),
            "purchaseRequestId": pr.id,
            "quotationId": quote.id,
            "poNumber": po_num,
            "creatorId": proc_user.id,
            "totalAmount": Decimal("10000000.00"),
            "quantity": 5,
            "status": "SENT",
        }
    )

    await prisma.disconnect()

    output = {
        "prId": pr.id,
        "poId": po.id,
        "poNumber": po.poNumber,
        "quotationId": quote.id,
        "quantity": 5,
        "totalAmount": 10000000,
        "supplierName": supplier.name,
    }
    print(json.dumps(output))

if __name__ == "__main__":
    asyncio.run(seed_data())

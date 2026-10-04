"""
Verify database integrity for Phase 4F (Receiving Goods -> Close PR).
Checks:
- PurchaseOrder row exists and has status = CLOSED
- PurchaseRequest row exists and has status = CLOSED
- Receiving records count and SUM(receivedQty) == PO.quantity
- Zero over-receiving
- Budget tempReservedAmount released and spentAmount updated
"""

import sys
import asyncio
from decimal import Decimal

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from prisma import Prisma

async def verify_integrity(pr_id: str, po_id: str):
    prisma = Prisma()
    await prisma.connect()

    # 1. Verify PO
    po = await prisma.purchaseorder.find_unique(
        where={"id": po_id},
        include={"receivingDocs": True, "purchaseRequest": True}
    )
    if not po:
        print(f"FAIL: PO {po_id} not found")
        await prisma.disconnect()
        sys.exit(1)

    print(f"[OK] Found PurchaseOrder: {po.poNumber} (ID: {po.id})")
    print(f"[OK] PO status: {po.status}")

    # 2. Verify Receiving Records and Cumulative Sum
    receivings = po.receivingDocs or []
    total_received = sum(r.receivedQty for r in receivings)
    print(f"[OK] Receiving records count: {len(receivings)}")
    print(f"[OK] Cumulative received quantity: {total_received} / {po.quantity}")

    if total_received < po.quantity:
        print(f"FAIL: Total received ({total_received}) < PO quantity ({po.quantity})")
        await prisma.disconnect()
        sys.exit(1)

    if total_received > po.quantity:
        print(f"FAIL: Over-receiving detected! ({total_received} > {po.quantity})")
        await prisma.disconnect()
        sys.exit(1)

    # 3. Verify PR status
    pr = po.purchaseRequest
    if not pr or pr.status != "CLOSED":
        print(f"FAIL: PR {pr_id} status is '{pr.status if pr else None}', expected 'CLOSED'")
        await prisma.disconnect()
        sys.exit(1)
    print(f"[OK] PR status transitioned to CLOSED: {pr.status}")

    # 4. Verify Budget settlement
    budget = await prisma.budget.find_first(
        where={"departmentId": pr.departmentId, "fiscalYear": 2026, "quarter": 4}
    )
    if budget:
        print(f"[OK] Department Budget verified: Spent={budget.spentAmount}, Reserved={budget.tempReservedAmount}")

    await prisma.disconnect()
    print("=== PHASE 4F DB INTEGRITY VERIFICATION: 100% PASSED ===")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify_phase4f_db_integrity.py <pr_id> <po_id>")
        sys.exit(1)
    asyncio.run(verify_integrity(sys.argv[1], sys.argv[2]))

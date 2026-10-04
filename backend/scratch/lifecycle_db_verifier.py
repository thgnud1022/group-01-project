"""
lifecycle_db_verifier.py
Comprehensive PostgreSQL verifier and snapshot utility for the FINAL FULL LIFECYCLE E2E.
"""

import sys
import json
import asyncio
from decimal import Decimal
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from prisma import Prisma

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def capture_snapshot(pr_id: str, milestone_label: str):
    prisma = Prisma()
    await prisma.connect()

    try:
        pr = await prisma.purchaserequest.find_unique(
            where={"id": pr_id},
            include={
                "creator": True,
                "department": True,
                "approvals": {"include": {"approver": True}},
                "quotations": {"include": {"supplier": True}},
                "purchaseOrders": {
                    "include": {
                        "quotation": {"include": {"supplier": True}},
                        "receivingDocs": True,
                        "creator": True,
                    }
                }
            }
        )

        if not pr:
            print(json.dumps({"error": f"PR {pr_id} not found"}, ensure_ascii=False, indent=2))
            return None

        # Fetch department budget line
        budget = await prisma.budget.find_first(
            where={"departmentId": pr.departmentId}
        )

        # Calculate receiving statistics
        total_received = 0
        pos_data = []
        for po in pr.purchaseOrders or []:
            po_received = sum(r.receivedQty for r in (po.receivingDocs or []))
            total_received += po_received
            pos_data.append({
                "poId": po.id,
                "poNumber": po.poNumber,
                "status": po.status,
                "quantity": po.quantity,
                "totalAmount": float(po.totalAmount),
                "supplierName": po.quotation.supplier.name if po.quotation and po.quotation.supplier else None,
                "supplierId": po.quotation.supplierId if po.quotation else None,
                "receivedQtySum": po_received,
                "receivingDocs": [
                    {
                        "id": r.id,
                        "receivedQty": r.receivedQty,
                        "receivedItems": r.receivedItems,
                        "receivedDate": r.receivedDate.isoformat() if r.receivedDate else None,
                    } for r in (po.receivingDocs or [])
                ]
            })

        snapshot = {
            "milestone": milestone_label,
            "timestamp": datetime.now().isoformat(),
            "pr": {
                "id": pr.id,
                "title": pr.title,
                "status": pr.status,
                "estimatedValue": float(pr.estimatedValue),
                "departmentId": pr.departmentId,
                "departmentName": pr.department.name if pr.department else None,
                "creator": {
                    "id": pr.creator.id if pr.creator else None,
                    "name": pr.creator.name if pr.creator else None,
                    "email": pr.creator.email if pr.creator else None,
                    "role": pr.creator.role if pr.creator else None,
                },
                "approvals": [
                    {
                        "id": app.id,
                        "decision": app.decision,
                        "comments": app.comments,
                        "approverName": app.approver.name if app.approver else None,
                        "approverEmail": app.approver.email if app.approver else None,
                        "approverRole": app.approver.role if app.approver else None,
                        "createdAt": app.created_at.isoformat() if app.created_at else None,
                    } for app in (pr.approvals or [])
                ],
                "quotationsCount": len(pr.quotations or []),
                "quotations": [
                    {
                        "id": q.id,
                        "supplierId": q.supplierId,
                        "supplierName": q.supplier.name if q.supplier else None,
                        "totalAmount": float(q.totalAmount),
                        "quantity": q.quantity,
                        "deliveryDays": q.deliveryDays,
                        "warrantyTerms": q.warrantyTerms,
                        "isAnomaly": q.isAnomaly,
                    } for q in (pr.quotations or [])
                ],
                "purchaseOrdersCount": len(pos_data),
                "purchaseOrders": pos_data,
                "totalReceivedUnits": total_received,
            },
            "budget": {
                "departmentId": budget.departmentId if budget else None,
                "fiscalYear": budget.fiscalYear if budget else None,
                "allocatedAmount": float(budget.allocatedAmount) if budget else 0.0,
                "spentAmount": float(budget.spentAmount) if budget else 0.0,
                "tempReservedAmount": float(budget.tempReservedAmount) if budget else 0.0,
            } if budget else None
        }

        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        return snapshot

    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python lifecycle_db_verifier.py <PR_ID> <MILESTONE_LABEL>")
        sys.exit(1)

    pr_id_arg = sys.argv[1]
    milestone_arg = sys.argv[2]
    asyncio.run(capture_snapshot(pr_id_arg, milestone_arg))

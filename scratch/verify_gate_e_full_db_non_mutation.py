import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.ai_service import AIService
from app.services.procurement_service import ProcurementService

async def run_gate_e_audit():
    await connect_db()
    prisma = get_prisma()
    pr_id = "PR-2026-001"

    print("=== GATE E: AI ZERO SIDE-EFFECT VERIFICATION ===")
    print("1. Capturing pre-AI database baseline...")

    # PR Baseline
    pr_before = await prisma.purchaserequest.find_unique(where={"id": pr_id})
    assert pr_before is not None, f"PR {pr_id} must exist in DB"
    status_before = pr_before.status
    updated_at_before = pr_before.updated_at

    # Quotations Baseline
    quotes_before = await prisma.quotation.find_many(where={"purchaseRequestId": pr_id}, order={"id": "asc"})
    quotes_before_summary = [
        {"id": q.id, "supplierId": q.supplierId, "totalAmount": float(q.totalAmount), "quantity": q.quantity}
        for q in quotes_before
    ]

    # Suppliers Baseline
    suppliers_before = await prisma.supplier.find_many()
    suppliers_before_count = len(suppliers_before)

    # Approvals Baseline
    approvals_before = await prisma.approval.find_many(where={"purchaseRequestId": pr_id})
    approvals_before_count = len(approvals_before)

    # PO Baseline
    pos_before = await prisma.purchaseorder.find_many()
    pos_before_count = len(pos_before)

    # Receiving / GoodsReceipt Baseline
    # Check if table exists
    try:
        receipts_before = await prisma.receiving.find_many()
        receipts_before_count = len(receipts_before)
    except Exception:
        receipts_before_count = 0

    print(f"  PR Status: {status_before}")
    print(f"  Quotation Count: {len(quotes_before_summary)}")
    print(f"  Supplier Count: {suppliers_before_count}")
    print(f"  Approval Count: {approvals_before_count}")
    print(f"  PO Count: {pos_before_count}")
    print(f"  Receiving Count: {receipts_before_count}")

    print("\n2. Executing AI Analysis / Recommendation via AIService...")
    # Load authoritative facts from DB as the router does
    from app.schemas.ai import QuotationInputItem
    comparison = await ProcurementService.compare_quotations_prisma(pr_id)
    items = []
    for q in comparison:
        items.append(
            QuotationInputItem(
                quotation_id=q["id"],
                supplier_name=q.get("supplierName") or (q.get("supplier", {}).get("name") if isinstance(q.get("supplier"), dict) else "Nhà cung cấp"),
                total_amount=float(q["totalAmount"]),
                unit_price=float(q["unitPrice"]),
                quantity=int(q.get("quantity", 1)),
                delivery_days=int(q.get("deliveryDays", 0)),
                warranty_terms=q.get("warrantyTerms"),
                valid_until=q.get("validUntil").isoformat() if hasattr(q.get("validUntil"), "isoformat") else (str(q.get("validUntil")) if q.get("validUntil") else None),
                flags=q.get("flags", [])
            )
        )

    from app.schemas.ai import QuotationRecommendationRequest
    req = QuotationRecommendationRequest(
        purchase_request_id=pr_id,
        pr_title="PR-2026-001 Hardware",
        quotations=items,
        deterministic_anomalies=[]
    )
    ai_result = await AIService.recommend_quotations_async(req)
    print(f"  AI Execution complete. Mode: {'FALLBACK' if ai_result.is_fallback else 'LIVE'}")
    print(f"  Recommended quote: {ai_result.recommended_quotation_id} (score {ai_result.rankings[0].score if ai_result.rankings else 'N/A'})")

    print("\n3. Capturing post-AI database state and verifying against baseline...")
    pr_after = await prisma.purchaserequest.find_unique(where={"id": pr_id})
    quotes_after = await prisma.quotation.find_many(where={"purchaseRequestId": pr_id}, order={"id": "asc"})
    quotes_after_summary = [
        {"id": q.id, "supplierId": q.supplierId, "totalAmount": float(q.totalAmount), "quantity": q.quantity}
        for q in quotes_after
    ]
    suppliers_after = await prisma.supplier.find_many()
    approvals_after = await prisma.approval.find_many(where={"purchaseRequestId": pr_id})
    pos_after = await prisma.purchaseorder.find_many()
    try:
        receipts_after = await prisma.receiving.find_many()
        receipts_after_count = len(receipts_after)
    except Exception:
        receipts_after_count = 0

    await disconnect_db()

    # Assertions
    assert pr_after.status == status_before, f"PR Status mutated! Expected {status_before}, got {pr_after.status}"
    assert pr_after.updated_at == updated_at_before, f"PR updatedAt timestamp changed!"
    assert quotes_after_summary == quotes_before_summary, "Quotation records or values mutated!"
    assert len(suppliers_after) == suppliers_before_count, "Supplier records count changed!"
    assert len(approvals_after) == approvals_before_count, "Approval records count changed!"
    assert len(pos_after) == pos_before_count, f"PO created! Expected {pos_before_count}, got {len(pos_after)}"
    assert receipts_after_count == receipts_before_count, "Receiving records count changed!"

    print("\n=== GATE E RESULT: 100% PASS ===")
    print("Baseline Comparison Table:")
    print("| Metric | Pre-AI Baseline | Post-AI State | Status |")
    print("| :--- | :--- | :--- | :--- |")
    print(f"| PR Status | {status_before} | {pr_after.status} | UNCHANGED (PASS) |")
    print(f"| Quotation Count & Values | {len(quotes_before_summary)} quotes | {len(quotes_after_summary)} quotes | UNCHANGED (PASS) |")
    print(f"| Supplier Count | {suppliers_before_count} | {len(suppliers_after)} | UNCHANGED (PASS) |")
    print(f"| Approval Count | {approvals_before_count} | {len(approvals_after)} | UNCHANGED (PASS) |")
    print(f"| PO Count | {pos_before_count} | {len(pos_after)} | UNCHANGED (PASS) |")
    print(f"| Receiving Count | {receipts_before_count} | {receipts_after_count} | UNCHANGED (PASS) |")

if __name__ == "__main__":
    asyncio.run(run_gate_e_audit())

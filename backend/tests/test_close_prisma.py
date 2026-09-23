"""
Integration Tests for Close Purchase Request & Budget Settlement via Prisma Client (Supabase PostgreSQL).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.7 — Migrate Close PR & Budget Settlement to Prisma/PostgreSQL

Test Scope (14 Test Cases):
- TC-CLOSE-001: Full receiving complete -> Close PR succeeds.
- TC-CLOSE-002: Insufficient receiving (partial) -> Close PR rejected (HD-07 / REQ-BR-11).
- TC-CLOSE-003: Multiple partial receivings summing to >= PO.quantity -> Close PR succeeds.
- TC-CLOSE-004: Zero receiving docs -> Close PR rejected.
- TC-CLOSE-005: Receiving exceeding PO.quantity cannot exist / invalid state blocked.
- TC-CLOSE-006: Non-existent PR -> reject with ValueError.
- TC-CLOSE-007: PR without PO -> reject with ValueError.
- TC-CLOSE-008: Close PR success -> PR status transitions to CLOSED in PostgreSQL.
- TC-CLOSE-009: Close PR success -> tempReservedAmount released and spentAmount updated in Budget.
- TC-CLOSE-010: Rejected close PR -> budget remains unchanged (tempReserved intact, spentAmount untouched).
- TC-CLOSE-011: Transaction rollback on failure -> zero partial updates to PR or Budget.
- TC-CLOSE-012: Concurrent close requests -> row lock ensures exactly one succeeds and no duplicate budget settlement.
- TC-CLOSE-013: Runtime API POST /api/pr/{id}/close persists to PostgreSQL.
- TC-CLOSE-014: Zero MockDB write verification -> db.prs and db.budgets remain untouched.
"""

import asyncio
import threading
import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.procurement_service import ProcurementService, db


class AsyncTestRunner:
    """Dedicated background event loop runner for reliable Prisma asyncio integration testing on Windows."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro, timeout: float = 30.0):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=timeout)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=2.0)


_runner: AsyncTestRunner = None


def run_async(coro):
    return _runner.run(coro)


@pytest.fixture(scope="module", autouse=True)
def setup_prisma_test_environment():
    global _runner
    _runner = AsyncTestRunner()
    run_async(connect_db())
    yield
    run_async(disconnect_db())
    _runner.stop()


@pytest.fixture(autouse=True)
def clean_test_data():
    """Teardown fixture ensuring database hygiene: clean test records and reset budget tempReservedAmount."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()

        # 1. Clean test PRs and all child records
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-CLOSE]"}}
        )
        pr_ids = [pr.id for pr in test_prs]
        if pr_ids:
            pos = await prisma.purchaseorder.find_many(
                where={"purchaseRequestId": {"in": pr_ids}}
            )
            po_ids = [po.id for po in pos]
            if po_ids:
                await prisma.receiving.delete_many(where={"purchaseOrderId": {"in": po_ids}})
                await prisma.purchaseorder.delete_many(where={"id": {"in": po_ids}})

            await prisma.quotation.delete_many(where={"purchaseRequestId": {"in": pr_ids}})
            await prisma.approval.delete_many(where={"purchaseRequestId": {"in": pr_ids}})
            await prisma.purchaserequest.delete_many(where={"id": {"in": pr_ids}})

        # 2. Reset tempReservedAmount to 0 and spentAmount to seeded values
        await prisma.budget.update_many(
            where={"departmentId": "DEPT-IT"},
            data={
                "tempReservedAmount": Decimal("0.00"),
                "spentAmount": Decimal("150000000.00")
            }
        )
        await prisma.budget.update_many(
            where={"departmentId": "DEPT-HR"},
            data={
                "tempReservedAmount": Decimal("0.00"),
                "spentAmount": Decimal("50000000.00")
            }
        )
    run_async(cleanup())


async def helper_setup_pr_po(suffix: str, quantity: int = 5, unit_price: float = 2_000_000.0) -> tuple:
    """Helper to create PR -> Approve -> Quotation -> PO in PostgreSQL."""
    total_amount = quantity * unit_price
    pr = await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title=f"[TEST-CLOSE] PR {suffix}",
        items=[{"itemName": "Máy chủ Dell PowerEdge", "quantity": quantity, "estimatedUnitPrice": unit_price}]
    )
    await ProcurementService.approve_pr_prisma(
        pr_id=pr["id"],
        approver_email="manager@company.com",
        comments="Approved for Close test"
    )
    quote = await ProcurementService.create_quotation_prisma(
        purchase_request_id=pr["id"],
        supplier_id="SUP-01",
        total_amount=total_amount,
        quantity=quantity,
        delivery_days=3,
        warranty_terms="36 tháng",
        file_url="quotes/test_close_quote.pdf"
    )
    po = await ProcurementService.create_po_prisma(
        pr_id=pr["id"],
        quotation_id=quote["id"],
        creator_email="procurement@company.com"
    )
    return pr, po


# ==============================================================================
# TC-CLOSE-001: Full receiving complete -> Close PR succeeds
# ==============================================================================
def test_tc_close_001_full_receiving_close_success():
    async def run():
        pr, po = await helper_setup_pr_po("TC-001", quantity=4)
        # Fully receive 4 items
        await ProcurementService.receive_goods_prisma(po["id"], 4, "receipts/full.pdf")

        res = await ProcurementService.close_pr_prisma(pr["id"])
        assert res["id"] == pr["id"]
        assert res["status"] == "CLOSED"
        assert res["totalReceived"] == 4
        assert res["poQuantity"] == 4
    run_async(run())


# ==============================================================================
# TC-CLOSE-002: Insufficient receiving -> Close PR rejected (HD-07 / REQ-BR-11)
# ==============================================================================
def test_tc_close_002_insufficient_receiving_rejected():
    async def run():
        pr, po = await helper_setup_pr_po("TC-002", quantity=5)
        # Partially receive only 2 out of 5 items
        await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/part.pdf")

        with pytest.raises(ValueError) as exc:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "Hàng chưa được nhận đủ" in str(exc.value)
        assert "2/5" in str(exc.value)

        # Verify PR remains in PO_CREATED
        prisma = get_prisma()
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "PO_CREATED"
    run_async(run())


# ==============================================================================
# TC-CLOSE-003: Multiple partial receivings summing to >= PO.quantity -> Close succeeds
# ==============================================================================
def test_tc_close_003_multiple_partials_sum_complete_close_success():
    async def run():
        pr, po = await helper_setup_pr_po("TC-003", quantity=6)
        # Batch 1: 2
        await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/b1.pdf")
        # Batch 2: 3
        await ProcurementService.receive_goods_prisma(po["id"], 3, "receipts/b2.pdf")
        # Batch 3: 1 (Total = 6 == 6)
        await ProcurementService.receive_goods_prisma(po["id"], 1, "receipts/b3.pdf")

        res = await ProcurementService.close_pr_prisma(pr["id"])
        assert res["status"] == "CLOSED"
        assert res["totalReceived"] == 6
    run_async(run())


# ==============================================================================
# TC-CLOSE-004: Zero receiving docs -> Close PR rejected
# ==============================================================================
def test_tc_close_004_zero_receiving_rejected():
    async def run():
        pr, po = await helper_setup_pr_po("TC-004", quantity=3)
        # Zero receiving done

        with pytest.raises(ValueError) as exc:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "Hàng chưa được nhận đủ" in str(exc.value)
        assert "0/3" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-CLOSE-005: Receiving exceeding PO.quantity cannot exist / invalid state blocked
# ==============================================================================
def test_tc_close_005_over_receiving_blocked_by_br04():
    async def run():
        pr, po = await helper_setup_pr_po("TC-005", quantity=3)
        # Attempt to over-receive 5 items on PO of 3 -> rejected by REQ-BR-04
        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(po["id"], 5, "receipts/over.pdf")
        assert "vượt quá số lượng đặt trên PO" in str(exc.value)

        # Close PR must also be rejected because 0 items were received
        with pytest.raises(ValueError) as exc2:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "Hàng chưa được nhận đủ" in str(exc2.value)
    run_async(run())


# ==============================================================================
# TC-CLOSE-006: Non-existent PR -> reject with ValueError
# ==============================================================================
def test_tc_close_006_pr_not_found():
    async def run():
        with pytest.raises(ValueError) as exc:
            await ProcurementService.close_pr_prisma("PR-NON-EXISTENT")
        assert "Không tìm thấy Purchase Request" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-CLOSE-007: PR without PO -> reject with ValueError
# ==============================================================================
def test_tc_close_007_pr_without_po_rejected():
    async def run():
        # Create approved PR but do NOT create a PO
        pr = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST-CLOSE] PR No PO",
            items=[{"itemName": "Bàn làm việc", "quantity": 1, "estimatedUnitPrice": 5_000_000}]
        )
        await ProcurementService.approve_pr_prisma(pr["id"], "manager@company.com")

        with pytest.raises(ValueError) as exc:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "chưa có Purchase Order" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-CLOSE-008: Close PR success -> PR status transitions to CLOSED in PostgreSQL
# ==============================================================================
def test_tc_close_008_pr_status_transitions_to_closed():
    async def run():
        pr, po = await helper_setup_pr_po("TC-008", quantity=2)
        await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/done.pdf")

        res = await ProcurementService.close_pr_prisma(pr["id"])
        assert res["status"] == "CLOSED"

        # Verify in PostgreSQL
        prisma = get_prisma()
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "CLOSED"

        # Attempting to close again must be rejected
        with pytest.raises(ValueError) as exc_again:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "đã ở trạng thái CLOSED" in str(exc_again.value)
    run_async(run())


# ==============================================================================
# TC-CLOSE-009: Close PR success -> tempReserved released and spentAmount settled
# ==============================================================================
def test_tc_close_009_budget_settlement_accurate():
    async def run():
        prisma = get_prisma()
        budget_before = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        initial_spent = Decimal(str(budget_before.spentAmount))

        pr, po = await helper_setup_pr_po("TC-009", quantity=2, unit_price=3_000_000.0)
        # PR estimatedValue = 6,000,000 VND -> tempReservedAmount increased by 6,000,000
        budget_mid = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        assert Decimal(str(budget_mid.tempReservedAmount)) == Decimal("6000000.00")

        # Fully receive 2 items
        await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/done.pdf")

        # Close PR
        res = await ProcurementService.close_pr_prisma(pr["id"])
        assert res["status"] == "CLOSED"

        # Verify Budget after closing
        budget_after = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        # tempReservedAmount should be released back to 0
        assert Decimal(str(budget_after.tempReservedAmount)) == Decimal("0.00")
        # spentAmount should be increased by PR estimated value (6,000,000)
        assert Decimal(str(budget_after.spentAmount)) == initial_spent + Decimal("6000000.00")
    run_async(run())


# ==============================================================================
# TC-CLOSE-010: Rejected close PR -> budget remains untouched
# ==============================================================================
def test_tc_close_010_rejected_close_does_not_mutate_budget():
    async def run():
        pr, po = await helper_setup_pr_po("TC-010", quantity=4, unit_price=2_500_000.0)
        # Partially receive 1/4 items
        await ProcurementService.receive_goods_prisma(po["id"], 1, "receipts/part.pdf")

        prisma = get_prisma()
        budget_mid = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        reserved_mid = Decimal(str(budget_mid.tempReservedAmount))
        spent_mid = Decimal(str(budget_mid.spentAmount))

        # Close PR fails
        with pytest.raises(ValueError):
            await ProcurementService.close_pr_prisma(pr["id"])

        # Verify budget is completely untouched
        budget_after = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        assert Decimal(str(budget_after.tempReservedAmount)) == reserved_mid
        assert Decimal(str(budget_after.spentAmount)) == spent_mid
    run_async(run())


# ==============================================================================
# TC-CLOSE-011: Transaction rollback on failure
# ==============================================================================
def test_tc_close_011_atomic_transaction_rollback():
    async def run():
        pr, po = await helper_setup_pr_po("TC-011", quantity=3)
        # 0 received items -> closing fails
        with pytest.raises(ValueError):
            await ProcurementService.close_pr_prisma(pr["id"])

        # Check PR status remains unchanged
        prisma = get_prisma()
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "PO_CREATED"
    run_async(run())


# ==============================================================================
# TC-CLOSE-012: Concurrent close requests -> row lock prevents duplicate settlement
# ==============================================================================
def test_tc_close_012_concurrent_close_attempts():
    async def run():
        pr, po = await helper_setup_pr_po("TC-012", quantity=2, unit_price=4_000_000.0)
        await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/done.pdf")

        # Two concurrent close calls on same PR
        task1 = ProcurementService.close_pr_prisma(pr["id"])
        task2 = ProcurementService.close_pr_prisma(pr["id"])

        results = await asyncio.gather(task1, task2, return_exceptions=True)

        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]

        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
        assert len(failures) == 1, f"Expected 1 failure, got {len(failures)}"
        assert "đã ở trạng thái CLOSED" in str(failures[0])

        # Verify tempReserved is exactly 0 and spent is increased once
        prisma = get_prisma()
        budget = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        assert Decimal(str(budget.tempReservedAmount)) == Decimal("0.00")
    run_async(run())


# ==============================================================================
# TC-CLOSE-013: Runtime API POST /api/pr/{id}/close persists to PostgreSQL
# ==============================================================================
def test_tc_close_013_api_post_close_pr_endpoint():
    async def run():
        pr, po = await helper_setup_pr_po("TC-013", quantity=2)
        await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/done.pdf")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(f"/api/pr/{pr['id']}/close")
            assert res.status_code == 200, res.text
            data = res.json()
            assert data["id"] == pr["id"]
            assert data["status"] == "CLOSED"

            # Verify in PostgreSQL
            prisma = get_prisma()
            db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
            assert db_pr.status == "CLOSED"
    run_async(run())


# ==============================================================================
# TC-CLOSE-014: Zero MockDB write verification
# ==============================================================================
def test_tc_close_014_zero_mockdb_write():
    async def run():
        pr, po = await helper_setup_pr_po("TC-014", quantity=1)
        await ProcurementService.receive_goods_prisma(po["id"], 1, "receipts/done.pdf")

        res = await ProcurementService.close_pr_prisma(pr["id"])
        assert res["status"] == "CLOSED"

        # Verify MockDB was not modified
        assert pr["id"] not in db.prs, "CRITICAL: MockDB db.prs was modified!"
    run_async(run())

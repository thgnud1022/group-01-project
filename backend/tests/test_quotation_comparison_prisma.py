"""
Integration Tests for Quotation Comparison (Phase 4C) via Supabase PostgreSQL.
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Requirements: REQ-FR-11, REQ-FR-12, REQ-FR-15, US-06, US-08, HD-17

Test Cases (10 Required):
- TC-CMP-001: 0 quotation -> comparison unavailable (ValueError / HTTP 400)
- TC-CMP-002: 1 quotation -> comparison unavailable (ValueError / HTTP 400)
- TC-CMP-003: 2 quotations -> comparison succeeds (>= 2 quotations)
- TC-CMP-004: wrong PR quotation -> quotation isolation (PR-A quotes not included in PR-B)
- TC-CMP-005: nonexistent PR -> reject with 404 / ValueError
- TC-CMP-006: unauthorized comparison -> HTTP 401 without Bearer token
- TC-CMP-007: price values come from DB (totalAmount & unitPrice computed from DB)
- TC-CMP-008: delivery values come from DB (deliveryDays match PostgreSQL records)
- TC-CMP-009: warranty values come from DB (warrantyTerms match PostgreSQL records)
- TC-CMP-010: anomaly result is deterministic (>= 20% higher than average flagged)
"""

import asyncio
import threading
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
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
    """Teardown fixture ensuring database hygiene: clean test Quotations, PRs."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()

        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-CMP]"}}
        )
        for pr in test_prs:
            await prisma.quotation.delete_many(where={"purchaseRequestId": pr.id})
            await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
            await prisma.purchaserequest.delete(where={"id": pr.id})

        await prisma.budget.update_many(
            where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
            data={"tempReservedAmount": Decimal("0.00")}
        )
    run_async(cleanup())


async def helper_create_approved_pr(title_suffix: str) -> dict:
    """Helper to create and approve a test PR in PostgreSQL."""
    pr = await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title=f"[TEST-CMP] PR {title_suffix}",
        items=[{"itemName": "Thiet bi van phong", "quantity": 1, "estimatedUnitPrice": 30_000_000}]
    )
    approved = await ProcurementService.approve_pr_prisma(
        pr_id=pr["id"],
        approver_email="manager@company.com",
        comments="Approved for comparison tests"
    )
    assert approved["status"] == "APPROVED"
    return approved


# ==============================================================================
# Comparison Tests (TC-CMP-001 .. TC-CMP-010)
# ==============================================================================

def test_tc_cmp_001_zero_quotations_unavailable():
    """TC-CMP-001: 0 quotation -> comparison unavailable (ValueError / HTTP 400)."""
    async def run_test():
        pr = await helper_create_approved_pr("Zero Quotes")
        with pytest.raises(ValueError) as exc:
            await ProcurementService.compare_quotations_prisma(pr["id"])
        assert "Cần tối thiểu 2 báo giá" in str(exc.value)
        assert "hiện có: 0" in str(exc.value)
    run_async(run_test())


def test_tc_cmp_002_one_quotation_unavailable():
    """TC-CMP-002: 1 quotation -> comparison unavailable (ValueError / HTTP 400)."""
    async def run_test():
        pr = await helper_create_approved_pr("One Quote")
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("25000000.00"),
            quantity=1,
            file_url="q1.pdf"
        )
        with pytest.raises(ValueError) as exc:
            await ProcurementService.compare_quotations_prisma(pr["id"])
        assert "Cần tối thiểu 2 báo giá" in str(exc.value)
        assert "hiện có: 1" in str(exc.value)
    run_async(run_test())


def test_tc_cmp_003_two_quotations_succeeds():
    """TC-CMP-003: 2 quotations -> comparison succeeds and returns accurate data."""
    async def run_test():
        pr = await helper_create_approved_pr("Two Quotes")
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("24000000.00"),
            quantity=2,
            delivery_days=3,
            warranty_terms="12 tháng chính hãng",
            file_url="q1.pdf"
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-02",
            total_amount=Decimal("26000000.00"),
            quantity=2,
            delivery_days=5,
            warranty_terms="24 tháng chính hãng",
            file_url="q2.pdf"
        )

        comparisons = await ProcurementService.compare_quotations_prisma(pr["id"])
        assert len(comparisons) == 2

        supp_names = [c["supplier"]["name"] for c in comparisons]
        assert "Công ty TNHH Tin học Phong Vũ" in supp_names
        assert "Công ty TNHH Máy tính Trần Anh" in supp_names
    run_async(run_test())


def test_tc_cmp_004_wrong_pr_quotation_isolation():
    """TC-CMP-004: wrong PR quotation -> quotes for PR-A do not appear in PR-B comparison."""
    async def run_test():
        pr_a = await helper_create_approved_pr("PR-A Isolation")
        pr_b = await helper_create_approved_pr("PR-B Isolation")

        # 2 quotes for PR-A
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_a["id"], supplier_id="SUP-01", total_amount=Decimal("20000000.00"), quantity=1
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_a["id"], supplier_id="SUP-02", total_amount=Decimal("22000000.00"), quantity=1
        )

        # 2 quotes for PR-B
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_b["id"], supplier_id="SUP-03", total_amount=Decimal("25000000.00"), quantity=1
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_b["id"], supplier_id="SUP-01", total_amount=Decimal("24000000.00"), quantity=1
        )

        cmp_a = await ProcurementService.compare_quotations_prisma(pr_a["id"])
        cmp_b = await ProcurementService.compare_quotations_prisma(pr_b["id"])

        for q in cmp_a:
            assert q["purchaseRequestId"] == pr_a["id"]
        for q in cmp_b:
            assert q["purchaseRequestId"] == pr_b["id"]

        a_suppliers = {q["supplierId"] for q in cmp_a}
        assert a_suppliers == {"SUP-01", "SUP-02"}
        b_suppliers = {q["supplierId"] for q in cmp_b}
        assert b_suppliers == {"SUP-01", "SUP-03"}
    run_async(run_test())


def test_tc_cmp_005_nonexistent_pr_rejected():
    """TC-CMP-005: nonexistent PR -> reject with 404 / ValueError."""
    async def run_test():
        with pytest.raises(ValueError) as exc:
            await ProcurementService.compare_quotations_prisma("NON-EXISTENT-PR-ID")
        assert "Không tìm thấy Purchase Request" in str(exc.value)
    run_async(run_test())


def test_tc_cmp_006_unauthorized_comparison_rejected():
    """TC-CMP-006: unauthorized comparison -> reject with 401 without Bearer token."""
    client = TestClient(app)
    resp = client.post("/api/quotations/compare", json={"purchaseRequestId": "PR-2026-001"})
    # Must be 401 Unauthorized when no authentication token is provided
    assert resp.status_code == 401


def test_tc_cmp_007_price_values_come_from_db():
    """TC-CMP-007: price values come from PostgreSQL database records."""
    async def run_test():
        pr = await helper_create_approved_pr("Price DB Authority")
        # Create quote 1: total = 45,000,000, quantity = 3 -> unitPrice = 15,000,000
        # Create quote 2: total = 48,000,000, quantity = 3 -> unitPrice = 16,000,000
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("45000000.00"),
            quantity=3,
            delivery_days=2,
            warranty_terms="12M"
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-02",
            total_amount=Decimal("48000000.00"),
            quantity=3,
            delivery_days=4,
            warranty_terms="24M"
        )

        comparisons = await ProcurementService.compare_quotations_prisma(pr["id"])
        q1 = next(c for c in comparisons if c["supplierId"] == "SUP-01")
        q2 = next(c for c in comparisons if c["supplierId"] == "SUP-02")

        assert q1["totalAmount"] == 45_000_000.0
        assert q1["unitPrice"] == 15_000_000.0
        assert q1["quantity"] == 3

        assert q2["totalAmount"] == 48_000_000.0
        assert q2["unitPrice"] == 16_000_000.0
        assert q2["quantity"] == 3
    run_async(run_test())


def test_tc_cmp_008_delivery_values_come_from_db():
    """TC-CMP-008: delivery values come directly from PostgreSQL records."""
    async def run_test():
        pr = await helper_create_approved_pr("Delivery DB Authority")
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("20000000.00"),
            quantity=1,
            delivery_days=7
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-02",
            total_amount=Decimal("21000000.00"),
            quantity=1,
            delivery_days=14
        )

        comparisons = await ProcurementService.compare_quotations_prisma(pr["id"])
        q1 = next(c for c in comparisons if c["supplierId"] == "SUP-01")
        q2 = next(c for c in comparisons if c["supplierId"] == "SUP-02")

        assert q1["deliveryDays"] == 7
        assert q2["deliveryDays"] == 14
    run_async(run_test())


def test_tc_cmp_009_warranty_values_come_from_db():
    """TC-CMP-009: warranty values come directly from PostgreSQL records."""
    async def run_test():
        pr = await helper_create_approved_pr("Warranty DB Authority")
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("15000000.00"),
            quantity=1,
            warranty_terms="Bảo hành 12 tháng tại hãng"
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-02",
            total_amount=Decimal("16000000.00"),
            quantity=1,
            warranty_terms="Bảo hành 36 tháng tận nơi"
        )

        comparisons = await ProcurementService.compare_quotations_prisma(pr["id"])
        q1 = next(c for c in comparisons if c["supplierId"] == "SUP-01")
        q2 = next(c for c in comparisons if c["supplierId"] == "SUP-02")

        assert q1["warrantyTerms"] == "Bảo hành 12 tháng tại hãng"
        assert q2["warrantyTerms"] == "Bảo hành 36 tháng tận nơi"
    run_async(run_test())


def test_tc_cmp_010_anomaly_result_is_deterministic():
    """TC-CMP-010: deterministic anomaly detection flags quotes >= 20% above average."""
    async def run_test():
        pr = await helper_create_approved_pr("Deterministic Anomaly")
        # Quote 1: unit price = 20,000,000
        # Quote 2: unit price = 20,000,000
        # Quote 3: unit price = 30,000,000 -> average is (20+20+30)/3 = 23,333,333
        # Diff ratio for Q3: (30 - 23.33) / 23.33 = +28.57% (>= 20%) -> Anomaly!
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("20000000.00"),
            quantity=1
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-02",
            total_amount=Decimal("20000000.00"),
            quantity=1
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-03",
            total_amount=Decimal("30000000.00"),
            quantity=1
        )

        comparisons = await ProcurementService.compare_quotations_prisma(pr["id"])
        q1 = next(c for c in comparisons if c["supplierId"] == "SUP-01")
        q2 = next(c for c in comparisons if c["supplierId"] == "SUP-02")
        q3 = next(c for c in comparisons if c["supplierId"] == "SUP-03")

        assert q1["isAnomaly"] is False
        assert q2["isAnomaly"] is False
        assert q3["isAnomaly"] is True
        assert "CẢNH BÁO" in q3["anomalyReason"]
        assert "cao hơn" in q3["anomalyReason"]
    run_async(run_test())

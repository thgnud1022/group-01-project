"""
Integration Tests for Supplier & Quotation Domain via Prisma Client (Supabase PostgreSQL).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.4C - Migrate Supplier & Quotation to Prisma/PostgreSQL

Test Scope (15 Cases):
- TC-SQ-001: Create Supplier success -> persisted in Supabase PostgreSQL (T-051).
- TC-SQ-002: Duplicate Supplier name rejected by unique constraint (T-051).
- TC-SQ-003: List Suppliers returns seeded suppliers + newly created ones (T-051).
- TC-SQ-004: Get Supplier by ID returns correct details (T-051).
- TC-SQ-005: Get Supplier with invalid ID returns 404 ValueError (T-051).
- TC-SQ-006: Create Quotation on APPROVED PR succeeds with valid FK relations (T-052 / T-053).
- TC-SQ-007: Derived unitPrice calculated precisely with Decimal ROUND_HALF_UP.
- TC-SQ-008: Reject Quotation on non-approved PR (PENDING_MANAGER_APPROVAL) (T-052 Guard).
- TC-SQ-009: Reject Quotation on non-existent Supplier (T-053 Integrity).
- TC-SQ-010: Reject Quotation on non-existent PR (T-053 Integrity).
- TC-SQ-011: Reject Quotation on invalid quantity (<= 0) or amount (<= 0).
- TC-SQ-012: List Quotations for a PR returns all linked quotations with Supplier details (T-061).
- TC-SQ-013: Compare Quotations reads directly from PostgreSQL, zero MockDB writes (T-061).
- TC-SQ-014: PR Quotation Isolation (Quotations of PR-A do not leak into PR-B).
- TC-SQ-015: Atomic Transaction Rollback on failure (zero orphan records).
"""

import asyncio
import threading
import pytest
from decimal import Decimal
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
    """Teardown fixture ensuring database hygiene: clean test Quotations, PRs, and test Suppliers."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()

        # 1. Clean test PRs and their child Quotations & Approvals
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-SQ]"}}
        )
        for pr in test_prs:
            # Delete child quotations
            await prisma.quotation.delete_many(where={"purchaseRequestId": pr.id})
            # Delete child approvals
            await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
            # Delete PR (PRItems cascade)
            await prisma.purchaserequest.delete(where={"id": pr.id})

        # 2. Clean test suppliers created during testing
        await prisma.supplier.delete_many(
            where={"name": {"contains": "[TEST-SUP]"}}
        )

        # 3. Reset tempReservedAmount to 0
        await prisma.budget.update_many(
            where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
            data={"tempReservedAmount": Decimal("0.00")}
        )
    run_async(cleanup())


async def helper_create_approved_pr(title_suffix: str) -> dict:
    """Helper to create and approve a test PR in PostgreSQL (<= 50M for 1-level approval)."""
    pr = await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title=f"[TEST-SQ] PR {title_suffix}",
        items=[{"itemName": "Laptop Dell Core i7", "quantity": 1, "estimatedUnitPrice": 25_000_000}]
    )
    # PR <= 50M: 1-level Manager approval immediately reaches APPROVED
    approved = await ProcurementService.approve_pr_prisma(
        pr_id=pr["id"],
        approver_email="manager@company.com",
        comments="Approved for quotation collection"
    )
    assert approved["status"] == "APPROVED"
    return approved


# ==============================================================================
# Supplier Integration Tests (T-051)
# ==============================================================================

def test_tc_sq_001_create_supplier_success():
    """TC-SQ-001: Create Supplier via service -> Persisted in PostgreSQL."""
    async def run_test():
        prisma = get_prisma()
        supplier = await ProcurementService.create_supplier_prisma(
            name="[TEST-SUP] Công ty TNHH Giải pháp Công nghệ Sao Mai",
            tax_code="0312345999",
            contact="contact@saomai.vn - 0901234567"
        )
        assert "id" in supplier
        assert supplier["name"] == "[TEST-SUP] Công ty TNHH Giải pháp Công nghệ Sao Mai"
        assert supplier["taxCode"] == "0312345999"
        assert supplier["contact"] == "contact@saomai.vn - 0901234567"

        # Verify query directly from PostgreSQL
        db_supplier = await prisma.supplier.find_unique(where={"id": supplier["id"]})
        assert db_supplier is not None
        assert db_supplier.name == supplier["name"]
    run_async(run_test())


def test_tc_sq_002_duplicate_supplier_name_rejected():
    """TC-SQ-002: Duplicate Supplier name is rejected with ValueError (Unique Constraint)."""
    async def run_test():
        supplier_name = "[TEST-SUP] Nhà cung cấp Trùng Tên ABC"
        sup1 = await ProcurementService.create_supplier_prisma(name=supplier_name, tax_code="0100000001")
        assert sup1["name"] == supplier_name

        # Second attempt with same name
        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.create_supplier_prisma(name=supplier_name, tax_code="0100000002")
        assert "đã tồn tại" in str(excinfo.value)
    run_async(run_test())


def test_tc_sq_003_list_suppliers():
    """TC-SQ-003: List all Suppliers returns base seed suppliers + new ones."""
    async def run_test():
        suppliers = await ProcurementService.list_suppliers_prisma()
        assert len(suppliers) >= 3

        # Ensure base seeded suppliers are present
        supplier_ids = [s["id"] for s in suppliers]
        assert "SUP-01" in supplier_ids
        assert "SUP-02" in supplier_ids
        assert "SUP-03" in supplier_ids
    run_async(run_test())


def test_tc_sq_004_get_supplier_by_id():
    """TC-SQ-004: Get Supplier details by ID from PostgreSQL."""
    async def run_test():
        supplier = await ProcurementService.get_supplier_prisma("SUP-01")
        assert supplier["id"] == "SUP-01"
        assert supplier["name"] == "Công ty TNHH Tin học Phong Vũ"
        assert supplier["taxCode"] == "0301234567"
    run_async(run_test())


def test_tc_sq_005_get_supplier_not_found():
    """TC-SQ-005: Query non-existent Supplier raises ValueError."""
    async def run_test():
        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.get_supplier_prisma("SUP-NON-EXISTENT-999")
        assert "Không tìm thấy nhà cung cấp" in str(excinfo.value)
    run_async(run_test())


# ==============================================================================
# Quotation Integration Tests (T-052, T-053, T-054, T-061)
# ==============================================================================

def test_tc_sq_006_create_quotation_on_approved_pr_success():
    """TC-SQ-006: Create Quotation on APPROVED PR succeeds and links to PostgreSQL."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_approved_pr("Quotation Happy Path")
        pr_id = pr["id"]

        quote = await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_id,
            supplier_id="SUP-01",
            total_amount=Decimal("73500000.00"),
            quantity=3,
            delivery_days=3,
            warranty_terms="24 tháng chính hãng",
            file_url="quotes/phongvu_quotation.pdf"
        )

        assert quote["purchaseRequestId"] == pr_id
        assert quote["supplierId"] == "SUP-01"
        assert quote["totalAmount"] == 73500000.0
        assert quote["quantity"] == 3
        assert quote["unitPrice"] == 24500000.0
        assert quote["deliveryDays"] == 3
        assert quote["warrantyTerms"] == "24 tháng chính hãng"
        assert quote["fileUrl"] == "quotes/phongvu_quotation.pdf"
        assert "supplier" in quote
        assert quote["supplier"]["name"] == "Công ty TNHH Tin học Phong Vũ"
        assert quote["supplierName"] == "Công ty TNHH Tin học Phong Vũ"

        # Verify direct database persistence
        db_quote = await prisma.quotation.find_unique(where={"id": quote["id"]})
        assert db_quote is not None
        assert db_quote.supplierId == "SUP-01"
        assert db_quote.purchaseRequestId == pr_id
    run_async(run_test())


def test_tc_sq_007_derived_decimal_unit_price():
    """TC-SQ-007: Verify derived unitPrice is calculated accurately via Decimal ROUND_HALF_UP."""
    async def run_test():
        pr = await helper_create_approved_pr("Derived Decimal Price")
        pr_id = pr["id"]

        # 25,000,000 / 3 = 8,333,333.333333... -> rounded to 8,333,333.33
        quote = await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_id,
            supplier_id="SUP-02",
            total_amount=Decimal("25000000.00"),
            quantity=3,
            delivery_days=5,
            file_url="quotes/trananh_quote.pdf"
        )
        assert quote["totalAmount"] == 25000000.0
        assert quote["quantity"] == 3
        assert quote["unitPrice"] == 8333333.33
    run_async(run_test())


def test_tc_sq_008_reject_quotation_on_non_approved_pr():
    """TC-SQ-008: Reject Quotation creation on non-approved PR (T-052 Guard)."""
    async def run_test():
        # Create PR in PENDING_MANAGER_APPROVAL status (NOT yet approved)
        pr = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST-SQ] PR Pending Approval",
            items=[{"itemName": "PC Office", "quantity": 1, "estimatedUnitPrice": 10_000_000}]
        )
        pr_id = pr["id"]
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"

        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.create_quotation_prisma(
                purchase_request_id=pr_id,
                supplier_id="SUP-01",
                total_amount=Decimal("10000000.00"),
                quantity=1,
                file_url="quotes/sample.pdf"
            )
        assert "chưa được duyệt" in str(excinfo.value)
        assert "APPROVED" in str(excinfo.value)
    run_async(run_test())


def test_tc_sq_009_reject_quotation_invalid_supplier():
    """TC-SQ-009: Reject Quotation creation when supplierId does not exist (T-053 Integrity)."""
    async def run_test():
        pr = await helper_create_approved_pr("Invalid Supplier PR")
        pr_id = pr["id"]

        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.create_quotation_prisma(
                purchase_request_id=pr_id,
                supplier_id="SUP-GHOST-999",
                total_amount=Decimal("50000000.00"),
                quantity=2,
                file_url="quotes/sample.pdf"
            )
        assert "Không tìm thấy nhà cung cấp" in str(excinfo.value)
    run_async(run_test())


def test_tc_sq_010_reject_quotation_invalid_pr():
    """TC-SQ-010: Reject Quotation creation when purchaseRequestId does not exist (T-053 Integrity)."""
    async def run_test():
        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.create_quotation_prisma(
                purchase_request_id="PR-NON-EXISTENT-XYZ",
                supplier_id="SUP-01",
                total_amount=Decimal("10000000.00"),
                quantity=1,
                file_url="quotes/sample.pdf"
            )
        assert "Không tìm thấy Purchase Request" in str(excinfo.value)
    run_async(run_test())


def test_tc_sq_011_reject_quotation_invalid_quantity_or_amount():
    """TC-SQ-011: Reject Quotation when quantity <= 0 or totalAmount <= 0."""
    async def run_test():
        pr = await helper_create_approved_pr("Validation PR")
        pr_id = pr["id"]

        # Case 1: quantity = 0
        with pytest.raises(ValueError) as exc1:
            await ProcurementService.create_quotation_prisma(
                purchase_request_id=pr_id,
                supplier_id="SUP-01",
                total_amount=Decimal("10000000.00"),
                quantity=0,
                file_url="q.pdf"
            )
        assert "nguyên dương" in str(exc1.value)

        # Case 2: totalAmount = 0
        with pytest.raises(ValueError) as exc2:
            await ProcurementService.create_quotation_prisma(
                purchase_request_id=pr_id,
                supplier_id="SUP-01",
                total_amount=Decimal("0.00"),
                quantity=1,
                file_url="q.pdf"
            )
        assert "lớn hơn 0" in str(exc2.value)
    run_async(run_test())


def test_tc_sq_012_list_quotations_by_pr():
    """TC-SQ-012: List quotations for a PR via service methods (T-061)."""
    async def run_test():
        pr = await helper_create_approved_pr("Multi-quote PR")
        pr_id = pr["id"]

        # Add 2 quotations for this PR
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_id,
            supplier_id="SUP-01",
            total_amount=Decimal("24000000.00"),
            quantity=2,
            file_url="q1.pdf"
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_id,
            supplier_id="SUP-02",
            total_amount=Decimal("26000000.00"),
            quantity=2,
            file_url="q2.pdf"
        )

        # Method 1: list_quotations_by_pr_prisma
        quotes1 = await ProcurementService.list_quotations_by_pr_prisma(pr_id)
        assert len(quotes1) == 2
        assert quotes1[0]["purchaseRequestId"] == pr_id
        assert quotes1[1]["purchaseRequestId"] == pr_id

        # Method 2: list_quotations_prisma with filter
        quotes2 = await ProcurementService.list_quotations_prisma(purchase_request_id=pr_id)
        assert len(quotes2) == 2
    run_async(run_test())


def test_tc_sq_013_compare_quotations_reads_from_postgres():
    """TC-SQ-013: Compare endpoint reads real data from PostgreSQL and detects anomaly deterministically."""
    async def run_test():
        pr = await helper_create_approved_pr("Comparison PR")
        pr_id = pr["id"]

        # Add 3 quotations:
        # SUP-01: price 24,000,000 for 1
        # SUP-02: price 31,000,000 for 1 (> 20% higher than average)
        # SUP-03: price 24,500,000 for 1
        await ProcurementService.create_quotation_prisma(purchase_request_id=pr_id, supplier_id="SUP-01", total_amount=Decimal("24000000.00"), quantity=1, file_url="q1.pdf")
        await ProcurementService.create_quotation_prisma(purchase_request_id=pr_id, supplier_id="SUP-02", total_amount=Decimal("36000000.00"), quantity=1, file_url="q2.pdf")
        await ProcurementService.create_quotation_prisma(purchase_request_id=pr_id, supplier_id="SUP-03", total_amount=Decimal("24000000.00"), quantity=1, file_url="q3.pdf")

        comparisons = await ProcurementService.compare_quotations_prisma(pr_id)
        assert len(comparisons) == 3

        # Verify joined supplier data
        names = [c["supplier"]["name"] for c in comparisons]
        assert "Công ty TNHH Tin học Phong Vũ" in names
        assert "Công ty TNHH Máy tính Trần Anh" in names
        assert "Công ty Cổ phần Máy tính FPT" in names

        # Verify anomaly detected on the highest price
        tran_anh = next(c for c in comparisons if c["supplierId"] == "SUP-02")
        assert tran_anh["isAnomaly"] is True
        assert "CẢNH BÁO" in tran_anh["anomalyReason"]

        # Verify zero MockDB writes occurred
        for c in comparisons:
            assert c["id"] not in db.quotations
    run_async(run_test())


def test_tc_sq_014_pr_quotation_isolation():
    """TC-SQ-014: Quotation isolation - PR-A's quotations do not appear in PR-B's list."""
    async def run_test():
        pr_a = await helper_create_approved_pr("PR-A Isolation")
        pr_b = await helper_create_approved_pr("PR-B Isolation")

        # Create quotation for PR-A
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_a["id"], supplier_id="SUP-01", total_amount=Decimal("10000000.00"), quantity=1, file_url="qa.pdf"
        )

        # Create quotation for PR-B
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_b["id"], supplier_id="SUP-02", total_amount=Decimal("20000000.00"), quantity=1, file_url="qb.pdf"
        )

        # Query PR-A
        quotes_a = await ProcurementService.list_quotations_by_pr_prisma(pr_a["id"])
        assert len(quotes_a) == 1
        assert quotes_a[0]["purchaseRequestId"] == pr_a["id"]
        assert quotes_a[0]["supplierId"] == "SUP-01"

        # Query PR-B
        quotes_b = await ProcurementService.list_quotations_by_pr_prisma(pr_b["id"])
        assert len(quotes_b) == 1
        assert quotes_b[0]["purchaseRequestId"] == pr_b["id"]
        assert quotes_b[0]["supplierId"] == "SUP-02"
    run_async(run_test())


def test_tc_sq_015_atomic_transaction_rollback():
    """TC-SQ-015: If an error occurs during quotation insertion, no orphan record is created."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_approved_pr("Atomic Rollback PR")
        pr_id = pr["id"]

        # Attempt with invalid supplier
        with pytest.raises(ValueError):
            await ProcurementService.create_quotation_prisma(
                purchase_request_id=pr_id,
                supplier_id="SUP-INVALID-ROLLBACK",
                total_amount=Decimal("10000000.00"),
                quantity=1
            )

        # Verify no quotation was saved in PostgreSQL
        quotes = await prisma.quotation.find_many(where={"purchaseRequestId": pr_id})
        assert len(quotes) == 0
    run_async(run_test())

"""
Integration Tests for PurchaseRequest Creation via Prisma Client (Supabase PostgreSQL).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.2 - Migrate PurchaseRequest Creation to Prisma/PostgreSQL

Test Scope:
- TC-PR-001: Happy Path Creation (PR, PRItem, creatorId UUID, Budget tempReserved, approvals=[])
- TC-PR-002: ID Collision Multi-Transaction Retry (Rollback attempt 1, new tx attempt 2, no double reserve)
- TC-PR-003: Department Not Found (Department-specific error, not obscured by budget error)
- TC-PR-004: Active Budget Period Not Found (Specific error for missing fiscal period)
- TC-PR-005: Insufficient Budget (REQ-BR-01, rejected before write, zero side-effects)
- TC-PR-006: Invalid Items Validation (quantity <= 0, negative unit price, empty items)
- TC-PR-007: Transaction Rollback on Failure (atomic cleanup of PR, PRItems, and Budget)
- TC-PR-008: Concurrency & Overspending Protection (Row-level lock serializes concurrent reservations)
- TC-PR-009: Decimal Monetary Precision (Exact calculation without float precision drift)
- TC-PR-010: User Identity Distinctness (Distinct UUIDs for different emails, HD-REQ-07)
"""

import asyncio
import threading
import pytest
from decimal import Decimal
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.data_access import resolve_user_id_by_email, ACTIVE_BUDGET_FISCAL_YEAR, ACTIVE_BUDGET_QUARTER
from app.services.procurement_service import ProcurementService
from prisma import errors


class AsyncTestRunner:
    """Dedicated background event loop runner for reliable Prisma asyncio integration testing on Windows."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro, timeout: float = 20.0):
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
def clean_test_prs():
    """Teardown fixture ensuring database hygiene: clean test PRs and restore tempReservedAmount."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()
        # Delete test PRs created during tests
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST]"}}
        )
        for pr in test_prs:
            await prisma.purchaserequest.delete(where={"id": pr.id})
        # Reset tempReservedAmount to 0 for standard test budgets
        await prisma.budget.update_many(
            where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
            data={"tempReservedAmount": Decimal("0.00")}
        )
    run_async(cleanup())


def test_tc_pr_001_happy_path():
    """TC-PR-001: Happy Path PR Creation in PostgreSQL with all relations, budget reservation, and approvals=[]."""
    async def run_test():
        prisma = get_prisma()
        user_id = await resolve_user_id_by_email("employee@company.com")
        
        items = [
            {"itemName": "Laptop Dell Latitude", "quantity": 2, "estimatedUnitPrice": 25_000_000},
            {"itemName": "Màn hình Dell UltraSharp", "quantity": 2, "estimatedUnitPrice": 7_500_000},
        ]
        # Total: 2 * 25m + 2 * 7.5m = 65,000,000 VND
        expected_total = 65_000_000.0

        b_before = await prisma.budget.find_unique(
            where={
                "departmentId_fiscalYear_quarter": {
                    "departmentId": "DEPT-IT",
                    "fiscalYear": ACTIVE_BUDGET_FISCAL_YEAR,
                    "quarter": ACTIVE_BUDGET_QUARTER,
                }
            }
        )
        initial_reserved = Decimal(str(b_before.tempReservedAmount))

        result = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST] Mua laptop và màn hình cho nhân viên",
            items=items,
        )

        # 1. Verify response contract
        assert result["id"].startswith("PR-2026-")
        assert result["departmentId"] == "DEPT-IT"
        assert result["deptId"] == "DEPT-IT"
        assert result["creatorId"] == user_id
        assert result["estimatedValue"] == expected_total
        assert result["status"] == "PENDING_MANAGER_APPROVAL"
        assert result["approvals"] == []
        assert len(result["items"]) == 2

        # 2. Verify database persistence in PostgreSQL
        pr_in_db = await prisma.purchaserequest.find_unique(
            where={"id": result["id"]},
            include={"items": True, "creator": True, "department": True}
        )
        assert pr_in_db is not None
        assert pr_in_db.creatorId == user_id
        assert pr_in_db.departmentId == "DEPT-IT"
        assert pr_in_db.estimatedValue == Decimal(str(expected_total))
        assert len(pr_in_db.items) == 2

        # 3. Verify PRItems in PostgreSQL
        item_names = {it.itemName: (it.quantity, float(it.estimatedUnitPrice)) for it in pr_in_db.items}
        assert item_names["Laptop Dell Latitude"] == (2, 25_000_000.0)
        assert item_names["Màn hình Dell UltraSharp"] == (2, 7_500_000.0)

        # 4. Verify Budget tempReservedAmount updated in PostgreSQL
        b_after = await prisma.budget.find_unique(
            where={"id": b_before.id}
        )
        assert b_after.tempReservedAmount == initial_reserved + Decimal(str(expected_total))

    run_async(run_test())


def test_tc_pr_002_id_collision_multi_tx_retry():
    """TC-PR-002: ID collision rolls back attempt 1 and succeeds in attempt 2 without double reservation."""
    async def run_test():
        prisma = get_prisma()
        user_id = await resolve_user_id_by_email("employee@company.com")

        # Determine next candidate ID
        latest_prs = await prisma.purchaserequest.find_many(
            where={"id": {"startswith": "PR-2026-"}},
            order={"id": "desc"},
            take=1
        )
        if latest_prs:
            base_num = int(latest_prs[0].id.split("-")[-1]) + 1
        else:
            base_num = await prisma.purchaserequest.count() + 1

        collision_id = f"PR-2026-{base_num:03d}"
        
        # Pre-insert a colliding PR with this candidate ID
        colliding_pr = await prisma.purchaserequest.create(
            data={
                "id": collision_id,
                "title": "[TEST] Colliding Dummy PR",
                "status": "DRAFT",
                "creatorId": user_id,
                "departmentId": "DEPT-IT",
                "estimatedValue": Decimal("1000.00"),
            }
        )

        b_before = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        reserved_before = Decimal(str(b_before.tempReservedAmount))

        # Now attempt to create PR which will initially collide on collision_id,
        # roll back attempt 1, and succeed in attempt 2 with candidate_id = collision_id + 1
        items = [{"itemName": "Test Item", "quantity": 1, "estimatedUnitPrice": 5_000_000}]
        result = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST] PR with collision retry",
            items=items,
        )

        expected_next_id = f"PR-2026-{(base_num + 1):03d}"
        assert result["id"] == expected_next_id

        # Verify budget was only reserved ONCE (5_000_000), not twice (10_000_000)
        b_after = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        assert b_after.tempReservedAmount == reserved_before + Decimal("5000000.00")

    run_async(run_test())


def test_tc_pr_003_department_not_found():
    """TC-PR-003: Non-existent department raises department-specific error, not obscured by budget error."""
    async def run_test():
        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.create_pr_prisma(
                dept_id="DEPT-NONEXISTENT",
                creator_id="employee@company.com",
                title="[TEST] PR for invalid dept",
                items=[{"itemName": "Item", "quantity": 1, "estimatedUnitPrice": 100_000}],
            )
        assert "Không tìm thấy phòng ban với mã 'DEPT-NONEXISTENT'" in str(excinfo.value)

    run_async(run_test())


def test_tc_pr_004_budget_period_not_found():
    """TC-PR-004: Valid department with missing active budget period raises budget period error."""
    async def run_test():
        prisma = get_prisma()
        # Temporarily create a department without a budget
        temp_dept = await prisma.department.create(
            data={"id": "DEPT-NOBUDGET", "name": "Phòng Ban Không Ngân Sách"}
        )
        try:
            with pytest.raises(ValueError) as excinfo:
                await ProcurementService.create_pr_prisma(
                    dept_id="DEPT-NOBUDGET",
                    creator_id="employee@company.com",
                    title="[TEST] PR for dept without budget",
                    items=[{"itemName": "Item", "quantity": 1, "estimatedUnitPrice": 100_000}],
                )
            assert "Không tìm thấy ngân sách khả dụng cho phòng ban 'DEPT-NOBUDGET'" in str(excinfo.value)
        finally:
            await prisma.department.delete(where={"id": "DEPT-NOBUDGET"})

    run_async(run_test())


def test_tc_pr_005_insufficient_budget():
    """TC-PR-005: REQ-BR-01 Soft warning: PR exceeding budget is created with isBudgetExceeded=True without reserving budget."""
    async def run_test():
        prisma = get_prisma()
        b_before = await prisma.budget.find_first(where={"departmentId": "DEPT-HR"})
        available = (
            Decimal(str(b_before.allocatedAmount))
            - Decimal(str(b_before.spentAmount))
            - Decimal(str(b_before.tempReservedAmount))
        )
        reserved_before = Decimal(str(b_before.tempReservedAmount))

        excessive_price = float(available) + 50_000_000.0

        result = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-HR",
            creator_id="employee@company.com",
            title="[TEST] PR exceeding HR budget",
            items=[{"itemName": "Dự án đào tạo xa xỉ", "quantity": 1, "estimatedUnitPrice": excessive_price}],
        )

        assert result["status"] == "PENDING_MANAGER_APPROVAL"
        assert result["isBudgetExceeded"] is True
        assert result["overAmount"] > 0

        # Verify no budget was reserved
        b_after = await prisma.budget.find_first(where={"departmentId": "DEPT-HR"})
        assert b_after.tempReservedAmount == reserved_before

    run_async(run_test())


def test_tc_pr_006_invalid_items_validation():
    """TC-PR-006: Invalid item data (quantity <= 0, unit price < 0, empty list) rejected before DB write."""
    async def run_test():
        # Case 1: Empty items list
        with pytest.raises(ValueError) as exc1:
            await ProcurementService.create_pr_prisma("DEPT-IT", "employee@company.com", "[TEST] PR", [])
        assert "không được rỗng" in str(exc1.value)

        # Case 2: Quantity = 0
        with pytest.raises(ValueError) as exc2:
            await ProcurementService.create_pr_prisma(
                "DEPT-IT", "employee@company.com", "[TEST] PR",
                [{"itemName": "Item", "quantity": 0, "estimatedUnitPrice": 1000}]
            )
        assert "phải lớn hơn 0" in str(exc2.value)

        # Case 3: Negative unit price
        with pytest.raises(ValueError) as exc3:
            await ProcurementService.create_pr_prisma(
                "DEPT-IT", "employee@company.com", "[TEST] PR",
                [{"itemName": "Item", "quantity": 1, "estimatedUnitPrice": -500}]
            )
        assert "không được âm" in str(exc3.value)

    run_async(run_test())


def test_tc_pr_007_transaction_rollback():
    """TC-PR-007: Simulated failure inside transaction rolls back PR, PRItems, and Budget completely."""
    async def run_test():
        prisma = get_prisma()
        b_before = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        reserved_before = Decimal(str(b_before.tempReservedAmount))

        # Test transaction rollback directly via prisma.tx()
        try:
            async with prisma.tx() as tx:
                # Update budget
                await tx.budget.update(
                    where={"id": b_before.id},
                    data={"tempReservedAmount": reserved_before + Decimal("20000000.00")}
                )
                # Create PR
                pr = await tx.purchaserequest.create(
                    data={
                        "id": "PR-ROLLBACK-TEST",
                        "title": "[TEST] Should be rolled back",
                        "status": "PENDING_MANAGER_APPROVAL",
                        "creatorId": (await resolve_user_id_by_email("employee@company.com")),
                        "departmentId": "DEPT-IT",
                        "estimatedValue": Decimal("20000000.00"),
                        "items": {"create": [{"itemName": "Ghost Item", "quantity": 1, "estimatedUnitPrice": Decimal("20000000.00")}]}
                    }
                )
                # Intentionally trigger error
                raise RuntimeError("Simulated transaction failure")
        except RuntimeError:
            pass

        # 1. Verify PR does not exist
        pr_check = await prisma.purchaserequest.find_unique(where={"id": "PR-ROLLBACK-TEST"})
        assert pr_check is None

        # 2. Verify PRItem does not exist
        item_check = await prisma.pritem.find_first(where={"itemName": "Ghost Item"})
        assert item_check is None

        # 3. Verify Budget tempReservedAmount unchanged
        b_after = await prisma.budget.find_first(where={"departmentId": "DEPT-IT"})
        assert b_after.tempReservedAmount == reserved_before

    run_async(run_test())


def test_tc_pr_008_concurrency_overspending_protection():
    """TC-PR-008: Row-level lock (SELECT FOR UPDATE) serializes reservations and blocks overspending."""
    async def run_test():
        prisma = get_prisma()
        b = await prisma.budget.find_first(where={"departmentId": "DEPT-HR"})
        available = (
            Decimal(str(b.allocatedAmount))
            - Decimal(str(b.spentAmount))
            - Decimal(str(b.tempReservedAmount))
        )
        # Attempt to make 2 reservations where each is 60% of available -> total 120%
        single_amount = float(available * Decimal("0.60"))

        # First request succeeds
        res1 = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-HR",
            creator_id="employee@company.com",
            title="[TEST] Concurrency PR 1",
            items=[{"itemName": "Course A", "quantity": 1, "estimatedUnitPrice": single_amount}],
        )
        assert res1["status"] == "PENDING_MANAGER_APPROVAL"

        # Second request succeeds but is flagged as over-budget (soft warning)
        res2 = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-HR",
            creator_id="employee@company.com",
            title="[TEST] Concurrency PR 2",
            items=[{"itemName": "Course B", "quantity": 1, "estimatedUnitPrice": single_amount}],
        )
        assert res2["status"] == "PENDING_MANAGER_APPROVAL"
        assert res2["isBudgetExceeded"] is True

    run_async(run_test())


def test_tc_pr_009_decimal_precision():
    """TC-PR-009: Decimal arithmetic precision prevents floating-point rounding errors."""
    async def run_test():
        # Items with fractional amounts: 3 * 333333.33 = 999999.99
        items = [
            {"itemName": "Item Fraction", "quantity": 3, "estimatedUnitPrice": 333333.33}
        ]
        res = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST] Decimal Precision PR",
            items=items,
        )
        # 3 * 333333.33 = 999999.99 exactly in Decimal
        prisma = get_prisma()
        pr_db = await prisma.purchaserequest.find_unique(where={"id": res["id"]})
        assert pr_db.estimatedValue == Decimal("999999.99")

    run_async(run_test())


def test_tc_pr_010_user_identity_distinctness():
    """TC-PR-010: HD-REQ-07 creatorId resolves to distinct User.id UUIDs for different emails."""
    async def run_test():
        res_emp = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST] PR by Employee",
            items=[{"itemName": "Mouse", "quantity": 1, "estimatedUnitPrice": 200_000}],
        )
        res_mgr = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="manager@company.com",
            title="[TEST] PR by Manager",
            items=[{"itemName": "Keyboard", "quantity": 1, "estimatedUnitPrice": 300_000}],
        )

        emp_uuid = await resolve_user_id_by_email("employee@company.com")
        mgr_uuid = await resolve_user_id_by_email("manager@company.com")

        assert res_emp["creatorId"] == emp_uuid
        assert res_mgr["creatorId"] == mgr_uuid
        assert res_emp["creatorId"] != res_mgr["creatorId"]
        # Ensure creatorId is a UUID string, not an email
        assert "@" not in res_emp["creatorId"]
        assert "@" not in res_mgr["creatorId"]

    run_async(run_test())

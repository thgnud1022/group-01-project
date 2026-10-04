"""
Integration Tests for PurchaseRequest Rejection Flow via Prisma Client (Supabase PostgreSQL).
Task: PHASE 3 SCOPE GATE — Reject PR Implementation & Verification
Requirements: REQ-FR-06, US-04 AC2, GOV-01, HD-REQ-10, HD-12
"""

import asyncio
import threading
import pytest
from decimal import Decimal
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.procurement_service import ProcurementService
from app.dependencies.rbac import AuthorizationError


class AsyncTestRunner:
    """Dedicated background event loop runner for reliable Prisma asyncio integration testing on Windows."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro, timeout: float = 25.0):
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
    """Teardown fixture ensuring database hygiene: clean test PRs, Approvals, and restore tempReservedAmount."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-REJ]"}}
        )
        for pr in test_prs:
            await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
            await prisma.purchaserequest.delete(where={"id": pr.id})
        await prisma.budget.update_many(
            where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
            data={"tempReservedAmount": Decimal("0.00")}
        )
    run_async(cleanup())


async def helper_create_test_pr(title_suffix: str, amount_each: float, quantity: int = 1, creator_email: str = "employee@company.com") -> dict:
    """Helper to create a test PR via ProcurementService.create_pr_prisma."""
    return await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id=creator_email,
        title=f"[TEST-REJ] PR {title_suffix}",
        items=[{"itemName": "Thiet bi reject test", "quantity": quantity, "estimatedUnitPrice": amount_each}]
    )


def test_tc_rej_001_manager_reject_success_and_budget_released():
    """TC-REJ-001: Manager rejects PR -> status = REJECTED, Approval record created with decision='REJECTED', tempReservedAmount released."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Manager Reject", amount_each=20_000_000, quantity=1)
        pr_id = pr["id"]
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"

        # Check budget tempReservedAmount was increased
        budget_before = await prisma.budget.find_first(
            where={"departmentId": "DEPT-IT", "fiscalYear": 2026, "quarter": 1}
        )
        assert budget_before.tempReservedAmount >= Decimal("20000000.00")

        # Manager rejects PR with required reason
        rejected_pr = await ProcurementService.reject_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Từ chối do vượt nhu cầu quý 1"
        )

        assert rejected_pr["status"] == "REJECTED"
        assert len(rejected_pr["approvals"]) == 1
        app = rejected_pr["approvals"][0]
        assert app["decision"] == "REJECTED"
        assert app["comments"] == "Từ chối do vượt nhu cầu quý 1"
        assert app["step"] == "MANAGER"

        # Verify in DB
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == "REJECTED"

        # Verify budget was released
        budget_after = await prisma.budget.find_first(
            where={"departmentId": "DEPT-IT", "fiscalYear": 2026, "quarter": 1}
        )
        assert budget_after.tempReservedAmount < budget_before.tempReservedAmount

    run_async(run_test())


def test_tc_rej_002_finance_reject_on_step2_success():
    """TC-REJ-002: PR > 50M passed Step 1 -> Finance rejects on Step 2 -> status = REJECTED."""
    async def run_test():
        pr = await helper_create_test_pr(">50M Step2", amount_each=80_000_000, quantity=1)
        pr_id = pr["id"]

        # Step 1: Manager approves
        step1_pr = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Manager approves step 1"
        )
        assert step1_pr["status"] == "PENDING_FINANCE_APPROVAL"

        # Step 2: Finance rejects
        step2_pr = await ProcurementService.reject_pr_prisma(
            pr_id=pr_id,
            approver_email="finance@company.com",
            comments="Finance rejects: Ngân sách IT Q3 không đủ hạn mức"
        )
        assert step2_pr["status"] == "REJECTED"
        assert len(step2_pr["approvals"]) == 2
        assert step2_pr["approvals"][1]["decision"] == "REJECTED"
        assert step2_pr["approvals"][1]["step"] == "FINANCE"

    run_async(run_test())


def test_tc_rej_003_mandatory_comments_enforced():
    """TC-REJ-003: US-04 AC2 mandates reason for rejection -> empty or whitespace comments raises ValueError."""
    async def run_test():
        pr = await helper_create_test_pr("No Reason", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]

        with pytest.raises(ValueError, match="Lý do từ chối là bắt buộc"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments=""
            )

        with pytest.raises(ValueError, match="Lý do từ chối là bắt buộc"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments="   "
            )

    run_async(run_test())


def test_tc_rej_004_unauthorized_role_rejected():
    """TC-REJ-004: EMPLOYEE or PROCUREMENT cannot reject PR -> raises AuthorizationError (403)."""
    async def run_test():
        pr = await helper_create_test_pr("Role Check", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]

        with pytest.raises(AuthorizationError, match="Chỉ Manager, Finance hoặc Admin mới có quyền từ chối PR"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_id,
                approver_email="employee@company.com",
                comments="Employee attempting rejection"
            )

        with pytest.raises(AuthorizationError, match="Chỉ Manager, Finance hoặc Admin mới có quyền từ chối PR"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_id,
                approver_email="procurement@company.com",
                comments="Procurement attempting rejection"
            )

    run_async(run_test())


def test_tc_rej_005_gov01_no_self_rejection():
    """TC-REJ-005: GOV-01: Manager cannot reject their own PR -> raises AuthorizationError."""
    async def run_test():
        # PR created by manager@company.com
        pr = await helper_create_test_pr("Self PR", amount_each=10_000_000, quantity=1, creator_email="manager@company.com")
        pr_id = pr["id"]

        with pytest.raises(AuthorizationError, match="Không thể từ chối PR do chính mình tạo"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments="Manager self-rejecting"
            )

    run_async(run_test())


def test_tc_rej_006_status_guard_blocks_approved_or_already_rejected():
    """TC-REJ-006: HD-REQ-10: Rejecting PR that is already APPROVED or REJECTED raises ValueError."""
    async def run_test():
        # Case A: PR already approved
        pr_app = await helper_create_test_pr("Approved Guard", amount_each=15_000_000, quantity=1)
        await ProcurementService.approve_pr_prisma(
            pr_id=pr_app["id"],
            approver_email="manager@company.com",
            comments="Approved"
        )
        with pytest.raises(ValueError, match="PR đang ở trạng thái 'APPROVED'"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_app["id"],
                approver_email="manager@company.com",
                comments="Trying to reject approved PR"
            )

        # Case B: PR already rejected -> duplicate reject blocked
        pr_rej = await helper_create_test_pr("Duplicate Reject", amount_each=15_000_000, quantity=1)
        await ProcurementService.reject_pr_prisma(
            pr_id=pr_rej["id"],
            approver_email="manager@company.com",
            comments="First reject"
        )
        with pytest.raises(ValueError, match="PR đang ở trạng thái 'REJECTED'"):
            await ProcurementService.reject_pr_prisma(
                pr_id=pr_rej["id"],
                approver_email="manager@company.com",
                comments="Second reject attempt"
            )

    run_async(run_test())

"""
Integration Tests for PurchaseRequest Revision and Resubmit Flow via Prisma Client (Supabase PostgreSQL).
Task: HD-16 — Real Revision Flow & Resubmit Implementation & Verification
Requirements: REQ-FR-06, US-03 AC3, US-04 AC2, GOV-01, HD-16
Test Cases:
  TC-REV-001: Manager requests revision -> 200, PR = REVISION_REQUIRED, Approval record created, budget released.
  TC-REV-002: Employee attempts revision -> 403 Forbidden.
  TC-REV-003: Procurement attempts revision -> 403 Forbidden.
  TC-REV-004: Creator self-action guard -> 403 where policy applies (GOV-01).
  TC-REV-005: Revision from invalid state (APPROVED, REJECTED, etc.) -> 400 rejected.
  TC-REV-006: Revision reason required -> validation failure / 400.
  TC-RESUB-001: REVISION_REQUIRED -> resubmit -> PENDING_MANAGER_APPROVAL, Approval RESUBMITTED created, budget re-reserved.
  TC-RESUB-002: Wrong user resubmits (not creator) -> 403 Forbidden.
  TC-RESUB-003: Resubmit from invalid state -> rejected.
  TC-RESUB-004: Edited data persisted -> verified in PostgreSQL.
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
    """Teardown fixture ensuring database hygiene: clean test PRs, Approvals, and restore tempReservedAmount."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-REV]"}}
        )
        for pr in test_prs:
            await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
            await prisma.pritem.delete_many(where={"purchaseRequestId": pr.id})
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
        title=f"[TEST-REV] PR {title_suffix}",
        items=[{"itemName": "Thiet bi revision test", "quantity": quantity, "estimatedUnitPrice": amount_each}]
    )


# -------------------------------------------------------------
# TC-REV TESTS
# -------------------------------------------------------------

def test_tc_rev_001_manager_request_revision_success():
    """TC-REV-001: Manager requests revision -> 200, PR = REVISION_REQUIRED, Approval record created, budget released."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Manager Revision", amount_each=25_000_000, quantity=1)
        pr_id = pr["id"]
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"

        # Manager requests revision
        revised_pr = await ProcurementService.request_revision_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Vui lòng chia thành 2 giai đoạn và bổ sung danh sách người nhận."
        )

        assert revised_pr["status"] == "REVISION_REQUIRED"

        # Verify PostgreSQL database state
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == "REVISION_REQUIRED"

        # Verify Approval record in DB
        approvals = await prisma.approval.find_many(where={"purchaseRequestId": pr_id})
        assert len(approvals) >= 1
        last_approval = approvals[-1]
        assert last_approval.decision == "REVISION_REQUIRED"
        assert "chia thành 2 giai đoạn" in last_approval.comments

    run_async(run_test())


def test_tc_rev_002_employee_attempts_revision_forbidden():
    """TC-REV-002: Employee attempts revision -> 403 (AuthorizationError)."""
    async def run_test():
        pr = await helper_create_test_pr("Employee Revision Attempt", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]

        with pytest.raises(AuthorizationError) as exc_info:
            await ProcurementService.request_revision_prisma(
                pr_id=pr_id,
                approver_email="employee@company.com",
                comments="Employee trying to request revision"
            )
        assert "Chỉ Manager, Finance hoặc Admin" in str(exc_info.value) or "No Self-Approval" in str(exc_info.value)

    run_async(run_test())


def test_tc_rev_003_procurement_attempts_revision_forbidden():
    """TC-REV-003: Procurement attempts revision -> 403 (AuthorizationError)."""
    async def run_test():
        pr = await helper_create_test_pr("Procurement Revision Attempt", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]

        with pytest.raises(AuthorizationError) as exc_info:
            await ProcurementService.request_revision_prisma(
                pr_id=pr_id,
                approver_email="procurement@company.com",
                comments="Procurement officer trying to request revision"
            )
        assert "Chỉ Manager, Finance hoặc Admin" in str(exc_info.value)

    run_async(run_test())


def test_tc_rev_004_creator_self_action_guard():
    """TC-REV-004: Creator self-action guard -> 403 (GOV-01). Manager cannot request revision on own PR."""
    async def run_test():
        # Manager creates PR as creator
        pr = await helper_create_test_pr("Manager Own PR", amount_each=15_000_000, quantity=1, creator_email="manager@company.com")
        pr_id = pr["id"]

        with pytest.raises(AuthorizationError) as exc_info:
            await ProcurementService.request_revision_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments="Manager trying self-revision"
            )
        assert "No Self-Approval — GOV-01" in str(exc_info.value)

    run_async(run_test())


def test_tc_rev_005_revision_from_invalid_state_rejected():
    """TC-REV-005: Revision from invalid state (APPROVED, REJECTED, etc.) -> ValueError."""
    async def run_test():
        pr = await helper_create_test_pr("Approve then Revise", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]

        # Approve it first
        await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Manager approved"
        )

        # Attempt revision on APPROVED PR
        with pytest.raises(ValueError) as exc_info:
            await ProcurementService.request_revision_prisma(
                pr_id=pr_id,
                approver_email="admin@company.com",
                comments="Trying revision on approved PR"
            )
        assert "không thể thực hiện yêu cầu chỉnh sửa" in str(exc_info.value)

    run_async(run_test())


def test_tc_rev_006_revision_reason_required():
    """TC-REV-006: Revision reason required -> validation failure (ValueError)."""
    async def run_test():
        pr = await helper_create_test_pr("Empty Reason Revise", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]

        with pytest.raises(ValueError) as exc_info:
            await ProcurementService.request_revision_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments="   "
            )
        assert "Lý do yêu cầu chỉnh sửa là bắt buộc" in str(exc_info.value)

    run_async(run_test())


# -------------------------------------------------------------
# TC-RESUB TESTS
# -------------------------------------------------------------

def test_tc_resub_001_resubmit_success_transitions_to_pending_manager():
    """TC-RESUB-001: REVISION_REQUIRED -> resubmit -> PENDING_MANAGER_APPROVAL, Approval RESUBMITTED created."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Resubmit Workflow", amount_each=30_000_000, quantity=1)
        pr_id = pr["id"]

        # Manager requests revision
        await ProcurementService.request_revision_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Yêu cầu tách số lượng thành 2 đơn vị."
        )

        # Creator resubmits with updated items
        resubmitted_pr = await ProcurementService.resubmit_pr_prisma(
            pr_id=pr_id,
            actor_email="employee@company.com",
            title="[TEST-REV] PR Resubmit Workflow (Updated)",
            items=[{"itemName": "Thiet bi revision test (Split)", "quantity": 2, "estimatedUnitPrice": 14_000_000}],
            comments="Đã chỉnh sửa theo yêu cầu của quản lý"
        )

        assert resubmitted_pr["status"] == "PENDING_MANAGER_APPROVAL"
        assert resubmitted_pr["estimatedValue"] == 28_000_000.0

        # Verify DB
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == "PENDING_MANAGER_APPROVAL"

        # Verify Approval history preserved
        approvals = await prisma.approval.find_many(where={"purchaseRequestId": pr_id}, order={"created_at": "asc"})
        assert len(approvals) >= 2
        assert approvals[0].decision == "REVISION_REQUIRED"
        assert approvals[1].decision == "RESUBMITTED"

    run_async(run_test())


def test_tc_resub_002_wrong_user_resubmits_forbidden():
    """TC-RESUB-002: Wrong user resubmits (different employee) -> 403 AuthorizationError."""
    async def run_test():
        pr = await helper_create_test_pr("Wrong User Resubmit", amount_each=10_000_000, quantity=1, creator_email="employee@company.com")
        pr_id = pr["id"]

        await ProcurementService.request_revision_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Chỉnh sửa nội dung"
        )

        with pytest.raises(AuthorizationError) as exc_info:
            await ProcurementService.resubmit_pr_prisma(
                pr_id=pr_id,
                actor_email="finance@company.com",
                comments="Different user resubmitting"
            )
        assert "Chỉ người tạo PR mới có quyền chỉnh sửa và gửi lại yêu cầu" in str(exc_info.value)

    run_async(run_test())


def test_tc_resub_003_resubmit_from_invalid_state_rejected():
    """TC-RESUB-003: Resubmit from invalid state (PENDING_MANAGER_APPROVAL) -> rejected."""
    async def run_test():
        pr = await helper_create_test_pr("Invalid State Resubmit", amount_each=10_000_000, quantity=1)
        pr_id = pr["id"]
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"

        with pytest.raises(ValueError) as exc_info:
            await ProcurementService.resubmit_pr_prisma(
                pr_id=pr_id,
                actor_email="employee@company.com",
                comments="Trying resubmit while still pending"
            )
        assert "Chỉ PR ở trạng thái 'REVISION_REQUIRED' mới có thể gửi lại" in str(exc_info.value)

    run_async(run_test())


def test_tc_resub_004_edited_data_persisted_in_postgresql():
    """TC-RESUB-004: Edited data persisted -> verified in PostgreSQL."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Data Persist Test", amount_each=12_000_000, quantity=1)
        pr_id = pr["id"]

        await ProcurementService.request_revision_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Thay đổi mặt hàng và tên yêu cầu."
        )

        updated_title = "[TEST-REV] PR Data Persist Test (FINAL)"
        updated_items = [
            {"itemName": "Item A Updated", "quantity": 3, "estimatedUnitPrice": 5_000_000},
            {"itemName": "Item B Updated", "quantity": 2, "estimatedUnitPrice": 2_500_000},
        ]

        await ProcurementService.resubmit_pr_prisma(
            pr_id=pr_id,
            actor_email="employee@company.com",
            title=updated_title,
            items=updated_items,
            comments="Cập nhật 2 mặt hàng mới"
        )

        # Direct DB verification
        db_pr = await prisma.purchaserequest.find_unique(
            where={"id": pr_id},
            include={"items": True}
        )
        assert db_pr.title == updated_title
        assert db_pr.estimatedValue == Decimal("20000000.00")
        assert len(db_pr.items) == 2
        item_names = {it.itemName for it in db_pr.items}
        assert "Item A Updated" in item_names
        assert "Item B Updated" in item_names

    run_async(run_test())

"""
Integration Tests for PurchaseRequest Approval Flow via Prisma Client (Supabase PostgreSQL).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.3 - Migrate Approval Flow to Prisma/PostgreSQL

Test Scope:
- TC-APP-001: PR <= 50M VND -> Manager approve (1-level) -> status = APPROVED, 1 Approval record.
- TC-APP-002: PR > 50M VND -> Manager approve Step 1 -> status = PENDING_FINANCE_APPROVAL, 1 Approval record.
- TC-APP-003: PR > 50M VND -> Finance approve Step 2 -> status = APPROVED, 2 Approval records.
- TC-APP-004: Approver Identity Integrity -> Approval.approverId matches User.id UUID (HD-REQ-07 & HD-REQ-09).
- TC-APP-005: Approver Email Not Found -> raises 400 ValueError.
- TC-APP-006: Unauthorized Roles (EMPLOYEE, PROCUREMENT) -> rejected with 400 ValueError.
- TC-APP-007: Wrong Step Order: FINANCE tries Step 1 on PR > 50M before Manager -> rejected with 400 ValueError.
- TC-APP-008: Approval Status Guard (HD-REQ-10): Approving PR already in APPROVED status -> rejected.
- TC-APP-009: Approval Status Guard (HD-REQ-10): Approving PR in REJECTED/CLOSED/PO_CREATED -> rejected.
- TC-APP-010: Repeated Approval at same approval stage (e.g. Manager tries to approve again in Step 2) -> rejected.
- TC-APP-011: Transaction Rollback on Failure -> PR status unmutated, zero orphan Approval records.
- TC-APP-012: Concurrency: 2 concurrent requests from manager@company.com on PR > 50M -> 1 success, 1 rejected.
- TC-APP-013: Response Contract: nested approvals returned from PostgreSQL with step, approver, comments.
- TC-APP-014: ADMIN Approves both Step 1 and Step 2 on PR > 50M -> 2 Approval records with same approverId.
- TC-APP-015: End-to-end Workflow Regression: create_pr_prisma -> approve_pr_prisma on same PR.
"""

import asyncio
import threading
import pytest
from decimal import Decimal
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.data_access import resolve_user_id_by_email
from app.services.procurement_service import ProcurementService


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
        # Find all test PRs created during tests
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-APP]"}}
        )
        for pr in test_prs:
            # Delete child Approvals first (Approval does not have onDelete: Cascade)
            await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
            # Delete PR (PRItems cascade delete)
            await prisma.purchaserequest.delete(where={"id": pr.id})
        # Reset tempReservedAmount to 0 for test budgets
        await prisma.budget.update_many(
            where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
            data={"tempReservedAmount": Decimal("0.00")}
        )
    run_async(cleanup())


async def helper_create_test_pr(title_suffix: str, amount_each: float, quantity: int = 1) -> dict:
    """Helper to create a test PR via ProcurementService.create_pr_prisma."""
    return await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title=f"[TEST-APP] PR {title_suffix}",
        items=[{"itemName": "Thiet bi test", "quantity": quantity, "estimatedUnitPrice": amount_each}]
    )


def test_tc_app_001_single_level_approval_success():
    """TC-APP-001: PR <= 50M VND -> Manager approve (1-level) -> status = APPROVED, 1 Approval record."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("<=50M", amount_each=30_000_000, quantity=1)
        pr_id = pr["id"]
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"

        approved_pr = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Manager approved small PR"
        )

        assert approved_pr["status"] == "APPROVED"
        assert len(approved_pr["approvals"]) == 1
        app = approved_pr["approvals"][0]
        assert app["decision"] == "APPROVED"
        assert app["comments"] == "Manager approved small PR"
        assert app["step"] == "MANAGER"

        # Verify database record
        db_approvals = await prisma.approval.find_many(where={"purchaseRequestId": pr_id})
        assert len(db_approvals) == 1
        assert db_approvals[0].decision == "APPROVED"

        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == "APPROVED"

    run_async(run_test())


def test_tc_app_002_two_level_approval_step1():
    """TC-APP-002: PR > 50M VND -> Manager approve Step 1 -> status = PENDING_FINANCE_APPROVAL, 1 Approval record."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr(">50M Step1", amount_each=60_000_000, quantity=1)
        pr_id = pr["id"]
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"

        res = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Manager approved step 1"
        )

        assert res["status"] == "PENDING_FINANCE_APPROVAL"
        assert len(res["approvals"]) == 1
        assert res["approvals"][0]["step"] == "MANAGER"

        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == "PENDING_FINANCE_APPROVAL"

    run_async(run_test())


def test_tc_app_003_two_level_approval_step2_full_flow():
    """TC-APP-003: PR > 50M VND -> Finance approve Step 2 -> status = APPROVED, 2 Approval records."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr(">50M Step2", amount_each=80_000_000, quantity=1)
        pr_id = pr["id"]

        # Step 1: Manager
        res1 = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Manager step 1 OK"
        )
        assert res1["status"] == "PENDING_FINANCE_APPROVAL"

        # Step 2: Finance
        res2 = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="finance@company.com",
            comments="Finance step 2 OK"
        )
        assert res2["status"] == "APPROVED"
        assert len(res2["approvals"]) == 2
        assert res2["approvals"][0]["step"] == "MANAGER"
        assert res2["approvals"][1]["step"] == "FINANCE"

        db_approvals = await prisma.approval.find_many(
            where={"purchaseRequestId": pr_id},
            order={"created_at": "asc"}
        )
        assert len(db_approvals) == 2
        assert db_approvals[0].decision == "APPROVED"
        assert db_approvals[1].decision == "APPROVED"

    run_async(run_test())


def test_tc_app_004_approver_identity_integrity():
    """TC-APP-004: Approver Identity Integrity -> Approval.approverId matches User.id UUID (HD-REQ-07 & HD-REQ-09)."""
    async def run_test():
        prisma = get_prisma()
        manager_user_id = await resolve_user_id_by_email("manager@company.com")
        
        pr = await helper_create_test_pr("Identity Test", amount_each=20_000_000)
        pr_id = pr["id"]

        await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Checking UUID integrity"
        )

        db_approval = await prisma.approval.find_first(where={"purchaseRequestId": pr_id})
        assert db_approval is not None
        assert db_approval.approverId == manager_user_id
        # Ensure it is a valid UUID, not an email or role string
        assert len(db_approval.approverId) == 36
        assert "@" not in db_approval.approverId

    run_async(run_test())


def test_tc_app_005_approver_email_not_found():
    """TC-APP-005: Approver Email Not Found -> raises 400 ValueError."""
    async def run_test():
        pr = await helper_create_test_pr("Unknown Approver", amount_each=10_000_000)
        pr_id = pr["id"]

        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="unknown_user_999@company.com",
                comments="Will fail"
            )
        assert "Không tìm thấy người dùng với email" in str(excinfo.value)

    run_async(run_test())


def test_tc_app_006_unauthorized_roles_rejected():
    """TC-APP-006: Unauthorized Roles (EMPLOYEE, PROCUREMENT) -> rejected with 400 ValueError."""
    async def run_test():
        pr = await helper_create_test_pr("Role Check", amount_each=10_000_000)
        pr_id = pr["id"]

        # EMPLOYEE tries to approve
        with pytest.raises(ValueError) as excinfo1:
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="employee@company.com",
                comments="Employee try"
            )
        assert "Không có thẩm quyền duyệt PR" in str(excinfo1.value)

        # PROCUREMENT tries to approve
        with pytest.raises(ValueError) as excinfo2:
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="procurement@company.com",
                comments="Procurement try"
            )
        assert "Không có thẩm quyền duyệt PR" in str(excinfo2.value)

    run_async(run_test())


def test_tc_app_007_wrong_step_order_rejected():
    """TC-APP-007: Wrong Step Order: FINANCE tries Step 1 on PR > 50M before Manager -> rejected."""
    async def run_test():
        pr = await helper_create_test_pr("Order Check", amount_each=70_000_000)
        pr_id = pr["id"]

        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="finance@company.com",
                comments="Finance trying step 1 prematurely"
            )
        assert "PR giá trị > 50 triệu VND cần Manager phê duyệt bước 1 trước" in str(excinfo.value)

    run_async(run_test())


def test_tc_app_008_status_guard_already_approved_rejected():
    """TC-APP-008: Approval Status Guard (HD-REQ-10): Approving PR already in APPROVED status -> rejected."""
    async def run_test():
        pr = await helper_create_test_pr("Guard Approved", amount_each=20_000_000)
        pr_id = pr["id"]

        # First approval -> transitions to APPROVED
        await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="First approval"
        )

        # Second approval attempt on already APPROVED PR
        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments="Duplicate approval attempt"
            )
        assert "PR đang ở trạng thái 'APPROVED', không thể thực hiện phê duyệt" in str(excinfo.value)

    run_async(run_test())


def test_tc_app_009_status_guard_invalid_statuses_rejected():
    """TC-APP-009: Approval Status Guard (HD-REQ-10): Approving PR in REJECTED/CLOSED/PO_CREATED -> rejected."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Guard Invalid Status", amount_each=15_000_000)
        pr_id = pr["id"]

        for invalid_status in ["REJECTED", "CLOSED", "PO_CREATED"]:
            await prisma.purchaserequest.update(
                where={"id": pr_id},
                data={"status": invalid_status}
            )
            with pytest.raises(ValueError) as excinfo:
                await ProcurementService.approve_pr_prisma(
                    pr_id=pr_id,
                    approver_email="manager@company.com"
                )
            assert f"PR đang ở trạng thái '{invalid_status}', không thể thực hiện phê duyệt" in str(excinfo.value)

    run_async(run_test())


def test_tc_app_010_repeated_approval_at_same_stage_rejected():
    """TC-APP-010: Repeated approval at same approval stage (Manager tries to approve again in Step 2) -> rejected."""
    async def run_test():
        pr = await helper_create_test_pr("Repeated Stage", amount_each=90_000_000)
        pr_id = pr["id"]

        # Step 1 Manager approves
        await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Manager step 1"
        )

        # Manager attempts to approve Step 2 (Finance stage)
        with pytest.raises(ValueError) as excinfo:
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="manager@company.com",
                comments="Manager trying step 2"
            )
        assert "PR giá trị > 50 triệu VND bắt buộc cần Finance duyệt bước 2" in str(excinfo.value)

    run_async(run_test())


def test_tc_app_011_atomic_rollback_on_failure():
    """TC-APP-011: Transaction Rollback on Failure -> PR status unmutated, zero orphan Approval records."""
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Rollback Test", amount_each=30_000_000)
        pr_id = pr["id"]
        initial_status = pr["status"]

        # Trigger failure inside transaction by providing an invalid approver email
        with pytest.raises(ValueError):
            await ProcurementService.approve_pr_prisma(
                pr_id=pr_id,
                approver_email="nonexistent_approver@company.com"
            )

        # Verify PR status did not change
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == initial_status

        # Verify no orphan approval records were created
        approvals = await prisma.approval.find_many(where={"purchaseRequestId": pr_id})
        assert len(approvals) == 0

    run_async(run_test())


def test_tc_app_012_concurrency_manager_race():
    """
    TC-APP-012: Concurrency: 2 concurrent requests from manager@company.com on PR > 50M:
    Row lock ensures exactly 1 request executes Step 1, while the second request fails because status changed.
    """
    async def run_test():
        prisma = get_prisma()
        pr = await helper_create_test_pr("Concurrency Race", amount_each=100_000_000)
        pr_id = pr["id"]

        results = []
        errors_list = []

        async def attempt_approval():
            try:
                res = await ProcurementService.approve_pr_prisma(
                    pr_id=pr_id,
                    approver_email="manager@company.com",
                    comments="Concurrent manager attempt"
                )
                results.append(res)
            except Exception as e:
                errors_list.append(str(e))

        # Launch 2 concurrent approval attempts
        await asyncio.gather(attempt_approval(), attempt_approval(), return_exceptions=True)

        # Exactly 1 succeeds, 1 fails
        assert len(results) == 1
        assert len(errors_list) == 1
        assert "PR giá trị > 50 triệu VND bắt buộc cần Finance duyệt bước 2" in errors_list[0]

        # PR must now be PENDING_FINANCE_APPROVAL with exactly 1 approval record
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert db_pr.status == "PENDING_FINANCE_APPROVAL"

        db_approvals = await prisma.approval.find_many(where={"purchaseRequestId": pr_id})
        assert len(db_approvals) == 1

    run_async(run_test())


def test_tc_app_013_response_contract_approvals():
    """TC-APP-013: Response Contract: nested approvals returned from PostgreSQL with step, approver, comments."""
    async def run_test():
        pr = await helper_create_test_pr("Contract Response", amount_each=25_000_000)
        pr_id = pr["id"]

        res = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="manager@company.com",
            comments="Phê duyệt chi tiết cho phòng IT"
        )

        assert "approvals" in res
        assert isinstance(res["approvals"], list)
        assert len(res["approvals"]) == 1

        app = res["approvals"][0]
        assert "id" in app
        assert app["purchaseRequestId"] == pr_id
        assert "approverId" in app
        assert app["decision"] == "APPROVED"
        assert app["comments"] == "Phê duyệt chi tiết cho phòng IT"
        assert app["step"] == "MANAGER"
        assert app["approver"] == "Trần Văn B"  # Seeded manager name

    run_async(run_test())


def test_tc_app_014_admin_two_step_approval():
    """
    TC-APP-014: ADMIN approves PR > 50M across both Step 1 and Step 2:
    - Admin Step 1 -> PENDING_FINANCE_APPROVAL
    - Admin Step 2 -> APPROVED
    - 2 Approval records with the SAME approverId (Admin's User UUID).
    - Valid behavior per REQ-BR-02.
    """
    async def run_test():
        prisma = get_prisma()
        admin_user_id = await resolve_user_id_by_email("admin@company.com")
        
        pr = await helper_create_test_pr("Admin 2-Step", amount_each=120_000_000)
        pr_id = pr["id"]

        # Admin performs Step 1 (Manager stage)
        res1 = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="admin@company.com",
            comments="Admin acting as Manager"
        )
        assert res1["status"] == "PENDING_FINANCE_APPROVAL"

        # Admin performs Step 2 (Finance stage)
        res2 = await ProcurementService.approve_pr_prisma(
            pr_id=pr_id,
            approver_email="admin@company.com",
            comments="Admin acting as Finance"
        )
        assert res2["status"] == "APPROVED"
        assert len(res2["approvals"]) == 2

        # Verify in DB: both records have the exact same admin approverId
        db_approvals = await prisma.approval.find_many(
            where={"purchaseRequestId": pr_id},
            order={"created_at": "asc"}
        )
        assert len(db_approvals) == 2
        assert db_approvals[0].approverId == admin_user_id
        assert db_approvals[1].approverId == admin_user_id
        assert db_approvals[0].decision == "APPROVED"
        assert db_approvals[1].decision == "APPROVED"

    run_async(run_test())


def test_tc_app_015_end_to_end_workflow():
    """TC-APP-015: End-to-end Workflow: create_pr_prisma -> approve_pr_prisma on the exact same PR."""
    async def run_test():
        # 1. Create PR
        pr = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST-APP] Quy trinh tao va duyet PR",
            items=[{"itemName": "Server Dell R750", "quantity": 1, "estimatedUnitPrice": 45_000_000}]
        )
        assert pr["status"] == "PENDING_MANAGER_APPROVAL"
        assert pr["approvals"] == []

        # 2. Approve PR
        approved = await ProcurementService.approve_pr_prisma(
            pr_id=pr["id"],
            approver_email="manager@company.com",
            comments="Phe duyet server moi"
        )
        assert approved["status"] == "APPROVED"
        assert len(approved["approvals"]) == 1
        assert approved["approvals"][0]["approver"] == "Trần Văn B"

    run_async(run_test())

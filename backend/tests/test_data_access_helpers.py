"""
Unit Tests for Data Access Helpers (Prisma Runtime).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.1 - User Identity Resolution & Active Budget Resolution

Tests:
- User identity resolution (email -> User.id)
  1. Valid email returns exact User.id (UUID).
  2. Non-existent email raises ValueError with clear message.
  3. Empty/whitespace email raises ValueError.
  4. Different users resolve to distinct IDs.
  5. Resolution strictly relies on email, never role/name.
- Active budget resolution (departmentId + 2026 + Q1)
  1. DEPT-IT + 2026 + Q1 returns correct Budget.
  2. DEPT-HR + 2026 + Q1 returns correct Budget.
  3. Non-existent department raises ValueError.
  4. Non-existent fiscalYear/quarter raises ValueError.
  5. Resolution does NOT mutate or auto-create Budget records.
"""

import asyncio
import threading
import pytest
from decimal import Decimal
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.data_access import (
    resolve_user_id_by_email,
    resolve_active_budget,
    ACTIVE_BUDGET_FISCAL_YEAR,
    ACTIVE_BUDGET_QUARTER,
)


class AsyncTestRunner:
    """Runs async coroutines on a single dedicated background event loop to prevent Proactor loop closure in tests."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro, timeout: float = 15.0):
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
    """Maintain single event loop and connected shared Prisma client for the test module."""
    global _runner
    _runner = AsyncTestRunner()

    async def _init_connection():
        prisma = get_prisma()
        if prisma.is_connected():
            if prisma._internal_engine is not None:
                prisma._internal_engine.close()
                prisma._internal_engine = None
        await connect_db()

    _runner.run(_init_connection())
    yield
    _runner.run(disconnect_db())
    _runner.stop()



# ==============================================================================
# User Identity Resolution Tests (HD-REQ-07)
# ==============================================================================

def test_resolve_user_id_by_email_valid():
    """Valid seeded email resolves to the correct User.id UUID."""
    async def _test():
        user_id = await resolve_user_id_by_email("employee@company.com")
        assert isinstance(user_id, str)
        assert len(user_id) == 36  # UUID standard length

        prisma = get_prisma()
        user = await prisma.user.find_unique(where={"email": "employee@company.com"})
        assert user is not None
        assert user.id == user_id
        assert user.role == "EMPLOYEE"

    run_async(_test())


def test_resolve_user_id_by_email_not_found():
    """Non-existent email raises ValueError with a clear, descriptive message."""
    async def _test():
        non_existent_email = "non_existent_999@company.com"
        with pytest.raises(ValueError) as excinfo:
            await resolve_user_id_by_email(non_existent_email)
        assert "Không tìm thấy người dùng với email" in str(excinfo.value)
        assert non_existent_email in str(excinfo.value)

    run_async(_test())


def test_resolve_user_id_by_email_empty_or_whitespace():
    """Empty, whitespace, or invalid email raises ValueError."""
    async def _test():
        for invalid in ["", "   ", None]:
            with pytest.raises(ValueError) as excinfo:
                await resolve_user_id_by_email(invalid)
            assert "không hợp lệ hoặc rỗng" in str(excinfo.value)

    run_async(_test())


def test_resolve_user_id_different_users_distinct_ids():
    """Different seeded users must resolve to distinct UUIDs without collision."""
    async def _test():
        emp_id = await resolve_user_id_by_email("employee@company.com")
        mgr_id = await resolve_user_id_by_email("manager@company.com")
        fin_id = await resolve_user_id_by_email("finance@company.com")
        proc_id = await resolve_user_id_by_email("procurement@company.com")
        adm_id = await resolve_user_id_by_email("admin@company.com")

        ids = [emp_id, mgr_id, fin_id, proc_id, adm_id]
        assert len(ids) == len(set(ids)), "Mỗi email phải resolve ra đúng User.id UUID riêng biệt"

    run_async(_test())


def test_resolve_user_id_does_not_use_role_or_name():
    """Attempting to resolve by role or name instead of email must fail."""
    async def _test():
        # Searching by role string instead of email must fail
        with pytest.raises(ValueError):
            await resolve_user_id_by_email("EMPLOYEE")

        # Searching by user name instead of email must fail
        with pytest.raises(ValueError):
            await resolve_user_id_by_email("Nguyễn Văn A")

    run_async(_test())


# ==============================================================================
# Active Budget Resolution Tests (HD-REQ-08)
# ==============================================================================

def test_resolve_active_budget_dept_it():
    """DEPT-IT resolves active Budget for 2026 Q1 matching seeded values."""
    async def _test():
        budget = await resolve_active_budget("DEPT-IT")
        assert budget is not None
        assert budget.departmentId == "DEPT-IT"
        assert budget.fiscalYear == 2026
        assert budget.quarter == 1
        assert budget.allocatedAmount == Decimal("500000000.00")
        assert budget.spentAmount == Decimal("150000000.00")
        assert budget.tempReservedAmount == Decimal("0.00")
        assert budget.department.name == "Phòng Công nghệ Thông tin"

    run_async(_test())


def test_resolve_active_budget_dept_hr():
    """DEPT-HR resolves active Budget for 2026 Q1 matching seeded values."""
    async def _test():
        budget = await resolve_active_budget("DEPT-HR")
        assert budget is not None
        assert budget.departmentId == "DEPT-HR"
        assert budget.fiscalYear == 2026
        assert budget.quarter == 1
        assert budget.allocatedAmount == Decimal("200000000.00")
        assert budget.spentAmount == Decimal("50000000.00")
        assert budget.tempReservedAmount == Decimal("0.00")
        assert budget.department.name == "Phòng Nhân sự"

    run_async(_test())


def test_resolve_active_budget_department_not_found():
    """Non-existent department ID raises ValueError with a clear message."""
    async def _test():
        with pytest.raises(ValueError) as excinfo:
            await resolve_active_budget("DEPT-UNKNOWN")
        assert "Không tìm thấy ngân sách khả dụng cho phòng ban 'DEPT-UNKNOWN'" in str(excinfo.value)

    run_async(_test())


def test_resolve_active_budget_period_not_found():
    """Valid department with unseeded fiscalYear or quarter raises ValueError."""
    async def _test():
        with pytest.raises(ValueError) as excinfo:
            await resolve_active_budget("DEPT-IT", fiscal_year=2025, quarter=4)
        assert "Năm 2025 - Quý 4" in str(excinfo.value)

    run_async(_test())


def test_resolve_active_budget_does_not_mutate_or_auto_create():
    """Looking up non-existent budget does NOT create records in database."""
    async def _test():
        prisma = get_prisma()
        initial_count = await prisma.budget.count()

        with pytest.raises(ValueError):
            await resolve_active_budget("DEPT-UNKNOWN")

        with pytest.raises(ValueError):
            await resolve_active_budget("DEPT-IT", fiscal_year=2099, quarter=1)

        after_count = await prisma.budget.count()
        assert after_count == initial_count, "Database không được tự ý thêm Budget record khi query thất bại"

    run_async(_test())

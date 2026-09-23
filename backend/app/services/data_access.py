"""
Data Access Helpers for Prisma Runtime.
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.1 - User Identity Resolution & Active Budget Resolution

Human Decisions Enforced:
- HD-REQ-07: API receives email strings, backend resolves email -> User.id (UUID).
  Foreign keys (PurchaseRequest.creatorId, Approval.approverId) MUST store User.id.
  approverRole and approverName are NOT database identities.
- HD-REQ-08: Active budget period technical convention:
  fiscalYear = 2026, quarter = 1.
  This is a Human-approved technical convention for current course/demo/integration runtime,
  NOT a confirmed business requirement or company policy.
"""

from typing import Optional
from prisma.models import User, Budget
from app.services.db import get_prisma, connect_db

# Human-approved technical convention for active budget period in course/demo runtime (HD-REQ-08)
# NOTE: This is NOT a confirmed business requirement or permanent corporate policy.
ACTIVE_BUDGET_FISCAL_YEAR = 2026
ACTIVE_BUDGET_QUARTER = 1


async def resolve_user_id_by_email(email: str) -> str:
    """
    Resolve User.id (UUID) given a valid email address.
    Enforces HD-REQ-07:
    - Resolves User.email -> User.id.
    - Does NOT use role or name to identify users.
    - Raises ValueError with clear message if user is not found or email is invalid.
    - Does NOT create a new user automatically.
    """
    if not email or not isinstance(email, str) or not email.strip():
        raise ValueError("Email người dùng không hợp lệ hoặc rỗng.")

    clean_email = email.strip()
    await connect_db()
    prisma = get_prisma()

    user = await prisma.user.find_unique(where={"email": clean_email})
    if not user:
        raise ValueError(f"Không tìm thấy người dùng với email: '{clean_email}'.")

    return user.id


async def resolve_active_budget(
    department_id: str,
    fiscal_year: int = ACTIVE_BUDGET_FISCAL_YEAR,
    quarter: int = ACTIVE_BUDGET_QUARTER,
) -> Budget:
    """
    Resolve active Budget for a department using the composite unique key:
    [departmentId, fiscalYear, quarter].
    Enforces HD-REQ-08:
    - Default period is 2026 Q1 (Human-approved technical convention for current course/demo/integration runtime).
    - Queries Budget by composite key.
    - Raises ValueError with clear message if budget or department is not found.
    - Does NOT create or mutate Budget records automatically.
    """
    if not department_id or not isinstance(department_id, str) or not department_id.strip():
        raise ValueError("Mã phòng ban (departmentId) không hợp lệ hoặc rỗng.")

    clean_dept_id = department_id.strip()
    await connect_db()
    prisma = get_prisma()

    budget = await prisma.budget.find_unique(
        where={
            "departmentId_fiscalYear_quarter": {
                "departmentId": clean_dept_id,
                "fiscalYear": fiscal_year,
                "quarter": quarter,
            }
        },
        include={"department": True},
    )

    if not budget:
        raise ValueError(
            f"Không tìm thấy ngân sách khả dụng cho phòng ban '{clean_dept_id}' "
            f"trong kỳ tài chính Năm {fiscal_year} - Quý {quarter}."
        )

    return budget

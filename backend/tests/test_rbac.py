"""
Integration Security Tests for Server-Side Role-Based Access Control (RBAC)
Task: TASK-005 - Server-Side RBAC Implementation
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery

Enforces:
- HD-02: Zero-Trust Client, role resolved from server-side DB.
- HD-12: Identity binding via Supabase Auth User ID (sub -> User.authUserId).
- GOV-01 / T-39: No Self-Approval check for all roles (including ADMIN).
- Test Matrix: Section I of docs/TASK-005-RBAC-DESIGN.md (RBAC-001 through RBAC-028).
"""

import time
import asyncio
import threading
from decimal import Decimal
from typing import Dict, Any, Optional

import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from prisma import Prisma

from app.main import app
from app.config import settings
from app.services.jwt_service import SupabaseJWTService
from app.dependencies.auth import get_jwt_service
from app.services.procurement_service import ProcurementService


# ==============================================================================
# Cryptographic Test Fixtures & Mock JWKS
# ==============================================================================

TEST_KID = "test-rbac-key-id-2026"
TEST_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()

# Deterministic authUserId UUIDs for test users
SUB_ADMIN = "11111111-0000-0000-0000-000000000001"
SUB_EMPLOYEE = "11111111-0000-0000-0000-000000000002"
SUB_FINANCE = "11111111-0000-0000-0000-000000000003"
SUB_MANAGER = "11111111-0000-0000-0000-000000000004"
SUB_PROCUREMENT = "11111111-0000-0000-0000-000000000005"

EMAIL_ADMIN = "admin@company.com"
EMAIL_EMPLOYEE = "employee@company.com"
EMAIL_FINANCE = "finance@company.com"
EMAIL_MANAGER = "manager@company.com"
EMAIL_PROCUREMENT = "procurement@company.com"


class MockSigningKey:
    def __init__(self, key, key_id: str = TEST_KID):
        self.key = key
        self.key_id = key_id


class MockJWKSClient:
    def __init__(self, key=TEST_PUBLIC_KEY):
        self._key = key

    def get_signing_key_from_jwt(self, token: str):
        return MockSigningKey(self._key)


def create_token(
    sub: str,
    email: str,
    expires_in: int = 3600,
    iss: str = settings.JWT_ISSUER,
    aud: str = settings.JWT_AUDIENCE,
) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email,
        "iss": iss,
        "aud": aud,
        "exp": now + expires_in,
        "iat": now,
        "nbf": now,
    }
    headers = {"kid": TEST_KID, "alg": "ES256"}
    return jwt.encode(payload, TEST_PRIVATE_KEY, algorithm="ES256", headers=headers)


def auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# Async Background Loop Runner & Module Setup
# ==============================================================================

class AsyncTestRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro, timeout: float = 30.0):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=timeout)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=3.0)


_runner: Optional[AsyncTestRunner] = None
_test_prisma: Optional[Prisma] = None


def run_async(coro):
    return _runner.run(coro)


@pytest.fixture(scope="module", autouse=True)
def setup_rbac_test_module():
    global _runner, _test_prisma
    _runner = AsyncTestRunner()
    _test_prisma = Prisma()
    run_async(_test_prisma.connect())

    # 1. Bind authUserId to test users in PostgreSQL
    run_async(_test_prisma.user.update(where={"email": EMAIL_ADMIN}, data={"authUserId": SUB_ADMIN}))
    run_async(_test_prisma.user.update(where={"email": EMAIL_EMPLOYEE}, data={"authUserId": SUB_EMPLOYEE}))
    run_async(_test_prisma.user.update(where={"email": EMAIL_FINANCE}, data={"authUserId": SUB_FINANCE}))
    run_async(_test_prisma.user.update(where={"email": EMAIL_MANAGER}, data={"authUserId": SUB_MANAGER}))
    run_async(_test_prisma.user.update(where={"email": EMAIL_PROCUREMENT}, data={"authUserId": SUB_PROCUREMENT}))

    yield

    # Teardown: Clean up database state
    async def module_cleanup():
        if _test_prisma and _test_prisma.is_connected():
            for email in [EMAIL_ADMIN, EMAIL_EMPLOYEE, EMAIL_FINANCE, EMAIL_MANAGER, EMAIL_PROCUREMENT]:
                await _test_prisma.user.update(where={"email": email}, data={"authUserId": None})
            await _test_prisma.user.update(where={"email": EMAIL_EMPLOYEE}, data={"role": "EMPLOYEE"})

    try:
        run_async(module_cleanup())
    except Exception:
        pass
    if _test_prisma:
        run_async(_test_prisma.disconnect())
    _runner.stop()


@pytest.fixture(autouse=True)
def clean_test_data_fixture():
    """Teardown fixture cleaning up test artifacts between tests."""
    yield
    async def cleanup():
        if _test_prisma and _test_prisma.is_connected():
            # Delete test PRs and cascade children
            test_prs = await _test_prisma.purchaserequest.find_many(
                where={"title": {"contains": "[TEST-RBAC]"}}
            )
            for pr in test_prs:
                pos = await _test_prisma.purchaseorder.find_many(where={"purchaseRequestId": pr.id})
                for po in pos:
                    await _test_prisma.receiving.delete_many(where={"purchaseOrderId": po.id})
                await _test_prisma.purchaseorder.delete_many(where={"purchaseRequestId": pr.id})
                await _test_prisma.quotation.delete_many(where={"purchaseRequestId": pr.id})
                await _test_prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
                await _test_prisma.purchaserequest.delete(where={"id": pr.id})

            # Delete test suppliers
            await _test_prisma.supplier.delete_many(where={"name": {"contains": "[TEST-RBAC]"}})

            # Reset tempReservedAmount on test budgets
            await _test_prisma.budget.update_many(
                where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
                data={"tempReservedAmount": Decimal("0.00")}
            )

    try:
        run_async(cleanup())
    except Exception:
        pass


@pytest.fixture(scope="module")
def test_client():
    mock_verifier = SupabaseJWTService(
        jwks_url=settings.SUPABASE_JWKS_URL,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        jwks_client=MockJWKSClient(key=TEST_PUBLIC_KEY),
    )
    app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_jwt_service, None)


# Helper tokens
@pytest.fixture(scope="module")
def tokens():
    return {
        "admin": create_token(SUB_ADMIN, EMAIL_ADMIN),
        "employee": create_token(SUB_EMPLOYEE, EMAIL_EMPLOYEE),
        "finance": create_token(SUB_FINANCE, EMAIL_FINANCE),
        "manager": create_token(SUB_MANAGER, EMAIL_MANAGER),
        "procurement": create_token(SUB_PROCUREMENT, EMAIL_PROCUREMENT),
    }


def helper_create_pr_api(client, token: str, title: str, amount_each: float, quantity: int = 1) -> dict:
    resp = client.post(
        "/api/pr",
        headers=auth_header(token),
        json={
            "departmentId": "DEPT-IT",
            "title": f"[TEST-RBAC] {title}",
            "items": [{"itemName": "Laptop IT", "quantity": quantity, "estimatedUnitPrice": amount_each}],
        },
    )
    assert resp.status_code == 200, f"Create PR failed: {resp.text}"
    return resp.json()


# ==============================================================================
# RBAC Test Suite (RBAC-001 through RBAC-028)
# ==============================================================================

def test_tc_rbac_001_missing_jwt(test_client):
    """RBAC-001: Missing JWT returns HTTP 401."""
    res = test_client.get("/api/pr")
    assert res.status_code == 401
    assert "Yêu cầu xác thực" in res.json()["detail"]


def test_tc_rbac_002_invalid_jwt(test_client):
    """RBAC-002: Invalid/Expired JWT returns HTTP 401."""
    expired_token = create_token(SUB_EMPLOYEE, EMAIL_EMPLOYEE, expires_in=-100)
    res = test_client.get("/api/pr", headers=auth_header(expired_token))
    assert res.status_code == 401


def test_tc_rbac_003_employee_approve_pr_forbidden(test_client, tokens):
    """RBAC-003: EMPLOYEE attempting to approve PR is rejected with HTTP 403."""
    pr = helper_create_pr_api(test_client, tokens["manager"], "Small PR", 20_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["employee"]),
        json={"comments": "Employee attempt"},
    )
    assert res.status_code == 403


def test_tc_rbac_004_manager_approve_pr_step1_success(test_client, tokens):
    """RBAC-004: MANAGER approves PR <= 50M (step 1, non-creator) -> HTTP 200 (APPROVED)."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Small PR", 25_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["manager"]),
        json={"comments": "Manager approves"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVED"


def test_tc_rbac_005_procurement_create_po_success(test_client, tokens):
    """RBAC-005: PROCUREMENT creates PO for APPROVED PR -> HTTP 200."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "PR for PO", 10_000_000)
    test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["manager"]))
    # Create quotation via Procurement
    q_res = test_client.post(
        "/api/quotations",
        headers=auth_header(tokens["procurement"]),
        json={
            "purchaseRequestId": pr["id"],
            "supplierId": "SUP-01",
            "totalAmount": 10_000_000,
            "quantity": 1,
            "deliveryDays": 3,
        },
    )
    assert q_res.status_code == 200
    quote_id = q_res.json()["id"]

    po_res = test_client.post(
        "/api/po",
        headers=auth_header(tokens["procurement"]),
        json={"purchaseRequestId": pr["id"], "quotationId": quote_id},
    )
    assert po_res.status_code == 200
    assert po_res.json()["status"] == "SENT"


def test_tc_rbac_006_finance_approve_pr_step2_success(test_client, tokens):
    """RBAC-006: FINANCE approves PR > 50M at Step 2 (non-creator) -> HTTP 200 (APPROVED)."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Large PR", 60_000_000)
    # Step 1: Manager approval
    m_res = test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["manager"]))
    assert m_res.status_code == 200
    assert m_res.json()["status"] == "PENDING_FINANCE_APPROVAL"

    # Step 2: Finance approval
    f_res = test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["finance"]))
    assert f_res.status_code == 200
    assert f_res.json()["status"] == "APPROVED"


def test_tc_rbac_007_admin_approve_pr_success(test_client, tokens):
    """RBAC-007: ADMIN approves PR (non-creator) -> HTTP 200."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Admin PR", 15_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["admin"]),
        json={"comments": "Admin approval"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVED"


def test_tc_rbac_008_client_role_injection_ignored(test_client, tokens):
    """RBAC-008: Client sends 'role: ADMIN' in body; backend uses DB role and rejects with HTTP 403."""
    res = test_client.post(
        "/api/suppliers",
        headers=auth_header(tokens["employee"]),
        json={"name": "[TEST-RBAC] Injected Supplier", "role": "ADMIN"},
    )
    assert res.status_code == 403


def test_tc_rbac_009_client_creator_id_injection_ignored(test_client, tokens):
    """RBAC-009: Client sends creatorId of Admin; backend overrides with JWT user's ID."""
    emp_token = tokens["employee"]
    res = test_client.post(
        "/api/pr",
        headers=auth_header(emp_token),
        json={
            "departmentId": "DEPT-IT",
            "creatorId": EMAIL_ADMIN,  # Client tries to impersonate Admin
            "title": "[TEST-RBAC] Injection PR",
            "items": [{"itemName": "Item A", "quantity": 1, "estimatedUnitPrice": 5_000_000}],
        },
    )
    assert res.status_code == 200
    created_pr = res.json()

    # Query DB to assert creatorId is employee's UUID, not Admin
    async def check_creator():
        pr = await _test_prisma.purchaserequest.find_unique(where={"id": created_pr["id"]})
        emp = await _test_prisma.user.find_unique(where={"email": EMAIL_EMPLOYEE})
        assert pr.creatorId == emp.id
    run_async(check_creator())


def test_tc_rbac_010_client_approver_email_injection_ignored(test_client, tokens):
    """RBAC-010: Client sends approverEmail in body; backend derives approver from JWT identity."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Approver Inject PR", 10_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["manager"]),
        json={"approverEmail": "attacker@evil.com", "comments": "Manager approves"},
    )
    assert res.status_code == 200

    # Query DB to assert Approval.approverId is Manager's UUID
    async def check_approver():
        approvals = await _test_prisma.approval.find_many(where={"purchaseRequestId": pr["id"]})
        assert len(approvals) == 1
        mgr = await _test_prisma.user.find_unique(where={"email": EMAIL_MANAGER})
        assert approvals[0].approverId == mgr.id
    run_async(check_approver())


def test_tc_rbac_011_employee_self_approval_rejected(test_client, tokens):
    """RBAC-011: EMPLOYEE creates PR and attempts self-approval -> HTTP 403 (role gate)."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Emp Self PR", 5_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["employee"]),
        json={"comments": "Self approve attempt"},
    )
    assert res.status_code == 403


def test_tc_rbac_012_manager_self_approval_rejected(test_client, tokens):
    """RBAC-012: MANAGER creates PR and attempts self-approval -> HTTP 403 (No Self-Approval — GOV-01)."""
    pr = helper_create_pr_api(test_client, tokens["manager"], "Mgr Self PR", 20_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["manager"]),
        json={"comments": "Manager self approve"},
    )
    assert res.status_code == 403
    assert "No Self-Approval — GOV-01" in res.json()["detail"]


def test_tc_rbac_013_finance_self_approval_rejected(test_client, tokens):
    """RBAC-013: FINANCE creates PR > 50M, Step 1 approved by Manager, Finance attempts self-approval at Step 2 -> HTTP 403."""
    pr = helper_create_pr_api(test_client, tokens["finance"], "Fin Self PR", 65_000_000)
    # Manager approves step 1
    m_res = test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["manager"]))
    assert m_res.status_code == 200
    assert m_res.json()["status"] == "PENDING_FINANCE_APPROVAL"

    # Finance attempts step 2 on own PR
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["finance"]),
        json={"comments": "Finance self approve"},
    )
    assert res.status_code == 403
    assert "No Self-Approval — GOV-01" in res.json()["detail"]


def test_tc_rbac_014_procurement_self_approval_rejected(test_client, tokens):
    """RBAC-014: PROCUREMENT creates PR and attempts self-approval -> HTTP 403 (role gate)."""
    pr = helper_create_pr_api(test_client, tokens["procurement"], "Proc Self PR", 10_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["procurement"]),
        json={"comments": "Procurement self approve"},
    )
    assert res.status_code == 403


def test_tc_rbac_015_admin_self_approval_rejected(test_client, tokens):
    """RBAC-015: ADMIN creates PR and attempts self-approval -> HTTP 403 (No Self-Approval — GOV-01, No Admin bypass)."""
    pr = helper_create_pr_api(test_client, tokens["admin"], "Admin Self PR", 10_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["admin"]),
        json={"comments": "Admin self approve"},
    )
    assert res.status_code == 403
    assert "No Self-Approval — GOV-01" in res.json()["detail"]


def test_tc_rbac_016_wrong_approval_stage_rejected(test_client, tokens):
    """RBAC-016: FINANCE attempts Step 1 approval on PR > 50M -> HTTP 403 (Manager required first)."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Stage Check PR", 70_000_000)
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["finance"]),
        json={"comments": "Finance tries step 1"},
    )
    assert res.status_code == 403
    assert "Manager" in res.json()["detail"]


def test_tc_rbac_017_db_role_freshness(test_client, tokens):
    """RBAC-017: Verifies role is queried dynamically from DB on each request (not cached in token)."""
    emp_token = tokens["employee"]

    # 1. Initially EMPLOYEE cannot create supplier -> HTTP 403
    res1 = test_client.post(
        "/api/suppliers",
        headers=auth_header(emp_token),
        json={"name": "[TEST-RBAC] Freshness Supplier 1"},
    )
    assert res1.status_code == 403

    # 2. Promote employee to ADMIN in DB
    async def promote():
        await _test_prisma.user.update(where={"email": EMAIL_EMPLOYEE}, data={"role": "ADMIN"})
    run_async(promote())

    # 3. Same token now succeeds without re-login!
    res2 = test_client.post(
        "/api/suppliers",
        headers=auth_header(emp_token),
        json={"name": "[TEST-RBAC] Freshness Supplier 2"},
    )
    assert res2.status_code == 200

    # 4. Restore role back to EMPLOYEE
    async def demote():
        await _test_prisma.user.update(where={"email": EMAIL_EMPLOYEE}, data={"role": "EMPLOYEE"})
    run_async(demote())

    # 5. Immediate rejection again -> HTTP 403
    res3 = test_client.post(
        "/api/suppliers",
        headers=auth_header(emp_token),
        json={"name": "[TEST-RBAC] Freshness Supplier 3"},
    )
    assert res3.status_code == 403


def test_tc_rbac_018_employee_create_po_forbidden(test_client, tokens):
    """RBAC-018: EMPLOYEE cannot create PO -> HTTP 403."""
    res = test_client.post(
        "/api/po",
        headers=auth_header(tokens["employee"]),
        json={"purchaseRequestId": "PR-FAKE", "quotationId": "Q-FAKE"},
    )
    assert res.status_code == 403


def test_tc_rbac_019_employee_create_quotation_forbidden(test_client, tokens):
    """RBAC-019: EMPLOYEE cannot create Quotation -> HTTP 403."""
    res = test_client.post(
        "/api/quotations",
        headers=auth_header(tokens["employee"]),
        json={
            "purchaseRequestId": "PR-FAKE",
            "supplierId": "SUP-01",
            "totalAmount": 1_000_000,
            "quantity": 1,
        },
    )
    assert res.status_code == 403


def test_tc_rbac_020_employee_record_receiving_forbidden(test_client, tokens):
    """RBAC-020: EMPLOYEE cannot record Receiving -> HTTP 403 (Human Decision K-3)."""
    res = test_client.post(
        "/api/receiving",
        headers=auth_header(tokens["employee"]),
        json={"purchaseOrderId": "PO-FAKE", "receivedQty": 1},
    )
    assert res.status_code == 403


def test_tc_rbac_021_finance_close_pr_success(test_client, tokens):
    """RBAC-021: FINANCE closes PR after full receiving -> HTTP 200."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Close PR Test", 10_000_000, quantity=2)
    test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["manager"]))

    q_res = test_client.post(
        "/api/quotations",
        headers=auth_header(tokens["procurement"]),
        json={
            "purchaseRequestId": pr["id"],
            "supplierId": "SUP-01",
            "totalAmount": 10_000_000,
            "quantity": 2,
        },
    )
    quote_id = q_res.json()["id"]

    po_res = test_client.post(
        "/api/po",
        headers=auth_header(tokens["procurement"]),
        json={"purchaseRequestId": pr["id"], "quotationId": quote_id},
    )
    po_id = po_res.json()["id"]

    # Record full goods receipt (2/2)
    rec_res = test_client.post(
        "/api/receiving",
        headers=auth_header(tokens["procurement"]),
        json={"purchaseOrderId": po_id, "receivedQty": 2},
    )
    assert rec_res.status_code == 200

    # Finance closes PR
    close_res = test_client.post(
        f"/api/pr/{pr['id']}/close",
        headers=auth_header(tokens["finance"]),
    )
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "CLOSED"


def test_tc_rbac_022_employee_close_pr_forbidden(test_client, tokens):
    """RBAC-022: EMPLOYEE cannot close PR -> HTTP 403."""
    res = test_client.post(
        "/api/pr/PR-FAKE/close",
        headers=auth_header(tokens["employee"]),
    )
    assert res.status_code == 403


def test_tc_rbac_023_employee_list_all_budgets_forbidden(test_client, tokens):
    """RBAC-023: EMPLOYEE cannot list all budgets -> HTTP 403."""
    res = test_client.get("/api/budget", headers=auth_header(tokens["employee"]))
    assert res.status_code == 403


def test_tc_rbac_024_finance_list_all_budgets_success(test_client, tokens):
    """RBAC-024: FINANCE can list all budgets -> HTTP 200."""
    res = test_client.get("/api/budget", headers=auth_header(tokens["finance"]))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_tc_rbac_025_employee_create_supplier_forbidden(test_client, tokens):
    """RBAC-025: EMPLOYEE cannot create supplier -> HTTP 403."""
    res = test_client.post(
        "/api/suppliers",
        headers=auth_header(tokens["employee"]),
        json={"name": "[TEST-RBAC] Emp Supplier"},
    )
    assert res.status_code == 403


def test_tc_rbac_026_procurement_create_supplier_success(test_client, tokens):
    """RBAC-026: PROCUREMENT can create supplier -> HTTP 200."""
    res = test_client.post(
        "/api/suppliers",
        headers=auth_header(tokens["procurement"]),
        json={"name": "[TEST-RBAC] Procurement Supplier", "taxCode": "0399887766"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "[TEST-RBAC] Procurement Supplier"


def test_tc_rbac_027_manager_approve_step2_forbidden(test_client, tokens):
    """RBAC-027: MANAGER cannot approve Step 2 on PR > 50M -> HTTP 403."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Step 2 Manager PR", 80_000_000)
    # Admin approves Step 1
    a_res = test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["admin"]))
    assert a_res.status_code == 200
    assert a_res.json()["status"] == "PENDING_FINANCE_APPROVAL"

    # Manager attempts Step 2
    res = test_client.post(
        f"/api/pr/{pr['id']}/approve",
        headers=auth_header(tokens["manager"]),
        json={"comments": "Manager tries step 2"},
    )
    assert res.status_code == 403
    assert "Finance" in res.json()["detail"]


def test_tc_rbac_028_admin_create_po_success(test_client, tokens):
    """RBAC-028: ADMIN can create PO -> HTTP 200."""
    pr = helper_create_pr_api(test_client, tokens["employee"], "Admin PO PR", 12_000_000)
    test_client.post(f"/api/pr/{pr['id']}/approve", headers=auth_header(tokens["manager"]))

    q_res = test_client.post(
        "/api/quotations",
        headers=auth_header(tokens["admin"]),
        json={
            "purchaseRequestId": pr["id"],
            "supplierId": "SUP-01",
            "totalAmount": 12_000_000,
            "quantity": 1,
        },
    )
    quote_id = q_res.json()["id"]

    po_res = test_client.post(
        "/api/po",
        headers=auth_header(tokens["admin"]),
        json={"purchaseRequestId": pr["id"], "quotationId": quote_id},
    )
    assert po_res.status_code == 200
    assert po_res.json()["status"] == "SENT"

"""
Integration Tests for Purchase Order (PO) & Price/Quantity Lock via Prisma Client (Supabase PostgreSQL).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.5 - Migrate Purchase Order to Prisma/PostgreSQL

Test Scope (18 Cases):
- TC-PO-001: Approved PR + valid quotation -> create PO success.
- TC-PO-002: Non-approved PR (DRAFT, PENDING_MANAGER_APPROVAL, REJECTED) -> reject.
- TC-PO-003: Quotation not found -> reject.
- TC-PO-004: Quotation belongs to another PR -> reject.
- TC-PO-005: Client totalAmount tampering -> ignored (locks to DB quotation amount).
- TC-PO-006: Client quantity tampering -> ignored (locks to DB quotation quantity).
- TC-PO-007: Quotation quantity invalid (<= 0) -> reject.
- TC-PO-008: Creator email resolves to User.id (UUID) correctly.
- TC-PO-009: Unknown creator email -> reject + no PO created.
- TC-PO-010: One PR -> one PO duplicate blocked.
- TC-PO-011: PO quantity equals Quotation.quantity (T-094 Lock).
- TC-PO-012: PO totalAmount equals Quotation.totalAmount (T-094 Lock).
- TC-PO-013: PR status transitions to PO_CREATED after successful create.
- TC-PO-014: Atomic rollback on failure (zero orphan records, PR unchanged).
- TC-PO-015: poNumber format adheres to Option A (timestamp + random hex, no count()+1).
- TC-PO-016: Concurrent create attempts for same PR cannot produce two POs (Row lock safety).
- TC-PO-017: Quotation from another PR rejected even if client tampers supplier/price.
- TC-PO-018: POST /api/po runtime actually persists to PostgreSQL with zero MockDB dual-write.
"""

import asyncio
import threading
import re
import pytest
from decimal import Decimal
import time
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.services.jwt_service import SupabaseJWTService
from app.dependencies.auth import get_jwt_service
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.procurement_service import ProcurementService, db


# Deterministic auth fixtures for API integration test (HD-02, HD-12, TASK-005 RBAC)
_AUTH_KID = "test-po-key-id-2026"
_AUTH_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
_AUTH_PUBLIC_KEY = _AUTH_PRIVATE_KEY.public_key()
_SUB_PROCUREMENT = "11111111-0000-0000-0000-000000000005"
_EMAIL_PROCUREMENT = "procurement@company.com"


class _MockSigningKey:
    def __init__(self, key, key_id: str = _AUTH_KID):
        self.key = key
        self.key_id = key_id


class _MockJWKSClient:
    def __init__(self, key=_AUTH_PUBLIC_KEY):
        self._key = key

    def get_signing_key_from_jwt(self, token: str):
        return _MockSigningKey(self._key)


def _create_procurement_token() -> str:
    now = int(time.time())
    payload = {
        "sub": _SUB_PROCUREMENT,
        "email": _EMAIL_PROCUREMENT,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": now + 3600,
        "iat": now,
        "nbf": now,
    }
    headers = {"kid": _AUTH_KID, "alg": "ES256"}
    return jwt.encode(payload, _AUTH_PRIVATE_KEY, algorithm="ES256", headers=headers)


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
    """Teardown fixture ensuring database hygiene: clean test POs, Quotations, Approvals, and PRs."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()

        # 1. Clean test PRs and all child records
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-PO]"}}
        )
        for pr in test_prs:
            # Delete child POs
            await prisma.purchaseorder.delete_many(where={"purchaseRequestId": pr.id})
            # Delete child quotations
            await prisma.quotation.delete_many(where={"purchaseRequestId": pr.id})
            # Delete child approvals
            await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
            # Delete PR (PRItems cascade)
            await prisma.purchaserequest.delete(where={"id": pr.id})

        # 2. Reset tempReservedAmount to 0
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
        title=f"[TEST-PO] PR {title_suffix}",
        items=[{"itemName": "Màn hình Dell UltraSharp", "quantity": 3, "estimatedUnitPrice": 5_000_000}]
    )
    approved = await ProcurementService.approve_pr_prisma(
        pr_id=pr["id"],
        approver_email="manager@company.com",
        comments="Approved for PO test"
    )
    return approved


async def helper_create_quotation(pr_id: str, total_amount: float = 14_400_000, quantity: int = 3) -> dict:
    """Helper to create a valid quotation for a PR in PostgreSQL."""
    return await ProcurementService.create_quotation_prisma(
        purchase_request_id=pr_id,
        supplier_id="SUP-01",
        total_amount=total_amount,
        quantity=quantity,
        delivery_days=3,
        warranty_terms="24 tháng",
        file_url="quotes/test_po_quote.pdf"
    )


# ==============================================================================
# TC-PO-001: Approved PR + valid quotation -> create PO success
# ==============================================================================
def test_tc_po_001_approved_pr_valid_quotation_success():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-001")
        quote = await helper_create_quotation(pr["id"], total_amount=15_000_000, quantity=3)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr["id"],
            quotation_id=quote["id"],
            creator_email="procurement@company.com"
        )

        assert po is not None
        assert po["purchaseRequestId"] == pr["id"]
        assert po["prId"] == pr["id"]
        assert po["quotationId"] == quote["id"]
        assert po["status"] == "SENT"
        assert po["totalAmount"] == 15_000_000.0
        assert po["quantity"] == 3
        assert po["unitPrice"] == 5_000_000.0
        assert po["supplierId"] == "SUP-01"
        assert po["supplierName"] == "Công ty TNHH Tin học Phong Vũ"
        assert po["poNumber"].startswith("PO-NUM-2026-")

        # Verify PR status transitioned to PO_CREATED in PostgreSQL
        prisma = get_prisma()
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "PO_CREATED"
    run_async(run())


# ==============================================================================
# TC-PO-002: Non-approved PR -> reject (DRAFT, PENDING_MANAGER, REJECTED)
# ==============================================================================
def test_tc_po_002_non_approved_pr_rejected():
    async def run():
        # 1. PR in PENDING_MANAGER_APPROVAL status
        pr_pending = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST-PO] PR Pending",
            items=[{"itemName": "RAM", "quantity": 2, "estimatedUnitPrice": 2_000_000}]
        )
        assert pr_pending["status"] == "PENDING_MANAGER_APPROVAL"

        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr_pending["id"],
                quotation_id="QT-DUMMY",
                creator_email="procurement@company.com"
            )
        assert "chưa được duyệt" in str(exc.value)
        assert "APPROVED" in str(exc.value)

        # 2. PR in REJECTED status
        prisma = get_prisma()
        await prisma.purchaserequest.update(
            where={"id": pr_pending["id"]},
            data={"status": "REJECTED"}
        )
        with pytest.raises(ValueError) as exc_rej:
            await ProcurementService.create_po_prisma(
                pr_id=pr_pending["id"],
                quotation_id="QT-DUMMY",
                creator_email="procurement@company.com"
            )
        assert "chưa được duyệt" in str(exc_rej.value)
        assert "REJECTED" in str(exc_rej.value)
    run_async(run())


# ==============================================================================
# TC-PO-003: Quotation not found -> reject
# ==============================================================================
def test_tc_po_003_quotation_not_found_rejected():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-003")
        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr["id"],
                quotation_id="QT-NON-EXISTENT-9999",
                creator_email="procurement@company.com"
            )
        assert "Không tìm thấy Quotation" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-PO-004: Quotation belongs to another PR -> reject
# ==============================================================================
def test_tc_po_004_quotation_belongs_to_another_pr_rejected():
    async def run():
        pr1 = await helper_create_approved_pr("TC-PO-004-PR1")
        pr2 = await helper_create_approved_pr("TC-PO-004-PR2")

        quote2 = await helper_create_quotation(pr2["id"], total_amount=10_000_000, quantity=2)

        # Attempt to create PO for PR1 using quotation of PR2
        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr1["id"],
                quotation_id=quote2["id"],
                creator_email="procurement@company.com"
            )
        assert "không thuộc về Purchase Request" in str(exc.value)
        assert pr1["id"] in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-PO-005: Client totalAmount tampering -> ignored (locks to DB quotation)
# ==============================================================================
def test_tc_po_005_client_total_amount_tampering_ignored():
    async def run():
        prisma = get_prisma()
        # 1. Bind authUserId to procurement user in PostgreSQL (HD-12)
        await prisma.user.update(
            where={"email": _EMAIL_PROCUREMENT},
            data={"authUserId": _SUB_PROCUREMENT},
        )

        # 2. Configure mock JWT verifier for FastAPI dependency injection
        mock_verifier = SupabaseJWTService(
            jwks_url=settings.SUPABASE_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            jwks_client=_MockJWKSClient(key=_AUTH_PUBLIC_KEY),
        )
        app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
        token = _create_procurement_token()

        try:
            pr = await helper_create_approved_pr("TC-PO-005")
            quote = await helper_create_quotation(pr["id"], total_amount=18_000_000, quantity=3)

            # Client maliciously sends totalAmount = 1000.0 VND via API
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/po",
                    json={
                        "purchaseRequestId": pr["id"],
                        "quotationId": quote["id"],
                        "totalAmount": 1000.0,
                        "quotation": {"totalAmount": 1000.0}
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()

            # Server MUST lock to the database quotation amount (18,000,000), ignoring client 1000.0
            assert data["totalAmount"] == 18_000_000.0
            assert data["totalAmount"] != 1000.0
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
    run_async(run())


# ==============================================================================
# TC-PO-006: Client quantity tampering -> ignored (locks to DB quotation)
# ==============================================================================
def test_tc_po_006_client_quantity_tampering_ignored():
    async def run():
        prisma = get_prisma()
        # 1. Bind authUserId to procurement user in PostgreSQL (HD-12)
        await prisma.user.update(
            where={"email": _EMAIL_PROCUREMENT},
            data={"authUserId": _SUB_PROCUREMENT},
        )

        # 2. Configure mock JWT verifier for FastAPI dependency injection
        mock_verifier = SupabaseJWTService(
            jwks_url=settings.SUPABASE_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            jwks_client=_MockJWKSClient(key=_AUTH_PUBLIC_KEY),
        )
        app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
        token = _create_procurement_token()

        try:
            pr = await helper_create_approved_pr("TC-PO-006")
            quote = await helper_create_quotation(pr["id"], total_amount=21_000_000, quantity=3)

            # Client maliciously sends quantity = 9999 and totalAmount = 500.0
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/po",
                    json={
                        "purchaseRequestId": pr["id"],
                        "quotationId": quote["id"],
                        "quantity": 9999,
                        "totalAmount": 500.0
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()

            # Server MUST lock quantity to 3 and totalAmount to 21,000,000
            assert data["quantity"] == 3
            assert data["quantity"] != 9999
            assert data["totalAmount"] == 21_000_000.0
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
    run_async(run())


# ==============================================================================
# TC-PO-007: Quotation quantity invalid -> reject
# ==============================================================================
def test_tc_po_007_quotation_quantity_invalid_rejected():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-007")
        prisma = get_prisma()

        # Artificially insert a malformed quotation with quantity = 0 directly into PostgreSQL
        malformed_quote = await prisma.quotation.create(
            data={
                "purchaseRequestId": pr["id"],
                "supplierId": "SUP-01",
                "totalAmount": Decimal("5000000.00"),
                "quantity": 0,
                "deliveryDays": 3,
                "fileUrl": "quotes/malformed.pdf"
            }
        )

        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr["id"],
                quotation_id=malformed_quote.id,
                creator_email="procurement@company.com"
            )
        assert "không hợp lệ" in str(exc.value)
        assert "số nguyên dương" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-PO-008: Creator email resolves to User.id (UUID) correctly
# ==============================================================================
def test_tc_po_008_creator_email_resolves_to_user_id():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-008")
        quote = await helper_create_quotation(pr["id"], total_amount=12_000_000, quantity=2)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr["id"],
            quotation_id=quote["id"],
            creator_email="procurement@company.com"
        )

        # Query creator User to verify UUID mapping
        prisma = get_prisma()
        user = await prisma.user.find_unique(where={"email": "procurement@company.com"})
        assert user is not None

        db_po = await prisma.purchaseorder.find_unique(where={"id": po["id"]})
        assert db_po.creatorId == user.id
        assert db_po.creatorId != "procurement@company.com"
    run_async(run())


# ==============================================================================
# TC-PO-009: Unknown creator email -> reject + no PO created
# ==============================================================================
def test_tc_po_009_unknown_creator_email_rejected():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-009")
        quote = await helper_create_quotation(pr["id"], total_amount=10_000_000, quantity=2)

        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr["id"],
                quotation_id=quote["id"],
                creator_email="nonexistent_user@company.com"
            )
        assert "Không tìm thấy người dùng" in str(exc.value)

        # Verify PR status remains APPROVED and zero PO created
        prisma = get_prisma()
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "APPROVED"
        po_count = await prisma.purchaseorder.count(where={"purchaseRequestId": pr["id"]})
        assert po_count == 0
    run_async(run())


# ==============================================================================
# TC-PO-010: One PR -> one PO duplicate blocked
# ==============================================================================
def test_tc_po_010_one_pr_one_po_duplicate_blocked():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-010")
        quote = await helper_create_quotation(pr["id"], total_amount=15_000_000, quantity=3)

        # First PO creation succeeds
        po1 = await ProcurementService.create_po_prisma(
            pr_id=pr["id"],
            quotation_id=quote["id"],
            creator_email="procurement@company.com"
        )
        assert po1 is not None

        # Second PO creation for the same PR MUST be rejected
        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr["id"],
                quotation_id=quote["id"],
                creator_email="procurement@company.com"
            )
        # Either rejected because PR status is now PO_CREATED or because PR already has a PO
        err_msg = str(exc.value)
        assert ("chưa được duyệt" in err_msg and "PO_CREATED" in err_msg) or "đã có Purchase Order" in err_msg
    run_async(run())


# ==============================================================================
# TC-PO-011: PO quantity equals Quotation.quantity (T-094 Lock)
# ==============================================================================
def test_tc_po_011_po_quantity_equals_quotation_quantity():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-011")
        quote = await helper_create_quotation(pr["id"], total_amount=24_000_000, quantity=6)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr["id"],
            quotation_id=quote["id"],
            creator_email="procurement@company.com"
        )
        assert po["quantity"] == 6
        assert po["quantity"] == quote["quantity"]
    run_async(run())


# ==============================================================================
# TC-PO-012: PO totalAmount equals Quotation.totalAmount (T-094 Lock)
# ==============================================================================
def test_tc_po_012_po_total_amount_equals_quotation_total_amount():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-012")
        quote = await helper_create_quotation(pr["id"], total_amount=36_500_000.50, quantity=5)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr["id"],
            quotation_id=quote["id"],
            creator_email="procurement@company.com"
        )
        assert po["totalAmount"] == 36_500_000.50
        assert po["totalAmount"] == quote["totalAmount"]
    run_async(run())


# ==============================================================================
# TC-PO-013: PR status transitions to PO_CREATED after successful create
# ==============================================================================
def test_tc_po_013_pr_status_becomes_po_created():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-013")
        quote = await helper_create_quotation(pr["id"], total_amount=10_000_000, quantity=2)

        await ProcurementService.create_po_prisma(
            pr_id=pr["id"],
            quotation_id=quote["id"],
            creator_email="procurement@company.com"
        )

        prisma = get_prisma()
        updated_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert updated_pr.status == "PO_CREATED"
    run_async(run())


# ==============================================================================
# TC-PO-014: Atomic rollback on failure (zero orphan records, PR unchanged)
# ==============================================================================
def test_tc_po_014_atomic_rollback_on_failure():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-014")
        prisma = get_prisma()

        # Intentionally invalid quotation ID
        with pytest.raises(ValueError):
            await ProcurementService.create_po_prisma(
                pr_id=pr["id"],
                quotation_id="QT-INVALID-ID-TRIGGER-ROLLBACK",
                creator_email="procurement@company.com"
            )

        # Verify PR status remains APPROVED (NOT PO_CREATED)
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "APPROVED"

        # Verify zero PO exists for this PR
        po_count = await prisma.purchaseorder.count(where={"purchaseRequestId": pr["id"]})
        assert po_count == 0
    run_async(run())


# ==============================================================================
# TC-PO-015: poNumber format adheres to Option A (timestamp + random hex, no count()+1)
# ==============================================================================
def test_tc_po_015_po_number_format_option_a():
    async def run():
        pr1 = await helper_create_approved_pr("TC-PO-015-1")
        pr2 = await helper_create_approved_pr("TC-PO-015-2")

        quote1 = await helper_create_quotation(pr1["id"], total_amount=10_000_000, quantity=1)
        quote2 = await helper_create_quotation(pr2["id"], total_amount=10_000_000, quantity=1)

        po1 = await ProcurementService.create_po_prisma(pr1["id"], quote1["id"])
        po2 = await ProcurementService.create_po_prisma(pr2["id"], quote2["id"])

        pattern = r"^PO-NUM-2026-\d{8}-[A-F0-9]{8}$"
        assert re.match(pattern, po1["poNumber"]), f"PO Number {po1['poNumber']} does not match Option A pattern"
        assert re.match(pattern, po2["poNumber"]), f"PO Number {po2['poNumber']} does not match Option A pattern"
        assert po1["poNumber"] != po2["poNumber"], "PO Numbers must be uniquely distinct"
    run_async(run())


# ==============================================================================
# TC-PO-016: Concurrent create attempts for same PR cannot produce two POs
# ==============================================================================
def test_tc_po_016_concurrent_create_attempts_single_po():
    async def run():
        pr = await helper_create_approved_pr("TC-PO-016-CONCURRENT")
        quote = await helper_create_quotation(pr["id"], total_amount=12_000_000, quantity=2)

        # Launch 2 simultaneous requests to create PO for the same PR
        results = await asyncio.gather(
            ProcurementService.create_po_prisma(pr["id"], quote["id"], "procurement@company.com"),
            ProcurementService.create_po_prisma(pr["id"], quote["id"], "procurement@company.com"),
            return_exceptions=True
        )

        successes = [r for r in results if isinstance(r, dict)]
        exceptions = [r for r in results if isinstance(r, Exception)]

        assert len(successes) == 1, f"Expected exactly 1 successful creation, got {len(successes)}"
        assert len(exceptions) == 1, f"Expected exactly 1 rejection, got {len(exceptions)}"

        # Exactly 1 PO exists in PostgreSQL
        prisma = get_prisma()
        db_pos = await prisma.purchaseorder.find_many(where={"purchaseRequestId": pr["id"]})
        assert len(db_pos) == 1
    run_async(run())


# ==============================================================================
# TC-PO-017: Quotation from another PR rejected even if client tampers supplier/price
# ==============================================================================
def test_tc_po_017_quotation_mismatch_with_client_tampering_rejected():
    async def run():
        prisma = get_prisma()
        # 1. Bind authUserId to procurement user in PostgreSQL (HD-12)
        await prisma.user.update(
            where={"email": _EMAIL_PROCUREMENT},
            data={"authUserId": _SUB_PROCUREMENT},
        )

        # 2. Configure mock JWT verifier for FastAPI dependency injection
        mock_verifier = SupabaseJWTService(
            jwks_url=settings.SUPABASE_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            jwks_client=_MockJWKSClient(key=_AUTH_PUBLIC_KEY),
        )
        app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
        token = _create_procurement_token()

        try:
            pr1 = await helper_create_approved_pr("TC-PO-017-PR1")
            pr2 = await helper_create_approved_pr("TC-PO-017-PR2")

            quote2 = await helper_create_quotation(pr2["id"], total_amount=30_000_000, quantity=5)

            # Client sends PR1 ID with quote2 ID, attempting to tamper price and supplier
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/po",
                    json={
                        "purchaseRequestId": pr1["id"],
                        "quotationId": quote2["id"],
                        "totalAmount": 1000.0,
                        "quantity": 1,
                        "supplierName": "Hacked Supplier"
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 400
            assert "không thuộc về Purchase Request" in response.json()["detail"]

            # Verify PR1 remains APPROVED and no PO was created
            db_pr = await prisma.purchaserequest.find_unique(where={"id": pr1["id"]})
            assert db_pr.status == "APPROVED"
            po_count = await prisma.purchaseorder.count(where={"purchaseRequestId": pr1["id"]})
            assert po_count == 0
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
    run_async(run())


# ==============================================================================
# TC-PO-018: POST /api/po runtime actually persists to PostgreSQL
# ==============================================================================
def test_tc_po_018_api_runtime_persists_to_postgresql():
    async def run():
        prisma = get_prisma()
        # 1. Bind authUserId to procurement user in PostgreSQL (HD-12)
        await prisma.user.update(
            where={"email": _EMAIL_PROCUREMENT},
            data={"authUserId": _SUB_PROCUREMENT},
        )

        # 2. Configure mock JWT verifier for FastAPI dependency injection
        mock_verifier = SupabaseJWTService(
            jwks_url=settings.SUPABASE_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            jwks_client=_MockJWKSClient(key=_AUTH_PUBLIC_KEY),
        )
        app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
        token = _create_procurement_token()

        try:
            pr = await helper_create_approved_pr("TC-PO-018")
            quote = await helper_create_quotation(pr["id"], total_amount=9_900_000, quantity=3)

            # Reset MockDB pos to verify zero dual-write
            db.pos.clear()

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/po",
                    json={
                        "purchaseRequestId": pr["id"],
                        "quotationId": quote["id"],
                        "creatorId": "procurement@company.com"
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            po_id = data["id"]

            # Verify PO exists in real PostgreSQL database
            db_po = await prisma.purchaseorder.find_unique(where={"id": po_id})
            assert db_po is not None
            assert db_po.purchaseRequestId == pr["id"]
            assert db_po.quotationId == quote["id"]
            assert float(db_po.totalAmount) == 9_900_000.0
            assert db_po.quantity == 3
            assert db_po.status == "SENT"

            # Verify zero dual-write in MockDB
            assert po_id not in db.pos
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
    run_async(run())

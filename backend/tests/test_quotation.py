"""
Tests for Quotation Domain and Server-Side Quantity Integrity (T-094 / HD-08 / TASK-008).
Synchronized with Supabase PostgreSQL Prisma Runtime & Server-Side RBAC (TASK-005).

Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-008 — Supplier & Quotation Backend API
"""

import asyncio
import threading
import time
from decimal import Decimal
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import AsyncClient, ASGITransport

import prisma.models as prisma_models
from app.config import settings
from app.dependencies.auth import get_jwt_service
from app.main import app
from app.services.db import connect_db, disconnect_db, get_prisma
from app.services.jwt_service import SupabaseJWTService
from app.services.procurement_service import ProcurementService, db

# ==============================================================================
# Deterministic Auth Fixtures for Quotation API (TASK-004 / TASK-005)
# ==============================================================================
_AUTH_KID = "test-quote-key-id-2026"
_AUTH_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
_AUTH_PUBLIC_KEY = _AUTH_PRIVATE_KEY.public_key()
_SUB_PROCUREMENT = "11111111-0000-0000-0000-000000000004"
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
def setup_quotation_test_environment():
    global _runner
    _runner = AsyncTestRunner()
    run_async(connect_db())

    prisma = get_prisma()
    # 1. Bind authUserId to procurement user in PostgreSQL (HD-12)
    run_async(prisma.user.update(
        where={"email": _EMAIL_PROCUREMENT},
        data={"authUserId": _SUB_PROCUREMENT},
    ))

    # 2. Configure mock JWT verifier for FastAPI dependency injection
    mock_verifier = SupabaseJWTService(
        jwks_url=settings.SUPABASE_JWKS_URL,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        jwks_client=_MockJWKSClient(key=_AUTH_PUBLIC_KEY),
    )
    app.dependency_overrides[get_jwt_service] = lambda: mock_verifier

    yield

    # Teardown
    app.dependency_overrides.pop(get_jwt_service, None)
    async def cleanup_module():
        p = get_prisma()
        if p and p.is_connected():
            await p.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
            # Clean test PRs and child quotations
            test_prs = await p.purchaserequest.find_many(
                where={"title": {"contains": "[TEST-QUOTE]"}}
            )
            for pr in test_prs:
                await p.quotation.delete_many(where={"purchaseRequestId": pr.id})
                await p.approval.delete_many(where={"purchaseRequestId": pr.id})
                await p.purchaserequest.delete(where={"id": pr.id})

    try:
        run_async(cleanup_module())
    except Exception:
        pass
    run_async(disconnect_db())
    _runner.stop()


@pytest.fixture(autouse=True)
def clean_quotation_test_data():
    """Teardown fixture cleaning up test artifacts between tests."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if prisma and prisma.is_connected():
            test_prs = await prisma.purchaserequest.find_many(
                where={"title": {"contains": "[TEST-QUOTE]"}}
            )
            for pr in test_prs:
                await prisma.quotation.delete_many(where={"purchaseRequestId": pr.id})
                await prisma.approval.delete_many(where={"purchaseRequestId": pr.id})
                await prisma.purchaserequest.delete(where={"id": pr.id})
    try:
        run_async(cleanup())
    except Exception:
        pass


def test_tc_quote_001_ai_compare_creates_and_persists_quantity():
    """
    TC-QUOTE-001: Comparison endpoint evaluates Quotations with valid integer quantity
    and verifies persistence server-side in Supabase PostgreSQL (T-094 / HD-08 / T-061).
    """
    async def run_test():
        prisma = get_prisma()
        # 1. Create and approve a test PR in PostgreSQL
        pr = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST-QUOTE] Comparison Test PR 001",
            items=[{"itemName": "Laptop Dell Core i7", "quantity": 1, "estimatedUnitPrice": 25_000_000}],
        )
        approved_pr = await ProcurementService.approve_pr_prisma(
            pr_id=pr["id"],
            approver_email="manager@company.com",
            comments="Approved for quotation comparison",
        )
        pr_id = approved_pr["id"]

        # 2. Persist 2 Quotations in PostgreSQL with quantity=3
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_id,
            supplier_id="SUP-01",
            total_amount=Decimal("73500000.00"),
            quantity=3,
            delivery_days=3,
            warranty_terms="24 tháng chính hãng",
            file_url="quote_dell_01.pdf",
        )
        await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr_id,
            supplier_id="SUP-02",
            total_amount=Decimal("75000000.00"),
            quantity=3,
            delivery_days=5,
            warranty_terms="12 tháng chính hãng",
            file_url="quote_hp_02.pdf",
        )

        token = _create_procurement_token()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/quotations/compare",
                headers={"Authorization": f"Bearer {token}"},
                json={"purchaseRequestId": pr_id, "files": ["quote_dell_01.pdf", "quote_hp_02.pdf"]},
            )
            assert response.status_code == 200, response.text
            data = response.json()
            assert "comparisons" in data
            assert len(data["comparisons"]) == 2

            for q in data["comparisons"]:
                # Verify quantity exists and is an integer > 0
                assert "quantity" in q
                assert isinstance(q["quantity"], int)
                assert q["quantity"] > 0
                assert q["quantity"] == 3

                # Verify commercial calculation: totalAmount == unitPrice * quantity
                assert q["totalAmount"] == q["unitPrice"] * q["quantity"]

                # Verify persistence in server-side DB (Supabase PostgreSQL via Prisma)
                q_id = q["id"]
                db_quote = await prisma.quotation.find_unique(where={"id": q_id})
                assert db_quote is not None
                assert db_quote.quantity == q["quantity"]
                assert float(db_quote.totalAmount) == q["totalAmount"]

    run_async(run_test())


def test_tc_quote_002_get_quotation_by_id_returns_quantity():
    """
    TC-QUOTE-002: Querying /api/quotations/{quotation_id} returns the quotation
    including authoritative server-side quantity from PostgreSQL (HD-08 / T-094).
    """
    async def run_test():
        # 1. Create and approve a test PR in PostgreSQL
        pr = await ProcurementService.create_pr_prisma(
            dept_id="DEPT-IT",
            creator_id="employee@company.com",
            title="[TEST-QUOTE] Get Quotation PR 002",
            items=[{"itemName": "Laptop IT", "quantity": 1, "estimatedUnitPrice": 25_000_000}],
        )
        await ProcurementService.approve_pr_prisma(
            pr_id=pr["id"],
            approver_email="manager@company.com",
            comments="Approved for quotation",
        )

        # 2. Persist quotation in PostgreSQL with quantity=3, totalAmount=75_000_000
        quote = await ProcurementService.create_quotation_prisma(
            purchase_request_id=pr["id"],
            supplier_id="SUP-01",
            total_amount=Decimal("75000000.00"),
            quantity=3,
            delivery_days=3,
            warranty_terms="24 tháng chính hãng",
            file_url="quotes/phongvu.pdf",
        )
        q_id = quote["id"]

        token = _create_procurement_token()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(
                f"/api/quotations/{q_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["id"] == q_id
            assert data["quantity"] == 3
            assert data["totalAmount"] == 75_000_000.0

    run_async(run_test())


def test_tc_quote_003_get_quotation_not_found():
    """TC-QUOTE-003: Querying a non-existent quotation returns 404 with error detail."""
    async def run_test():
        token = _create_procurement_token()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(
                "/api/quotations/QT-NON-EXISTENT",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 404
            assert "Không tìm thấy Quotation" in response.json()["detail"]
    run_async(run_test())


def test_tc_quote_004_register_quotation_service():
    """
    TC-QUOTE-004: ProcurementService.register_quotation validates integer quantity > 0
    and stores it in the database.
    """
    quote = ProcurementService.register_quotation(
        quotation_id="QT-SVC-01",
        pr_id="PR-SVC-01",
        supplier_name="FPT Computer",
        total_amount=50_000_000,
        quantity=5,
        unit_price=10_000_000
    )
    assert quote["quantity"] == 5
    assert quote["totalAmount"] == 50_000_000
    assert quote["unitPrice"] == 10_000_000
    assert db.quotations["QT-SVC-01"]["quantity"] == 5


def test_tc_quote_005_register_quotation_invalid_quantity_rejected():
    """
    TC-QUOTE-005: Reject registration if quantity <= 0 or not an int
    """
    with pytest.raises(ValueError) as exc1:
        ProcurementService.register_quotation(
            quotation_id="QT-INV-01",
            pr_id="PR-01",
            supplier_name="Test",
            total_amount=10_000_000,
            quantity=0
        )
    assert "phải là số nguyên dương" in str(exc1.value)

    with pytest.raises(ValueError) as exc2:
        ProcurementService.register_quotation(
            quotation_id="QT-INV-02",
            pr_id="PR-01",
            supplier_name="Test",
            total_amount=10_000_000,
            quantity=-2
        )
    assert "phải là số nguyên dương" in str(exc2.value)


def test_tc_quote_006_prisma_quotation_model_has_quantity():
    """
    TC-QUOTE-006: Verify Prisma Client model Quotation has field 'quantity' (int).
    Proves that data model gap in Prisma schema was resolved in Step 1 & 2.
    """
    quotation_fields = prisma_models.Quotation.model_fields
    assert "quantity" in quotation_fields
    assert quotation_fields["quantity"].annotation is int

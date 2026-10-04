"""
Phase 4F Test Suite: Goods Receiving -> Close PR Lifecycle (REQ-BR-04, HD-07, US-09, US-10).
Covers TC-REC-001 through TC-REC-012 required by Section 21:
- TC-REC-001: valid receiving
- TC-REC-002: partial receiving
- TC-REC-003: over-receiving rejected
- TC-REC-004: close while incomplete rejected
- TC-REC-005: close after full receiving succeeds
- TC-REC-006: receiving unauthorized role rejected
- TC-REC-007: nonexistent PO rejected
- TC-REC-008: closed PR/PO cannot receive incorrectly
- TC-REC-009: SUM(receivedQty) calculated from DB
- TC-REC-010: close uses DB receiving total, not client value
- TC-REC-011: PO quantity remains authoritative
- TC-REC-012: PR becomes CLOSED only after completion
"""

import asyncio
import threading
import pytest
from decimal import Decimal
import uuid
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.procurement_service import ProcurementService
from app.main import app
from app.config import settings
from app.services.jwt_service import SupabaseJWTService
from app.dependencies.auth import get_jwt_service
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import AsyncClient, ASGITransport


_AUTH_KID = "test-phase4f-key-2026"
_AUTH_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
_AUTH_PUBLIC_KEY = _AUTH_PRIVATE_KEY.public_key()

_SUB_EMPLOYEE = "33333333-0000-0000-0000-000000000001"
_EMAIL_EMPLOYEE = "employee@company.com"

_SUB_MANAGER = "33333333-0000-0000-0000-000000000002"
_EMAIL_MANAGER = "manager@company.com"

_SUB_PROCUREMENT = "33333333-0000-0000-0000-000000000003"
_EMAIL_PROCUREMENT = "procurement@company.com"

_SUB_FINANCE = "33333333-0000-0000-0000-000000000004"
_EMAIL_FINANCE = "finance@company.com"

_SUB_ADMIN = "33333333-0000-0000-0000-000000000005"
_EMAIL_ADMIN = "admin@company.com"


class _MockSigningKey:
    def __init__(self, key, key_id: str = _AUTH_KID):
        self.key = key
        self.key_id = key_id


class _MockJWKSClient:
    def __init__(self, key=_AUTH_PUBLIC_KEY):
        self._key = key

    def get_signing_key_from_jwt(self, token: str):
        return _MockSigningKey(self._key)


def _create_token(sub: str, email: str, role: str) -> str:
    headers = {"kid": _AUTH_KID}
    payload = {
        "sub": sub,
        "email": email,
        "role": role,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": 9999999999,
    }
    return jwt.encode(payload, _AUTH_PRIVATE_KEY, algorithm="ES256", headers=headers)


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
        self.thread.join(timeout=2.0)


_runner: AsyncTestRunner = None


def run_async(coro):
    return _runner.run(coro)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    global _runner
    _runner = AsyncTestRunner()
    run_async(connect_db())
    yield
    run_async(disconnect_db())
    _runner.stop()


@pytest.fixture(autouse=True)
def clean_test_data():
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()

        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-4F]"}}
        )
        pr_ids = [pr.id for pr in test_prs]
        if pr_ids:
            pos = await prisma.purchaseorder.find_many(
                where={"purchaseRequestId": {"in": pr_ids}}
            )
            po_ids = [po.id for po in pos]
            if po_ids:
                await prisma.receiving.delete_many(where={"purchaseOrderId": {"in": po_ids}})
                await prisma.purchaseorder.delete_many(where={"id": {"in": po_ids}})

            await prisma.quotation.delete_many(where={"purchaseRequestId": {"in": pr_ids}})
            await prisma.approval.delete_many(where={"purchaseRequestId": {"in": pr_ids}})
            await prisma.purchaserequest.delete_many(where={"id": {"in": pr_ids}})
    run_async(cleanup())


async def helper_setup_pr_po(suffix: str, quantity: int = 5, unit_price: float = 2000000.0):
    total_amount = quantity * unit_price
    pr = await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title=f"[TEST-4F] PR {suffix}",
        items=[{"itemName": "Laptop Dell Precision", "quantity": quantity, "estimatedUnitPrice": unit_price}]
    )
    await ProcurementService.approve_pr_prisma(
        pr_id=pr["id"],
        approver_email="manager@company.com",
        comments="Approved for Phase 4F testing"
    )
    quote = await ProcurementService.create_quotation_prisma(
        purchase_request_id=pr["id"],
        supplier_id="SUP-01",
        total_amount=total_amount,
        quantity=quantity,
        delivery_days=3,
        warranty_terms="24 tháng chính hãng",
        file_url="quotes/test_quote.pdf"
    )
    po = await ProcurementService.create_po_prisma(
        pr_id=pr["id"],
        quotation_id=quote["id"],
        creator_email="procurement@company.com"
    )
    return pr, po


# ==============================================================================
# TC-REC-001: Valid full receiving
# ==============================================================================
def test_tc_rec_001_valid_full_receiving():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-001", quantity=4)
        rec = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=4,
            file_url="receipts/full_rec.pdf",
            received_items="Nhận đủ 4 máy"
        )
        assert rec is not None
        assert rec["purchaseOrderId"] == po["id"]
        assert rec["receivedQty"] == 4
        assert rec["totalReceived"] == 4
        assert rec["poQuantity"] == 4

        # Check DB PO status updated to RECEIVED
        prisma = get_prisma()
        db_po = await prisma.purchaseorder.find_unique(where={"id": po["id"]})
        assert db_po.status == "RECEIVED"
    run_async(run())


# ==============================================================================
# TC-REC-002: Partial receiving
# ==============================================================================
def test_tc_rec_002_partial_receiving():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-002", quantity=10)
        rec1 = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=3,
            file_url="receipts/part1.pdf",
            received_items="Đợt 1 nhận 3 máy"
        )
        assert rec1["receivedQty"] == 3
        assert rec1["totalReceived"] == 3
        assert rec1["poQuantity"] == 10

        rec2 = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=4,
            file_url="receipts/part2.pdf",
            received_items="Đợt 2 nhận 4 máy"
        )
        assert rec2["receivedQty"] == 4
        assert rec2["totalReceived"] == 7
        assert rec2["poQuantity"] == 10
    run_async(run())


# ==============================================================================
# TC-REC-003: Over-receiving rejected (REQ-BR-04)
# ==============================================================================
def test_tc_rec_003_over_receiving_rejected():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-003", quantity=5)
        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty=6,
            )
        assert "vượt quá số lượng đặt trên PO" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-004: Close while incomplete rejected (HD-07)
# ==============================================================================
def test_tc_rec_004_close_while_incomplete_rejected():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-004", quantity=5)
        # Receive only 3 of 5
        await ProcurementService.receive_goods_prisma(po["id"], 3)

        with pytest.raises(ValueError) as exc:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "Hàng chưa được nhận đủ" in str(exc.value)
        assert "HD-07" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-005: Close after full receiving succeeds
# ==============================================================================
def test_tc_rec_005_close_after_full_receiving_succeeds():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-005", quantity=3)
        await ProcurementService.receive_goods_prisma(po["id"], 3)

        close_res = await ProcurementService.close_pr_prisma(pr["id"])
        assert close_res["id"] == pr["id"]
        assert close_res["status"] == "CLOSED"

        # Verify DB states
        prisma = get_prisma()
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "CLOSED"
        db_po = await prisma.purchaseorder.find_unique(where={"id": po["id"]})
        assert db_po.status == "CLOSED"
    run_async(run())


# ==============================================================================
# TC-REC-006: Receiving unauthorized role rejected
# ==============================================================================
def test_tc_rec_006_receiving_unauthorized_role_rejected():
    async def run():
        prisma = get_prisma()
        await prisma.user.update(where={"email": _EMAIL_EMPLOYEE}, data={"authUserId": _SUB_EMPLOYEE})

        mock_verifier = SupabaseJWTService(
            jwks_url=settings.SUPABASE_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            jwks_client=_MockJWKSClient(key=_AUTH_PUBLIC_KEY),
        )
        app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
        emp_token = _create_token(_SUB_EMPLOYEE, _EMAIL_EMPLOYEE, "EMPLOYEE")

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/receiving",
                    headers={"Authorization": f"Bearer {emp_token}"},
                    json={"purchaseOrderId": "PO-FAKE-ID", "receivedQty": 1}
                )
                assert res.status_code == 403
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(where={"email": _EMAIL_EMPLOYEE}, data={"authUserId": None})
    run_async(run())


# ==============================================================================
# TC-REC-007: Nonexistent PO rejected
# ==============================================================================
def test_tc_rec_007_nonexistent_po_rejected():
    async def run():
        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(
                po_id="PO-NON-EXISTENT-9999",
                received_qty=1
            )
        assert "Không tìm thấy Purchase Order" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-008: Closed PR/PO cannot receive incorrectly
# ==============================================================================
def test_tc_rec_008_closed_po_cannot_receive():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-008", quantity=2)
        await ProcurementService.receive_goods_prisma(po["id"], 2)
        await ProcurementService.close_pr_prisma(pr["id"])

        # Attempt to receive on closed PO
        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(po["id"], 1)
        assert "CLOSED" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-009: SUM(receivedQty) calculated from DB
# ==============================================================================
def test_tc_rec_009_sum_calculated_from_db():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-009", quantity=6)
        await ProcurementService.receive_goods_prisma(po["id"], 2)
        await ProcurementService.receive_goods_prisma(po["id"], 3)

        prisma = get_prisma()
        recs = await prisma.receiving.find_many(where={"purchaseOrderId": po["id"]})
        db_sum = sum(r.receivedQty for r in recs)
        assert db_sum == 5
    run_async(run())


# ==============================================================================
# TC-REC-010: Close uses DB receiving total, not client value
# ==============================================================================
def test_tc_rec_010_close_uses_db_total_authority():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-010", quantity=4)
        # Client only received 2 in DB
        await ProcurementService.receive_goods_prisma(po["id"], 2)

        # Trying to close PR must fail because DB total is 2 < 4
        with pytest.raises(ValueError) as exc:
            await ProcurementService.close_pr_prisma(pr["id"])
        assert "Tổng đã nhận: 2/4" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-011: PO quantity remains authoritative
# ==============================================================================
def test_tc_rec_011_po_quantity_authoritative():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-011", quantity=5)
        # Exactly 5 receives succeed
        await ProcurementService.receive_goods_prisma(po["id"], 5)
        # 1 more must fail against DB PO quantity
        with pytest.raises(ValueError):
            await ProcurementService.receive_goods_prisma(po["id"], 1)
    run_async(run())


# ==============================================================================
# TC-REC-012: PR becomes CLOSED only after completion
# ==============================================================================
def test_tc_rec_012_pr_closed_only_after_completion():
    async def run():
        pr, po = await helper_setup_pr_po("TC-REC-012", quantity=4)
        prisma = get_prisma()

        # Before receiving
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "PO_CREATED"

        # Partial receiving
        await ProcurementService.receive_goods_prisma(po["id"], 2)
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "PO_CREATED"

        # Complete receiving
        await ProcurementService.receive_goods_prisma(po["id"], 2)
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "PO_CREATED"

        # Close PR
        await ProcurementService.close_pr_prisma(pr["id"])
        db_pr = await prisma.purchaserequest.find_unique(where={"id": pr["id"]})
        assert db_pr.status == "CLOSED"
    run_async(run())

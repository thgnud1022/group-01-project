"""
Integration Tests for Goods Receiving via Prisma Client (Supabase PostgreSQL).
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 3B.6 — Migrate Goods Receiving to Prisma/PostgreSQL

Test Scope (14 Test Cases):
- TC-REC-001: Valid full receiving (receivedQty == PO.quantity) -> success, totalReceived matches.
- TC-REC-002: Valid partial receiving (receivedQty < PO.quantity) -> success, totalReceived matches.
- TC-REC-003: Multiple partial receivings up to PO.quantity -> cumulative sum tracked accurately.
- TC-REC-004: PO not found (non-existent UUID or poNumber) -> reject with ValueError.
- TC-REC-005: Invalid receivedQty (<= 0 or non-integer) -> reject with ValueError.
- TC-REC-006: Single receiving exceeding PO quantity -> reject with ValueError (REQ-BR-04).
- TC-REC-007: Accumulated receiving exceeding PO quantity -> reject subsequent request (REQ-BR-04).
- TC-REC-008: Goods receipt lookup by poNumber instead of PO UUID -> success.
- TC-REC-009: Atomic transaction rollback on failure -> zero orphan records in PostgreSQL.
- TC-REC-010: Concurrency safety via row-level lock (SELECT ... FOR UPDATE) -> cumulative sum never exceeds PO quantity.
- TC-REC-011: PostgreSQL persistence verification -> record verified in PostgreSQL "Receiving" table.
- TC-REC-012: Runtime API POST /api/receiving endpoint persists to PostgreSQL.
- TC-REC-013: Zero MockDB dual-write verification -> db.receivings remains untouched by PostgreSQL receiving.
- TC-REC-014: Runtime API GET /api/receiving endpoint retrieves receipts directly from PostgreSQL.
"""

import asyncio
import threading
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
_AUTH_KID = "test-rec-key-id-2026"
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
    """Teardown fixture ensuring database hygiene: clean test Receivings, POs, Quotations, Approvals, and PRs."""
    yield
    async def cleanup():
        prisma = get_prisma()
        if not prisma.is_connected():
            await prisma.connect()

        # 1. Clean test PRs and all child records
        test_prs = await prisma.purchaserequest.find_many(
            where={"title": {"contains": "[TEST-REC]"}}
        )
        pr_ids = [pr.id for pr in test_prs]
        if pr_ids:
            # Find POs to delete related Receivings
            pos = await prisma.purchaseorder.find_many(
                where={"purchaseRequestId": {"in": pr_ids}}
            )
            po_ids = [po.id for po in pos]
            if po_ids:
                await prisma.receiving.delete_many(where={"purchaseOrderId": {"in": po_ids}})
                await prisma.purchaseorder.delete_many(where={"id": {"in": po_ids}})

            # Delete child quotations
            await prisma.quotation.delete_many(where={"purchaseRequestId": {"in": pr_ids}})
            # Delete child approvals
            await prisma.approval.delete_many(where={"purchaseRequestId": {"in": pr_ids}})
            # Delete PRs (PRItems cascade)
            await prisma.purchaserequest.delete_many(where={"id": {"in": pr_ids}})

        # 2. Reset tempReservedAmount to 0
        await prisma.budget.update_many(
            where={"departmentId": {"in": ["DEPT-IT", "DEPT-HR"]}},
            data={"tempReservedAmount": Decimal("0.00")}
        )
    run_async(cleanup())


async def helper_create_test_po(title_suffix: str, quantity: int = 5, unit_price: float = 2_000_000.0) -> dict:
    """Helper to set up a complete PO in PostgreSQL: PR -> Approve -> Quotation -> PO."""
    total_amount = quantity * unit_price
    pr = await ProcurementService.create_pr_prisma(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title=f"[TEST-REC] PR {title_suffix}",
        items=[{"itemName": "Màn hình Dell Ultrasharp", "quantity": quantity, "estimatedUnitPrice": unit_price}]
    )
    await ProcurementService.approve_pr_prisma(
        pr_id=pr["id"],
        approver_email="manager@company.com",
        comments="Approved for Receiving test"
    )
    quote = await ProcurementService.create_quotation_prisma(
        purchase_request_id=pr["id"],
        supplier_id="SUP-01",
        total_amount=total_amount,
        quantity=quantity,
        delivery_days=3,
        warranty_terms="24 tháng",
        file_url="quotes/test_receiving_quote.pdf"
    )
    po = await ProcurementService.create_po_prisma(
        pr_id=pr["id"],
        quotation_id=quote["id"],
        creator_email="procurement@company.com"
    )
    return po


# ==============================================================================
# TC-REC-001: Valid full receiving (receivedQty == PO.quantity)
# ==============================================================================
def test_tc_rec_001_valid_full_receiving():
    async def run():
        po = await helper_create_test_po("TC-REC-001", quantity=5)
        rec = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=5,
            file_url="receipts/full_delivery.pdf",
            received_items="Giao đợt 1 đủ 5 màn hình Dell"
        )
        assert rec is not None
        assert rec["purchaseOrderId"] == po["id"]
        assert rec["receivedQty"] == 5
        assert rec["totalReceived"] == 5
        assert rec["poQuantity"] == 5
        assert rec["receivedItems"] == "Giao đợt 1 đủ 5 màn hình Dell"
        assert rec["fileUrl"] == "receipts/full_delivery.pdf"
        assert rec["receivedDate"] is not None
    run_async(run())


# ==============================================================================
# TC-REC-002: Valid partial receiving (receivedQty < PO.quantity)
# ==============================================================================
def test_tc_rec_002_valid_partial_receiving():
    async def run():
        po = await helper_create_test_po("TC-REC-002", quantity=10)
        rec = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=4,
            file_url="receipts/partial_delivery_1.pdf",
            received_items="Nhận trước đợt 1: 4 màn hình"
        )
        assert rec is not None
        assert rec["purchaseOrderId"] == po["id"]
        assert rec["receivedQty"] == 4
        assert rec["totalReceived"] == 4
        assert rec["poQuantity"] == 10
    run_async(run())


# ==============================================================================
# TC-REC-003: Multiple partial receivings up to PO.quantity
# ==============================================================================
def test_tc_rec_003_multiple_partial_receivings():
    async def run():
        po = await helper_create_test_po("TC-REC-003", quantity=6)
        
        # Batch 1: receive 2
        rec1 = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=2,
            file_url="receipts/batch_1.pdf"
        )
        assert rec1["receivedQty"] == 2
        assert rec1["totalReceived"] == 2

        # Batch 2: receive 3
        rec2 = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=3,
            file_url="receipts/batch_2.pdf"
        )
        assert rec2["receivedQty"] == 3
        assert rec2["totalReceived"] == 5

        # Batch 3: receive remaining 1
        rec3 = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=1,
            file_url="receipts/batch_3.pdf"
        )
        assert rec3["receivedQty"] == 1
        assert rec3["totalReceived"] == 6
        assert rec3["poQuantity"] == 6
    run_async(run())


# ==============================================================================
# TC-REC-004: PO not found (non-existent UUID or poNumber)
# ==============================================================================
def test_tc_rec_004_po_not_found():
    async def run():
        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(
                po_id="00000000-0000-0000-0000-000000000000",
                received_qty=2,
                file_url="receipts/ghost.pdf"
            )
        assert "Không tìm thấy Purchase Order" in str(exc.value)

        with pytest.raises(ValueError) as exc2:
            await ProcurementService.receive_goods_prisma(
                po_id="PO-NON-EXISTENT",
                received_qty=2,
                file_url="receipts/ghost.pdf"
            )
        assert "Không tìm thấy Purchase Order" in str(exc2.value)
    run_async(run())


# ==============================================================================
# TC-REC-005: Invalid receivedQty (<= 0 or non-integer)
# ==============================================================================
def test_tc_rec_005_invalid_received_quantity():
    async def run():
        po = await helper_create_test_po("TC-REC-005", quantity=5)

        with pytest.raises(ValueError) as exc_zero:
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty=0,
                file_url="receipts/zero.pdf"
            )
        assert "phải là số nguyên dương (> 0)" in str(exc_zero.value)

        with pytest.raises(ValueError) as exc_neg:
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty=-3,
                file_url="receipts/negative.pdf"
            )
        assert "phải là số nguyên dương (> 0)" in str(exc_neg.value)

        with pytest.raises(ValueError) as exc_invalid:
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty="invalid_qty",
                file_url="receipts/invalid.pdf"
            )
        assert "phải là số nguyên hợp lệ" in str(exc_invalid.value)
    run_async(run())


# ==============================================================================
# TC-REC-006: Single receiving exceeding PO quantity (REQ-BR-04)
# ==============================================================================
def test_tc_rec_006_single_receiving_exceeds_po_quantity():
    async def run():
        po = await helper_create_test_po("TC-REC-006", quantity=5)

        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty=6,
                file_url="receipts/over.pdf"
            )
        assert "vượt quá số lượng đặt trên PO" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-007: Accumulated receiving exceeding PO quantity (REQ-BR-04)
# ==============================================================================
def test_tc_rec_007_accumulated_receiving_exceeds_po_quantity():
    async def run():
        po = await helper_create_test_po("TC-REC-007", quantity=5)

        # Batch 1: receive 4 -> OK
        rec1 = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=4,
            file_url="receipts/batch1.pdf"
        )
        assert rec1["totalReceived"] == 4

        # Batch 2: receive 2 -> 4 + 2 = 6 > 5 -> Blocked
        with pytest.raises(ValueError) as exc:
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty=2,
                file_url="receipts/batch2_over.pdf"
            )
        assert "vượt quá số lượng đặt trên PO" in str(exc.value)
    run_async(run())


# ==============================================================================
# TC-REC-008: Goods receipt lookup by poNumber instead of PO UUID
# ==============================================================================
def test_tc_rec_008_lookup_by_po_number():
    async def run():
        po = await helper_create_test_po("TC-REC-008", quantity=3)
        po_number = po["poNumber"]
        assert po_number.startswith("PO-NUM-2026-")

        rec = await ProcurementService.receive_goods_prisma(
            po_id=po_number,  # passing poNumber string instead of UUID
            received_qty=3,
            file_url="receipts/ponumber_delivery.pdf"
        )
        assert rec["purchaseOrderId"] == po["id"]
        assert rec["poNumber"] == po_number
        assert rec["receivedQty"] == 3
        assert rec["totalReceived"] == 3
    run_async(run())


# ==============================================================================
# TC-REC-009: Atomic transaction rollback on failure
# ==============================================================================
def test_tc_rec_009_atomic_transaction_rollback():
    async def run():
        po = await helper_create_test_po("TC-REC-009", quantity=4)
        prisma = get_prisma()

        # Attempt to receive with invalid quantity exceeding PO max
        with pytest.raises(ValueError):
            await ProcurementService.receive_goods_prisma(
                po_id=po["id"],
                received_qty=10,
                file_url="receipts/fail.pdf"
            )

        # Verify zero Receiving records created for this PO in PostgreSQL
        count = await prisma.receiving.count(where={"purchaseOrderId": po["id"]})
        assert count == 0
    run_async(run())


# ==============================================================================
# TC-REC-010: Concurrency safety via row-level lock (SELECT ... FOR UPDATE)
# ==============================================================================
def test_tc_rec_010_concurrency_safety():
    async def run():
        po = await helper_create_test_po("TC-REC-010", quantity=5)

        # Launch 2 concurrent receiving requests: each requests 3 items
        # Total requested = 6 > 5. Exactly ONE must succeed and ONE must fail.
        task1 = ProcurementService.receive_goods_prisma(po["id"], 3, "url1")
        task2 = ProcurementService.receive_goods_prisma(po["id"], 3, "url2")

        results = await asyncio.gather(task1, task2, return_exceptions=True)

        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]

        assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}"
        assert len(failures) == 1, f"Expected exactly 1 failure, got {len(failures)}"
        assert "vượt quá số lượng đặt trên PO" in str(failures[0])

        # Verify total in database is exactly 3
        prisma = get_prisma()
        recs = await prisma.receiving.find_many(where={"purchaseOrderId": po["id"]})
        assert sum(r.receivedQty for r in recs) == 3
    run_async(run())


# ==============================================================================
# TC-REC-011: PostgreSQL persistence verification
# ==============================================================================
def test_tc_rec_011_postgresql_persistence():
    async def run():
        po = await helper_create_test_po("TC-REC-011", quantity=3)
        rec = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=3,
            file_url="receipts/verified.pdf",
            received_items="Bàn giao nghiệm thu toàn bộ"
        )

        prisma = get_prisma()
        db_rec = await prisma.receiving.find_unique(where={"id": rec["id"]})
        assert db_rec is not None
        assert db_rec.purchaseOrderId == po["id"]
        assert db_rec.receivedQty == 3
        assert db_rec.receivedItems == "Bàn giao nghiệm thu toàn bộ"
        assert db_rec.fileUrl == "receipts/verified.pdf"
    run_async(run())


# ==============================================================================
# TC-REC-012: Runtime API POST /api/receiving endpoint persists to PostgreSQL
# ==============================================================================
def test_tc_rec_012_api_post_receiving_endpoint():
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
            po = await helper_create_test_po("TC-REC-012", quantity=4)

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                payload = {
                    "purchaseOrderId": po["id"],
                    "receivedQty": 4,
                    "fileUrl": "https://company.com/receipts/rec-api.pdf",
                    "receivedItems": "Giao 4 màn hình qua API"
                }
                res = await client.post(
                    "/api/receiving",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert res.status_code == 200, res.text
                data = res.json()
                assert data["purchaseOrderId"] == po["id"]
                assert data["receivedQty"] == 4
                assert data["totalReceived"] == 4
                assert data["receivedItems"] == "Giao 4 màn hình qua API"

                # Verify in PostgreSQL
                db_rec = await prisma.receiving.find_unique(where={"id": data["id"]})
                assert db_rec is not None
                assert db_rec.receivedQty == 4
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
    run_async(run())


# ==============================================================================
# TC-REC-013: Zero MockDB dual-write verification
# ==============================================================================
def test_tc_rec_013_zero_mockdb_dual_write():
    async def run():
        po = await helper_create_test_po("TC-REC-013", quantity=2)

        rec = await ProcurementService.receive_goods_prisma(
            po_id=po["id"],
            received_qty=2,
            file_url="receipts/no_dual_write.pdf"
        )
        assert rec is not None

        # Verify db.receivings in MockDB has NOT been modified
        assert po["id"] not in db.receivings, "CRITICAL: MockDB dual-write detected in db.receivings!"
    run_async(run())


# ==============================================================================
# TC-REC-014: Runtime API GET /api/receiving endpoint retrieves from PostgreSQL
# ==============================================================================
def test_tc_rec_014_api_get_receiving_endpoint():
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
            po = await helper_create_test_po("TC-REC-014", quantity=5)

            # Create 2 receipts for this PO
            await ProcurementService.receive_goods_prisma(po["id"], 2, "receipts/part1.pdf", "Đợt 1")
            await ProcurementService.receive_goods_prisma(po["id"], 3, "receipts/part2.pdf", "Đợt 2")

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Query by purchaseOrderId
                res = await client.get(
                    f"/api/receiving?purchaseOrderId={po['id']}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert res.status_code == 200, res.text
                items = res.json()
                assert len(items) == 2
                assert all(item["purchaseOrderId"] == po["id"] for item in items)
                assert items[0]["poNumber"] == po["poNumber"]
        finally:
            app.dependency_overrides.pop(get_jwt_service, None)
            await prisma.user.update(
                where={"email": _EMAIL_PROCUREMENT},
                data={"authUserId": None},
            )
    run_async(run())

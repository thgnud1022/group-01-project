"""
Integration Tests for Purchase Order Creation via Prisma Client (Supabase PostgreSQL).
Phase 4E: Human Award -> Purchase Order Flow (US-09 / HD-04 / T-091..T-094)

Test Scope:
- TC-PO-001: APPROVED PR + valid quotation -> PO created successfully via create_po_prisma.
- TC-PO-002: non-APPROVED PR (DRAFT, PENDING, REJECTED) -> PO rejected with ValueError.
- TC-PO-003: quotation does not belong to PR -> rejected with ValueError.
- TC-PO-004: nonexistent quotation -> rejected with ValueError.
- TC-PO-005: unauthorized role (EMPLOYEE) -> HTTP 403 Forbidden.
- TC-PO-006: PO strictly uses DB quotation quantity (client quantity ignored).
- TC-PO-007: PO strictly uses DB quotation price (client totalAmount ignored).
- TC-PO-008: PO strictly uses DB supplier linked via Quotation.
- TC-PO-009: PO number is generated server-side.
- TC-PO-010: AI recommendation does NOT automatically create PO (Decision support boundary).
- TC-PO-011: duplicate create on same PR rejected (1 PR -> 1 PO constraint).
- TC-PO-012: created PO appears in GET /api/po listing.
"""

import asyncio
import threading
import uuid
import pytest
from decimal import Decimal
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.services.db import get_prisma, connect_db, disconnect_db
from app.services.data_access import resolve_user_id_by_email
from app.services.procurement_service import ProcurementService
from app.services.ai_service import AIService
from app.schemas.ai import QuotationRecommendationRequest, QuotationInputItem
from app.dependencies.auth import AuthenticatedUser, get_current_identity
from app.dependencies.rbac import RoleChecker
from app.routers.po import create_po, list_pos, CreatePOSchema

client = TestClient(app)


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
    try:
        run_async(disconnect_db())
    finally:
        _runner.stop()


async def _create_test_supplier(name_suffix: str = None) -> str:
    prisma = get_prisma()
    unique_suffix = f"{name_suffix or 'PO'}_{uuid.uuid4().hex[:8]}"
    supp = await prisma.supplier.create(
        data={
            "name": f"Supplier {unique_suffix}",
            "contact": f"contact_{unique_suffix}@supplier.com",
            "taxCode": f"TAX-{unique_suffix.upper()}",
        }
    )
    return supp.id


async def _create_test_pr(
    status: str = "APPROVED",
    title: str = "PR for PO testing",
    estimated_amount: float = 20_000_000,
    creator_email: str = "employee@company.com"
) -> str:
    prisma = get_prisma()
    pr_id = f"PR-PO-{uuid.uuid4().hex[:8].upper()}"
    creator_user_id = await resolve_user_id_by_email(creator_email)
    dept = await prisma.department.find_first()
    dept_id = dept.id if dept else "DEPT-IT"

    pr = await prisma.purchaserequest.create(
        data={
            "id": pr_id,
            "title": title,
            "departmentId": dept_id,
            "creatorId": creator_user_id,
            "status": status,
            "estimatedValue": Decimal(str(estimated_amount)),
            "items": {
                "create": [
                    {
                        "itemName": "Laptop Dell Precision",
                        "quantity": 2,
                        "estimatedUnitPrice": Decimal(str(estimated_amount / 2)),
                    }
                ]
            }
        }
    )
    return pr.id


async def _create_test_quotation(
    pr_id: str,
    supplier_id: str,
    total_amount: float = 19_500_000,
    quantity: int = 2,
    delivery_days: int = 5,
) -> str:
    prisma = get_prisma()
    quote = await prisma.quotation.create(
        data={
            "purchaseRequestId": pr_id,
            "supplierId": supplier_id,
            "totalAmount": Decimal(str(total_amount)),
            "quantity": quantity,
            "deliveryDays": delivery_days,
            "warrantyTerms": "24 months manufacturer warranty",
            "fileUrl": "https://storage.company.com/test_quote.pdf",
        }
    )
    return quote.id


async def _get_auth_user(email: str, role_override: str = None) -> AuthenticatedUser:
    prisma = get_prisma()
    u = await prisma.user.find_unique(where={"email": email})
    if not u:
        raise ValueError(f"User not found for email: {email}")
    return AuthenticatedUser(
        id=u.id,
        auth_sub=u.authUserId or f"sub-{u.id}",
        email=u.email,
        name=u.name,
        role=role_override or u.role,
        departmentId=u.departmentId,
    )


# ==============================================================================
# TC-PO-001: APPROVED PR + valid quotation -> PO created successfully
# ==============================================================================
def test_tc_po_001_approved_pr_valid_quotation_success():
    async def _test():
        prisma = get_prisma()
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id, total_amount=18_000_000, quantity=2)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr_id,
            quotation_id=quote_id,
            creator_email="procurement@company.com"
        )

        assert po is not None
        assert po["purchaseRequestId"] == pr_id
        assert po["quotationId"] == quote_id
        assert po["supplierId"] == supp_id
        assert po["totalAmount"] == 18_000_000.0
        assert po["quantity"] == 2
        assert po["unitPrice"] == 9_000_000.0
        assert po["status"] == "SENT"
        assert po["poNumber"].startswith("PO-NUM-")
        assert po.get("prTitle") == "PR for PO testing"

        # Verify PR status updated to PO_CREATED
        pr = await prisma.purchaserequest.find_unique(where={"id": pr_id})
        assert pr.status == "PO_CREATED"

    run_async(_test())


# ==============================================================================
# TC-PO-002: Non-APPROVED PR -> PO rejected (HD-04)
# ==============================================================================
def test_tc_po_002_non_approved_pr_rejected():
    async def _test():
        supp_id = await _create_test_supplier()

        for invalid_status in ["DRAFT", "PENDING_MANAGER_APPROVAL", "REVISION_REQUIRED", "REJECTED"]:
            pr_id = await _create_test_pr(status=invalid_status)
            quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id)

            with pytest.raises(ValueError) as exc:
                await ProcurementService.create_po_prisma(
                    pr_id=pr_id,
                    quotation_id=quote_id,
                    creator_email="procurement@company.com"
                )
            assert "chưa được duyệt" in str(exc.value)

    run_async(_test())


# ==============================================================================
# TC-PO-003: Quotation does not belong to PR -> rejected
# ==============================================================================
def test_tc_po_003_quotation_mismatch_pr_rejected():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_a_id = await _create_test_pr(status="APPROVED", title="PR A")
        pr_b_id = await _create_test_pr(status="APPROVED", title="PR B")
        quote_b_id = await _create_test_quotation(pr_id=pr_b_id, supplier_id=supp_id)

        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr_a_id,
                quotation_id=quote_b_id,
                creator_email="procurement@company.com"
            )
        assert "không thuộc về Purchase Request" in str(exc.value)

    run_async(_test())


# ==============================================================================
# TC-PO-004: Nonexistent quotation -> rejected
# ==============================================================================
def test_tc_po_004_nonexistent_quotation_rejected():
    async def _test():
        pr_id = await _create_test_pr(status="APPROVED")
        fake_quote_id = f"fake-quote-{uuid.uuid4().hex}"

        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr_id,
                quotation_id=fake_quote_id,
                creator_email="procurement@company.com"
            )
        assert "Không tìm thấy Quotation" in str(exc.value)

    run_async(_test())


# ==============================================================================
# TC-PO-005: Unauthorized role (EMPLOYEE) -> HTTP 403 Forbidden
# ==============================================================================
def test_tc_po_005_unauthorized_role_rejected():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id)
        emp_user = await _get_auth_user("employee@company.com")
        proc_user = await _get_auth_user("procurement@company.com")

        # Test RoleChecker dependency
        checker = RoleChecker(["PROCUREMENT", "ADMIN"])
        with pytest.raises(HTTPException) as exc:
            await checker(current_user=emp_user)
        assert exc.value.status_code == 403
        assert "Quyền truy cập bị từ chối" in str(exc.value.detail)

        # Procurement user passes
        ok_user = await checker(current_user=proc_user)
        assert ok_user.role == "PROCUREMENT"

        # Unauthenticated request without JWT header returns 401
        unauth_resp = client.post("/api/po", json={"purchaseRequestId": pr_id, "quotationId": quote_id})
        assert unauth_resp.status_code == 401

    run_async(_test())


# ==============================================================================
# TC-PO-006: PO strictly uses DB quotation quantity (client quantity ignored)
# ==============================================================================
def test_tc_po_006_po_uses_db_quotation_quantity():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        # Quotation has quantity 5 in DB
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id, quantity=5, total_amount=25_000_000)
        proc_user = await _get_auth_user("procurement@company.com")

        # Client attempts to tamper quantity to 9999 via CreatePOSchema payload
        payload = CreatePOSchema(
            purchaseRequestId=pr_id,
            quotationId=quote_id,
            quantity=9999
        )
        po = await create_po(payload=payload, current_user=proc_user)

        assert po is not None
        assert po["quantity"] == 5  # strictly DB value, NOT 9999

    run_async(_test())


# ==============================================================================
# TC-PO-007: PO strictly uses DB quotation price (client totalAmount ignored)
# ==============================================================================
def test_tc_po_007_po_uses_db_quotation_price():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        # Quotation has totalAmount 30_000_000 in DB
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id, quantity=3, total_amount=30_000_000)
        proc_user = await _get_auth_user("procurement@company.com")

        # Client attempts to tamper totalAmount to 1.0 via CreatePOSchema payload
        payload = CreatePOSchema(
            purchaseRequestId=pr_id,
            quotationId=quote_id,
            totalAmount=1.0
        )
        po = await create_po(payload=payload, current_user=proc_user)

        assert po is not None
        assert po["totalAmount"] == 30_000_000.0  # strictly DB value
        assert po["unitPrice"] == 10_000_000.0

    run_async(_test())


# ==============================================================================
# TC-PO-008: PO strictly uses DB supplier linked via Quotation
# ==============================================================================
def test_tc_po_008_po_uses_db_supplier():
    async def _test():
        supp_id = await _create_test_supplier("Alpha")
        pr_id = await _create_test_pr(status="APPROVED")
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr_id,
            quotation_id=quote_id,
            creator_email="procurement@company.com"
        )
        assert po["supplierId"] == supp_id
        assert "Alpha" in po["supplierName"]

    run_async(_test())


# ==============================================================================
# TC-PO-009: PO number generated server-side
# ==============================================================================
def test_tc_po_009_po_number_generated_server_side():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id)

        po = await ProcurementService.create_po_prisma(
            pr_id=pr_id,
            quotation_id=quote_id,
            creator_email="procurement@company.com"
        )
        assert po["poNumber"] is not None
        assert len(po["poNumber"]) > 10
        assert po["poNumber"].startswith("PO-NUM-")

    run_async(_test())


# ==============================================================================
# TC-PO-010: AI recommendation does NOT automatically create PO
# ==============================================================================
def test_tc_po_010_ai_recommendation_does_not_create_po():
    async def _test():
        prisma = get_prisma()
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        quote_1 = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id, total_amount=10_000_000)
        quote_2 = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id, total_amount=12_000_000)

        # Count POs before AI
        pos_before = await prisma.purchaseorder.count(where={"purchaseRequestId": pr_id})
        assert pos_before == 0

        # Run AI recommendation
        req = QuotationRecommendationRequest(
            purchase_request_id=pr_id,
            quotations=[
                QuotationInputItem(
                    quotation_id=quote_1,
                    supplier_name="Supplier 1",
                    total_amount=10_000_000,
                    unit_price=5_000_000,
                    quantity=2,
                    delivery_days=3
                ),
                QuotationInputItem(
                    quotation_id=quote_2,
                    supplier_name="Supplier 2",
                    total_amount=12_000_000,
                    unit_price=6_000_000,
                    quantity=2,
                    delivery_days=5
                )
            ]
        )
        res = await AIService.recommend_quotations_async(req)
        assert res.recommended_quotation_id is not None

        # Verify zero PO created after AI
        pos_after = await prisma.purchaseorder.count(where={"purchaseRequestId": pr_id})
        assert pos_after == 0

    run_async(_test())


# ==============================================================================
# TC-PO-011: Duplicate create does not create duplicate PO (1 PR -> 1 PO)
# ==============================================================================
def test_tc_po_011_duplicate_create_rejected():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED")
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id)

        # First PO creation succeeds
        await ProcurementService.create_po_prisma(
            pr_id=pr_id,
            quotation_id=quote_id,
            creator_email="procurement@company.com"
        )

        # Second PO creation on same PR MUST be rejected
        with pytest.raises(ValueError) as exc:
            await ProcurementService.create_po_prisma(
                pr_id=pr_id,
                quotation_id=quote_id,
                creator_email="procurement@company.com"
            )
        assert "chưa được duyệt" in str(exc.value) or "đã có Purchase Order" in str(exc.value)

    run_async(_test())


# ==============================================================================
# TC-PO-012: Created PO appears in GET /api/po listing
# ==============================================================================
def test_tc_po_012_created_po_appears_in_listing():
    async def _test():
        supp_id = await _create_test_supplier()
        pr_id = await _create_test_pr(status="APPROVED", title="Unique Monitor Setup PR")
        quote_id = await _create_test_quotation(pr_id=pr_id, supplier_id=supp_id, total_amount=15_000_000)

        created_po = await ProcurementService.create_po_prisma(
            pr_id=pr_id,
            quotation_id=quote_id,
            creator_email="procurement@company.com"
        )

        proc_user = await _get_auth_user("procurement@company.com")
        po_list = await list_pos(current_user=proc_user)

        matched = [p for p in po_list if p["id"] == created_po["id"]]
        assert len(matched) == 1
        assert matched[0]["poNumber"] == created_po["poNumber"]
        assert matched[0]["prTitle"] == "Unique Monitor Setup PR"
        assert matched[0]["status"] == "SENT"

        # Unauthenticated request without JWT returns 401
        unauth_resp = client.get("/api/po")
        assert unauth_resp.status_code == 401

    run_async(_test())

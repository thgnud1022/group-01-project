import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.procurement_service import ProcurementService, db
import prisma.models as prisma_models

client = TestClient(app)

def test_tc_quote_001_ai_compare_creates_and_persists_quantity():
    """
    TC-QUOTE-001: AI comparison generates Quotations with valid integer quantity
    and persists them server-side into db.quotations.
    """
    pr_id = "PR-QUOTE-TEST-01"
    files = ["quote_dell_01.pdf", "quote_hp_02.pdf"]
    
    response = client.post(
        "/api/quotations/compare",
        json={"purchaseRequestId": pr_id, "files": files}
    )
    assert response.status_code == 200
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
        
        # Verify persistence in server-side DB
        q_id = q["id"]
        assert q_id in db.quotations
        stored = db.quotations[q_id]
        assert stored["quantity"] == q["quantity"]
        assert stored["totalAmount"] == q["totalAmount"]

def test_tc_quote_002_get_quotation_by_id_returns_quantity():
    """
    TC-QUOTE-002: Querying /api/quotations/{quotation_id} returns the quotation
    including authoritative server-side quantity.
    """
    q_id = "QT-TEST-GET-01"
    db.quotations[q_id] = {
        "id": q_id,
        "quotation_id": q_id,
        "purchaseRequestId": "PR-01",
        "supplierName": "Phong Vũ",
        "totalAmount": 75_000_000,
        "quantity": 3,
        "unitPrice": 25_000_000
    }
    
    response = client.get(f"/api/quotations/{q_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == q_id
    assert data["quantity"] == 3
    assert data["totalAmount"] == 75_000_000

def test_tc_quote_003_get_quotation_not_found():
    """TC-QUOTE-003: Querying a non-existent quotation returns 404"""
    response = client.get("/api/quotations/QT-NON-EXISTENT")
    assert response.status_code == 404
    assert "Không tìm thấy Quotation" in response.json()["detail"]

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

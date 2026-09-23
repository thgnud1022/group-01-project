import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.procurement_service import ProcurementService, db
import prisma.models as prisma_models

client = TestClient(app)

def setup_test_data():
    """Helper to set up an approved PR and a registered Quotation in MockDB"""
    db.budgets["DEPT-IT"]["tempReservedAmount"] = 0
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="Trang bi thiet bi cho phong IT",
        items=[{"itemName": "Server Component", "quantity": 3, "estimatedUnitPrice": 1_600_000}]
    )
    # PR <= 50m only needs Manager approval to be APPROVED
    ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "Approved for procurement")
    
    quote_id = f"QT-US09-{pr['id']}"
    quote_record = {
        "quotation_id": quote_id,
        "id": quote_id,
        "purchaseRequestId": pr["id"],
        "supplier_id": "SUP-01",
        "supplier_name": "Công ty TNHH Tin học Phong Vũ",
        "supplierName": "Công ty TNHH Tin học Phong Vũ",
        "totalAmount": 4_800_000,
        "total_amount": 4_800_000,
        "unitPrice": 1_600_000,
        "unit_price": 1_600_000,
        "quantity": 3,
        "deliveryDays": 3,
        "warrantyTerms": "36 tháng"
    }
    db.quotations[quote_id] = quote_record
    return pr, quote_record


# ==============================================================================
# TC-US09-001: Approved PR + valid quotation -> tạo PO thành công (HAPPY PATH)
# ==============================================================================
def test_tc_us09_001_approved_pr_valid_quotation_success():
    """
    TC-US09-001: Approved PR + valid quotation -> PO created successfully via service & API.
    Enforces Case 1 (Happy Path):
    - Quotation has quantity = 3, totalAmount = 4,800,000.
    - Client sends no commercial quantities.
    - PO.quantity is locked to 3 and PO.totalAmount is locked to 4,800,000.
    """
    pr, quote = setup_test_data()
    pr_id = pr["id"]
    quote_id = quote["quotation_id"]
    
    # Verify pre-condition: PR is APPROVED
    assert pr["status"] == "APPROVED"
    
    # API Call: Create PO using server-side quotationId (client supplies NO commercial data)
    response = client.post(
        "/api/po",
        json={
            "purchaseRequestId": pr_id,
            "quotationId": quote_id,
            "creatorId": "procurement@company.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["purchaseRequestId"] == pr_id
    assert data["quotationId"] == quote_id
    assert data["totalAmount"] == quote["totalAmount"]
    assert data["totalAmount"] == 4_800_000
    assert data["quantity"] == quote["quantity"]
    assert data["quantity"] == 3
    assert data["supplierName"] == "Công ty TNHH Tin học Phong Vũ"

    assert data["status"] == "SENT"
    assert "poNumber" in data
    
    # Verify PR state transitioned to PO_CREATED
    assert db.prs[pr_id]["status"] == "PO_CREATED"

# ==============================================================================
# TC-US09-002: Non-approved PR -> reject (BUG-001 / REQ-BR-10 / HD-04)
# ==============================================================================
def test_tc_us09_002_non_approved_pr_rejected_draft():
    """TC-US09-002a: PR in DRAFT status MUST be rejected when attempting to create PO"""
    pr_id = "PR-TEST-DRAFT"
    db.prs[pr_id] = {
        "id": pr_id,
        "title": "Draft PR",
        "deptId": "DEPT-IT",
        "creatorId": "emp@company.com",
        "estimatedValue": 10_000_000,
        "items": [],
        "status": "DRAFT"
    }
    quote_id = "QT-TEST-DRAFT"
    db.quotations[quote_id] = {
        "quotation_id": quote_id,
        "purchaseRequestId": pr_id,
        "totalAmount": 10_000_000
    }
    
    # Service call verification
    with pytest.raises(ValueError) as excinfo:
        ProcurementService.create_po(pr_id=pr_id, quotation_id=quote_id)
    assert "chưa được duyệt" in str(excinfo.value)
    assert "APPROVED" in str(excinfo.value)
    
    # API call verification
    response = client.post("/api/po", json={"purchaseRequestId": pr_id, "quotationId": quote_id})
    assert response.status_code == 400
    assert "chưa được duyệt" in response.json()["detail"]
    assert db.prs[pr_id]["status"] == "DRAFT"

def test_tc_us09_002_non_approved_pr_rejected_pending_manager():
    """TC-US09-002b: PR in PENDING_MANAGER_APPROVAL MUST be rejected"""
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="Unapproved PR",
        items=[{"itemName": "RAM", "quantity": 2, "estimatedUnitPrice": 2_000_000}]
    )
    pr_id = pr["id"]
    assert pr["status"] == "PENDING_MANAGER_APPROVAL"
    
    quote_id = f"QT-PENDING-{pr_id}"
    db.quotations[quote_id] = {
        "quotation_id": quote_id,
        "purchaseRequestId": pr_id,
        "totalAmount": 4_000_000
    }
    
    response = client.post("/api/po", json={"purchaseRequestId": pr_id, "quotationId": quote_id})
    assert response.status_code == 400
    assert "chưa được duyệt" in response.json()["detail"]
    assert db.prs[pr_id]["status"] == "PENDING_MANAGER_APPROVAL"

def test_tc_us09_002_non_approved_pr_rejected_pending_finance():
    """TC-US09-002c: PR > 50m in PENDING_FINANCE_APPROVAL MUST be rejected"""
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="High value PR needing 2-step approval",
        items=[{"itemName": "High End Switch", "quantity": 2, "estimatedUnitPrice": 35_000_000}] # 70m
    )
    # Only Step 1 Manager approved
    ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "Manager OK")
    assert pr["status"] == "PENDING_FINANCE_APPROVAL"
    
    quote_id = f"QT-PENDING-FIN-{pr['id']}"
    db.quotations[quote_id] = {
        "quotation_id": quote_id,
        "purchaseRequestId": pr["id"],
        "totalAmount": 70_000_000
    }
    
    response = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote_id})
    assert response.status_code == 400
    assert "chưa được duyệt" in response.json()["detail"]
    assert db.prs[pr["id"]]["status"] == "PENDING_FINANCE_APPROVAL"

def test_tc_us09_002_non_approved_pr_rejected_rejected():
    """TC-US09-002d: PR with status REJECTED MUST be rejected"""
    pr_id = "PR-TEST-REJECTED"
    db.prs[pr_id] = {
        "id": pr_id,
        "title": "Rejected PR",
        "deptId": "DEPT-IT",
        "creatorId": "emp@company.com",
        "estimatedValue": 10_000_000,
        "items": [],
        "status": "REJECTED"
    }
    quote_id = "QT-TEST-REJECTED"
    db.quotations[quote_id] = {
        "quotation_id": quote_id,
        "purchaseRequestId": pr_id,
        "totalAmount": 10_000_000
    }
    
    response = client.post("/api/po", json={"purchaseRequestId": pr_id, "quotationId": quote_id})
    assert response.status_code == 400
    assert "chưa được duyệt" in response.json()["detail"]
    assert db.prs[pr_id]["status"] == "REJECTED"

# ==============================================================================
# TC-US09-003: PR ↔ Quotation Integrity
# ==============================================================================
def test_tc_us09_003_quotation_mismatch_pr_rejected():
    """TC-US09-003a: Quotation belonging to another PR MUST be rejected"""
    pr1, quote1 = setup_test_data()
    pr2, quote2 = setup_test_data()
    
    # Attempt to create PO for PR1 using Quotation of PR2
    response = client.post(
        "/api/po",
        json={
            "purchaseRequestId": pr1["id"],
            "quotationId": quote2["quotation_id"]
        }
    )
    assert response.status_code == 400
    assert "không thuộc về Purchase Request" in response.json()["detail"]
    assert pr1["status"] == "APPROVED"

def test_tc_us09_003_quotation_not_found_rejected():
    """TC-US09-003b: Non-existent quotation MUST be rejected"""
    pr, _ = setup_test_data()
    response = client.post(
        "/api/po",
        json={
            "purchaseRequestId": pr["id"],
            "quotationId": "QT-NON-EXISTENT"
        }
    )
    assert response.status_code == 400
    assert "Không tìm thấy Quotation" in response.json()["detail"]

def test_tc_us09_003_duplicate_po_rejected():
    """TC-US09-003c: Cannot create duplicate PO for the same PR (1-1 relation)"""
    pr, quote = setup_test_data()
    # First PO creation succeeds
    res1 = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote["quotation_id"]})
    assert res1.status_code == 200
    
    # Second PO creation for same PR must be rejected (status is now PO_CREATED, not APPROVED)
    res2 = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote["quotation_id"]})
    assert res2.status_code == 400
    assert "PO_CREATED" in res2.json()["detail"] or "đã có Purchase Order" in res2.json()["detail"]

    # Even if PR status were artificially kept as APPROVED, 1-1 guard explicitly rejects duplicate PO
    db.prs[pr["id"]]["status"] = "APPROVED"
    res3 = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote["quotation_id"]})
    assert res3.status_code == 400
    assert "đã có Purchase Order" in res3.json()["detail"]


# ==============================================================================
# TC-US09-004: Commercial Data Lock (REQ-BR-03 / REQ-BR-12 / REQ-FR-16)
# ==============================================================================
def test_tc_us09_004_client_tamper_total_amount_ignored():
    """TC-US09-004: Client attempts to tamper with totalAmount -> Server ignores and locks DB amount"""
    pr, quote = setup_test_data()
    db_amount = quote["totalAmount"] # 44,000,000
    
    # Client maliciously sends totalAmount = 1,000 VND
    response = client.post(
        "/api/po",
        json={
            "purchaseRequestId": pr["id"],
            "quotationId": quote["quotation_id"],
            "totalAmount": 1000.0,
            "quotation": {"total_amount": 1000.0}
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Server MUST have locked to the database amount, ignoring the client payload
    assert data["totalAmount"] == db_amount
    assert data["totalAmount"] != 1000.0

# ==============================================================================
# TC-US09-005: Server-Side Quantity Lock & Client Tampering (HD-08 / T-094)
# ==============================================================================
def test_tc_us09_005_client_tamper_quantity_ignored():
    """
    TC-US09-005a: Client attempts to send arbitrary quantity & totalAmount ->
    Server NEVER uses client quantity/totalAmount, locks strictly to server-side quotation (Case 2).
    """
    pr, quote = setup_test_data()
    
    response = client.post(
        "/api/po",
        json={
            "purchaseRequestId": pr["id"],
            "quotationId": quote["quotation_id"],
            "quantity": 9999,
            "totalAmount": 1.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Server must lock PO.quantity to Quotation.quantity (3) and ignore client 9999
    assert data.get("quantity") == quote["quantity"]
    assert data.get("quantity") == 3
    assert data.get("quantity") != 9999
    
    # Server must lock PO.totalAmount to Quotation.totalAmount (4,800,000) and ignore client 1.0
    assert data.get("totalAmount") == quote["totalAmount"]
    assert data.get("totalAmount") == 4_800_000
    assert data.get("totalAmount") != 1.0


# ==============================================================================
# TC-US09-006: Invalid Quotation Quantity Validation (Case 3 / HD-08 / T-094)
# ==============================================================================
def test_tc_us09_006_missing_quotation_quantity_rejected():
    """TC-US09-006a: Quotation missing quantity MUST be rejected and block PO creation"""
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="PR for missing quote qty test",
        items=[{"itemName": "Part", "quantity": 1, "estimatedUnitPrice": 1_000_000}]
    )
    ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "Approved")
    
    quote_id = f"QT-NO-QTY-{pr['id']}"
    db.quotations[quote_id] = {
        "quotation_id": quote_id,
        "id": quote_id,
        "purchaseRequestId": pr["id"],
        "totalAmount": 1_000_000,
        "supplierName": "Test Supplier"
        # quantity field is missing entirely
    }
    
    # Service call verification
    with pytest.raises(ValueError) as excinfo:
        ProcurementService.create_po(pr_id=pr["id"], quotation_id=quote_id)
    assert "thiếu thông tin số lượng" in str(excinfo.value)
    
    # API call verification
    response = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote_id})
    assert response.status_code == 400
    assert "thiếu thông tin số lượng" in response.json()["detail"]
    assert db.prs[pr["id"]]["status"] == "APPROVED"  # Not transitioned to PO_CREATED


def test_tc_us09_006_zero_or_negative_quotation_quantity_rejected():
    """TC-US09-006b: Quotation with quantity <= 0 MUST be rejected and block PO creation"""
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="PR for non-positive quote qty test",
        items=[{"itemName": "Part", "quantity": 1, "estimatedUnitPrice": 1_000_000}]
    )
    ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "Approved")
    
    # Test zero quantity
    quote_id_zero = f"QT-ZERO-QTY-{pr['id']}"
    db.quotations[quote_id_zero] = {
        "quotation_id": quote_id_zero,
        "id": quote_id_zero,
        "purchaseRequestId": pr["id"],
        "totalAmount": 1_000_000,
        "quantity": 0,
        "supplierName": "Test Supplier"
    }
    response = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote_id_zero})
    assert response.status_code == 400
    assert "phải là số nguyên dương" in response.json()["detail"]
    assert db.prs[pr["id"]]["status"] == "APPROVED"

    # Test negative quantity
    quote_id_neg = f"QT-NEG-QTY-{pr['id']}"
    db.quotations[quote_id_neg] = {
        "quotation_id": quote_id_neg,
        "id": quote_id_neg,
        "purchaseRequestId": pr["id"],
        "totalAmount": 1_000_000,
        "quantity": -3,
        "supplierName": "Test Supplier"
    }
    response_neg = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote_id_neg})
    assert response_neg.status_code == 400
    assert "phải là số nguyên dương" in response_neg.json()["detail"]
    assert db.prs[pr["id"]]["status"] == "APPROVED"


def test_tc_us09_006_non_integer_quotation_quantity_rejected():
    """TC-US09-006c: Quotation with non-integer quantity (e.g. float or str) MUST be rejected"""
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="PR for non-int quote qty test",
        items=[{"itemName": "Part", "quantity": 1, "estimatedUnitPrice": 1_000_000}]
    )
    ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "Approved")
    
    quote_id = f"QT-FLOAT-QTY-{pr['id']}"
    db.quotations[quote_id] = {
        "quotation_id": quote_id,
        "id": quote_id,
        "purchaseRequestId": pr["id"],
        "totalAmount": 1_000_000,
        "quantity": 3.5,  # float instead of int
        "supplierName": "Test Supplier"
    }
    response = client.post("/api/po", json={"purchaseRequestId": pr["id"], "quotationId": quote_id})
    assert response.status_code == 400
    assert "phải là số nguyên dương" in response.json()["detail"]
    assert db.prs[pr["id"]]["status"] == "APPROVED"


def test_t094_quantity_field_resolved():
    """
    TC-US09-005b: Verification of Data Model Resolution for T-094 (HD-08 Option A):
    - Model PurchaseOrder HAS field 'quantity' (Int)
    - Model Quotation HAS field 'quantity' (Int)
    Authoritative server-side data source for PO quantity is now present in Prisma schema & PostgreSQL.
    """
    po_fields = prisma_models.PurchaseOrder.model_fields
    quotation_fields = prisma_models.Quotation.model_fields

    assert "quantity" in po_fields, "PurchaseOrder model must have quantity"
    assert "quantity" in quotation_fields, "Quotation model must have quantity field after HD-08 resolution"
    assert quotation_fields["quantity"].annotation is int, "Quotation.quantity must be of type integer"



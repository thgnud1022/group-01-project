import pytest
from app.services.procurement_service import ProcurementService, db

def test_req_br_01_budget_check_rejection():
    """REQ-BR-01: System must block PR creation if estimated value exceeds available budget"""
    dept_id = "DEPT-IT"
    budget = ProcurementService.get_budget(dept_id)
    available = budget["availableAmount"]
    
    # Attempt to create PR exceeding available budget by 10,000,000 VND
    excessive_price = available + 10_000_000
    
    with pytest.raises(ValueError) as excinfo:
        ProcurementService.create_pr(
            dept_id=dept_id,
            creator_id="employee@company.com",
            title="Thử nghiệm PR vượt ngân sách",
            items=[{"itemName": "Siêu máy tính Server", "quantity": 1, "estimatedUnitPrice": excessive_price}]
        )
        
    assert "vượt quá Ngân sách khả dụng" in str(excinfo.value)

def test_req_br_02_multilevel_approval_threshold():
    """REQ-BR-02: PR > 50m VND requires 2-level approval (Manager then Finance)"""
    pr = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="Thiết bị hạ tầng mạng > 50 triệu",
        items=[{"itemName": "Switch Cisco Enterprise", "quantity": 2, "estimatedUnitPrice": 30_000_000}] # Total: 60m
    )
    
    # Manager Step 1 Approval
    pr = ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "Manager approved step 1")
    assert pr["status"] == "PENDING_FINANCE_APPROVAL"
    
    # Finance Step 2 Approval
    pr = ProcurementService.approve_pr(pr["id"], "FINANCE", "Finance D", "Finance approved step 2")
    assert pr["status"] == "APPROVED"

def test_req_br_03_po_price_lock():
    """REQ-BR-03: PO total & unit price must match 100% with chosen quotation"""
    quotation = {
        "quotation_id": "QT-999",
        "supplier_name": "Phong Vũ",
        "unit_price": 24_500_000,
        "quantity": 3,
        "total_amount": 73_500_000
    }
    
    # Create PR & Approve
    pr = ProcurementService.create_pr("DEPT-IT", "emp1", "Test PO Lock", [{"itemName": "Dell", "quantity": 3, "estimatedUnitPrice": 25_000_000}])
    ProcurementService.approve_pr(pr["id"], "MANAGER", "Manager B", "OK")
    
    po = ProcurementService.create_po(pr["id"], quotation, "proc1")
    assert po["unitPrice"] == quotation["unit_price"]
    assert po["totalAmount"] == quotation["total_amount"]
    assert po["supplierName"] == quotation["supplier_name"]

def test_req_br_04_receiving_qty_limit():
    """REQ-BR-04: Accumulated received quantity cannot exceed PO quantity"""
    po_id = "PO-MOCK-1"
    db.pos[po_id] = {"id": po_id, "quantity": 5}
    
    # Receive 3 items
    ProcurementService.receive_goods(po_id, 3, "url1")
    
    # Receive 2 items (Total 5 - OK)
    ProcurementService.receive_goods(po_id, 2, "url2")
    
    # Attempt to receive 1 extra item (Total 6 > 5 -> Blocked)
    with pytest.raises(ValueError) as excinfo:
        ProcurementService.receive_goods(po_id, 1, "url3")
        
    assert "vượt quá số lượng đặt trên PO" in str(excinfo.value)

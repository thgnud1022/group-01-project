from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_budget():
    response = client.get("/api/budget/DEPT-IT")
    assert response.status_code == 200
    data = response.json()
    assert data["departmentName"] == "Phòng Công nghệ Thông tin"
    assert data["allocatedAmount"] == 500000000

def test_ai_standardize_pr():
    payload = {"raw_text": "Cần mua gấp 3 máy in HP cho phòng IT"}
    response = client.post("/api/assistant/standardize-pr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["items"][0]["itemName"] == "Máy in HP Laser Multifunction"
    assert data["items"][0]["quantity"] == 3

def test_full_7step_procurement_workflow():
    # 1. Create PR
    pr_payload = {
        "departmentId": "DEPT-IT",
        "creatorId": "employee@company.com",
        "title": "Mua 3 máy in HP Laser Multifunction",
        "items": [{"itemName": "Máy in HP Laser Multifunction", "quantity": 3, "estimatedUnitPrice": 8500000}]
    }
    res_pr = client.post("/api/pr", json=pr_payload)
    assert res_pr.status_code == 200
    pr_id = res_pr.json()["id"]

    # 2. Approve PR Step 1 (Manager)
    res_app1 = client.post(f"/api/pr/{pr_id}/approve", json={"approverRole": "MANAGER", "approverName": "Manager B"})
    assert res_app1.status_code == 200
    assert res_app1.json()["status"] == "APPROVED"

    # 3. AI Compare Quotations
    res_comp = client.post("/api/quotations/compare", json={"purchaseRequestId": pr_id, "files": ["q1.pdf", "q2.pdf", "q3.pdf"]})
    assert res_comp.status_code == 200
    comparisons = res_comp.json()["comparisons"]
    assert len(comparisons) == 3

    # 4. Create PO (Choose Quotation 0 with 100% price lock)
    best_quotation = comparisons[0]
    res_po = client.post("/api/po", json={"purchaseRequestId": pr_id, "quotation": best_quotation})
    assert res_po.status_code == 200
    po_id = res_po.json()["id"]

    # 5. Receive Goods (Goods Receipt)
    res_rec = client.post("/api/receiving", json={"purchaseOrderId": po_id, "receivedQty": 3, "fileUrl": "url"})
    assert res_rec.status_code == 200
    assert res_rec.json()["receivedQty"] == 3

    # 6. Close PR & Settle Budget
    res_close = client.post(f"/api/pr/{pr_id}/close")
    assert res_close.status_code == 200
    assert res_close.json()["status"] == "CLOSED"

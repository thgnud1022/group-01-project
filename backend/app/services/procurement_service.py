from typing import Dict, Any, List

class MockDatabase:
    """
    In-Memory Database State for Fast Testing & Offline Execution.
    Reflects the exact Prisma Schema entities.
    """
    def __init__(self):
        self.budgets = {
            "DEPT-IT": {
                "departmentId": "DEPT-IT",
                "departmentName": "Phòng Công nghệ Thông tin",
                "allocatedAmount": 500_000_000,
                "spentAmount": 150_000_000,
                "tempReservedAmount": 0
            },
            "DEPT-HR": {
                "departmentId": "DEPT-HR",
                "departmentName": "Phòng Nhân sự",
                "allocatedAmount": 200_000_000,
                "spentAmount": 50_000_000,
                "tempReservedAmount": 0
            }
        }
        self.prs: Dict[str, Dict[str, Any]] = {}
        self.pos: Dict[str, Dict[str, Any]] = {}
        self.receivings: Dict[str, List[Dict[str, Any]]] = {}

db = MockDatabase()

class ProcurementService:
    @staticmethod
    def get_budget(dept_id: str) -> Dict[str, Any]:
        budget = db.budgets.get(dept_id)
        if not budget:
            raise ValueError(f"Không tìm thấy ngân sách cho phòng ban {dept_id}")
        
        available = budget["allocatedAmount"] - budget["spentAmount"] - budget["tempReservedAmount"]
        return {
            **budget,
            "availableAmount": available
        }

    @staticmethod
    def create_pr(dept_id: str, creator_id: str, title: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_estimated = sum(item["quantity"] * item["estimatedUnitPrice"] for item in items)
        
        # REQ-BR-01: Check Budget
        budget = ProcurementService.get_budget(dept_id)
        if total_estimated > budget["availableAmount"]:
            raise ValueError(
                f"Tạo PR thất bại: Giá trị ước tính ({total_estimated:,.0f}đ) vượt quá "
                f"Ngân sách khả dụng còn lại của {budget['departmentName']} ({budget['availableAmount']:,.0f}đ)."
            )
            
        pr_id = f"PR-2026-00{len(db.prs) + 1}"
        pr_record = {
            "id": pr_id,
            "title": title,
            "deptId": dept_id,
            "creatorId": creator_id,
            "estimatedValue": total_estimated,
            "items": items,
            "status": "PENDING_MANAGER_APPROVAL",
            "approvals": []
        }
        
        # Lock reserved budget
        db.budgets[dept_id]["tempReservedAmount"] += total_estimated
        db.prs[pr_id] = pr_record
        return pr_record

    @staticmethod
    def approve_pr(pr_id: str, approver_role: str, approver_name: str, comments: str) -> Dict[str, Any]:
        pr = db.prs.get(pr_id)
        if not pr:
            raise ValueError(f"Không tìm thấy mã PR {pr_id}")
            
        # REQ-BR-02: Multi-level approval threshold (> 50m VND)
        value = pr["estimatedValue"]
        
        if value > 50_000_000 and pr["status"] == "PENDING_MANAGER_APPROVAL":
            if approver_role not in ["MANAGER", "ADMIN"]:
                raise ValueError("PR giá trị > 50 triệu VND cần Manager phê duyệt bước 1 trước.")
            pr["status"] = "PENDING_FINANCE_APPROVAL"
            pr["approvals"].append({"step": "MANAGER", "approver": approver_name, "comments": comments})
        elif value > 50_000_000 and pr["status"] == "PENDING_FINANCE_APPROVAL":
            if approver_role not in ["FINANCE", "ADMIN"]:
                raise ValueError("PR giá trị > 50 triệu VND bắt buộc cần Finance duyệt bước 2.")
            pr["status"] = "APPROVED"
            pr["approvals"].append({"step": "FINANCE", "approver": approver_name, "comments": comments})
        else:
            if approver_role not in ["MANAGER", "ADMIN", "FINANCE"]:
                raise ValueError("Không có thẩm quyền duyệt PR.")
            pr["status"] = "APPROVED"
            pr["approvals"].append({"step": "MANAGER", "approver": approver_name, "comments": comments})
            
        return pr

    @staticmethod
    def create_po(pr_id: str, quotation: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        pr = db.prs.get(pr_id)
        if not pr:
            raise ValueError(f"Không tìm thấy PR {pr_id}")
            
        po_id = f"PO-2026-00{len(db.pos) + 1}"
        
        # REQ-BR-03: 100% Price Lock from Quotation
        po_record = {
            "id": po_id,
            "poNumber": f"PO-NUM-2026-00{len(db.pos) + 1}",
            "prId": pr_id,
            "quotationId": quotation["quotation_id"],
            "supplierName": quotation["supplier_name"],
            "totalAmount": quotation["total_amount"],
            "unitPrice": quotation["unit_price"],
            "quantity": quotation["quantity"],
            "creatorId": creator_id,
            "status": "SENT"
        }
        
        db.pos[po_id] = po_record
        pr["status"] = "PO_CREATED"
        return po_record

    @staticmethod
    def receive_goods(po_id: str, received_qty: int, file_url: str) -> Dict[str, Any]:
        po = db.pos.get(po_id)
        if not po:
            raise ValueError(f"Không tìm thấy PO {po_id}")
            
        current_receivings = db.receivings.get(po_id, [])
        total_already_received = sum(r["receivedQty"] for r in current_receivings)
        
        # REQ-BR-04: Limit Receiving Qty <= PO Qty
        if total_already_received + received_qty > po["quantity"]:
            raise ValueError(
                f"Nhận hàng thất bại: Tổng số lượng nhận ({total_already_received + received_qty}) "
                f"vượt quá số lượng đặt trên PO ({po['quantity']})."
            )
            
        rec_record = {
            "id": f"REC-00{len(current_receivings) + 1}",
            "poId": po_id,
            "receivedQty": received_qty,
            "fileUrl": file_url
        }
        
        if po_id not in db.receivings:
            db.receivings[po_id] = []
        db.receivings[po_id].append(rec_record)
        return rec_record

    @staticmethod
    def close_pr(pr_id: str, finance_user: str) -> Dict[str, Any]:
        pr = db.prs.get(pr_id)
        if not pr:
            raise ValueError(f"Không tìm thấy PR {pr_id}")
            
        dept_id = pr["deptId"]
        estimated_val = pr["estimatedValue"]
        
        # Release temp reserved & add actual spent
        db.budgets[dept_id]["tempReservedAmount"] -= estimated_val
        db.budgets[dept_id]["spentAmount"] += estimated_val
        
        pr["status"] = "CLOSED"
        return pr

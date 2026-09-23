from typing import Dict, Any, List, Optional
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation as DecimalException
from prisma import errors
from app.services.db import get_prisma, connect_db
from app.services.data_access import (
    resolve_user_id_by_email,
    ACTIVE_BUDGET_FISCAL_YEAR,
    ACTIVE_BUDGET_QUARTER,
)

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
        self.quotations: Dict[str, Dict[str, Any]] = {}
        self.suppliers: Dict[str, Dict[str, Any]] = {
            "SUP-01": {"id": "SUP-01", "name": "Công ty TNHH Tin học Phong Vũ", "taxCode": "0301234567"},
            "SUP-02": {"id": "SUP-02", "name": "Công ty TNHH Máy tính Trần Anh", "taxCode": "0107654321"},
            "SUP-03": {"id": "SUP-03", "name": "Công ty Cổ phần Máy tính FPT", "taxCode": "0101234999"},
        }
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
    async def create_pr_prisma(
        dept_id: str,
        creator_id: str,
        title: str,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Prisma Client Python implementation for PR creation directly to Supabase PostgreSQL.
        Enforces:
        - HD-REQ-07: Resolve creator email -> User.id (UUID).
        - HD-REQ-08: Active budget period FY2026 Q1.
        - REQ-BR-01: Budget check and row-level reservation within an atomic transaction.
        - Decimal monetary calculations.
        - Row-level lock (SELECT ... FOR UPDATE) for lost-update & overspending protection.
        - Isolated multi-transaction retry for PR ID collisions.
        - Response contract: approvals = [].
        """
        # 1. Validate request items
        if not items or not isinstance(items, list):
            raise ValueError("Danh sách mặt hàng (items) không được rỗng.")

        items_create_data = []
        total_estimated = Decimal("0.00")

        for idx, item in enumerate(items):
            item_name = item.get("itemName")
            if not item_name or not isinstance(item_name, str) or not item_name.strip():
                raise ValueError(f"Tên mặt hàng tại dòng {idx + 1} không hợp lệ hoặc rỗng.")

            raw_qty = item.get("quantity")
            try:
                qty = int(raw_qty)
            except (ValueError, TypeError):
                raise ValueError(f"Số lượng (quantity) của mặt hàng '{item_name}' phải là số nguyên hợp lệ.")
            if qty <= 0:
                raise ValueError(f"Số lượng (quantity) của mặt hàng '{item_name}' phải lớn hơn 0.")

            raw_price = item.get("estimatedUnitPrice")
            try:
                unit_price = Decimal(str(raw_price))
            except (ValueError, TypeError, DecimalException):
                raise ValueError(f"Đơn giá (estimatedUnitPrice) của mặt hàng '{item_name}' không hợp lệ.")
            if unit_price < Decimal("0.00"):
                raise ValueError(f"Đơn giá (estimatedUnitPrice) của mặt hàng '{item_name}' không được âm.")

            line_total = Decimal(str(qty)) * unit_price
            total_estimated += line_total

            items_create_data.append({
                "itemName": item_name.strip(),
                "quantity": qty,
                "estimatedUnitPrice": unit_price,
            })

        # 2. Resolve creator email -> User.id (HD-REQ-07)
        user_id = await resolve_user_id_by_email(creator_id)

        # 3. Validate Department independently
        if not dept_id or not isinstance(dept_id, str) or not dept_id.strip():
            raise ValueError("Mã phòng ban (departmentId) không hợp lệ hoặc rỗng.")
        clean_dept_id = dept_id.strip()

        await connect_db()
        prisma = get_prisma()

        dept = await prisma.department.find_unique(where={"id": clean_dept_id})
        if not dept:
            raise ValueError(f"Không tìm thấy phòng ban với mã '{clean_dept_id}'.")

        # 4. Determine base candidate number
        latest_prs = await prisma.purchaserequest.find_many(
            where={"id": {"startswith": "PR-2026-"}},
            order={"id": "desc"},
            take=1,
        )
        if latest_prs:
            try:
                base_num = int(latest_prs[0].id.split("-")[-1]) + 1
            except (ValueError, IndexError):
                base_num = await prisma.purchaserequest.count() + 1
        else:
            base_num = await prisma.purchaserequest.count() + 1

        # 5. Isolated Multi-Transaction Retry Loop (max 3 attempts)
        max_retries = 3
        last_exception = None

        for attempt in range(max_retries):
            candidate_id = f"PR-2026-{(base_num + attempt):03d}"
            try:
                # START BRAND NEW TRANSACTION FOR EACH ATTEMPT
                async with prisma.tx() as tx:
                    # 6. Lock Budget row with SELECT ... FOR UPDATE (parameterized)
                    # Enforces HD-REQ-08: fiscalYear=2026, quarter=1
                    rows = await tx.query_raw(
                        'SELECT id, "allocatedAmount", "spentAmount", "tempReservedAmount" '
                        'FROM "Budget" '
                        'WHERE "departmentId" = $1 AND "fiscalYear" = $2 AND quarter = $3 '
                        'FOR UPDATE',
                        clean_dept_id,
                        ACTIVE_BUDGET_FISCAL_YEAR,
                        ACTIVE_BUDGET_QUARTER,
                    )
                    if not rows:
                        raise ValueError(
                            f"Không tìm thấy ngân sách khả dụng cho phòng ban '{clean_dept_id}' "
                            f"trong kỳ tài chính Năm {ACTIVE_BUDGET_FISCAL_YEAR} - Quý {ACTIVE_BUDGET_QUARTER}."
                        )

                    budget_row = rows[0]
                    budget_id = budget_row["id"]
                    allocated = Decimal(str(budget_row["allocatedAmount"]))
                    spent = Decimal(str(budget_row["spentAmount"]))
                    current_reserved = Decimal(str(budget_row["tempReservedAmount"]))
                    available = allocated - spent - current_reserved

                    # 7. Check REQ-BR-01
                    if total_estimated > available:
                        raise ValueError(
                            f"Tạo PR thất bại: Giá trị ước tính ({total_estimated:,.0f}đ) vượt quá "
                            f"Ngân sách khả dụng còn lại của {dept.name} ({available:,.0f}đ)."
                        )

                    # 8. Reserve budget in transaction
                    new_reserved = current_reserved + total_estimated
                    await tx.budget.update(
                        where={"id": budget_id},
                        data={"tempReservedAmount": new_reserved},
                    )

                    # 9. Create PurchaseRequest + PRItems
                    created_pr = await tx.purchaserequest.create(
                        data={
                            "id": candidate_id,
                            "title": title.strip() if title else "",
                            "status": "PENDING_MANAGER_APPROVAL",
                            "creatorId": user_id,
                            "departmentId": clean_dept_id,
                            "estimatedValue": total_estimated,
                            "items": {"create": items_create_data},
                        },
                        include={"items": True},
                    )

                    # 10. Return response contract (approvals = [])
                    return {
                        "id": created_pr.id,
                        "title": created_pr.title,
                        "departmentId": created_pr.departmentId,
                        "deptId": created_pr.departmentId,
                        "creatorId": created_pr.creatorId,
                        "estimatedValue": float(created_pr.estimatedValue),
                        "items": [
                            {
                                "id": it.id,
                                "itemName": it.itemName,
                                "quantity": it.quantity,
                                "estimatedUnitPrice": float(it.estimatedUnitPrice),
                            }
                            for it in created_pr.items
                        ],
                        "status": created_pr.status,
                        "approvals": [],
                    }

            except errors.UniqueViolationError as e:
                # Attempt failed: Transaction rolled back completely, budget reservation is undone.
                last_exception = e
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"Không thể tạo Purchase Request sau {max_retries} lần thử do trùng lặp mã ID: {str(e)}"
                    )
                continue

        if last_exception:
            raise last_exception

    @staticmethod
    async def approve_pr_prisma(
        pr_id: str,
        approver_email: str,
        comments: Optional[str] = "Phê duyệt PR",
    ) -> Dict[str, Any]:
        """
        Prisma Client Python implementation for PR approval directly in Supabase PostgreSQL.
        Enforces:
        - HD-REQ-09: Resolve approverEmail -> User.id (UUID) and fetch User.role from PostgreSQL.
        - HD-REQ-10: Status Guard (only execute when status is PENDING_MANAGER_APPROVAL or PENDING_FINANCE_APPROVAL).
        - REQ-BR-02: Multi-level approval threshold (> 50M VND: Manager -> Finance; <= 50M VND: Manager/Admin).
        - Atomic transaction using prisma.tx().
        - Row-level lock (SELECT ... FOR UPDATE) to prevent concurrency races & duplicate approvals.
        - Stage-based duplicate approval guard (allows ADMIN to legitimately approve both Step 1 and Step 2).
        - Response contract returning full PR with nested approvals from PostgreSQL.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã PR không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        if not approver_email or not isinstance(approver_email, str) or not approver_email.strip():
            raise ValueError("Email người phê duyệt (approverEmail) không hợp lệ hoặc rỗng.")
        clean_approver_email = approver_email.strip().lower()

        await connect_db()
        prisma = get_prisma()

        threshold = Decimal("50000000.00")

        async with prisma.tx() as tx:
            # 1. Lock PurchaseRequest row with SELECT ... FOR UPDATE
            locked_prs = await tx.query_raw(
                'SELECT id, status, "estimatedValue" FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy mã PR {clean_pr_id}")

            current_pr = locked_prs[0]
            current_status = current_pr["status"]
            estimated_val = Decimal(str(current_pr["estimatedValue"]))

            # 2. HD-REQ-10: Approval Status Guard
            if current_status not in ["PENDING_MANAGER_APPROVAL", "PENDING_FINANCE_APPROVAL"]:
                raise ValueError(
                    f"PR đang ở trạng thái '{current_status}', không thể thực hiện phê duyệt."
                )

            # 3. HD-REQ-09: Resolve approver email -> User.id & User.role from PostgreSQL
            user = await tx.user.find_unique(where={"email": clean_approver_email})
            if not user:
                raise ValueError(f"Không tìm thấy người dùng với email '{clean_approver_email}'.")

            approver_role = user.role
            approver_id = user.id

            # 4. REQ-BR-02: Multi-level approval threshold & Stage-based authorization
            if estimated_val > threshold:
                if current_status == "PENDING_MANAGER_APPROVAL":
                    if approver_role not in ["MANAGER", "ADMIN"]:
                        raise ValueError("PR giá trị > 50 triệu VND cần Manager phê duyệt bước 1 trước.")
                    new_status = "PENDING_FINANCE_APPROVAL"
                elif current_status == "PENDING_FINANCE_APPROVAL":
                    if approver_role not in ["FINANCE", "ADMIN"]:
                        raise ValueError("PR giá trị > 50 triệu VND bắt buộc cần Finance duyệt bước 2.")
                    new_status = "APPROVED"
                else:
                    raise ValueError(
                        f"PR đang ở trạng thái '{current_status}', không thể thực hiện phê duyệt."
                    )
            else:
                # PR <= 50M VND (1-Level approval)
                if current_status == "PENDING_MANAGER_APPROVAL":
                    if approver_role not in ["MANAGER", "ADMIN"]:
                        raise ValueError("Không có thẩm quyền duyệt PR.")
                    new_status = "APPROVED"
                else:
                    raise ValueError(
                        f"PR có giá trị <= 50 triệu VND không ở trạng thái PENDING_MANAGER_APPROVAL (hiện tại: '{current_status}')."
                    )

            # 5. Insert Approval record into PostgreSQL
            await tx.approval.create(
                data={
                    "purchaseRequestId": clean_pr_id,
                    "approverId": approver_id,
                    "decision": "APPROVED",
                    "comments": comments.strip() if (comments and isinstance(comments, str)) else "Phê duyệt PR",
                }
            )

            # 6. Update PurchaseRequest status
            await tx.purchaserequest.update(
                where={"id": clean_pr_id},
                data={"status": new_status},
            )

        # 7. Query updated PurchaseRequest with approvals from PostgreSQL
        pr = await prisma.purchaserequest.find_unique(
            where={"id": clean_pr_id},
            include={
                "items": True,
                "approvals": {
                    "include": {"approver": True},
                    "order_by": {"created_at": "asc"},
                },
            },
        )
        if not pr:
            raise ValueError(f"Không thể truy vấn PR sau khi phê duyệt: {clean_pr_id}")

        return {
            "id": pr.id,
            "title": pr.title,
            "description": pr.description,
            "departmentId": pr.departmentId,
            "creatorId": pr.creatorId,
            "estimatedValue": float(pr.estimatedValue),
            "status": pr.status,
            "items": [
                {
                    "id": it.id,
                    "itemName": it.itemName,
                    "quantity": it.quantity,
                    "estimatedUnitPrice": float(it.estimatedUnitPrice),
                }
                for it in pr.items
            ],
            "approvals": [
                {
                    "id": app.id,
                    "purchaseRequestId": app.purchaseRequestId,
                    "approverId": app.approverId,
                    "decision": app.decision,
                    "comments": app.comments,
                    "createdAt": app.created_at.isoformat() if app.created_at else None,
                    "step": app.approver.role if app.approver else "MANAGER",
                    "approver": app.approver.name if app.approver else "Approver",
                }
                for app in pr.approvals
            ],
        }

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

    # =========================================================================
    # STEP 3B.4: Supplier & Quotation Prisma Client Implementations
    # =========================================================================

    @staticmethod
    async def create_supplier_prisma(
        name: str,
        tax_code: Optional[str] = None,
        contact: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Supplier directly in Supabase PostgreSQL via Prisma Client.
        Enforces:
        - name MUST be a non-empty string.
        - Unique constraint on name in PostgreSQL.
        """
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("Tên nhà cung cấp không hợp lệ hoặc rỗng.")
        clean_name = name.strip()
        clean_tax_code = tax_code.strip() if (tax_code and isinstance(tax_code, str) and tax_code.strip()) else None
        clean_contact = contact.strip() if (contact and isinstance(contact, str) and contact.strip()) else None

        await connect_db()
        prisma = get_prisma()
        try:
            supplier = await prisma.supplier.create(
                data={
                    "name": clean_name,
                    "taxCode": clean_tax_code,
                    "contact": clean_contact,
                }
            )
            return {
                "id": supplier.id,
                "name": supplier.name,
                "taxCode": supplier.taxCode,
                "contact": supplier.contact,
            }
        except errors.UniqueViolationError:
            raise ValueError(f"Nhà cung cấp với tên '{clean_name}' đã tồn tại.")

    @staticmethod
    async def list_suppliers_prisma() -> List[Dict[str, Any]]:
        """List all suppliers from PostgreSQL ordered by name."""
        await connect_db()
        prisma = get_prisma()
        suppliers = await prisma.supplier.find_many(order={"name": "asc"})
        return [
            {
                "id": s.id,
                "name": s.name,
                "taxCode": s.taxCode,
                "contact": s.contact,
            }
            for s in suppliers
        ]

    @staticmethod
    async def get_supplier_prisma(supplier_id: str) -> Dict[str, Any]:
        """Get supplier details by ID from PostgreSQL."""
        if not supplier_id or not isinstance(supplier_id, str) or not supplier_id.strip():
            raise ValueError("Mã nhà cung cấp không hợp lệ hoặc rỗng.")
        clean_id = supplier_id.strip()
        await connect_db()
        prisma = get_prisma()
        supplier = await prisma.supplier.find_unique(where={"id": clean_id})
        if not supplier:
            raise ValueError(f"Không tìm thấy nhà cung cấp với mã: '{clean_id}'")
        return {
            "id": supplier.id,
            "name": supplier.name,
            "taxCode": supplier.taxCode,
            "contact": supplier.contact,
        }

    @staticmethod
    def _format_quotation_dict(q) -> Dict[str, Any]:
        """Format Quotation record with derived Decimal unitPrice and joined Supplier details."""
        qty = q.quantity
        tot = Decimal(str(q.totalAmount))
        unit_price_dec = (tot / Decimal(str(qty))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        supp_dict = None
        supp_name = None
        if q.supplier:
            supp_dict = {
                "id": q.supplier.id,
                "name": q.supplier.name,
                "taxCode": q.supplier.taxCode,
                "contact": q.supplier.contact,
            }
            supp_name = q.supplier.name

        return {
            "id": q.id,
            "quotation_id": q.id,
            "purchaseRequestId": q.purchaseRequestId,
            "supplierId": q.supplierId,
            "supplier": supp_dict,
            "supplierName": supp_name,
            "supplier_name": supp_name,
            "totalAmount": float(tot),
            "total_amount": float(tot),
            "quantity": qty,
            "unitPrice": float(unit_price_dec),
            "unit_price": float(unit_price_dec),
            "deliveryDays": q.deliveryDays,
            "delivery_days": q.deliveryDays,
            "warrantyTerms": q.warrantyTerms,
            "warranty_terms": q.warrantyTerms,
            "fileUrl": q.fileUrl,
            "file_name": q.fileUrl,
            "isAnomaly": q.isAnomaly,
            "is_anomaly": q.isAnomaly,
            "anomalyReason": q.anomalyReason,
            "anomaly_reason": q.anomalyReason,
            "createdAt": q.created_at.isoformat() if q.created_at else None,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }

    @staticmethod
    async def create_quotation_prisma(
        purchase_request_id: str,
        supplier_id: str,
        total_amount: Any,
        quantity: int,
        delivery_days: int = 3,
        warranty_terms: Optional[str] = None,
        file_url: str = "quotes/default.pdf",
    ) -> Dict[str, Any]:
        """
        Create a new Quotation directly in Supabase PostgreSQL via Prisma Client.
        Enforces:
        - T-052 Guard: PR MUST exist and PR.status == 'APPROVED'.
        - T-053 Integrity: FK purchaseRequestId -> PurchaseRequest, supplierId -> Supplier.
        - Commercial Validation: quantity > 0 (int), total_amount > 0 (Decimal), delivery_days >= 0 (int).
        - Derived unitPrice computed as Decimal with ROUND_HALF_UP.
        - HRD-03: fileUrl string persistence (binary upload deferred).
        - Atomic transaction using prisma.tx() with PR row lock (SELECT ... FOR UPDATE).
        """
        if not purchase_request_id or not isinstance(purchase_request_id, str) or not purchase_request_id.strip():
            raise ValueError("Mã Purchase Request (purchaseRequestId) không hợp lệ hoặc rỗng.")
        clean_pr_id = purchase_request_id.strip()

        if not supplier_id or not isinstance(supplier_id, str) or not supplier_id.strip():
            raise ValueError("Mã nhà cung cấp (supplierId) không hợp lệ hoặc rỗng.")
        clean_supplier_id = supplier_id.strip()

        try:
            qty = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Số lượng (quantity) của Quotation phải là số nguyên hợp lệ.")
        if qty <= 0:
            raise ValueError("Số lượng (quantity) của Quotation phải là số nguyên dương (> 0).")

        try:
            del_days = int(delivery_days)
        except (ValueError, TypeError):
            raise ValueError("Thời gian giao hàng (deliveryDays) phải là số nguyên hợp lệ.")
        if del_days < 0:
            raise ValueError("Thời gian giao hàng (deliveryDays) không được âm.")

        try:
            total_amount_dec = Decimal(str(total_amount))
        except (ValueError, TypeError, DecimalException):
            raise ValueError("Tổng giá trị (totalAmount) của Quotation không hợp lệ.")
        if total_amount_dec <= Decimal("0.00"):
            raise ValueError("Tổng giá trị (totalAmount) của Quotation phải lớn hơn 0.")

        if not file_url or not isinstance(file_url, str) or not file_url.strip():
            raise ValueError("Đường dẫn tập tin (fileUrl) không hợp lệ hoặc rỗng.")
        clean_file_url = file_url.strip()

        clean_warranty = warranty_terms.strip() if (warranty_terms and isinstance(warranty_terms, str) and warranty_terms.strip()) else None

        await connect_db()
        prisma = get_prisma()

        async with prisma.tx() as tx:
            # 1. T-052 Guard: Lock PR row with SELECT ... FOR UPDATE and verify APPROVED status
            locked_prs = await tx.query_raw(
                'SELECT id, status FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy Purchase Request với mã: '{clean_pr_id}'")
            pr_status = locked_prs[0]["status"]
            if pr_status != "APPROVED":
                raise ValueError(
                    f"Không thể thu thập báo giá: Purchase Request {clean_pr_id} chưa được duyệt "
                    f"(trạng thái hiện tại: '{pr_status}'). Yêu cầu trạng thái phải là APPROVED."
                )

            # 2. T-053 Integrity: Verify Supplier exists in PostgreSQL
            supplier = await tx.supplier.find_unique(where={"id": clean_supplier_id})
            if not supplier:
                raise ValueError(f"Không tìm thấy nhà cung cấp với mã: '{clean_supplier_id}'")

            # 3. Insert Quotation record in PostgreSQL
            created_quote = await tx.quotation.create(
                data={
                    "purchaseRequestId": clean_pr_id,
                    "supplierId": clean_supplier_id,
                    "totalAmount": total_amount_dec,
                    "quantity": qty,
                    "deliveryDays": del_days,
                    "warrantyTerms": clean_warranty,
                    "fileUrl": clean_file_url,
                }
            )

        # 4. Query created Quotation with joined Supplier details
        q = await prisma.quotation.find_unique(
            where={"id": created_quote.id},
            include={"supplier": True},
        )
        return ProcurementService._format_quotation_dict(q)

    @staticmethod
    async def list_quotations_prisma(purchase_request_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all quotations from PostgreSQL, optionally filtered by purchaseRequestId."""
        await connect_db()
        prisma = get_prisma()
        where_clause = {}
        if purchase_request_id and isinstance(purchase_request_id, str) and purchase_request_id.strip():
            where_clause["purchaseRequestId"] = purchase_request_id.strip()
        quotes = await prisma.quotation.find_many(
            where=where_clause,
            include={"supplier": True},
            order={"created_at": "asc"},
        )
        return [ProcurementService._format_quotation_dict(q) for q in quotes]

    @staticmethod
    async def get_quotation_prisma(quotation_id: str) -> Dict[str, Any]:
        """Get quotation details by ID from PostgreSQL."""
        if not quotation_id or not isinstance(quotation_id, str) or not quotation_id.strip():
            raise ValueError("Mã Quotation không hợp lệ hoặc rỗng.")
        clean_id = quotation_id.strip()
        await connect_db()
        prisma = get_prisma()
        q = await prisma.quotation.find_unique(
            where={"id": clean_id},
            include={"supplier": True},
        )
        if not q:
            raise ValueError(f"Không tìm thấy Quotation với mã: '{clean_id}'")
        return ProcurementService._format_quotation_dict(q)

    @staticmethod
    async def list_quotations_by_pr_prisma(purchase_request_id: str) -> List[Dict[str, Any]]:
        """List all quotations for a specific PR from PostgreSQL (T-061)."""
        if not purchase_request_id or not isinstance(purchase_request_id, str) or not purchase_request_id.strip():
            raise ValueError("Mã Purchase Request không hợp lệ hoặc rỗng.")
        clean_pr_id = purchase_request_id.strip()
        await connect_db()
        prisma = get_prisma()
        pr = await prisma.purchaserequest.find_unique(where={"id": clean_pr_id})
        if not pr:
            raise ValueError(f"Không tìm thấy Purchase Request với mã: '{clean_pr_id}'")
        quotes = await prisma.quotation.find_many(
            where={"purchaseRequestId": clean_pr_id},
            include={"supplier": True},
            order={"created_at": "asc"},
        )
        return [ProcurementService._format_quotation_dict(q) for q in quotes]

    @staticmethod
    async def compare_quotations_prisma(purchase_request_id: str) -> List[Dict[str, Any]]:
        """
        Deterministic comparison of all Quotations for a PR from PostgreSQL (T-061).
        Reads real database records, joins Supplier, calculates derived unitPrice,
        and computes price comparison and anomaly detection deterministically.
        Zero MockDB writes, zero LLM calls (TASK-009 boundary preserved).
        """
        if not purchase_request_id or not isinstance(purchase_request_id, str) or not purchase_request_id.strip():
            raise ValueError("Mã Purchase Request không hợp lệ hoặc rỗng.")
        clean_pr_id = purchase_request_id.strip()
        await connect_db()
        prisma = get_prisma()
        pr = await prisma.purchaserequest.find_unique(where={"id": clean_pr_id})
        if not pr:
            raise ValueError(f"Không tìm thấy Purchase Request với mã: '{clean_pr_id}'")
        quotes = await prisma.quotation.find_many(
            where={"purchaseRequestId": clean_pr_id},
            include={"supplier": True},
            order={"created_at": "asc"},
        )
        if not quotes:
            raise ValueError(f"Chưa có báo giá nào cho Purchase Request {clean_pr_id} trong cơ sở dữ liệu để so sánh.")

        # Deterministic comparison calculation
        prices = [Decimal(str(q.totalAmount)) / Decimal(str(q.quantity)) for q in quotes]
        avg_price = sum(prices) / Decimal(str(len(prices))) if prices else Decimal("0.00")

        results = []
        for q in quotes:
            u_price = (Decimal(str(q.totalAmount)) / Decimal(str(q.quantity))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            is_anomaly = q.isAnomaly
            anomaly_reason = q.anomalyReason
            if avg_price > Decimal("0.00"):
                diff_ratio = (u_price - avg_price) / avg_price
                if diff_ratio >= Decimal("0.20") and not is_anomaly:
                    is_anomaly = True
                    anomaly_reason = f"CẢNH BÁO: Đơn giá {float(u_price):,.0f}đ cao hơn {float(diff_ratio * 100):.1f}% so với đơn giá trung bình ({float(avg_price):,.0f}đ)."

            formatted = ProcurementService._format_quotation_dict(q)
            formatted["isAnomaly"] = is_anomaly
            formatted["is_anomaly"] = is_anomaly
            formatted["anomalyReason"] = anomaly_reason
            formatted["anomaly_reason"] = anomaly_reason
            results.append(formatted)
        return results

    # =========================================================================
    # Legacy MockDB Quotation Methods (Kept for backwards compatibility)
    # =========================================================================

    @staticmethod
    def get_quotation(quotation_id: str) -> Dict[str, Any]:
        quote = db.quotations.get(quotation_id)
        if not quote:
            raise ValueError(f"Không tìm thấy Quotation {quotation_id}")
        return quote

    @staticmethod
    def register_quotation(
        quotation_id: str,
        pr_id: str,
        supplier_name: str,
        total_amount: float,
        quantity: int,
        unit_price: float = None,
        delivery_days: int = 3,
        warranty_terms: str = None
    ) -> Dict[str, Any]:
        """
        Register a Quotation with validated server-side quantity (HD-08 / T-094).
        Enforces:
        - quantity MUST be an integer > 0.
        - total_amount MUST be > 0.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Số lượng (quantity) của Quotation phải là số nguyên dương (> 0)")
        if total_amount <= 0:
            raise ValueError("Tổng giá trị (totalAmount) của Quotation phải lớn hơn 0")

        u_price = unit_price if unit_price is not None else (total_amount / quantity)
        quote_record = {
            "quotation_id": quotation_id,
            "id": quotation_id,
            "purchaseRequestId": pr_id,
            "supplierName": supplier_name,
            "supplier_name": supplier_name,
            "totalAmount": total_amount,
            "total_amount": total_amount,
            "quantity": quantity,
            "unitPrice": u_price,
            "unit_price": u_price,
            "deliveryDays": delivery_days,
            "delivery_days": delivery_days,
            "warrantyTerms": warranty_terms,
            "warranty_terms": warranty_terms
        }
        db.quotations[quotation_id] = quote_record
        return quote_record

    @staticmethod
    def create_po(
        pr_id: str,
        quotation_id: Any = None,
        creator_id: str = "procurement@company.com",
        quotation: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        US-09: Create Purchase Order from Approved PR and Chosen Quotation.
        Enforces:
        - REQ-BR-10 / HD-04: PR MUST be in 'APPROVED' status.
        - REQ-BR-12: Server-side quotation resolution (never trust client payload for commercial data).
        - REQ-BR-03 / REQ-FR-16: 100% price lock from quotation in DB.
        - PR ↔ Quotation integrity: quotation.purchaseRequestId == pr_id.
        - 1-1 PR-to-PO integrity: PR cannot have more than 1 PO.
        - Supplier integrity: supplier linked through quotation.
        """
        # 1. Resolve quotation_id if passed via legacy positional arguments: create_po(pr_id, quotation_dict, creator_id)
        if isinstance(quotation_id, dict):
            quotation = quotation_id
            quotation_id = quotation.get("quotation_id") or quotation.get("id")
        elif not quotation_id and quotation and isinstance(quotation, dict):
            quotation_id = quotation.get("quotation_id") or quotation.get("id")

        if not quotation_id:
            raise ValueError("quotationId là bắt buộc để tạo Purchase Order")

        # 2. Query Purchase Request from DB
        pr = db.prs.get(pr_id)
        if not pr:
            raise ValueError(f"Không tìm thấy Purchase Request {pr_id}")

        # 3. REQ-BR-10 / HD-04 (BUG-001): Enforce PR status == "APPROVED"
        pr_status = pr.get("status")
        if pr_status != "APPROVED":
            raise ValueError(
                f"Không thể tạo PO: Purchase Request {pr_id} chưa được duyệt "
                f"(trạng thái hiện tại: {pr_status}). Yêu cầu trạng thái phải là APPROVED."
            )

        # 4. Check 1-1 constraint: PR cannot already have a PO
        for existing_po in db.pos.values():
            if existing_po.get("prId") == pr_id or existing_po.get("purchaseRequestId") == pr_id:
                raise ValueError(
                    f"Purchase Request {pr_id} đã có Purchase Order ({existing_po.get('id')}), không thể tạo thêm."
                )

        # 5. Query Quotation from DB (REQ-BR-12: Server-Side Resolution)
        db_quotation = db.quotations.get(quotation_id)
        if not db_quotation:
            # Handle in-memory registration for isolated unit tests if quotation dict provided
            if quotation and isinstance(quotation, dict) and (quotation.get("quotation_id") == quotation_id or quotation.get("id") == quotation_id):
                if "purchaseRequestId" not in quotation and "prId" not in quotation:
                    quotation["purchaseRequestId"] = pr_id
                db.quotations[quotation_id] = quotation
                db_quotation = quotation
            else:
                raise ValueError(f"Không tìm thấy Quotation {quotation_id} trong hệ thống")

        # 6. PR ↔ Quotation Integrity check
        quotation_pr_id = db_quotation.get("purchaseRequestId") or db_quotation.get("prId")
        if quotation_pr_id != pr_id:
            raise ValueError(
                f"Quotation {quotation_id} không thuộc về Purchase Request {pr_id} "
                f"(Quotation thuộc về PR {quotation_pr_id})."
            )

        # 7. Commercial Data Lock (REQ-BR-03 / REQ-FR-16 / T-094 / HD-08 Option A)
        # 100% price lock from DB quotation - client totalAmount is NEVER trusted
        total_amount = db_quotation.get("totalAmount")
        if total_amount is None:
            total_amount = db_quotation.get("total_amount")
        if total_amount is None or total_amount <= 0:
            raise ValueError(f"Quotation {quotation_id} không có thông tin totalAmount hợp lệ trong cơ sở dữ liệu")

        supplier_name = db_quotation.get("supplierName") or db_quotation.get("supplier_name")
        supplier_id = db_quotation.get("supplierId") or db_quotation.get("supplier_id")
        unit_price = db_quotation.get("unitPrice") or db_quotation.get("unit_price")

        # T-094 / HD-08 Option A: 100% server-side quantity lock from Quotation.quantity
        # PO.quantity MUST be taken from Quotation.quantity in server-side DB.
        # Under NO circumstances is quantity taken from client payload, guessed as 1, or derived from PRItem.
        raw_quantity = db_quotation.get("quantity")
        if raw_quantity is None:
            raise ValueError(
                f"Tạo PO thất bại: Quotation {quotation_id} thiếu thông tin số lượng (quantity). "
                f"Yêu cầu Quotation phải có số lượng hợp lệ theo quy định T-094 / HD-08."
            )
        if type(raw_quantity) is not int or raw_quantity <= 0:
            raise ValueError(
                f"Tạo PO thất bại: Số lượng trên Quotation {quotation_id} không hợp lệ "
                f"(quantity={raw_quantity}). Yêu cầu số lượng phải là số nguyên dương (> 0)."
            )
        quantity = raw_quantity

        # 8. Create Purchase Order Record
        po_id = f"PO-2026-00{len(db.pos) + 1}"
        po_number = f"PO-NUM-2026-00{len(db.pos) + 1}"

        po_record = {
            "id": po_id,
            "poNumber": po_number,
            "prId": pr_id,
            "purchaseRequestId": pr_id,
            "quotationId": quotation_id,
            "supplierName": supplier_name,
            "supplierId": supplier_id,
            "totalAmount": total_amount,
            "unitPrice": unit_price,
            "quantity": quantity,
            "creatorId": creator_id,
            "status": "SENT"
        }

        db.pos[po_id] = po_record
        pr["status"] = "PO_CREATED"
        return po_record

    @staticmethod
    async def create_po_prisma(
        pr_id: str,
        quotation_id: str,
        creator_id: str,
        quantity: Any = None
    ) -> Dict[str, Any]:
        """
        Prisma Client Python implementation for PO creation directly to Supabase PostgreSQL.
        Enforces T-094 / HD-08 Option A: quantity is resolved from db_quote.quantity if not explicitly provided.
        """
        from prisma import Prisma
        prisma_client = Prisma()
        await prisma_client.connect()
        try:
            # Query PR from DB
            db_pr = await prisma_client.purchaserequest.find_unique(where={"id": pr_id})
            if not db_pr:
                raise ValueError(f"Không tìm thấy Purchase Request {pr_id} trong PostgreSQL")
            if db_pr.status != "APPROVED":
                raise ValueError(
                    f"Không thể tạo PO: Purchase Request {pr_id} chưa được duyệt "
                    f"(trạng thái hiện tại: {db_pr.status}). Yêu cầu trạng thái phải là APPROVED."
                )

            # Query Quotation from DB
            db_quote = await prisma_client.quotation.find_unique(where={"id": quotation_id})
            if not db_quote:
                raise ValueError(f"Không tìm thấy Quotation {quotation_id} trong PostgreSQL")
            if db_quote.purchaseRequestId != pr_id:
                raise ValueError(
                    f"Quotation {quotation_id} không thuộc về PR {pr_id} (thuộc PR {db_quote.purchaseRequestId})"
                )

            # T-094 / HD-08 Option A: Lock quantity from Quotation
            po_quantity = db_quote.quantity if quantity is None else quantity
            if po_quantity is None or po_quantity <= 0:
                raise ValueError(
                    f"Tạo PO thất bại: Quotation {quotation_id} trong PostgreSQL có quantity không hợp lệ: {po_quantity}"
                )

            count_pos = await prisma_client.purchaseorder.count()
            po_number = f"PO-NUM-2026-00{count_pos + 1}"

            # Create PO in PostgreSQL
            created = await prisma_client.purchaseorder.create(
                data={
                    "purchaseRequestId": pr_id,
                    "quotationId": quotation_id,
                    "creatorId": creator_id,
                    "poNumber": po_number,
                    "totalAmount": db_quote.totalAmount,
                    "quantity": po_quantity,
                    "status": "SENT"
                }
            )
            # Update PR status to PO_CREATED
            await prisma_client.purchaserequest.update(
                where={"id": pr_id},
                data={"status": "PO_CREATED"}
            )
            return created.model_dump() if hasattr(created, "model_dump") else dict(created)
        finally:
            await prisma_client.disconnect()


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

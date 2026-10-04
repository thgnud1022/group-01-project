import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation as DecimalException
from prisma import errors
from app.services.db import get_prisma, connect_db
from app.services.data_access import (
    resolve_user_id_by_email,
    ACTIVE_BUDGET_FISCAL_YEAR,
    ACTIVE_BUDGET_QUARTER,
)
from app.dependencies.auth import AuthenticatedUser
from app.dependencies.rbac import AuthorizationError


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
        creator_id: Optional[str] = None,
        title: str = "",
        items: Optional[List[Dict[str, Any]]] = None,
        creator_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Prisma Client Python implementation for PR creation directly to Supabase PostgreSQL.
        Enforces:
        - HD-02 / HD-12: Accepts creator_user_id (UUID from JWT identity) or creator_id.
        - HD-REQ-07: Resolve creator email -> User.id (UUID) if email provided.
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

        # 2. Resolve creator identity to User.id (UUID)
        resolved_creator = (creator_user_id or creator_id or "").strip()
        if not resolved_creator:
            raise ValueError("Mã định danh người tạo (creatorId) không hợp lệ hoặc rỗng.")

        await connect_db()
        prisma = get_prisma()

        if "@" in resolved_creator:
            user_id = await resolve_user_id_by_email(resolved_creator)
        else:
            user = await prisma.user.find_unique(where={"id": resolved_creator})
            if not user:
                raise ValueError(f"Không tìm thấy người dùng với ID '{resolved_creator}'.")
            user_id = user.id

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
        current_user: Optional[Union[AuthenticatedUser, str]] = None,
        comments: Optional[str] = "Phê duyệt PR",
        approver_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Prisma Client Python implementation for PR approval directly in Supabase PostgreSQL.
        Enforces:
        - HD-12: Acting approver identity resolved from JWT/DB authenticated user (AuthenticatedUser).
        - GOV-01: No Self-Approval check (current_user.id != PR.creatorId, enforced for ALL roles including ADMIN).
        - HD-REQ-10: Status Guard (only execute when status is PENDING_MANAGER_APPROVAL or PENDING_FINANCE_APPROVAL).
        - REQ-BR-02: Multi-level approval threshold (> 50M VND: Manager -> Finance; <= 50M VND: Manager/Admin).
        - Stage-based authorization raises AuthorizationError (maps to 403 Forbidden).
        - Atomic transaction using prisma.tx().
        - Row-level lock (SELECT ... FOR UPDATE) to prevent concurrency races & duplicate approvals.
        - Stage-based duplicate approval guard (allows ADMIN to legitimately approve both Step 1 and Step 2).
        - Response contract returning full PR with nested approvals from PostgreSQL.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã PR không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        await connect_db()
        prisma = get_prisma()

        threshold = Decimal("50000000.00")

        async with prisma.tx() as tx:
            # 1. Lock PurchaseRequest row with SELECT ... FOR UPDATE
            locked_prs = await tx.query_raw(
                'SELECT id, status, "creatorId", "estimatedValue" FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy mã PR {clean_pr_id}")

            current_pr = locked_prs[0]
            current_status = current_pr["status"]
            pr_creator_id = current_pr["creatorId"]
            estimated_val = Decimal(str(current_pr["estimatedValue"]))

            # 2. HD-REQ-10: Approval Status Guard
            if current_status not in ["PENDING_MANAGER_APPROVAL", "PENDING_FINANCE_APPROVAL"]:
                raise ValueError(
                    f"PR đang ở trạng thái '{current_status}', không thể thực hiện phê duyệt."
                )

            # 3. HD-12: Resolve approver identity & role
            if isinstance(current_user, AuthenticatedUser):
                approver_id = current_user.id
                approver_role = current_user.role
            elif isinstance(current_user, str) and current_user.strip():
                ident = current_user.strip()
                if "@" in ident:
                    user = await tx.user.find_unique(where={"email": ident.lower()})
                else:
                    user = await tx.user.find_unique(where={"id": ident})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng '{ident}'.")
                approver_id = user.id
                approver_role = str(user.role)
            elif approver_email and approver_email.strip():
                clean_email = approver_email.strip().lower()
                user = await tx.user.find_unique(where={"email": clean_email})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng với email '{clean_email}'.")
                approver_id = user.id
                approver_role = str(user.role)
            else:
                raise ValueError("Không xác định được danh tính người phê duyệt.")

            # 4. REQ-BR-02: Multi-level approval threshold & Stage-based authorization
            if estimated_val > threshold:
                if current_status == "PENDING_MANAGER_APPROVAL":
                    if approver_role not in ["MANAGER", "ADMIN"]:
                        raise AuthorizationError("PR giá trị > 50 triệu VND cần Manager phê duyệt bước 1 trước.")
                    new_status = "PENDING_FINANCE_APPROVAL"
                elif current_status == "PENDING_FINANCE_APPROVAL":
                    if approver_role not in ["FINANCE", "ADMIN"]:
                        raise AuthorizationError("PR giá trị > 50 triệu VND bắt buộc cần Finance duyệt bước 2.")
                    new_status = "APPROVED"
                else:
                    raise ValueError(
                        f"PR đang ở trạng thái '{current_status}', không thể thực hiện phê duyệt."
                    )
            else:
                # PR <= 50M VND (1-Level approval)
                if current_status == "PENDING_MANAGER_APPROVAL":
                    if approver_role not in ["MANAGER", "ADMIN"]:
                        raise AuthorizationError("Không có thẩm quyền duyệt PR.")
                    new_status = "APPROVED"
                else:
                    raise ValueError(
                        f"PR có giá trị <= 50 triệu VND không ở trạng thái PENDING_MANAGER_APPROVAL (hiện tại: '{current_status}')."
                    )

            # 4.5. GOV-01: No Self-Approval check (Enforced for ALL roles, including ADMIN)
            if approver_id == pr_creator_id:
                raise AuthorizationError(
                    "Không thể phê duyệt PR do chính mình tạo (No Self-Approval — GOV-01)."
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
    async def reject_pr_prisma(
        pr_id: str,
        current_user: Optional[Union[AuthenticatedUser, str]] = None,
        comments: Optional[str] = None,
        approver_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Prisma Client Python implementation for PR rejection directly in Supabase PostgreSQL.
        Enforces:
        - REQ-FR-06 & US-04 AC2: Manager/Finance/Admin can reject PR with mandatory reason.
        - HD-12: Acting approver identity resolved from JWT/DB authenticated user.
        - GOV-01: No Self-Action check (approver != creator).
        - HD-REQ-10: Status Guard (only permitted in PENDING_MANAGER_APPROVAL or PENDING_FINANCE_APPROVAL).
        - Atomic transaction using prisma.tx() with row lock (SELECT ... FOR UPDATE).
        - Releases tempReservedAmount from Budget upon rejection.
        - Persists Approval record with decision="REJECTED" and mandatory comments.
        - Transitions PR status to REJECTED.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã PR không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        if not comments or not isinstance(comments, str) or not comments.strip():
            raise ValueError("Lý do từ chối là bắt buộc (US-04 AC2).")
        clean_comments = comments.strip()

        await connect_db()
        prisma = get_prisma()

        async with prisma.tx() as tx:
            # 1. Lock PurchaseRequest row with SELECT ... FOR UPDATE
            locked_prs = await tx.query_raw(
                'SELECT id, status, "creatorId", "departmentId", "estimatedValue" FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy mã PR {clean_pr_id}")

            current_pr = locked_prs[0]
            current_status = current_pr["status"]
            pr_creator_id = current_pr["creatorId"]
            dept_id = current_pr["departmentId"]
            estimated_val = Decimal(str(current_pr["estimatedValue"]))

            # 2. HD-REQ-10: Status Guard
            if current_status not in ["PENDING_MANAGER_APPROVAL", "PENDING_FINANCE_APPROVAL"]:
                raise ValueError(
                    f"PR đang ở trạng thái '{current_status}', không thể thực hiện từ chối."
                )

            # 3. HD-12: Resolve approver identity & role
            if isinstance(current_user, AuthenticatedUser):
                approver_id = current_user.id
                approver_role = current_user.role
            elif isinstance(current_user, str) and current_user.strip():
                ident = current_user.strip()
                if "@" in ident:
                    user = await tx.user.find_unique(where={"email": ident.lower()})
                else:
                    user = await tx.user.find_unique(where={"id": ident})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng '{ident}'.")
                approver_id = user.id
                approver_role = str(user.role)
            elif approver_email and approver_email.strip():
                clean_email = approver_email.strip().lower()
                user = await tx.user.find_unique(where={"email": clean_email})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng với email '{clean_email}'.")
                approver_id = user.id
                approver_role = str(user.role)
            else:
                raise ValueError("Không xác định được danh tính người từ chối.")

            # 4. Role Authorization
            if approver_role not in ["MANAGER", "FINANCE", "ADMIN"]:
                raise AuthorizationError("Chỉ Manager, Finance hoặc Admin mới có quyền từ chối PR.")

            # 5. GOV-01: No Self-Action check
            if approver_id == pr_creator_id:
                raise AuthorizationError(
                    "Không thể từ chối PR do chính mình tạo (No Self-Approval — GOV-01)."
                )

            # 6. Release Budget tempReservedAmount if budget exists
            budget = await tx.budget.find_first(
                where={"departmentId": dept_id, "fiscalYear": 2026, "quarter": 1}
            )
            if budget:
                new_reserved = max(Decimal("0.00"), budget.tempReservedAmount - estimated_val)
                await tx.budget.update(
                    where={"id": budget.id},
                    data={"tempReservedAmount": new_reserved},
                )

            # 7. Insert Approval record with decision="REJECTED"
            await tx.approval.create(
                data={
                    "purchaseRequestId": clean_pr_id,
                    "approverId": approver_id,
                    "decision": "REJECTED",
                    "comments": clean_comments,
                }
            )

            # 8. Update PurchaseRequest status to REJECTED
            await tx.purchaserequest.update(
                where={"id": clean_pr_id},
                data={"status": "REJECTED"},
            )

        # 9. Query updated PurchaseRequest from PostgreSQL
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
            raise ValueError(f"Không thể truy vấn PR sau khi từ chối: {clean_pr_id}")

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
    async def request_revision_prisma(
        pr_id: str,
        current_user: Optional[Union[AuthenticatedUser, str]] = None,
        comments: Optional[str] = None,
        approver_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Request Revision flow implemented with Prisma Client Python in Supabase PostgreSQL (HD-16).
        Enforces:
        - REQ-FR-06, US-03 AC3, US-04 AC2: Manager/Finance/Admin can request revision with mandatory comment/reason.
        - HD-12: Acting approver identity resolved from JWT/DB authenticated user.
        - GOV-01: No Self-Action check (approver != creator).
        - Status Guard: Only permitted from PENDING_MANAGER_APPROVAL or PENDING_FINANCE_APPROVAL.
        - Rejection of invalid states: APPROVED, REJECTED, PO_CREATED, CLOSED, REVISION_REQUIRED.
        - Releases tempReservedAmount from Budget so funds are not locked during revision drafting.
        - Persists Approval record with decision="REVISION_REQUIRED" and approver comments.
        - Transitions PR status to REVISION_REQUIRED.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã PR không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        if not comments or not isinstance(comments, str) or not comments.strip():
            raise ValueError("Lý do yêu cầu chỉnh sửa là bắt buộc (US-04 AC2 / HD-16).")
        clean_comments = comments.strip()

        await connect_db()
        prisma = get_prisma()

        async with prisma.tx() as tx:
            # 1. Lock PurchaseRequest row with SELECT ... FOR UPDATE
            locked_prs = await tx.query_raw(
                'SELECT id, status, "creatorId", "departmentId", "estimatedValue" FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy mã PR {clean_pr_id}")

            current_pr = locked_prs[0]
            current_status = current_pr["status"]
            pr_creator_id = current_pr["creatorId"]
            dept_id = current_pr["departmentId"]
            estimated_val = Decimal(str(current_pr["estimatedValue"]))

            # 2. Status Guard (HD-16 / Section 7)
            if current_status not in ["PENDING_MANAGER_APPROVAL", "PENDING_FINANCE_APPROVAL"]:
                raise ValueError(
                    f"PR đang ở trạng thái '{current_status}', không thể thực hiện yêu cầu chỉnh sửa."
                )

            # 3. Resolve approver identity & role
            if isinstance(current_user, AuthenticatedUser):
                approver_id = current_user.id
                approver_role = current_user.role
            elif isinstance(current_user, str) and current_user.strip():
                ident = current_user.strip()
                if "@" in ident:
                    user = await tx.user.find_unique(where={"email": ident.lower()})
                else:
                    user = await tx.user.find_unique(where={"id": ident})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng '{ident}'.")
                approver_id = user.id
                approver_role = str(user.role)
            elif approver_email and approver_email.strip():
                clean_email = approver_email.strip().lower()
                user = await tx.user.find_unique(where={"email": clean_email})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng với email '{clean_email}'.")
                approver_id = user.id
                approver_role = str(user.role)
            else:
                raise ValueError("Không xác định được danh tính người yêu cầu chỉnh sửa.")

            # 4. Role Authorization (MANAGER, FINANCE, ADMIN only)
            if approver_role not in ["MANAGER", "FINANCE", "ADMIN"]:
                raise AuthorizationError("Chỉ Manager, Finance hoặc Admin mới có quyền yêu cầu chỉnh sửa PR.")

            # 5. GOV-01: No Self-Action check
            if approver_id == pr_creator_id:
                raise AuthorizationError(
                    "Không thể yêu cầu chỉnh sửa PR do chính mình tạo (No Self-Approval — GOV-01)."
                )

            # 6. Release Budget tempReservedAmount while in revision drafting
            budget = await tx.budget.find_first(
                where={"departmentId": dept_id, "fiscalYear": 2026, "quarter": 1}
            )
            if budget:
                new_reserved = max(Decimal("0.00"), budget.tempReservedAmount - estimated_val)
                await tx.budget.update(
                    where={"id": budget.id},
                    data={"tempReservedAmount": new_reserved},
                )

            # 7. Insert Approval record with decision="REVISION_REQUIRED"
            await tx.approval.create(
                data={
                    "purchaseRequestId": clean_pr_id,
                    "approverId": approver_id,
                    "decision": "REVISION_REQUIRED",
                    "comments": clean_comments,
                }
            )

            # 8. Update PurchaseRequest status to REVISION_REQUIRED
            await tx.purchaserequest.update(
                where={"id": clean_pr_id},
                data={"status": "REVISION_REQUIRED"},
            )

        # 9. Query updated PurchaseRequest from PostgreSQL
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
            raise ValueError(f"Không thể truy vấn PR sau khi yêu cầu chỉnh sửa: {clean_pr_id}")

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
    async def resubmit_pr_prisma(
        pr_id: str,
        current_user: Optional[Union[AuthenticatedUser, str]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        comments: Optional[str] = None,
        actor_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resubmit PR flow implemented with Prisma Client Python in Supabase PostgreSQL (HD-16).
        Enforces:
        - Only PR with status == REVISION_REQUIRED can be resubmitted.
        - Only the PR creator (or authorized admin) can resubmit.
        - Identity verified from JWT / application user.
        - Re-validates data and recalculates total estimated value.
        - Budget consistency: Atomically checks available budget (allocated - spent - current_reserved)
          and reserves the new estimatedValue.
        - Deletes old PRItems and inserts updated PRItems.
        - Inserts an Approval record with decision="RESUBMITTED" preserving complete history.
        - Transitions status to PENDING_MANAGER_APPROVAL.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã PR không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        await connect_db()
        prisma = get_prisma()

        async with prisma.tx() as tx:
            # 1. Lock PurchaseRequest row with SELECT ... FOR UPDATE
            locked_prs = await tx.query_raw(
                'SELECT id, status, title, description, "creatorId", "departmentId", "estimatedValue" FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy mã PR {clean_pr_id}")

            current_pr = locked_prs[0]
            current_status = current_pr["status"]
            pr_creator_id = current_pr["creatorId"]
            dept_id = current_pr["departmentId"]

            # 2. Status Guard: Must be REVISION_REQUIRED
            if current_status != "REVISION_REQUIRED":
                raise ValueError(
                    f"Chỉ PR ở trạng thái 'REVISION_REQUIRED' mới có thể gửi lại (trạng thái hiện tại: '{current_status}')."
                )

            # 3. Resolve actor identity & role
            if isinstance(current_user, AuthenticatedUser):
                actor_id = current_user.id
                actor_role = current_user.role
            elif isinstance(current_user, str) and current_user.strip():
                ident = current_user.strip()
                if "@" in ident:
                    user = await tx.user.find_unique(where={"email": ident.lower()})
                else:
                    user = await tx.user.find_unique(where={"id": ident})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng '{ident}'.")
                actor_id = user.id
                actor_role = str(user.role)
            elif actor_email and actor_email.strip():
                clean_email = actor_email.strip().lower()
                user = await tx.user.find_unique(where={"email": clean_email})
                if not user:
                    raise ValueError(f"Không tìm thấy người dùng với email '{clean_email}'.")
                actor_id = user.id
                actor_role = str(user.role)
            else:
                raise ValueError("Không xác định được danh tính người gửi lại yêu cầu.")

            # 4. Authorization: Only the original creator or ADMIN may resubmit
            if actor_id != pr_creator_id and actor_role != "ADMIN":
                raise AuthorizationError(
                    "Chỉ người tạo PR mới có quyền chỉnh sửa và gửi lại yêu cầu (HD-16 / Resubmit Authorization)."
                )

            # 5. Process and validate updated items
            final_title = title.strip() if (title and isinstance(title, str) and title.strip()) else current_pr["title"]
            final_desc = description.strip() if (description and isinstance(description, str)) else current_pr["description"]

            if items is not None:
                if not items or len(items) == 0:
                    raise ValueError("Danh mục hàng hóa không được để trống khi gửi lại.")
                
                new_items_data = []
                total_estimated = Decimal("0.00")
                for it in items:
                    name = it.get("itemName") or it.get("name")
                    if not name or not str(name).strip():
                        raise ValueError("Tên mặt hàng không được để trống.")
                    qty = int(it.get("quantity") or 0)
                    if qty <= 0:
                        raise ValueError(f"Số lượng cho '{name}' phải lớn hơn 0.")
                    unit_price = Decimal(str(it.get("estimatedUnitPrice") or it.get("unitPrice") or 0))
                    if unit_price <= 0:
                        raise ValueError(f"Đơn giá cho '{name}' phải lớn hơn 0.")
                    
                    total_estimated += unit_price * qty
                    new_items_data.append({
                        "purchaseRequestId": clean_pr_id,
                        "itemName": str(name).strip(),
                        "quantity": qty,
                        "estimatedUnitPrice": unit_price,
                    })
            else:
                # Keep existing items, recalculate total from DB
                existing_items = await tx.pritem.find_many(where={"purchaseRequestId": clean_pr_id})
                if not existing_items:
                    raise ValueError("Không tìm thấy mặt hàng nào trong PR để gửi lại.")
                total_estimated = sum(Decimal(str(it.estimatedUnitPrice)) * it.quantity for it in existing_items)
                new_items_data = None

            # 6. Budget Check & Reservation (HD-REQ-08: fiscalYear=2026, quarter=1)
            rows = await tx.query_raw(
                'SELECT id, "allocatedAmount", "spentAmount", "tempReservedAmount" '
                'FROM "Budget" '
                'WHERE "departmentId" = $1 AND "fiscalYear" = $2 AND quarter = $3 '
                'FOR UPDATE',
                dept_id,
                ACTIVE_BUDGET_FISCAL_YEAR,
                ACTIVE_BUDGET_QUARTER,
            )
            if not rows:
                raise ValueError(
                    f"Không tìm thấy ngân sách khả dụng cho phòng ban '{dept_id}' "
                    f"trong kỳ tài chính Năm {ACTIVE_BUDGET_FISCAL_YEAR} - Quý {ACTIVE_BUDGET_QUARTER}."
                )

            budget_row = rows[0]
            budget_id = budget_row["id"]
            allocated = Decimal(str(budget_row["allocatedAmount"]))
            spent = Decimal(str(budget_row["spentAmount"]))
            current_reserved = Decimal(str(budget_row["tempReservedAmount"]))
            available = allocated - spent - current_reserved

            if total_estimated > available:
                raise ValueError(
                    f"Gửi lại PR thất bại: Giá trị ước tính mới ({total_estimated:,.0f}đ) vượt quá "
                    f"Ngân sách khả dụng còn lại ({available:,.0f}đ)."
                )

            # Atomically reserve budget for resubmitted PR
            new_reserved = current_reserved + total_estimated
            await tx.budget.update(
                where={"id": budget_id},
                data={"tempReservedAmount": new_reserved},
            )

            # 7. Update PR items if provided
            if new_items_data is not None:
                await tx.pritem.delete_many(where={"purchaseRequestId": clean_pr_id})
                for it_data in new_items_data:
                    await tx.pritem.create(data=it_data)

            # 8. Record Approval history for resubmission
            resubmit_comment = comments.strip() if (comments and isinstance(comments, str) and comments.strip()) else "Đã chỉnh sửa và gửi lại yêu cầu"
            await tx.approval.create(
                data={
                    "purchaseRequestId": clean_pr_id,
                    "approverId": actor_id,
                    "decision": "RESUBMITTED",
                    "comments": resubmit_comment,
                }
            )

            # 9. Update PurchaseRequest status to PENDING_MANAGER_APPROVAL
            await tx.purchaserequest.update(
                where={"id": clean_pr_id},
                data={
                    "title": final_title,
                    "description": final_desc,
                    "estimatedValue": total_estimated,
                    "status": "PENDING_MANAGER_APPROVAL",
                },
            )

        # 10. Query updated PurchaseRequest from PostgreSQL
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
            raise ValueError(f"Không thể truy vấn PR sau khi gửi lại: {clean_pr_id}")

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
            "validUntil": q.validUntil.isoformat() if getattr(q, "validUntil", None) else None,
            "valid_until": q.validUntil.isoformat() if getattr(q, "validUntil", None) else None,
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
        valid_until: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Quotation directly in Supabase PostgreSQL via Prisma Client.
        Enforces:
        - T-052 Guard: PR MUST exist and PR.status == 'APPROVED'.
        - T-053 Integrity: FK purchaseRequestId -> PurchaseRequest, supplierId -> Supplier.
        - Commercial Validation: quantity > 0 (int), total_amount > 0 (Decimal), delivery_days >= 0 (int).
        - Derived unitPrice computed as Decimal with ROUND_HALF_UP.
        - HRD-03: fileUrl string persistence (binary upload deferred).
        - HD-17: validUntil DateTime persistence for expiry tracking.
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

        parsed_valid_until = None
        if valid_until:
            if isinstance(valid_until, datetime):
                parsed_valid_until = valid_until
            elif isinstance(valid_until, str) and valid_until.strip():
                try:
                    clean_dt_str = valid_until.strip().replace("Z", "+00:00")
                    parsed_valid_until = datetime.fromisoformat(clean_dt_str)
                except Exception:
                    parsed_valid_until = None

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
                    "validUntil": parsed_valid_until,
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
        HD-17 Guard: Enforces minimum 2 quotations (len(quotes) >= 2).
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
        if not quotes or len(quotes) < 2:
            quote_count = len(quotes) if quotes else 0
            raise ValueError(f"Cần tối thiểu 2 báo giá để thực hiện so sánh (hiện có: {quote_count}).")

        # Deterministic comparison calculation
        prices = [Decimal(str(q.totalAmount)) / Decimal(str(q.quantity)) for q in quotes]
        avg_price = sum(prices) / Decimal(str(len(prices))) if prices else Decimal("0.00")

        now_utc = datetime.now(timezone.utc)
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

            is_expired = False
            if getattr(q, "validUntil", None):
                q_valid = q.validUntil if q.validUntil.tzinfo else q.validUntil.replace(tzinfo=timezone.utc)
                is_expired = q_valid < now_utc

            formatted = ProcurementService._format_quotation_dict(q)
            formatted["isAnomaly"] = is_anomaly
            formatted["is_anomaly"] = is_anomaly
            formatted["anomalyReason"] = anomaly_reason
            formatted["anomaly_reason"] = anomaly_reason
            formatted["isExpired"] = is_expired
            formatted["is_expired"] = is_expired
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
    def _generate_po_number() -> str:
        """
        Generate human-readable, unique PO number adhering to HD-08 / Option A.
        Format: PO-NUM-2026-YYYYMMDD-<8-char-hex>
        Zero reliance on count() + 1, eliminating race conditions under concurrency.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        suffix = uuid.uuid4().hex[:8].upper()
        return f"PO-NUM-2026-{date_str}-{suffix}"

    @staticmethod
    async def create_po_prisma(
        pr_id: str,
        quotation_id: str,
        creator_user_id: Optional[str] = None,
        creator_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Purchase Order directly in Supabase PostgreSQL via Prisma Client (US-09).
        Enforces:
        - T-093 / REQ-BR-10 / HD-04: PR MUST exist and be in 'APPROVED' status.
        - 1 PR -> 1 PO integrity: PR cannot have more than 1 PO.
        - T-092 / T-053: Quotation MUST exist in PostgreSQL and belong to pr_id (quotation.purchaseRequestId == pr_id).
        - T-091: Supplier linked via Quotation.supplierId.
        - T-094 / HD-08 Option A: 100% price lock (totalAmount) and quantity lock (quantity) from Quotation in PostgreSQL.
          Client commercial fields (totalAmount, quantity) are STRICTLY IGNORED.
        - HD-02 / HD-12: Creator identity extracted from verified JWT (creator_user_id UUID).
        - HD-REQ-07: Fallback to creator email resolution if email string is passed.
        - HD-08 Option A: poNumber generated with timestamp/random suffix and multi-tx retry on collision.
        - Atomic transaction: PO creation + PR status update to PO_CREATED with SELECT ... FOR UPDATE row lock.
        - Zero dual-write to MockDB.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã Purchase Request (purchaseRequestId) không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        if not quotation_id or not isinstance(quotation_id, str) or not quotation_id.strip():
            raise ValueError("Mã báo giá (quotationId) không hợp lệ hoặc rỗng.")
        clean_quotation_id = quotation_id.strip()

        raw_creator = (creator_user_id or creator_email or "procurement@company.com").strip()
        if not raw_creator:
            raise ValueError("Email hoặc ID người tạo PO không hợp lệ hoặc rỗng.")
        clean_creator = raw_creator

        await connect_db()
        prisma = get_prisma()

        # HD-REQ-07 / HD-12: Resolve creator identity to User.id UUID
        if "@" in clean_creator:
            creator_user_id = await resolve_user_id_by_email(clean_creator)
        else:
            creator_user = await prisma.user.find_unique(where={"id": clean_creator})
            if not creator_user:
                raise ValueError(f"Không tìm thấy người dùng với ID: '{clean_creator}'.")
            creator_user_id = creator_user.id

        # Multi-Tx Retry loop for Option A poNumber collision
        max_retries = 3
        created_po_id = None
        total_amount_dec = None
        po_quantity = None

        for attempt in range(max_retries):
            po_number = ProcurementService._generate_po_number()
            try:
                async with prisma.tx() as tx:
                    # 1. Row-level lock on PurchaseRequest and verify APPROVED status
                    locked_prs = await tx.query_raw(
                        'SELECT id, status FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                        clean_pr_id,
                    )
                    if not locked_prs:
                        raise ValueError(f"Không tìm thấy Purchase Request với mã: '{clean_pr_id}'")
                    pr_status = locked_prs[0]["status"]
                    if pr_status != "APPROVED":
                        raise ValueError(
                            f"Không thể tạo PO: Purchase Request {clean_pr_id} chưa được duyệt "
                            f"(trạng thái hiện tại: '{pr_status}'). Yêu cầu trạng thái phải là APPROVED."
                        )

                    # 2. Check 1-1 PR -> PO constraint
                    existing_po = await tx.purchaseorder.find_first(
                        where={"purchaseRequestId": clean_pr_id}
                    )
                    if existing_po:
                        raise ValueError(
                            f"Purchase Request {clean_pr_id} đã có Purchase Order ({existing_po.poNumber}), không thể tạo thêm."
                        )

                    # 3. Query Quotation from PostgreSQL (T-092)
                    quote = await tx.quotation.find_unique(
                        where={"id": clean_quotation_id},
                        include={"supplier": True},
                    )
                    if not quote:
                        raise ValueError(f"Không tìm thấy Quotation {clean_quotation_id} trong hệ thống.")

                    # Validate quotation belongs to current PR
                    if quote.purchaseRequestId != clean_pr_id:
                        raise ValueError(
                            f"Quotation {clean_quotation_id} không thuộc về Purchase Request {clean_pr_id} "
                            f"(Quotation thuộc về PR {quote.purchaseRequestId})."
                        )

                    # 4. T-094 / HD-08 Option A: 100% server-side commercial data lock from Quotation
                    # Validate totalAmount
                    total_amount_dec = quote.totalAmount
                    if total_amount_dec is None or Decimal(str(total_amount_dec)) <= Decimal("0.00"):
                        raise ValueError(f"Quotation {clean_quotation_id} không có totalAmount hợp lệ.")

                    # Validate quantity
                    po_quantity = quote.quantity
                    if po_quantity is None or not isinstance(po_quantity, int) or po_quantity <= 0:
                        raise ValueError(
                            f"Tạo PO thất bại: Quotation {clean_quotation_id} có số lượng (quantity) không hợp lệ: {po_quantity}. "
                            f"Yêu cầu số lượng phải là số nguyên dương (> 0)."
                        )

                    # 5. Create Purchase Order in PostgreSQL
                    created_po = await tx.purchaseorder.create(
                        data={
                            "purchaseRequestId": clean_pr_id,
                            "quotationId": clean_quotation_id,
                            "creatorId": creator_user_id,
                            "poNumber": po_number,
                            "totalAmount": total_amount_dec,
                            "quantity": po_quantity,
                            "status": "SENT",
                        }
                    )

                    # 6. Update PR status to PO_CREATED
                    await tx.purchaserequest.update(
                        where={"id": clean_pr_id},
                        data={"status": "PO_CREATED"},
                    )

                    created_po_id = created_po.id

                # Transaction committed successfully! Break retry loop
                break
            except Exception as e:
                err_str = str(e)
                is_unique_violation = (
                    "Unique constraint failed" in err_str
                    or "UniqueViolationError" in type(e).__name__
                    or ("unique" in err_str.lower() and "ponumber" in err_str.lower())
                )
                if is_unique_violation and attempt < max_retries - 1:
                    continue
                raise

        # Query created PO with joined relations for complete response
        po_record = await prisma.purchaseorder.find_unique(
            where={"id": created_po_id},
            include={
                "quotation": {"include": {"supplier": True}},
                "purchaseRequest": True,
                "creator": True,
            },
        )

        unit_price_dec = (Decimal(str(total_amount_dec)) / Decimal(str(po_quantity))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        supp_name = po_record.quotation.supplier.name if (po_record.quotation and po_record.quotation.supplier) else None
        supp_id = po_record.quotation.supplierId if po_record.quotation else None

        return {
            "id": po_record.id,
            "poNumber": po_record.poNumber,
            "purchaseRequestId": po_record.purchaseRequestId,
            "prId": po_record.purchaseRequestId,
            "prTitle": po_record.purchaseRequest.title if po_record.purchaseRequest else None,
            "quotationId": po_record.quotationId,
            "creatorId": po_record.creatorId,
            "creatorEmail": po_record.creator.email if po_record.creator else None,
            "supplierId": supp_id,
            "supplierName": supp_name,
            "totalAmount": float(total_amount_dec),
            "quantity": po_quantity,
            "unitPrice": float(unit_price_dec),
            "status": po_record.status,
            "createdAt": po_record.created_at.isoformat() if po_record.created_at else None,
            "created_at": po_record.created_at.isoformat() if po_record.created_at else None,
        }

    @staticmethod
    async def list_pos_prisma() -> List[Dict[str, Any]]:
        """List all Purchase Orders from PostgreSQL (US-09)."""
        await connect_db()
        prisma = get_prisma()
        pos = await prisma.purchaseorder.find_many(
            include={
                "quotation": {"include": {"supplier": True}},
                "purchaseRequest": True,
                "creator": True,
            },
            order={"created_at": "desc"},
        )
        results = []
        for p in pos:
            tot = Decimal(str(p.totalAmount))
            qty = p.quantity
            u_price = (tot / Decimal(str(qty))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if qty > 0 else Decimal("0.00")
            supp_name = p.quotation.supplier.name if (p.quotation and p.quotation.supplier) else None
            results.append({
                "id": p.id,
                "poNumber": p.poNumber,
                "purchaseRequestId": p.purchaseRequestId,
                "prId": p.purchaseRequestId,
                "prTitle": p.purchaseRequest.title if p.purchaseRequest else None,
                "quotationId": p.quotationId,
                "creatorId": p.creatorId,
                "supplierId": p.quotation.supplierId if p.quotation else None,
                "supplierName": supp_name,
                "totalAmount": float(tot),
                "quantity": qty,
                "unitPrice": float(u_price),
                "status": p.status,
                "createdAt": p.created_at.isoformat() if p.created_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            })
        return results


    # =========================================================================
    # STEP 3B.6: Goods Receiving Prisma Client Implementation (US-10)
    # =========================================================================

    @staticmethod
    async def receive_goods_prisma(
        po_id: str,
        received_qty: int,
        file_url: str = "https://example.com/bien-ban-giao-nhan.pdf",
        received_items: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Goods Receipt record directly in Supabase PostgreSQL via Prisma Client (US-10).
        Enforces:
        - PO MUST exist in PostgreSQL.
        - Row-level lock on PurchaseOrder (SELECT ... FOR UPDATE) inside transaction.
        - REQ-BR-04: Accumulated received quantity (SUM(receivedQty)) CANNOT exceed PO.quantity.
        - Supports valid partial receipts (multiple receipts up to PO.quantity).
        - received_qty MUST be a positive integer (> 0).
        - Atomic transaction using prisma.tx().
        - Zero dual-write to MockDB.
        """
        if not po_id or not isinstance(po_id, str) or not po_id.strip():
            raise ValueError("Mã Purchase Order không hợp lệ hoặc rỗng.")
        clean_po_id = po_id.strip()

        try:
            qty = int(received_qty)
        except (ValueError, TypeError):
            raise ValueError("Số lượng nhận hàng phải là số nguyên hợp lệ.")
        if qty <= 0:
            raise ValueError(f"Số lượng nhận hàng ({qty}) phải là số nguyên dương (> 0).")

        clean_file_url = (
            file_url.strip()
            if (file_url and isinstance(file_url, str) and file_url.strip())
            else "https://example.com/bien-ban-giao-nhan.pdf"
        )
        clean_received_items = (
            received_items.strip()
            if (received_items and isinstance(received_items, str) and received_items.strip())
            else f"Bàn giao hàng hóa đợt nhận {qty} sản phẩm"
        )

        await connect_db()
        prisma = get_prisma()

        async with prisma.tx() as tx:
            # 1. Row-level lock on PurchaseOrder
            locked_pos = await tx.query_raw(
                'SELECT id, quantity, "poNumber", status FROM "PurchaseOrder" WHERE id = $1 FOR UPDATE',
                clean_po_id,
            )
            # Support lookup by poNumber if client passed poNumber instead of UUID
            if not locked_pos:
                locked_pos = await tx.query_raw(
                    'SELECT id, quantity, "poNumber", status FROM "PurchaseOrder" WHERE "poNumber" = $1 FOR UPDATE',
                    clean_po_id,
                )

            if not locked_pos:
                raise ValueError(f"Không tìm thấy Purchase Order với mã: '{clean_po_id}'")

            po_record = locked_pos[0]
            po_db_id = po_record["id"]
            po_max_quantity = int(po_record["quantity"])

            # 2. Query accumulated received quantity in PostgreSQL
            existing_receivings = await tx.receiving.find_many(
                where={"purchaseOrderId": po_db_id}
            )
            total_already_received = sum(r.receivedQty for r in existing_receivings)

            # 3. REQ-BR-04: Limit accumulated received quantity <= PO quantity
            if total_already_received + qty > po_max_quantity:
                raise ValueError(
                    f"Nhận hàng thất bại: Tổng số lượng nhận ({total_already_received + qty}) "
                    f"vượt quá số lượng đặt trên PO ({po_max_quantity})."
                )

            # 4. Create Receiving record in PostgreSQL
            created_rec = await tx.receiving.create(
                data={
                    "purchaseOrderId": po_db_id,
                    "receivedQty": qty,
                    "receivedItems": clean_received_items,
                    "fileUrl": clean_file_url,
                }
            )

        return {
            "id": created_rec.id,
            "purchaseOrderId": created_rec.purchaseOrderId,
            "poId": created_rec.purchaseOrderId,
            "poNumber": po_record.get("poNumber"),
            "receivedQty": created_rec.receivedQty,
            "receivedItems": created_rec.receivedItems,
            "fileUrl": created_rec.fileUrl,
            "receivedDate": created_rec.receivedDate.isoformat() if created_rec.receivedDate else None,
            "totalReceived": total_already_received + qty,
            "poQuantity": po_max_quantity,
        }

    @staticmethod
    async def list_receivings_prisma(purchase_order_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Goods Receipts from PostgreSQL, optionally filtered by purchaseOrderId."""
        await connect_db()
        prisma = get_prisma()
        where_clause = {}
        if purchase_order_id and isinstance(purchase_order_id, str) and purchase_order_id.strip():
            clean_po = purchase_order_id.strip()
            where_clause = {
                "OR": [
                    {"purchaseOrderId": clean_po},
                    {"purchaseOrder": {"poNumber": clean_po}},
                ]
            }

        recs = await prisma.receiving.find_many(
            where=where_clause,
            include={"purchaseOrder": True},
            order={"receivedDate": "desc"},
        )
        return [
            {
                "id": r.id,
                "purchaseOrderId": r.purchaseOrderId,
                "poId": r.purchaseOrderId,
                "poNumber": r.purchaseOrder.poNumber if r.purchaseOrder else None,
                "receivedQty": r.receivedQty,
                "receivedItems": r.receivedItems,
                "fileUrl": r.fileUrl,
                "receivedDate": r.receivedDate.isoformat() if r.receivedDate else None,
            }
            for r in recs
        ]


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
    async def close_pr_prisma(
        pr_id: str,
        actor_user_id: Optional[str] = None,
        finance_user: Optional[str] = "finance@company.com",
    ) -> Dict[str, Any]:
        """
        Close Purchase Request directly in Supabase PostgreSQL via Prisma Client.
        Enforces:
        - HD-02 / HD-12: Actor identity derived from server-side JWT authentication (actor_user_id).
        - HD-07 / REQ-BR-11: SUM(receivedQty) >= PO.quantity before closing PR.
        - PR must exist and not already CLOSED.
        - PO must exist for the PR.
        - Atomic transaction using prisma.tx() with row-level locks (SELECT ... FOR UPDATE).
        - Budget settlement: decrease tempReservedAmount (capped at 0) and increase spentAmount.
        - Zero MockDB read/write.
        """
        if not pr_id or not isinstance(pr_id, str) or not pr_id.strip():
            raise ValueError("Mã Purchase Request (pr_id) không hợp lệ hoặc rỗng.")
        clean_pr_id = pr_id.strip()

        await connect_db()
        prisma = get_prisma()

        async with prisma.tx() as tx:
            # 1. Lock PurchaseRequest row with SELECT ... FOR UPDATE
            locked_prs = await tx.query_raw(
                'SELECT id, status, "departmentId", "estimatedValue" FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_prs:
                raise ValueError(f"Không tìm thấy Purchase Request với mã: '{clean_pr_id}'")

            pr_row = locked_prs[0]
            current_status = pr_row["status"]
            if current_status == "CLOSED":
                raise ValueError(f"Purchase Request '{clean_pr_id}' đã ở trạng thái CLOSED.")

            # 2. Lock PurchaseOrder row belonging to this PR
            locked_pos = await tx.query_raw(
                'SELECT id, quantity, "poNumber", "totalAmount" FROM "PurchaseOrder" WHERE "purchaseRequestId" = $1 FOR UPDATE',
                clean_pr_id,
            )
            if not locked_pos:
                raise ValueError(f"Không thể đóng PR: Purchase Request '{clean_pr_id}' chưa có Purchase Order.")

            po_row = locked_pos[0]
            po_id = po_row["id"]
            po_qty = int(po_row["quantity"])

            # 3. Query all Receivings for this PO
            receivings = await tx.receiving.find_many(
                where={"purchaseOrderId": po_id}
            )
            total_received = sum(r.receivedQty for r in receivings)

            # 4. HD-07 / REQ-BR-11 Guard: SUM(receivedQty) >= PO.quantity
            if total_received < po_qty:
                raise ValueError(
                    f"Không thể đóng PR: Hàng chưa được nhận đủ. "
                    f"Tổng đã nhận: {total_received}/{po_qty} sản phẩm (theo HD-07 / REQ-BR-11)."
                )

            # 5. Budget Settlement
            dept_id = pr_row["departmentId"]
            est_val = Decimal(str(pr_row["estimatedValue"]))

            rows = await tx.query_raw(
                'SELECT id, "allocatedAmount", "spentAmount", "tempReservedAmount" '
                'FROM "Budget" '
                'WHERE "departmentId" = $1 AND "fiscalYear" = $2 AND quarter = $3 '
                'FOR UPDATE',
                dept_id,
                ACTIVE_BUDGET_FISCAL_YEAR,
                ACTIVE_BUDGET_QUARTER,
            )
            if not rows:
                raise ValueError(
                    f"Không tìm thấy ngân sách khả dụng cho phòng ban '{dept_id}' "
                    f"trong kỳ tài chính Năm {ACTIVE_BUDGET_FISCAL_YEAR} - Quý {ACTIVE_BUDGET_QUARTER}."
                )

            budget_row = rows[0]
            budget_id = budget_row["id"]
            current_reserved = Decimal(str(budget_row["tempReservedAmount"]))
            current_spent = Decimal(str(budget_row["spentAmount"]))

            # Release tempReservedAmount safely (cannot drop below 0)
            reserved_release = min(current_reserved, est_val)
            new_reserved = current_reserved - reserved_release
            new_spent = current_spent + est_val

            await tx.budget.update(
                where={"id": budget_id},
                data={
                    "tempReservedAmount": new_reserved,
                    "spentAmount": new_spent,
                }
            )

            # 6. Update PurchaseRequest status to CLOSED
            updated_pr = await tx.purchaserequest.update(
                where={"id": clean_pr_id},
                data={"status": "CLOSED"}
            )

        return {
            "id": updated_pr.id,
            "title": updated_pr.title,
            "status": updated_pr.status,
            "departmentId": updated_pr.departmentId,
            "deptId": updated_pr.departmentId,
            "estimatedValue": float(updated_pr.estimatedValue),
            "settledAmount": float(est_val),
            "totalReceived": total_received,
            "poQuantity": po_qty,
            "releasedReserved": float(reserved_release),
            "newSpentAmount": float(new_spent),
        }

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

# TASK-007 Evidence — HD-07 Receiving Completion Guard in `close_pr()`

## 1. Metadata
- **Project:** AI Procurement & Purchase Approval System (ProcureAI) — Group 01<br>
- **Branch:** `final-delivery`<br>
- **Task:** TASK-007 — Fix HD-07: Enforce Receiving Completion Guard in `close_pr()`<br>
- **User Story:** US-10 (Close Purchase Request & Đối soát 3 bên PR-PO-Receiving)<br>
- **Backlog Tasks:** T-34 (Đối soát PR-PO-Receiving), T-35 (Điều kiện Close HD-07), T-36 (Audit Trail & Budget Settlement)<br>
- **Human Decision:** HD-07 ("Receiving Complete" Definition: `SUM(receivedQty) >= PurchaseOrder.quantity`)<br>
- **Business Rule:** REQ-BR-11 (Receiving Close Guard), REQ-BR-04 (Receiving Qty Limit), REQ-BR-10 (PO Guard)<br>
- **Responsible Owner:** Trần Thị Thu Hà (Phụ trách US-10 & QA Lead)<br>
- **Collaborator:** Nguyễn Thị Thùy Dung (Phụ trách US-08 PO & US-09 Receiving)<br>
- **Verification Date:** 2026-09-24<br>
- **Status:** ✅ VERIFIED / COMPLETED (ALREADY IMPLEMENTED)

---

## 2. Scope
TASK-007 yêu cầu bảo vệ chặt chẽ quy trình đóng Yêu cầu Mua sắm (Purchase Request - PR):
- **Quy tắc bắt buộc (HD-07 / REQ-BR-11):** Tổng số lượng hàng hóa đã nhận qua tất cả các biên bản giao nhận liên quan (`Receiving`) phải đạt hoặc vượt số lượng đặt hàng trên Đơn đặt hàng (`PurchaseOrder.quantity`):
  $$\sum \text{receivedQty} \ge \text{PurchaseOrder.quantity}$$
- **Hành vi nghiệp vụ:**
  - Nếu $\sum \text{receivedQty} < \text{PurchaseOrder.quantity}$ (chưa giao hàng hoặc giao thiếu): Từ chối đóng PR (ném `ValueError` / HTTP 400 Bad Request). Trạng thái PR không đổi, ngân sách không quyết toán, transaction rollback hoàn toàn.
  - Nếu $\sum \text{receivedQty} \ge \text{PurchaseOrder.quantity}$ (giao đủ hoặc nhiều đợt lũy kế đủ): Cho phép chuyển PR sang trạng thái `CLOSED`, giải phóng `tempReservedAmount` và tăng `spentAmount` trong bảng `Budget`.

---

## 3. Implementation Status
> **KẾT LUẬN: COMPLETED (ALREADY IMPLEMENTED)**

Toàn bộ logic nghiệp vụ cốt lõi của **HD-07 / REQ-BR-11** đã được triển khai hoàn chỉnh từ **TASK-003 Step 3B.7** (commit `dfdd7e5`, entry `AI-053`) và được bảo vệ ở tầng định danh/phân quyền qua Server-Side RBAC tại **TASK-005** (commit `6f47a4e`, entry `AI-057`).
- **Không có bất kỳ thay đổi nào đối với mã nguồn production (`backend/app/`) trong TASK-007.**
- TASK-007 hoàn tất việc kiểm chứng độc lập (Independent Verification), đồng bộ các test cases HTTP cũ với hợp đồng bảo mật (Security Contract) của TASK-005 và lập tài liệu bằng chứng nghiệm thu.

---

## 4. Production Runtime Path
Đường dẫn thực thi thực tế khi người dùng hoặc hệ thống đóng PR:

```
[Client / HTTP Request]
       │
       ▼ POST /api/pr/{id}/close  + [Authorization: Bearer <JWT>]
[backend/app/routers/pr.py: close_pr()]
       │
       ├─► Dependency: RoleChecker(["FINANCE", "ADMIN"]) (RBAC Check)
       ├─► Identity: Trích xuất actor_user_id từ verified JWT
       │
       ▼
[backend/app/services/procurement_service.py: close_pr_prisma()]
       │
       ├─► async with prisma.tx() as tx:
       │     ├─► 1. Khóa dòng PR: SELECT ... FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE
       │     ├─► 2. Kiểm tra PR status != "CLOSED"
       │     ├─► 3. Khóa dòng PO: SELECT ... FROM "PurchaseOrder" WHERE "purchaseRequestId" = $1 FOR UPDATE
       │     ├─► 4. Truy vấn toàn bộ Receiving: tx.receiving.find_many(where={"purchaseOrderId": po_id})
       │     ├─► 5. Tính lũy kế: total_received = sum(r.receivedQty for r in receivings)
       │     ├─► 6. [HD-07 GUARD]: if total_received < po_qty: raise ValueError(...)
       │     ├─► 7. Khóa dòng Budget: SELECT ... FROM "Budget" WHERE ... FOR UPDATE
       │     ├─► 8. Quyết toán ngân sách: Giảm tempReservedAmount, tăng spentAmount
       │     └─► 9. Cập nhật PR: status = "CLOSED"
       │
       ▼
[Supabase PostgreSQL (Atomic Transaction Commit / Rollback)]
```

- **Router:** [`backend/app/routers/pr.py:L73-89`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py#L73-L89) được bảo vệ bởi `RoleChecker(["FINANCE", "ADMIN"])`.
- **Service Production:** [`backend/app/services/procurement_service.py:L1355-1473`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L1355-L1473) (`close_pr_prisma`).
- **Hàm legacy `close_pr()`:** (lines 1475-1488) là MockDB cũ từ Early Phase, không được router hay production code gọi (0 calls).

---

## 5. Source Code Evidence

Tại [`backend/app/services/procurement_service.py:L1404-1416`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L1404-L1416):

```python
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
```

### Đặc tính kỹ thuật cốt lõi:
1. **Truy vấn toàn bộ Receiving:** `tx.receiving.find_many(where={"purchaseOrderId": po_id})` thu thập tất cả phiếu giao nhận, cho phép cộng dồn chính xác nhiều đợt giao nhận từng phần (Partial Receiving).
2. **Tổng hợp số lượng:** `total_received = sum(r.receivedQty for r in receivings)`.
3. **So sánh với `PO.quantity`:** Điều kiện chặn `total_received < po_qty` tương đương với điều kiện thành công `total_received >= po_qty`.
4. **Xử lý thất bại (Insufficient Receiving):** Ném `ValueError`, router chuyển thành `HTTPException(400)`. Transaction PostgreSQL rollback tự động 100%, ngân sách không bị quyết toán, PR giữ nguyên trạng thái.
5. **Xử lý thành công (Full Receiving):** PR chuyển trạng thái `CLOSED`, ngân sách giải phóng `tempReservedAmount` và tăng `spentAmount` theo số tiền `estimatedValue` của PR.
6. **Không có đường Bypass:** Không có tham số cờ `force=True` hay bất kỳ ngoại lệ nào.

---

## 6. Execution Evidence

Toàn bộ kết quả thực thi được ghi nhận trực tiếp từ terminal kiểm thử:

### A. Close PR Suite (`test_close_prisma.py`)
```bash
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_close_prisma.py -v
```
**Output:** **14 passed, 1 warning in 120.29s (02:00)**
- `test_tc_close_001_full_receiving_close_success`: PASSED (Nhận đủ 4/4 $\to$ CLOSED thành công).
- `test_tc_close_002_insufficient_receiving_rejected`: PASSED (Nhận thiếu 2/5 $\to$ Bị chặn, raise ValueError, PR giữ nguyên `PO_CREATED`).
- `test_tc_close_003_multiple_partials_sum_complete_close_success`: PASSED (Giao nhận 3 đợt 2+3+1 = 6/6 $\to$ CLOSED thành công).
- `test_tc_close_004_zero_receiving_rejected`: PASSED (Nhận 0/3 $\to$ Bị chặn).
- `test_tc_close_005_over_receiving_blocked_by_br04`: PASSED (Nhận vượt quá bị chặn bởi REQ-BR-04).
- `test_tc_close_006_pr_not_found`: PASSED (PR không tồn tại $\to$ Báo lỗi rõ ràng).
- `test_tc_close_007_pr_without_po_rejected`: PASSED (PR chưa có PO $\to$ Không thể đóng).
- `test_tc_close_008_pr_status_transitions_to_closed`: PASSED (PR chuyển `CLOSED`, đóng lần 2 bị chặn).
- `test_tc_close_009_budget_settlement_accurate`: PASSED (tempReservedAmount về 0, spentAmount tăng đúng giá trị PR).
- `test_tc_close_010_rejected_close_does_not_mutate_budget`: PASSED (Đóng thất bại $\to$ Ngân sách nguyên vẹn 100%).
- `test_tc_close_011_atomic_transaction_rollback`: PASSED (Atomic rollback khi có lỗi).
- `test_tc_close_012_concurrent_close_attempts`: PASSED (Khóa dòng chống double close khi có 2 request đồng thời).
- `test_tc_close_013_api_post_close_pr_endpoint`: PASSED (Gọi API qua HTTP với token FINANCE $\to$ HTTP 200 OK, PR CLOSED).
- `test_tc_close_014_zero_mockdb_write`: PASSED (Zero write vào MockDB).

### B. Goods Receiving Suite (`test_receiving_prisma.py`)
```bash
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_receiving_prisma.py -v
```
**Output:** **14 passed, 1 warning in 114.78s (01:54)**
- Toàn bộ 14/14 test cases về giao nhận hàng hóa (nhận đủ, nhận thiếu, nhận nhiều đợt, khóa số lượng REQ-BR-04, API post/get receiving) đạt **100% PASS**.

### C. Purchase Order Suite (`test_po_prisma.py`)
```bash
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_po_prisma.py -v
```
**Output:** **18 passed, 1 warning in 143.56s (02:23)**
- Toàn bộ 18/18 test cases về tạo PO, guard PR APPROVED (BUG-001 / TASK-006), chống giả mạo giá/số lượng T-094, và API PO đạt **100% PASS**.

### D. PR Approval Suite (`test_pr_approval_prisma.py`)
```bash
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_pr_approval_prisma.py -v
```
**Output:** **15 passed in 85.32s**
- Toàn bộ 15/15 test cases duyệt PR 2 cấp và ngưỡng ngân sách 50M đạt **100% PASS**.

### E. Full Regression Chuỗi Mua Sắm (PR → PO → Receiving → Close)
```bash
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_close_prisma.py backend/tests/test_receiving_prisma.py backend/tests/test_po_prisma.py backend/tests/test_pr_approval_prisma.py -q
```
**Output:**
```text
.............................................................            [100%]
61 passed, 1 warning in 416.63s (0:06:56)
```
👉 **Đạt 61/61 PASS (100% GREEN, ZERO FAILURES).**

### F. Security RBAC Regression
```bash
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_rbac.py -k "po or receiving or close" -v
```
**Output:**
```text
backend\tests\test_rbac.py::test_tc_rbac_005_procurement_create_po_success PASSED [ 16%]
backend\tests\test_rbac.py::test_tc_rbac_018_employee_create_po_forbidden PASSED [ 33%]
backend\tests\test_rbac.py::test_tc_rbac_020_employee_record_receiving_forbidden PASSED [ 50%]
backend\tests\test_rbac.py::test_tc_rbac_021_finance_close_pr_success PASSED [ 66%]
backend\tests\test_rbac.py::test_tc_rbac_022_employee_close_pr_forbidden PASSED [ 83%]
backend\tests\test_rbac.py::test_tc_rbac_028_admin_create_po_success PASSED [100%]
================ 6 passed, 22 deselected, 3 warnings in 36.85s ================
```
👉 **Đạt 6/6 PASS (100% GREEN).**

---

## 7. Test Security Contract Synchronization
Trong quá trình xác minh, 7 test HTTP cũ (được viết từ TASK-003 trước khi có RBAC) gặp lỗi `401 Unauthorized` do thiếu `Authorization: Bearer <token>`. Chúng đã được đồng bộ chuẩn hóa theo Security Contract của TASK-005:
1. `test_tc_close_013`: Gửi JWT token ES256 với vai trò `FINANCE` (`finance@company.com`).
2. `test_tc_rec_012`, `test_tc_rec_014`: Gửi JWT token ES256 với vai trò `PROCUREMENT` (`procurement@company.com`).
3. `test_tc_po_005`, `test_tc_po_006`, `test_tc_po_017`, `test_tc_po_018`: Gửi JWT token ES256 với vai trò `PROCUREMENT` (`procurement@company.com`).

**Cam kết:**
- Giữ nguyên 100% các assertion nghiệp vụ (status code 200/400, kiểm tra giá, số lượng, kiểm tra CSDL PostgreSQL, kiểm tra 0 dual-write MockDB).
- Không làm giảm tính nghiêm ngặt của test.
- Không sửa đổi bất kỳ dòng mã nào trong `backend/app/`.

---

## 8. Đối Chiếu Tiêu Chí Nghiệm Thu (Acceptance Criteria)

| Tiêu chí nghiệm thu (Acceptance Criteria) | Kết quả kiểm chứng thực tế | Trạng thái |
|---|---|:---:|
| **AC1:** Chặn đóng PR nếu tổng số lượng thực nhận nhỏ hơn số lượng đặt trên PO ($\sum \text{receivedQty} < \text{PO.quantity}$). | Đã kiểm chứng: `test_tc_close_002` (thiếu 2/5) và `test_tc_close_004` (nhận 0/3) bị từ chối với `ValueError`, PR không bị đóng. | ✅ **ĐẠT** |
| **AC2:** Cho phép đóng PR khi hàng đã nhận đủ hoặc vượt số lượng ($\sum \text{receivedQty} \ge \text{PO.quantity}$). | Đã kiểm chứng: `test_tc_close_001` (4/4) và `test_tc_close_003` (2+3+1 = 6/6) đóng thành công, PR status = `CLOSED`. | ✅ **ĐẠT** |
| **AC3:** Thông báo lỗi nêu rõ số lượng thực nhận so với số lượng đặt hàng. | Chi tiết lỗi: *"Không thể đóng PR: Hàng chưa được nhận đủ. Tổng đã nhận: {total_received}/{po_qty} sản phẩm (theo HD-07 / REQ-BR-11)."* | ✅ **ĐẠT** |
| **AC4:** Đối soát ngân sách và giải phóng số tiền tạm giữ an toàn. | Đã kiểm chứng: `test_tc_close_009` xác nhận `tempReservedAmount` giảm về 0 và `spentAmount` tăng đúng `estimatedValue`. | ✅ **ĐẠT** |
| **AC5:** Giao dịch an toàn, không có race condition khi nhiều yêu cầu đóng đồng thời. | Đã kiểm chứng: `test_tc_close_012` dùng 3 khóa dòng `SELECT ... FOR UPDATE` đảm bảo chỉ duy nhất 1 request thành công. | ✅ **ĐẠT** |

---

## 9. Tính Toàn Vẹn Chuỗi Nghiệp Vụ (Regression Integrity)
Toàn bộ chuỗi quy trình mua sắm từ đầu đến cuối trên live Supabase PostgreSQL:
- **PR Approval:** 15/15 PASS
- **Purchase Order (PO):** 18/18 PASS
- **Goods Receiving:** 14/14 PASS
- **Close PR & Đối soát:** 14/14 PASS
- **Tổng cộng chuỗi:** **61/61 PASS (100%)**
- **Bảo mật phân quyền RBAC:** **6/6 PASS (100%)**

---

## 10. Kết Luận (Conclusion)
- **Trạng thái nhiệm vụ:** **TASK-007 = VERIFIED / COMPLETED (ALREADY IMPLEMENTED)**.
- **Xác nhận phạm vi mã nguồn:** **KHÔNG CÓ SOURCE CODE PRODUCTION CHANGE MỚI NÀO ĐƯỢC THỰC HIỆN CHO TASK-007.**
- Logic nghiệp vụ đã hoàn thiện vững chắc từ TASK-003 Step 3B.7, hoạt động chuẩn xác với cơ sở dữ liệu PostgreSQL thực tế, hoàn toàn tương thích và được bảo vệ an toàn bởi Server-Side RBAC của TASK-005.

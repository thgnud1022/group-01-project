# BÁO CÁO NGHIỆM THU — TASK-006: ENFORCE PR APPROVED GUARD IN `create_po` (BUG-001)

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)<br>
**Nhánh:** `final-delivery`<br>
**Nhiệm vụ:** TASK-006 — Fix BUG-001: Enforce PR APPROVED Guard in `create_po()`<br>
**User Story:** US-08 (Lựa chọn NCC & Tạo Purchase Order)<br>
**Backlog Tasks:** T-26, T-27, T-28, T-29<br>
**Cơ sở quyết định:** HD-04 (Enforce PR "APPROVED" Status for PO Creation), HD-08 (Option A), HD-12, GOV-01<br>
**Quy tắc nghiệp vụ:** REQ-BR-10 (PO Creation Approval Guard), REQ-BR-12 (Server-side quotation resolution)<br>
**Người thực hiện chính:** Nguyễn Thị Thùy Dung (US-08, Backend PO Implementation)<br>
**QA Lead / Kiểm thử:** Trần Thị Thu Hà (QA Lead / Verification)<br>
**Ngày nghiệm thu:** 2026-09-24<br>
**Trạng thái:** ✅ VERIFIED / COMPLETED (ALREADY IMPLEMENTED)

---

## 1. PHẠM VI & MỤC TIÊU (SCOPE)

TASK-006 xử lý lỗi thiếu sót nghiệp vụ mang mã hiệu **BUG-001** đã được xác định từ giai đoạn khảo sát Baseline (`FINAL_DELIVERY_BASELINE.md`) và quy định bắt buộc sửa đổi theo **HD-04 / REQ-BR-10**:
- **Quy tắc bắt buộc:** Một Đơn đặt hàng (Purchase Order - PO) tuyệt đối KHÔNG ĐƯỢC PHÉP tạo ra trừ khi Yêu cầu Mua sắm (Purchase Request - PR) liên quan đã ở trạng thái **`APPROVED`**.
- **Hành vi kỳ vọng:**
  - PR ở trạng thái `DRAFT`, `PENDING_MANAGER_APPROVAL`, `PENDING_FINANCE_APPROVAL` $\to$ Từ chối (HTTP 400 Bad Request / ValueError).
  - PR ở trạng thái `REJECTED` $\to$ Từ chối (HTTP 400 Bad Request / ValueError).
  - PR ở trạng thái `APPROVED` $\to$ Tạo PO thành công (PO `status = SENT`, PR chuyển sang `PO_CREATED`).

---

## 2. BẰNG CHỨNG MÃ NGUỒN (SOURCE CODE EVIDENCE)

Khảo sát và Final Audit độc lập ngày 2026-09-24 xác nhận logic guard của HD-04 / REQ-BR-10 **đã được triển khai hoàn chỉnh 100% trong cả 2 tầng mã nguồn**, không cần viết thêm mã mới:

### A. Tầng Production Runtime: `create_po_prisma()` & Router `POST /api/po`
- **File:** [`backend/app/services/procurement_service.py:L1030-1044`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L1030-L1044) (triển khai tại TASK-003 Step 3B.5, entry `AI-051`).
- **File Router:** [`backend/app/routers/po.py:L19-45`](file:///d:/LTUD/group-01-project-main/backend/app/routers/po.py#L19-L45) (bảo vệ RBAC tại TASK-005, entry `AI-057`).
- **Production Path:** Router `POST /api/po` được bảo vệ bởi `RoleChecker(["PROCUREMENT", "ADMIN"])`, trích xuất `creator_user_id` từ verified JWT, và gọi trực tiếp `ProcurementService.create_po_prisma(...)`.
- **Cơ chế Khóa dòng & Transaction:**
  ```python
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
  ```
  *Đánh giá:* Guard nằm trong khối `async with prisma.tx()` với câu lệnh `SELECT ... FOR UPDATE` trên PostgreSQL, loại trừ hoàn toàn nguy cơ race condition. Nếu trạng thái khác `APPROVED`, `ValueError` lập tức được kích hoạt, transaction tự động rollback 100% và router trả về HTTP 400.

### B. Tầng MockDB Legacy: `create_po()`
- **File:** [`backend/app/services/procurement_service.py:L877-883`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L877-L883) (triển khai tại US-09 Backend Core, entry `AI-026`).
- **Mã nguồn Guard:**
  ```python
  # 3. REQ-BR-10 / HD-04 (BUG-001): Enforce PR status == "APPROVED"
  pr_status = pr.get("status")
  if pr_status != "APPROVED":
      raise ValueError(
          f"Không thể tạo PO: Purchase Request {pr_id} chưa được duyệt "
          f"(trạng thái hiện tại: {pr_status}). Yêu cầu trạng thái phải là APPROVED."
      )
  ```
  *Đánh giá:* Hàm đồng bộ phục vụ tương thích ngược với các unit tests MockDB cũ, cũng được bảo vệ nghiêm ngặt bởi cùng một điều kiện kiểm tra.

---

## 3. BẰNG CHỨNG KIỂM THỬ THỰC TẾ (EXECUTION EVIDENCE)

Toàn bộ các bằng chứng dưới đây đều được trích xuất trực tiếp từ kết quả chạy thực nghiệm (Terminal Execution Outputs) trong quá trình audit:

### A. Kiểm thử Tích hợp trên Supabase PostgreSQL thật (`test_po_prisma.py`)
- **Lệnh thực thi:**
  ```bash
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_po_prisma.py -k "tc_po_001 or tc_po_002"
  ```
- **Kết quả thực tế từ Terminal:**
  ```text
  ============================= test session starts =============================
  platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
  rootdir: D:\LTUD\group-01-project-main\backend
  configfile: pyproject.toml
  plugins: anyio-4.15.1
  collected 18 items / 16 deselected / 2 selected

  backend\tests\test_po_prisma.py ..                                       [100%]
  ================ 2 passed, 16 deselected, 1 warning in 16.25s =================
  ```
- **Chi tiết các Test Case đã kiểm chứng:**
  - `test_tc_po_001_approved_pr_valid_quotation_success`: Tạo PR, duyệt PR lên `APPROVED`, tạo Quotation, gọi `create_po_prisma` $\to$ Thành công, tạo PO mã `PO-NUM-2026-...`, status `SENT`, trạng thái PR chuyển sang `PO_CREATED` trên CSDL PostgreSQL. (**PASS**)
  - `test_tc_po_002_non_approved_pr_rejected`:
    1. Thử tạo PO khi PR ở trạng thái `PENDING_MANAGER_APPROVAL` $\to$ Bị chặn, raise `ValueError`: *"Purchase Request ... chưa được duyệt (trạng thái hiện tại: 'PENDING_MANAGER_APPROVAL'). Yêu cầu trạng thái phải là APPROVED."* (**PASS**)
    2. Thử tạo PO khi PR ở trạng thái `REJECTED` $\to$ Bị chặn, raise `ValueError`: *"Purchase Request ... chưa được duyệt (trạng thái hiện tại: 'REJECTED'). Yêu cầu trạng thái phải là APPROVED."* (**PASS**)

### B. Kiểm thử Trực tiếp Luồng Đồng bộ (`create_po`)
- **Thực thi script kiểm tra:**
  ```python
  # 1. DRAFT PR
  PASS (DRAFT BLOCKED): Không thể tạo PO: Purchase Request PR-DRAFT-TEST chưa được duyệt (trạng thái hiện tại: DRAFT). Yêu cầu trạng thái phải là APPROVED.
  # 2. REJECTED PR
  PASS (REJECTED BLOCKED): Không thể tạo PO: Purchase Request PR-REJ-TEST chưa được duyệt (trạng thái hiện tại: REJECTED). Yêu cầu trạng thái phải là APPROVED.
  # 3. APPROVED PR
  PASS (APPROVED SUCCESS): PO id = PO-2026-001 | status = SENT
  ```

### C. Kiểm thử Tích hợp An ninh API & RBAC (`test_rbac.py`)
- `test_tc_rbac_005_procurement_full_lifecycle_success`: Sau khi PR được Manager duyệt thành công (`APPROVED`), vai trò `PROCUREMENT` gọi `POST /api/po` $\to$ **HTTP 200 OK**, PO được khởi tạo với trạng thái `SENT`. (**PASS**)
- `test_tc_rbac_018_employee_create_po_forbidden`: Người dùng vai trò `EMPLOYEE` gọi `POST /api/po` $\to$ Bị chặn bởi `RoleChecker`, trả về **HTTP 403 Forbidden**. (**PASS**)

---

## 4. ĐỐI CHIẾU TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

| Tiêu chí nghiệm thu (Acceptance Criteria) | Kết quả kiểm chứng | Trạng thái |
|---|---|:---:|
| **AC1:** Không thể tạo PO từ PR chưa được duyệt dưới bất kỳ hình thức nào (`DRAFT`, `PENDING`, `REJECTED`). | Đã kiểm chứng: `test_tc_po_002` PASS trên PostgreSQL; `create_po` reject DRAFT/REJECTED. | ✅ **ĐẠT** |
| **AC2:** Tạo PO thành công khi PR đã ở trạng thái `APPROVED`. | Đã kiểm chứng: `test_tc_po_001` và `test_tc_rbac_005` PASS, PO sinh ra với `status: SENT` và PR chuyển thành `PO_CREATED`. | ✅ **ĐẠT** |
| **AC3:** Thông báo lỗi rõ ràng, tường minh về trạng thái không hợp lệ. | Báo cáo chi tiết: *"Không thể tạo PO: Purchase Request {id} chưa được duyệt (trạng thái hiện tại: '{status}'). Yêu cầu trạng thái phải là APPROVED."* | ✅ **ĐẠT** |
| **AC4:** Test case tự động chạy trong test suite có bằng chứng thực thi. | `test_po_prisma.py` (2 passed in 16.25s) và `test_business_rules.py` (4 passed in 1.48s) chạy thực tế 100% green. | ✅ **ĐẠT** |

---

## 5. KẾT LUẬN (CONCLUSION)

- **Trạng thái nhiệm vụ:** **TASK-006 = VERIFIED / COMPLETED (ALREADY IMPLEMENTED)**.
- **Xác nhận phạm vi mã nguồn:** **KHÔNG CÓ SOURCE-CODE CHANGE MỚI ĐƯỢC THỰC HIỆN CHO TASK-006.** Logic nghiệp vụ và các chốt chặn an ninh đã tồn tại vững chắc từ các giai đoạn trước (US-09, TASK-003 Step 3B.5, TASK-005), bảo vệ nguyên vẹn kiến trúc Server-Side RBAC và PostgreSQL Persistence.

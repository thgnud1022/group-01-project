# TASK-008 Pre-Close Review Report — Supplier & Quotation Backend API

**Dự án:** AI Procurement & Purchase Approval System — Group 01
**Branch:** `final-delivery`
**Ngày lập:** 2026-09-24
**Người thực hiện:** Senior Backend Reviewer & QA Lead
**Mục tiêu:** Rà soát toàn diện trước khi đóng TASK-008 dựa trên source code thực tế và các Human Decisions đã phê duyệt.

---

## 1. Human Decisions Formally Recorded

Hai quyết định kiến trúc và phạm vi then chốt cho TASK-008 đã được Human phê duyệt chính thức và ghi nhận đồng bộ vào [`docs/DECISION_LOG.md`](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md), [`docs/HUMAN_DECISION_BRIEF.md`](file:///d:/LTUD/group-01-project-main/docs/HUMAN_DECISION_BRIEF.md), và [`docs/IMPLEMENTATION_PLAN.md`](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md):

### 1.1. HD-14 / HRD-03: Quotation File Storage Architecture
- **Quyết định:** **APPROVED — OPTION A: URL METADATA PERSISTENCE**
- **Nội dung:**
  - Hệ thống duy trì trường `fileUrl: String` trong model `Quotation` (PostgreSQL) và lưu chuỗi đường dẫn/URL metadata từ client (ví dụ: `"quotes/default.pdf"`).
  - Không triển khai upload tệp nhị phân (binary multipart/form-data) lên Supabase Storage bucket trong phạm vi Final Delivery.
- **Lý do & Tác động:**
  - Loại bỏ hoàn toàn sự phụ thuộc vào Supabase Service Role Key và rủi ro trễ mạng/lỗi upload khi chấm điểm và kiểm thử tự động.
  - Tận dụng 100% Prisma schema và logic hiện hữu trong `procurement_service.py` mà không làm gián đoạn chuỗi quy trình mua sắm.

### 1.2. HD-15: Supplier Management Scope for Procurement Flow (CLD)
- **Quyết định:** **APPROVED — OPTION A: SCOPE CREATE, LIST, DETAIL (CLD)**
- **Nội dung:**
  - Backend API cung cấp 3 endpoints: `POST /api/suppliers` (tạo mới), `GET /api/suppliers` (danh sách), `GET /api/suppliers/{id}` (chi tiết).
  - HD-15 scope = Create + List + Detail (CLD); Update/Delete không thuộc Final Delivery scope.
- **Lý do & Tác động:**
  - Đáp ứng 100% yêu cầu nghiệp vụ của US-06 (T-17: Quản lý Supplier) phục vụ việc liên kết báo giá.
  - Bảo vệ tuyệt đối tính toàn vẹn khóa ngoại (Foreign Key Integrity) trong PostgreSQL: ngăn ngừa việc xóa nhà cung cấp đã có liên kết với `Quotation` và `PurchaseOrder`.

---

## 2. Requirement Interpretation & Mapping

| Backlog / Spec | Requirement ID | Mô tả nghiệp vụ | Hiện trạng trong Code |
| :--- | :--- | :--- | :--- |
| **US-06 / T-17** | `REQ-FR-10` | Procurement quản lý nhà cung cấp để thu thập báo giá. | `POST /api/suppliers`, `GET /api/suppliers`, `GET /api/suppliers/{id}`. |
| **US-06 / T-18** | `REQ-FR-10`, `HRD-03` | Upload và lưu trữ thông tin Quotation. | `POST /api/quotations` lưu `fileUrl`, `totalAmount`, `quantity`, `deliveryDays`, `warrantyTerms`. |
| **US-06 / T-19** | `REQ-BR-06`, `T-052` | Chỉ liên kết Quotation vào Purchase Request đã được `APPROVED`. | `create_quotation_prisma` thực hiện row lock `SELECT FOR UPDATE` và chặn nếu `status != 'APPROVED'`. |
| **US-06 / T-20** | `REQ-FR-11`, `REQ-BR-12` | Chuẩn hóa đơn giá (Derived `unitPrice`) và số lượng (HD-08 `quantity`). | Tính `unitPrice = (totalAmount / quantity)` dạng Decimal `ROUND_HALF_UP`. |
| **US-06 / T-20** | `REQ-FR-12`, `REQ-FR-15` | So sánh báo giá giữa các nhà cung cấp, cảnh báo chênh lệch $\ge 20\%$. | `POST /api/quotations/compare` truy vấn CSDL PostgreSQL, tính đơn giá trung bình và cắm cờ `isAnomaly`. |
| **Governance** | `REQ-NFR-02`, `HD-13` | Phân quyền truy cập Server-Side RBAC. | RoleChecker(`["PROCUREMENT", "ADMIN"]`) cho thao tác ghi; `get_current_identity` cho thao tác đọc. |

---

## 3. Current Implementation Status

### 3.1. Database Layer (PostgreSQL / Prisma)
- Model `Supplier` ([`backend/prisma/schema.prisma:98-104`](file:///d:/LTUD/group-01-project-main/backend/prisma/schema.prisma#L98-L104)): `id`, `name` (unique), `taxCode`, `contact`, quan hệ 1-N với `Quotation`.
- Model `Quotation` ([`backend/prisma/schema.prisma:106-122`](file:///d:/LTUD/group-01-project-main/backend/prisma/schema.prisma#L106-L122)): `id`, `purchaseRequestId`, `supplierId`, `totalAmount` (Decimal 18,2), `quantity` (Int), `deliveryDays` (Int), `warrantyTerms`, `fileUrl`, `isAnomaly`, `anomalyReason`, quan hệ N-1 với `PurchaseRequest` và `Supplier`, quan hệ 1-N với `PurchaseOrder`.
- Cả hai model đã được migrate bền vững trên Supabase PostgreSQL.

### 3.2. Service Layer ([`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py))
- `create_supplier_prisma(name, tax_code, contact)`: Insert PostgreSQL, bắt lỗi `UniqueViolationError` (HTTP 400).
- `list_suppliers_prisma()`: Query tất cả supplier từ PostgreSQL sắp xếp theo tên.
- `get_supplier_prisma(supplier_id)`: Query supplier theo ID từ PostgreSQL.
- `create_quotation_prisma(...)`: Atomic transaction `prisma.tx()`:
  - Row lock PR với `SELECT ... FOR UPDATE`.
  - Guard T-052: Bắt buộc PR `status == 'APPROVED'`.
  - Kiểm tra Supplier tồn tại (T-053).
  - Validate thương mại: `quantity > 0`, `totalAmount > 0`, `deliveryDays >= 0`.
  - Insert record vào bảng `Quotation`.
  - Re-query kèm join `include={"supplier": True}` và tính derived `unitPrice`.
- `list_quotations_prisma(purchase_request_id)`: Liệt kê báo giá, hỗ trợ filter.
- `get_quotation_prisma(quotation_id)`: Lấy chi tiết báo giá kèm joined supplier.
- `list_quotations_by_pr_prisma(purchase_request_id)`: Lấy danh sách báo giá của PR.
- `compare_quotations_prisma(purchase_request_id)`: So sánh báo giá đọc trực tiếp từ PostgreSQL, tính giá trung bình và cắm cờ `isAnomaly` nếu cao hơn $\ge 20\%$.

### 3.3. Router Layer
- [`backend/app/routers/suppliers.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/suppliers.py):
  - `POST /api/suppliers`: `RoleChecker(["PROCUREMENT", "ADMIN"])`
  - `GET /api/suppliers`: `get_current_identity`
  - `GET /api/suppliers/{supplier_id}`: `get_current_identity`
- [`backend/app/routers/quotations.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/quotations.py):
  - `POST /api/quotations`: `RoleChecker(["PROCUREMENT", "ADMIN"])`
  - `GET /api/quotations`: `get_current_identity`
  - `GET /api/quotations/{quotation_id}`: `get_current_identity`
  - `GET /api/purchase-requests/{pr_id}/quotations`: `get_current_identity`
  - `POST /api/quotations/compare`: `get_current_identity`

---

## 4. Test Status & Audit Phân Loại

### 4.1. Integration Test Suite ([`backend/tests/test_supplier_quotation_prisma.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_supplier_quotation_prisma.py))
- **Kết quả thực tế:** **15/15 PASSED in 59.04s** (100% GREEN trên PostgreSQL thực).
- Bao phủ:
  - `TC-SQ-001`: Tạo nhà cung cấp thành công.
  - `TC-SQ-002`: Chặn trùng tên nhà cung cấp (Unique constraint).
  - `TC-SQ-003`: Liệt kê nhà cung cấp.
  - `TC-SQ-004`: Lấy chi tiết nhà cung cấp theo ID.
  - `TC-SQ-005`: Báo lỗi khi ID nhà cung cấp không tồn tại.
  - `TC-SQ-006`: Tạo Quotation trên PR đã `APPROVED` thành công, verify liên kết FK.
  - `TC-SQ-007`: Đơn giá derived `unitPrice` được tính chính xác với Decimal `ROUND_HALF_UP`.
  - `TC-SQ-008`: Chặn tạo Quotation trên PR chưa duyệt (`PENDING_MANAGER_APPROVAL`).
  - `TC-SQ-009`: Chặn tạo Quotation khi `supplierId` không tồn tại.
  - `TC-SQ-010`: Chặn tạo Quotation khi `purchaseRequestId` không tồn tại.
  - `TC-SQ-011`: Chặn tạo Quotation khi `quantity <= 0` hoặc `totalAmount <= 0`.
  - `TC-SQ-012`: Liệt kê danh sách Quotation của một PR.
  - `TC-SQ-013`: Endpoint Compare đọc trực tiếp từ PostgreSQL, phát hiện anomaly 20% tiền định, 0 MockDB writes.
  - `TC-SQ-014`: Cách ly dữ liệu báo giá giữa các PR (PR-A không rò rỉ sang PR-B).
  - `TC-SQ-015`: Rollback giao dịch nguyên tử khi gặp lỗi (không tạo orphan record).

### 4.2. RBAC Test Suite ([`backend/tests/test_rbac.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_rbac.py))
- **Kết quả thực tế:** **3/3 PASSED** cho các test liên quan Supplier & Quotation:
  - `RBAC-019`: Employee tạo Quotation -> 403 Forbidden (PASS).
  - `RBAC-025`: Employee tạo Supplier -> 403 Forbidden (PASS).
  - `RBAC-026`: Procurement tạo Supplier -> 200 OK (PASS).

### 4.3. Audit File Test Cũ: [`backend/tests/test_quotation.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_quotation.py)
- **Kết quả thực tế:** 3 FAILED, 3 PASSED.
- **Phân loại từng test case:**

| Test Case | Kết quả | Phân loại | Nguyên nhân chi tiết |
| :--- | :--- | :--- | :--- |
| `test_tc_quote_001` | FAILED (401) | **STALE TEST + DUPLICATED COVERAGE** | Test gọi `POST /api/quotations/compare` không có Bearer token. Đồng thời assert dữ liệu được ghi vào `db.quotations` (MockDB), trong khi router production hiện đọc từ PostgreSQL. Tính năng compare trên PostgreSQL đã được cover 100% bởi `test_tc_sq_013` (PASS). |
| `test_tc_quote_002` | FAILED (401) | **STALE TEST + DUPLICATED COVERAGE** | Test gọi `GET /api/quotations/{id}` không có Bearer token. Đồng thời gán mock data vào `db.quotations[q_id]`, trong khi router production hiện đọc từ PostgreSQL. Tính năng get quotation đã được cover bởi `test_tc_sq_006` (PASS). |
| `test_tc_quote_003` | FAILED (401) | **TEST THAT SHOULD BE UPDATED** | Test gọi `GET /api/quotations/QT-NON-EXISTENT` mong đợi 404 nhưng nhận 401 do thiếu JWT token. Nếu cung cấp token hợp lệ, endpoint sẽ trả về đúng HTTP 404 `Không tìm thấy Quotation`. Cần cập nhật fixture token cho test này. |
| `test_tc_quote_004` | PASSED | **STALE TEST (LEGACY COMPATIBILITY)** | Kiểm tra hàm legacy `ProcurementService.register_quotation()` trên MockDB. |
| `test_tc_quote_005` | PASSED | **STALE TEST (LEGACY COMPATIBILITY)** | Kiểm tra validation quantity trong hàm legacy `register_quotation()`. |
| `test_tc_quote_006` | PASSED | **ACTIVE & VALID** | Kiểm tra Prisma model `Quotation` có trường `quantity: int` (HD-08 Contract). |

### 4.4. Audit File Test Cũ: [`backend/tests/test_all_endpoints.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_all_endpoints.py)
- **Kết quả thực tế:** 2 FAILED, 2 PASSED (`test_healthcheck`: PASS, `test_get_budget`: FAIL 401, `test_ai_standardize_pr`: PASS, `test_full_7step_procurement_workflow`: FAIL 401).
- **Phân loại:** **STALE TEST (PRE-AUTH SMOKE SUITE)**.
- **Nguyên nhân:** File smoke test từ Phase 0 gọi toàn bộ endpoints mà không truyền JWT Bearer token. Toàn bộ 7 bước mua sắm này hiện đã có các bộ test chuyên biệt chạy trên PostgreSQL với đầy đủ authentication/RBAC.

---

## 5. Remaining Gaps

1. **Gap 1 (Test Sync):** File [`backend/tests/test_quotation.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_quotation.py) cần được đồng bộ hóa authentication và loại bỏ các assertion phụ thuộc MockDatabase để phản ánh đúng Prisma/PostgreSQL runtime hiện tại.
2. **Gap 2 (Documentation Alignment):** [`docs/IMPLEMENTATION_PLAN.md`](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md) vẫn ghi `Status: PLANNED` cho TASK-008, cần được cập nhật thành `COMPLETED (ALREADY IMPLEMENTED)` kèm đánh dấu các Acceptance Criteria sau khi xử lý xong test scope.
3. **Gap 3 (Traceability):** [`docs/AI_USAGE_TRACEABILITY.md`](file:///d:/LTUD/group-01-project-main/docs/AI_USAGE_TRACEABILITY.md) và [`docs/logs/ai-usage-log.md`](file:///d:/LTUD/group-01-project-main/docs/logs/ai-usage-log.md) cần ghi nhận lượt hoàn tất nghiệm thu cho TASK-008.

---

## 6. Exact Files That Need Changes vs. Do NOT Need Changes

### 6.1. Files that do NOT need changes (Giữ nguyên tuyệt đối)
- `backend/prisma/schema.prisma` — Model `Supplier` và `Quotation` đã đủ 100%.
- `backend/app/routers/suppliers.py` — Đã có 3 endpoints chuẩn kèm RBAC.
- `backend/app/routers/quotations.py` — Đã có 5 endpoints chuẩn kèm RBAC.
- `backend/app/services/procurement_service.py` — Đã có đủ 8 Prisma methods hoạt động hoàn hảo.
- `backend/app/main.py` — Đã include đầy đủ cả 2 routers.
- `backend/tests/test_supplier_quotation_prisma.py` — 15/15 test cases đang PASS 100%.
- `backend/tests/test_rbac.py` — 28/28 test cases đang PASS 100%.

### 6.2. Files that NEED changes (Trong các bước tiếp theo)
1. [`backend/tests/test_quotation.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_quotation.py):
   - Cung cấp JWT authentication header (ES256 / `_MockJWKSClient`).
   - Cập nhật test `test_tc_quote_001` và `test_tc_quote_002` để gọi endpoint thật hoặc seed dữ liệu PostgreSQL thay vì mock dictionary in-memory.
   - Cập nhật `test_tc_quote_003` thêm header auth để verify HTTP 404.
2. [`docs/IMPLEMENTATION_PLAN.md`](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md):
   - Đổi `Status: COMPLETED (ALREADY IMPLEMENTED)` cho TASK-008.
   - Đánh dấu hoàn thành các checkbox Acceptance Criteria.
3. [`docs/AI_USAGE_TRACEABILITY.md`](file:///d:/LTUD/group-01-project-main/docs/AI_USAGE_TRACEABILITY.md) & [`docs/logs/ai-usage-log.md`](file:///d:/LTUD/group-01-project-main/docs/logs/ai-usage-log.md):
   - Ghi nhận phiên làm việc đóng TASK-008.
4. [`docs/evidence/TASK-008-SUPPLIER-QUOTATION.md`](file:///d:/LTUD/group-01-project-main/docs/evidence/TASK-008-SUPPLIER-QUOTATION.md):
   - Tạo hồ sơ nghiệm thu chính thức sau khi test suite đạt 100% GREEN.

---

## 7. Close Criteria for TASK-008

TASK-008 sẽ đủ điều kiện đóng khi và chỉ khi:
- [x] **Criterion 1 (Human Decisions):** HD-14 (HRD-03) và HD-15 đã được phê duyệt và ghi nhận đầy đủ vào Decision Log.
- [x] **Criterion 2 (Core Logic & DB):** Logic quản lý Supplier & Quotation, PR status guard, FK integrity, Decimal `unitPrice`, và so sánh báo giá đã chạy trên Supabase PostgreSQL.
- [x] **Criterion 3 (RBAC Enforcement):** Phân quyền đúng theo HD-13 K-1/K-2.
- [ ] **Criterion 4 (Test Suite Sync):** File test [`backend/tests/test_quotation.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_quotation.py) được đồng bộ authentication, đạt 6/6 PASS; regression [`test_supplier_quotation_prisma.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_supplier_quotation_prisma.py) giữ vững 15/15 PASS.
- [ ] **Criterion 5 (Evidence & Traceability):** Hồ sơ nghiệm thu `TASK-008-SUPPLIER-QUOTATION.md` được tạo và các tài liệu quản trị được đồng bộ trạng thái `COMPLETED`.

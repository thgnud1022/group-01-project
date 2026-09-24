# Verification & Evidence Report — TASK-008: Supplier & Quotation Backend API

**Project:** AI Procurement & Purchase Approval System — Group 01
**Branch:** `final-delivery`
**Date:** 2026-09-24
**Status:** COMPLETED / VERIFIED

---

## A. Task Identity

* **Task ID:** TASK-008 — Supplier & Quotation Backend API
* **Related Epic:** EPIC-03 (Supplier & Quotation Management)
* **Related User Stories:**
  * **US-06:** Thu thập & Liên kết Quotations (T-17, T-18, T-19, T-20)
  * **US-05:** Finance Budget Check (T-14, T-15, T-16)
* **Team Allocation (Group-01 Authoritative Allocation):**
  * **Responsible Owner:** Nguyễn Trương Thùy Dương (BA / PO phụ trách US-04, US-05, US-06)
  * **Backend Engineering & Security Support:** Nguyễn Thị Thùy Dung
  * **Frontend UI Support:** Trần Thị Kiều Giang
  * **QA Lead & Test Auditor:** Trần Thị Thu Hà

---

## B. Human Decisions (Formally Resolved)

Hai quyết định kiến trúc và phạm vi chính thức đã được Human phê duyệt, ghi nhận tại [`docs/DECISION_LOG.md`](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md) và [`docs/HUMAN_DECISION_BRIEF.md`](file:///d:/LTUD/group-01-project-main/docs/HUMAN_DECISION_BRIEF.md):

### 1. HD-14 / HRD-03: Quotation File Storage Architecture
* **Quyết định:** **APPROVED — OPTION A: URL METADATA PERSISTENCE**
* **Nội dung:** Hệ thống duy trì trường `fileUrl: String` trong model `Quotation` (PostgreSQL) và lưu trữ chuỗi đường dẫn/URL metadata được cung cấp từ client (ví dụ: `"quotes/default.pdf"`). Hệ thống **không** triển khai multipart binary upload lên Supabase Storage bucket trong phạm vi Final Delivery.
* **Lý do & Rationale:**
  * Loại bỏ hoàn toàn sự phụ thuộc vào Supabase Service Role Key và nguy cơ trễ mạng khi kiểm thử tự động, CI/CD hoặc bảo vệ đồ án (Viva defense).
  * Mô hình dữ liệu và quy trình Prisma Client hiện hữu đã hoạt động ổn định 100% từ TASK-003 Step 3B.4, đảm bảo liên kết toàn vẹn từ PR → Quotation → PO → Receiving → Close PR.
* **Định vị phạm vi:** Đây là quyết định đã chốt chính thức (Approved Scope), không phải là unresolved blocker.

### 2. HD-15: Supplier Management Scope for Procurement Flow (CLD)
* **Quyết định:** **APPROVED — OPTION A: SCOPE CREATE, LIST, DETAIL (CLD)**
* **Nội dung:** Phạm vi quản lý Supplier tại backend API bao gồm 3 endpoints: `POST /api/suppliers` (tạo mới), `GET /api/suppliers` (danh sách), `GET /api/suppliers/{id}` (chi tiết). HD-15 scope = Create + List + Detail (CLD); Update/Delete không thuộc Final Delivery scope.
* **Lý do & Rationale:**
  * Đáp ứng 100% nhu cầu nghiệp vụ của US-06 (T-17: Quản lý Supplier) phục vụ lựa chọn nhà cung cấp và thu thập báo giá.
  * Ngăn ngừa việc xóa nhà cung cấp đã có giao dịch liên kết với `Quotation` và `PurchaseOrder`, bảo vệ tuyệt đối tính toàn vẹn khóa ngoại (Foreign Key Integrity) trong cơ sở dữ liệu PostgreSQL.
* **Định vị phạm vi:** Đây là quyết định đã chốt chính thức (Approved Scope), không phải là unresolved blocker.

---

## C. Production Implementation Verified

Toàn bộ 8 endpoints thuộc phạm vi TASK-008 đã được triển khai hoàn chỉnh bằng Prisma Client kết nối Supabase PostgreSQL:

### 1. Supplier Endpoints ([`backend/app/routers/suppliers.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/suppliers.py))
* `POST /api/suppliers`: Tạo nhà cung cấp mới trong PostgreSQL (Yêu cầu role `PROCUREMENT`, `ADMIN`).
* `GET /api/suppliers`: Liệt kê tất cả nhà cung cấp từ PostgreSQL (Mọi authenticated user theo HD-13 K-1).
* `GET /api/suppliers/{supplier_id}`: Lấy chi tiết nhà cung cấp theo ID từ PostgreSQL (Mọi authenticated user theo HD-13 K-1).

### 2. Quotation Endpoints ([`backend/app/routers/quotations.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/quotations.py))
* `POST /api/quotations`: Tạo và liên kết báo giá với PR đã duyệt trong PostgreSQL (Yêu cầu role `PROCUREMENT`, `ADMIN`).
* `GET /api/quotations`: Liệt kê tất cả báo giá (hỗ trợ filter `?purchaseRequestId=...`).
* `GET /api/quotations/{quotation_id}`: Lấy chi tiết báo giá kèm joined thông tin Supplier và derived `unitPrice`.
* `GET /api/purchase-requests/{pr_id}/quotations`: Lấy danh sách báo giá của một Purchase Request.
* `POST /api/quotations/compare`: So sánh báo giá đọc trực tiếp từ PostgreSQL, tính đơn giá trung bình và cắm cờ anomaly $\ge 20\%$ tiền định (Mọi authenticated user theo HD-13 K-2).

### 3. Service Layer Methods ([`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py))

Supplier management methods (HD-15 scope = Create + List + Detail (CLD); Update/Delete không thuộc Final Delivery scope):
* `create_supplier_prisma(name, tax_code, contact)`
* `list_suppliers_prisma()`
* `get_supplier_prisma(supplier_id)`

Quotation management methods:
* `create_quotation_prisma(purchase_request_id, supplier_id, total_amount, quantity, delivery_days, warranty_terms, file_url)`
* `list_quotations_prisma(purchase_request_id)`
* `get_quotation_prisma(quotation_id)`
* `list_quotations_by_pr_prisma(purchase_request_id)`
* `compare_quotations_prisma(purchase_request_id)`

---

## D. Database Evidence

* **Prisma Models ([`backend/prisma/schema.prisma`](file:///d:/LTUD/group-01-project-main/backend/prisma/schema.prisma)):**
  ```prisma
  model Supplier {
    id         String      @id @default(uuid())
    name       String      @unique
    taxCode    String?
    contact    String?
    quotations Quotation[]
  }

  model Quotation {
    id                String          @id @default(uuid())
    purchaseRequestId String
    purchaseRequest   PurchaseRequest @relation(fields: [purchaseRequestId], references: [id])
    supplierId        String
    supplier          Supplier        @relation(fields: [supplierId], references: [id])
    totalAmount       Decimal         @db.Decimal(18, 2)
    quantity          Int
    deliveryDays      Int
    warrantyTerms     String?
    fileUrl           String
    isAnomaly         Boolean         @default(false)
    anomalyReason     String?
    purchaseOrders    PurchaseOrder[]
    created_at        DateTime        @default(now())
  }
  ```
* **Foreign Keys:**
  * `Quotation.purchaseRequestId` trỏ tới `PurchaseRequest.id`.
  * `Quotation.supplierId` trỏ tới `Supplier.id`.
* **Trường số lượng (HD-08 Option A):** `quantity Int` được lưu trữ trực tiếp trên Quotation, đóng vai trò là server-side source of truth cho đơn hàng (PO.quantity).
* **Trường tệp đính kèm (HD-14 Option A):** `fileUrl String` lưu chuỗi đường dẫn/URL metadata.
* **Prisma Schema Changes:** **0 changes** mới trong TASK-008 (schema đã hoàn chỉnh từ các task trước).

---

## E. Business Rules & Security Evidence

1. **Guard PR APPROVED (T-052 / REQ-BR-06):**
   * Trong `create_quotation_prisma`, hệ thống mở transaction `prisma.tx()` và thực thi khóa dòng `SELECT id, status FROM "PurchaseRequest" WHERE id = $1 FOR UPDATE`.
   * Nếu `pr.status != 'APPROVED'`, hệ thống từ chối ngay lập tức với `ValueError` (HTTP 400).
2. **Kiểm tra tính toàn vẹn nhà cung cấp (T-053):**
   * Xác minh `Supplier.id` tồn tại trong PostgreSQL trước khi cho phép tạo Quotation.
3. **Validation thương mại chặt chẽ:**
   * `quantity > 0` (số nguyên dương).
   * `totalAmount > 0` (Decimal).
   * `deliveryDays >= 0` (số nguyên không âm).
4. **Xử lý đơn giá Derived `unitPrice` kiểu Decimal:**
   * `unitPrice = (totalAmount / quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
   * Đảm bảo tính toán thương mại chính xác tuyệt đối, tránh sai số số thực (floating point error).
5. **So sánh báo giá & Cảnh báo bất thường (REQ-FR-12, REQ-FR-15):**
   * Truy vấn 100% dữ liệu từ PostgreSQL, join bảng `Supplier`.
   * Tính đơn giá trung bình của các báo giá thuộc PR.
   * Nếu đơn giá cao hơn $\ge 20\%$ so với mức trung bình, cắm cờ `isAnomaly = True` kèm `anomalyReason` mang tính tiền định.
6. **Transaction Rollback & Isolation (T-053 / TC-SQ-015):**
   * Mọi lỗi xảy ra trong quá trình tạo báo giá đều rollback toàn bộ giao dịch, đảm bảo không sinh bản ghi mồ côi (orphan records).
   * Báo giá của PR-A hoàn toàn cách ly với PR-B (TC-SQ-014).
7. **Server-Side RBAC Enforcement (HD-13 / TASK-005):**
   * Thao tác ghi Supplier (`POST /api/suppliers`): Giới hạn cho `PROCUREMENT`, `ADMIN`.
   * Thao tác ghi Quotation (`POST /api/quotations`): Giới hạn cho `PROCUREMENT`, `ADMIN`.
   * Thao tác đọc (`GET`): Cho phép mọi người dùng đã xác thực (HD-13 Policy K-1).
   * Thao tác so sánh (`POST /api/quotations/compare`): Cho phép mọi người dùng đã xác thực (HD-13 Policy K-2).

---

## F. Test Evidence

Toàn bộ 24 test cases thuộc domain Supplier & Quotation đã được kiểm thử thực tế và đạt trạng thái **100% GREEN**:

### 1. `backend/tests/test_quotation.py` (6/6 PASS in 14.59s)
```text
test_tc_quote_001_ai_compare_creates_and_persists_quantity   PASSED
test_tc_quote_002_get_quotation_by_id_returns_quantity       PASSED
test_tc_quote_003_get_quotation_not_found                    PASSED
test_tc_quote_004_register_quotation_service                 PASSED
test_tc_quote_005_register_quotation_invalid_quantity_rejected PASSED
test_tc_quote_006_prisma_quotation_model_has_quantity        PASSED
==================================================
6 passed, 1 warning in 14.59s
```

### 2. `backend/tests/test_supplier_quotation_prisma.py` (15/15 PASS in 51.38s)
```text
test_tc_sq_001_create_supplier_success                       PASSED
test_tc_sq_002_duplicate_supplier_name_rejected              PASSED
test_tc_sq_003_list_suppliers                                PASSED
test_tc_sq_004_get_supplier_by_id                            PASSED
test_tc_sq_005_get_supplier_not_found                        PASSED
test_tc_sq_006_create_quotation_on_approved_pr_success       PASSED
test_tc_sq_007_derived_decimal_unit_price                    PASSED
test_tc_sq_008_reject_quotation_on_non_approved_pr           PASSED
test_tc_sq_009_reject_quotation_invalid_supplier             PASSED
test_tc_sq_010_reject_quotation_invalid_pr                   PASSED
test_tc_sq_011_reject_quotation_invalid_quantity_or_amount   PASSED
test_tc_sq_012_list_quotations_by_pr                         PASSED
test_tc_sq_013_compare_quotations_reads_from_postgres        PASSED
test_tc_sq_014_pr_quotation_isolation                        PASSED
test_tc_sq_015_atomic_transaction_rollback                   PASSED
==================================================
15 passed, 1 warning in 51.38s
```

### 3. `backend/tests/test_rbac.py -k "supplier or quotation"` (3/3 PASS in 7.36s)
```text
test_tc_rbac_019_employee_create_quotation_forbidden         PASSED
test_tc_rbac_025_employee_create_supplier_forbidden          PASSED
test_tc_rbac_026_procurement_create_supplier_success         PASSED
==================================================
3 passed, 25 deselected, 3 warnings in 7.36s
```

### Tổng kết Domain Supplier & Quotation:
```text
TOTAL: 24 passed, 0 failed (100% GREEN)
```

---

## G. Out-of-Scope Known Tests

File kiểm thử sơ khai từ Phase 0 [`backend/tests/test_all_endpoints.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_all_endpoints.py) vẫn tồn tại 2 trường hợp lỗi 401 Unauthorized (`test_get_budget`, `test_full_7step_procurement_workflow`) do gửi request trực tiếp không kèm header JWT Bearer.

* **Đánh giá kỹ thuật:** File này là pre-auth smoke suite được viết trước khi hệ thống tích hợp Supabase JWT (TASK-004) và Server-Side RBAC (TASK-005). Toàn bộ 7 bước nghiệp vụ trong luồng mua sắm hiện đã có các bộ test tích hợp chuyên biệt kết nối CSDL Supabase PostgreSQL với đầy đủ authentication context.
* **Kết luận:** Hai lỗi này **hoàn toàn nằm ngoài phạm vi nghiệm thu của TASK-008** và không ảnh hưởng đến tính đúng đắn của domain Supplier & Quotation.

---

## H. Acceptance Criteria Matrix

| AC | Requirement | Implementation | Test | Evidence | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **AC-1** | Quản lý Supplier (HD-15 scope = Create, List, Detail) | `routers/suppliers.py`<br>`ProcurementService` management methods (CLD) | `TC-SQ-001`, `002`, `003`, `004`, `005` | Postgres table `Supplier`<br>Unique constraint | **VERIFIED** |
| **AC-2** | Quotation chỉ liên kết vào PR đã `APPROVED` | `routers/quotations.py`<br>`create_quotation_prisma` | `TC-SQ-008` | `SELECT FOR UPDATE`<br>ValueError 400 | **VERIFIED** |
| **AC-3** | Toàn vẹn Foreign Key (Supplier & PR) | `schema.prisma`<br>`create_quotation_prisma` | `TC-SQ-006`, `009`, `010` | FK relations trong DB<br>Test rollback | **VERIFIED** |
| **AC-4** | Toàn vẹn thương mại (quantity > 0, amount > 0) | Pydantic validation<br>`create_quotation_prisma` | `TC-SQ-007`, `011`<br>`TC-QUOTE-001` | Derived Decimal unitPrice<br>Assert DB persistence | **VERIFIED** |
| **AC-5** | Bảng so sánh báo giá & Cảnh báo Anomaly 20% | `compare_quotations_prisma`<br>`POST /compare` | `TC-SQ-013`<br>`TC-QUOTE-001` | Tính đơn giá trung bình<br>Cắm cờ isAnomaly | **VERIFIED** |
| **AC-6** | Cách ly dữ liệu & Rollback giao dịch | Prisma transaction `prisma.tx()` | `TC-SQ-014`, `015` | Zero orphan records<br>Zero leakage giữa PR | **VERIFIED** |
| **AC-7** | Server-Side RBAC Enforcement | `RoleChecker(["PROCUREMENT", "ADMIN"])`<br>`get_current_identity` | `RBAC-019`, `025`, `026` | 403 Forbidden cho Employee<br>200 OK cho Procurement | **VERIFIED** |
| **AC-8** | Legacy Test Synchronization | `test_quotation.py` đồng bộ JWT ES256 & Prisma | `TC-QUOTE-001..006` | 6/6 tests PASSED<br>100% business intent và expected business outcomes được bảo toàn. Các assertion persistence cũ trên MockDB được thay thế bằng assertion tương đương trên Prisma/PostgreSQL; không có business requirement nào bị giảm, bypass hoặc weakening. | **VERIFIED** |

---

## I. Scope Limitations

1. **HD-14 (HRD-03):** Không triển khai upload tệp nhị phân lên Supabase Storage bucket. Hệ thống lưu chuỗi metadata `fileUrl: String`.
2. **HD-15:** Không triển khai endpoint `PUT /api/suppliers/{id}` và `DELETE /api/suppliers/{id}` để bảo vệ toàn vẹn khóa ngoại với Quotation và PO.
3. **Phân định rõ ràng:** Các giới hạn trên là **phạm vi đã được Human phê duyệt chính thức**, không phải là khoảng trống kỹ thuật chưa giải quyết (unresolved gaps).

---

## J. Closure Statement

> **TASK-008 (Supplier & Quotation Backend API) is READY and COMPLETED.**
>
> * Core backend implementation và CSDL Supabase PostgreSQL đã vận hành ổn định 100%.
> * Toàn bộ 24/24 test cases thuộc domain Supplier & Quotation đạt **100% GREEN**.
> * Mã nguồn production và schema giữ nguyên trạng thái bất biến (**0 code changes**).
> * Hồ sơ bằng chứng, quyết định kiến trúc và ma trận truy vết đã được đồng bộ hóa hoàn chỉnh.

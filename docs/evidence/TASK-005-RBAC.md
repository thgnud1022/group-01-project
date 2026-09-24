# BÁO CÁO NGHIỆM THU — TASK-005: SERVER-SIDE RBAC IMPLEMENTATION

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)<br>
**Nhánh:** `final-delivery`<br>
**Nhiệm vụ:** TASK-005 — Implement Server-Side Role-Based Access Control (RBAC)<br>
**Cơ sở quyết định:** HD-02, HD-12, HD-REQ-07, HD-REQ-09, GOV-01, REQ-BR-02, REQ-BR-04, REQ-BR-10, REQ-BR-11, T-37, T-38, T-39<br>
**Người thực hiện chính:** Nguyễn Thị Thùy Dung (GOV-01, US-08, Backend RBAC)<br>
**Ngày hoàn thành:** 2026-09-24<br>
**Trạng thái:** ✅ COMPLETED — 28/28 RBAC TESTS PASSED

---

## 1. TỔNG QUAN KẾT QUẢ TRIỂN KHAI

TASK-005 đã triển khai toàn diện cơ chế Kiểm soát Truy cập Dựa trên Vai trò (RBAC) phía Server theo kiến trúc Zero-Trust (HD-02, HD-12), xóa bỏ triệt để việc tin tưởng dữ liệu danh tính từ client và thực thi chính sách cấm tự phê duyệt (No Self-Approval — GOV-01) cho mọi vai trò.

### Các thành quả trọng tâm:
1. **Bảo vệ 100% Endpoints Nghiệp vụ (19/19):**
   - Không còn bất kỳ endpoint nghiệp vụ nào mở tự do (open unauthenticated).
   - Mỗi endpoint đều được kiểm soát qua `get_current_identity` (xác thực danh tính) và `RoleChecker` (phân quyền vai trò).
2. **Khắc phục Triệt để Client Identity Injection:**
   - `creatorId` trong `POST /api/pr` và `POST /api/po` được ghi đè tự động bằng `current_user.id` (UUID từ database qua `JWT.sub`).
   - `approverEmail` trong `POST /api/pr/{id}/approve` bị vô hiệu hóa vai trò danh tính; người phê duyệt được xác thực 100% từ JWT.
   - `finance_user` trong `POST /api/pr/{id}/close` được thay bằng `current_user.id` từ JWT.
3. **Thực thi No Self-Approval (GOV-01 / T-39):**
   - Kiểm tra `approver_id == pr_creator_id` tại tầng Service (`approve_pr_prisma`).
   - Áp dụng bình đẳng cho mọi vai trò (`EMPLOYEE`, `MANAGER`, `FINANCE`, `PROCUREMENT`, `ADMIN`), không có ngoại lệ Admin.
   - Trả về mã lỗi HTTP 403 Forbidden với thông báo: *"Không thể phê duyệt PR do chính mình tạo (No Self-Approval — GOV-01)."*
4. **Phân quyền Đa tầng theo Trạng thái & Hạn mức (REQ-BR-02):**
   - PR > 50 triệu VND: Bước 1 bắt buộc `MANAGER` hoặc `ADMIN` duyệt; Bước 2 bắt buộc `FINANCE` hoặc `ADMIN` duyệt.
   - Kiểm tra vai trò giai đoạn trước, chặn tự duyệt sau, đảm bảo tính nhất quán nghiệp vụ.
5. **Đồng nhất Hợp đồng Mã lỗi (401 vs 403 vs 400):**
   - 401 Unauthorized: Lỗi xác thực JWT (thiếu header, sai định dạng, token hết hạn/sai chữ ký, user không tồn tại trong DB).
   - 403 Forbidden: Lỗi phân quyền vai trò (RoleChecker), vi phạm No Self-Approval, duyệt sai vai trò giai đoạn.
   - 400 Bad Request: Lỗi nghiệp vụ (trạng thái PR không hợp lệ, dữ liệu thương mại không hợp lệ).

---

## 2. MA TRẬN BẢO VỆ 19 ENDPOINTS

| # | Router | Endpoint | HTTP Method | Vai trò cho phép (Role Gate) | Ghi chú & Nguồn quyết định |
| :-: | :--- | :--- | :---: | :--- | :--- |
| 1 | `pr.py` | `/api/pr` | POST | ALL (`EMPLOYEE`, `MANAGER`, `PROCUREMENT`, `FINANCE`, `ADMIN`) | US-01; Ghi đè `creatorId` bằng `current_user.id` |
| 2 | `pr.py` | `/api/pr` | GET | ALL (`get_current_identity`) | US-02; Người dùng xác thực có quyền xem danh sách |
| 3 | `pr.py` | `/api/pr/{id}/approve` | POST | `MANAGER`, `FINANCE`, `ADMIN` | REQ-BR-02, GOV-01; No Self-Approval & Stage auth tại Service |
| 4 | `pr.py` | `/api/pr/{id}/close` | POST | `FINANCE`, `ADMIN` | US-10; Ghi đè `actor_user_id` bằng `current_user.id` |
| 5 | `pr.py` | `/api/pr/{id}/quotations` | GET | ALL (`get_current_identity`) | T-061; Xem báo giá liên kết PR |
| 6 | `po.py` | `/api/po` | POST | `PROCUREMENT`, `ADMIN` | US-08; Ghi đè `creatorId` bằng `current_user.id` |
| 7 | `po.py` | `/api/po` | GET | ALL (`get_current_identity`) | Quyết định K-1: ALLOW cho nhân viên xem PO |
| 8 | `quotations.py` | `/api/quotations` | POST | `PROCUREMENT`, `ADMIN` | US-06; Chỉ Procurement/Admin tạo báo giá |
| 9 | `quotations.py` | `/api/quotations` | GET | ALL (`get_current_identity`) | Quyết định K-1: ALLOW xem danh sách báo giá |
| 10 | `quotations.py` | `/api/quotations/{id}` | GET | ALL (`get_current_identity`) | Quyết định K-1: ALLOW xem chi tiết báo giá |
| 11 | `quotations.py` | `/api/quotations/compare` | POST | ALL (`get_current_identity`) | Quyết định K-2: ALLOW so sánh báo giá |
| 12 | `quotations.py` | `/api/purchase-requests/{id}/quotations` | GET | ALL (`get_current_identity`) | T-061; Xem báo giá của PR |
| 13 | `receiving.py` | `/api/receiving` | POST | `PROCUREMENT`, `ADMIN` | Quyết định K-3: Giới hạn PROCUREMENT + ADMIN ghi nhận hàng |
| 14 | `receiving.py` | `/api/receiving` | GET | ALL (`get_current_identity`) | Quyết định K-1: ALLOW xem biên bản nhận hàng |
| 15 | `budget.py` | `/api/budget/{dept_id}` | GET | ALL (`get_current_identity`) | US-04, US-05; Xem ngân sách phòng ban |
| 16 | `budget.py` | `/api/budget` | GET | `FINANCE`, `ADMIN` | Tổng quan toàn bộ ngân sách công ty |
| 17 | `suppliers.py` | `/api/suppliers` | POST | `PROCUREMENT`, `ADMIN` | US-06, T-17; Tạo mới nhà cung cấp |
| 18 | `suppliers.py` | `/api/suppliers` | GET | ALL (`get_current_identity`) | Quyết định K-1: ALLOW xem danh sách NCC |
| 19 | `suppliers.py` | `/api/suppliers/{id}` | GET | ALL (`get_current_identity`) | Quyết định K-1: ALLOW xem chi tiết NCC |

---

## 3. CÁC TẬP TIN TẠO MỚI VÀ CHỈNH SỬA

| Tập tin | Loại | Mô tả thay đổi |
| :--- | :---: | :--- |
| `backend/app/dependencies/rbac.py` | **MỚI** | Triển khai dependency factory `RoleChecker` và exception `AuthorizationError` (kế thừa `PermissionError` và `ValueError`). |
| `backend/tests/test_rbac.py` | **MỚI** | Bộ kiểm thử tích hợp 28 ca kiểm thử bảo mật RBAC (RBAC-001 -> RBAC-028). |
| `docs/evidence/TASK-005-RBAC.md` | **MỚI** | Tài liệu nghiệm thu và bằng chứng kiểm thử TASK-005. |
| `backend/app/services/procurement_service.py` | SỬA | Nâng cấp `approve_pr_prisma` thực thi No Self-Approval và stage-based auth; nâng cấp `create_pr_prisma`, `create_po_prisma`, `close_pr_prisma` hỗ trợ nhận UUID người dùng từ JWT. |
| `backend/app/routers/pr.py` | SỬA | Gắn `RoleChecker` và `get_current_identity` vào 5 endpoints PR; loại bỏ tin tưởng `creatorId`, `approverEmail`, `finance_user`. |
| `backend/app/routers/po.py` | SỬA | Gắn `RoleChecker(["PROCUREMENT", "ADMIN"])` và `get_current_identity` vào 2 endpoints PO; loại bỏ tin tưởng `creatorId`. |
| `backend/app/routers/quotations.py` | SỬA | Gắn `RoleChecker(["PROCUREMENT", "ADMIN"])` và `get_current_identity` vào 5 endpoints Báo giá. |
| `backend/app/routers/receiving.py` | SỬA | Gắn `RoleChecker(["PROCUREMENT", "ADMIN"])` và `get_current_identity` vào 2 endpoints Nhận hàng. |
| `backend/app/routers/budget.py` | SỬA | Gắn `RoleChecker(["FINANCE", "ADMIN"])` vào `GET /api/budget` và `get_current_identity` vào `GET /api/budget/{dept_id}`. |
| `backend/app/routers/suppliers.py` | SỬA | Gắn `RoleChecker(["PROCUREMENT", "ADMIN"])` và `get_current_identity` vào 3 endpoints Nhà cung cấp. |

---

## 4. KẾT QUẢ KIỂM THỬ (TEST RESULTS)

### 4.1. Bộ Test RBAC Chuyên biệt (`backend/tests/test_rbac.py`)
- **Tổng số test cases:** 28/28
- **Kết quả:** 100% PASSED

| Mã TC | Tên Ca Kiểm Thử | Phân loại | Kết quả |
| :--- | :--- | :---: | :---: |
| **RBAC-001** | Missing JWT | Auth (401) | ✅ PASSED |
| **RBAC-002** | Invalid/Expired JWT | Auth (401) | ✅ PASSED |
| **RBAC-003** | Employee approve PR | Role Gate (403) | ✅ PASSED |
| **RBAC-004** | Manager approve PR (step 1, non-creator) | Role + Stage (200) | ✅ PASSED |
| **RBAC-005** | Procurement create PO | Role Gate (200) | ✅ PASSED |
| **RBAC-006** | Finance approve PR (step 2, non-creator) | Role + Stage (200) | ✅ PASSED |
| **RBAC-007** | Admin approve PR (non-creator) | Role + Stage (200) | ✅ PASSED |
| **RBAC-008** | Client role injection ignored | Injection Prevention (403) | ✅ PASSED |
| **RBAC-009** | Client creatorId injection ignored | Identity Integrity (200, JWT bound) | ✅ PASSED |
| **RBAC-010** | Client approverEmail injection ignored | Identity Integrity (200, JWT bound) | ✅ PASSED |
| **RBAC-011** | Employee self-approval rejected | Self-Approval / Role (403) | ✅ PASSED |
| **RBAC-012** | Manager self-approval rejected | Self-Approval (403 GOV-01) | ✅ PASSED |
| **RBAC-013** | Finance self-approval rejected | Self-Approval (403 GOV-01) | ✅ PASSED |
| **RBAC-014** | Procurement self-approval rejected | Self-Approval / Role (403) | ✅ PASSED |
| **RBAC-015** | Admin self-approval rejected | Self-Approval (403 GOV-01, No Admin bypass) | ✅ PASSED |
| **RBAC-016** | Wrong approval stage rejected (Finance step 1) | Stage-Based Auth (403) | ✅ PASSED |
| **RBAC-017** | DB role dynamic freshness (DB change immediate) | Dynamic Freshness (200 <-> 403) | ✅ PASSED |
| **RBAC-018** | Employee create PO forbidden | Role Gate (403) | ✅ PASSED |
| **RBAC-019** | Employee create Quotation forbidden | Role Gate (403) | ✅ PASSED |
| **RBAC-020** | Employee record Receiving forbidden | Role Gate (403) | ✅ PASSED |
| **RBAC-021** | Finance close PR success | Role + Business State (200) | ✅ PASSED |
| **RBAC-022** | Employee close PR forbidden | Role Gate (403) | ✅ PASSED |
| **RBAC-023** | Employee list all budgets forbidden | Role Gate (403) | ✅ PASSED |
| **RBAC-024** | Finance list all budgets success | Role Gate (200) | ✅ PASSED |
| **RBAC-025** | Employee create supplier forbidden | Role Gate (403) | ✅ PASSED |
| **RBAC-026** | Procurement create supplier success | Role Gate (200) | ✅ PASSED |
| **RBAC-027** | Manager approve step 2 (>50M) forbidden | Stage-Based Auth (403) | ✅ PASSED |
| **RBAC-028** | Admin create PO success | Role Gate (200) | ✅ PASSED |

### 4.2. Bộ Test Hồi quy (Regression Tests)
- `test_jwt_auth.py`: 12/12 PASSED (Xác thực JWT/JWKS không bị ảnh hưởng).
- `test_pr_approval_prisma.py`: 15/15 PASSED (Toàn bộ logic phê duyệt PR, concurrency, rollback tương thích hoàn toàn).

---

## 5. KẾT LUẬN & BÀN GIAO

TASK-005 hoàn thành đầy đủ các yêu cầu theo thiết kế được phê duyệt tại `docs/TASK-005-RBAC-DESIGN.md`:
- Hệ thống đạt mức độ bảo mật Server-side Zero-Trust hoàn chỉnh.
- Toàn bộ 19 endpoints đã được khóa an toàn.
- Hành vi cấm tự phê duyệt (No Self-Approval) hoạt động nghiêm ngặt trên mọi vai trò.
- Sẵn sàng chuyển giao tích hợp Frontend và chuẩn bị cho đợt demo nghiệm thu.

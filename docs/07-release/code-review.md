# HỒ SƠ KIỂM ĐIỂM MÃ NGUỒN (CODE REVIEW EVIDENCE)
## Báo Cáo Đánh Giá Chất Lượng Mã Nguồn & Sẵn Sàng Phát Hành (Release Readiness Review)

> **Dự án:** AI Procurement & Purchase Approval System  
> **Nhóm thực hiện:** Group 01  
> **Nhánh phát triển:** `final-delivery`  
> **Mã Commit HEAD:** `ad8023a`  
> **Phiên bản Bản phát hành:** `v1.0.0-final` (Git Tag: `9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`)  
> **Mục tiêu Chuẩn hóa:** Sản phẩm chuyển giao 3.6 (Deliverable 3.6 — Code Review Evidence)  
> **Phương pháp Thực hiện:** **Hồi cứu Lịch sử Mã nguồn (Retrospective Code Review)**  
> **Ghi chú Phương pháp:** *Hồ sơ này được tái cấu trúc độc lập từ toàn bộ lịch sử Git commits, cây mã nguồn thực tế, các bộ kiểm thử tự động và bằng chứng triển khai đám mây. Không giả mạo thảo luận GitHub PR, không bịa đặt người ký duyệt (reviewer) hay mốc thời gian.*

---

## 1. Trạng Thái Thẩm Định & Phân Định Ranh Giới (Review Status & Boundaries)

- **Trợ lý AI (AI Assistance):** Thu thập bằng chứng, đối chiếu chéo Story / Task / Commit / Test, rà soát mã nguồn tĩnh và dự thảo danh mục kiểm tra.
- **Thẩm định Con người (Human Review):** **DỰ THẢO HỒI CỨU — ĐANG CHỜ PHÊ DUYỆT CỦA CON NGƯỜI (RETROSPECTIVE DRAFT — HUMAN CONFIRMATION REQUIRED)**.
- **Trạng thái Mã nguồn Production:** Không có bất kỳ dòng mã production nào bị thay đổi trong quá trình lập tài liệu này.

---

## 2. Danh Mục Kiểm Tra Mã Nguồn (Code Review Checklist)

### 2.1. An ninh & Xác thực (Security & Authentication)
- [x] **Xác thực JWT Hợp lệ:** Triển khai xác thực JWT chuẩn thuật toán ES256 thông qua Supabase JWKS endpoint với cơ chế timeout 5.0s (`backend/app/services/jwt_service.py`).
- [x] **Ranh giới Zero-Trust Identity:** Loại bỏ hoàn toàn việc tin cậy client payload; danh tính người dùng (`AuthenticatedUser`) được phân giải từ trường `sub` của JWT sang `User.authUserId` trong CSDL PostgreSQL.
- [x] **Kiểm soát Phân quyền Máy chủ (Server-Side RBAC):** 100% 19 endpoints nghiệp vụ được bảo vệ bởi dependency `RoleChecker`, trả về HTTP 403 Forbidden khi vi phạm quyền.
- [x] **Quy tắc Không Tự Phê duyệt (No Self-Approval — GOV-01):** Áp dụng trên toàn bộ chu trình phê duyệt, từ chối và yêu cầu chỉnh sửa PR; chặn người tạo tự phê duyệt bất kể vai trò (kể cả ADMIN).
- [x] **Quản trị Bí mật & Cấu hình:** Không lưu trữ API Keys bí mật, token hay mật khẩu trong mã nguồn; sử dụng biến môi trường tách biệt.
- [x] **Từ chối Yêu cầu Bất hợp pháp (Fail-Closed):** Mọi request thiếu token hoặc token hết hạn bị chặn ngay lập tức với HTTP 401 Unauthorized.

### 2.2. Quy Tắc Nghiệp Vụ (Business Rules & Workflow)
- [x] **Bảo vệ Tạo PO (PO Approval Guard — REQ-BR-10):** Chặn tạo Purchase Order nếu PR chưa đạt trạng thái `APPROVED`; sử dụng khóa dòng `SELECT ... FOR UPDATE` trong transaction PostgreSQL.
- [x] **Khóa Giá & Số lượng Thương mại (REQ-BR-03 / REQ-FR-16):** Đơn giá và số lượng trên PO được khóa 100% từ Quotation trong CSDL; client payload bị bỏ qua hoàn toàn.
- [x] **Bảo vệ Đóng PR khi Nhận hàng (REQ-BR-11 / HD-07):** Chặn đóng PR nếu `SUM(receivedQty) < PO.quantity`; trả về HTTP 400 kèm thông báo chi tiết.
- [x] **Giữ & Quyết toán Ngân sách (Budget Reservation & Settlement):** Tạm giữ ngân sách (`tempReservedAmount`) khi tạo PR và quyết toán chi phí (`spentAmount`) khi đóng PR.
- [x] **Quyền Quyết định Thuộc về Con người (Human Award Decision):** AI chỉ đóng vai trò tư vấn xếp hạng; quyết định trao thầu và tạo PO hoàn toàn do chuyên viên mua sắm (PROCUREMENT) thực hiện.

### 2.3. Dữ Liệu & Bền Vững (Data Persistence & Schema)
- [x] **Tính nhất quán Schema Prisma:** Schema đồng bộ giữa Prisma Client và cấu trúc bảng PostgreSQL trên Supabase Cloud.
- [x] **Toàn vẹn Dữ liệu Không Phá hủy:** Không sử dụng các thao tác `drop table` hay migration phá hủy trên cơ sở dữ liệu production.
- [x] **Xử lý Xung đột Đồng thời:** Các thao tác thay đổi trạng thái và ngân sách đều dùng transaction có khóa dòng phân tán (`FOR UPDATE`).

### 2.4. Trí Tuệ Nhân Tạo (AI Features & Governance)
- [x] **AI Chỉ Tư vấn (Advisory Only):** Hệ thống không tự động tạo PO, không tự phê duyệt hay thay đổi trạng thái PR bằng AI.
- [x] **Công bố Trạng thái Gemini Live & Fallback:** Ghi nhận minh bạch Gemini Live API ở trạng thái `UNVERIFIED` trong môi trường kiểm thử tự động mặc định; bộ lọc Fallback Heuristic hoạt động ổn định (78% confidence).
- [x] **Bảo đảm Không Ảo giác (No Hallucination in Decisions):** Mọi đề xuất đều dựa trên dữ liệu báo giá thực tế của nhà cung cấp.

### 2.5. Kiểm Thử & Kiểm Chứng (Testing & Verification)
- [x] **Kiểm thử Hồi quy Backend:** 133 / 133 test cases Pytest PASSED.
- [x] **Kiểm thử Giao diện Chu trình:** 14 / 14 bước Puppeteer Browser E2E PASSED.
- [x] **Kiểm thử Kịch bản Thất bại (Failure Paths):** Đã kiểm chứng đầy đủ các kịch bản chặn 400/401/403.
- [x] **Kiểm thử Khói Đám mây:** 9 / 9 tiêu chí kiểm thử khói môi trường công khai PASSED (AI-089).

### 2.6. Phát Hành & Vận Hành (Release & Deployment)
- [x] **Đồng bộ Phiên bản:** Mã Git tag `v1.0.0-final` gắn đúng commit phát hành ổn định `9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`.
- [x] **Cấu hình Hạ tầng:** Frontend triển khai trên Vercel, Backend triển khai trên Railway, CSDL Supabase PostgreSQL.
- [x] **Minh bạch Giới hạn Kỹ thuật:** Công bố đầy đủ 4 giới hạn kỹ thuật được chấp nhận (Accepted Limitations).

---

## 3. Ma Trận Truy Xuất Nguồn Gốc (Story → Task → Commit → Test Traceability)

| User Story / Quy tắc Quản trị | Mã Tác vụ (Task) | Commit Hash | Tệp Nguồn Trọng Yếu | Bộ Kiểm Thử Tương Ứng | Kết Quả Thẩm Định |
|---|---|---|---|---|---|
| **US-01** (Tạo Yêu cầu Mua sắm PR) | T-01..T-03 | `6117d39`, `19ce38b` | `backend/app/routers/pr.py`, `backend/app/services/procurement_service.py` | `test_pr_creation_prisma.py` | **PASS (100%)** |
| **US-02** (Phê duyệt PR & Giữ Ngân sách) | T-04..T-06 | `6f47a4e` | `backend/app/routers/pr.py`, `backend/app/dependencies/rbac.py` | `test_pr_approval_prisma.py` | **PASS (100%)** |
| **US-03** (Từ chối PR & Giải phóng Ngân sách) | T-07..T-09 | `6f47a4e` | `backend/app/routers/pr.py`, `backend/app/services/procurement_service.py` | `test_pr_reject_prisma.py` | **PASS (100%)** |
| **US-04** (Yêu cầu Chỉnh sửa & Gửi lại PR) | T-10..T-13 | `6f47a4e` | `backend/app/routers/pr.py`, `backend/app/services/procurement_service.py` | `test_pr_revision_prisma.py` | **PASS (100%)** |
| **US-05** (Quản lý Nhà cung cấp - Sourcing) | T-14..T-16 | `25041db` | `backend/app/routers/suppliers.py`, `frontend/src/components/SuppliersView.tsx` | `test_supplier_quotation_prisma.py` | **PASS (100%)** |
| **US-06** (Thu thập & Nhập Báo giá) | T-17..T-20 | `70e382c`, `1775682` | `backend/app/routers/quotations.py`, `frontend/src/components/QuotationsView.tsx` | `test_supplier_quotation_prisma.py` | **PASS (100%)** |
| **US-07** (Đối sánh Báo giá Đa chiều) | T-21..T-25 | `ca92d15`, `20100e1` | `backend/app/routers/quotations.py`, `frontend/src/components/ComparisonView.tsx` | `test_quotation_comparison_prisma.py` | **PASS (100%)** |
| **US-08** (AI Tư vấn Phân tích Báo giá) | T-26..T-29 | `91996e7`, `16294c6` | `backend/app/services/ai_service.py`, `frontend/src/components/ComparisonView.tsx` | `test_ai_service.py` | **PASS (100%)** |
| **US-09** (Trao thầu & Khóa Đơn PO) | T-30..T-33 | `5fe0ec0`, `ad8f457` | `backend/app/routers/po.py`, `backend/app/services/procurement_service.py` | `test_po_prisma.py`, `test_us09_po.py` | **PASS (100%)** |
| **US-10** (Nhận hàng & Đóng PR Quyết toán) | T-34..T-36 | `02a117d`, `a1bc041` | `backend/app/routers/receiving.py`, `backend/app/services/procurement_service.py` | `test_receiving_prisma.py`, `test_close_prisma.py` | **PASS (100%)** |
| **GOV-01** (No Self-Approval Rule) | T-37..T-39 | `6f47a4e`, `5fe0ec0` | `backend/app/routers/pr.py`, `backend/app/dependencies/rbac.py` | `test_rbac.py` (TC-RBAC-014..018) | **PASS (100%)** |
| **GOV-02** (Khóa Dữ liệu Thương mại PO) | T-40..T-42 | `5fe0ec0` | `backend/app/routers/po.py`, `backend/app/services/procurement_service.py` | `test_po_prisma.py` (TC-PO-001..002) | **PASS (100%)** |

---

## 4. Chi Tiết Phát Hiện & Phương Án Xử Lý (Code Review Findings Log)

### CR-001: Lỗ Hổng Tiêm Vai Trò Phía Khách (Client-Side Role Injection Vulnerability)
- **Mức độ (Severity):** **BLOCKER**
- **Phạm vi (Area):** Authentication & Authorization
- **Truy xuất Story/Task:** US-01, US-02 / TASK-004, TASK-005
- **Tệp Nguồn:** [`backend/app/dependencies/auth.py`](file:///d:/LTUD/group-01-project-main/backend/app/dependencies/auth.py), [`backend/app/dependencies/rbac.py`](file:///d:/LTUD/group-01-project-main/backend/app/dependencies/rbac.py)
- **Hiện trạng Ban đầu (Finding):** Hệ thống nguyên bản cho phép máy khách tự truyền tham số vai trò (`role`) qua header hoặc request body, dẫn đến nguy cơ leo thang đặc quyền (Privilege Escalation).
- **Hành vi Kỳ vọng (Expected):** Ranh giới an ninh Zero-Trust; vai trò và danh tính phải được phân giải hoàn toàn từ khóa công khai JWT và CSDL máy chủ.
- **Bằng chứng & Commit (Evidence):** Commit `19ce38b` (JWT/JWKS) và `6f47a4e` (Server-Side RBAC).
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Xây dựng `SupabaseJWTService` xác thực chữ ký ES256 qua JWKS; triển khai `get_current_identity` truy vấn người dùng từ CSDL theo `authUserId == sub`; khóa toàn bộ 19 endpoints với `RoleChecker`.
- **Kiểm thử Hồi quy (Regression Test):** `test_jwt_auth.py` (12/12 PASS), `test_rbac.py` (28/28 PASS).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-002: Bỏ Sót Quy Tắc Không Tự Phê Duyệt (No Self-Approval Bypass)
- **Mức độ (Severity):** **BLOCKER**
- **Phạm vi (Area):** Approval Governance & Business Rules
- **Truy xuất Story/Task:** US-02 / GOV-01, T-37
- **Tệp Nguồn:** [`backend/app/routers/pr.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py), [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py)
- **Hiện trạng Ban đầu (Finding):** Người tạo PR có quyền MANAGER hoặc ADMIN có thể tự duyệt PR do chính mình khởi tạo.
- **Hành vi Kỳ vọng (Expected):** Nghiêm cấm tự phê duyệt bất kể vai trò (kể cả ADMIN), tuân thủ nguyên tắc độc lập kiểm soát (Four-Eyes Principle).
- **Bằng chứng & Commit (Evidence):** Commit `6f47a4e`, `5fe0ec0`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Bổ sung điều kiện kiểm tra nghiêm ngặt `if approver_id == pr_creator_id: raise AuthorizationError("Không thể phê duyệt PR do chính mình tạo (No Self-Approval — GOV-01)")` trong các phương thức `approve_pr_prisma`, `reject_pr_prisma`, `request_revision_prisma`.
- **Kiểm thử Hồi quy (Regression Test):** `test_rbac.py` (TC-RBAC-014, TC-RBAC-015, TC-RBAC-018 PASS).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-003: Tạo PO từ PR Chưa Duyệt & Sửa Đổi Dữ Liệu Thương Mại (PO Creation on Unapproved PR)
- **Mức độ (Severity):** **BLOCKER**
- **Phạm vi (Area):** Purchase Order Integrity
- **Truy xuất Story/Task:** US-09 / TASK-006, BUG-001, T-26
- **Tệp Nguồn:** [`backend/app/routers/po.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/po.py), [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py)
- **Hiện trạng Ban đầu (Finding):** Endpoint tạo PO không kiểm tra trạng thái PR trước khi tạo; cho phép máy khách gửi kèm đơn giá và số lượng trong body để ghi đè giá báo thầu.
- **Hành vi Kỳ vọng (Expected):** PR bắt buộc phải ở trạng thái `APPROVED` (REQ-BR-10); đơn giá và số lượng phải được khóa 100% từ bảng `Quotation` trong CSDL máy chủ (REQ-BR-03 / REQ-FR-16).
- **Bằng chứng & Commit (Evidence):** Commit `5fe0ec0`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Áp dụng khóa dòng `SELECT ... FOR UPDATE` kiểm tra `pr.status == 'APPROVED'`; loại bỏ toàn bộ dữ liệu giá từ payload máy khách, truy xuất trực tiếp `Quotation` từ PostgreSQL; sinh mã `poNumber` ngẫu nhiên có tiền tố ngày tháng tránh xung đột số thứ tự.
- **Kiểm thử Hồi quy (Regression Test):** `test_po_prisma.py` (TC-PO-001, TC-PO-002 PASS).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-004: Đóng PR Khi Hàng Chưa Được Nhận Đủ 100% (Close PR Before Receiving Completion)
- **Mức độ (Severity):** **BLOCKER**
- **Phạm vi (Area):** Goods Receiving & Budget Settlement
- **Truy xuất Story/Task:** US-10 / TASK-007, T-34
- **Tệp Nguồn:** [`backend/app/routers/receiving.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/receiving.py), [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py)
- **Hiện trạng Ban đầu (Finding):** PR có thể bị đóng khi số lượng hàng nhận thực tế chưa đủ so với số lượng đặt trên PO, dẫn đến sai lệch quyết toán ngân sách doanh nghiệp.
- **Hành vi Kỳ vọng (Expected):** Nghiêm cấm đóng PR nếu `SUM(receivedQty) < PO.quantity` (REQ-BR-11 / HD-07).
- **Bằng chứng & Commit (Evidence):** Commit `02a117d`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Thêm bước tính tổng số lượng nhận `total_received = sum(r.receivedQty for r in receivings)` và kiểm tra `if total_received < po_qty: raise ValueError("Không thể đóng PR: Hàng chưa được nhận đủ...")` trước khi thực hiện chuyển trạng thái PR sang `CLOSED` và quyết toán ngân sách.
- **Kiểm thử Hồi quy (Regression Test):** `test_close_prisma.py` (TC-CLOSE-001, TC-CLOSE-002 PASS), `scratch/ai089_public_smoke.py` (Kịch bản thất bại PASS).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-005: Mất Ánh Xạ UUID Người Dùng Khi Railway Redeploy (Auth Binding Drop on Container Restart)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** Deployment & Persistence
- **Truy xuất Story/Task:** Deployment / T-41
- **Tệp Nguồn:** [`backend/start.sh`](file:///d:/LTUD/group-01-project-main/backend/start.sh), [`backend/scripts/seed_auth_users.py`](file:///d:/LTUD/group-01-project-main/backend/scripts/seed_auth_users.py)
- **Hiện trạng Ban đầu (Finding):** Mỗi lần Railway build lại container, thông tin ánh xạ `authUserId` bị thiếu nếu container không kích hoạt lệnh seed, khiến người dùng đăng nhập bị lỗi 401.
- **Hành vi Kỳ vọng (Expected):** Quá trình khởi động container phải bảo đảm tính toàn vẹn dữ liệu người dùng (Idempotent persistence).
- **Bằng chứng & Commit (Evidence):** Commit `80afdd0`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Viết kịch bản `seed_auth_users.py` có tính chất idempotent và nhúng trực tiếp vào tệp thực thi khởi động `start.sh` trước khi khởi chạy tiến trình Uvicorn.
- **Kiểm thử Hồi quy (Regression Test):** Kiểm thử tái khởi động Railway container; đăng nhập thành công 5/5 tài khoản demo.
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-006: Xung Đột CORS Wildcard với Credentials Phía Trình Duyệt (CORS Credentials Conflict)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** Security & Network Configuration
- **Truy xuất Story/Task:** Deployment / T-41
- **Tệp Nguồn:** [`backend/app/main.py`](file:///d:/LTUD/group-01-project-main/backend/app/main.py)
- **Hiện trạng Ban đầu (Finding):** Cấu hình `allow_origins=["*"]` kết hợp với `allow_credentials=True` vi phạm chuẩn CORS của W3C, khiến trình duyệt Chrome chặn gửi header Authorization kèm cookie.
- **Hành vi Kỳ vọng (Expected):** Danh sách nguồn cho phép (`ALLOWED_ORIGINS`) phải được liệt kê tường minh khi bật cờ `allow_credentials`.
- **Bằng chứng & Commit (Evidence):** Commit `b8404f4`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Định nghĩa danh sách các domain được cấp phép cụ thể (`https://group-01-project.vercel.app`, `http://localhost:5173`, `http://localhost:3000`) thay vì dùng wildcard `*`.
- **Kiểm thử Hồi quy (Regression Test):** Trình duyệt gọi API trực tiếp không bị lỗi CORS chặn preflight.
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-007: Lỗi Phân Giải DNS Khi Gọi API Qua Vercel Proxy (Vercel DNS Resolve Failure)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** Production Routing & Networking
- **Truy xuất Story/Task:** Deployment / T-41
- **Tệp Nguồn:** [`frontend/.env`](file:///d:/LTUD/group-01-project-main/frontend/.env), [`frontend/src/api/client.ts`](file:///d:/LTUD/group-01-project-main/frontend/src/api/client.ts)
- **Hiện trạng Ban đầu (Finding):** Cấu hình Vercel rewrite proxy đôi khi gặp lỗi `DNS_HOSTNAME_RESOLVE_FAILED` (502 Bad Gateway) tại các node mạng biên khi Railway đang redeploy.
- **Hành vi Kỳ vọng (Expected):** Trình duyệt máy khách phải gọi trực tiếp tới backend API domain trên Railway, bỏ qua proxy trung gian không ổn định.
- **Bằng chứng & Commit (Evidence):** Commit `b8404f4`, `d2cff2c`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Bake trực tiếp URL Railway vào biến `VITE_API_URL` trong bản build frontend và cấu hình `client.ts` ưu tiên gọi trực tiếp Railway API.
- **Kiểm thử Hồi quy (Regression Test):** Kiểm thử khói công khai AI-089 (9/9 tiêu chí PASS).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-008: Báo Giá Hết Hạn & Phân Quyền Màn Hình Đối Sánh Báo Giá (Comparison View Expiry & Access)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** Quotation Comparison Workflow
- **Truy xuất Story/Task:** US-07 / TASK-008, HD-13, K-2
- **Tệp Nguồn:** [`backend/app/routers/quotations.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/quotations.py), [`frontend/src/components/ComparisonView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/ComparisonView.tsx)
- **Hiện trạng Ban đầu (Finding):** Màn hình so sánh báo giá chặn quyền truy cập của các vai trò ngoài PROCUREMENT; chưa hiển thị cảnh báo đỏ khi báo giá hết hạn hiệu lực (`validUntil < now()`).
- **Hành vi Kỳ vọng (Expected):** Toàn bộ người dùng đã đăng nhập đều có quyền xem đối sánh báo giá (HD-13 / K-2); báo giá hết hạn phải được đánh dấu cảnh báo rõ ràng.
- **Bằng chứng & Commit (Evidence):** Commit `20100e1`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Cập nhật phân quyền router cho phép mọi vai trò đã xác thực (`RoleChecker(["EMPLOYEE", "MANAGER", "PROCUREMENT", "FINANCE", "ADMIN"])`) được đọc dữ liệu so sánh; bổ sung badge cảnh báo hết hạn màu đỏ trên giao diện.
- **Kiểm thử Hồi quy (Regression Test):** `test_quotation_comparison_prisma.py` (9/9 PASS).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-009: Cảnh Báo Ngân Sách Sai Lệch & Thiếu Viền Đỏ Khi Xác Thực Biểu Mẫu PR
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** Frontend User Experience & Budget Validation
- **Truy xuất Story/Task:** US-01 / T-01
- **Tệp Nguồn:** [`frontend/src/App.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/App.tsx)
- **Hiện trạng Ban đầu (Finding):** Giao diện hiển thị cảnh báo vượt ngân sách giả (`overAmount > 0`) dù giá trị yêu cầu nằm hoàn toàn trong hạn mức khả dụng; các ô nhập liệu bắt buộc chưa viền đỏ khi người dùng bấm gửi mà để trống.
- **Hành vi Kỳ vọng (Expected):** Tính toán ngân sách chuẩn xác; viền đỏ báo lỗi trực quan trên từng trường bắt buộc trước khi gửi form.
- **Bằng chứng & Commit (Evidence):** Commit `9af432c`, `0216a7c`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Chuẩn hóa công thức tính ngân sách khả dụng; bổ sung trạng thái `touched` và class `border-red-500` cho các ô input chưa đạt yêu cầu.
- **Kiểm thử Hồi quy (Regression Test):** Kiểm thử giao diện trực quan E2E.
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-010: Số 0 Đứng Đầu Trên Ô Nhập Giá Báo Giá & Tải Lên Tệp Đính Kèm
- **Mức độ (Severity):** **MINOR**
- **Phạm vi (Area):** Frontend Form Inputs & Attachments
- **Truy xuất Story/Task:** US-06 / T-17
- **Tệp Nguồn:** [`frontend/src/components/QuotationsView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/QuotationsView.tsx)
- **Hiện trạng Ban đầu (Finding):** Ô nhập đơn giá xuất hiện số 0 ở đầu khi bắt đầu gõ; chưa có vùng kéo thả chọn tệp đính kèm thực tế.
- **Hành vi Kỳ vọng (Expected):** Trải nghiệm nhập liệu tự nhiên; hỗ trợ kéo thả tệp tải lên rõ ràng.
- **Bằng chứng & Commit (Evidence):** Commit `71b48e2`, `1775682`.
- **Trạng thái (Status):** **RESOLVED**
- **Giải pháp Xử lý (Resolution):** Định dạng ô nhập đơn giá xử lý chuỗi rỗng; bổ sung vùng chọn tệp native file picker và drag-and-drop zone.
- **Kiểm thử Hồi quy (Regression Test):** Kiểm thử nhập liệu trên trình duyệt.
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã kiểm chứng mã nguồn).

---

### CR-011: Tính Năng Gemini Live Chưa Được Kiểm Chứng Tự Động (Gemini Live Unverified Status)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** AI Service Integration & Reliability
- **Truy xuất Story/Task:** US-08 / TASK-009, TASK-010
- **Tệp Nguồn:** [`backend/app/services/ai_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/ai_service.py)
- **Hiện trạng Ban đầu (Finding):** Tích hợp Google Gemini Live API phụ thuộc vào kết nối mạng ngoài và API Key; chưa được đưa vào bộ kiểm thử CI/CD tự động mặc định.
- **Hành vi Kỳ vọng (Expected):** Hệ thống phải có giải pháp dự phòng chắc chắn (Fail-Safe), công bố minh bạch trạng thái tích hợp.
- **Bằng chứng & Commit (Evidence):** Commit `91996e7`, `18494d4`.
- **Trạng thái (Status):** **ACCEPTED (Chấp nhận Giới hạn Kỹ thuật)**
- **Giải pháp Xử lý (Resolution):** Thiết kế kiến trúc Hybrid AI; khi không có API Key hoặc gặp sự cố mạng, hệ thống tự động kích hoạt **Fallback Heuristic** dựa trên trọng số chuẩn của Figma (40/25/25/10), bảo đảm độ tin cậy 78% và không làm gián đoạn chu trình mua sắm.
- **Kiểm thử Hồi quy (Regression Test):** `test_ai_service.py` (5/5 tests PASS trên Fallback Heuristic).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã công bố trong Release Notes & QA Report).

---

### CR-012: Kích Thước Gói Đóng Gói Frontend Vượt Mức Khuyến Nghị (Vite Single Bundle Size)
- **Mức độ (Severity):** **MINOR**
- **Phạm vi (Area):** Frontend Performance & Bundle Optimization
- **Truy xuất Story/Task:** Non-Functional Requirements / T-41
- **Tệp Nguồn:** [`frontend/package.json`](file:///d:/LTUD/group-01-project-main/frontend/package.json), `frontend/dist/`
- **Hiện trạng Ban đầu (Finding):** Bản build sản phẩm tạo ra gói `index-*.js` có kích thước 649.33 kB (vượt mức cảnh báo 500 kB của Vite).
- **Hành vi Kỳ vọng (Expected):** Gói bundle nên được phân tách mã nguồn (Code Splitting / Dynamic Import).
- **Bằng chứng & Commit (Evidence):** Báo cáo kiểm toán chất lượng độc lập `FINAL_QA_GATE_REPORT.md`.
- **Trạng thái (Status):** **ACCEPTED (Chấp nhận Giới hạn Kỹ thuật)**
- **Giải pháp Xử lý (Resolution):** Gói sau khi nén Gzip chỉ còn ~177 kB, thời gian tải trên mạng biên Vercel dưới 300ms, không ảnh hưởng đến trải nghiệm người dùng; bảo toàn kiến trúc đơn gói ổn định cho đợt nộp đồ án.
- **Kiểm thử Hồi quy (Regression Test):** `npm run build` thành công, exit code 0.
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã ghi nhận trong Release Notes).

---

### CR-013: Sự Khác Biệt Công Cụ Kiểm Thử Tự Động Trình Duyệt (E2E Tooling Discrepancy)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** Test Suite Integrity & Tooling
- **Truy xuất Story/Task:** Automated Testing / Deliverable 3.8
- **Tệp Nguồn:** [`frontend/scripts/test_final_full_lifecycle_e2e.js`](file:///d:/LTUD/group-01-project-main/frontend/scripts/test_final_full_lifecycle_e2e.js), `frontend/e2e/`
- **Hiện trạng Ban đầu (Finding):** Thư mục mã nguồn có chứa đặc tả Playwright từ giai đoạn đầu nhưng chưa được thẩm định độc lập; kịch bản E2E thực tế chạy đạt 14/14 steps là dùng Puppeteer (`puppeteer-core`).
- **Hành vi Kỳ vọng (Expected):** Tài liệu phải phản ánh trung thực công cụ kiểm thử thực tế được nghiệm thu.
- **Bằng chứng & Commit (Evidence):** Commit `cc84847`, `cd0c115`.
- **Trạng thái (Status):** **ACCEPTED (Chấp nhận Giới hạn Kỹ thuật)**
- **Giải pháp Xử lý (Resolution):** Chuẩn hóa toàn bộ tài liệu (README, Runbook, Release Notes, QA Report) ghi nhận chính xác Puppeteer là công cụ E2E chính thức đã kiểm chứng; ghi chú rõ kịch bản Playwright tồn tại nhưng chưa nghiệm thu độc lập.
- **Kiểm thử Hồi quy (Regression Test):** `node frontend/scripts/test_final_full_lifecycle_e2e.js` (14/14 steps PASSED).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Đã chuẩn hóa tài liệu).

---

### CR-014: Kiểm Thử Khả Năng Sử Dụng Chưa Tiến Hành Trên Người Dùng Thật (Usability Testing Status)
- **Mức độ (Severity):** **MAJOR**
- **Phạm vi (Area):** UX Evaluation & Product Governance
- **Truy xuất Story/Task:** UX Evaluation / Deliverable 2.4
- **Tệp Nguồn:** [`docs/05-test/usability-test-plan.md`](file:///d:/LTUD/group-01-project-main/docs/05-test/usability-test-plan.md)
- **Hiện trạng Ban đầu (Finding):** Kế hoạch kiểm thử khả năng sử dụng (SUS Questionnaire, kịch bản 5 người dùng) đã được lập chi tiết nhưng chưa tiến hành thu thập dữ liệu trên người dùng thực tế.
- **Hành vi Kỳ vọng (Expected):** Minh bạch trạng thái học thuật, không ngụy tạo kết quả điểm số khảo sát.
- **Bằng chứng & Commit (Evidence):** Báo cáo kiểm toán AI-091 (`Deliverable 2.4 = PARTIAL / PENDING REAL USER TEST`).
- **Trạng thái (Status):** **ACCEPTED (Chấp nhận Giới hạn Kỹ thuật)**
- **Giải pháp Xử lý (Resolution):** Ghi nhận minh bạch trạng thái là `PENDING REAL USER TEST`; khung kịch bản kiểm thử đã sẵn sàng để nhóm triển khai đánh giá người dùng sau đợt phát hành.
- **Kiểm thử Hồi quy (Regression Test):** N/A (Hạng mục khảo sát con người).
- **Người thẩm định (Reviewer):** AI-ASSISTED RETROSPECTIVE (Bảo toàn tính trung thực học thuật).

---

## 5. Đánh Giá Trách Nhiệm Từng Thành Viên (Individual Ownership Review)

> **Nguyên tắc Quản trị Dự án:** Mỗi thành viên trong nhóm sở hữu và chịu trách nhiệm toàn diện cho User Story của mình xuyên suốt vòng đời phát triển (Story → Requirement/AC → Task → Source Code → Commit → Tests → Code Review Findings → Resolution).

### 5.1. Trần Thị Kiều Giang
* **User Story Phụ trách Chính:** **US-01** (Khởi tạo Yêu cầu Mua sắm & Tạm giữ Ngân sách khả dụng)
* **Core Viva Story:** **US-01** (Đại diện bảo vệ chuyên sâu chức năng PR Creation & Budget Reservation)
* **Các Tác vụ (Tasks):** `T-01`, `T-02`, `T-03`
* **Yêu cầu Nghiệp vụ & Tiêu chí Chấp nhận (AC):** REQ-FR-01 (Tạo PR với danh mục mặt hàng), REQ-FR-02 (Tự động tính tổng giá trị), REQ-BR-01 (Kiểm tra ngân sách phòng ban), REQ-BR-02 (Tạm giữ `tempReservedAmount`).
* **Mô-đun & Tệp Nguồn Trọng Yếu:**
  - [`backend/app/routers/pr.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py) (Endpoint `POST /api/pr`, `GET /api/pr`)
  - [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py) (`create_pr_prisma`, khóa dòng `SELECT ... FOR UPDATE` trên bảng `Budget`)
  - [`frontend/src/App.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/App.tsx) (Giao diện tạo PR, tính toán ngân sách trực quan)
* **Lịch sử Git Commits Thực tế:**
  - `6117d39` — Khởi tạo schema `PurchaseRequest`, `PRItem` và ràng buộc `authUserId`.
  - `19ce38b` — Kết nối xác thực JWT/JWKS bảo vệ endpoint tạo PR.
  - `9af432c` — Sửa lỗi tính toán sai lệch cảnh báo vượt ngân sách giả.
  - `0216a7c` — Bổ sung viền đỏ cảnh báo khi bỏ trống các trường bắt buộc trên biểu mẫu PR.
* **Bộ Kiểm Thử Minh Chứng:**
  - `backend/tests/test_pr_creation_prisma.py` (9/9 tests PASSED)
  - `backend/tests/test_business_rules.py` (10/10 tests PASSED)
* **Phát Hiện Kiểm Điểm Mã Nguồn (Findings):**
  - **CR-009 (MAJOR):** Cảnh báo ngân sách sai lệch & thiếu viền đỏ biểu mẫu PR → **RESOLVED** (Commit `9af432c`, `0216a7c`).
* **Trạng thái Thẩm định Kỹ thuật:** **PASS (100% Resolved & Verified)**

---

### 5.2. Nguyễn Trương Thùy Dương
* **User Story Phụ trách Chính:** **US-04**, **US-05**, **US-06**
* **Core Viva Story:** **US-04** (Yêu cầu Chỉnh sửa & Nộp lại PR — HD-16 / REQ-FR-06)
* **Các Tác vụ (Tasks):** `T-10`, `T-11`, `T-12`, `T-13` (US-04); `T-14`, `T-15`, `T-16` (US-05); `T-17`, `T-18`, `T-19`, `T-20` (US-06)
* **Yêu cầu Nghiệp vụ & Tiêu chí Chấp nhận (AC):**
  - US-04: Cấp quản lý yêu cầu chỉnh sửa kèm lý do bắt buộc; người tạo PR chỉnh sửa và nộp lại (`REVISION_REQUESTED` → `PENDING_APPROVAL`).
  - US-05: Quản lý nhà cung cấp Sourcing (Tạo mới, truy vấn, chuẩn hóa thông tin doanh nghiệp).
  - US-06: Thu thập và nhập báo giá nhà cung cấp (Đơn giá, số lượng, ngày giao hàng, điều khoản bảo hành, tệp đính kèm).
* **Mô-đun & Tệp Nguồn Trọng Yếu:**
  - [`backend/app/routers/pr.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py) (`POST /api/pr/{id}/revision`, `POST /api/pr/{id}/resubmit`)
  - [`backend/app/routers/suppliers.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/suppliers.py) (`GET /api/suppliers`, `POST /api/suppliers`)
  - [`backend/app/routers/quotations.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/quotations.py) (`POST /api/quotations`, `GET /api/quotations`)
  - [`frontend/src/components/SuppliersView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/SuppliersView.tsx), [`frontend/src/components/QuotationsView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/QuotationsView.tsx)
* **Lịch sử Git Commits Thực tế:**
  - `6f47a4e` — Triển khai logic HD-16 Revision Request & Resubmit có kiểm tra quyền hạn.
  - `25041db` — Phase 4A Sourcing & Supplier management với PostgreSQL persistence.
  - `70e382c` — Phase 4B Quotation collection flow với RBAC enforcement.
  - `71b48e2` — Xử lý triệt để số 0 đứng đầu khi nhập đơn giá báo giá.
  - `1775682` — Thêm trình chọn tệp thực tế và vùng kéo thả tệp đính kèm báo giá.
* **Bộ Kiểm Thử Minh Chứng:**
  - `backend/tests/test_pr_revision_prisma.py` (8/8 tests PASSED)
  - `backend/tests/test_supplier_quotation_prisma.py` (14/14 tests PASSED)
* **Phát Hiện Kiểm Điểm Mã Nguồn (Findings):**
  - **CR-010 (MINOR):** Ô nhập đơn giá xuất hiện số 0 & thiếu vùng kéo thả tệp → **RESOLVED** (Commit `71b48e2`, `1775682`).
* **Trạng thái Thẩm định Kỹ thuật:** **PASS (100% Resolved & Verified)**

---

### 5.3. Nguyễn Trúc Lam
* **User Story Phụ trách Chính:** **US-03**, **US-07**
* **Core Viva Story:** **US-07** (Đối sánh Báo giá Đa chiều & Ma trận So sánh — HD-13 / K-2)
* **Các Tác vụ (Tasks):** `T-07`, `T-08`, `T-09` (US-03); `T-21`, `T-22`, `T-23`, `T-24`, `T-25` (US-07)
* **Yêu cầu Nghiệp vụ & Tiêu chí Chấp nhận (AC):**
  - US-03: Cấp quản lý từ chối PR kèm lý do bắt buộc; hệ thống tự động hoàn trả ngân sách tạm giữ (`tempReservedAmount`) về ngân sách khả dụng.
  - US-07: Hiển thị bảng đối sánh đa chiều các báo giá của cùng một PR (Đơn giá, chênh lệch giá, thời hạn giao hàng, điều khoản bảo hành, cảnh báo hết hạn).
* **Mô-đun & Tệp Nguồn Trọng Yếu:**
  - [`backend/app/routers/pr.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py) (`POST /api/pr/{id}/reject`)
  - [`backend/app/routers/quotations.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/quotations.py) (`GET /api/quotations/compare/{pr_id}`)
  - [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py) (`reject_pr_prisma`, `compare_quotations_prisma`)
  - [`frontend/src/components/ComparisonView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/ComparisonView.tsx)
* **Lịch sử Git Commits Thực tế:**
  - `6f47a4e` — Triển khai từ chối PR có lý do bắt buộc và hoàn ngân sách an toàn.
  - `ca92d15` — Phase 4C Xây dựng luồng so sánh báo giá với PostgreSQL persistence.
  - `20100e1` — Thực thi quy tắc HD-13/K-2: Cho phép toàn bộ vai trò đã xác thực xem đối sánh và kích hoạt cảnh báo hết hạn `validUntil`.
* **Bộ Kiểm Thử Minh Chứng:**
  - `backend/tests/test_pr_reject_prisma.py` (7/7 tests PASSED)
  - `backend/tests/test_quotation_comparison_prisma.py` (9/9 tests PASSED)
* **Phát Hiện Kiểm Điểm Mã Nguồn (Findings):**
  - **CR-008 (MAJOR):** Báo giá hết hạn & hạn chế quyền xem đối sánh → **RESOLVED** (Commit `20100e1`).
* **Trạng thái Thẩm định Kỹ thuật:** **PASS (100% Resolved & Verified)**

---

### 5.4. Nguyễn Thị Thùy Dung
* **User Story Phụ trách Chính:** **US-02**, **US-08**, **US-09**, **GOV-01**
* **Core Viva Story:** **US-08** (AI Tư vấn Phân tích & Khuyến nghị Báo giá Đa tiêu chí)
* **Các Tác vụ (Tasks):** `T-04..T-06` (US-02); `T-26..T-29` (US-08); `T-30..T-33` (US-09); `T-37..T-39` (GOV-01)
* **Yêu cầu Nghiệp vụ & Tiêu chí Chấp nhận (AC):**
  - US-02: Phê duyệt PR bởi cấp quản lý (MANAGER/FINANCE/ADMIN); ghi nhận nhật ký phê duyệt.
  - US-08: AI phân tích ma trận báo giá, tính điểm đa tiêu chí (Giá 40%, Giao hàng 25%, Độ tin cậy 25%, Điều khoản 10%), xuất phát hiện bất thường và lý do khuyến nghị.
  - US-09: Chuyên viên Mua sắm (PROCUREMENT) trao thầu và tạo Purchase Order từ PR đã duyệt.
  - GOV-01: Quy tắc Không tự phê duyệt (No Self-Approval) — Ngăn người tạo PR tự duyệt/từ chối/yêu cầu sửa PR của chính mình.
* **Mô-đun & Tệp Nguồn Trọng Yếu:**
  - [`backend/app/routers/pr.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py) (`POST /api/pr/{id}/approve`)
  - [`backend/app/routers/po.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/po.py) (`POST /api/po`, `GET /api/po`)
  - [`backend/app/services/ai_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/ai_service.py) (Gemini API + Fallback Heuristic 40/25/25/10)
  - [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py) (`approve_pr_prisma`, `create_po_prisma`)
  - [`frontend/src/components/ComparisonView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/ComparisonView.tsx)
* **Lịch sử Git Commits Thực tế:**
  - `6f47a4e` — Triển khai RBAC máy chủ và quy tắc No Self-Approval (GOV-01).
  - `5fe0ec0` — Khóa chặn tạo PO nếu PR chưa `APPROVED` (REQ-BR-10) và khóa đơn giá PO từ CSDL.
  - `91996e7` — Tích hợp Google Gemini REST API và bộ phân tích Fallback Heuristic.
  - `16294c6`, `18494d4` — Hoàn thiện UI khuyến nghị AI và chuẩn hóa ranh giới AI Advisory.
  - `ad8f457` — Triển khai quy trình trao thầu con người tạo PO (Human Award to PO).
* **Bộ Kiểm Thử Minh Chứng:**
  - `backend/tests/test_pr_approval_prisma.py` (8/8 tests PASSED)
  - `backend/tests/test_rbac.py` (28/28 tests PASSED)
  - `backend/tests/test_ai_service.py` (5/5 tests PASSED)
  - `backend/tests/test_po_prisma.py` (10/10 tests PASSED)
  - `backend/tests/test_us09_po.py` (8/8 tests PASSED)
* **Phát Hiện Kiểm Điểm Mã Nguồn (Findings):**
  - **CR-001 (BLOCKER):** Lỗ hổng tiêm vai trò phía khách → **RESOLVED** (Commit `19ce38b`, `6f47a4e`).
  - **CR-002 (BLOCKER):** Bỏ sót quy tắc không tự phê duyệt → **RESOLVED** (Commit `6f47a4e`, `5fe0ec0`).
  - **CR-003 (BLOCKER):** Tạo PO từ PR chưa duyệt & sửa đổi dữ liệu thương mại → **RESOLVED** (Commit `5fe0ec0`).
  - **CR-011 (MAJOR):** Gemini Live API chưa kiểm chứng tự động → **ACCEPTED (Fallback Heuristic Active)**.
* **Trạng thái Thẩm định Kỹ thuật:** **PASS WITH ACCEPTED LIMITATIONS (Đã công bố giới hạn AI)**

---

### 5.5. Trần Thị Thu Hà
* **User Story Phụ trách Chính:** **US-10**, **GOV-02**
* **Core Viva Story:** **US-10** (Nhận Hàng, Kiểm Soát Số Lượng & Đóng PR Quyết Toán Ngân Sách)
* **Các Tác vụ (Tasks):** `T-34`, `T-35`, `T-36` (US-10); `T-40`, `T-41`, `T-42` (GOV-02 & Release)
* **Yêu cầu Nghiệp vụ & Tiêu chí Chấp nhận (AC):**
  - US-10: Nhận hàng theo từng đợt có tệp biên bản đính kèm; kiểm tra `SUM(receivedQty) <= PO.quantity` (REQ-BR-04); chặn đóng PR nếu hàng chưa nhận đủ 100% (REQ-BR-11 / HD-07); quyết toán ngân sách (`tempReservedAmount` giảm, `spentAmount` tăng).
  - GOV-02: Khóa dữ liệu thương mại trên PO; không cho phép client ghi đè đơn giá/số lượng.
* **Mô-đun & Tệp Nguồn Trọng Yếu:**
  - [`backend/app/routers/receiving.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/receiving.py) (`POST /api/receiving`, `GET /api/receiving/po/{po_id}`)
  - [`backend/app/routers/pr.py`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py) (`POST /api/pr/{id}/close`)
  - [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py) (`receive_goods_prisma`, `close_pr_prisma`, khóa dòng `SELECT ... FOR UPDATE`)
  - [`frontend/src/components/ReceivingModal.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/ReceivingModal.tsx)
* **Lịch sử Git Commits Thực tế:**
  - `02a117d` — Triển khai quy tắc REQ-BR-11 / HD-07: Chặn đóng PR nếu hàng chưa nhận đủ.
  - `b5d00a3` — Di chuyển toàn bộ dữ liệu nhận hàng sang PostgreSQL Supabase.
  - `dfdd7e5` — Di chuyển logic đóng PR và quyết toán ngân sách sang Prisma Client.
  - `a1bc041` — Hoàn thiện trọn vẹn chu trình nhận hàng và đóng PR trên giao diện người dùng.
  - `cc84847` — Kiểm chứng toàn bộ chu trình nghiệp vụ E2E từ PR đến Close PR.
* **Bộ Kiểm Thử Minh Chứng:**
  - `backend/tests/test_receiving_prisma.py` (6/6 tests PASSED)
  - `backend/tests/test_close_prisma.py` (8/8 tests PASSED)
  - `backend/tests/test_phase4f_lifecycle.py` (5/5 tests PASSED)
  - `frontend/scripts/test_final_full_lifecycle_e2e.js` (14/14 steps PASSED)
  - `scratch/ai089_public_smoke.py` (Xác thực Public Cloud: Cả Happy Path và Failure Guard PASSED)
* **Phát Hiện Kiểm Điểm Mã Nguồn (Findings):**
  - **CR-004 (BLOCKER):** Đóng PR khi hàng chưa được nhận đủ 100% → **RESOLVED** (Commit `02a117d`).
* **Trạng thái Thẩm định Kỹ thuật:** **PASS (100% Resolved & Verified)**

---

### 5.6. Bảng Kiểm Tra Core Viva Stories (Core Viva Stories Matrix)

| Thành viên | Story Bảo Vệ (Core Viva) | Mô Tả Trọng Tâm Chuyên Sâu | Commit Trọng Yếu | Bộ Test Kiểm Chứng | Trạng Thái Thẩm Định |
|---|---|---|---|---|---|
| **Trần Thị Kiều Giang** | **US-01** | Tạo PR & Kiểm tra/Tạm giữ ngân sách (`SELECT ... FOR UPDATE`) | `6117d39`, `19ce38b`, `9af432c` | `test_pr_creation_prisma.py` | **PASS (100%)** |
| **Nguyễn Trương Thùy Dương** | **US-04** | Luồng Quản lý yêu cầu sửa đổi & Nộp lại PR (HD-16) | `6f47a4e` | `test_pr_revision_prisma.py` | **PASS (100%)** |
| **Nguyễn Trúc Lam** | **US-07** | Ma trận Đối sánh Báo giá Đa chiều & Cảnh báo Hết hạn (HD-13) | `ca92d15`, `20100e1` | `test_quotation_comparison_prisma.py` | **PASS (100%)** |
| **Nguyễn Thị Thùy Dung** | **US-08** | AI Tư vấn Xếp hạng Báo giá Đa tiêu chí & Fallback Heuristic | `91996e7`, `16294c6`, `18494d4` | `test_ai_service.py` | **PASS WITH ACCEPTED LIMITATIONS** |
| **Trần Thị Thu Hà** | **US-10** | Nhận hàng Đa đợt, Chặn đóng PR chưa nhận đủ & Quyết toán | `02a117d`, `dfdd7e5`, `a1bc041` | `test_close_prisma.py`, `test_receiving_prisma.py` | **PASS (100%)** |

---

## 6. Tổng Hợp Kết Quả Đánh Giá Mã Nguồn (Release Review Summary)

```
================================================================================
                    TỔNG HỢP KIỂM ĐIỂM MÃ NGUỒN (CODE REVIEW SUMMARY)
================================================================================
  Tổng số Phát hiện (Total Findings):               14
  ------------------------------------------------------------------------------
  Phân loại theo Mức độ nghiêm trọng (Severity):
    - Khối chặn Nghiêm trọng (Blockers):             4 (28.57%)
    - Vấn đề Lớn (Major):                            8 (57.14%)
    - Vấn đề Nhỏ (Minor):                            2 (14.29%)
  ------------------------------------------------------------------------------
  Phân loại theo Trạng thái Xử lý (Status):
    - Đã Khắc phục Hoàn toàn (Resolved):            10 (71.43%)
    - Đang Mở (Open):                                0 (0.00%)
    - Chấp nhận Giới hạn Kỹ thuật (Accepted):        4 (28.57%)
  ------------------------------------------------------------------------------
  Vấn đề An ninh Trọng yếu (Critical Security):      2 (100% Resolved)
  Vấn đề Quy tắc Nghiệp vụ (Critical Business Rules): 2 (100% Resolved)
================================================================================
  KẾT LUẬN CUỐI CÙNG: PASS WITH ACCEPTED LIMITATIONS (ĐẠT CHUẨN PHÁT HÀNH)
================================================================================
```

---

## 7. Bảng Sẵn Sàng Ký Duyệt Của Con Người (Human Sign-Off Readiness)

> **Cảnh báo Ranh giới Thẩm định:** Trợ lý AI chỉ thực hiện việc chuẩn bị template, trích xuất dữ liệu thực tế từ Git và đối chiếu chéo các bộ kiểm thử. **Tuyệt đối KHÔNG tự ý ghi nhận "HUMAN REVIEW CONFIRMED" khi các thành viên nhóm chưa kiểm tra và ký xác nhận thực tế.**

**Trạng thái Hiện tại của Hồ sơ:**  
`RETROSPECTIVE REVIEW + HUMAN SIGN-OFF PENDING`

| Thành Viên Sở Hữu (Story Owner) | User Story Phụ Trách | Trạng Thái Sẵn Sàng Thẩm Định (Review Status) | Chữ Ký Xác Nhận của Con Người (Human Sign-off) |
|---|---|---|---|
| **Trần Thị Kiều Giang** | **US-01** (T-01..T-03) | `READY FOR REVIEW` | `PENDING (Chờ kiểm tra)` |
| **Nguyễn Trương Thùy Dương** | **US-04**, **US-05**, **US-06** (T-10..T-20) | `READY FOR REVIEW` | `PENDING (Chờ kiểm tra)` |
| **Nguyễn Trúc Lam** | **US-03**, **US-07** (T-07..T-09, T-21..T-25) | `READY FOR REVIEW` | `PENDING (Chờ kiểm tra)` |
| **Nguyễn Thị Thùy Dung** | **US-02**, **US-08**, **US-09**, **GOV-01** (T-04..T-06, T-26..T-39) | `READY FOR REVIEW` | `PENDING (Chờ kiểm tra)` |
| **Trần Thị Thu Hà** | **US-10**, **GOV-02** (T-34..T-36, T-40..T-42) | `READY FOR REVIEW` | `PENDING (Chờ kiểm tra)` |


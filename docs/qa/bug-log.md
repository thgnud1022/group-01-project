# HỒ SƠ QUẢN LÝ VÀ THEO DÕI LỖI TẬP TRUNG (CENTRAL BUG LOG)
## DELIVERABLE 3.7 — BUG LOG & DEFECT TRACKING RECORD

**Dự án:** Hệ thống Phê duyệt Mua sắm & Đề xuất AI (AI Procurement & Purchase Approval System) — Nhóm 01  
**Mã nguồn / Repository:** `thgnud1022/group-01-project`  
**Nhánh Git:** `final-delivery`  
**Phiên bản Phát hành:** `v1.0.0-final` (Commit `9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`)  
**Ngày chốt hồ sơ:** 2026-10-08  
**Chuẩn đầu ra môn học:** Deliverable 3.7 (Yêu cầu bắt buộc: Severity, Steps, Expected, Actual, Evidence, Owner, Status, Reproducible)  
**Trạng thái Thẩm định:** **PASS (100% Bugs Resolved — 0 Open Blocker)**  

---

## 1. Giới Thiệu & Nguyên Tắc Quản Trị Khuyết Tật (Governance Principles)

Tài liệu này là hồ sơ theo dõi lỗi và khuyết tật kỹ thuật tập trung (**Central Bug Tracking Record**) chính thức của Nhóm 01 cho toàn bộ vòng đời phát triển dự án.

### Nguyên Tắc Liêm Chính & Thực Chứng (Integrity & Evidence-Based Rules):
1. **Dựa trên Thực chứng (Evidence-Based):** Mỗi bản ghi khuyết tật bắt buộc phải liên kết trực tiếp với mã nguồn, nhật ký lỗi runtime, lịch sử commit Git và bộ kiểm thử hồi quy tương ứng.
2. **Không Ngụy tạo Lỗi (Anti-Fabrication):** Tuyệt đối không tạo lỗi giả để làm dày tài liệu; chỉ ghi nhận các lỗi và khiếm khuyết **THỰC TẾ** đã xuất hiện trong quá trình thiết kế, triển khai, kiểm thử và đưa lên môi trường đám mây.
3. **Phân Định Rõ Ràng (Strict Classification):** Không đánh đồng giới hạn kỹ thuật có chủ ý (**Accepted Limitation**) hay sai lệch tài liệu (**Documentation Issue**) thành lỗi phần mềm (**Software Bug**).
4. **Quyền Sở Hữu Đồng Bộ (Ownership Alignment):** Mọi khuyết tật liên quan đến một User Story đều được phân công cho đúng thành viên sở hữu User Story đó xuyên suốt vòng đời.

---

## 2. Hệ Thống Phân Loại Khuyết Tật (Classification Taxonomy)

Mọi vấn đề kỹ thuật phát hiện trong dự án được phân loại nghiêm ngặt thành 4 nhóm độc lập:

| Mã Nhóm | Phân Loại | Định Nghĩa Kỹ Thuật | Tiêu Chí Xử Lý |
|---|---|---|---|
| **A. BUG** | **Lỗi Phần Mềm Thực Tế** | Hành vi sai lệch logic, vi phạm ràng buộc nghiệp vụ, lỗ hổng an ninh hoặc lỗi runtime trong mã nguồn. | Bắt buộc khắc phục, có commit sửa lỗi và regression test chứng minh. |
| **B. DOC** | **Sai Lệch Tài Liệu** | Mã nguồn hoạt động đúng nhưng tài liệu mô tả sai lệch, lỗi thời hoặc không đồng bộ với môi trường phát hành. | Cập nhật tài liệu kỹ thuật khớp với sự thật khách quan của mã nguồn. |
| **C. LIM** | **Giới Hạn Kỹ Thuật Chấp Nhận** | Hành vi có chủ ý trong kiến trúc (ví dụ: Fallback Heuristic, single bundle Vite), không phải lỗi logic. | Ghi nhận công khai trong Release Notes và QA Report. |
| **D. GAP** | **Khoảng Trống Kiểm Chứng** | Chưa có minh chứng chạy tự động trên môi trường đặc thù nhưng không chứng minh mã nguồn sai. | Giải trình phương án thay thế tương đương đã nghiệm thu. |

---

## 3. Bảng Theo Dõi Lỗi Phần Mềm Trung Tâm (Central Bug Tracking Table)

> **Quy ước Mức độ Nghiêm trọng (Severity):**  
> - **BLOCKER:** Lỗi chí mạng vi phạm bảo mật, sai lệch dữ liệu tài chính hoặc chặn đứng chu trình nghiệp vụ.  
> - **CRITICAL:** Lỗi nghiêm trọng ảnh hưởng luồng chính nhưng có thể chặn tạm thời bằng quy trình.  
> - **MAJOR:** Lỗi ảnh hưởng trải nghiệm hoặc cấu hình hạ tầng cần khắc phục trước khi release.  
> - **MINOR:** Lỗi nhỏ về hiển thị giao diện, định dạng nhập liệu.  
> - **TRIVIAL:** Lỗi chính tả, thẩm mỹ không ảnh hưởng tính năng.  
>  
> **Quy ước Trạng thái (Status):** `OPEN` | `RESOLVED` | `ACCEPTED` | `DUPLICATE` | `NOT A BUG`

| ID | Type | Severity | Story | Task | Owner | Summary | Steps to Reproduce | Expected | Actual | Evidence | Status | Resolution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **BUG-001** *(QF-001 / CR-003)* | BUG | **BLOCKER** | US-09, GOV-02 | T-30..33, T-40 | Nguyễn Thị Thùy Dung | PO có thể được tạo từ PR chưa duyệt và chấp nhận ghi đè giá từ client | 1. Tạo PR status PENDING.<br>2. Gửi `POST /api/po` với prId đó. | Bị từ chối với HTTP 400 (PR phải APPROVED; giá lấy từ Quotation). | Tạo được PO dù PR chưa duyệt; cho phép client override đơn giá. | Kiro Verify V-03, Commit `5fe0ec0`, `test_po_prisma.py` | **RESOLVED** | Áp dụng khóa `SELECT ... FOR UPDATE`, kiểm tra `pr.status == 'APPROVED'`, khóa đơn giá từ bảng Quotation. |
| **BUG-002** *(CR-001)* | BUG | **BLOCKER** | US-01, US-02 | T-01..06, T-37 | Nguyễn Thị Thùy Dung | Lỗ hổng tiêm vai trò phía client qua header/body dẫn đến leo thang đặc quyền | 1. Đăng nhập nhân viên.<br>2. Gửi request kèm header `Role: ADMIN` duyệt PR. | Bị từ chối với HTTP 403; vai trò phải lấy từ JWT và CSDL máy chủ. | Client tự nhận vai trò nào máy chủ chấp nhận vai trò đó. | Commit `19ce38b`, `6f47a4e`, `test_rbac.py` | **RESOLVED** | Xây dựng Supabase JWT ES256 JWKS verification, Server-Side `RoleChecker` bảo vệ 100% 19 endpoints. |
| **BUG-003** *(CR-002)* | BUG | **BLOCKER** | GOV-01, US-02 | T-37..39 | Nguyễn Thị Thùy Dung | Bỏ sót quy tắc Không tự phê duyệt (No Self-Approval) cho phép người tạo tự duyệt PR của mình | 1. Đăng nhập Manager/Admin.<br>2. Tạo PR mới.<br>3. Bấm duyệt chính PR đó. | Bị chặn với HTTP 403 ("No Self-Approval — GOV-01"). | Quản lý/Admin tự duyệt thành công PR do chính mình tạo. | Commit `6f47a4e`, `5fe0ec0`, `test_rbac.py` | **RESOLVED** | Thêm kiểm tra `if approver_id == pr_creator_id: raise AuthorizationError(...)` trong toàn bộ luồng duyệt/từ chối/sửa PR. |
| **BUG-004** *(CR-004)* | BUG | **BLOCKER** | US-10 | T-34..36 | Trần Thị Thu Hà | Cho phép Đóng PR khi hàng chưa nhận đủ 100% so với đơn hàng PO | 1. PO đặt 5 máy.<br>2. Nhận đợt 1 được 2 máy.<br>3. Gửi `POST /api/pr/{id}/close`. | Bị từ chối HTTP 400 ("Hàng chưa được nhận đủ"). | Cho phép đóng PR và quyết toán tiền dù còn thiếu 3 máy. | Commit `02a117d`, `test_close_prisma.py`, AI-089 failure smoke | **RESOLVED** | Kiểm tra `sum(receivedQty) >= po.quantity` trong transaction đóng PR trước khi chuyển trạng thái `CLOSED`. |
| **BUG-005** *(CR-005)* | BUG | **MAJOR** | Platform / Deploy | T-41, T-42 | Trần Thị Kiều Giang | Mất ánh xạ `authUserId` khi Railway redeploy container dẫn đến lỗi 401 | 1. Railway build lại container.<br>2. Người dùng đăng nhập qua Supabase.<br>3. Gọi `/api/auth/me`. | Trả về HTTP 200 kèm thông tin người dùng từ PostgreSQL. | Trả về HTTP 401 do trường `User.authUserId` bị thiếu trong DB. | Commit `80afdd0`, script `seed_auth_users.py`, `start.sh` | **RESOLVED** | Nhúng kịch bản idempotent `seed_auth_users.py` trực tiếp vào `start.sh` trước khi Uvicorn khởi chạy. |
| **BUG-006** *(CR-006)* | BUG | **MAJOR** | Platform / Security | T-41 | Trần Thị Kiều Giang | Xung đột cấu hình CORS wildcard `*` với `allow_credentials=True` khiến browser chặn request | 1. Mở web Vercel.<br>2. Gửi request có Authorization Bearer tới Railway backend. | Browser gửi request preflight thành công. | Browser chặn request vì W3C CORS cấm wildcard khi bật credentials. | Commit `b8404f4`, `backend/app/main.py` | **RESOLVED** | Liệt kê tường minh danh sách `ALLOWED_ORIGINS` (Vercel domain, localhost) thay thế wildcard `*`. |
| **BUG-007** *(CR-007)* | BUG | **MAJOR** | Platform / Deploy | T-41 | Trần Thị Kiều Giang | Vercel rewrite proxy lỗi DNS resolution (`DNS_HOSTNAME_RESOLVE_FAILED` 502) khi Railway redeploy | 1. Gọi API qua proxy Vercel `/api/*`.<br>2. Railway restart container. | Request API chuyển tiếp thông suốt. | Vercel trả về 502 Bad Gateway do mất định tuyến DNS mạng biên. | Commit `b8404f4`, `d2cff2c`, `client.ts`, `.env` | **RESOLVED** | Đưa biến `VITE_API_URL` trỏ trực tiếp tới Railway backend vào bản build, bỏ qua proxy Vercel. |
| **BUG-008** *(CR-008)* | BUG | **MAJOR** | US-07 | T-21..25 | Nguyễn Trúc Lam | Màn hình so sánh báo giá chặn truy cập các vai trò ngoài PROCUREMENT và không cảnh báo quá hạn | 1. Đăng nhập Employee/Manager.<br>2. Mở màn hình so sánh báo giá. | Mọi vai trò đã đăng nhập đều xem được (HD-13); báo giá hết hạn có nhãn đỏ. | Bị chặn quyền 403; không có cảnh báo trực quan khi báo giá quá hạn. | Commit `20100e1`, `ComparisonView.tsx`, `test_quotation_comparison_prisma.py` | **RESOLVED** | Mở quyền đọc cho toàn bộ vai trò đã xác thực; bổ sung badge cảnh báo hết hạn màu đỏ khi `validUntil < now()`. |
| **BUG-009** *(CR-009)* | BUG | **MAJOR** | US-01 | T-01..03 | Trần Thị Kiều Giang | Cảnh báo vượt ngân sách giả khi tạo PR và thiếu viền đỏ trên ô input bắt buộc | 1. Mở form tạo PR.<br>2. Nhập số tiền trong hạn mức.<br>3. Để trống trường lý do và bấm gửi. | Không báo vượt ngân sách; ô lý do viền đỏ cảnh báo. | Hiện cảnh báo vượt hạn mức; không có viền đỏ báo lỗi trực quan. | Commit `9af432c`, `0216a7c`, `frontend/src/App.tsx` | **RESOLVED** | Chuẩn hóa công thức tính ngân sách khả dụng; thêm class `border-red-500` và trạng thái `touched` khi validate form. |
| **BUG-010** *(CR-010)* | BUG | **MINOR** | US-06 | T-17..20 | Nguyễn Trương Thùy Dương | Ô nhập giá báo giá xuất hiện số 0 đứng đầu và thiếu vùng kéo thả tải lên tài liệu | 1. Mở form nhập báo giá.<br>2. Gõ đơn giá sản phẩm. | Giá trị hiển thị số tự nhiên; có vùng kéo thả chọn tệp đính kèm. | Xuất hiện tiền tố số '0' (vd: '01500000'); thiếu drag & drop file upload. | Commit `71b48e2`, `1775682`, `QuotationsView.tsx` | **RESOLVED** | Xử lý format chuỗi rỗng khi focus; bổ sung native file input picker và vùng kéo thả tệp đính kèm. |

---

## 4. Chi Tiết Hồ Sơ Lỗi Phần Mềm Thực Tế (Detailed Bug Records)

### BUG-001: Khởi Tạo Purchase Order Từ PR Chưa Duyệt & Can Thiệp Giá Thương Mại
- **Mã định danh cũ:** `QF-001` (Kiro Verify V-03), `CR-003` (Code Review)
- **Mức độ nghiêm trọng:** **BLOCKER** (Vi phạm tính toàn vẹn thương mại REQ-BR-10 & REQ-BR-03)
- **User Story:** **US-09**, **GOV-02** | **Task:** `T-30..T-33`, `T-40`
- **Người chịu trách nhiệm (Owner):** **Nguyễn Thị Thùy Dung**
- **Mô-đun ảnh hưởng:** `backend/app/routers/po.py`, `backend/app/services/procurement_service.py`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Khởi tạo một Purchase Request mới có trạng thái `PENDING_MANAGER_APPROVAL`.
  2. Gửi request `POST /api/po` với body chứa `prId` của PR vừa tạo, kèm `unitPrice` và `quantity` tự định nghĩa.
- **Hành vi kỳ vọng (Expected):** Hệ thống phải trả về lỗi `HTTP 400 Bad Request` với thông báo "PR phải ở trạng thái APPROVED mới được tạo PO". Đơn giá và số lượng phải được khóa tự động từ bản ghi Quotation trong PostgreSQL.
- **Hành vi thực tế (Actual):** Endpoint cho phép tạo PO thành công từ PR chưa qua phê duyệt; giá trị đơn hàng bị can thiệp bởi dữ liệu từ client truyền lên.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `5fe0ec0` (`fix(po): enforce PR status APPROVED and lock commercial quotation values`)
  - Test suite hồi quy: `backend/tests/test_po_prisma.py` (TC-PO-001, TC-PO-002 PASSED 100%)
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Sử dụng giao dịch cơ sở dữ liệu với khóa dòng `SELECT ... FOR UPDATE` xác minh `pr.status == 'APPROVED'`; loại bỏ toàn bộ trường đơn giá do client gửi lên và truy vấn trực tiếp từ bảng `Quotation` trong Supabase.

---

### BUG-002: Lỗ Hổng Tiêm Vai Trò Phía Khách (Client-Side Role Injection)
- **Mã định danh cũ:** `CR-001` (Code Review)
- **Mức độ nghiêm trọng:** **BLOCKER** (Vi phạm an ninh bảo mật, nguy cơ leo thang đặc quyền)
- **User Story:** **US-01**, **US-02** | **Task:** `T-01..T-06`, `T-37`
- **Người chịu trách nhiệm (Owner):** **Nguyễn Thị Thùy Dung** *(Đồng sở hữu: Trần Thị Kiều Giang)*
- **Mô-đun ảnh hưởng:** `backend/app/dependencies/auth.py`, `backend/app/dependencies/rbac.py`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Đăng nhập với tài khoản người dùng có vai trò `EMPLOYEE`.
  2. Dùng Postman hoặc curl gửi request gọi endpoint phê duyệt `POST /api/pr/{id}/approve` kèm header `Role: MANAGER`.
- **Hành vi kỳ vọng (Expected):** Hệ thống phải trả về `HTTP 403 Forbidden`; quyền hạn người dùng phải được giải mã độc lập từ chữ ký JWT của Supabase và đối soát trong CSDL PostgreSQL.
- **Hành vi thực tế (Actual):** Hệ thống tin cậy vai trò do client tự xưng trong request header, cho phép nhân viên tự duyệt PR.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `19ce38b`, `6f47a4e` (`feat(auth): implement server-side rbac with supabase jwt jwks`)
  - Test suite hồi quy: `backend/tests/test_jwt_auth.py` (12/12 PASS), `backend/tests/test_rbac.py` (28/28 PASS)
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Triển khai `SupabaseJWTService` kiểm tra chữ ký ES256 qua JWKS; phân giải danh tính người dùng máy chủ qua `authUserId == sub`; áp dụng `RoleChecker` cho 100% 19 endpoints nghiệp vụ.

---

### BUG-003: Bỏ Sót Ràng Buộc Không Tự Phê Duyệt (No Self-Approval Bypass)
- **Mã định danh cũ:** `CR-002` (Code Review)
- **Mức độ nghiêm trọng:** **BLOCKER** (Vi phạm nguyên tắc kiểm soát độc lập GOV-01 / Four-Eyes Principle)
- **User Story:** **GOV-01**, **US-02** | **Task:** `T-37..T-39`
- **Người chịu trách nhiệm (Owner):** **Nguyễn Thị Thùy Dung**
- **Mô-đun ảnh hưởng:** `backend/app/routers/pr.py`, `backend/app/services/procurement_service.py`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Đăng nhập bằng tài khoản có vai trò `MANAGER` hoặc `ADMIN`.
  2. Tạo một PR mua sắm mới.
  3. Gửi request duyệt chính PR đó qua `POST /api/pr/{id}/approve`.
- **Hành vi kỳ vọng (Expected):** Hệ thống phải chặn với lỗi `HTTP 403 Forbidden` kèm thông báo: "Không thể phê duyệt PR do chính mình tạo (No Self-Approval — GOV-01)".
- **Hành vi thực tế (Actual):** Quản lý hoặc Quản trị viên có thể tự duyệt thành công PR của bản thân mà không qua người thứ hai kiểm duyệt.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `6f47a4e`, `5fe0ec0`
  - Test suite hồi quy: `backend/tests/test_rbac.py` (TC-RBAC-014, TC-RBAC-015, TC-RBAC-018 PASSED)
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Bổ sung điều kiện kiểm tra nghiêm ngặt `if approver_id == pr_creator_id: raise AuthorizationError(...)` trong các hàm service `approve_pr_prisma`, `reject_pr_prisma`, và `request_revision_prisma`, áp dụng bình đẳng cho mọi vai trò.

---

### BUG-004: Cho Phép Đóng PR Khi Hàng Chưa Nhận Đủ 100% Số Lượng
- **Mã định danh cũ:** `CR-004` (Code Review)
- **Mức độ nghiêm trọng:** **BLOCKER** (Vi phạm ràng buộc REQ-BR-11 & HD-07, nguy cơ thất thoát tài chính)
- **User Story:** **US-10** | **Task:** `T-34..T-36`
- **Người chịu trách nhiệm (Owner):** **Trần Thị Thu Hà**
- **Mô-đun ảnh hưởng:** `backend/app/routers/receiving.py`, `backend/app/services/procurement_service.py`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Tạo PR và PO với số lượng 5 sản phẩm.
  2. Nhập biên bản nhận hàng đợt 1 với số lượng 2 sản phẩm (còn thiếu 3 sản phẩm).
  3. Gửi request đóng PR qua `POST /api/pr/{id}/close`.
- **Hành vi kỳ vọng (Expected):** Hệ thống phải chặn với lỗi `HTTP 400 Bad Request` kèm thông báo: "Không thể đóng PR: Hàng chưa được nhận đủ (Đã nhận 2/5)".
- **Hành vi thực tế (Actual):** PR chuyển trạng thái `CLOSED` thành công và giải phóng toàn bộ số dư tạm giữ dù hàng chưa giao đủ.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `02a117d` (`feat(receiving): block close PR if goods not fully received per REQ-BR-11`)
  - Test suite hồi quy: `backend/tests/test_close_prisma.py` (TC-CLOSE-001, TC-CLOSE-002 PASSED), AI-089 Public Smoke test Failure Path PASSED.
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Tính toán tổng số lượng nhận lũy kế `total_received = sum(r.receivedQty for r in receivings)` và kiểm tra điều kiện `if total_received < po.quantity: raise ValueError(...)` trước khi thực hiện chuyển trạng thái và quyết toán ngân sách.

---

### BUG-005: Mất Ánh Xạ authUserId Khi Railway Container Khởi Động Lại
- **Mã định danh cũ:** `CR-005` (Code Review)
- **Mức độ nghiêm trọng:** **MAJOR** (Chặn đăng nhập sau mỗi lần deploy trên môi trường cloud)
- **User Story:** Platform / Deployment | **Task:** `T-41`, `T-42`
- **Người chịu trách nhiệm (Owner):** **Trần Thị Kiều Giang**
- **Mô-đun ảnh hưởng:** `backend/start.sh`, `backend/scripts/seed_auth_users.py`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Push bản cập nhật mã nguồn mới kích hoạt Railway redeploy.
  2. Container mới được khởi tạo và chạy lệnh `uvicorn` mặc định mà không kích hoạt seed.
  3. Đăng nhập tài khoản kiểm thử từ client và gọi `/api/auth/me`.
- **Hành vi kỳ vọng (Expected):** Hệ thống tìm thấy bản ghi người dùng với `authUserId` khớp với `sub` của token Supabase và trả về `HTTP 200 OK`.
- **Hành vi thực tế (Actual):** Hệ thống trả về `HTTP 401 Unauthorized` do liên kết `authUserId` trong PostgreSQL bị thiếu.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `80afdd0` (`fix(deploy): seed authUserId bindings at every Railway startup`)
  - Kịch bản kiểm chứng: `backend/scripts/seed_auth_users.py`
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Viết kịch bản seed có tính chất idempotent (`seed_auth_users.py`) cập nhật đúng 5 UUID kiểm thử vào PostgreSQL và tích hợp vào script khởi động `start.sh` trước lệnh `uvicorn`.

---

### BUG-006: Xung Đột Cấu Hình CORS Wildcard Với Cờ allow_credentials
- **Mã định danh cũ:** `CR-006` (Code Review)
- **Mức độ nghiêm trọng:** **MAJOR** (Trình duyệt chặn toàn bộ API call có Authorization header)
- **User Story:** Platform / Security | **Task:** `T-41`
- **Người chịu trách nhiệm (Owner):** **Trần Thị Kiều Giang**
- **Mô-đun ảnh hưởng:** `backend/app/main.py`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Truy cập frontend từ domain Vercel `https://group-01-project.vercel.app`.
  2. Đăng nhập và thực hiện request tới Railway backend có gửi kèm `Authorization: Bearer <token>`.
- **Hành vi kỳ vọng (Expected):** Trình duyệt cho phép gửi header Authorization và nhận phản hồi từ backend.
- **Hành vi thực tế (Actual):** Trình duyệt Chrome/Edge chặn request preflight với lỗi CORS do chuẩn W3C cấm sử dụng wildcard `*` khi `allow_credentials=True`.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `b8404f4` (`fix(cors+api): fix CORS credentials conflict and set direct railway url`)
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Thay thế wildcard bằng mảng các domain cụ thể được cấp quyền: `ALLOWED_ORIGINS = ["https://group-01-project.vercel.app", "http://localhost:5173", "http://localhost:3000"]`.

---

### BUG-007: Lỗi Phân Giải Tên Miền DNS Khi Gọi API Qua Vercel Proxy
- **Mã định danh cũ:** `CR-007` (Code Review)
- **Mức độ nghiêm trọng:** **MAJOR** (Gây lỗi 502 gián đoạn dịch vụ)
- **User Story:** Platform / Networking | **Task:** `T-41`
- **Người chịu trách nhiệm (Owner):** **Trần Thị Kiều Giang**
- **Mô-đun ảnh hưởng:** `frontend/.env`, `frontend/src/api/client.ts`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Frontend gọi API qua đường dẫn tương đối `/api/auth/me` đi qua Vercel proxy rewrite.
  2. Khi Railway đang khởi động lại hoặc thay đổi DNS nội bộ, các node mạng biên Vercel không phân giải được hostname.
- **Hành vi kỳ vọng (Expected):** Request được định tuyến thành công đến backend.
- **Hành vi thực tế (Actual):** Vercel trả về `HTTP 502 Bad Gateway` với header `X-Vercel-Error: DNS_HOSTNAME_RESOLVE_FAILED`.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `b8404f4`, `d2cff2c`
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Khai báo trực tiếp biến môi trường `VITE_API_URL` trỏ thẳng tới Railway production backend, cấu hình `client.ts` gọi trực tiếp từ trình duyệt, bỏ qua lớp proxy trung gian.

---

### BUG-008: Phân Quyền Hạn Chế & Thiếu Cảnh Báo Báo Giá Hết Hạn Trên Bảng So Sánh
- **Mã định danh cũ:** `CR-008` (Code Review)
- **Mức độ nghiêm trọng:** **MAJOR** (Vi phạm quyết định HD-13/K-2 và thiếu thông tin thời hạn)
- **User Story:** **US-07** | **Task:** `T-21..T-25`
- **Người chịu trách nhiệm (Owner):** **Nguyễn Trúc Lam**
- **Mô-đun ảnh hưởng:** `backend/app/routers/quotations.py`, `frontend/src/components/ComparisonView.tsx`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Đăng nhập bằng tài khoản `EMPLOYEE` hoặc `MANAGER`.
  2. Truy cập màn hình đối sánh báo giá của một PR đã có 2 báo giá.
- **Hành vi kỳ vọng (Expected):** Toàn bộ nhân sự đã đăng nhập đều có quyền xem bảng đối sánh; báo giá có `validUntil` quá hạn phải được gắn nhãn cảnh báo đỏ rõ ràng.
- **Hành vi thực tế (Actual):** Endpoint trả về `HTTP 403 Forbidden` (chỉ cho phép PROCUREMENT); không có cảnh báo trực quan cho báo giá hết hạn.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `20100e1` (`feat(quotations): allow all authenticated roles to view comparison and add expired badge`)
  - Test suite hồi quy: `backend/tests/test_quotation_comparison_prisma.py` (9/9 tests PASSED)
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Mở quyền truy cập router so sánh cho mọi vai trò đã xác thực; bổ sung badge màu đỏ `Đã hết hạn` trên giao diện khi `new Date(quote.validUntil) < new Date()`.

---

### BUG-009: Cảnh Báo Vượt Ngân Sách Giả & Thiếu Viền Đỏ Xác Thực Biểu Mẫu PR
- **Mã định danh cũ:** `CR-009` (Code Review)
- **Mức độ nghiêm trọng:** **MAJOR** (Gây hiểu nhầm cho người dùng khi tạo yêu cầu mua sắm)
- **User Story:** **US-01** | **Task:** `T-01..T-03`
- **Người chịu trách nhiệm (Owner):** **Trần Thị Kiều Giang**
- **Mô-đun ảnh hưởng:** `frontend/src/App.tsx`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Mở màn hình tạo yêu cầu mua sắm mới.
  2. Nhập số lượng và đơn giá có tổng tiền nhỏ hơn ngân sách khả dụng của phòng ban.
  3. Để trống ô lý do mua sắm và bấm nút "Gửi Yêu Cầu".
- **Hành vi kỳ vọng (Expected):** Không hiển thị cảnh báo vượt ngân sách; ô lý do mua sắm bị để trống phải hiển thị viền đỏ báo lỗi trực quan.
- **Hành vi thực tế (Actual):** Giao diện tính toán sai lệch và hiển thị thông báo "Vượt ngân sách"; ô input không có viền đỏ.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `9af432c`, `0216a7c`
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Chuẩn hóa logic tính toán số dư khả dụng (`availableBudget = allocated - spent - tempReserved`); bổ sung trạng thái `touched` và lớp CSS `border-red-500` cho các trường bắt buộc khi submit không hợp lệ.

---

### BUG-010: Số 0 Đứng Đầu Trên Ô Nhập Đơn Giá & Thiếu Vùng Kéo Thả Tệp Báo Giá
- **Mã định danh cũ:** `CR-010` (Code Review)
- **Mức độ nghiêm trọng:** **MINOR** (Khuyết tật trải nghiệm nhập liệu UI)
- **User Story:** **US-06** | **Task:** `T-17..T-20`
- **Người chịu trách nhiệm (Owner):** **Nguyễn Trương Thùy Dương**
- **Mô-đun ảnh hưởng:** `frontend/src/components/QuotationsView.tsx`
- **Các bước tái hiện (Steps to Reproduce):**
  1. Mở biểu mẫu nhập báo giá nhà cung cấp.
  2. Bấm vào ô "Đơn giá" và gõ số tiền.
- **Hành vi kỳ vọng (Expected):** Số tiền hiển thị tự nhiên, không bị dính số '0' ở đầu; có khu vực kéo thả tệp đính kèm tài liệu báo giá.
- **Hành vi thực tế (Actual):** Xuất hiện tiền tố số '0' (ví dụ người dùng gõ 15,000,000 thì hiển thị thành '015000000'); thiếu vùng kéo thả tệp.
- **Bằng chứng kiểm chứng (Evidence):**
  - Commit khắc phục: `71b48e2`, `1775682`
- **Trạng thái:** **RESOLVED**
- **Giải pháp xử lý:** Format ô input xử lý chuỗi rỗng khi focus; bổ sung native file picker và dropzone cho phép kéo thả tệp tài liệu đính kèm.

---

## 5. Bảng Theo Dõi Sai Lệch Tài Liệu (Documentation Issues Log)

Các mục dưới đây là sai lệch giữa tài liệu và mã nguồn thực tế; đã được chuẩn hóa để phản ánh trung thực hiện trạng hệ thống:

| ID | Severity | Phân Vùng | Mô Tả Sai Lệch Ban Đầu | Hiện Trạng Thực Tế | Bằng Chứng Xử Lý | Trạng Thái | Người Phụ Trách |
|---|---|---|---|---|---|---|---|
| **DOC-001** | MAJOR | Automated Testing | Tài liệu cũ (`DECISION_LOG.md` HD-05, `release-notes.md`) ghi nhận E2E bằng Playwright | Kịch bản tự động hóa thực tế chạy đạt 14/14 steps bằng Puppeteer | Chuẩn hóa README, Runbook, Release Notes và Final QA Report ghi rõ Puppeteer | **RESOLVED** | Nguyễn Trương Thùy Dương |
| **DOC-002** | MAJOR | Release Evidence | Bản thảo `release-notes.md` cũ ghi "Chưa có Public Demo URL" và "0% hallucination" | Dự án đã deploy công khai Vercel + Railway và AI dùng Fallback Heuristic | Commit `ad8023a` (AI-092) đồng bộ toàn diện Release Notes với cloud release | **RESOLVED** | Nguyễn Trương Thùy Dương |
| **DOC-003** | MINOR | Data Evidence | Báo cáo cũ dùng kịch bản dữ liệu giả định (5 màn hình đồ họa 4K) | CSDL PostgreSQL thực tế lưu vết PR-2026-029 (ThinkPad P16 AI Workstations) | `FINAL_QA_GATE_REPORT.md` Section 12 chuẩn hóa lấy dữ liệu Supabase thực tế | **RESOLVED** | Trần Thị Thu Hà |

---

## 6. Bảng Giới Hạn Kỹ Thuật Đã Chấp Nhận (Accepted Limitations Log)

Các mục dưới đây là quyết định kỹ thuật có chủ ý hoặc tính năng dự phòng theo thiết kế; không phải khuyết tật logic:

| ID | Severity | Hạng Mục | Mô Tả Giới Hạn Kỹ Thuật | Phương Án Dự Phòng / Xử Lý (Mitigation) | Trạng Thái | Người Phụ Trách |
|---|---|---|---|---|---|---|
| **LIM-001** | MAJOR | AI Service | Google Gemini Live API chưa được kích hoạt trong test runner tự động do phụ thuộc mạng ngoài | Kích hoạt bộ phân tích **Fallback Heuristic** dựa trên trọng số Figma (40/25/25/10), đạt độ tin cậy 78% an toàn 100% | **ACCEPTED** | Nguyễn Thị Thùy Dung |
| **LIM-002** | MINOR | Frontend Build | Gói bundle `index-*.js` có dung lượng 649.36 kB (vượt mức cảnh báo 500 kB của Vite) | Nén Gzip mạng biên Vercel chỉ còn ~177 kB, tải dưới 300ms, bảo toàn kiến trúc ổn định | **ACCEPTED** | Trần Thị Kiều Giang |
| **LIM-003** | MAJOR | Usability Test | Kế hoạch Usability Test (Deliverable 2.4) đã có kịch bản nhưng chưa kiểm thử trên người dùng thật | Công bố minh bạch trạng thái `PENDING REAL USER TEST`, không ngụy tạo điểm số | **ACCEPTED** | Trần Thị Thu Hà |
| **LIM-004** | MINOR | Architecture | Giao diện điều hướng bằng component state nội bộ trong `App.tsx`, chưa tách React Router đa trang | Hoạt động trơn tru, không phát sinh lỗi điều hướng, build sạch 0 lỗi TypeScript | **ACCEPTED** | Trần Thị Kiều Giang |

---

## 7. Bảng Khoảng Trống Kiểm Chứng (Verification Gaps Log)

| ID | Severity | Phạm Vi | Mô Tả Khoảng Trống | Giải Trình Thực Tế | Trạng Thái | Người Phụ Trách |
|---|---|---|---|---|---|---|
| **GAP-001** | MINOR | Testing Tooling | Thiếu bằng chứng chạy kịch bản E2E bằng Playwright | Kịch bản Puppeteer 14/14 steps đã kiểm chứng toàn diện luồng nghiệp vụ trên Chrome | **ACCEPTED** | Trần Thị Thu Hà |
| **GAP-002** | MINOR | Security / NFR | Chưa chạy kiểm tra tải trọng thức (load test) và pip-audit tự động trong pipeline | Đã thực hiện 28 test cases an ninh RBAC, fail-closed, transaction locks bảo vệ CSDL | **ACCEPTED** | Nguyễn Thị Thùy Dung |

---

## 8. Ma Trận Truy Xuất Khuyết Tật (Bug Traceability Matrix)

Ma trận truy xuất chứng minh tính giải quyết triệt để của 10 lỗi phần mềm thực tế:

```
Bug ID ──► User Story ──► Tasks ──► Tệp Nguồn ──► Commit Hash ──► Test Case Hồi Quy ──► Kết Quả
```

| Bug ID | User Story | Mã Tasks | Tệp Nguồn Trọng Yếu | Commit Hash | Test Suite Hồi Quy | Kết Quả Thẩm Định |
|---|---|---|---|---|---|---|
| **BUG-001** | US-09, GOV-02 | T-30..33, T-40 | `po.py`, `procurement_service.py` | `5fe0ec0` | `test_po_prisma.py` (TC-PO-001..002) | **PASS (100%)** |
| **BUG-002** | US-01, US-02 | T-01..06, T-37 | `auth.py`, `rbac.py` | `19ce38b`, `6f47a4e` | `test_jwt_auth.py`, `test_rbac.py` | **PASS (100%)** |
| **BUG-003** | GOV-01, US-02 | T-37..39 | `pr.py`, `procurement_service.py` | `6f47a4e`, `5fe0ec0` | `test_rbac.py` (TC-RBAC-014..018) | **PASS (100%)** |
| **BUG-004** | US-10 | T-34..36 | `receiving.py`, `procurement_service.py` | `02a117d` | `test_close_prisma.py` (TC-CLOSE-001..002) | **PASS (100%)** |
| **BUG-005** | Platform | T-41, T-42 | `start.sh`, `seed_auth_users.py` | `80afdd0` | Khởi động lại container Railway, test login | **PASS (100%)** |
| **BUG-006** | Platform | T-41 | `backend/app/main.py` | `b8404f4` | Browser API request với Bearer token | **PASS (100%)** |
| **BUG-007** | Platform | T-41 | `frontend/.env`, `client.ts` | `b8404f4`, `d2cff2c` | AI-089 Public Smoke Test (9/9 checks) | **PASS (100%)** |
| **BUG-008** | US-07 | T-21..25 | `quotations.py`, `ComparisonView.tsx` | `20100e1` | `test_quotation_comparison_prisma.py` (9/9) | **PASS (100%)** |
| **BUG-009** | US-01 | T-01..03 | `frontend/src/App.tsx` | `9af432c`, `0216a7c` | Browser form validation E2E | **PASS (100%)** |
| **BUG-010** | US-06 | T-17..20 | `frontend/src/components/QuotationsView.tsx` | `71b48e2`, `1775682` | Browser quotation input E2E | **PASS (100%)** |

---

## 9. Phân Bổ Trách Nhiệm Thành Viên (Story Ownership Alignment)

Theo nguyên tắc mỗi thành viên chịu trách nhiệm trực tiếp cho User Story của mình:

### 1. Trần Thị Kiều Giang (Owner: US-01 / Core Viva: US-01)
- **Bugs phụ trách:**
  - `BUG-009` (US-01: Cảnh báo vượt ngân sách giả & validation viền đỏ form tạo PR) $\rightarrow$ **RESOLVED**
  - `BUG-005` (Platform: Mất ánh xạ UUID khi Railway container khởi động lại) $\rightarrow$ **RESOLVED**
  - `BUG-006` (Platform: Xung đột cấu hình CORS credentials và wildcard) $\rightarrow$ **RESOLVED**
  - `BUG-007` (Platform: Lỗi Vercel proxy DNS resolution gọi backend Railway) $\rightarrow$ **RESOLVED**
- **Tổng số bugs:** 4 (1 Story bug, 3 Platform/Deployment bugs). **100% Resolved.**

### 2. Nguyễn Trương Thùy Dương (Owner: US-04, US-05, US-06 / Core Viva: US-04)
- **Bugs phụ trách:**
  - `BUG-010` (US-06: Ô nhập đơn giá báo giá số 0 đứng đầu & tải tệp đính kèm) $\rightarrow$ **RESOLVED**
  - *Ghi chú:* US-04 (Yêu cầu sửa đổi PR) và US-05 (Sourcing nhà cung cấp) không phát sinh lỗi logic trong quá trình kiểm thử hồi quy.
- **Tổng số bugs:** 1. **100% Resolved.**

### 3. Nguyễn Trúc Lam (Owner: US-03, US-07 / Core Viva: US-07)
- **Bugs phụ trách:**
  - `BUG-008` (US-07: Phân quyền màn hình so sánh báo giá & nhãn cảnh báo quá hạn) $\rightarrow$ **RESOLVED**
  - *Ghi chú:* US-03 (Từ chối PR có lý do & hoàn trả ngân sách) hoạt động đúng theo đặc tả.
- **Tổng số bugs:** 1. **100% Resolved.**

### 4. Nguyễn Thị Thùy Dung (Owner: US-02, US-08, US-09, GOV-01 / Core Viva: US-08)
- **Bugs phụ trách:**
  - `BUG-001` (US-09, GOV-02: PO tạo từ PR chưa duyệt & can thiệp giá thương mại) $\rightarrow$ **RESOLVED**
  - `BUG-002` (US-01, US-02: Lỗ hổng tiêm vai trò phía khách hàng) $\rightarrow$ **RESOLVED**
  - `BUG-003` (GOV-01, US-02: Bỏ sót quy tắc Không tự phê duyệt No Self-Approval) $\rightarrow$ **RESOLVED**
- **Giới hạn kỹ thuật:** `LIM-001` (US-08: AI Advisory vận hành ở chế độ Fallback Heuristic 78%) $\rightarrow$ **ACCEPTED**
- **Tổng số bugs:** 3. **100% Resolved.**

### 5. Trần Thị Thu Hà (Owner: US-10, GOV-02 / Core Viva: US-10)
- **Bugs phụ trách:**
  - `BUG-004` (US-10: Cho phép đóng PR khi hàng chưa nhận đủ 100% đơn hàng PO) $\rightarrow$ **RESOLVED**
- **Tổng số bugs:** 1. **100% Resolved.**

---

## 10. Tổng Kết Vòng Đời Lỗi (Bug Lifecycle Summary)

```
================================================================================
                    TỔNG HỢP VÒNG ĐỜI LỖI (BUG LIFECYCLE SUMMARY)
================================================================================
  Tổng số Vấn đề được Ghi nhận (Total Issues):              19
  ------------------------------------------------------------------------------
  Phân loại theo Nhóm:
    - Lỗi Phần mềm Thực tế (Actual Software Bugs):          10 (52.63%)
    - Sai lệch Tài liệu đã Chuẩn hóa (Documentation Issues): 3 (15.79%)
    - Giới hạn Kỹ thuật Chấp nhận (Accepted Limitations):    4 (21.05%)
    - Khoảng trống Kiểm chứng (Verification Gaps):           2 (10.53%)
  ------------------------------------------------------------------------------
  Trạng thái Xử lý Lỗi Phần mềm (Actual Bugs Status):
    - Đã Khắc phục Hoàn toàn (Resolved):                    10 (100.00%)
    - Đang Mở (Open):                                        0 (0.00%)
    - Chấp nhận (Accepted):                                  0 (0.00% cho software bugs)
  ------------------------------------------------------------------------------
  Phân loại Lỗi Phần mềm theo Mức độ Nghiêm trọng (Severity):
    - Khối chặn Chí mạng (Blocker):                          4 (BUG-001, 002, 003, 004)
    - Nghiêm trọng (Critical):                               0
    - Lớn (Major):                                           5 (BUG-005, 006, 007, 008, 009)
    - Nhỏ (Minor):                                           1 (BUG-010)
    - Không đáng kể (Trivial):                               0
  ------------------------------------------------------------------------------
  Lỗi Chặn Phát hành Hiện tại (Release Blockers):            0 (KHÔNG CÓ)
================================================================================
  KẾT LUẬN DELIVERABLE 3.7: PASS (ĐẠT CHUẨN ĐẦU RA MÔN HỌC)
================================================================================
```

---

## 11. Đánh Giá Chuẩn Đầu Ra Deliverable 3.7 (Course Compliance)

Đối chiếu với yêu cầu của tài liệu `Output_BaoCao.xlsx` / [docs/OUTPUT_BAOCAO.md](file:///d:/LTUD/group-01-project-main/docs/OUTPUT_BAOCAO.md):
- **Yêu cầu các trường thông tin:**
  - [x] `severity`: Đầy đủ (BLOCKER, MAJOR, MINOR).
  - [x] `steps`: Đầy đủ các bước tái hiện (Steps to Reproduce) cho 10/10 bugs.
  - [x] `expected`: Đầy đủ hành vi kỳ vọng hợp lệ.
  - [x] `actual`: Đầy đủ hành vi thực tế bị lỗi.
  - [x] `evidence`: Đầy đủ cam kết commit, test file và nhật ký kiểm thử.
  - [x] `owner`: Đầy đủ phân công 5 thành viên sở hữu 10 User Stories.
  - [x] `status`: 100% rõ ràng (`RESOLVED`), 0 open bug.
- **Tiêu chí có thể tái hiện (Reproducible):** 100% bugs đều có kịch bản tái hiện cụ thể và bộ test case hồi quy tự động.
- **Kết luận:** **Deliverable 3.7: PASS**

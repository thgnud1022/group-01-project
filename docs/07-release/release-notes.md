# RELEASE NOTES: AI Procurement & Purchase Approval System

- **Phiên bản (Release Version):** `v1.0.0-final`
- **Git Tag Chính thức:** `v1.0.0-final` (Commit: `9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`)
- **Nhánh Git:** `final-delivery`
- **Ngày phát hành:** 2026-10-07
- **Public Frontend URL:** `https://group-01-project.vercel.app` (Triển khai trên Vercel)
- **Public Backend URL:** `https://group-01-project-production.up.railway.app` (Triển khai trên Railway)
- **Cơ sở dữ liệu:** Supabase Cloud PostgreSQL (Kết nối qua IPv4 Connection Pooler)
- **Trạng thái thẩm định:** `RELEASED & VERIFIED ON PUBLIC CLOUD` (Đã kiểm chứng thực nghiệm 100% PASS trên live stack công khai qua AI-089 Public Smoke Test)

---

## 1. Tổng quan & Phạm vi Phát hành (Release Scope)

Bản phát hành chính thức `v1.0.0-final` hiện thực hóa trọn vẹn chu trình mua sắm doanh nghiệp nội bộ (End-to-End Procurement Lifecycle) với sự tham gia của AI ở vai trò tư vấn ra quyết định (Decision Support / Advisory), kết hợp cơ chế kiểm soát ngân sách thời gian thực và phân quyền máy chủ nghiêm ngặt (Zero-Trust Server-Side RBAC). Toàn bộ hệ thống đã được triển khai và xác minh vận hành trên hạ tầng đám mây công cộng.

### Các tính năng đã được kiểm chứng thực nghiệm (Verified Capabilities):

1. **Hạ tầng Đám mây & Triển khai Công khai (Public Cloud Deployment):**
   - Frontend tĩnh (React 19 + TypeScript + Vite) triển khai công khai trên **Vercel** (`https://group-01-project.vercel.app`).
   - Backend API (FastAPI + Python 3.11 + Uvicorn + Prisma Client) triển khai trên **Railway** (`https://group-01-project-production.up.railway.app`).
   - CSDL quan hệ Supabase PostgreSQL Cloud kết nối qua cổng pooler IPv4.
   - Cơ chế tự động seed ánh xạ danh tính `authUserId` tại mỗi lần container khởi động (`backend/start.sh`), bảo toàn phiên đăng nhập sau các đợt redeploy.
   - Cấu hình CORS chuẩn chỉ định rõ explicit origins, tương thích tuyệt đối với `allow_credentials=True`.

2. **Xác thực & Danh tính Zero-Trust (Authentication & Identity):**
   - Xác thực JWT Supabase qua JWKS (thuật toán chữ ký ES256) với cơ chế timeout mạng 5.0s chống treo socket.
   - Ánh xạ danh tính an toàn `authUserId` liên kết giữa Supabase Auth và bảng `User` trong PostgreSQL.
   - Cô lập hoàn toàn cơ chế mock auth cũ, từ chối client identity injection.

3. **Kiểm soát Truy cập Phân quyền Máy chủ (Server-Side RBAC & Governance):**
   - `RoleChecker` bảo vệ 100% 19/19 REST API endpoints theo đúng ma trận phân quyền (EMPLOYEE, MANAGER, PROCUREMENT, FINANCE, ADMIN).
   - Thực thi triệt để nguyên tắc **Không tự phê duyệt (No Self-Approval — GOV-01 / HD-13)** tại tầng dịch vụ cho mọi vai trò (kể cả Quản trị viên).

4. **Quản lý Yêu cầu Mua sắm (Purchase Request Management):**
   - Tạo PR với đầy đủ thông số hàng hóa, đơn giá ước tính, phòng ban và mức độ ưu tiên; xác thực trường bắt buộc kèm viền đỏ trực quan.
   - Hàng đợi phê duyệt (Approval Queue) hỗ trợ Trưởng bộ phận thực hiện Phê duyệt (`APPROVED`), Từ chối (`REJECTED`) hoặc Yêu cầu chỉnh sửa (`REVISION_REQUIRED`).
   - Kiểm tra ngân sách tự động (Budget Guard) và tạm giữ ngân sách (`tempReservedAmount`) khi PR được phê duyệt.

5. **Quản lý Nguồn cung & Nhà cung cấp (Sourcing & Supplier Management):**
   - Tạo mới, tra cứu danh sách và xem chi tiết thông tin nhà cung cấp (tuân thủ phạm vi HD-15).

6. **Thu thập & So sánh Báo giá (Quotation Collection & Comparison):**
   - Thu thập nhiều báo giá cho PR đã duyệt với đơn giá, số lượng, thời hạn hiệu lực (`validUntil`) và đính kèm tệp qua vùng kéo thả.
   - Màn hình đối sánh báo giá đa chiều (Side-by-side comparison) theo thiết kế Figma 9:4373 và 9:4790, hỗ trợ kiểm tra hạn báo giá thực tế.

7. **Tư vấn Phân tích Báo giá AI (AI Quotation Advisory):**
   - Thẻ khuyến nghị tư vấn tích hợp trong màn hình so sánh, cung cấp phân tích đánh đổi (trade-offs) về giá cả, thời gian giao hàng, bảo hành và rủi ro.
   - Cơ chế bảo vệ: AI chỉ đóng vai trò khuyến nghị (Advisory Only), không tự động tạo PO trên CSDL.

8. **Trao thầu Con người & Khóa Đơn đặt hàng (Human Award & PO Lock Price):**
   - Quyết định trao thầu hoàn toàn thuộc về con người (Human Award Selection).
   - Tạo Purchase Order khóa cứng 100% đơn giá và số lượng từ báo giá trúng thầu (HD-08 Option A: mã PO định dạng `PO-NUM-YYYY-YYYYMMDD-XXXXXXXX`).
   - Guard REQ-BR-10 / HD-04 trong transaction PostgreSQL chặn tuyệt đối việc tạo PO từ PR chưa được duyệt (`APPROVED`).

9. **Nhận hàng & Quyết toán Đóng PR (Goods Receiving & Close PR):**
   - Ghi nhận biên bản nhận hàng từng phần (Partial) hoặc nhận đủ (Complete).
   - Guard REQ-BR-11 / HD-07 (`SUM(receivedQty) >= PO.quantity`) chặn hoàn toàn thao tác đóng PR nếu chưa nhận đủ 100% số lượng.
   - Quyết toán ngân sách: hoàn ứng tạm giữ về 0 và ghi nhận chính xác chi phí thực tế (`spentAmount`).

10. **Lưu trữ Bền vững CSDL (Database Persistence):**
    - Hệ quản trị CSDL Supabase PostgreSQL quản lý bởi Prisma Client Python v0.15.0, hỗ trợ khóa dòng `SELECT ... FOR UPDATE` chống xung đột giao dịch.

---

## 2. Kết quả Thẩm định Chất lượng (Verified Quality Gates)

Toàn bộ các chỉ số dưới đây đã được kiểm chứng độc lập trên live stack tại tag `v1.0.0-final` (`9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`) và public deployment:

* **Kiểm thử Khói Phát hành Công khai (Public Cloud Smoke Test — AI-089):**
  - Đạt **100% PASS** trên toàn bộ 9 tiêu chí vận hành trực tiếp giữa trình duyệt và cloud services:
    1. Frontend tải thành công từ Vercel (`https://group-01-project.vercel.app`, HTTP 200).
    2. Backend Railway phản hồi sống tại `/api/health` (`{"status": "ok", "database": "connected"}`).
    3. Xác thực người dùng hợp lệ qua `/api/auth/me` trả về HTTP 200 kèm danh tính nhân viên.
    4. Yêu cầu không có token bị từ chối chính xác với HTTP 401 Unauthorized.
    5. Cố tình duyệt PR trái thẩm quyền bị chặn đứng với HTTP 403 Forbidden.
    6. **Happy Path:** Khởi tạo PR `PR-2026-039` $\rightarrow$ Duyệt $\rightarrow$ Sourcing báo giá $\rightarrow$ Con người trao thầu $\rightarrow$ Tạo PO $\rightarrow$ Nhận hàng 100% $\rightarrow$ Đóng PR chuyển trạng thái `CLOSED`.
    7. **Failure Path Guard:** Đóng PR khi chưa nhận hàng bị chặn đứng với HTTP 400 Bad Request: *"Không thể đóng PR: Hàng chưa được nhận đủ"*.
    8. Dữ liệu ghi nhận bền vững trên Supabase Cloud PostgreSQL.
    9. Script thẩm định tự động: `scratch/ai089_public_smoke.py`.

* **Kiểm thử Hồi quy Backend (Backend Pytest Regression):**
  - Đạt **133 / 133 PASSED** (0 failed, 0 error) trên toàn bộ 9 test suites kết nối CSDL Supabase PostgreSQL thật (thời gian chạy: 448.93s).
  - Bao phủ: RBAC Security (28 tests), JWT Auth (12 tests), PO Guards (2 tests), Close PR & Receiving (14 tests), Quotation Comparison (15 tests), Lifecycle Flow (14 tests), PR Approval/Revision/Rejection (26 tests), AI Service (22 tests).

* **Kiểm thử Tự động Trình duyệt Toàn chu trình (Final Browser E2E Lifecycle):**
  - Đạt **14 / 14 bước nghiệp vụ PASSED** từ Đăng nhập -> Tạo PR -> Duyệt PR -> Sourcing -> Báo giá 1 & 2 -> So sánh -> AI Advisory -> Trao thầu -> Phát hành PO -> Nhận hàng một phần -> Chặn đóng PR -> Nhận đủ -> Đóng PR & Quyết toán -> Reload kiểm tra bền vững.
  - Công cụ thực thi thực tế: **Puppeteer / puppeteer-core** (`frontend/scripts/test_final_full_lifecycle_e2e.js`).

* **Bằng chứng Ảnh chụp Màn hình Trình duyệt (Visual Browser Evidence):**
  - 8 ảnh chụp màn hình chính thức được lưu trữ tại `docs/evidence/browser/`:
    1. `lifecycle-01-pr-approved.png` (PR được duyệt & tạm giữ ngân sách).
    2. `lifecycle-02-quotation-comparison.png` (Màn hình so sánh 2 báo giá).
    3. `lifecycle-03-ai-analysis.png` (Thẻ AI Advisory hiển thị khuyến nghị).
    4. `lifecycle-04-po-issued.png` (PO được tạo thành công với mã Option A).
    5. `lifecycle-05-receiving-partial.png` (Nhận hàng đợt 1: 2/5 thiết bị).
    6. `lifecycle-06-close-blocked.png` (Cảnh báo chặn đóng PR khi thiếu hàng).
    7. `lifecycle-07-receiving-complete.png` (Nhận đủ đợt 2: 5/5 thiết bị).
    8. `lifecycle-08-closed.png` (PR chuyển CLOSED & quyết toán ngân sách).

* **Kiểm chứng CSDL Bền vững (Live Database Persistence):**
  - Xác nhận trực tiếp trên live PostgreSQL:
    - PR `PR-2026-029`: trạng thái `CLOSED` (Lifecycle run 1).
    - PR `PR-2026-039`: trạng thái `CLOSED` (Public smoke run).
    - Báo giá, đơn hàng và các biên bản nhận hàng lưu trữ đầy đủ.
    - Ngân sách phòng ban hoàn ứng tạm giữ về 0 và ghi nhận chính xác chi phí thực tế (`spentAmount`).

* **Đóng gói Giao diện (Frontend Production Build):**
  - Lệnh `npm.cmd run build` hoàn thành trong 4.05s, 0 lỗi TypeScript, sinh bundle tĩnh sẵn sàng phục vụ (`dist/assets/index-*.js`, kích thước 649.36 kB).

---

## 3. Minh bạch Kỹ thuật về Trí tuệ Nhân tạo (AI Status & Provenance)

Tuân thủ nghiêm ngặt nguyên tắc liêm chính học thuật và quản trị rủi ro AI:

* **Tích hợp Gemini Live API:** `CHƯA XÁC MINH TRỰC TIẾP (UNVERIFIED)`.
  - *Lý do:* Biến môi trường `GEMINI_API_KEY` chưa được cấp trong phiên kiểm thử tự động E2E; hệ thống kích hoạt cơ chế phòng vệ tự động.
* **Chế độ Vận hành Thực tế:** `FALLBACK / HEURISTIC`.
  - Hệ thống sử dụng thuật toán chấm điểm dự phòng có trọng số chuẩn theo Figma 9:5589 (Đơn giá 40%, Giao hàng 25%, Bảo hành 25%, Uy tín 10%).
  - Điểm số tin cậy hiển thị 78% là **Điểm số Heuristic Dự phòng (Fallback / Heuristic Confidence)**, không phải do mô hình Gemini sinh ra.
* **Quyền Quyết định Thuộc về Con người (Human-in-the-Loop):**
  - Khuyến nghị của AI chỉ mang tính tham khảo ($\text{AI recommendation} \neq \text{procurement decision}$).
  - CSDL ghi nhận chính xác 0 bản ghi PO sinh tự động tại bước phân tích của AI. Con người trực tiếp bấm nút Trao thầu để chuyển sang bước tạo PO.
* **Bác bỏ các Tuyên bố Không có Căn cứ:**
  - Không tuyên bố "0% hallucination", "100% correct", "AI tự động phê duyệt", hoặc "Gemini Live verified" khi chưa có bằng chứng runtime độc lập.

---

## 4. Các Giới hạn Kỹ thuật Đã Biết (Known Technical Limitations)

Bản phát hành được đánh giá ở mức **RELEASE READY WITH KNOWN LIMITATIONS** phục vụ báo cáo và bảo vệ đồ án môn học. Các giới hạn kỹ thuật được ghi nhận minh bạch gồm:

1. **Cuộc gọi ra Gemini Live API chưa được xác thực runtime:** Cơ chế phân tích trực tiếp với mô hình LLM bên ngoài cần được cung cấp API key hợp lệ để kiểm chứng trực tiếp; trong điều kiện mặc định hệ thống hoạt động ổn định trên nhánh Fallback Heuristic.
2. **Công cụ Kiểm thử Trình duyệt E2E là Puppeteer:** Kịch bản kiểm thử tự động 14 bước sử dụng `puppeteer-core`. Kiểm thử bằng Playwright chưa được thiết lập độc lập trong đợt kiểm định này.
3. **Kiến trúc Giao diện Đơn khối (Single-Bundle):** Giao diện được cấu trúc dạng các view thành phần điều hướng nội bộ trong `App.tsx`, bundle đơn khối kích thước 649.36 kB, chưa tách route hoàn chỉnh bằng React Router đa trang.
4. **Dữ liệu Usability Test thật đang chờ ghi nhận:** Bộ kịch bản và template kiểm thử trải nghiệm người dùng đã hoàn tất chuẩn bị tại `docs/03-product/usability-findings.md` nhưng kết quả thực nghiệm từ $\ge 3$ người dùng thật cần nhóm sinh viên tổ chức thực hiện trước khi nộp đồ án.

---

## 5. Nhật Ký Thay Đổi (Changelog — v1.0.0-final)

### Added
- **Public Cloud Hosting:** Triển khai Frontend lên Vercel (`https://group-01-project.vercel.app`) và Backend lên Railway (`https://group-01-project-production.up.railway.app`).
- **Startup Identity Seed:** Kịch bản `backend/scripts/seed_auth_users.py` nhúng trực tiếp vào `backend/start.sh` tự động ánh xạ `authUserId` trên CSDL mỗi lần khởi động lại container Railway.
- **Vercel Routing:** Cấu hình `frontend/vercel.json` phục vụ điều hướng SPA và biến môi trường `VITE_API_URL` trỏ trực tiếp Railway.
- **Drag & Drop Upload:** Vùng tải lên tệp tin và drag-and-drop cho tài liệu đính kèm báo giá trong `CollectQuotationsView.tsx`.
- **Form Validation Indicator:** Cảnh báo viền đỏ trực quan trên các trường bắt buộc chưa nhập khi tạo Purchase Request trong `NewRequestView.tsx`.
- **Automated Public Smoke Suite:** Kịch bản `scratch/ai089_public_smoke.py` tự động hóa thẩm định 9 tiêu chí phát hành công khai.

### Verified
- **Backend Pytest:** 133/133 tests PASSED (448.93s) bao phủ toàn diện 9 test suites kết nối CSDL Supabase PostgreSQL.
- **Browser Lifecycle:** 14/14 bước nghiệp vụ hoàn chỉnh đạt 100% Green qua Puppeteer kèm 8 ảnh chụp màn hình chính thức.
- **Public Cloud Smoke:** 9/9 tiêu chí kiểm thử trực tiếp trên Vercel và Railway đạt 100% PASS (AI-089).
- **Business Workflow Guards:** Guard REQ-BR-10 (khóa PO trước duyệt) và REQ-BR-11 (chặn đóng PR khi thiếu hàng) chặn đứng vi phạm tại tầng CSDL transaction.
- **Database Persistence:** Bản ghi trạng thái `CLOSED` và quyết toán ngân sách phòng ban được lưu trữ bền vững trên Supabase Cloud.

### Fixed
- **CORS Configuration:** Khắc phục lỗi cấu hình CORS trong `backend/app/main.py` (loại bỏ wildcard `allow_origins=["*"]` xung đột với `allow_credentials=True`, thay bằng explicit allowed origins).
- **Vercel Hostname Resolution:** Khắc phục lỗi `DNS_HOSTNAME_RESOLVE_FAILED` bằng cách thiết lập `VITE_API_URL` trong frontend môi trường để gọi trực tiếp Railway API.
- **Container Restart Auth Session:** Xử lý triệt để lỗi 401 sau khi Railway tái khởi động container thông qua bước seed idempotent.
- **UI Price Display:** Loại bỏ số 0 thừa ở đầu đơn giá báo giá và cập nhật màu nút "Lưu ý cấu trúc" sang màu xanh dương chuẩn Figma trong `CollectQuotationsView.tsx`.

### Known Limitations
- Gemini Live API ở trạng thái `UNVERIFIED`; vận hành chính thức trên nhánh Fallback Heuristic có trọng số (độ tin cậy 78%).
- Kịch bản kiểm thử trình duyệt thực thi qua Puppeteer (`test_final_full_lifecycle_e2e.js`), Playwright spec chưa được thiết lập độc lập.
- Giao diện người dùng đóng gói dạng single-bundle (649 kB), điều hướng thông qua state view trong `App.tsx`.
- Bằng chứng kiểm thử trải nghiệm người dùng (`Deliverable 2.4 Usability Test`) đang ở trạng thái `PENDING REAL USER TEST` chờ đo lường trên $\ge 3$ người dùng thật.

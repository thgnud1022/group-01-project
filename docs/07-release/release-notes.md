# RELEASE NOTES: AI Procurement & Purchase Approval System

- **Phiên bản (Target Version):** `v1.0.0-final`
- **Mã commit Release Candidate:** `cc848479a5fb2ed7353dd22ca2a8d353666597e7`
- **Nhánh Git:** `final-delivery`
- **Ngày lập:** 2026-10-05
- **Trạng thái thẩm định:** `RELEASE READY WITH KNOWN LIMITATIONS` (Đã xác minh kỹ thuật trên live stack; chờ hoàn thiện Deploy URL và Usability Test thật)

---

## 1. Tổng quan & Phạm vi Phát hành (Release Scope)

Bản phát hành `v1.0.0-final` hiện thực hóa trọn vẹn chu trình mua sắm doanh nghiệp nội bộ (End-to-End Procurement Lifecycle) với sự tham gia của AI ở vai trò tư vấn ra quyết định (Decision Support / Advisory), kết hợp cơ chế kiểm soát ngân sách thời gian thực và phân quyền máy chủ nghiêm ngặt (Zero-Trust Server-Side RBAC).

### Các tính năng đã được kiểm chứng thực nghiệm (Verified Capabilities):
1. **Xác thực & Danh tính Zero-Trust (Authentication & Identity):**
   - Xác thực JWT Supabase qua JWKS (thuật toán chữ ký ES256) với cơ chế timeout mạng 5.0s chống treo socket.
   - Ánh xạ danh tính an toàn `authUserId` liên kết giữa Supabase Auth và bảng `User` trong PostgreSQL.
   - Cô lập hoàn toàn cơ chế mock auth cũ, từ chối client identity injection.
2. **Kiểm soát Truy cập Phân quyền Máy chủ (Server-Side RBAC & Governance):**
   - `RoleChecker` bảo vệ 100% 19/19 REST API endpoints theo đúng ma trận phân quyền (EMPLOYEE, MANAGER, PROCUREMENT, FINANCE, ADMIN).
   - Thực thi triệt để nguyên tắc **Không tự phê duyệt (No Self-Approval — GOV-01 / HD-13)** tại tầng dịch vụ cho mọi vai trò (kể cả Quản trị viên).
3. **Quản lý Yêu cầu Mua sắm (Purchase Request Management):**
   - Tạo PR với đầy đủ thông số hàng hóa, đơn giá ước tính, phòng ban và mức độ ưu tiên.
   - Hàng đợi phê duyệt (Approval Queue) hỗ trợ Trưởng bộ phận thực hiện Phê duyệt (`APPROVED`), Từ chối (`REJECTED`) hoặc Yêu cầu chỉnh sửa (`REVISION_REQUIRED`).
   - Kiểm tra ngân sách tự động (Budget Guard) và tạm giữ ngân sách (`tempReservedAmount`) khi PR được phê duyệt.
4. **Quản lý Nguồn cung & Nhà cung cấp (Sourcing & Supplier Management):**
   - Tạo mới, tra cứu danh sách và xem chi tiết thông tin nhà cung cấp (tuân thủ phạm vi HD-15).
5. **Thu thập & So sánh Báo giá (Quotation Collection & Comparison):**
   - Thu thập nhiều báo giá cho PR đã duyệt với đơn giá, số lượng và thời hạn hiệu lực (`validUntil`).
   - Màn hình đối sánh báo giá đa chiều (Side-by-side comparison) theo thiết kế Figma 9:4373 và 9:4790, hỗ trợ kiểm tra hạn báo giá thực tế.
6. **Tư vấn Phân tích Báo giá AI (AI Quotation Advisory):**
   - Thẻ khuyến nghị tư vấn tích hợp trong màn hình so sánh, cung cấp phân tích đánh đổi (trade-offs) về giá cả, thời gian giao hàng, bảo hành và rủi ro.
   - Cơ chế bảo vệ: AI chỉ đóng vai trò khuyến nghị (Advisory Only), không tự động tạo PO trên CSDL.
7. **Trao thầu Con người & Khóa Đơn đặt hàng (Human Award & PO Lock Price):**
   - Quyết định trao thầu hoàn toàn thuộc về con người (Human Award Selection).
   - Tạo Purchase Order khóa cứng 100% đơn giá và số lượng từ báo giá trúng thầu (HD-08 Option A: mã PO định dạng `PO-NUM-YYYY-YYYYMMDD-XXXXXXXX`).
   - Guard REQ-BR-10 / HD-04 trong transaction PostgreSQL chặn tuyệt đối việc tạo PO từ PR chưa được duyệt (`APPROVED`).
8. **Nhận hàng & Quyết toán Đóng PR (Goods Receiving & Close PR):**
   - Ghi nhận biên bản nhận hàng từng phần (Partial) hoặc nhận đủ (Complete).
   - Guard REQ-BR-11 / HD-07 (`SUM(receivedQty) >= PO.quantity`) chặn hoàn toàn thao tác đóng PR nếu chưa nhận đủ 100% số lượng.
   - Quyết toán ngân sách: hoàn ứng tạm giữ về 0 và ghi nhận chính xác chi phí thực tế (`spentAmount`).
9. **Lưu trữ Bền vững CSDL (Database Persistence):**
   - Hệ quản trị CSDL Supabase PostgreSQL quản lý bởi Prisma Client Python v0.15.0, hỗ trợ khóa dòng `SELECT ... FOR UPDATE` chống xung đột giao dịch.

---

## 2. Kết quả Thẩm định Chất lượng (Verified Quality Gates)

Toàn bộ các chỉ số dưới đây đã được kiểm chứng độc lập trên live stack tại commit `cc848479a5fb2ed7353dd22ca2a8d353666597e7`:

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
  - Xác nhận trực tiếp qua `backend/scratch/lifecycle_db_verifier.py` trên live PostgreSQL:
    - PR `PR-2026-029`: trạng thái `CLOSED`.
    - Quotations: 2 bản ghi.
    - Purchase Order: 1 bản ghi mã `PO-NUM-2026-20261005-288028BC` trạng thái `CLOSED`.
    - Tổng hàng nhận: 5/5 thiết bị qua 2 biên bản nhận hàng.
    - Ngân sách phòng CNTT: `spentAmount = 306.000.000 VNĐ`, `tempReservedAmount = 0 VNĐ`.
* **Đóng gói Giao diện (Frontend Production Build):**
  - Lệnh `npm.cmd run build` hoàn thành trong 4.05s, 0 lỗi TypeScript, sinh bundle tĩnh sẵn sàng phục vụ (`dist/assets/index-Cp5TiUOm.js`, kích thước 649.36 kB).

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
2. **Công cụ Kiểm thử Trình duyệt E2E là Puppeteer:** Kịch bản kiểm thử tự động 14 bước sử dụng `puppeteer-core`. Kiểm thử bằng Playwright chưa được thiết lập trong đợt kiểm định này.
3. **Kiến trúc Giao diện Đơn khối (Single-Bundle):** Giao diện được cấu trúc dạng các view thành phần điều hướng nội bộ trong `App.tsx`, bundle đơn khối kích thước 649.36 kB, chưa tách route hoàn chỉnh bằng React Router đa trang.
4. **Chưa có Public Demo URL:** Ứng dụng hiện vận hành và kiểm chứng trên môi trường local stack (`localhost:5173` / `localhost:8000`), chưa được triển khai lên hạ tầng đám mây công cộng (Vercel / Render).
5. **Dữ liệu Usability Test thật đang chờ ghi nhận:** Bộ kịch bản và template kiểm thử trải nghiệm người dùng đã hoàn tất chuẩn bị tại `docs/03-product/usability-findings.md` nhưng kết quả thực nghiệm từ $\ge 3$ người dùng thật cần nhóm sinh viên tổ chức thực hiện trước khi nộp đồ án.

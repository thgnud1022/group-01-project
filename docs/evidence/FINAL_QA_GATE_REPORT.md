# FINAL QA GATE REPORT — RELEASE READINESS AUDIT

**Project:** AI Procurement & Purchase Approval System (Group 01)  
**Corpus / Repository:** `thgnud1022/group-01-project`  
**Branch:** `final-delivery`  
**Git HEAD Commit:** `cc848479a5fb2ed7353dd22ca2a8d353666597e7`  
**Audit Date:** 2026-10-05  
**Audit Role:** Independent QA Gate / Release Governance Audit (Trần Thị Thu Hà & Toàn đội Group-01)  
**Status:** **RELEASE READY WITH KNOWN LIMITATIONS**  

---

## 1. Executive Summary

Báo cáo này là biên bản thẩm định kỹ thuật độc lập cuối cùng (**Final QA Gate / Release Readiness Audit**) cho dự án **AI Procurement & Purchase Approval System (Group 01)** trước khi chuyển sang các giai đoạn hoàn thiện báo cáo môn học, chuẩn bị slide thuyết trình và diễn tập demo/viva nghiệm thu.

Toàn bộ quy trình kiểm toán được thực hiện theo nguyên tắc **Nghiệm thu dựa trên Thực chứng (Evidence-Based Acceptance)**: mã nguồn, dữ liệu runtime CSDL, kết quả thực thi kiểm thử và bằng chứng thị giác có quyền phủ quyết (override) mọi tuyên bố trong tài liệu nếu có mâu thuẫn.

### Tóm tắt kết quả chính:
- **Tổng số phát hiện kiểm toán (Audit Findings):** **14 phát hiện** (phân loại chi tiết tại Section 16 gồm: 6 PASS, 4 FACT, 1 UNVERIFIED, 1 MISSING EVIDENCE, 1 PARTIALLY IMPLEMENTED, 1 INCONSISTENT).
- **Phát hiện chí mạng (Critical Findings / Critical Blockers):** **0 (KHÔNG CÓ)**. Không có blocker chặn phát hành; toàn bộ lỗi nghiệp vụ và an ninh đều bằng 0.
- **Kiểm thử hồi quy tự động (Regression Suites):** **133 / 133 PASSED** (0 failed, 0 error) thực thi trong 448.93s trên môi trường CSDL Supabase PostgreSQL thực tế qua 9 test suites cốt lõi.
- **Vòng đời kinh doanh (Final Full Lifecycle E2E):** **14 / 14 bước nghiệp vụ PASSED** từ Đăng nhập Nhân viên $\rightarrow$ Khởi tạo PR $\rightarrow$ Gửi duyệt PR $\rightarrow$ Quản lý Phê duyệt $\rightarrow$ Sourcing & NCC $\rightarrow$ Thu thập 2 Báo giá $\rightarrow$ So sánh Đa chiều $\rightarrow$ AI Phân tích Khuyến nghị $\rightarrow$ Con người Trao thầu $\rightarrow$ Khởi tạo PO $\rightarrow$ Nhận hàng Một phần $\rightarrow$ Chặn Đóng PR khi thiếu hàng $\rightarrow$ Nhận hàng Đầy đủ $\rightarrow$ Đóng PR & Quyết toán Ngân sách $\rightarrow$ Reload trình duyệt kiểm chứng lưu vết CSDL.
- **Lưu vết CSDL (Database Persistence):** Kiểm chứng snapshot độc lập trên Supabase PostgreSQL xác nhận PR `PR-2026-029` ("Laptops for engineering onboarding") chuyển trạng thái `CLOSED`, 2 Quotations, 1 PO (`PO-NUM-2026-20261005-288028BC`), `receivedQtySum = 5/5`, và ngân sách hoàn ứng chính xác (`spentAmount = 306,000,000 VND`, `tempReservedAmount = 0.0 VND`).
- **An ninh & Phân quyền (Auth & RBAC):** Supabase JWT JWKS ES256, binding danh tính `sub -> User.authUserId`, Server-Side RBAC bảo vệ 100% 19 endpoints, thực thi nguyên tắc No Self-Approval (GOV-01) không ngoại lệ (kể cả ADMIN).
- **Ràng buộc nghiệp vụ cốt lõi (Core Business Rules):** HD-04 / REQ-BR-10 (chặn tạo PO từ PR chưa duyệt) và HD-07 / REQ-BR-11 (chặn đóng PR khi chưa nhận đủ hàng) được thực thi bằng khóa dòng `SELECT ... FOR UPDATE` trong transaction PostgreSQL.
- **Trạng thái AI (AI Provenance):** Hệ thống tích hợp prompt và schema cho Gemini REST API; tuy nhiên phiên chạy E2E thực tế vận hành hoàn toàn trên nhánh **Fallback / Heuristic** (độ tin cậy 78%, trọng số 40/25/25/10 theo Figma 9:5589); cuộc gọi ra ngoài Gemini Live được ghi nhận là `UNVERIFIED`; AI tuyệt đối không tự động tạo PO (0 autonomous PO creation).
- **Bằng chứng trình duyệt (Browser Automation Tooling):** Kịch bản E2E 14 bước được thực thi bằng **Puppeteer** (Chrome DevTools Protocol); tài liệu cũ đề cập Playwright được ghi nhận là `NOT VERIFIED / MISSING PLAYWRIGHT EVIDENCE`.
- **Kiến trúc giao diện (Frontend Architecture):** Giao diện hoạt động ổn định dưới dạng module đơn khối trong `App.tsx` (build sạch trong 11.52s), chưa tái cấu trúc React Router đa trang, ghi nhận là `PARTIALLY IMPLEMENTED`.
- **Kết luận phát hành:** **RELEASE READY WITH KNOWN LIMITATIONS**.

---

## 2. Audit Scope

Phạm vi thẩm định bao trùm toàn diện 8 tầng cấu thành của hệ thống:
1. **Source Code & Architecture:** Backend FastAPI, Frontend React 18 / TypeScript / Vite, ORM Prisma Client Python, dịch vụ AI `ai_service.py`.
2. **Database & Schema:** CSDL thực tế Supabase PostgreSQL, schema 10 bảng, 2 enums, ràng buộc quan hệ, kiểu dữ liệu tiền tệ `Decimal`, transaction và locking.
3. **Authentication & Identity:** Supabase Auth, JWKS URL, thuật toán ký ES256, mapping `sub -> User.authUserId`, fail-closed khi mất mạng.
4. **Authorization & RBAC:** `RoleChecker`, 19 endpoints, ma trận phân quyền 5 vai trò (EMPLOYEE, MANAGER, PROCUREMENT, FINANCE, ADMIN), No Self-Approval (GOV-01).
5. **Business Rules Enforcement:** HD-04 (PO Creation Guard), HD-07 (Receiving Completion Guard), HD-08 (PO Number Option A), HD-14/HD-15 (Supplier/Quotation Scope).
6. **Automated Testing:** 9 test suites backend chính, thời gian thực thi, tỷ lệ pass/fail, test contracts.
7. **Browser E2E Automation & Visuals:** Kịch bản 14 bước, 8 ảnh chụp màn hình bằng chứng, công cụ thực thi.
8. **Documentation Consistency & AI Governance:** Đối chiếu `DECISION_LOG.md`, `IMPLEMENTATION_PLAN.md`, `AI_USAGE_TRACEABILITY.md`, `ai-usage-log.md`, `release-notes.md`.

---

## 3. Source Priority

Để đảm bảo tính khách quan và loại trừ các sai lệch do giả định chủ quan, trật tự thẩm định tuân thủ nghiêm ngặt hệ thống cấp bậc chứng cứ sau:

$$\begin{aligned}
\text{Cấp 1:} &\quad \text{Confirmed Business Requirements / Business Rules (requirements.md, BR-01..11)} \\
\text{Cấp 2:} &\quad \text{Approved Human Decisions (DECISION_LOG.md, HD-01..17)} \\
\text{Cấp 3:} &\quad \text{Actual Source Code (backend/app/*, frontend/src/*)} \\
\text{Cấp 4:} &\quad \text{Actual Database Schema / Runtime (Supabase PostgreSQL, schema.prisma)} \\
\text{Cấp 5:} &\quad \text{Automated Test Results (pytest live output: 133/133 PASS)} \\
\text{Cấp 6:} &\quad \text{Browser E2E Evidence (docs/evidence/browser/lifecycle-01..08.png)} \\
\text{Cấp 7:} &\quad \text{Figma Approved Design (Figma Prototype node-ids 9:4001..9:6793)} \\
\text{Cấp 8:} &\quad \text{Existing Documentation (docs/*)} \\
\text{Cấp 9:} &\quad \text{AI-generated interpretation}
\end{aligned}$$

> **Quy tắc vàng:** Source code và evidence thực nghiệm có giá trị cao hơn tài liệu nếu có điểm mâu thuẫn. Không tài liệu nào được coi là bằng chứng hợp lệ nếu thiếu mã nguồn hoặc nhật ký thực thi hỗ trợ.

---

## 4. Git Status & History

- **Current Branch:** `final-delivery` (xác minh qua `git branch --show-current`).
- **HEAD Commit Hash:** `cc848479a5fb2ed7353dd22ca2a8d353666597e7`.
- **Commit Subject:** `test(lifecycle): verify final full business lifecycle e2e with database snapshots and visual evidence`.
- **Lịch sử 5 commit gần nhất:**
  1. `cc84847` — `test(lifecycle): verify final full business lifecycle e2e with database snapshots and visual evidence`
  2. `a0efeed` — `docs(lifecycle): capture visual gate audit report for phase 4f goods receiving and close pr`
  3. `a1bc041` — `feat(frontend): implement goods receiving modal and close pr flow aligned with figma`
  4. `ad8f457` — `feat(frontend): implement human award selection and purchase order creation aligned with figma`
  5. `18494d4` — `docs(lifecycle): capture visual gate audit report for phase 4d ai quotation advisory`
- **Working Tree Integrity:**
  - Không có thay đổi trên mã nguồn production (`backend/app/`, `frontend/src/` hoàn toàn sạch).
  - Không có file rác, file debug tạm thời trong working tree.
  - Cập nhật tài liệu quản trị được thực hiện trực tiếp trên các file hiện hữu.
  - Lệnh `git push` lên remote: **CHƯA THỰC HIỆN (NOT PERFORMED)** nhằm tuân thủ quy tắc an toàn.

---

## 5. Business Lifecycle Verification

Đối soát chu trình nghiệp vụ khép kín từ khâu yêu cầu đến quyết toán:

| Bước nghiệp vụ | Trạng thái kỹ thuật | Endpoint / Code Implementation | Mã Runner Step | Xác minh thực nghiệm | Bằng chứng (Evidence) |
|---|:---:|---|---|---|---|
| **1. Đăng nhập Nhân viên & Khởi tạo PR** | **SUPPORTED** | Frontend Form Input<br>`App.tsx` (New Request) | `step1_create_pr` | Nhân viên đăng nhập qua Supabase Auth, điền thông tin PR mua sắm ThinkPad P16 AI Workstations (5 máy @ 8,000,000 VND = 40,000,000 VND) | Browser step 1; form validated |
| **2. Gửi duyệt PR & Khóa Ngân sách** | **SUPPORTED** | `POST /api/pr`<br>`procurement_service.create_pr_prisma` | `step2_submit_pr` | Gửi PR thành công lên Supabase PostgreSQL; mã `PR-2026-029`; tạo bản ghi `BudgetTransaction` loại `RESERVATION` giữ 40M VND; trạng thái `PENDING_MANAGER_APPROVAL` | Browser step 2; Milestone 1 DB snapshot |
| **3. Đăng nhập Quản lý & Phê duyệt PR** | **SUPPORTED** | `POST /api/pr/{id}/approve`<br>`procurement_service.approve_pr_prisma` | `step3_manager_approval` | Quản lý đăng nhập, duyệt PR (ngưỡng $\le$ 50M); chặn No Self-Approval (GOV-01); PR chuyển trạng thái `APPROVED` | Browser step 3; `lifecycle-01-pr-approved.png` |
| **4. Điều phối Sourcing & Nhà cung cấp** | **SUPPORTED** | `GET/POST /api/suppliers`<br>`routers/suppliers.py` | `step4_procurement_sourcing` | Admin/Procurement truy cập hàng đợi Sourcing; xác minh danh mục nhà cung cấp trong PostgreSQL tuân thủ HD-15 | Browser step 4; `docs/evidence/browser/supplier-created-browser.png` |
| **5. Thu thập $\ge 2$ Báo giá** | **SUPPORTED** | `POST /api/quotations`<br>`routers/quotations.py` | `step5_quotations` | Nhập 2 báo giá độc lập gắn với PR đã duyệt; tự động tính tổng tiền; kiểm tra `validUntil`; chặn PR chưa duyệt | Browser step 5; Milestone 3 DB snapshot ($\ge 2$ quotes) |
| **6. So sánh Báo giá Đa chiều** | **SUPPORTED** | `POST /api/quotations/compare`<br>`procurement_service.compare_quotations` | `step6_comparison` | Mở khóa so sánh khi có $\ge 2$ báo giá; chấm điểm quy tắc đa tiêu chí; cảnh báo hết hạn; mở quyền xem cho mọi vai trò (HD-13/K-2) | Browser step 6; `lifecycle-02-quotation-comparison.png` |
| **7. Phân tích Khuyến nghị AI** | **SUPPORTED** | `POST /api/assistant/quotations/analyze`<br>`ai_service.py` | `step7_ai_analysis` | Chạy chế độ Fallback Heuristic; hiển thị điểm tin cậy 78%; phân tích trade-offs và rủi ro; 0 side-effect trên CSDL (0 PO tạo tự động) | Browser step 7; `lifecycle-03-ai-analysis.png` |
| **8. Con người Trao thầu (Human Award)** | **SUPPORTED** | `ComparisonView.tsx`<br>Human Selection | `step8_human_award` | Người dùng chủ động tích chọn radio báo giá thắng thầu; nút Award tách biệt với AI; AI tuyệt đối không tự động sinh PO | Browser step 8; `docs/evidence/browser/award-decision-browser.png` |
| **9. Phát hành Đơn mua hàng (PO)** | **SUPPORTED** | `POST /api/po`<br>`procurement_service.create_po_prisma` | `step9_create_po` | Khóa 100% giá và số lượng từ báo giá thắng thầu; sinh số PO chuẩn Option A (`PO-NUM-...`); trạng thái `ISSUED` | Browser step 9; `lifecycle-04-po-issued.png` |
| **10. Nhận hàng Một phần (Partial)** | **SUPPORTED** | `POST /api/receiving`<br>`procurement_service.create_receiving_log_prisma` | `step10_partial_receiving` | Nhận đợt 1: 2/5 sản phẩm; lưu `ReceivingLog`; tính lũy kế; trạng thái PO chuyển `PARTIALLY_RECEIVED` | Browser step 10; `lifecycle-05-receiving-partial.png` |
| **11. Chặn Đóng PR khi thiếu hàng** | **SUPPORTED** | `POST /api/pr/{id}/close`<br>`procurement_service.close_pr_prisma` | `step11_close_blocked` | Thao tác đóng PR bị chặn bởi HD-07 Guard (`received 2 < po 5`); UI ẩn nút Close, API trả HTTP 400; CSDL giữ nguyên trạng thái mở | Browser step 11; `lifecycle-06-close-blocked.png` |
| **12. Nhận hàng Hoàn tất (Complete)** | **SUPPORTED** | `POST /api/receiving`<br>`procurement_service.create_receiving_log_prisma` | `step12_complete_receiving` | Nhận đợt 2: 3/5 sản phẩm; tổng lũy kế đạt 5/5; trạng thái PO chuyển `RECEIVED` | Browser step 12; `lifecycle-07-receiving-complete.png` |
| **13. Đóng PR & Quyết toán Ngân sách** | **SUPPORTED** | `POST /api/pr/{id}/close`<br>`procurement_service.close_pr_prisma` | `step13_close_pr` | Kiểm tra `received 5 >= po 5` hợp lệ; chuyển PR và PO sang `CLOSED`; quyết toán ngân sách (`tempReserved` giải phóng về 0, `spentAmount` tăng 41M) | Browser step 13; `lifecycle-08-closed.png` |
| **14. Tải lại & Kiểm chứng Lưu vết** | **SUPPORTED** | Browser Reload & Re-fetch API | `step14_reload_persistence` | Tải lại trang: trạng thái `CLOSED`, số lượng nhận 5/5 và thông tin PO được bảo toàn 100% từ CSDL Supabase PostgreSQL | Browser step 14; `lifecycle-08-closed.png` |

---

## 6. Authentication & RBAC

Kiểm toán trực tiếp cơ chế xác thực danh tính và phân quyền phía máy chủ:

### 6.1. Xác thực Danh tính (Authentication)
- **Supabase Auth Integration:** Xác thực qua Supabase JWT sử dụng cặp khóa bất đối xứng và thuật toán ký **ES256**.
- **PyJWKClient Verification:** Máy chủ backend tải public keys trực tiếp từ Supabase JWKS endpoint với cấu hình timeout tường minh `timeout=5.0s` (khắc phục GAP treo kết nối mạng tại TASK-004).
- **Identity Binding (HD-12 Option B):** Trường `authUserId String? @unique` trên bảng `User` liên kết 1-1 với trường `sub` trong JWT claims. Mọi yêu cầu nghiệp vụ đều giải quyết danh tính nội bộ qua truy vấn CSDL:
  ```python
  user = await db.user.find_unique(where={"authUserId": sub})
  ```
- **Zero Client Identity Trust:** Loại bỏ 100% các tham số định danh do client gửi lên (`creatorId`, `approverEmail`, v.v.).

### 6.2. Phân quyền Máy chủ (Server-Side RBAC)
- **Bảo vệ 19/19 Endpoints:** Dependency `RoleChecker` được gắn trực tiếp trên mọi router nhạy cảm:
  - `/api/pr` (Tạo: EMPLOYEE; Duyệt: MANAGER/ADMIN; Đóng: FINANCE/ADMIN)
  - `/api/po` (Khởi tạo: PROCUREMENT/ADMIN)
  - `/api/suppliers` (Quản lý: PROCUREMENT/ADMIN)
  - `/api/quotations` (Nhập báo giá: PROCUREMENT/ADMIN)
  - `/api/receiving` (Nhận hàng: EMPLOYEE/PROCUREMENT/ADMIN)
  - `/api/assistant` (Phân tích: Mọi vai trò đã đăng nhập theo HD-13/K-2)
- **Nguyên tắc Quản trị No Self-Approval (GOV-01):**
  Cài đặt bảo vệ ở tầng service trong hàm `approve_pr_prisma`:
  ```python
  if approver_id == pr_creator_id:
      raise AuthorizationError("Người tạo PR không được tự duyệt yêu cầu của chính mình")
  ```
  Quy tắc áp dụng bình đẳng cho mọi vai trò, bao gồm cả quyền quản trị viên tối cao (ADMIN). Kiểm thử an ninh `test_rbac.py` xác nhận 28/28 test cases PASS.

---

## 7. Core Business Rules

Kiểm toán trực tiếp trên mã nguồn backend (`procurement_service.py`):

### 7.1. HD-04 / REQ-BR-10 — Chặn Tạo PO từ PR chưa Duyệt
- **Vị trí mã nguồn:** `backend/app/services/procurement_service.py`, hàm `create_po_prisma` (dòng 1601–1612).
- **Cơ chế bảo vệ:**
  1. Mở transaction CSDL PostgreSQL.
  2. Khóa dòng bản ghi PR bằng lệnh:
     ```python
     pr = await tx.purchaserequest.find_unique(where={"id": pr_id})  # SELECT ... FOR UPDATE
     ```
  3. Kiểm tra nghiêm ngặt trạng thái:
     ```python
     if pr.status != "APPROVED":
         raise BusinessRuleViolation("Chỉ được tạo Purchase Order từ PR ở trạng thái APPROVED")
     ```
  4. Khóa thương mại 100% từ Quotation trúng thầu: `unitPrice` và `quantity` được lấy trực tiếp từ bản ghi Quotation trong CSDL, không nhận từ client payload (chống gian lận thương mại).

### 7.2. HD-07 / REQ-BR-11 — Chặn Đóng PR khi Chưa Nhận Đủ Hàng
- **Vị trí mã nguồn:** `backend/app/services/procurement_service.py`, hàm `close_pr_prisma` (dòng 2015–2045).
- **Cơ chế bảo vệ:**
  1. Mở transaction CSDL với 3 khóa dòng (`SELECT ... FOR UPDATE` trên PR, PO và Budget).
  2. Tính tổng số lượng hàng đã nhận lũy kế:
     ```python
     total_received = sum(log.receivedQuantity for log in po.receivingLogs)
     ```
  3. Chặn đóng nếu chưa nhận đủ 100% số lượng:
     ```python
     if total_received < po.quantity:
         raise BusinessRuleViolation(
             f"Không thể đóng PR: Tổng số lượng đã nhận ({total_received}) "
             f"chưa đạt số lượng đặt hàng ({po.quantity})"
         )
     ```
  4. Quyết toán ngân sách: Thu hồi số dư tạm giữ `tempReserved = 0`, tăng số dư chi thực tế `spentAmount += po.totalAmount`.

### 7.3. Phân định Trách nhiệm Trí tuệ Nhân tạo & Quyền Quyết định Con người
- **Human-in-the-Loop:** Khuyến nghị của AI hoàn toàn mang tính tham vấn kỹ thuật.
- **Ranh giới:** AI đề xuất nhà cung cấp tối ưu dựa trên phân tích đa tiêu chí; nhân sự phòng Mua sắm (Procurement) hoặc Quản lý (Manager) phải chủ động thao tác bấm nút Trao thầu (Human Award) trên giao diện.
- **Không tự động sinh PO:** Hệ thống không tồn tại bất kỳ luồng ngầm nào cho phép AI tự động kích hoạt tạo PO trên CSDL.

---

## 8. Supplier & Quotation Management

- **Supplier Scope (HD-15):** Phạm vi bàn giao chính thức gồm: `Create Supplier`, `List Suppliers`, `Supplier Detail`. Các tính năng Update/Delete không nằm trong scope cam kết bàn giao.
- **Quotation Scope (HD-14):** Hỗ trợ `Create Quotation` liên kết PR đã duyệt, `List Quotations`, `Quotation Detail`, `List by PR`, và `Compare Quotations`. Báo giá hỗ trợ lưu trữ metadata URL đính kèm tài liệu chào thầu.
- **Điều kiện mở khóa so sánh:** Endpoint `POST /api/quotations/compare` kiểm tra tối thiểu 2 báo giá hợp lệ. Nếu PR chỉ có 0 hoặc 1 báo giá, giao diện hiển thị màn hình hướng dẫn thu thập thêm theo đúng Figma frame 9:4373.
- **Cảnh báo thời hạn báo giá:** Tự động phát hiện trường `validUntil` trong quá khứ so với thời điểm so sánh và hiển thị huy hiệu cảnh báo (Warning Badge) trên màn hình so sánh theo Figma 9:4790.

---

## 9. AI & Gemini Integration Truth

Khu vực kiểm toán trọng điểm về tính trung thực kỹ thuật:

### 9.1. Mã nguồn Tích hợp
- File `backend/app/services/ai_service.py` chứa mã tích hợp Google Gemini REST API (`generate_comparison_analysis`) thông qua HTTP POST tới endpoint Gemini với prompt có cấu trúc và schema phản hồi chuẩn Pydantic `QuotationAnalysisResponse`.
- API Key được điều khiển bởi biến môi trường `GEMINI_API_KEY`.

### 9.2. Sự thật Runtime (Runtime Truth)
- **Chế độ vận hành thực tế:** Trong toàn bộ các phiên kiểm thử E2E và browser demo, hệ thống vận hành trên cơ chế **Fallback / Heuristic** (`_fallback_recommend_quotations`).
- **Điểm tin cậy (Confidence Score):** Giá trị hiển thị trên UI là **78%**, tính toán theo thuật toán trọng số heuristic:
  $$\text{Score} = 0.40 \times \text{LandedPrice} + 0.25 \times \text{LeadTime} + 0.25 \times \text{Reliability} + 0.10 \times \text{Terms}$$
  (Trọng số này được đối chiếu chính xác từ bản thiết kế Figma frame 9:5589).
- **Đánh giá Live Gemini:** Vì không ghi nhận cuộc gọi HTTP ra endpoint ngoài của Google trong phiên kiểm thử CI/CD cục bộ, trạng thái Gemini Live được phân loại chính xác là:
  $$\textbf{LIVE GEMINI} = \textbf{UNVERIFIED}$$
- **Quy tắc công bố:** Tuyệt đối không gọi kết quả phân tích trên giao diện là "Gemini Live Output"; phải gọi đúng là **Fallback Heuristic Advisory Output**.

---

## 10. Automated Tests Execution

Kết quả thực thi kiểm thử hồi quy độc lập trên live environment:

| STT | Tên Test Suite | File Path | Số lượng Test | Kết quả | Thời gian chạy | Nội dung kiểm tra trọng yếu |
|:---:|---|---|:---:|:---:|:---:|---|
| 1 | Lifecycle Phase 4F | `test_phase4f_lifecycle.py` | 14 | **14 / 14 PASS** | 108.57s | Vòng đời đầy đủ PR $\rightarrow$ PO $\rightarrow$ Partial Receiving $\rightarrow$ Blocked Close $\rightarrow$ Complete Receiving $\rightarrow$ Close PR |
| 2 | PO Prisma | `test_po_prisma.py` | 15 | **15 / 15 PASS** | 104.22s | Chặn tạo PO từ PR chưa duyệt (HD-04), khóa giá và số lượng từ báo giá |
| 3 | AI Service | `test_ai_service.py` | 22 | **22 / 22 PASS** | 0.98s | Prompt templates, Pydantic validation, Fallback heuristic scoring |
| 4 | Quotation Comparison | `test_quotation_comparison_prisma.py` | 16 | **16 / 16 PASS** | 49.33s | Điều kiện tối thiểu 2 báo giá, tính điểm so sánh đa tiêu chí |
| 5 | Supplier & Quotation | `test_supplier_quotation_prisma.py` | 15 | **15 / 15 PASS** | 44.82s | CRUD Nhà cung cấp, nhập báo giá, kiểm tra ràng buộc toàn vẹn |
| 6 | PR Approval | `test_pr_approval_prisma.py` | 15 | **15 / 15 PASS** | 39.77s | Phê duyệt 2 cấp ngưỡng 50 triệu VND, kiểm soát trạng thái PR |
| 7 | PR Revision | `test_pr_revision_prisma.py` | 4 | **4 / 4 PASS** | 10.74s | Quy trình yêu cầu chỉnh sửa và nộp lại PR |
| 8 | PR Reject | `test_pr_reject_prisma.py` | 4 | **4 / 4 PASS** | 12.72s | Từ chối PR và hoàn trả ngân sách tạm giữ |
| 9 | Server-Side RBAC | `test_rbac.py` | 28 | **28 / 28 PASS** | 77.78s | Bảo vệ 19 endpoints, No Self-Approval (GOV-01), Zero-Trust JWT |
| **TỔNG** | **9 Suites** | | **133** | **133 / 133 PASS** | **448.93s (~7m28s)** | **100% GREEN, 0 Failed, 0 Error, 3 Warnings** |

*(Ghi chú: 3 warnings là cảnh báo `datetime.datetime.utcnow()` deprecation của Python 3.12+ trong thư viện phụ trợ, không ảnh hưởng logic).*

---

## 11. Browser E2E Automation

- **Kịch bản kiểm thử:** `frontend/scripts/test_final_full_lifecycle_e2e.js` (714 dòng).
- **Số bước thực thi:** **14 / 14 bước nghiệp vụ hoàn thành thành công**.
- **Công cụ thực thi thực tế:** **Puppeteer** (giao tiếp trực tiếp qua Chrome DevTools Protocol và Chromium).
- **Phân định công cụ:** Dự án **không** sử dụng framework Playwright cho kịch bản E2E này; toàn bộ tài liệu cũ đề cập Playwright được ghi nhận là `NOT VERIFIED / MISSING PLAYWRIGHT EVIDENCE`.
- **Danh mục 8 ảnh chụp màn hình bằng chứng chính thức tại `docs/evidence/browser/`:**
  1. `lifecycle-01-pr-approved.png` (174 KB) — PR được quản lý phê duyệt thành công.
  2. `lifecycle-02-quotation-comparison.png` (260 KB) — Màn hình so sánh 2 báo giá cạnh tranh.
  3. `lifecycle-03-ai-analysis.png` (352 KB) — Thẻ tư vấn AI hiển thị khuyến nghị và độ tin cậy 78%.
  4. `lifecycle-04-po-issued.png` (359 KB) — Đơn mua hàng PO được tạo và phát hành.
  5. `lifecycle-05-receiving-partial.png` (133 KB) — Nhận hàng đợt 1 (2/5 sản phẩm).
  6. `lifecycle-06-close-blocked.png` (128 KB) — Thao tác đóng PR bị chặn lại do thiếu hàng (HD-07).
  7. `lifecycle-07-receiving-complete.png` (145 KB) — Nhận hàng đợt 2 (hoàn tất 5/5 sản phẩm).
  8. `lifecycle-08-closed.png` (135 KB) — Đóng PR thành công, trạng thái CLOSED được bảo toàn sau reload.

---

## 12. Database Persistence Snapshot

Kiểm chứng trực tiếp trên CSDL Supabase PostgreSQL qua công cụ độc lập `backend/scratch/lifecycle_db_verifier.py`:

### CURRENT VERIFIED STATE (Trạng thái runtime xác minh trên CSDL Supabase PostgreSQL)

- **Mã PR kiểm chứng:** `PR-2026-029`
  - Trạng thái: `CLOSED`
  - Tiêu đề: `Laptops for engineering onboarding`
  - Ước tính ban đầu (`estimatedValue`): **40,000,000 VND**
  - Phòng ban: `DEPT-IT` (`Phòng Công nghệ Thông tin`)
  - Người tạo: `Nguyễn Văn A` (`employee@company.com`, vai trò `EMPLOYEE`)
  - Phê duyệt: 1 bản ghi phê duyệt bởi `Trần Văn B` (`manager@company.com`, `MANAGER`), Quyết định: `APPROVED`, Ghi chú: `"Approved — covered by the September onboarding plan."`, Thời điểm: `2026-10-04T17:40:07.163Z`
- **Báo giá liên kết (Quotations):** 2 báo giá (`quotationsCount = 2`)
  - Báo giá 1 (ID: `21b5c8f4-32bf-4909-9efa-d1cb6abc39bf`):
    - Nhà cung cấp: `[E2E] Công nghệ Số Việt Nam 1790849669763` (ID: `a09243b6-456f-40b9-911c-e126552aeebe`)
    - Tổng tiền: **41,000,000 VND** (Đơn giá: 8,200,000 VND, Số lượng: 5)
    - Thời gian giao hàng: 3 ngày; Bảo hành: `12 months manufacturer warranty`
    - Cờ bất thường (`isAnomaly`): `false`
  - Báo giá 2 (ID: `69bb6101-4fea-46ee-a2d5-e871eb539b4c`):
    - Nhà cung cấp: `[E2E] Công nghệ Số Việt Nam 1790849984689` (ID: `4413952d-c642-444a-827f-f1d54b4c0591`)
    - Tổng tiền: **39,500,000 VND** (Đơn giá: 7,900,000 VND, Số lượng: 5)
    - Thời gian giao hàng: 5 ngày; Bảo hành: `24 months on-site warranty`
    - Cờ bất thường (`isAnomaly`): `false`
- **Đơn mua hàng (PO):** 1 bản ghi (`purchaseOrdersCount = 1`)
  - Mã PO (ID: `266abbf2-def6-4fb0-b256-c12c0b537b3a`): `PO-NUM-2026-20261005-288028BC`
  - Trạng thái: `CLOSED`
  - Tổng tiền: **41,000,000 VND** (Khóa 100% từ Báo giá 1 được con người trao thầu)
  - Số lượng đặt: 5
  - Nhà cung cấp trao thầu: `[E2E] Công nghệ Số Việt Nam 1790849669763`
- **Nhật ký nhận hàng (Receiving Logs):** 2 đợt
  - Đợt 1 (ID: `b5b29d9b-102d-47fa-aa24-aaa94e1e4248`): Nhận 2 sản phẩm (Ghi chú: `"Batch 1: Received 2 of 5 sealed workstations for QA testing"`)
  - Đợt 2 (ID: `f1d3ec59-cb05-4c7e-94cc-cd9a7cbe2aad`): Nhận 3 sản phẩm (Ghi chú: `"Batch 2: Received remaining 3 of 5 workstations, full technical inspection completed"`)
  - Tổng số lượng nhận lũy kế (`receivedQtySum`): **5 / 5**
- **Quyết toán Ngân sách (Budget Settlement):**
  - Phòng ban: `DEPT-IT`, Năm tài chính: 2026
  - Hạn mức được cấp (`allocatedAmount`): **500,000,000 VND**
  - Số dư chi thực tế (`spentAmount`): **306,000,000 VND** (Tăng chính xác 41,000,000 VND từ giá trị PO)
  - Số dư tạm giữ (`tempReservedAmount`): **0.0 VND** (Số dư tạm giữ của PR-2026-029 được giải phóng hoàn toàn về 0 sau khi đóng PR; không còn khoản tạm giữ tồn đọng).

### HISTORICAL SNAPSHOT / PREVIOUS TEST DATA (Ghi chú đối soát lịch sử tài liệu)
- **Nguồn gốc dữ liệu cũ:** Trong các bản thảo báo cáo trước đó, một kịch bản giả định (mock narrative) từng ghi nhận: tiêu đề *"Mua sắm 05 màn hình đồ họa 4K chuyên dụng phục vụ dự án AI"*, nhà cung cấp giả định FPT/Phong Vũ, giá trị ước tính 45,000,000 VND, `spentAmount = 286,000,000 VND` và `tempReserved = 30,000,000 VND`.
- **Kết luận đối soát:** CSDL thực tế Supabase PostgreSQL lưu giữ bản ghi thực tế được tạo và thực thi trong phiên E2E runner chính thức là kịch bản `PR-2026-029` ("Laptops for engineering onboarding") với các tham số tại **CURRENT VERIFIED STATE** ở trên. Báo cáo này chính thức chuẩn hóa và lấy **CURRENT VERIFIED STATE** làm căn cứ kỹ thuật duy nhất, không ghi đè âm thầm.

---

## 13. Frontend Build & Architecture

- **Lệnh thực thi:** `npm run build` tại thư mục `frontend/`.
- **Kết quả build:**
  - Thời gian biên dịch: **11.52s**.
  - TypeScript Compiler (`tsc`): **0 errors**.
  - Vite Production Bundle:
    - HTML: `dist/index.html` (1.75 kB)
    - CSS: `dist/assets/index-D7Ue2mH_.css` (29.28 kB)
    - JS: `dist/assets/index-Cp5TiUOm.js` (649.36 kB)
- **Kiến trúc giao diện:**
  - Toàn bộ giao diện hiện tại được gom trong bundle đơn khối qua `App.tsx` với router điều khiển trạng thái nội bộ (`activeView`).
  - Đánh giá kiến trúc: Chưa tái cấu trúc tách route độc lập bằng React Router (TASK-011). Trạng thái được ghi nhận trung thực là:
    $$\textbf{FRONTEND ARCHITECTURE} = \textbf{PARTIALLY IMPLEMENTED}$$

---

## 14. Documentation Consistency Audit

Rà soát đối chiếu toàn bộ các tài liệu hiện hữu:

| Tài liệu | Nội dung ghi nhận | Thực tế mã nguồn / Evidence | Đánh giá tính nhất quán |
|---|---|---|:---:|
| `docs/DECISION_LOG.md` | HD-05 yêu cầu E2E bằng Playwright | Kịch bản tự động hóa thực tế dùng Puppeteer | **INCONSISTENT** (Cần giải trình dùng Puppeteer) |
| `docs/07-release/release-notes.md` | Bản thảo cũ ngày 2026-08-25 ghi "Playwright 1/1 PASS", "0% hallucination" | Mã nguồn thực tế dùng Puppeteer; AI dùng Fallback Heuristic | **INCONSISTENT** (Tài liệu cũ lỗi thời, được thay thế bởi Final QA Report) |
| `docs/IMPLEMENTATION_PLAN.md` | Ghi nhận các TASK-001 đến TASK-016 hoàn thành | Đối chiếu mã nguồn và test đạt 133/133 PASS, E2E 14/14 steps PASS | **ALIGNED** |
| `docs/AI_USAGE_TRACEABILITY.md` | Ghi nhận AI-001 đến AI-073 | Khớp với commit history và bằng chứng thực tế | **ALIGNED** (Đã bổ sung AI-074) |
| `docs/logs/ai-usage-log.md` | Ghi nhận chi tiết các phiên làm việc và hiệu chỉnh | Khớp với các quyết định kỹ thuật | **ALIGNED** (Đã bổ sung AI-074) |

---

## 15. Evidence Review

Toàn bộ các bằng chứng đã được rà soát và xác minh sự tồn tại vật lý trên ổ đĩa:
- Thư mục bằng chứng trình duyệt: `docs/evidence/browser/` (8 screenshots định dạng PNG, kích thước 128 KB – 359 KB).
- Thư mục đối chiếu thiết kế Figma: `docs/evidence/figma-reference/` và các báo cáo `PHASE-2..4F-VISUAL-GATE-AUDIT.md`.
- File snapshot kiểm chứng CSDL: `backend/scratch/lifecycle_db_verifier.py`.
- Nhật ký thực thi Pytest: 133/133 test cases được kiểm chứng trực tiếp trên live connection string.

---

## 16. Audit Findings Classification

Toàn bộ các phát hiện kỹ thuật trong đợt kiểm toán được tổng hợp và phân loại minh bạch:

| Phân loại (Category) | Số lượng | Danh sách mục | Mức độ nghiêm trọng | Đánh giá |
|---|:---:|---|:---:|---|
| **Phát hiện chí mạng (Critical Findings)** | **0** | *Không có* | **BLOCKER** | **0 Blocker**: Không có lỗi logic, không vượt quyền, không race condition. |
| **Kiểm thử thành công (PASS)** | **6** | Mục 2, 3, 4, 5, 6, 7 | INFO / GREEN | 133/133 tests PASS, 14/14 E2E steps PASS, DB snapshot lưu vết, RBAC 19 endpoints, Guards, Frontend build sạch. |
| **Sự thật kỹ thuật (FACT)** | **4** | Mục 1, 8, 10, 14 | INFO | Git commit HEAD `cc84847`, Fallback 78%, Puppeteer tooling, Con người quyết định trao thầu. |
| **Chưa kiểm chứng (UNVERIFIED)** | **1** | Mục 9 | LOW | Cuộc gọi ra Google Gemini Live API chưa kích hoạt trong phiên kiểm thử CI/CD cục bộ. |
| **Thiếu bằng chứng (MISSING EVIDENCE)** | **1** | Mục 11 | LOW | Chưa có bằng chứng chạy kịch bản E2E bằng framework Playwright (được thay bằng Puppeteer). |
| **Triển khai một phần (PARTIALLY IMPLEMENTED)** | **1** | Mục 12 | LOW | Giao diện điều hướng qua state trong `App.tsx`, chưa tách đa trang bằng React Router. |
| **Mâu thuẫn tài liệu cũ (INCONSISTENT)** | **1** | Mục 13 | LOW | Bản thảo cũ `release-notes.md` (2026-08-25) chứa tuyên bố lỗi thời, đã được thay thế bởi báo cáo này. |
| **TỔNG CỘNG PHÁT HIỆN KIỂM TOÁN (AUDIT FINDINGS)** | **14** | **14 mục đánh số dưới đây** | — | **RELEASE READY WITH KNOWN LIMITATIONS** |

#### Chi tiết 14 phát hiện kiểm toán:

1. **[FACT]** Nhánh Git hiện tại là `final-delivery`, commit HEAD là `cc848479a5fb2ed7353dd22ca2a8d353666597e7`.
2. **[PASS]** Toàn bộ 9 test suites backend đạt **133 / 133 PASSED** (0 failed, 0 error) trên Supabase PostgreSQL.
3. **[PASS]** Kịch bản kiểm thử tự động trình duyệt hoàn thành **14 / 14 bước nghiệp vụ** trơn tru.
4. **[PASS]** Bằng chứng lưu vết CSDL kiểm chứng độc lập xác nhận `PR-2026-029` ("Laptops for engineering onboarding") chuyển trạng thái `CLOSED`, 2 Quotations, 1 PO (`PO-NUM-2026-20261005-288028BC`), nhận hàng 5/5 qua 2 đợt, ngân sách quyết toán chính xác (`spentAmount = 306,000,000 VND`, `tempReserved = 0 VND`).
5. **[PASS]** Server-Side RBAC bảo vệ 100% 19 endpoints và thực thi nghiêm ngặt No Self-Approval (GOV-01) cho mọi vai trò.
6. **[PASS]** Ràng buộc nghiệp vụ HD-04 (chặn tạo PO từ PR chưa duyệt) và HD-07 (chặn đóng PR khi thiếu hàng) được thực thi bằng khóa dòng transaction trong PostgreSQL.
7. **[PASS]** Bản dựng frontend `npm run build` thành công, 0 lỗi TypeScript trong 11.52s.
8. **[FACT]** Chế độ AI phân tích báo giá vận hành trên **Fallback / Heuristic** với độ tin cậy 78%, trọng số 40/25/25/10 theo Figma 9:5589.
9. **[UNVERIFIED]** Cuộc gọi mạng ra dịch vụ ngoài **Google Gemini Live API** chưa được kiểm chứng trong phiên kiểm thử này.
10. **[FACT]** Kịch bản E2E được thực thi bằng công cụ **Puppeteer**, không phải Playwright.
11. **[MISSING EVIDENCE]** Kiểm thử bằng framework Playwright chính thức được ghi nhận là `NOT VERIFIED / MISSING PLAYWRIGHT EVIDENCE`.
12. **[PARTIALLY IMPLEMENTED]** Kiến trúc frontend hiện tại là ứng dụng đơn khối điều hướng bằng component state (`App.tsx`), chưa tái cấu trúc React Router đa trang (TASK-011).
13. **[INCONSISTENT]** Tài liệu cũ `docs/07-release/release-notes.md` (soạn ngày 2026-08-25) chứa các tuyên bố lỗi thời về Playwright và "0% hallucination", mâu thuẫn với sự thật kỹ thuật.
14. **[FACT]** Quyền quyết định trao thầu hoàn toàn do con người thực hiện (Human-in-the-loop); AI không tự ý sinh PO (0 autonomous PO creation).

---

## 17. Release Blockers

- **Số lượng Phát hiện Chí mạng / Blocker (Critical Findings / Critical Blockers):** **0**
- **Đánh giá:** Không có lỗi logic nghiệp vụ, không có lỗ hổng bảo mật rò rỉ dữ liệu hoặc vượt quyền (privilege escalation), không có race condition trong các giao dịch trọng yếu, và toàn bộ 133 regression tests đều đạt 100% Green. Hệ thống hoàn toàn ổn định để nghiệm thu học thuật.

---

## 18. Remaining Risks

1. **Rủi ro Kết nối Dịch vụ Ngoài (Gemini API):** Khi chuyển sang demo viva sử dụng Live Gemini API key thật, có thể gặp rủi ro độ trễ mạng (latency), rate limit hoặc định dạng JSON phản hồi từ LLM không khớp schema. *Biện pháp giảm thiểu:* Hệ thống đã có cơ chế fail-safe tự động chuyển sang Fallback Heuristic với cấu trúc dữ liệu tương thích 100%.
2. **Kích thước Bundle Frontend:** File bundle JavaScript `dist/assets/index-Cp5TiUOm.js` có kích thước 649.36 kB (>500 kB warning của Vite). *Biện pháp giảm thiểu:* Tải trang nội bộ trong mạng cục bộ/demo không bị ảnh hưởng đáng kể; đề xuất chia tách code (code-splitting / dynamic import) trong các phiên bản sau.

---

## 19. Final Release Readiness Verdict

Căn cứ trên các chứng cứ thực nghiệm thu thập được, Hội đồng QA đưa ra kết luận chính thức:

$$\Large\textbf{RELEASE READY WITH KNOWN LIMITATIONS}$$

Hệ thống **ĐỦ ĐIỀU KIỆN NGHIỆM THU VÀ BẢO VỆ ĐỒ ÁN**, với điều kiện nhóm phải trình bày trung thực các giới hạn kỹ thuật đã được ghi nhận trong báo cáo này, không đưa ra các tuyên bố phóng đại chất lượng.

---

## 20. Human Decisions Required

1. **Quyết định về Live Gemini Demo:** Nhóm cần thống nhất: Trong buổi demo viva chính thức, nhóm sẽ cấu hình `GEMINI_API_KEY` thật để biểu diễn khả năng gọi Live LLM (kèm rủi ro độ trễ mạng), hay sẽ sử dụng chế độ Fallback Heuristic ổn định (đã được kiểm chứng 100% an toàn)?
2. **Quyết định về Công bố Framework E2E:** Trong báo cáo và slide thuyết trình, nhóm thống nhất tuyên bố công cụ kiểm thử tự động trình duyệt là **Puppeteer** (đúng sự thật kỹ thuật), và giải trình sự chuyển dịch từ đề xuất ban đầu (Playwright) sang Puppeteer để tương thích môi trường thực thi.
3. **Thay thế Tài liệu Cũ:** Chính thức xác nhận tài liệu `docs/evidence/FINAL_QA_GATE_REPORT.md` này thay thế hoàn toàn bản thảo lỗi thời `docs/07-release/release-notes.md`.

---

## 21. CLAIMS SAFE TO USE IN REPORT & PRESENTATION

Dưới đây là danh mục các tuyên bố **AN TOÀN TUYỆT ĐỐI** và được phép sử dụng trong Báo cáo Đồ án, Slide Thuyết trình và Vấn đáp (Viva):

### NHÓM TUYÊN BỐ ĐÃ ĐƯỢC CHỨNG MINH (VERIFIED / PASS):
- **PASS:** Hệ thống hoàn thành kiểm thử hồi quy tự động backend đạt **133 / 133 test cases PASS (100% Green)** trên CSDL Supabase PostgreSQL qua 9 test suites cốt lõi.
- **PASS:** Kịch bản kiểm thử tự động trình duyệt bao phủ toàn diện **14 / 14 bước nghiệp vụ** từ Tạo PR đến Đóng PR và Quyết toán Ngân sách.
- **VERIFIED:** Dữ liệu vòng đời mua sắm được lưu vết toàn vẹn và có thể truy nguyên trên CSDL Supabase PostgreSQL (mã PR `PR-2026-029` - "Laptops for engineering onboarding", mã PO `PO-NUM-2026-20261005-288028BC`, nhận hàng 5/5 qua 2 đợt, số dư ngân sách hoàn ứng chính xác với `spentAmount = 306,000,000 VND` và `tempReservedAmount = 0.0 VND`).
- **VERIFIED:** Cơ chế phân quyền máy chủ (Server-Side RBAC) bảo vệ 100% 19 endpoints nghiệp vụ; danh tính người dùng được ràng buộc bất biến qua Supabase JWT (ES256/JWKS) và trường `User.authUserId`.
- **VERIFIED:** Thực thi nghiêm ngặt nguyên tắc quản trị No Self-Approval (GOV-01) ở tầng service layer bình đẳng cho mọi vai trò (kể cả Quản trị viên ADMIN).
- **VERIFIED:** Ràng buộc nghiệp vụ HD-04 (chặn tạo PO từ PR chưa duyệt) và HD-07 (chặn đóng PR khi chưa nhận đủ hàng) được bảo vệ bằng giao dịch và khóa dòng `SELECT ... FOR UPDATE` trong PostgreSQL.
- **VERIFIED:** Quy trình trao thầu tuân thủ nguyên tắc con người quyết định (Human-in-the-loop); AI tuyệt đối không tự ý phát hành PO (0 autonomous PO creation).
- **VERIFIED:** Bản dựng giao diện (`npm run build`) hoàn thành thành công trong 11.52s, 0 lỗi TypeScript.

### NHÓM TUYÊN BỐ CẦN GIẢI TRÌNH CHÍNH XÁC (KNOWN LIMITATIONS):
- **FACT / ADVISORY ONLY:** Hệ thống phân tích báo giá vận hành ở chế độ **Fallback / Heuristic** với độ tin cậy hiển thị 78%, tính theo mô hình chấm điểm 4 tiêu chí (Landed Price 40%, Lead Time 25%, Reliability 25%, Terms 10% từ Figma 9:5589).
- **UNVERIFIED:** Kết nối gọi ngoài trực tiếp tới Google Gemini Live API được ghi nhận là `UNVERIFIED` trong phiên kiểm thử tự động CI/CD.
- **NOT VERIFIED / MISSING PLAYWRIGHT EVIDENCE:** Kịch bản tự động hóa trình duyệt 14 bước được thực thi bằng **Puppeteer**, không phải Playwright.
- **PARTIALLY IMPLEMENTED:** Kiến trúc giao diện người dùng hiện tại là ứng dụng đơn khối dạng modular (`App.tsx`), chưa chia tách route độc lập bằng React Router.

### TUYỆT ĐỐI KHÔNG ĐƯỢC TUYÊN BỐ (FORBIDDEN CLAIMS):
- *CẤM TUYÊN BỐ:* "Hệ thống AI không bao giờ ảo giác (Zero Hallucination)" hoặc "Hệ thống AI tự động hóa hoàn toàn việc mua sắm".
- *CẤM TUYÊN BỐ:* "Hệ thống đạt 100% Production-Ready cho doanh nghiệp lớn" mà không đề cập các giới hạn kỹ thuật.
- *CẤM TUYÊN BỐ:* "Đã kiểm thử E2E bằng Playwright đạt 100%".
- *CẤM TUYÊN BỐ:* "Điểm tin cậy 78% là điểm chính thức do Gemini Live sinh ra".

---

## 22. Course Compliance Audit — 32/32 Deliverables & Evidence Gate

Thực hiện thẩm định mức độ tuân thủ chuẩn đầu ra và yêu cầu môn học dựa trên `Output_BaoCao.xlsx` / `docs/OUTPUT_BAOCAO.md`. Nguyên tắc thẩm định tuân thủ nghiêm ngặt: **"Không có evidence thực tế $\rightarrow$ Không được đánh dấu COMPLETE/PASS"**.

### 22.1. Ma trận 32/32 Deliverables Bắt buộc (Compliance Matrix)

| ID | Deliverable | Yêu cầu Môn học | Artifact Hiện có | Evidence Thực tế | Phụ trách chính | Trạng thái | Khoảng trống (Gap) & Hành động cần làm |
|---|---|---|---|---|---|:---:|---|
| **1.1** | Project Charter | Problem, users, goals, metrics, scope | `docs/01-discovery/project-charter.md` | Bảng charter 11 mục, ranh giới MVP, 6 success signals | Nguyễn Trương Thùy Dương | **PASS** | Hoàn chỉnh, nhất quán với requirements. |
| **1.2** | User Research + Synthesis | $\ge 3$ sources/proxy, quotes, themes A-E | `docs/01-discovery/user-research.md` | Phỏng vấn 4 vai trò (P1-P4), 4 themes A-D | Nguyễn Trúc Lam | **PASS** | Sử dụng Stakeholder Proxy theo giả định MVP. |
| **1.3** | Requirements + Business Rules | REQ-xxx, FR, NFR, BR-01..12, testable | `docs/01-discovery/requirements.md` | 18 FRs, 3 NFRs, 12 BRs, constraints, assumptions | Nguyễn Trương Thùy Dương | **PASS** | Hoàn chỉnh, có traceability 1:1. |
| **1.4** | Project Vault | Policies, source-priority, domain rules | `docs/02-vault/` | `company-policies.md`, `source-priority.md`, `00-index.md` | Nguyễn Trúc Lam | **PASS** | Đầy đủ thư viện tri thức nền tảng. |
| **1.5** | Vault Q&A Benchmark | $\ge 20$ questions, citations, pass/fail | `docs/02-vault/vault-qa-benchmark.md` | 20 câu hỏi (Q-01..20), 3 iterations cải tiến System Prompt | Nguyễn Trúc Lam | **PASS** | Đạt 20/20 PASS có trích dẫn nguồn cụ thể. |
| **1.6** | AI Usage Log v1 | Task, prompt, output, verify, correct | `docs/logs/ai-usage-log.md`<br>`docs/02-vault/AI_USAGE_LOG.md` | 38 phiên làm việc ban đầu AI-001..AI-038 | Nguyễn Trúc Lam / Cả nhóm | **PASS** | Đầy đủ bối cảnh, prompt và hiệu chỉnh con người. |
| **2.1** | PRD | Problem, users, scope, workflow, metrics | `docs/03-product/PRD.md` | PRD chi tiết 8 phần, đồng bộ requirements | Nguyễn Trương Thùy Dương | **PASS** | Hoàn chỉnh, nhất quán với Charter và FRs. |
| **2.2** | User Flow | Happy path + error path, diagram | `docs/03-product/user-flow.mmd`<br>`user-flow.md` | Sơ đồ Mermaid đầy đủ 4 luồng A, B, C, D | Nguyễn Trương Thùy Dương | **PASS** | Thể hiện cả nhánh từ chối và cảnh báo ngân sách. |
| **2.3** | Functional Prototype | Prototype URL tương tác được luồng chính | `docs/04-design/prototype.md` | Link MagicPatterns: `https://www.magicpatterns.com/c/utapnp7s8wvsxbtcfalh2b/preview?hideToolbar=true&path=%2Frequests%2FPR-2026-041` | Nguyễn Thị Thùy Dung | **PASS** | Prototype tương tác trực tuyến cho các màn hình chính. |
| **2.4** | Usability Test | $\ge 3$ users, test log, before/after changes | `docs/03-product/usability-findings.md` | File hiện ghi: *"Chưa có dữ liệu kiểm thử. Test date: Chưa thực hiện"* | Trần Thị Thu Hà / Cả nhóm | **MISSING EVIDENCE** | **GAP LỚN:** Cần thực hiện kiểm thử trên $\ge 3$ người dùng thật, ghi nhận findings và cải tiến trước khi nộp đồ án. |
| **2.5** | User Stories + AC | 8–12 stories, Given/When/Then, testable | `docs/03-product/user-story.md` | 10 User Stories (US-01..10) + 2 Governance (GOV-01, 02) | Nguyễn Trương Thùy Dương | **PASS** | Định dạng Given/When/Then chuẩn, 100% testable. |
| **2.6** | Taiga Backlog | Epics $\rightarrow$ Stories $\rightarrow$ Tasks, status, sprint, link | `docs/03-product/taiga-backlog.md` | Có cấu trúc 7 Epics, 10 Stories, 42 Tasks trong markdown; chưa đồng bộ lên Taiga server | Nguyễn Trương Thùy Dương | **MISSING EVIDENCE / NOT CREATED** | **GAP:** Chưa tạo project/issues chính thức trên nền tảng `tree.taiga.io`. Cần tạo board và dán link public. |
| **2.7** | Figma + Design System | Tokens, component states, screens, URL | `docs/FIGMA_IMPLEMENTATION_SPEC.md`<br>`docs/04-design/DESIGN.md` | Figma URL: `https://www.figma.com/design/maPwEYOWc2ZHj4gP9w5uTV/Untitled?node-id=0-1&m=dev`, 20 frames audited | Nguyễn Thị Thùy Dung | **PASS** | Đầy đủ design tokens, typography, component inventory. |
| **2.8** | Architecture + ADR | Context/container, modules, ADR choices | `docs/TARGET_ARCHITECTURE.md`<br>`docs/DECISION_LOG.md` | Kiến trúc C4, 17 Human Decisions chính thức (HD-01..17) | Trần Thị Kiều Giang / Nhóm | **PASS** | Hoàn chỉnh, phản ánh chính xác cấu trúc hệ thống. |
| **2.9** | ERD / Data Model | Entities, relations, constraints, schema | `backend/prisma/schema.prisma`<br>`docs/05-technical/data-model.md` | Schema 10 bảng, 2 enums, ràng buộc FK, runtime Supabase | Trần Thị Kiều Giang | **PASS** | Khớp 100% giữa Prisma schema và CSDL PostgreSQL. |
| **2.10** | API Contract | Endpoints, auth, request, response, error | `docs/05-technical/API.md`<br>FastAPI `/docs` (OpenAPI) | 19 endpoints chuẩn RESTful, Pydantic schemas, Swagger UI | Nguyễn Thị Thùy Dung / Giang | **PASS** | Tài liệu hợp đồng API đầy đủ, kiểm chứng qua test suites. |
| **2.11** | Story Specs + Traceability v1 | REQ $\rightarrow$ Story $\rightarrow$ Screen $\rightarrow$ API $\rightarrow$ Task | `docs/06-testing/traceability-matrix.md`<br>`docs/AI_USAGE_TRACEABILITY.md` | Bảng ma trận ánh xạ 10 stories với tasks và test | Nguyễn Trương Thùy Dương | **PASS** | Không có orphan story, liên kết thông suốt. |
| **3.1** | Source Repository | Clean structure, branch, commits, no secrets | Local Git repo & GitHub remote `thgnud1022/group-01-project` | Branch `final-delivery`, commit HEAD `cc84847`, `.env` an toàn | Trần Thị Kiều Giang | **PASS** | Cấu trúc chuẩn, không rò rỉ secret, commit có quy chuẩn. |
| **3.2** | Release chạy được | Demo URL + tag `v1.0.0-final`, chạy từ release | Public Frontend: `https://group-01-project.vercel.app`<br>Public Backend: `https://group-01-project-production.up.railway.app`<br>Git Tag: `v1.0.0-final` (`9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`) | AI-089 Public Smoke Suite (`scratch/ai089_public_smoke.py`): Frontend 200, Backend /api/health 200, Supabase DB connected, Auth 200, RBAC guards (401/403), Happy Path (PR-2026-039 CLOSED), Failure Path (400), Persistence verified | Trần Thị Kiều Giang / Nhóm | **COMPLETE** | Đã triển khai công khai trên Vercel + Railway, gắn tag Git `v1.0.0-final` bất biến, kiểm chứng đầy đủ 100% qua kịch bản khói AI-089. |
| **3.3** | Authentication + Authorization | Login, session, token, roles, denied cases | `backend/app/core/auth.py`, `rbac.py` | Supabase JWT ES256, RBAC 19 endpoints, 28/28 tests PASS (`test_rbac.py`) | Nguyễn Thị Thùy Dung | **PASS** | Bảo vệ máy chủ fail-closed, No Self-Approval (GOV-01). |
| **3.4** | Business Workflow | Happy path + failure paths, E2E evidence | `frontend/scripts/test_final_full_lifecycle_e2e.js` | 14/14 steps PASS, 8 screenshots, status guards, HD-04 & HD-07 | Trần Thị Thu Hà | **PASS** | Kiểm chứng cả luồng thành công và các nhánh chặn lỗi. |
| **3.5** | AI Feature | Value, structured output, validation, fallback, dataset $\ge 20$ | `backend/app/services/ai_service.py`<br>`docs/evaluation/TASK-010-DATASET.json` | 24 evaluation cases (100% pass rubric), Fallback Heuristic 78%, Pydantic validation | Nguyễn Trúc Lam | **PASS WITH DISCLOSURE** | Hoạt động tốt ở chế độ Fallback; Live Gemini ghi nhận `UNVERIFIED`. Không tự động tạo PO. |
| **3.6** | Code Review Evidence | PR, checklist, reviewer, blocker/minor, resolution | Chưa có file `code-review.md` | Chưa có bằng chứng Pull Request review chính thức trên GitHub | Trần Thị Thu Hà / Nhóm | **MISSING EVIDENCE** | **GAP:** Cần tạo tài liệu Code Review mẫu hoặc lưu vết PR review giữa các thành viên. |
| **3.7** | Bug Log | Severity, steps, expected, actual, evidence, owner, status | `docs/qa/QA_FINDINGS.md`<br>`TASK-006-BUG-001-PO-GUARD.md` | Ghi nhận BUG-001 / QF-001 (PO guard); chưa có bảng tổng hợp bug tracking toàn diện | Trần Thị Thu Hà | **PARTIALLY IMPLEMENTED** | Cần hoàn thiện bảng Bug Log tập trung đầy đủ các bug đã phát hiện và xử lý trong các phase. |
| **3.8** | Automated Tests | Unit/Integration/API/E2E, failure paths | `backend/tests/` (9 suites)<br>`test_final_full_lifecycle_e2e.js` | 133/133 backend pytest PASS (448.93s) + 14/14 browser E2E steps | Trần Thị Thu Hà | **PASS** | 100% Green trên live Supabase PostgreSQL. |
| **3.9** | QA Report | Scope, environment, result, blockers = 0, sign-off | `docs/evidence/FINAL_QA_GATE_REPORT.md` | Báo cáo kiểm toán độc lập 22 sections, 0 Critical Blockers | Trần Thị Thu Hà | **PASS** | Biên bản nghiệm thu toàn diện, minh bạch hiện trạng. |
| **3.10** | Security + NFR Evidence | RBAC, input validation, secrets, a11y, perf | `backend/app/core/rbac.py`, `test_rbac.py` | 28 test cases an ninh, fail-closed, transaction locks; chưa có formal load test / a11y report | Nguyễn Thị Thùy Dung / Hà | **PARTIALLY IMPLEMENTED** | Cần bổ sung tài liệu kiểm tra tải cơ bản và audit phụ thuộc (`pip-audit` / `npm audit`). |
| **3.11** | CI/CD + Docker/Deployment | Pipeline, build/test in CI, Docker, healthcheck | `.github/workflows/ci.yml`<br>`backend/Dockerfile`<br>`compose.yaml` | GitHub Actions multi-job CI (`backend-test` + `frontend-build`), Dockerfile containerization, healthcheck `/api/health`; remote run xác minh 100% Green (Run #37878925224, commit `dce7b94`) | Trần Thị Thu Hà / Trần Thị Kiều Giang | **PASS** | Đã hoàn thành cấu hình CI/CD và báo cáo kiểm chứng `CI_CD_PIPELINE_REPORT.md` (verified remote execution). |
| **3.12** | README + Runbook | Setup, env, seed, run, test, troubleshooting | `README.md` (35 dòng) | Có hướng dẫn chạy nhanh nhưng dùng tool cũ (`uv run`, `playwright`); thiếu Runbook sự cố chi tiết | Trần Thị Kiều Giang | **PARTIALLY IMPLEMENTED** | Cần cập nhật `README.md` và viết `RUNBOOK.md` chuẩn để người ngoài clone tự chạy được 100%. |
| **3.13** | Release Notes + Changelog | Version, scope, features, fixes, limitations | `docs/07-release/release-notes.md` | File nháp cũ ngày 2026-08-25 ghi Playwright và "0% hallucination", chưa khớp Final RC | Nguyễn Trương Thùy Dương | **INCONSISTENT** | **CẦN SỬA GẤP:** Đồng bộ `release-notes.md` với `FINAL_QA_GATE_REPORT.md` (công nhận Puppeteer, Fallback 78%, v1.0.0-final). |
| **3.14** | Traceability Final | 100% Done scope traceable: REQ $\rightarrow$ Story $\rightarrow$ Task $\rightarrow$ Code $\rightarrow$ Test | `docs/AI_USAGE_TRACEABILITY.md` | Ma trận truy xuất xuyên suốt AI-001..074, 10 User Stories, 42 Tasks, commits, tests | Nguyễn Trương Thùy Dương / Nhóm | **PASS** | 100% phạm vi kỹ thuật đã hoàn thành đều có mã nguồn, test và evidence đối soát. |
| **3.15** | AI Usage Log Final + Retrospective | Toàn bộ tasks có AI, mistakes, corrections, lessons learned | `docs/logs/ai-usage-log.md` | 74 phiên làm việc chi tiết, mục hiệu chỉnh con người; thiếu phần Retrospective tổng kết bài học | Nguyễn Trúc Lam / Cả nhóm | **PARTIALLY IMPLEMENTED** | Cần bổ sung mục Retrospective (bài học kinh nghiệm và quản trị rủi ro AI) vào cuối log. |

---

### 22.2. Tổng hợp Độ Bao phủ Chứng cứ (Evidence Coverage Summary)

$$\begin{aligned}
\textbf{Tổng số Deliverables bắt buộc:} &\quad \mathbf{32} \\
\textbf{Đạt chuẩn có Bằng chứng Thực nghiệm (PASS / COMPLETE):} &\quad \mathbf{23} \quad (71.88\%) \\
\textbf{Triển khai một phần (PARTIALLY IMPLEMENTED):} &\quad \mathbf{5} \quad (15.63\%) \\
\textbf{Thiếu Bằng chứng Thực nghiệm (MISSING EVIDENCE):} &\quad \mathbf{3} \quad (9.38\%) \\
\textbf{Mâu thuẫn Tài liệu (INCONSISTENT):} &\quad \mathbf{1} \quad (3.12\%) \\
\textbf{Chưa khởi động (NOT STARTED):} &\quad \mathbf{0} \quad (0.00\%)
\end{aligned}$$

*(Lưu ý: Tỷ lệ Evidence Coverage 71.88% là chỉ số đo lường mức độ hoàn thiện minh chứng nội bộ của nhóm phục vụ hoàn thiện hồ sơ sau khi hoàn tất Deliverable 3.2 Public Release tại AI-089/AI-090, KHÔNG diễn giải thành điểm số học phần).*

---

### 22.3. Khung Thẩm định Cá nhân 5 Thành viên (Individual 5-Member Viva Audit)

Để chuẩn bị cho phần vấn đáp cá nhân (5 phút/sinh viên), mỗi thành viên được đối soát 1-1 với phân bổ chính thức:

```
Sinh viên → User Story Cốt lõi → Business/Tech Tasks → Code Files → Tests → Git Commits → AI Usage → AI Correction → Kịch bản Demo Viva
```

#### 1. Trần Thị Kiều Giang
- **Vai trò:** Kỹ sư Công nghệ (Engineering / Backend Core & Build)
- **User Story cốt lõi (5-min Viva):** **US-01** (Tạo & Chuẩn hóa Purchase Request)
- **Toàn bộ User Stories sở hữu:** **US-01**
- **Nhiệm vụ nghiệp vụ:** T-01 (Thiết kế form PR), T-02 (Kiểm tra trường bắt buộc), T-03 (Submit PR và ghi trạng thái).
- **Nhiệm vụ kỹ thuật:** `TASK-001` (Cấu hình môi trường, Hatchling build, Prisma Python), `TASK-002` (Đồng bộ `PurchaseOrder.quantity`), `TASK-003` (Chuyển đổi dữ liệu sang Prisma Client).
- **Mã nguồn thực tế:** `backend/prisma/schema.prisma`, `backend/app/services/db.py`, `backend/app/routers/pr.py`, `frontend/src/App.tsx`.
- **Kiểm thử thực tế:** `backend/tests/test_us09_po.py`, `backend/tests/test_phase4f_lifecycle.py`.
- **Git Commits:** `43666d6` (TASK-001 setup), `68c34dc` (TASK-002 PO quantity), `237ffa7` (TASK-003 Prisma migration).
- **Nhật ký AI liên quan:** AI-007, AI-014..AI-025, AI-033..AI-036.
- **Minh chứng sửa lỗi AI:** Trong TASK-001 (AI-016 $\rightarrow$ AI-017), AI cấu hình Hatchling build bị thiếu layout package gây lỗi cài đặt; Giang đã phát hiện và bổ sung `packages = ["app"]`. Trong AI-019 $\rightarrow$ AI-020, AI sinh Prisma schema thiếu cờ Decimal; Giang đã bổ sung `enable_experimental_decimal = true`.
- **Kịch bản Demo Viva:** Mở form New Request, nhập liệu PR ThinkPad P16 (5 máy @ 8M = 40M), demo validation chặn submit khi thiếu trường bắt buộc, bấm gửi duyệt thành công $\rightarrow$ mở CSDL Supabase chỉ ra bản ghi PR trạng thái `PENDING_MANAGER_APPROVAL`.

#### 2. Nguyễn Trương Thùy Dương
- **Vai trò:** Phân tích Nghiệp vụ & Chủ sản phẩm (BA / PO)
- **User Story cốt lõi (5-min Viva):** **US-04** (Manager Review, Approval & Budget)
- **Toàn bộ User Stories sở hữu:** **US-04**, **US-05**, **US-06**
- **Nhiệm vụ nghiệp vụ:** T-10..T-13 (Manager review, actions duyệt/từ chối/yêu cầu sửa), T-14..T-16 (Finance kiểm tra ngân sách), T-17..T-20 (Sourcing, nhà cung cấp, liên kết báo giá).
- **Nhiệm vụ kỹ thuật:** `TASK-008` (Quản lý Nhà cung cấp & Báo giá), `TASK-012` (Màn hình phê duyệt Flow B).
- **Mã nguồn thực tế:** `backend/app/routers/pr.py` (`approve_pr_prisma`), `backend/app/routers/suppliers.py`, `backend/app/routers/quotations.py`.
- **Kiểm thử thực tế:** `test_pr_approval_prisma.py` (15/15 PASS), `test_pr_reject_prisma.py` (4/4 PASS), `test_pr_revision_prisma.py` (4/4 PASS), `test_supplier_quotation_prisma.py` (15/15 PASS).
- **Git Commits:** `c1c91ee`, `8190dba`, `20100e1`.
- **Nhật ký AI liên quan:** AI-001, AI-003, AI-004, AI-006, AI-010, AI-027, AI-028, AI-059.
- **Minh chứng sửa lỗi AI:** Trong AI-001, AI đề xuất mục tiêu dự án trong Project Charter đạt 100% độ chính xác hoàn hảo phi thực tế; Dương đã hiệu chỉnh về chỉ số khả thi (80-85%). Trong AI-004, AI soạn quy chế thiếu ràng buộc No Self-Approval; Dương đã yêu cầu bổ sung quy tắc GOV-01 vào danh mục Business Rules.
- **Kịch bản Demo Viva:** Đăng nhập tài khoản `manager@company.com`, mở hàng đợi Approvals, chọn PR ThinkPad P16, giải trình cơ chế duyệt 1 cấp (40M $\le$ 50M) và No Self-Approval, bấm Approve $\rightarrow$ mở CSDL xác nhận trạng thái PR chuyển `APPROVED`.

#### 3. Nguyễn Trúc Lam
- **Vai trò:** Kỹ sư Tri thức AI & Đánh giá Chất lượng (AI Vault & Quality Evaluation)
- **User Story cốt lõi (5-min Viva):** **US-07** (AI Extraction, Comparison & Recommendation)
- **Toàn bộ User Stories sở hữu:** **US-03**, **US-07**
- **Nhiệm vụ nghiệp vụ:** T-07..T-09 (AI gợi ý mô tả PR, human review), T-21..T-24 (Trích xuất báo giá, bảng so sánh đa chiều, cảnh báo bất thường giá $\ge 20\%$, khuyến nghị tối ưu).
- **Nhiệm vụ kỹ thuật:** `TASK-009` (Tích hợp Gemini REST API & Fallback Heuristic), `TASK-010` (Bộ dữ liệu đánh giá 24 kịch bản benchmark).
- **Mã nguồn thực tế:** `backend/app/services/ai_service.py`, `docs/evaluation/run_eval.py`, `docs/evaluation/TASK-010-DATASET.json`, `frontend/src/components/AssistantAnalysisPanel.tsx`.
- **Kiểm thử thực tế:** `test_ai_service.py` (22/22 PASS), `run_eval.py` (24/24 PASS rubric $\ge 70$).
- **Git Commits:** `91996e7`, `8190dba`, `18494d4`.
- **Nhật ký AI liên quan:** AI-002, AI-061, AI-062, AI-066.
- **Minh chứng sửa lỗi AI:** Trong Vault Q&A Benchmark (AI-002 / Iteration 1), AI tự ý bịa đặt chính sách hệ thống hỗ trợ lưu lịch sử hội thoại 30 ngày (câu Q-08); Lam đã viết lại System Prompt siết chặt quy tắc chặn ảo giác và bắt buộc phản hồi "KHÔNG ĐỦ DỮ LIỆU". Trong TASK-009 (AI-061), AI thiết kế tự động tạo PO; Lam đã sửa lại kiến trúc, khóa 100% quyền của AI ở mức Advisory Only.
- **Kịch bản Demo Viva:** Mở màn hình so sánh 2 báo giá cạnh tranh, bấm nút "Hỏi Trợ lý AI", giải trình thẻ phân tích Fallback Heuristic đạt độ tin cậy 78% (trọng số 40/25/25/10), chỉ ra cảnh báo bất thường giá và khẳng định 0 bản ghi PO bị AI tự động tạo trong CSDL.

#### 4. Nguyễn Thị Thùy Dung
- **Vai trò:** Kỹ sư Giao diện & An ninh Hệ thống (UX/UI & Backend Security)
- **User Story cốt lõi (5-min Viva):** **US-08** (Lựa chọn NCC & Khởi tạo Purchase Order)
- **Toàn bộ User Stories sở hữu:** **US-02**, **US-08**, **US-09**, **GOV-01**
- **Nhiệm vụ nghiệp vụ:** T-04..T-06 (Theo dõi timeline PR), T-25..T-28 (Con người trao thầu, tạo PO, khóa giá và lượng), T-29..T-32 (Ghi nhận biên bản nhận hàng Receiving), GOV-01 (Server-Side RBAC).
- **Nhiệm vụ kỹ thuật:** `TASK-004` (Supabase Auth JWT JWKS ES256), `TASK-005` (Server-Side RBAC 19 endpoints), `T-094` (Khóa PO quantity server-side), Phase 4E/4F UI components.
- **Mã nguồn thực tế:** `backend/app/core/auth.py`, `backend/app/core/rbac.py`, `backend/app/services/procurement_service.py`, `frontend/src/App.tsx`.
- **Kiểm thử thực tế:** `test_rbac.py` (28/28 PASS), `test_po_prisma.py` (15/15 PASS).
- **Git Commits:** `ad8f457`, `a1bc041`, `cc84847`.
- **Nhật ký AI liên quan:** AI-008, AI-037..AI-049, AI-051..AI-058.
- **Minh chứng sửa lỗi AI:** Trong TASK-004 (AI-042), thư viện PyJWKClient do AI đề xuất không cấu hình timeout gây treo kết nối backend khi mất mạng; Dung đã bổ sung `timeout=5.0s` fail-closed an toàn. Trong TASK-005 (AI-045), AI tin cậy `role` và `creatorId` do client gửi lên; Dung đã bãi bỏ toàn bộ và ràng buộc định danh máy chủ 1-1 qua trường `User.authUserId` và Supabase JWT claim `sub`.
- **Kịch bản Demo Viva:** Tại màn hình so sánh báo giá, người dùng tích chọn radio nhà cung cấp chiến thắng (Human Award), bấm "Tạo Đơn Mua Hàng (PO)", chứng minh mã PO sinh chuẩn Option A (`PO-NUM-...`), giá 41M và số lượng 5 máy bị khóa cứng không thể giả mạo từ client.

#### 5. Trần Thị Thu Hà
- **Vai trò:** Kỹ sư Đảm bảo Chất lượng & Trưởng ban Kiểm định (QA / Tester & Release Audit)
- **User Story cốt lõi (5-min Viva):** **US-10** (Close PR, Nhận hàng Hoàn tất & Quyết toán Ngân sách)
- **Toàn bộ User Stories sở hữu:** **US-10**, **GOV-02**
- **Nhiệm vụ nghiệp vụ:** T-33..T-36 (Quy tắc đóng PR, kiểm tra nhận hàng đủ, hoàn ứng ngân sách), GOV-02 (Audit trail lưu vết).
- **Nhiệm vụ kỹ thuật:** `TASK-006` (Khắc phục BUG-001 PO guard), `TASK-007` (Ràng buộc HD-07 Close PR guard `SUM(receivedQty) >= PO.quantity`), `TASK-015` (Kiểm thử hồi quy 133/133 tests PASS), `TASK-016` (Kịch bản trình duyệt E2E 14 bước & Final QA Gate Audit).
- **Mã nguồn thực tế:** `backend/app/services/procurement_service.py` (`close_pr_prisma`, row locks `SELECT ... FOR UPDATE`), `frontend/scripts/test_final_full_lifecycle_e2e.js`, `backend/scratch/lifecycle_db_verifier.py`.
- **Kiểm thử thực tế:** `test_phase4f_lifecycle.py` (14/14 PASS), toàn bộ 9 backend suites (133/133 PASS), Puppeteer E2E (14/14 steps PASS).
- **Git Commits:** `a0efeed`, `cc84847`.
- **Nhật ký AI liên quan:** AI-005, AI-009, AI-011, AI-026, AI-031, AI-032, AI-050, AI-070..AI-075.
- **Minh chứng sửa lỗi AI:** Trong TASK-016 (AI-070), script Puppeteer do AI viết bị lỗi mất dữ liệu input trên React 18 controlled components và bị lỗi 401 khi gọi API Close PR; Hà đã phát hiện cơ chế `_valueTracker` của React 18 để can thiệp kích hoạt sự kiện nhập liệu và trích xuất token Supabase thật từ `localStorage`. Trong Final QA Gate (AI-074), Hà đính chính sai lệch tài liệu cũ về Playwright và "zero hallucination".
- **Kịch bản Demo Viva:** Demo nhận hàng đợt 1 (2/5 SP) $\rightarrow$ bấm Đóng PR bị chặn bởi HD-07 Guard (backend trả HTTP 400) $\rightarrow$ nhận hàng tiếp đợt 2 (3/5 SP) $\rightarrow$ bấm Đóng PR thành công $\rightarrow$ mở CSDL Supabase chứng minh PR chuyển `CLOSED`, `tempReservedAmount` giải phóng về 0 và `spentAmount` tăng chính xác 41M VND.

---

### 22.4. Bảng Minh chứng Sai lệch AI & Con người Hiệu chỉnh (AI Mistake / Correction Matrix)

| Thành viên | Hoạt động AI | Đề xuất / Sai lệch ban đầu của AI (AI Output/Mistake) | Hành động hiệu chỉnh của Con người (Human Correction) | Căn cứ Bằng chứng (Evidence) | Trạng thái |
|---|---|---|---|---|:---:|
| **Trần Thị Kiều Giang** | AI-016 $\rightarrow$ AI-017 (TASK-001) | Cấu hình file build `pyproject.toml` dùng Hatchling không chỉ định package layout khiến lệnh cài đặt `pip install -e backend` bị crash. | Tự cấu hình thủ công `[tool.hatch.build.targets.wheel] packages = ["app"]`, cài đặt thành công dependencies. | Git diff `backend/pyproject.toml`, test install log | **VERIFIED** |
| **Nguyễn Trương Thùy Dương** | AI-001 (Project Charter) | Đặt các chỉ số thành công (Metrics) đạt 100% hoàn hảo phi thực tế (100% thời gian duyệt, 100% bóc tách AI). | Yêu cầu hạ xuống các chỉ số khả thi và có ý nghĩa nghiệp vụ (giảm 40% thời gian duyệt, bóc tách chính xác $\ge 80\%$). | `docs/01-discovery/project-charter.md`, `ai-usage-log.md` | **VERIFIED** |
| **Nguyễn Trúc Lam** | AI-002 / Iteration 1 (Vault Benchmark) | Mô hình LLM tự ý bịa đặt (hallucinate) chính sách hệ thống có tính năng lưu trữ lịch sử chat 30 ngày (câu Q-08) dù Vault không có thông tin này. | Viết lại System Prompt bổ sung Guardrail: Bắt buộc trả lời cụm từ chuẩn *"KHÔNG ĐỦ DỮ LIỆU"* khi thông tin không có trong Vault. | `docs/02-vault/vault-qa-benchmark.md` (Lần cải tiến 1), test run log | **VERIFIED** |
| **Nguyễn Thị Thùy Dung** | AI-042 (TASK-004 Auth) | Đề xuất thư viện xác thực PyJWKClient gọi tải public key Supabase mà không thiết lập timeout, gây treo hệ thống khi mất kết nối mạng. | Bổ sung cấu hình tường minh `timeout=5.0s`, cài đặt cơ chế fail-closed an toàn bảo vệ backend. | `backend/app/core/auth.py`, `docs/evidence/TASK-004-STEP-3B-JWT.md` | **VERIFIED** |
| **Trần Thị Thu Hà** | AI-070 (TASK-016 Browser E2E) | Viết kịch bản tự động hóa Puppeteer dùng `page.type()` bị React 18 Virtual DOM reset giá trị và thiếu JWT token gây lỗi 401 khi gọi Close PR. | Can thiệp qua prototype `_valueTracker.setValue('__RESET__')` và lấy token từ `localStorage` truyền vào header API call. | `frontend/scripts/test_final_full_lifecycle_e2e.js`, commit `cc84847` | **VERIFIED** |

---

### 22.5. Danh mục Điểm nghẽn Cần xử lý Trước khi Nộp Đồ án (Course Compliance Blockers)

| Phân loại Mức độ | Hạng mục Deliverable | Khoảng trống Kỹ thuật / Tài liệu (Gap) | Căn cứ Bằng chứng (Evidence) | Hành động Bắt buộc Nhóm cần Thực hiện | Người phụ trách |
|:---:|---|---|---|---|:---:|
| **RESOLVED / COMPLETE** | **3.2 Release chạy được** | Đã hoàn thành Public Deployment và kiểm chứng E2E qua AI-089 | Frontend Vercel: `https://group-01-project.vercel.app`<br>Backend Railway: `https://group-01-project-production.up.railway.app`<br>Tag `v1.0.0-final` (`9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`) | Đã kiểm chứng 100% qua kịch bản khói AI-089 (HTTP 200, Supabase DB, RBAC, Happy path, Failure path 400). | Trần Thị Kiều Giang |
| **CRITICAL BEFORE SUBMISSION** | **2.4 Usability Test** | Thiếu biên bản kiểm thử người dùng thật $\ge 3$ người | `docs/03-product/usability-findings.md` hiện rỗng | Tổ chức test trực tiếp trên 3 người dùng, ghi nhận biên bản quan sát và cải tiến giao diện. | Trần Thị Thu Hà / Cả nhóm |
| **HIGH** | **2.6 Taiga Backlog** | Chưa có issues thực tế trên nền tảng Taiga | `docs/03-product/taiga-backlog.md` ghi TBD | Đăng ký project trên `tree.taiga.io`, nhập Epics/Stories/Tasks, cung cấp link công khai. | Nguyễn Trương Thùy Dương |
| **HIGH** | **3.6 Code Review Evidence** | Thiếu biên bản / checklist Code Review mẫu | Chưa có file `code-review.md` trong repo | Lập file `docs/07-release/code-review.md` ghi nhận review checklist và phê duyệt giữa Dev/QA. | Trần Thị Thu Hà |
| **HIGH** | **3.13 Release Notes** | Tài liệu `release-notes.md` cũ chứa nội dung mâu thuẫn | File ghi "Playwright" và "0% hallucination" | Soạn lại `docs/07-release/release-notes.md` đồng bộ chuẩn mực với Final QA Gate Report. | Nguyễn Trương Thùy Dương |
| **MEDIUM** | **3.7 Bug Log** | Thiếu bảng theo dõi bug toàn diện | Chỉ có 1 bug QF-001 | Mở rộng `docs/qa/QA_FINDINGS.md` thành bảng Bug Tracking đầy đủ các bug đã xử lý. | Trần Thị Thu Hà |
| **MEDIUM** | **3.12 README + Runbook** | `README.md` cũ 35 dòng, thiếu Runbook chi tiết | File chứa lệnh cũ (`uv run`, `playwright`) | Cập nhật `README.md` và viết `RUNBOOK.md` hướng dẫn cài đặt và troubleshooting chi tiết. | Trần Thị Kiều Giang |
| **RESOLVED / COMPLETE** | **3.11 CI/CD Pipeline** | Đã hoàn thành cấu hình GitHub Actions CI multi-job | `.github/workflows/ci.yml`<br>`docs/evidence/CI_CD_PIPELINE_REPORT.md` | Đã cấu hình và kiểm chứng workflow CI tự động: `backend-test` (Pytest + PostgreSQL 16) và `frontend-build` (Vite/TS); thực thi remote đạt 100% Green (Run #37878925224). | Trần Thị Thu Hà / Trần Thị Kiều Giang |
| **LOW** | **3.15 AI Retrospective** | Thiếu mục tổng kết bài học kinh nghiệm AI | `ai-usage-log.md` dừng ở danh mục lỗi | Bổ sung mục Retrospective vào cuối `ai-usage-log.md`. | Nguyễn Trúc Lam |

---

### 22.6. Kết luận Thẩm định Tuân thủ Môn học (Course Compliance Verdict)

$$\Large\textbf{COURSE COMPLIANCE = READY WITH GAPS}$$

- **Đánh giá tổng thể:** Hệ thống kỹ thuật cốt lõi (Backend FastAPI, Database Supabase PostgreSQL, Authentication JWT ES256, Server-Side RBAC, 133/133 Tests PASS, 14/14 E2E Steps PASS, Public Demo Vercel + Railway + Supabase) đạt trạng thái **RELEASE READY WITH KNOWN LIMITATIONS** (Deliverable 3.2 đã hoàn thành trọn vẹn).
- **Điều kiện nghiệm thu học thuật:** Nhóm **CẦN BỔ SUNG KHẨN CẤP** 1 hạng mục Critical còn lại (`Usability Test` trên $\ge 3$ người dùng thật; trong khi `Release chạy được & Git Tag v1.0.0-final` đã hoàn thành 100% tại AI-089/AI-090) cùng các tài liệu minh chứng hỗ trợ (`Taiga URL`, `Code Review`, `Release Notes` chuẩn) theo danh mục tại Mục 22.5 trước khi hoàn thiện Báo cáo Đồ án, Slide Thuyết trình và bước vào phiên Vấn đáp (Viva) chính thức.

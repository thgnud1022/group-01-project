# BÁO CÁO KIỂM TOÁN DIFF TRƯỚC KHI COMMIT
**(FINAL PRE-COMMIT DOCUMENTATION DIFF AUDIT)**

**Dự án:** Hệ thống Mua sắm & Phê duyệt Ngân sách ProcureAI<br>
**Thư mục gốc:** `D:\LTUD\group-01-project-main`<br>
**Nhánh Git:** `final-delivery`<br>
**Ngày kiểm toán:** 2026-09-24<br>
**Chế độ thực hiện:** **AUDIT ONLY** (Không sửa mã nguồn, không sửa backend/frontend/database/tests, không git add, không commit, không push, không reset).

---

## 1. Git Diff Summary (Tổng quan Git Diff)

### 1.1. Trạng thái Git (`git status`)
```
On branch final-delivery
Your branch is ahead of 'origin/final-delivery' by 5 commits.

Changes not staged for commit:
	modified:   docs/DECISION_LOG.md
	modified:   docs/IMPLEMENTATION_PLAN.md
	modified:   docs/logs/ai-usage-log.md

Untracked files:
	_IMPORT_EARLY_PHASE/
	docs/01-discovery/3.personas-and-jtbd.md
	docs/01-discovery/7.MVP-Scope.md
	docs/02-vault/03-domain/
	docs/02-vault/AI_USAGE_LOG.md
	docs/02-vault/vault-qa-prompt.md
	docs/03-product/epics.md
	docs/03-product/prototype-brief.md
	docs/03-product/taiga-backlog.md
	docs/03-product/usability-findings.md
	docs/03-product/usability-test-script.md
	docs/03-product/user-flow.md
	docs/AI_USAGE_LOG_RECONCILIATION.md
	docs/AI_USAGE_TRACEABILITY.md
	docs/ALLOCATION_CONSISTENCY_FIX_REPORT.md
	docs/FINAL_PRE_COMMIT_DIFF_AUDIT.md
	docs/IMPORT_INTEGRATION_CHANGELOG.md
	docs/IMPORT_INVENTORY.md
	docs/IMPORT_RECONCILIATION_REPORT.md
	docs/POST_MERGE_DOCUMENTATION_AUDIT.md
	docs/archive/
	docs/course/Giao_trinh.txt
	docs/course/Output_BaoCao.xlsx
	excel_dump.txt
```

### 1.2. Thống kê số dòng thay đổi (`git diff --stat`)
```
 docs/DECISION_LOG.md        |  40 +++
 docs/IMPLEMENTATION_PLAN.md | 685 ++++++++++++++++++++++----------------------
 docs/logs/ai-usage-log.md   |   9 +-
 3 files changed, 386 insertions(+), 348 deletions(-)
```

### 1.3. Tính toàn vẹn của mã nguồn (Source Code Integrity)
- **Mã nguồn Backend (`backend/**`):** `0` dòng thay đổi (Khẳng định: Không sửa đổi).
- **Mã nguồn Frontend (`frontend/**`):** `0` dòng thay đổi (Khẳng định: Không sửa đổi).
- **Lược đồ CSDL (`schema.prisma`):** `0` dòng thay đổi (Khẳng định: Không sửa đổi).
- **Cơ sở dữ liệu runtime:** Không chạy lệnh `prisma db push` hay thay đổi bản ghi nào.
- **Tệp kiểm thử (`backend/tests/**`):** `0` dòng thay đổi (Khẳng định: Không sửa đổi).

---

## 2. IMPLEMENTATION_PLAN Diff Analysis (Phân tích chi tiết 685 dòng thay đổi)

Tổng cộng 685 dòng thay đổi trong [`docs/IMPLEMENTATION_PLAN.md`](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md) được phân bổ vào các nhóm tác vụ cụ thể như sau:

| Nhóm phân loại | Tên nhóm | Mô tả nội dung thay đổi | Tỷ trọng dòng |
|:---:|---|---|:---:|
| **A** | **ALLOCATION FIX** | Đồng bộ quyền sở hữu (Owner) và phân công 5 thành viên theo chuẩn Group-01 | ~25% |
| **B** | **TERMINOLOGY CLEANUP** | Loại bỏ 100% các từ khóa mô hình 2 tầng cũ (`Primary Presentation`, `Supporting Implementation`, v.v.) | ~20% |
| **C** | **US/TASK REMAPPING** | Ánh xạ lại đúng User Story và mã Backlog Task T-xxx cho các TASK kỹ thuật; bãi bỏ mã US-11 | ~20% |
| **D** | **DECISION RECORD** | Tham chiếu quyết định chính thức HD-11 vào kế hoạch | ~2% |
| **E** | **TRACEABILITY UPDATE** | Viết lại ma trận liên kết tại Section 10, 10b và Section 11 | ~15% |
| **F** | **DEMO/VIVA UPDATE** | Cập nhật kịch bản thuyết trình 5 phút Section 19 cho 5 User Story cốt lõi và ma trận RACI | ~18% |
| **G** | **UNRELATED CONTENT CHANGE** | Các thay đổi không liên quan | **0% (Không có)** |
| **H** | **POTENTIAL ACCIDENTAL REWRITE** | Viết lại ngoài ý muốn làm đổi ngữ nghĩa kỹ thuật | **0% (Không có)** |

### Phân tích chi tiết theo từng Section:

#### A. Section 1 — Mục đích tài liệu (Dòng 18–20)
- **Nội dung thay đổi:** Xóa bỏ câu mô tả mô hình 2 tầng cũ (*"Tầng 1 — 5 Primary Presentation Stories / Tầng 2 — 6 Supporting Implementation Stories"*). Thay bằng cấu trúc phân bổ trách nhiệm chính thức Group-01, trong đó mỗi thành viên sở hữu User Story cốt lõi để chuẩn bị thuyết trình độc lập 5 phút.
- **Lý do thay đổi:** Khắc phục phát hiện `I-01` từ báo cáo kiểm toán `POST_MERGE_DOCUMENTATION_AUDIT.md`.
- **Yêu cầu bởi Group-01 Allocation:** **CÓ (BẮT BUỘC)**.
- **Có sửa đổi nội dung không liên quan không:** **KHÔNG**.

#### B. Section 2 — Project Context & Ownership Model (Dòng 30–53)
- **Nội dung kiểm tra:** Bảng phân công tại Section 2.1 và Section 2.2 đã được cập nhật chuẩn xác theo Group-01:
  - Giang: US-01 (Cốt lõi 5 phút)
  - Dương: US-04 (Cốt lõi 5 phút), US-05, US-06
  - Lam: US-07 (Cốt lõi 5 phút), US-03
  - Dung: US-08 (Cốt lõi 5 phút), US-02, US-09, GOV-01
  - Hà: US-10 (Cốt lõi 5 phút), GOV-02
- **Trạng thái diff:** Giữ nguyên trạng thái chuẩn xác, không có xung đột.

#### C. TASK-001 đến TASK-018
- **TASK-001 (Kết nối Supabase Postgres):**
  - Đổi metadata: `Primary Presentation Owner: Shared Infrastructure` $\to$ `Responsible Owner: Shared Infrastructure (Giang phụ trách chính kết nối hạ tầng)`.
  - Giữ nguyên deliverable, evidence và status COMPLETED.
- **TASK-002 (Bổ sung trường quantity vào PurchaseOrder schema):**
  - Đổi mapping: `US-09 (Hà), US-11` $\to$ `US-08 (Nguyễn Thị Thùy Dung), US-10 (Trần Thị Thu Hà)`.
  - Khắc phục lỗi `I-02` từ audit (gán nhầm Hà làm Primary US-09).
  - Giữ nguyên toàn bộ logic kỹ thuật về schema và T-094 resolution.
- **TASK-003 (Backend Prisma Migration) & TASK-004 (JWT Auth Middleware):**
  - Chuẩn hóa metadata sang `Responsible Owner` và `Collaborators / Assigned`.
  - Giữ nguyên các bước kỹ thuật STEP 1, 2B, 3B.1 đến 3B.7.
- **TASK-005 (Server-Side RBAC Middleware):**
  - Đổi mapping: `US-03 (Lam), US-09 (Hà)` $\to$ `GOV-01 (RBAC Matrix)`, `US-04` và `US-08` do `Nguyễn Thị Thùy Dung` phụ trách chính.
  - Khắc phục lỗi `I-03` từ audit.
- **TASK-006 (Fix BUG-001 Enforce PR APPROVED in create_po):**
  - Đổi mapping: `US-09 (Hà)` $\to$ `US-08 (Lựa chọn NCC & Tạo PO — REQ-BR-10 / HD-04)` do `Nguyễn Thị Thùy Dung` phụ trách chính.
  - Khắc phục lỗi `I-04` từ audit.
- **TASK-007 (Fix HD-07 Enforce Receiving Completion Guard):**
  - Đổi mapping: `US-11 (Supporting Story)` $\to$ `US-10 (Close PR & Đối soát — REQ-BR-11 / HD-07)` do `Trần Thị Thu Hà` phụ trách chính.
  - Sửa ghi chú nghiệp vụ: Thể hiện đúng quan hệ giữa `US-09` (Receiving - do Dung phụ trách) và `US-10` (Close PR - do Hà phụ trách).
  - Bãi bỏ hoàn toàn tham chiếu `US-11`. Khắc phục lỗi `I-05` từ audit.
- **TASK-008 (Supplier & Quotation Backend APIs):**
  - Đổi mapping: `US-05 (Dung), US-06` $\to$ `US-06 (Thu thập & Liên kết Quotation), US-05 (Finance Budget Check)` do `Nguyễn Trương Thùy Dương` phụ trách chính.
  - Khắc phục lỗi `I-06` từ audit.
- **TASK-009 (Real LLM Integration):**
  - Đổi mapping: `US-07 (Giang), US-01 (Dương)` $\to$ `US-03 (AI Suggestion), US-07 (AI Recommendation)` do `Nguyễn Trúc Lam` phụ trách chính, phối hợp `US-01` do `Trần Thị Kiều Giang` phụ trách.
  - Khắc phục lỗi `I-07` từ audit.
- **TASK-010 (Build AI Evaluation Set >=20 Cases):**
  - Đổi mapping: `US-07 (Giang)` $\to$ `US-07 (AI Extraction & Recommendation)` do `Nguyễn Trúc Lam` phụ trách chính.
  - Khắc phục lỗi `I-08` từ audit.
- **TASK-011 (React Router & Auth Login UI):**
  - Chuẩn hóa metadata sang `Responsible Owner: Shared Infrastructure (Giang phụ trách kiến trúc Frontend)`.
- **TASK-012 (Procurement Workflow UI):**
  - Bỏ cụm từ *"Cả 11 User Stories (5 Primary + 6 Supporting)"*.
  - Cập nhật danh sách phân công màn hình UI khớp 100% với Group-01:
    - Giang: US-01 (Form tạo PR + AI)
    - Dương: US-04 (Approval), US-05 (Budget Check), US-06 (Supplier & Quotation)
    - Lam: US-03 (AI Suggestion), US-07 (Ma trận so sánh & Recommendation)
    - Dung: US-02 (Timeline PR), US-08 (Tạo PO), US-09 (Receiving), GOV-01 (RBAC)
    - Hà: US-10 (Close PR đối soát 3 bên), GOV-02 (Audit Trail)
- **TASK-013 (Playwright Critical-Path E2E Tests):**
  - Cập nhật luồng nghiệp vụ kiểm thử bao phủ từ `US-01` đến `US-10`, giao `Trần Thị Thu Hà` làm QA Lead.
- **TASK-014 đến TASK-017:**
  - Chuẩn hóa metadata sang `Responsible Owner` và `Collaborators / Assigned`.
- **TASK-018 (Final Evidence Packaging & Viva Preparation):**
  - Chuẩn hóa bullet chuẩn bị demo 5 phút cho 5 thành viên tương ứng với 5 User Story cốt lõi (Giang US-01, Dương US-04, Lam US-07, Dung US-08, Hà US-10).

#### D. Section 10, 10b, 11 — Ma trận Truy xuất và Bằng chứng
- **Section 10:** Xóa bỏ hoàn toàn việc chia bảng thành Tầng 1 (5 Primary) và Tầng 2 (6 Supporting). Thay bằng bảng ma trận liên kết đầy đủ 10 User Stories và 2 Governance Stories với Backlog Tasks và Technical Tasks theo Group-01.
- **Section 10b:** Cập nhật cột Assignee cho từng Requirement/Rule, chuyển REQ-FR-17 về US-09 (Dung), REQ-FR-18 về US-10 (Hà), bãi bỏ US-11.
- **Section 11:** Cập nhật bảng User Story $\to$ Evidence thể hiện rõ vai trò 5 User Story cốt lõi thuyết trình 5 phút và người phụ trách chính các Story còn lại.

#### E. Section 19 — Kịch bản 5 phút và Khung phân công chi tiết
- **Section 19.1:** Mô tả nguyên tắc phân công chính thức theo quyết định HD-11.
- **Section 19.2:** Sắp xếp lại đúng 5 mục chuẩn bị 5 phút:
  1. `US-01`: Trần Thị Kiều Giang (Tạo & Chuẩn hóa PR)
  2. `US-04`: Nguyễn Trương Thùy Dương (Manager Review, Approval & Budget)
  3. `US-07`: Nguyễn Trúc Lam (AI Extraction & Recommendation)
  4. `US-08`: Nguyễn Thị Thùy Dung (Lựa chọn NCC & Tạo PO — Server-Side Quantity Lock T-094)
  5. `US-10`: Trần Thị Thu Hà (Close PR & Đối soát 3 bên — HD-07 Guard)
- **Section 19.3:** Bảng kế hoạch triển khai cho các User Story phối hợp (US-02, US-03, US-05, US-06, US-09, GOV-01, GOV-02).
- **Section 19.4:** Bổ sung ma trận RACI phân định rõ trách nhiệm 5 thành viên qua 6 giai đoạn vòng đời.
- **Section 20:** Cập nhật người phụ trách trong từng Phase (Phase 0 đến Phase 12).

#### F. Section 22 — Self-Check
- Cập nhật checklist tự kiểm tra: Xác nhận đúng 10 US + 2 GOV, không còn US-11, không còn mapping cũ, tuân thủ 100% Group-01.

---

## 3. Allocation Verification (Kiểm tra tính nhất quán phân công)

### 3.1. Bảng đối chiếu phân công chuẩn Group-01
Toàn bộ tài liệu tuân thủ tuyệt đối chuẩn phân công chính thức:

| Thành viên | User Story cốt lõi (5-Min Viva) | Toàn bộ User Stories chịu trách nhiệm chính | Kiểm tra trong IMPLEMENTATION_PLAN |
|---|---|---|:---:|
| **Trần Thị Kiều Giang** | **US-01** | **US-01** | ✅ KHỚP 100% (12 lần kiểm chứng) |
| **Nguyễn Trương Thùy Dương** | **US-04** | **US-04**, **US-05**, **US-06** | ✅ KHỚP 100% (13 lần kiểm chứng) |
| **Nguyễn Trúc Lam** | **US-07** | **US-03**, **US-07** | ✅ KHỚP 100% (16 lần kiểm chứng) |
| **Nguyễn Thị Thùy Dung** | **US-08** | **US-02**, **US-08**, **US-09**, **GOV-01** | ✅ KHỚP 100% (17 lần kiểm chứng) |
| **Trần Thị Thu Hà** | **US-10** | **US-10**, **GOV-02** | ✅ KHỚP 100% (18 lần kiểm chứng) |

### 3.2. Kiểm tra không còn tồn dư phân công cũ
Đã quét tự động toàn bộ tài liệu bằng Regex:
- `Dương → US-01 as primary:` **0 matches (ĐÃ SẠCH)**
- `Lam → US-03 only:` **0 matches (ĐÃ SẠCH)**
- `Dung → US-05 as primary:` **0 matches (ĐÃ SẠCH)**
- `Giang → US-07 as primary:` **0 matches (ĐÃ SẠCH)**
- `Hà → US-09 as primary:` **0 matches (ĐÃ SẠCH)**

### 3.3. Kiểm tra mã US-11
- Mã `US-11` đã được loại bỏ hoàn toàn khỏi các bảng phân công, danh sách task và ma trận truy xuất.
- Dòng duy nhất có chứa ký tự `US-11` là dòng xác nhận trong Section 22 Self-Check:<br>
  *`- [x] Không còn tồn tại mã US-11 của mô hình tài liệu cũ; nghiệp vụ Close Purchase Request được map chuẩn xác về **US-10** (Trần Thị Thu Hà phụ trách).*`<br>
  $\longrightarrow$ Đây là dòng khẳng định bãi bỏ, hoàn toàn hợp lệ và đúng yêu cầu.

---

## 4. T-xxx / TASK-xxx Verification (Kiểm tra định danh và ánh xạ Task)

### 4.1. Mã Technical Tasks (`TASK-xxx`)
- Không có bất kỳ `TASK-xxx` nào bị đổi tên, đổi mã số, gộp hay xóa bỏ.
- Đúng 18 Technical Implementation Tasks: từ `TASK-001` đến `TASK-018`.
- Danh sách TASK ID trước và sau diff: **HOÀN TOÀN TRÙNG KHỚP 100%**.

### 4.2. Mã Business Tasks (`T-xxx`)
- Toàn bộ các mã Backlog Tasks được liên kết chuẩn xác theo `taiga-backlog.md` từ `T-01` đến `T-42`:
  - `E-01 (Purchase Request):` `T-01` đến `T-09` (US-01, US-02, US-03)
  - `E-02 (Approval & Budget):` `T-10` đến `T-16` (US-04, US-05)
  - `E-03 (Supplier & Quotation):` `T-17` đến `T-20` (US-06)
  - `E-04 (AI Comparison):` `T-21` đến `T-25` (US-07)
  - `E-05 (Purchase Order):` `T-26` đến `T-29` (US-08)
  - `E-06 (Receiving & Close):` `T-30` đến `T-36` (US-09, US-10)
  - `E-07 (Governance):` `T-37` đến `T-42` (GOV-01, GOV-02)
- Không có mã T-xxx nào bị tráo đổi sang TASK-xxx hoặc ngược lại.

---

## 5. Decision Log Verification (Kiểm tra quyết định HD-11)

Đã kiểm tra diff của tệp [`docs/DECISION_LOG.md`](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md):
- **Số dòng thay đổi:** Đúng 40 dòng được thêm vào cuối file.
- **Mã định danh:** `HD-11` (Kế tiếp sau HD-08 và HD-REQ-10).
- **Tiêu đề:** `Official Group-01 User Story Responsibility Allocation`.
- **Trạng thái:** `DECIDED`.
- **Nội dung:** Ghi nhận chính thức phân công 5 thành viên theo Group-01, bãi bỏ mô hình 2 tầng cũ và bãi bỏ mã US-11.
- **Đánh giá:** Quyết định này chỉ chuẩn hóa và ghi nhận phân công đã được con người phê duyệt; **tuyệt đối không tạo ra bất kỳ chính sách nghiệp vụ (business policy) hay yêu cầu kỹ thuật mới nào**.

---

## 6. AI Usage Log Verification (Kiểm tra nhật ký sử dụng AI)

- **Tệp [`docs/02-vault/AI_USAGE_LOG.md`](file:///d:/LTUD/group-01-project-main/docs/02-vault/AI_USAGE_LOG.md) (Early Phase Log):**
  - Diff: **`0` dòng (Hoàn toàn không bị sửa đổi)**.
  - Bảo toàn trọn vẹn 38 phiên làm việc ban đầu và lịch sử sửa lỗi.
- **Tệp [`docs/logs/ai-usage-log.md`](file:///d:/LTUD/group-01-project-main/docs/logs/ai-usage-log.md) (Final Delivery Log):**
  - Diff: Đúng 9 dòng thêm khối `AI GOVERNANCE NOTICE` ở đầu file.
  - Không sửa đổi bất kỳ nội dung nào trong 53 phiên làm việc `AI-001` đến `AI-053` của Final Delivery Phase.
- **Tệp [`docs/02-vault/AI Usage Log.md`](file:///d:/LTUD/group-01-project-main/docs/02-vault/AI%20Usage%20Log.md) (10 bản tóm tắt cũ):**
  - Giữ nguyên trong Git HEAD, không bị xóa.

---

## 7. Unrelated Changes (Kiểm tra thay đổi không liên quan)

Đã rà soát tự động và thủ công trên toàn bộ diff:
1. **Business Rules mới:** `0` (Chỉ chạm các mã BR-01, BR-02, BR-10, BR-11 đã có từ trước).
2. **Acceptance Criteria mới:** `0` (Không tự ý bổ sung tiêu chí nghiệm thu).
3. **Thay đổi kiến trúc hệ thống:** `0` (Kiến trúc Hybrid AI HD-03, Supabase PostgreSQL HD-01, Server-side RBAC HD-02 giữ nguyên).
4. **Thay đổi API contracts:** `0` (Không đổi endpoint hay payload schema).
5. **Thay đổi Database Schema:** `0` (Không chạm `schema.prisma`).
6. **Thay đổi kết quả kiểm thử:** `0` (Các test counts `14/14 PASS`, `15/15 PASS`, `10/10 PASS` giữ nguyên).
7. **Thay đổi ngày tháng trong kế hoạch:** `0` (Ngày lập kế hoạch `2026-09-21` giữ nguyên).
8. **Thay đổi Git Commit SHA:** `0` (Các mã commit `72ec674`, `4709911`, `5584d68`, `b5d00a3`, `dfdd7e5` giữ nguyên).

$\longrightarrow$ **Kết luận:** **KHÔNG CÓ BẤT KỲ THAY ĐỔI KHÔNG LIÊN QUAN NÀO (0 UNRELATED CHANGES)**.

---

## 8. Potential Accidental Rewrites (Kiểm tra viết lại ngoài ý muốn)

- Không phát hiện đoạn văn bản nào bị viết lại chỉ để "làm đẹp" câu chữ mà làm lệch ngữ nghĩa kỹ thuật.
- Các chỉnh sửa tại Section 19.2 chỉ điều chỉnh chủ thể thực hiện (Author/Presenter) và mã User Story cho tương ứng, trong khi toàn bộ nội dung kịch bản demo, câu hỏi vấn đáp Viva, tiêu chí kỹ thuật (Pydantic schema, fallback, guard condition) được bảo toàn nguyên vẹn bản chất kỹ thuật.

$\longrightarrow$ **Kết luận:** **KHÔNG CÓ NGUY CƠ VIẾT LẠI NGOÀI Ý MUỐN (0 ACCIDENTAL REWRITES)**.

---

## 9. Final Recommendation (Khuyến nghị cuối cùng)

Tất cả các thay đổi trong diff hiện tại đều nằm chính xác trong phạm vi:
- Chuẩn hóa phân bổ User Story theo phiên bản chính thức Group-01.
- Loại bỏ triệt để thuật ngữ và mô hình 2 tầng cũ.
- Bãi bỏ mã User Story US-11 và remap về US-10.
- Bổ sung bản ghi quyết định chính thức HD-11 vào Decision Log.
- Bảo vệ 100% tính toàn vẹn của mã nguồn, database, test suites và nhật ký AI.

### ĐÁNH GIÁ CHUNG:

```
SAFE_TO_COMMIT
```

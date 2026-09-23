# IMPORT RECONCILIATION REPORT — EARLY PHASE ARTIFACTS

**Ngày thực hiện đối chiếu:** 2026-09-23  
**Dự án hiện tại:** `D:\LTUD\group-01-project-main`  
**Folder đối chiếu:** `D:\LTUD\group-01-project-main\_IMPORT_EARLY_PHASE\group-01`  
**Nhánh Git:** `final-delivery`  
**Trạng thái kiểm tra:** Hoàn thành đối chiếu 37/37 artifacts  

---

## 1. Nguyên tắc đối chiếu & xử lý

1. **Source of Truth:** Project hiện tại là căn cứ tối cao cho toàn bộ runtime, mã nguồn (Backend FastAPI + Prisma, Frontend React, Database Supabase PostgreSQL) và các quyết định kỹ thuật đã phê duyệt.
2. **Bảo toàn Evidence:** Folder import là nguồn bổ sung cho các artifact giai đoạn đầu, đặc biệt là **AI Usage Log gốc (AI-001 đến AI-038)**, User Research bằng chứng gốc và cấu trúc phân công ban đầu.
3. **Không ghi đè (No Overwrite):** Tuyệt đối không copy đè toàn bộ folder import; không để các file placeholder, scaffold cũ ghi đè lên tài liệu kỹ thuật và mã nguồn hoàn thiện hiện tại.
4. **Minh bạch Conflict:** Mọi mâu thuẫn về phân công User Story, ID hoặc Business Rule đều được gắn cờ `ALLOCATION CONFLICT — HUMAN DECISION REQUIRED`.

---

## 2. Phân loại chi tiết 8 nhóm Artifacts

### Nhóm 1: UNIQUE_HISTORICAL_ARTIFACT (Artifacts lịch sử độc bản — Cần bảo toàn 100%)
Các artifact này chứa bằng chứng gốc hoặc dữ liệu phân tích chi tiết của giai đoạn đầu:

1. **`docs/02-vault/AI_USAGE_LOG.md` (24,735 Bytes):**
   - *Nội dung:* Chứa đầy đủ 38 AI sessions (`AI-001` đến `AI-038`) của giai đoạn đầu, có bảng Prompt/Skill, Verification, Error Corrections chi tiết.
   - *Đánh giá:* **DIRECT EVIDENCE** quý giá nhất của giai đoạn Early Phase.
   - *Đề xuất xử lý:* Khôi phục nguyên vẹn vào `docs/02-vault/AI_USAGE_LOG.md`.

2. **`docs/01-discovery/2.user-research.md` (14,100 Bytes):**
   - *Nội dung:* Báo cáo Mini-study đầy đủ 11 mục, 8 bằng chứng phỏng vấn (E-01..E-08), 4 cụm chủ đề (Themes A-E), Fact vs Assumption.
   - *So với hiện tại:* Bản hiện tại `docs/01-discovery/user-research.md` (6,358 Bytes) bị rút gọn mất bảng chi tiết phỏng vấn.
   - *Đề xuất xử lý:* Lưu trữ an toàn vào `docs/archive/early-phase/01-discovery/2.user-research.md` và giữ làm evidence gốc.

3. **`docs/01-discovery/3.personas-and-jtbd.md` (10,944 Bytes):**
   - *Nội dung:* Đặc tả chi tiết 5 Personas và Jobs-to-be-Done (Employee, Manager, Procurement, Finance, Admin).
   - *So với hiện tại:* Project hiện tại chưa có file độc lập này.
   - *Đề xuất xử lý:* Khôi phục vào `docs/01-discovery/3.personas-and-jtbd.md` và liên kết trong index.

4. **`docs/03-product/taiga-backlog.md` (14,563 Bytes):**
   - *Nội dung:* Bản backlog chi tiết 7 Epics, 10 User Stories, 42 Tasks (T-01 đến T-42), Estimate, Sprint và Phân công Primary Owner.
   - *So với hiện tại:* Project hiện tại chưa có file `taiga-backlog.md`.
   - *Đề xuất xử lý:* Khôi phục vào `docs/03-product/taiga-backlog.md` kèm theo ghi chú phân loại Conflict.

---

### Nhóm 2: MISSING_IN_CURRENT (Chưa có trong project hiện tại — An toàn tích hợp)
Các file bổ trợ giai đoạn đầu bị thiếu trong project hiện tại:

| File Path | Kích thước | Nội dung & Giá trị | Đề xuất tích hợp |
|---|:---:|---|---|
| `docs/01-discovery/7.MVP-Scope.md` | 9,078 B | Đặc tả phạm vi MVP, bảng phân loại Must/Should/Could/Out of Scope | Tích hợp vào `docs/01-discovery/7.MVP-Scope.md` |
| `docs/02-vault/vault-qa-prompt.md` | 7,738 B | System prompt chuẩn hóa cho trợ lý hỏi đáp tài liệu Vault | Tích hợp vào `docs/02-vault/vault-qa-prompt.md` |
| `docs/02-vault/03-domain/workflows.md` | 4,806 B | Luồng quy trình nghiệp vụ dạng Mermaid & nhánh rẽ Finance/Receiving | Tích hợp vào `docs/02-vault/03-domain/workflows.md` |
| `docs/03-product/epics.md` | 1,086 B | Khái quát 7 Epics sản phẩm và mục tiêu năng lực | Tích hợp vào `docs/03-product/epics.md` |
| `docs/03-product/prototype-brief.md` | 1,408 B | Yêu cầu thiết kế màn hình và các trạng thái luồng | Tích hợp vào `docs/03-product/prototype-brief.md` |
| `docs/03-product/usability-test-script.md` | 1,773 B | Kịch bản kiểm thử trải nghiệm người dùng (T-01..T-06) | Tích hợp vào `docs/03-product/usability-test-script.md` |
| `docs/03-product/usability-findings.md` | 633 B | Khung quan sát và ghi nhận kết quả usability testing | Tích hợp vào `docs/03-product/usability-findings.md` |
| `docs/03-product/user-flow.md` | 1,408 B | Thuyết minh luồng người dùng kèm sơ đồ Mermaid | Tích hợp vào `docs/03-product/user-flow.md` |

---

### Nhóm 3: CONFLICT (Mâu thuẫn cần lưu ý & Human Decision Required)

#### A. Conflict về phân công Primary Owner User Story:
- **Nguồn 1 — `taiga-backlog.md` (File import & Yêu cầu mục XI):**
  - **Trần Thị Kiều Giang:** PRIMARY **US-01** (Tạo Purchase Request)
  - **Nguyễn Thị Thùy Dung:** PRIMARY **US-02**, **US-08** (Tạo PO), **US-09** (Receiving), **GOV-01**
  - **Nguyễn Trúc Lam:** PRIMARY **US-03**, **US-07** (AI Extraction & Recommendation)
  - **Nguyễn Trương Thùy Dương:** PRIMARY **US-04** (Approval & Budget Check), **US-05**, **US-06**
  - **Trần Thị Thu Hà:** PRIMARY **US-10** (Close PR & 3-Way Matching), **GOV-02**
- **Nguồn 2 — `docs/IMPLEMENTATION_PLAN.md` (Project hiện tại):**
  - **Nguyễn Trương Thuỳ Dương:** Primary Owner **US-01** (Tạo PR)
  - **Nguyễn Trúc Lam:** Primary Owner **US-03** (Xem và xử lý Approval)
  - **Nguyễn Thị Thuỳ Dung:** Primary Owner **US-05** (Quản lý Supplier và Quotation)
  - **Trần Thị Kiều Giang:** Primary Owner **US-07** (AI phân tích và Recommendation)
  - **Trần Thị Thu Hà:** Primary Owner **US-09** (Lựa chọn Supplier và tạo PO)
- **Đánh giá ban đầu:** Xung đột phân công giữa bản thảo Taiga và mô hình phân công 2 tầng cũ của Implementation Plan.
- **Quyết định chính thức từ con người (HUMAN DECIDED):**
  * Con người đã phê duyệt chỉ đạo chính thức: **Dự án cũ là cái cần thay đổi, đổi theo phiên bản mới tức là folder `group-01` (`taiga-backlog.md`), tuyệt đối không gộp các User Story chịu trách nhiệm của mỗi người.**
  * Đã cập nhật Section 2 của `docs/IMPLEMENTATION_PLAN.md` đồng bộ 100% theo phiên bản mới:
    - **Trần Thị Kiều Giang:** Chịu trách nhiệm chính **US-01**
    - **Nguyễn Trương Thùy Dương:** Chịu trách nhiệm chính **US-04**, **US-05**, **US-06**
    - **Nguyễn Trúc Lam:** Chịu trách nhiệm chính **US-03**, **US-07**
    - **Nguyễn Thị Thùy Dung:** Chịu trách nhiệm chính **US-02**, **US-08**, **US-09**, **GOV-01**
    - **Trần Thị Thu Hà:** Chịu trách nhiệm chính **US-10**, **GOV-02**
  * Trạng thái xung đột: **RESOLVED BY HUMAN DECISION — CLOSED**.

#### B. Conflict về AI Usage Log IDs:
- **Trong `_IMPORT_EARLY_PHASE/group-01/docs/02-vault/AI_USAGE_LOG.md`:** Các mã từ `AI-005` đến `AI-038` thuộc về các task xây dựng Vault & Discovery.
- **Trong `docs/logs/ai-usage-log.md` hiện tại:** Các mã từ `AI-005` đến `AI-038` thuộc về các task kỹ thuật của Final Delivery Phase (Baseline, Git Setup, TASK-001, TASK-002, T-094, TASK-003).
- **Đánh giá:** Trùng mã định danh cục bộ (ID Collision) do hai giai đoạn được thực hiện độc lập tại các thời điểm khác nhau.
- **Hành động tuân thủ:**
  - Bảo toàn trọn vẹn file gốc `docs/02-vault/AI_USAGE_LOG.md` cho Early Phase.
  - Giữ nguyên `docs/logs/ai-usage-log.md` cho Final Delivery Phase.
  - Lập bảng đối chiếu chi tiết trong `docs/AI_USAGE_LOG_RECONCILIATION.md`.

---

### Nhóm 4: DUPLICATE (Bản sao lưu nội bộ trong folder import)
Các file nằm trong thư mục con của Vault chỉ là bản copy y hệt từ thư mục Discovery:
- `docs/02-vault/01-sources/user-research.md` (giống `docs/01-discovery/2.user-research.md`)
- `docs/02-vault/02-requirements/requirements.md` (giống `docs/01-discovery/5.requirements.md`)
- `docs/02-vault/03-domain/business_rules.md` (giống `docs/01-discovery/6.business-rules.md`)
- `docs/02-vault/03-domain/glossary.md` (giống `docs/01-discovery/4.glossary.md`)
- `docs/02-vault/source-priority.md` (trùng lặp với `docs/02-vault/source-priority.md` hiện tại)

*Xử lý:* Lưu giữ nguyên vẹn trong cấu trúc archive, không cần tạo thêm bản copy thứ ba.

---

### Nhóm 5: OLDER_VERSION (Bản cũ — Project hiện tại đã phát triển vượt bậc)
Các file trong folder import chỉ là bản thảo ban đầu, project hiện tại đã có phiên bản hoàn thiện và chi tiết hơn:
- `README.md` (779B vs 996B hiện tại)
- `docs/00-project-index.md` (2,022B vs 3,759B hiện tại)
- `docs/01-discovery/4.glossary.md` (2,476B vs 3,450B hiện tại)
- `docs/01-discovery/5.requirements.md` (7,975B vs 11,772B hiện tại)
- `docs/01-discovery/6.business-rules.md` (5,926B vs bản mở rộng hiện tại)
- `docs/02-vault/08-decisions/decision-log.md` (1,519B vs `docs/DECISION_LOG.md` 27,892B)
- `docs/02-vault/vault-qa-benchmark.md` (12,615B vs bản hiện tại 20,124B có kết quả test)
- `docs/03-product/PRD.md` (1,743B vs bản hiện tại 6,648B)
- `docs/03-product/user-stories.md` (2,290B vs `docs/03-product/user-story.md` 13,477B)

*Xử lý:* **SHOULD_NOT_IMPORT** đè lên bản hiện tại. Lưu vào `docs/archive/early-phase/` để làm tư liệu tham chiếu lịch sử.

---

### Nhóm 6: SHOULD_NOT_IMPORT (Các placeholder và scaffold rỗng)
Các file giữ chỗ rỗng hoặc scaffold cũ tuyệt đối không được đưa vào project:
- `docs/02-vault/09-meetings/README.md` (Placeholder 169B)
- `docs/03-product/prototype-URL/README.md` (Placeholder 252B)
- `docs/04-design/README.md` (Placeholder rỗng, trong khi project hiện tại đã có `DESIGN.md`, `prototype.md`)
- `docs/05-technical/README.md` (Placeholder rỗng, trong khi project hiện tại đã có `ADR`, `API.md`, `data-model.md`)
- `docs/06-testing/README.md` (Placeholder rỗng, trong khi project hiện tại đã có `playwright-e2e-us09.spec.ts`, `qa-comprehensive-test-matrix.md`)
- `docs/07-release/README.md` (Placeholder rỗng, trong khi project hiện tại đã có `release-notes.md`, `runbook.md`)
- `docs/logs/README.md` (Placeholder 160B)
- `src/.gitkeep`, `tests/.gitkeep` (Scaffold rỗng, project hiện tại có mã nguồn thực `backend/`, `frontend/`)

*Xử lý:* **Bỏ qua hoàn toàn (Intentionally Not Imported)**, không làm rác workspace.

---

## 3. Tổng kết Kế hoạch Tích hợp có kiểm soát

| Hành động | Số lượng File | Đường dẫn đích | Ghi chú an toàn |
|---|:---:|---|---|
| **Khôi phục nguyên bản (Direct Restore)** | 2 | `docs/02-vault/AI_USAGE_LOG.md`, `docs/03-product/taiga-backlog.md` | Giữ 100% nội dung gốc, bảo toàn chứng cứ |
| **Bổ sung tài liệu thiếu (Integrate Missing)** | 7 | `docs/01-discovery/3.personas-and-jtbd.md`, `docs/01-discovery/7.MVP-Scope.md`, `docs/02-vault/vault-qa-prompt.md`, `docs/02-vault/03-domain/workflows.md`, `docs/03-product/epics.md`, `docs/03-product/prototype-brief.md`, `docs/03-product/usability-*`, `docs/03-product/user-flow.md` | Làm giàu thêm kho tri thức, không đè code |
| **Lưu trữ lịch sử (Archive Historical)** | 20 | `docs/archive/early-phase/...` | Đánh dấu rõ HISTORICAL ARTIFACT |
| **Bỏ qua không import (Skip Scaffold/Placeholder)** | 8 | Bỏ qua | Tránh ghi đè lên tài liệu kỹ thuật & mã nguồn hiện tại |

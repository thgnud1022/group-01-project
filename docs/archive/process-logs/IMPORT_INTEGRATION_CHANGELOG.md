# IMPORT INTEGRATION CHANGELOG

**Ngày thực hiện:** 2026-09-23  
**Dự án:** AI Procurement & Purchase Approval System (Group 01)  
**Nhánh Git:** `final-delivery`  
**Mục tiêu:** Đối chiếu, khôi phục và tích hợp có kiểm soát các artifact giai đoạn đầu từ `_IMPORT_EARLY_PHASE/group-01` vào project hiện tại.  

---

## 1. Summary of Changes

### A. Files Added (Khôi phục trực tiếp vào thư mục tài liệu hoạt động)
1. `docs/01-discovery/3.personas-and-jtbd.md` (10,944 Bytes) — Bổ sung 5 personas và jobs-to-be-done.
2. `docs/01-discovery/7.MVP-Scope.md` (9,078 Bytes) — Bổ sung đặc tả phạm vi MVP và bảng Must/Should/Could/Out of Scope.
3. `docs/02-vault/AI_USAGE_LOG.md` (24,735 Bytes) — Khôi phục 100% nguyên bản nhật ký sử dụng AI 38 entries gốc (AI-001..AI-038) kèm Section 3 Error History.
4. `docs/02-vault/vault-qa-prompt.md` (7,738 Bytes) — Bổ sung System prompt chuẩn hóa cho trợ lý tra cứu Vault.
5. `docs/02-vault/03-domain/workflows.md` (4,806 Bytes) — Bổ sung luồng quy trình nghiệp vụ Mermaid chi tiết trong Vault.
6. `docs/03-product/epics.md` (1,086 Bytes) — Bổ sung định nghĩa 7 Epics sản phẩm (E-01..E-07).
7. `docs/03-product/prototype-brief.md` (1,408 Bytes) — Bổ sung yêu cầu thiết kế màn hình và tương tác prototype.
8. `docs/03-product/taiga-backlog.md` (14,563 Bytes) — Khôi phục bản backlog chi tiết 42 tasks và phân công ban đầu.
9. `docs/03-product/usability-test-script.md` (1,773 Bytes) — Bổ sung kịch bản kiểm thử trải nghiệm người dùng (T-01..T-06).
10. `docs/03-product/usability-findings.md` (633 Bytes) — Bổ sung khung ghi nhận kết quả kiểm thử usability.
11. `docs/03-product/user-flow.md` (1,408 Bytes) — Bổ sung thuyết minh luồng người dùng kèm Mermaid.
12. `docs/IMPORT_INVENTORY.md` — Kiểm kê 37 artifacts từ folder import.
13. `docs/IMPORT_RECONCILIATION_REPORT.md` — Báo cáo đối chiếu và phân loại chi tiết.
14. `docs/AI_USAGE_LOG_RECONCILIATION.md` — Báo cáo đối chiếu AI Usage Log.
15. `docs/AI_USAGE_TRACEABILITY.md` — Ma trận truy xuất nguồn gốc hai chiều xuyên suốt.
16. `docs/IMPORT_INTEGRATION_CHANGELOG.md` — Nhật ký thay đổi tích hợp.

### B. Files Updated (Cập nhật có kiểm soát)
1. `docs/logs/ai-usage-log.md` — Bổ sung khối Callout Notice dẫn chiếu tới `docs/02-vault/AI_USAGE_LOG.md` (38 entries Early Phase) và giải quyết trùng mã ID; giữ nguyên vẹn 100% 53 entries của Final Delivery Phase.
2. `docs/03-product/taiga-backlog.md` — Bổ sung Callout Warning về `ALLOCATION CONFLICT — HUMAN DECISION REQUIRED`.

### C. Files Archived (Lưu trữ lịch sử vào `docs/archive/early-phase/`)
Toàn bộ 29 tài liệu markdown của folder import đã được lưu trữ an toàn trong `docs/archive/early-phase/` để bảo đảm truy nguyên lịch sử vĩnh viễn:
- `docs/archive/early-phase/01-discovery/1.project-charter.md`
- `docs/archive/early-phase/01-discovery/2.user-research.md` (Báo cáo phỏng vấn 11 mục, 8 evidence gốc)
- `docs/archive/early-phase/01-discovery/3.personas-and-jtbd.md`
- `docs/archive/early-phase/01-discovery/4.glossary.md`
- `docs/archive/early-phase/01-discovery/5.requirements.md`
- `docs/archive/early-phase/01-discovery/6.business-rules.md`
- `docs/archive/early-phase/01-discovery/7.MVP-Scope.md`
- `docs/archive/early-phase/02-vault/...` (00-index, AI_USAGE_LOG, source-priority, benchmark, prompt, sources, requirements, domain, decisions, meetings)
- `docs/archive/early-phase/03-product/...` (epics, PRD, prototype-brief, taiga-backlog, usability, user-flow, user-stories)

### D. Files Intentionally Not Imported (Chủ động bỏ qua để bảo vệ mã nguồn & tài liệu hiện hành)
1. `README.md` (779B) — Không ghi đè lên `README.md` hiện tại (996B).
2. `docs/00-project-index.md` (2,022B) — Không ghi đè lên index hiện tại (3,759B) đã tích hợp kiến trúc mới.
3. `docs/03-product/PRD.md` (1,743B) — Không ghi đè lên PRD hiện tại (6,648B) chi tiết hơn.
4. `docs/04-design/README.md`, `docs/05-technical/README.md`, `docs/06-testing/README.md`, `docs/07-release/README.md`, `docs/logs/README.md` — Không đè các placeholder rỗng lên các tài liệu kỹ thuật, test spec và release notes thực tế đã có trong project.
5. `src/.gitkeep`, `tests/.gitkeep` — Không đưa scaffold rỗng vào repository đã có source code thực (`backend/`, `frontend/`).

---

## 2. AI USAGE LOG RECOVERY

### A. Entries phục hồi nguyên bản từ folder mới (Direct Evidence: 38 entries)
Toàn bộ 38 entries trong `_IMPORT_EARLY_PHASE/group-01/docs/02-vault/AI_USAGE_LOG.md` đã được phục hồi nguyên bản 100% tại `docs/02-vault/AI_USAGE_LOG.md`:
- `AI-001` đến `AI-004`: Phân tích ban đầu, User Research, Requirement Inventory (dùng chung cho cả 2 phase).
- `AI-005` đến `AI-012`: Rủi ro Persona/JTBD, MVP Scope, README, Index và chuẩn hóa tên file Discovery.
- `AI-013` đến `AI-019`: Vault Governance, Index, Workflows, Decision Log, Meetings và Vault QA Benchmark.
- `AI-020` đến `AI-025`: PRD, Epics, Prototype Brief, User Flow, User Stories và Taiga Backlog.
- `AI-026` đến `AI-028`: Usability Test Script, Usability Findings và Prototype README.
- `AI-029` đến `AI-035`: Thiết lập cấu trúc thư mục cho Design, Tech, Test, Release, Logs và scaffold.
- `AI-036` đến `AI-038`: Vault QA Benchmark 22 câu hỏi chuẩn, Budget Check Q&A và System Prompt.
- Kèm theo: Toàn bộ Section 3 ghi nhận lịch sử phát hiện và sửa lỗi của AI (AI Errors / Corrections).

### B. Entries trùng lặp (Deduplicated Entries: 4 entries)
- `AI-001` (Project Charter), `AI-002` (User Research), `AI-003` (Chuẩn hóa Research), `AI-004` (Requirement Inventory): Nội dung giữa bản Import và bản Current hoàn toàn trùng khớp 100%. Được giữ nguyên vẹn ở cả hai tài liệu mà không tạo thêm bản sao thừa.

### C. Entries mang tính hồi cứu (Retrospective Entries)
- File `docs/02-vault/AI Usage Log.md` cũ (8KB) với 10 mục `A-01` đến `A-10` được phân loại là **RETROSPECTIVE** (bản tóm tắt lại trước đây) và được thay thế chính thức bằng bản gốc đầy đủ `docs/02-vault/AI_USAGE_LOG.md` (24.7KB).

### D. Entries còn thiếu bằng chứng (Missing Evidence)
- **TASK-004 (Supabase JWT Auth):** Chưa có prompt sinh mã xác thực JWT thật.
- **TASK-005 (RBAC Middleware):** Chưa có prompt sinh middleware phân quyền HTTP.
- **TASK-006 (Frontend React Router):** Chưa có prompt sinh các component phân trang.
- **TASK-009 (Real LLM Integration):** Chưa có prompt tích hợp API Gemini/OpenAI thật.
- **TASK-013 (E2E Test Execution):** Chưa có prompt chạy kiểm thử Playwright thực tế trên browser.
*Tất cả các khoảng trống trên đều được ghi nhận rõ ràng là `MISSING EVIDENCE`, tuyệt đối không tự bịa đặt.*

---

## 3. Conflicts Found & Unresolved Issues

### Conflict 1: Phân công Primary Owner giữa `taiga-backlog.md` và `IMPLEMENTATION_PLAN.md`
- `taiga-backlog.md`: Giang (US-01), Dung (US-02, US-08, US-09, GOV-01), Lam (US-03, US-07), Dương (US-04, US-05, US-06), Hà (US-10, GOV-02).
- `docs/IMPLEMENTATION_PLAN.md`: Trước đây dùng mô hình 2 tầng cũ (Dương US-01, Lam US-03, Dung US-05, Giang US-07, Hà US-09).
- **Quyết định từ con người (HUMAN DECIDED):** Đổi dự án cũ theo phiên bản mới `group-01` (`taiga-backlog.md`), tuyệt đối không gộp User Story của mỗi người. Đã cập nhật Section 2 của `docs/IMPLEMENTATION_PLAN.md` đồng bộ 100%.
- **Trạng thái:** `RESOLVED BY HUMAN DECISION — CLOSED`.

### Conflict 2: Xung đột dải mã ID giữa Early Phase Log và Final Delivery Log
- Cả hai tập log đều sử dụng dải mã từ `AI-005` đến `AI-038` cho hai tập tác vụ hoàn toàn khác nhau.
- **Trạng thái:** Đã phân định ranh giới rõ ràng: Early Phase Log nằm tại `docs/02-vault/AI_USAGE_LOG.md`; Final Delivery Log nằm tại `docs/logs/ai-usage-log.md`. Không ghi đè làm mất mát lịch sử.

---

## 4. Verification Check

- **Source Code Integrity:** 100% mã nguồn backend (`backend/app/`, `backend/prisma/`) và frontend (`frontend/src/`) không bị can thiệp hay thay đổi.
- **Database Schema:** Không sửa `schema.prisma`, không chạy `prisma db push`, không can thiệp database.
- **Test Integrity:** Không sửa logic test hay xóa test cases.

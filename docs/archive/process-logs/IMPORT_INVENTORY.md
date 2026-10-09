# IMPORT INVENTORY — EARLY PHASE ARTIFACTS

**Thư mục nguồn:** `_IMPORT_EARLY_PHASE/group-01`  
**Ngày thực hiện kiểm kê:** 2026-09-23  
**Nhánh Git:** `final-delivery`  
**Người thực hiện:** Antigravity AI Pair Programmer & Group 01  

---

## 1. Tổng quan kiểm kê

Thư mục `_IMPORT_EARLY_PHASE/group-01` chứa snapshot của giai đoạn đầu dự án (Early Phase — Discovery, Vault, sơ khai Product). Tổng cộng có **37 files** được kiểm kê chi tiết dưới đây:

- **DOCUMENT / CHARTER / GLOSSARY:** 9 files
- **REQUIREMENT / BUSINESS RULES / SCOPE:** 5 files
- **USER STORY / PRODUCT / BACKLOG:** 6 files
- **AI USAGE LOG:** 1 file
- **EVIDENCE / USER RESEARCH:** 2 files
- **TEST / QA BENCHMARK & SCRIPT:** 4 files
- **DESIGN / PROTOTYPE BRIEF:** 2 files
- **CONFIG / PROMPT / SYSTEM:** 2 files
- **SCAFFOLD / PLACEHOLDER:** 6 files

---

## 2. Bảng kiểm kê chi tiết 37 Artifacts

| STT | File Path (trong folder import) | Loại Artifact | Mục đích | Phase | Ngày sửa đổi | Tồn tại trong Project hiện tại? | Mức độ liên quan | Đề xuất xử lý |
|:---:|---|---|---|---|:---:|:---:|:---:|---|
| 1 | `README.md` | DOCUMENT | Giới thiệu điểm vào dự án ban đầu | Early Phase | 2026-09-15 | Có (`README.md` 996B) | Low | **SHOULD_NOT_IMPORT** (Giữ bản hiện tại đầy đủ hơn) |
| 2 | `docs/00-project-index.md` | DOCUMENT | Chỉ mục tài liệu ban đầu | Early Phase | 2026-09-15 | Có (`docs/00-project-index.md` 3759B) | Medium | **SHOULD_NOT_IMPORT** (Bản hiện tại đã cập nhật kiến trúc mới) |
| 3 | `docs/01-discovery/1.project-charter.md` | DOCUMENT / CHARTER | Project Charter gốc có metrics khả thi | Discovery | 2026-09-15 | Có (`docs/01-discovery/project-charter.md` 5904B) | High | **SAFE_TO_MERGE** (Lưu vào archive làm historical charter) |
| 4 | `docs/01-discovery/2.user-research.md` | EVIDENCE / USER RESEARCH | Báo cáo nghiên cứu người dùng 11 mục, 8 evidence E01-E08 | Discovery | 2026-09-09 | Có (`docs/01-discovery/user-research.md` 6358B) | Critical | **UNIQUE_HISTORICAL_ARTIFACT** / **SAFE_TO_MERGE** (Evidence gốc) |
| 5 | `docs/01-discovery/3.personas-and-jtbd.md` | REQUIREMENT / PERSONA | Đặc tả 5 Personas và Jobs-to-be-Done | Discovery | 2026-09-15 | Chưa có | Critical | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/01-discovery/`) |
| 6 | `docs/01-discovery/4.glossary.md` | DOCUMENT | Thuật ngữ nghiệp vụ chuẩn hóa | Discovery | 2026-09-09 | Có (`docs/01-discovery/glossary.md` 3450B) | Medium | **OLDER_VERSION** / **ARCHIVE** |
| 7 | `docs/01-discovery/5.requirements.md` | REQUIREMENT | Yêu cầu nghiệp vụ FR-01..18, NFR-01..03, BR-01..11 | Discovery | 2026-09-15 | Có (`docs/01-discovery/requirements.md` 11772B) | High | **OLDER_VERSION** / **ARCHIVE** |
| 8 | `docs/01-discovery/6.business-rules.md` | REQUIREMENT | Quy tắc nghiệp vụ chi tiết | Discovery | 2026-09-15 | Có (trong `requirements.md` và `DECISION_LOG.md`) | High | **OLDER_VERSION** / **ARCHIVE** |
| 9 | `docs/01-discovery/7.MVP-Scope.md` | REQUIREMENT / SCOPE | Đặc tả phạm vi MVP, bảng Must/Should/Could/Out of Scope | Discovery | 2026-09-15 | Chưa có file riêng | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/01-discovery/`) |
| 10 | `docs/02-vault/00-index.md` | DOCUMENT | Vault Index phân cấp source priority | Vault | 2026-09-15 | Có (`docs/02-vault/00-index.md` 1569B) | Medium | **OLDER_VERSION** / **ARCHIVE** |
| 11 | `docs/02-vault/AI_USAGE_LOG.md` | AI USAGE LOG | Nhật ký sử dụng AI gốc 38 entries (AI-001..AI-038) + error history | Vault | 2026-09-15 | Có dạng khác (`docs/02-vault/AI Usage Log.md` 8624B) | Critical | **UNIQUE_HISTORICAL_ARTIFACT** / **SAFE_TO_MERGE** (Bảo toàn 100% bản gốc) |
| 12 | `docs/02-vault/source-priority.md` | CONFIG / GOVERNANCE | Quy định 6 cấp độ ưu tiên nguồn tin | Vault | 2026-09-09 | Có (`docs/02-vault/source-priority.md` 1397B) | Medium | **DUPLICATE** / Giữ bản current |
| 13 | `docs/02-vault/vault-qa-benchmark.md` | TEST / QA | Bộ câu hỏi benchmark kiểm tra độ chính xác của Vault | Vault | 2026-09-15 | Có (`docs/02-vault/vault-qa-benchmark.md` 20124B) | Medium | **OLDER_VERSION** (Bản current đã có kết quả chạy thực tế) |
| 14 | `docs/02-vault/vault-qa-prompt.md` | CONFIG / PROMPT | System Prompt chuẩn tra cứu tài liệu Vault | Vault | 2026-09-15 | Chưa có | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/02-vault/`) |
| 15 | `docs/02-vault/01-sources/user-research.md` | EVIDENCE | Bản sao lưu User Research trong Vault | Vault | 2026-09-09 | Trùng với file discovery số 4 | Medium | **DUPLICATE** (Đã có ở discovery) |
| 16 | `docs/02-vault/02-requirements/requirements.md` | REQUIREMENT | Bản sao lưu Requirements trong Vault | Vault | 2026-09-15 | Trùng với file discovery số 7 | Medium | **DUPLICATE** (Đã có ở discovery) |
| 17 | `docs/02-vault/03-domain/business_rules.md` | REQUIREMENT | Bản sao lưu Business Rules trong Vault | Vault | 2026-09-15 | Trùng với file discovery số 8 | Medium | **DUPLICATE** (Đã có ở discovery) |
| 18 | `docs/02-vault/03-domain/glossary.md` | DOCUMENT | Bản sao lưu Glossary trong Vault | Vault | 2026-09-09 | Trùng với file discovery số 6 | Medium | **DUPLICATE** (Đã có ở discovery) |
| 19 | `docs/02-vault/03-domain/workflows.md` | REQUIREMENT / WORKFLOW | Luồng nghiệp vụ dạng Mermaid & quy trình | Vault | 2026-09-15 | Chưa có file riêng trong vault | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/02-vault/03-domain/`) |
| 20 | `docs/02-vault/08-decisions/decision-log.md` | DOCUMENT / DECISION | Nhật ký quyết định giai đoạn đầu DEC-001..DEC-007 | Vault | 2026-09-15 | Có (`docs/DECISION_LOG.md` 27892B) | High | **OLDER_VERSION** / **ARCHIVE** |
| 21 | `docs/02-vault/09-meetings/README.md` | PLACEHOLDER | Thư mục ghi chú cuộc họp | Vault | 2026-09-15 | Chưa có | Low | **SHOULD_NOT_IMPORT** (Placeholder rỗng) |
| 22 | `docs/03-product/epics.md` | BACKLOG / PRODUCT | Định nghĩa 7 Epics (E-01 đến E-07) và mục tiêu | Product | 2026-09-15 | Chưa có file riêng | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/03-product/`) |
| 23 | `docs/03-product/PRD.md` | PRODUCT / DOCUMENT | Bản thảo PRD sơ khởi | Product | 2026-09-15 | Có (`docs/03-product/PRD.md` 6648B) | Medium | **OLDER_VERSION** (Bản current chi tiết hơn nhiều) |
| 24 | `docs/03-product/prototype-brief.md` | DESIGN / PRODUCT | Yêu cầu thiết kế màn hình và tương tác prototype | Product | 2026-09-15 | Chưa có | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/03-product/`) |
| 25 | `docs/03-product/taiga-backlog.md` | BACKLOG / USER STORY | Backlog chi tiết 7 Epics, 10 US, 42 Tasks, Owner/Assignee | Product | 2026-09-17 | Chưa có | Critical | **MISSING_IN_CURRENT** / **CONFLICT** / **SAFE_TO_MERGE** (Lưu giữ và đối chiếu phân công) |
| 26 | `docs/03-product/usability-findings.md` | EVIDENCE / TEST | Khung ghi nhận kết quả kiểm thử khả năng sử dụng | Product | 2026-09-15 | Chưa có | Medium | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** |
| 27 | `docs/03-product/usability-test-script.md` | TEST | Kịch bản kiểm thử người dùng cho 6 luồng chính | Product | 2026-09-15 | Chưa có | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** (Khôi phục vào `docs/03-product/`) |
| 28 | `docs/03-product/user-flow.md` | PRODUCT / DESIGN | Diễn giải luồng người dùng và sơ đồ Mermaid | Product | 2026-09-15 | Có dạng khác (`docs/03-product/user-flow.mmd` 1165B) | High | **MISSING_IN_CURRENT** / **SAFE_TO_MERGE** |
| 29 | `docs/03-product/user-stories.md` | USER STORY | Danh sách User Stories ban đầu US-01..US-10 | Product | 2026-09-15 | Có (`docs/03-product/user-story.md` 13477B) | High | **OLDER_VERSION** / **CONFLICT** (Khác về phân công và format) |
| 30 | `docs/03-product/prototype-URL/README.md` | PLACEHOLDER | Thư mục URL prototype | Product | 2026-09-15 | Chưa có | Low | **SHOULD_NOT_IMPORT** (Placeholder rỗng) |
| 31 | `docs/04-design/README.md` | PLACEHOLDER | Giữ chỗ tài liệu thiết kế | Design | 2026-09-15 | Đã có tài liệu thật (`DESIGN.md`, `prototype.md`) | Low | **SHOULD_NOT_IMPORT** (Không đè lên tài liệu thật) |
| 32 | `docs/05-technical/README.md` | PLACEHOLDER | Giữ chỗ tài liệu kỹ thuật | Technical | 2026-09-15 | Đã có tài liệu thật (ADR, API, data-model) | Low | **SHOULD_NOT_IMPORT** (Không đè lên tài liệu thật) |
| 33 | `docs/06-testing/README.md` | PLACEHOLDER | Giữ chỗ tài liệu kiểm thử | Testing | 2026-09-15 | Đã có tài liệu thật (test matrix, spec) | Low | **SHOULD_NOT_IMPORT** (Không đè lên tài liệu thật) |
| 34 | `docs/07-release/README.md` | PLACEHOLDER | Giữ chỗ tài liệu phát hành | Release | 2026-09-15 | Đã có tài liệu thật (release-notes, runbook) | Low | **SHOULD_NOT_IMPORT** (Không đè lên tài liệu thật) |
| 35 | `docs/logs/README.md` | PLACEHOLDER | Giữ chỗ thư mục logs | Logs | 2026-09-15 | Đã có log thật (`ai-usage-log.md`) | Low | **SHOULD_NOT_IMPORT** (Không đè lên tài liệu thật) |
| 36 | `src/.gitkeep` | SCAFFOLD | Giữ chỗ thư mục mã nguồn | Scaffold | 2026-09-15 | Đã có mã nguồn thật (`backend/`, `frontend/`) | None | **SHOULD_NOT_IMPORT** |
| 37 | `tests/.gitkeep` | SCAFFOLD | Giữ chỗ thư mục kiểm thử | Scaffold | 2026-09-15 | Đã có bộ test thật trong `backend/tests/` | None | **SHOULD_NOT_IMPORT** |

# FINAL DELIVERY BASELINE AUDIT
## AI Procurement & Purchase Approval System
### MIS3032_1 — Group 01 — Bài cuối (Full Delivery)

**Ngày kiểm tra:** 2026-09-16  
**Người kiểm tra:** Senior Software Engineer + QA Engineer + Technical Lead (AI Audit)  
**Phương pháp:** Đọc toàn bộ source code, documentation, test files — KHÔNG sửa code  
**Trạng thái:** BASELINE ESTABLISHED — Chờ human decision trước khi thực hiện bước tiếp theo

---

## 1. EXECUTIVE SUMMARY

### Tình trạng tổng thể: ⚠️ PARTIAL — NHIỀU GAP NGHIÊM TRỌNG

Project đã có nền tảng documentation và architecture tốt, nhưng **implementation thực tế chỉ là MVP in-memory prototype**, không phải production-ready system. Có khoảng cách rất lớn giữa những gì được mô tả trong documentation và những gì thực sự được implement trong code.

| Hạng mục | Tình trạng | Ghi chú |
|---|---|---|
| Requirements / Business Rules | ✅ GOOD | Đầy đủ, có ID, có trace |
| User Stories / AC | ✅ GOOD | 11 US, đầy đủ AC |
| Backlog / Tasks | ✅ GOOD | Có task ID |
| Architecture docs | ⚠️ PARTIAL | ADR có nhưng thiếu architecture.md chính |
| API Contract | ⚠️ PARTIAL | Tóm tắt, không đầy đủ |
| Data Model | ✅ GOOD | Prisma schema đầy đủ |
| Frontend | ⚠️ PARTIAL | Single-file SPA, thiếu nhiều tính năng |
| Backend | 🔴 CRITICAL | In-memory mock, KHÔNG dùng Prisma/PostgreSQL |
| Authentication | 🔴 BROKEN | Mock JWT, không verify token |
| Authorization / RBAC | 🔴 MISSING | Không có middleware RBAC |
| Unit Tests | ⚠️ PARTIAL | 4 tests BR, có pass nhưng có bug isolation |
| Integration Tests | 🔴 MISSING | Không có |
| E2E Tests | 🔴 NOT RUNNABLE | File spec tồn tại nhưng không runnable |
| AI Usage Log | ⚠️ PARTIAL | Có vault log (A-01..A-10), log chính rỗng |
| Deployment | 🔴 BROKEN | Runbook sai path, DB không kết nối với backend |
| Git / Pull Request | 🔴 MISSING | Không có git repo |
| Traceability Matrix | ⚠️ PARTIAL | Chỉ có cho US-09, nhiều phantom references |

**Ước tính completion:** ~35–45% so với yêu cầu Bài cuối

---

## 2. CURRENT ARCHITECTURE

### 2.1 Kiến trúc thực tế (source code evidence)

```
Frontend (React + Vite + TypeScript)
  └── src/App.tsx (1 file duy nhất, ~418 lines)
        └── Gọi API: http://localhost:8000/api/*

Backend (FastAPI + Python)
  ├── app/main.py               — FastAPI app entry point
  ├── app/config.py             — Settings (pydantic-settings)
  ├── app/routers/
  │   ├── auth.py               — Mock login, hardcoded users
  │   ├── pr.py                 — Create/List/Approve/Close PR
  │   ├── quotations.py         — AI Compare (mock)
  │   ├── po.py                 — Create/List PO
  │   ├── receiving.py          — Record receiving
  │   ├── budget.py             — Get budget
  │   └── assistant.py          — AI standardize PR
  ├── app/services/
  │   ├── procurement_service.py — MockDatabase class (IN-MEMORY)
  │   └── ai_service.py          — Rule-based parser (NOT LLM)
  └── prisma/schema.prisma        — Schema định nghĩa nhưng KHÔNG ĐƯỢC SỬ DỤNG

Database
  └── compose.yaml: PostgreSQL 18 (Docker)
      WARN: Backend KHÔNG kết nối PostgreSQL — dùng in-memory dict
      WARN: seed.py chỉ seed vào MockDatabase, không ghi DB thật
```

### 2.2 Kiến trúc theo documentation (vs thực tế)

| Component | Doc nói | Code thực |
|---|---|---|
| Database | PostgreSQL + Prisma ORM | In-memory Python dict |
| Auth | JWT real token | Mock string `"mock-jwt-token-for-..."` |
| AI | LLM / extraction | Regex rule-based parser |
| Frontend | Modular React components | Single `App.tsx` file |
| PO Service | `backend/app/services/po_service.py` | FILE KHÔNG TỒN TẠI |
| PR Service | `backend/app/services/pr_service.py` | FILE KHÔNG TỒN TẠI |

---

## 3. IMPLEMENTED FEATURES

### Thực sự implemented (confirmed from source code)

| Feature | File | Ghi chú |
|---|---|---|
| Mock Login | `auth.py` | 5 users hardcoded, password `password123` |
| Create PR + Budget Check | `pr.py` + `procurement_service.py` | BR-01 implemented (in-memory) |
| List PR | `pr.py` | `GET /api/pr` |
| Approve PR (2-level) | `pr.py` + `procurement_service.py` | BR-02 partially implemented |
| AI Standardize PR | `assistant.py` + `ai_service.py` | Regex parser, NOT real AI/LLM |
| AI Compare Quotations | `quotations.py` + `ai_service.py` | Mock suppliers, hardcoded data |
| Anomaly Detection | `ai_service.py` | Hardcoded 20% threshold vs historical_avg=25M |
| Create PO (price lock) | `po.py` + `procurement_service.py` | BR-03 in-memory |
| Record Receiving | `receiving.py` + `procurement_service.py` | BR-04 quantity limit |
| Close PR + Budget settle | `pr.py` + `procurement_service.py` | tempReserved to spent |
| Budget view | `budget.py` | Only 2 departments: DEPT-IT, DEPT-HR |
| Health check | `main.py` | Returns hardcoded FALSE "PostgreSQL Connected" |
| Frontend role selector | `App.tsx` | UI-only, không dùng JWT |
| Frontend PR create flow | `App.tsx` | Backend call or fallback mock |
| Frontend PR list | `App.tsx` | Display status, basic action buttons |
| Frontend Quotation compare | `App.tsx` | Hiển thị 3 quotes từ API |
| Frontend PO create | `App.tsx` | Gọi POST /api/po |
| Frontend Close PR | `App.tsx` | Gọi POST /api/pr/:id/close |

---

## 4. MISSING FEATURES

### 4.1 Backend — MISSING hoàn toàn

| Feature | Requirement | Tình trạng |
|---|---|---|
| Reject PR | REQ-FR-06 / US-03 AC3 | MISSING |
| Request Revision flow | REQ-FR-06 / US-03 AC3 | MISSING — no `REVISION_REQUESTED` status |
| Supplier management (CRUD) | REQ-FR-10 / US-05 | MISSING — no supplier endpoint |
| Quotation file upload | REQ-FR-10 / US-05 | MISSING — only accepts filename string |
| Quotation standardization (per-item) | REQ-FR-11 | MISSING |
| Get PR by ID | API Contract | MISSING — only GET all |
| Filter PR by role / department | API Contract | MISSING |
| POItem table (PO line items) | data-model.md | MISSING — schema has PRItem but PO has no POItem |
| Partial Receiving tracking | US-10 AC2 / ASM-06 | MISSING — no `PARTIALLY_RECEIVED` status update |
| Close PR prerequisite check | US-11 AC2 / REQ-BR-11 | MISSING — `close_pr()` does not check receiving |
| Audit/approval log API | REQ-NFR-03 | MISSING — Approval model in schema but no endpoint |
| Database persistence | Core | MISSING — all in-memory |
| Real JWT generation/validation | REQ-NFR-02 | MISSING |
| RBAC middleware | REQ-NFR-02 | MISSING — all endpoints require no auth |
| Budget check khi Finance approve | US-04 AC1 | MISSING |

### 4.2 Frontend — MISSING

| Feature | Ghi chú |
|---|---|
| Login page | Không có — chỉ có role selector dropdown |
| Route-based navigation | Không có React Router |
| Reject PR button | Không có UI |
| Request Revision button | Không có UI |
| Supplier management UI | Không có |
| Quotation file upload UI | Không có real file upload |
| PR detail page | Không có (chỉ list) |
| PO detail page | Không có |
| Receiving detail / history | Không có |
| Budget warning display | Không có warning alert khi vượt |
| RBAC-based UI protection | Không có (role selector là UI-only trust) |
| 403 Forbidden page | Không có |

### 4.3 Playwright E2E Tests — NOT RUNNABLE

Playwright test file (`playwright-e2e-us09.spec.ts`) tồn tại trong `docs/06-testing/` (sai location), và test đang expect:

- Route `/login` → Không tồn tại trong frontend
- Route `/pr` → Không tồn tại (frontend là single page, không có routing)
- CSS selectors như `.supplier-card`, `table.comparison-table` → Không tồn tại trong `App.tsx`
- `div.modal`, `div.confirm-dialog` → Không có modal trong frontend
- `span.status-badge` → Code dùng inline span không có class này

> **Kết luận: 0/3 E2E test cases có thể chạy được trong trạng thái hiện tại.**

---

## 5. BROKEN FEATURES & BUGS

### BUG-001 — CRITICAL: PO có thể tạo khi PR chưa APPROVED

- **Severity:** CRITICAL
- **Category:** Business Rule Violation
- **Evidence:** `procurement_service.py` L101–124 — `create_po()` chỉ check `pr` tồn tại, không check `pr["status"] == "APPROVED"`
- **Affected Requirement:** REQ-BR-10 / US-09 AC2
- **Affected File:** `backend/app/services/procurement_service.py`
- **Current state:** `if not pr: raise ValueError` — chỉ check existence
- **Expected state:** Phải check `pr["status"] in ["APPROVED", "COLLECTING_QUOTATIONS"]` trước khi tạo PO
- **QA Finding:** Đã ghi nhận tại `docs/qa/QA_FINDINGS.md` — QF-001 — Status: OPEN (chưa sửa)
- **Recommended next step:** Add status check before PO creation

### BUG-002 — CRITICAL: Authentication không thực sự verify token

- **Severity:** CRITICAL
- **Category:** Security / Auth
- **Evidence:** `auth.py` trả về string `"mock-jwt-token-for-{email}"`. Các endpoints khác không verify token. `pyproject.toml` có `pyjwt>=2.9.0` nhưng không dùng.
- **Affected Requirement:** REQ-NFR-02
- **Affected File:** `backend/app/routers/auth.py` và tất cả routers
- **Current state:** Mock string token, no verification middleware
- **Expected state:** Real JWT với secret key, middleware verification
- **Recommended next step:** Implement JWT generation và dependency injection cho auth

### BUG-003 — CRITICAL: Health check trả về sai trạng thái (False Positive)

- **Severity:** CRITICAL
- **Category:** False Positive / Documentation Drift
- **Evidence:** `main.py` L43 hardcode `"database": "PostgreSQL Connected (Prisma)"` nhưng backend KHÔNG kết nối PostgreSQL
- **Affected File:** `backend/app/main.py`
- **Current state:** Always returns "ok" regardless of actual DB state
- **Expected state:** Thực sự test DB connection
- **Recommended next step:** Either connect real DB or change message to reflect actual state

### BUG-004 — HIGH: Frontend TypeScript syntax error

- **Severity:** HIGH
- **Category:** Compile/Build Issue
- **Evidence:** `App.tsx` L256: `fontWeight 700` (thiếu dấu `:`) — Invalid TypeScript/JSX. Tương tự L260.
- **Affected File:** `frontend/src/App.tsx`
- **Current state:** TypeScript syntax error — sẽ fail khi `npm run build`
- **Expected state:** `fontWeight: 700`
- **Recommended next step:** Add colon after `fontWeight` on both lines

### BUG-005 — HIGH: Frontend/Backend response mismatch (standardize PR)

- **Severity:** HIGH
- **Category:** Frontend/Backend Mismatch
- **Evidence:** `App.tsx` L75: `setStandardized(data.standardized)` — nhưng `ai_service.py` trả về `{ title, items, total_estimated_value, ... }` — không có key `standardized`
- **Affected Files:** `frontend/src/App.tsx`, `backend/app/services/ai_service.py`
- **Current state:** `standardized` sẽ luôn là `undefined` → fallback mock được dùng thay thế (masked bug)
- **Expected state:** `setStandardized(data)` hoặc backend wrap trong `{ standardized: ... }`
- **Recommended next step:** Fix `App.tsx` L75 to use `data` directly

### BUG-006 — HIGH: Close PR không check Receiving completion

- **Severity:** HIGH
- **Category:** Business Rule Violation
- **Evidence:** `procurement_service.py` L154–168: `close_pr()` không verify receiving đã đủ so với PO quantity
- **Affected Requirement:** REQ-BR-11 / US-11 AC2
- **Affected File:** `backend/app/services/procurement_service.py`
- **Current state:** Finance có thể Close PR bất kỳ lúc nào sau khi PO được tạo
- **Expected state:** Phải verify receiving complete trước khi Close
- **Recommended next step:** Add receiving completion check in `close_pr()`

### BUG-007 — HIGH: Runbook có wrong path

- **Severity:** HIGH
- **Category:** Documentation Drift / Deployment
- **Evidence:** `runbook.md` L12–29 dùng path `d:\THUDDN\group-01-project` — sai (project nằm ở `d:\LTUD\group-01-project-main`). `README.md` L34 cũng link sai path.
- **Affected Files:** `docs/07-release/runbook.md`, `README.md`
- **Recommended next step:** Update paths to correct location

### BUG-008 — MEDIUM: Test isolation issue (shared in-memory state)

- **Severity:** MEDIUM
- **Category:** Broken Test / Test Isolation
- **Evidence:** Tests dùng shared `db` singleton. `test_req_br_02` tạo PR 60M từ `DEPT-IT` nhưng nếu `test_req_br_01` đã lock budget, test có thể fail theo thứ tự chạy.
- **Affected File:** `backend/tests/test_business_rules.py`
- **Recommended next step:** Add pytest fixture to reset `db` state between tests

### BUG-009 — MEDIUM: test_full_7step_workflow potential logic gap

- **Severity:** MEDIUM
- **Category:** Test Logic
- **Evidence:** Step 4 gửi `best_quotation = comparisons[0]` trực tiếp vào PO creation. Keys phải match giữa `ai_service.compare_quotations()` output và `create_po()` expected input. Cần verify manually.
- **Affected File:** `backend/tests/test_all_endpoints.py`

### BUG-010 — LOW: Playwright E2E file đặt sai thư mục

- **Severity:** LOW
- **Category:** Documentation / Deployment
- **Evidence:** `playwright-e2e-us09.spec.ts` nằm trong `docs/06-testing/` thay vì `frontend/`. Không có `playwright.config.ts` trong project.
- **Recommended next step:** Move to `frontend/` and create `playwright.config.ts`

---

## 6. CRITICAL BUGS SUMMARY

| ID | Severity | Mô tả | Status |
|---|---|---|---|
| BUG-001 | CRITICAL | PO tạo được dù PR chưa APPROVED | OPEN (QF-001) |
| BUG-002 | CRITICAL | Auth không real JWT, không verify | OPEN |
| BUG-003 | CRITICAL | Health check báo false positive | OPEN |
| BUG-004 | HIGH | TypeScript syntax error trong App.tsx | OPEN |
| BUG-005 | HIGH | Frontend/Backend response mismatch (standardize) | OPEN |
| BUG-006 | HIGH | Close PR không check receiving completion | OPEN |
| BUG-007 | HIGH | Runbook có wrong path | OPEN |
| BUG-008 | MEDIUM | Test isolation issue (shared in-memory state) | OPEN |
| BUG-009 | MEDIUM | E2E test logic gap | OPEN |
| BUG-010 | LOW | Playwright spec ở sai location | OPEN |

---

## 7. SECURITY GAPS

| ID | Severity | Category | Description | Affected File |
|---|---|---|---|---|
| SEC-01 | CRITICAL | Authentication bypass | Tất cả API endpoints không require Authorization header. Ai cũng có thể gọi POST /api/pr, POST /api/po mà không cần login | Tất cả routers |
| SEC-02 | CRITICAL | Privilege escalation | POST /api/pr/:id/approve nhận `approverRole` từ request body — client tự khai role, không verify | `pr.py` L19–22 |
| SEC-03 | HIGH | Hardcoded credentials | `auth.py` L21: password hardcoded. `config.py` L6: JWT_SECRET hardcoded | `auth.py`, `config.py` |
| SEC-04 | HIGH | CORS wildcard | `main.py` L14: `allow_origins=["*"]` | `main.py` |
| SEC-05 | HIGH | No input sanitization | API nhận raw string không có sanitization | Multiple |
| SEC-06 | MEDIUM | No rate limiting | Không có rate limiting trên bất kỳ endpoint nào | All |

---

## 8. TESTING GAPS

### 8.1 Test Coverage thực tế

| Test Type | Planned | Actually Exists | Actually Runnable |
|---|---|---|---|
| Unit (pytest) | TC-01 đến TC-10 | 8 test functions (4 BR + 4 endpoint) | Partial (isolation risk) |
| Integration | TC-06, TC-07 (DB+API) | 0 | No |
| E2E Playwright | TC-11 | 1 spec file (3 scenarios) | No — cannot run |
| Performance | None planned | 0 | No |

### 8.2 Business Rules không có test

| Business Rule | Test tương ứng | Status |
|---|---|---|
| REQ-BR-10: PO chỉ tạo khi PR APPROVED | Không có (đây là bug đã biết) | MISSING |
| REQ-BR-11: Close chỉ sau Receiving hoàn thành | Không có | MISSING |
| REQ-BR-12: PO price khớp Quotation (API-level) | Chỉ có service-level test | PARTIAL |
| REQ-BR-03: Manager chỉ duyệt PR thuộc phạm vi mình | Không có | MISSING |
| REQ-NFR-02: RBAC enforcement | Không có (không có RBAC) | MISSING |

### 8.3 User Stories chưa có test coverage đầy đủ

| User Story | Test Coverage |
|---|---|
| US-01 AC1 (validation before submit) | MISSING |
| US-01 AC2 (AI suggestion for missing fields) | MISSING |
| US-02 (status tracking) | MISSING |
| US-03 AC3 (Reject / Request Revision) | MISSING |
| US-04 (Budget check by Finance) | MISSING |
| US-05 (Supplier management) | MISSING |
| US-06 (Quotation comparison UI) | PARTIAL (API-level only) |
| US-07 (AI Recommendation) | PARTIAL |
| US-08 (Anomaly alert) | PARTIAL |
| US-10 AC2 (Receiving qty limit) | IMPLEMENTED (test_req_br_04) |
| US-11 AC2 (Close prerequisite) | MISSING |

---

## 9. DOCUMENTATION DRIFT

| ID | Severity | Document | Claim | Reality |
|---|---|---|---|---|
| DD-01 | CRITICAL | `traceability-matrix.md` | References `backend/app/services/po_service.py` | File KHÔNG TỒN TẠI |
| DD-02 | CRITICAL | `traceability-matrix.md` | References `frontend/src/modules/po/hooks/usePOCreation.ts` | File KHÔNG TỒN TẠI |
| DD-03 | CRITICAL | `traceability-matrix.md` | References `frontend/src/modules/quotations/components/ComparisonTable.tsx` | File KHÔNG TỒN TẠI |
| DD-04 | CRITICAL | `traceability-matrix.md` | References `backend/tests/test_po.py` | File KHÔNG TỒN TẠI |
| DD-05 | CRITICAL | `release-notes.md` | "10/10 pytest PASS" | Chỉ có 8 test functions, không có 10 |
| DD-06 | CRITICAL | `release-notes.md` | "1/1 Playwright E2E PASS" | E2E không runnable |
| DD-07 | CRITICAL | `release-notes.md` | "20/20 Q&A Benchmark PASS" | Không có evidence of execution |
| DD-08 | HIGH | `main.py` health check | "PostgreSQL Connected (Prisma)" | Backend không dùng PostgreSQL |
| DD-09 | HIGH | `data-model.md` | Đề cập `POItem` entity | Prisma schema KHÔNG có `POItem` |
| DD-10 | HIGH | `API.md` | PROCUREMENT auth on compare | Router không check auth |
| DD-11 | HIGH | `runbook.md` | Path `d:\THUDDN\group-01-project` | Sai path |
| DD-12 | HIGH | `qa-comprehensive-test-matrix.md` | References `frontend/src/pages/PRList.tsx` | File KHÔNG TỒN TẠI |
| DD-13 | HIGH | `qa-comprehensive-test-matrix.md` | References `backend/app/services/pr_service.py` | File KHÔNG TỒN TẠI |
| DD-14 | MEDIUM | `test-strategy.md` | TC-06: REQ-FR-05/06 mapping | REQ-FR-05/06 là PR approval, không phải quotation |
| DD-15 | MEDIUM | `traceability-matrix.md` | "Chạy mượt mà trên Docker Compose + PostgreSQL 18" | Backend không kết nối PostgreSQL |
| DD-16 | LOW | `docs/logs/ai-usage-log.md` | File tồn tại | File rỗng (1 byte). Actual log ở `docs/02-vault/AI Usage Log.md` |

---

## 10. TRACEABILITY GAPS

### User Story Traceability Table

| Req ID | User Story | Task | File/Code | API | Test | Status |
|---|---|---|---|---|---|---|
| REQ-FR-01 | US-01 | T-011 | `procurement_service.py:create_pr()` | POST /api/pr | `test_all_endpoints.py` | PARTIAL |
| REQ-FR-02 | US-01 | T-012 | Không có validation logic riêng | POST /api/pr | MISSING | PARTIAL |
| REQ-FR-03 | US-01 | T-013/014 | `ai_service.py:standardize_pr()` | POST /api/assistant/standardize-pr | `test_all_endpoints.py` | PARTIAL |
| REQ-FR-04 | US-02 | T-021 | `App.tsx` status badge | GET /api/pr | MISSING | PARTIAL |
| REQ-FR-05 | US-03 | T-031 | `pr.py:list_prs()` | GET /api/pr | MISSING | PARTIAL |
| REQ-FR-06 | US-03 | T-032/033/034 | `approve_pr()` — APPROVE ONLY | POST /api/pr/:id/approve | `test_business_rules.py` | PARTIAL — Reject/Revision MISSING |
| REQ-FR-07 | US-03 | T-032 | `approve_pr()` | POST /api/pr/:id/approve | `test_business_rules.py` | PARTIAL |
| REQ-FR-08 | US-04 | T-041 | `get_budget()` | GET /api/budget/:id | MISSING | PARTIAL |
| REQ-FR-09 | US-04 | T-042 | Budget check in `create_pr()` | POST /api/pr | `test_req_br_01` | PARTIAL — Warning UI MISSING |
| REQ-FR-10 | US-05 | T-051/052/053 | No Supplier CRUD | MISSING endpoint | MISSING | MISSING |
| REQ-FR-11 | US-05 | T-054 | `compare_quotations()` partial | POST /api/quotations/compare | MISSING | PARTIAL |
| REQ-FR-12 | US-06 | T-061/062/063 | `App.tsx` comparison table | POST /api/quotations/compare | MISSING | PARTIAL |
| REQ-FR-13 | US-07 | T-071/072/073 | `compare_quotations()` | POST /api/quotations/compare | MISSING | PARTIAL |
| REQ-FR-14 | US-07 | T-072 | No explicit recommendation field in response | POST /api/quotations/compare | MISSING | MISSING |
| REQ-FR-15 | US-08 | T-081/082/083 | `ai_service.py` anomaly flag | POST /api/quotations/compare | MISSING | PARTIAL |
| REQ-FR-16 | US-09 | T-091..094 | `create_po()` | POST /api/po | `test_req_br_03` | PARTIAL — missing PR status check (BUG-001) |
| REQ-FR-17 | US-10 | T-101/102/103 | `receive_goods()` | POST /api/receiving | `test_req_br_04` | PARTIAL |
| REQ-FR-18 | US-11 | T-111 | `close_pr()` | POST /api/pr/:id/close | MISSING | PARTIAL — missing prerequisite check (BUG-006) |
| REQ-NFR-01 | All | — | In-memory only, no persistence | — | MISSING | MISSING |
| REQ-NFR-02 | All | — | No RBAC middleware | — | MISSING | MISSING |
| REQ-NFR-03 | All | — | Approval log in-memory only | — | MISSING | PARTIAL |
| REQ-BR-10 | US-09 | T-093 | BUG — not checked in code | — | MISSING | BROKEN |
| REQ-BR-11 | US-11 | T-111 | Not implemented | — | MISSING | MISSING |
| REQ-BR-12 | US-09 | T-094 | Service-level only | — | `test_req_br_03` | PARTIAL |

**Legend:**  
- IMPLEMENTED — Code + Test + Evidence tất cả có  
- PARTIAL — Code có nhưng thiếu test hoặc thiếu feature  
- MISSING — Không có code thực thi  
- BROKEN — Code có nhưng logic sai  
- UNKNOWN — Không đủ thông tin

---

## 11. DEPLOYMENT GAPS

| ID | Severity | Issue |
|---|---|---|
| DEP-01 | CRITICAL | Backend KHÔNG kết nối PostgreSQL — toàn bộ là in-memory. Docker Compose chạy DB nhưng backend không dùng |
| DEP-02 | CRITICAL | Không có git repository — không có version control, không có commit history |
| DEP-03 | HIGH | `seed.py` chỉ seed in-memory MockDatabase, không phải PostgreSQL/Prisma |
| DEP-04 | HIGH | Không có Prisma migration files. Schema có nhưng không có `prisma/migrations/` |
| DEP-05 | HIGH | `backend/.env.example` tồn tại nhưng không có `.env` thực |
| DEP-06 | HIGH | Runbook dùng sai path (`d:\THUDDN\` thay vì `d:\LTUD\`) |
| DEP-07 | MEDIUM | Không có deployment URL accessible (chỉ localhost) |
| DEP-08 | MEDIUM | Không có Docker image cho backend/frontend — chỉ có DB trong compose.yaml |
| DEP-09 | MEDIUM | Playwright tests require `playwright.config.ts` và `npx playwright install` — không có config file |
| DEP-10 | LOW | Frontend có `lucide-react` dependency nhưng không được dùng trong `App.tsx` |

---

## 12. AI EVIDENCE GAPS

| ID | Severity | Issue |
|---|---|---|
| AI-01 | CRITICAL | `docs/logs/ai-usage-log.md` — rỗng (1 byte) |
| AI-02 | HIGH | `docs/02-vault/AI Usage Log.md` — có content (A-01..A-10) nhưng chỉ cover requirements/design phase, không cover implementation phase |
| AI-03 | HIGH | Không có AI prompt evidence cho: code generation, test generation, review |
| AI-04 | HIGH | Không có evidence AI được dùng thực sự cho AI features — `ai_service.py` là regex parser, không phải LLM |
| AI-05 | MEDIUM | `release-notes.md` claim "20-Q&A Benchmark: 20/20 PASS" — không có evidence of execution |
| AI-06 | MEDIUM | `traceability-matrix.md` có VIVA Q&A answers nhưng đây là preparation document, không phải execution evidence |
| AI-07 | LOW | AI Usage Log thiếu: Task ID, AI Tool name, Prompt content, execution timestamp |

### Phân tích AI features thực tế

**1. PR Standardization (`ai_service.py:standardize_pr()`)**
- Thực chất: Regex parser (`re.search()`)
- Không phải LLM
- Hardcoded item names và prices
- Không grounded trong real product catalog

**2. Quotation Comparison (`ai_service.py:compare_quotations()`)**
- Thực chất: Hardcoded 3 suppliers với fixed prices
- Không extract từ real PDF files
- `files` parameter bị ignore (chỉ dùng để loop index)
- `historical_avg_price = 25_000_000` hardcoded, không phải từ DB

---

## 13. HUMAN DECISIONS REQUIRED

> Những vấn đề sau đây cần **Human Decision** trước khi có thể proceed với implementation.

### HD-01 — SCOPE: In-memory vs Real Database
**Vấn đề:** Backend hiện tại dùng in-memory dict. Có cần kết nối PostgreSQL thật không?  
**Options:** (1) Giữ in-memory (demo được nhanh) / (2) Chuyển sang Prisma+PostgreSQL thật (đúng architecture)  
**Impact:** Ảnh hưởng đến tất cả các task còn lại

### HD-02 — SCOPE: Real JWT vs Mock Auth
**Vấn đề:** Auth hiện tại là mock string. Có cần real JWT không?  
**Note:** PyJWT đã trong dependencies (`pyproject.toml`) nhưng chưa dùng  
**Impact:** SEC-01, SEC-02, SEC-03

### HD-03 — SCOPE: Real AI vs Rule-based
**Vấn đề:** AI features hiện là regex/hardcoded. Course requirements có yêu cầu real LLM không?  
**Note:** `config.py` có `LLM_API_KEY` field nhưng không được dùng  
**Impact:** AI evidence, course grading

### HD-04 — PRIORITY: Fix BUG-001 trước khi demo?
**Vấn đề:** QF-001 đã được document là OPEN. PR status check cho PO creation thiếu.  
**Decision needed:** Fix ngay hay demo workaround?

### HD-05 — PLAYWRIGHT: Giữ hay rebuild E2E tests?
**Vấn đề:** Playwright spec file không runnable với frontend hiện tại.  
**Options:** (1) Rebuild frontend với routing để match E2E / (2) Rewrite E2E để match current frontend

### HD-06 — GIT: Cần setup git repository không?
**Vấn đề:** Course requirements đề cập Pull Requests, commits. Project không có git.  
**Decision needed:** Initialize git repo và tạo commit history?

### HD-07 — CLOSE PR: Confirm trigger condition
**Vấn đề:** Close PR hiện trigger bởi Finance ở trạng thái `PO_CREATED`. Theo prototype.md, cần Receiving hoàn thành trước.  
**Decision needed:** Confirm close PR trigger condition và required receiving state.

---

## 14. RECOMMENDED DEVELOPMENT ORDER

> Khuyến nghị này dựa trên analysis. **KHÔNG thực hiện cho đến khi có Human Decision** về scope (HD-01, HD-02, HD-03).

### Phase 1 — Critical Fixes (Blockers cho demo)
1. FIX BUG-004 — Sửa TypeScript syntax error (`fontWeight 700` → `fontWeight: 700`) để build được
2. FIX BUG-005 — Sửa `setStandardized(data.standardized)` → `setStandardized(data)` trong `App.tsx`
3. FIX BUG-001 — Thêm PR status check vào `create_po()` (đã documented QF-001)
4. FIX BUG-006 — Thêm receiving completion check vào `close_pr()`
5. FIX BUG-007 — Update path trong `runbook.md` và `README.md`

### Phase 2 — Missing Must-have Features
6. ADD: Reject PR endpoint và logic
7. ADD: Request Revision endpoint và logic + `REVISION_REQUESTED` status
8. ADD: Filter PR by role (list PRs based on role)
9. ADD: Budget warning display trên Frontend
10. ADD: Close PR prerequisite validation

### Phase 3 — Security (nếu scope cho phép)
11. Real JWT generation trong `auth.py`
12. JWT middleware verification
13. RBAC middleware (role-based endpoint protection)
14. Fix CORS từ wildcard sang specific origins

### Phase 4 — Testing
15. Fix test isolation (reset `db` state trước mỗi test)
16. Add missing business rule tests (BR-10, BR-11)
17. Viết integration tests
18. Fix/rewrite Playwright E2E (sau khi confirm frontend structure)

### Phase 5 — Documentation & Evidence
19. Update `ai-usage-log.md` với actual log entries (implementation phase)
20. Fix tất cả phantom references trong `traceability-matrix.md`
21. Update `release-notes.md` với accurate test counts và actual results
22. Fix health check response
23. Initialize git repository và create meaningful commits

### Phase 6 — Database (nếu scope yêu cầu)
24. Implement Prisma client calls thay thế MockDatabase
25. Run `prisma migrate dev`
26. Update `seed.py` để seed PostgreSQL thật

---

## APPENDIX A: Phantom Files (Referenced in docs but NOT EXISTS)

```
backend/app/services/po_service.py               NOT EXISTS — phantom
backend/app/services/pr_service.py               NOT EXISTS — phantom
backend/tests/test_po.py                         NOT EXISTS — phantom
frontend/src/modules/po/hooks/usePOCreation.ts   NOT EXISTS — phantom
frontend/src/modules/quotations/components/ComparisonTable.tsx  NOT EXISTS — phantom
frontend/src/pages/PRList.tsx                    NOT EXISTS — phantom
docs/architecture.md                             NOT EXISTS — phantom (referenced in AI log)
docs/DESIGN.md                                   NOT EXISTS — phantom (referenced in traceability)
prisma/migrations/                               NOT EXISTS — phantom
```

---

*Báo cáo này được tạo bằng cách đọc và phân tích trực tiếp toàn bộ source code và documentation. Không có code nào được sửa đổi trong quá trình kiểm tra.*

*Phiên bản: BASELINE v1.0 — 2026-09-16*

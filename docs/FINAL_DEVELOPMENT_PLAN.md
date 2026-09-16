# FINAL DEVELOPMENT PLAN
## AI Procurement & Purchase Approval System
### MIS3032_1 — Group 01 — Branch: final-delivery

**Baseline:** `docs/FINAL_DELIVERY_BASELINE.md` (commit 24739fb)
**Ngay lap ke hoach:** 2026-09-16
**Trang thai:** PLAN ONLY — Cho Human Decision HD-01..HD-05, HD-07 truoc khi thuc thi
**Nguon su that:** Source code > Documentation khi mau thuan

> QUAN TRONG: Tai lieu nay KHONG tu chon scope cho bat ky Human Decision nao.
> Moi task co dependency vao HD chua duoc chot se ghi ro: BLOCKED on HD-XX.

---

## 1. CURRENT STATE

Trang thai duoc xac dinh truc tiep tu source code. Khong suy doan.

### 1.1 Backend

| Component | Trang thai | Evidence |
|---|---|---|
| FastAPI app entry point | IMPLEMENTED | `backend/app/main.py` |
| Router: auth | IMPLEMENTED (MOCK) | `auth.py` — hardcoded users, plain string token |
| Router: pr (create, list, approve, close) | PARTIAL | `pr.py` — missing reject, revision |
| Router: quotations (compare) | PARTIAL | `quotations.py` — no auth check |
| Router: po (create, list) | PARTIAL | `po.py` — missing PR status check (BUG-001) |
| Router: receiving | IMPLEMENTED | `receiving.py` — quantity guard present |
| Router: budget | IMPLEMENTED | `budget.py` — 2 departments only |
| Router: assistant (standardize) | IMPLEMENTED | `assistant.py` — calls ai_service |
| Service: procurement_service | PARTIAL | In-memory dict, missing checks (BUG-001, BUG-006) |
| Service: ai_service | IMPLEMENTED (MOCK) | Regex parser, hardcoded suppliers |
| Service: po_service | MISSING | File khong ton tai — phantom reference |
| Service: pr_service | MISSING | File khong ton tai — phantom reference |
| Database connection | MISSING | Backend khong goi Prisma, khong connect PostgreSQL |
| JWT authentication | BROKEN | Tra ve mock string, khong verify |
| RBAC middleware | MISSING | Khong co middleware, khong require auth |
| Config | IMPLEMENTED | `config.py` — LLM_API_KEY field co nhung unused |
| Health check | BROKEN | Hardcode "PostgreSQL Connected" — false positive |

### 1.2 Frontend

| Component | Trang thai | Evidence |
|---|---|---|
| Single page app (App.tsx) | IMPLEMENTED | `frontend/src/App.tsx` 418 lines |
| Role selector (dropdown UI) | IMPLEMENTED (MOCK) | UI-only, not JWT-based |
| Budget display card | IMPLEMENTED | 4-column budget grid |
| AI standardize PR | PARTIAL | BUG-005: reads data.standardized but API returns flat object |
| Create PR flow | IMPLEMENTED | Calls POST /api/pr |
| PR list with status badge | IMPLEMENTED | Basic inline styles |
| Approve PR button (Manager) | IMPLEMENTED | Role-conditional render |
| Finance approve button | IMPLEMENTED | Role-conditional render |
| AI compare quotations | IMPLEMENTED | Calls POST /api/quotations/compare |
| Create PO button | IMPLEMENTED | Calls POST /api/po |
| Close PR button | IMPLEMENTED | Calls POST /api/pr/:id/close |
| Login page | MISSING | Khong co — chi co role selector dropdown |
| React Router | MISSING | Single page, no routes |
| Reject PR UI | MISSING | Khong co button |
| Request Revision UI | MISSING | Khong co button |
| Supplier management UI | MISSING | Khong co |
| File upload UI | MISSING | Khong co real file input |
| Budget warning alert | MISSING | Khong co warning khi vuot budget |
| TypeScript build validity | BROKEN | BUG-004: fontWeight 700 syntax error (L256, L260) |

### 1.3 Database

| Component | Trang thai | Evidence |
|---|---|---|
| Prisma schema | DOCUMENTATION ONLY | `backend/prisma/schema.prisma` — day du nhung khong dung |
| PostgreSQL Docker | IMPLEMENTED | `compose.yaml` — runs on port 5432 |
| Prisma migration | MISSING | Khong co `prisma/migrations/` |
| Backend DB connection | MISSING | Backend dung in-memory dict |
| Data persistence | MISSING | Data mat sau khi restart backend |
| Seed script (DB that) | MISSING | `seed.py` seed vao MockDatabase, khong ghi PostgreSQL |

### 1.4 Authentication

| Component | Trang thai | Evidence |
|---|---|---|
| Login endpoint | IMPLEMENTED (MOCK) | `auth.py` — hardcoded dict lookup |
| Password verification | BROKEN | Hardcoded == "password123" |
| JWT generation | MISSING | Returns plain string, not JWT |
| JWT verification middleware | MISSING | Khong co dependency injection |
| bcrypt password hashing | MISSING | passlib[bcrypt] in pyproject.toml nhung khong import |

### 1.5 Authorization / RBAC

| Component | Trang thai | Evidence |
|---|---|---|
| RBAC middleware | MISSING | Khong co |
| PR list filter by role | MISSING | list_prs() tra ve tat ca |
| Approve role check | BROKEN (SEC-02) | approverRole nhan tu client body, khong verify JWT |
| PO create role check | MISSING | Khong co |
| Close PR role check | MISSING | Khong co |
| Frontend role-based render | PARTIAL | Conditional render nhung dua vao dropdown, khong JWT |

### 1.6 AI Features

| Feature | Trang thai | Evidence | ADR |
|---|---|---|---|
| PR standardization | IMPLEMENTED (MOCK) | ai_service.py:standardize_pr() — regex | ADR-001: Fallback |
| Quotation comparison | IMPLEMENTED (MOCK) | ai_service.py:compare_quotations() — hardcoded | ADR-001: Fallback |
| Anomaly detection (>=20%) | IMPLEMENTED (MOCK) | historical_avg=25M hardcoded | ADR-001 |
| AI Recommendation field | PARTIAL | is_anomaly flag present, no explicit recommendation | REQ-FR-14 |
| PDF file extraction | MISSING | files param ignored | ASM-07 |
| LLM integration (Gemini/OpenAI) | MISSING | LLM_API_KEY in config but unused | ADR-001: Primary |

### 1.7 Business Rules

| Rule | Trang thai | Evidence |
|---|---|---|
| REQ-BR-01: Budget check khi tao PR | IMPLEMENTED | create_pr() kiem tra available budget |
| REQ-BR-02: 2-level approval (>50M) | IMPLEMENTED | approve_pr() — logic co, role tu client body |
| REQ-BR-03: Manager approval scope | UNVERIFIED | Khong co dept-based scope check |
| REQ-BR-10: PO chi sau PR APPROVED | BROKEN | BUG-001 — create_po() khong check PR status |
| REQ-BR-11: Close sau Receiving hoan thanh | MISSING | BUG-006 — close_pr() khong check receiving |
| REQ-BR-12: PO price = Quotation price | IMPLEMENTED (SERVICE LEVEL) | create_po() copy price tu quotation |

### 1.8 Testing

| Test Type | Trang thai | Evidence |
|---|---|---|
| 4 Business Rule unit tests | IMPLEMENTED | test_business_rules.py |
| 4 API endpoint tests | IMPLEMENTED | test_all_endpoints.py |
| Test isolation | BROKEN | Shared db singleton |
| pytest execution evidence | UNVERIFIED | Tests exist but no execution log |
| Integration tests | MISSING | Khong co |
| E2E Playwright spec | DOCUMENTATION ONLY | File in wrong dir, selectors don't match |
| E2E runnable | MISSING | No playwright.config.ts, frontend has no routing |
| TC-US09-001 | NOT RUN | docs/qa/TEST_CASES_US09.md — Status: NOT RUN |

### 1.9 Documentation

| Document | Trang thai |
|---|---|
| requirements.md | IMPLEMENTED — Good |
| user-story.md | IMPLEMENTED — Good |
| backlog.md | IMPLEMENTED — Good |
| ADR-001, ADR-002 | IMPLEMENTED — Good |
| traceability-matrix.md | PARTIAL — US-09 only, 4 phantom file refs |
| release-notes.md | BROKEN — False PASS claims |
| runbook.md | BROKEN — Wrong paths |
| ai-usage-log.md (logs/) | BROKEN — Empty (1 byte) |
| AI Usage Log.md (vault/) | PARTIAL — Design phase only |
| FINAL_DELIVERY_BASELINE.md | IMPLEMENTED — Committed to git |

### 1.10 Git

| Component | Trang thai | Evidence |
|---|---|---|
| Git repository | IMPLEMENTED | Initialized 2026-09-16 |
| Branch: master | IMPLEMENTED | commit 3df8a55 (58 files) |
| Branch: final-delivery | IMPLEMENTED | commit 24739fb (FINAL_DELIVERY_BASELINE.md) |
| Remote repository | MISSING | No remote configured |

---

## 2. HUMAN DECISIONS

### HD-01 — In-memory hay Real PostgreSQL?

**Requirement:** REQ-NFR-01 (data consistency)
**ADR:** ADR-002 — "PostgreSQL 18 + Prisma Client" (ACCEPTED)
**Conflict:** ADR-002 quyet dinh PostgreSQL + Prisma nhung code la in-memory MockDatabase.

**Current implementation:** procurement_service.py — class MockDatabase dung Python dict. prisma/schema.prisma day du nhung khong duoc backend goi. pyproject.toml co prisma>=0.14.0 nhung khong import.

**Phuong an A — Giu in-memory:**
- Khong can thay doi infrastructure
- Data mat khi restart (demo phai trong 1 session)
- Bo qua REQ-NFR-01 va ADR-002
- Demo on dinh hon, risk thap hon

**Phuong an B — Implement Prisma + PostgreSQL:**
- Phai chay prisma generate, prisma migrate dev
- Thay the toan bo MockDatabase bang Prisma calls
- Data persist qua sessions, dap ung ADR-002
- Effort cao hon, risk introduce bugs moi

**Files bi anh huong (neu B):** procurement_service.py toan bo, seed.py, main.py, tat ca routers
**Dependencies:** HD-01 anh huong den tat ca task backend
**Effort:** A = 0, B = cao (2-3x effort)
**Testing (neu B):** Integration tests voi real DB
**Evidence (neu B):** DB query logs, migration output

---

### HD-02 — Mock Auth hay Real JWT?

**Requirement:** REQ-NFR-02 (RBAC)
**ADR:** ADR-002 — "JWT Token + bcrypt password hashing" (ACCEPTED)
**Conflict:** ADR-002 quyet dinh JWT + bcrypt nhung implementation la plaintext mock string.

**Current implementation:** auth.py tra ve f"mock-jwt-token-for-{email}". Endpoints khong verify token. pyjwt>=2.9.0 va passlib[bcrypt]>=1.7.4 trong pyproject.toml nhung khong import.

**Phuong an A — Giu Mock Auth:**
- SEC-01, SEC-02, SEC-03 van open
- RBAC khong enforce duoc properly
- Demo qua role selector dropdown
- Effort: 0

**Phuong an B — Real JWT:**
- Generate JWT voi pyjwt, verify qua middleware
- Frontend phai send Authorization header
- Phu thuoc HD-01 direction (user data tu DB hay hardcoded list)
- Effort: trung binh

**Files bi anh huong (neu B):** auth.py, config.py, tat ca routers, App.tsx
**Dependencies:** HD-02=B phu thuoc HD-01 direction
**Effort:** A = 0, B = trung binh

---

### HD-03 — Regex/Mock AI hay Real LLM?

**Requirement:** REQ-FR-03, REQ-FR-13, REQ-FR-14, REQ-FR-15
**ADR:** ADR-001 — "Primary = Gemini/OpenAI, Fallback = Mock" (ACCEPTED)
**Conflict:** ADR-001 mo ta Mock la fallback, khong phai primary. Hien tai chi co fallback.

**Current implementation:** ai_service.py dung re.search() va hardcoded data. files parameter bi ignore. LLM_API_KEY trong config nhung ai_service.py khong import config.

**Phuong an A — Giu Mock/Regex:**
- Dung voi ADR-001 fallback mode
- Demo on dinh, sub-second, no API quota risk
- Khong co LLM execution evidence
- Can update documentation

**Phuong an B — Implement Real LLM:**
- Goi Gemini/OpenAI API thuc
- Output validate qua Pydantic schema (ADR-001 requirement)
- API quota risk trong demo, latency cao
- Evidence day du: actual AI response, prompt+response pairs

**Files bi anh huong (neu B):** ai_service.py, config.py, backend/.env
**Dependencies:** HD-03 doc lap voi HD-01, HD-02
**Effort:** A = thap (chi them recommendation field), B = trung binh-cao

---

### HD-04 — Fix BUG-001 (PO khi PR chua APPROVED)?

**Requirement:** REQ-BR-10
**US:** US-09 AC2
**QA Finding:** QF-001 — Status OPEN

**Current implementation:** procurement_service.py:create_po() chi check PR ton tai, khong check pr["status"] == "APPROVED".

**Phuong an A — Fix BUG-001:**
Them status check vao create_po(). Chay TC-US09-001. Effort: rat thap (~5 phut code).

**Phuong an B — Demo workaround:**
Khong sua code. Huong dan demo de khong trigger bug. Rui ro: giang vien co the test case nay.

**Files bi anh huong (neu A):** procurement_service.py (L101-124), test_business_rules.py
**Dependencies:** Khong phu thuoc HD-01, HD-02, HD-03
**Effort:** A = thap nhat, B = 0

---

### HD-05 — Rebuild Frontend hay Rewrite E2E Tests?

**Current state:** Playwright spec o docs/06-testing/ (sai location). Frontend khong co routing, khong co CSS classes matching spec, khong co modal, khong co /login route.

**Phuong an A — Rebuild Frontend voi proper routing:**
- Install react-router-dom, tao separate pages /login, /pr, /pr/:id
- Add CSS classes matching E2E spec selectors, add modal component
- Effort: cao — major frontend refactor

**Phuong an B — Rewrite E2E Tests de match current frontend:**
- Giu App.tsx single-page structure
- Rewrite Playwright spec voi selectors phu hop App.tsx hien tai
- Tao playwright.config.ts, move spec file vao frontend/
- Effort: trung binh

**Files bi anh huong:**
- A: App.tsx + nhieu file moi
- B: playwright-e2e-us09.spec.ts + playwright.config.ts

**Dependencies:** HD-05=A phu thuoc HD-02 (login page = auth decision)

---

### HD-06 — Git Repository

**Status: DECIDED / COMPLETED**

**Evidence (confirmed from source):**
- Git repository: D:/LTUD/group-01-project-main/.git/ — Initialized 2026-09-16
- Branch master: commit 3df8a55 — "chore: initial commit — project baseline before final delivery" (58 files)
- Branch final-delivery: commit 24739fb — "docs: add FINAL_DELIVERY_BASELINE audit report"
- docs/FINAL_DELIVERY_BASELINE.md committed to branch final-delivery

**Note:** No remote repository configured. If GitHub PR evidence required by course, additional action needed.

---

### HD-07 — Close PR trigger condition?

**Requirement:** REQ-FR-18, REQ-BR-11
**US:** US-11 AC1, US-11 AC2
**Current state:** close_pr() khong verify receiving. App.tsx shows Close button when status === 'PO_CREATED'.

**Cau hoi can Human confirm:**

Q1: "Hoan tat" nghia la:
- (a) Tong receivedQty >= po["quantity"]
- (b) Co it nhat 1 Receiving record (partial OK)
- (c) Condition khac?

Q2: Ai duoc phep Close PR?
- (a) Chi FINANCE (nhu hien tai trong App.tsx)
- (b) FINANCE hoac ADMIN

Q3: PR status nao cho phep Close?
- (a) PO_CREATED (nhu hien tai)
- (b) PARTIALLY_RECEIVED
- (c) RECEIVED (sau full receive)

**Files bi anh huong:** procurement_service.py:close_pr(), App.tsx, test_business_rules.py
**Dependencies:** Khong phu thuoc HD-01, HD-02

---

## 3. DEPENDENCY MAP

```
[HD-06: Git] --- COMPLETED

[HD-04: BUG-001] --------> WS-03 (TASK-005) --------> WS-08 (TASK-020)
[HD-07: Close PR] -------> WS-03 (TASK-006) --------> WS-08 (TASK-021)

[HD-01: Database] -------> WS-05 (TASK-014, 015)
    |
    v
[HD-02: Auth] -----------> WS-04 (TASK-010..013)
    |
    v
[HD-05: E2E] ------------> WS-07 (TASK-017, 018)

[HD-03: AI] -------------> WS-06 (TASK-016A or 016B)

[WS-02: Frontend Build] -> blocks demo, independent
[WS-09: Documentation] -> parallel with all WS
[WS-10: AI Evidence] ---> follows each coding task
[WS-11: Final Verify] --> last, depends on ALL
```

**Mandatory decision order:**
1. HD-04 — doc lap, effort thap nhat, unlock TASK-005+020
2. HD-07 — doc lap, can confirm condition, unlock TASK-006+021
3. HD-01 — highest impact, decide before WS-05
4. HD-02 — after HD-01 direction clear
5. HD-03 — doc lap, decide for WS-06
6. HD-05 — after knowing frontend direction from HD-02

---

## 4. FINAL WORKSTREAMS

| WS | Name | Mo ta | Blocked on |
|---|---|---|---|
| WS-01 | Git & Baseline | Init git, branch, commit baseline | COMPLETED |
| WS-02 | Frontend Build Fix | Fix syntax errors, ensure build works | None |
| WS-03 | Business Rules | Fix BUG-001, BUG-006, reject PR, revision | HD-04, HD-07 |
| WS-04 | Authentication & RBAC | JWT, middleware, RBAC enforcement | HD-01, HD-02 |
| WS-05 | Database / Persistence | Prisma migration, replace MockDatabase | HD-01 |
| WS-06 | AI Features | Mock enhancement or LLM integration | HD-03 |
| WS-07 | E2E Testing | Playwright config, spec fix or rebuild | HD-05 |
| WS-08 | Unit & Integration Testing | Fix isolation, add missing tests, evidence | HD-04, HD-07 |
| WS-09 | Documentation | Fix phantom refs, runbook, release notes | None |
| WS-10 | AI Prompt Evidence | Document AI usage for each coding task | Follows WS |
| WS-11 | Final Verification | Run all tests, review evidence, demo prep | All WS |

---

## 5. TASK BREAKDOWN

### WS-01: Git & Baseline — COMPLETED

**TASK-001** — Initialize Git, branch, commit FINAL_DELIVERY_BASELINE
Status: COMPLETED (commits 3df8a55, 24739fb on branch final-delivery)

---

### WS-02: Frontend Build Fix

**TASK-002** — Fix TypeScript syntax errors (BUG-004)
Objective: npm run build succeeds without errors
Req: REQ-NFR-01 | Files: frontend/src/App.tsx (L256, L260)
Dependencies: None
Implementation: L256 and L260: fontWeight 700 -> fontWeight: 700 (add colon)
Test: npm run build exits code 0
Evidence: Build output log showing 0 errors
DoD: Zero TypeScript errors; build succeeds

**TASK-003** — Fix frontend/backend mismatch for AI standardize (BUG-005)
Objective: Standardize PR result displays from real API, not fallback mock
Req: REQ-FR-03 | US: US-01 AC2 | Files: frontend/src/App.tsx (L75)
Dependencies: TASK-002
Implementation: Change setStandardized(data.standardized) -> setStandardized(data)
Test: Manual — click AI standardize, verify real API data shown
Evidence: Browser Network tab screenshot
DoD: Real API data shown without hitting fallback

**TASK-004** — Fix false health check response (BUG-003)
Objective: Health check reflects actual system state
Req: REQ-NFR-01 | Files: backend/app/main.py (L38-44)
Dependencies: HD-01 (message content depends on DB decision)
Implementation: HD-01=A -> "In-Memory Demo Mode"; HD-01=B -> actual DB ping
Test: GET /api/health response matches actual state
Evidence: API response screenshot
DoD: Health check does not claim false PostgreSQL connection

---

### WS-03: Business Rules

**TASK-005** — Fix BUG-001: PR status check before PO creation (QF-001 / REQ-BR-10)
Objective: create_po() rejects with ValueError when PR not APPROVED
Req: REQ-FR-16, REQ-BR-10 | US: US-09 AC2
Files: backend/app/services/procurement_service.py (L101-124)
Dependencies: HD-04 must be decided (if A: implement fix)
Implementation: After pr = db.prs.get(pr_id) check, add:
  if pr["status"] not in ["APPROVED", "COLLECTING_QUOTATIONS"]:
    raise ValueError(f"Khong the tao PO: PR {pr_id} dang o trang thai {pr['status']}. PR phai APPROVED truoc.")
Test: TC-US09-001 — PENDING_MANAGER_APPROVAL PR -> create_po -> expect ValueError
Evidence: pytest output showing TC-US09-001 PASS; update QA_FINDINGS.md QF-001 status to FIXED
DoD: ValueError raised for non-APPROVED PR; TC-US09-001 = PASS with execution log

**TASK-006** — Fix BUG-006: Receiving completion check before Close PR (REQ-BR-11)
Objective: close_pr() rejects when receiving incomplete per HD-07 condition
Req: REQ-FR-18, REQ-BR-11 | US: US-11 AC2
Files: backend/app/services/procurement_service.py (L154-168)
Dependencies: BLOCKED on HD-07
Implementation: PENDING HD-07. Logic: sum receivedQty for PR POs, compare to po["quantity"]
Test: Negative: close without receiving -> ValueError; Positive: full receive -> CLOSED
Evidence: pytest output for both test cases
DoD: close_pr() enforces condition per HD-07; both tests PASS

**TASK-007** — Implement Reject PR
Objective: Manager/Finance can Reject PR; status = REJECTED; tempReservedAmount released
Req: REQ-FR-06 | US: US-03 AC3
Files: procurement_service.py (add reject_pr), pr.py (add router), App.tsx (add button)
Dependencies: TASK-002
Implementation:
  Service: reject_pr(pr_id, role, name, comments) -> status=REJECTED, release tempReservedAmount
  Router: POST /api/pr/:id/reject
  Frontend: Reject button for MANAGER when status=PENDING_MANAGER_APPROVAL
Test: reject_pr changes status; budget released
Evidence: pytest PASS; frontend screenshot of Reject button and REJECTED status
DoD: Reject works via API and UI; budget released; test PASS with evidence

**TASK-008** — Implement Request Revision
Objective: Manager can request revision; PR status = REVISION_REQUESTED
Req: REQ-FR-06 | US: US-03 AC3
Files: procurement_service.py, pr.py, App.tsx
Dependencies: TASK-007
Implementation: Add REVISION_REQUESTED status handling. POST /api/pr/:id/request-revision router.
Note: PRStatus enum in Prisma schema does NOT include REVISION_REQUESTED.
      If HD-01=B, this needs schema migration.
Test: Request Revision -> REVISION_REQUESTED; status transitions correct
Evidence: pytest PASS; frontend screenshot
DoD: Status transitions correct; tests PASS

**TASK-009** — PR list filter by role
Objective: Role-appropriate PR list (EMPLOYEE->own, MANAGER->pending, PROCUREMENT->approved)
Req: REQ-FR-05, REQ-NFR-02 | US: US-02, US-03
Files: pr.py (list_prs), procurement_service.py, App.tsx
Dependencies: HD-02 direction (query param role vs JWT)
Implementation:
  HD-02=A: add ?role= query param to GET /api/pr, filter in service
  HD-02=B: use JWT identity from token
Test: API test confirming role-filtered response
Evidence: API response showing filtered results
DoD: PR list returns role-appropriate subset; test PASS

---

### WS-04: Authentication & RBAC — BLOCKED on HD-01, HD-02

**TASK-010** — Real JWT generation (HD-02=B path only)
Objective: /api/auth/login returns signed JWT
Req: REQ-NFR-02 | Files: auth.py, config.py
Dependencies: BLOCKED on HD-02
Implementation: pyjwt generate JWT with payload {sub, role, departmentId, exp=now+8h}
Test: Login returns decodable JWT with correct claims
DoD: Real JWT returned; can be decoded with JWT_SECRET

**TASK-011** — JWT verification middleware (HD-02=B)
Objective: Protected endpoints require valid JWT; return 401 otherwise
Req: REQ-NFR-02 | Files: new backend/app/dependencies.py; all routers
Dependencies: TASK-010; BLOCKED on HD-02
Test: No token -> 401; invalid token -> 401; valid token -> passes
DoD: All protected endpoints return 401 without valid JWT

**TASK-012** — RBAC enforcement (HD-02=B)
Objective: Only authorized roles can call protected endpoints
Req: REQ-NFR-02 | US: US-03, US-09, US-10, US-11
Files: All routers, dependencies.py
Dependencies: TASK-011; BLOCKED on HD-02
Implementation: require_role(*roles) dependency. Apply to: approve (MANAGER/FINANCE), po (PROCUREMENT), close (FINANCE). Remove approverRole from request body.
Test: EMPLOYEE tries approve -> 403; PROCUREMENT tries approve -> 403
DoD: All critical endpoints enforce role; tests PASS; approverRole removed from request body

**TASK-013** — Frontend login flow (HD-02=B)
Objective: User must login; JWT stored; all API calls include Authorization header
Req: REQ-NFR-02 | Files: App.tsx
Dependencies: TASK-010, TASK-011, HD-05 decision
Test: Login flow works; role selector removed, replaced by JWT-decoded role
DoD: JWT used in all API calls; login page exists

---

### WS-05: Database / Persistence — BLOCKED on HD-01

**TASK-014** — Implement Prisma DB connection (HD-01=B path only)
Objective: Backend connects to PostgreSQL; all operations persist
Req: REQ-NFR-01 | Files: main.py, new database.py, all services
Dependencies: BLOCKED on HD-01
Test: Create PR -> restart server -> PR still exists
DoD: Data persists across restarts; all CRUD uses PostgreSQL

**TASK-015** — Rewrite seed.py for PostgreSQL (HD-01=B)
Objective: python seed.py populates real PostgreSQL via Prisma
Files: backend/seed.py
Dependencies: TASK-014; BLOCKED on HD-01
Test: Run seed -> GET /api/pr returns seeded data
DoD: Seed creates test data in PostgreSQL; idempotent execution

---

### WS-06: AI Features — BLOCKED on HD-03

**TASK-016A** — Add AI Recommendation field (HD-03=A: Mock path)
Objective: compare_quotations response includes explicit recommendation
Req: REQ-FR-14 | US: US-07 AC2
Files: backend/app/services/ai_service.py
Dependencies: HD-03 = A
Implementation: Find lowest non-anomaly quotation. Return recommendation: {quotation_id, reason}.
Test: API response includes recommendation field; frontend highlights it
DoD: Recommendation field in response; UI displays it

**TASK-016B** — Integrate real LLM API (HD-03=B: Real LLM path)
Objective: PR standardization and quotation analysis use real LLM
Req: REQ-FR-03, REQ-FR-13, REQ-FR-14 | Files: ai_service.py, config.py, backend/.env
Dependencies: HD-03 = B; LLM_API_KEY must be configured in .env
Implementation: Import LLM client (google-generativeai or openai). Create Pydantic schemas for output validation (ADR-001). Keep mock as fallback. Handle quota/timeout errors.
Test: LLM API call evidence; Pydantic schema validation; fallback on error
DoD: Real LLM called; output validated; AI evidence documented with actual prompts

---

### WS-07: E2E Testing — BLOCKED on HD-05

**TASK-017** — Create playwright.config.ts
Objective: npx playwright test can locate and run spec files
Files: frontend/playwright.config.ts (new)
Dependencies: HD-05 decision; TASK-002
Test: npx playwright test --list shows test files
DoD: Playwright finds specs; can launch browser against localhost:5173

**TASK-018** — Move/Rewrite E2E spec for US-09
Objective: At least 1 E2E scenario runs with execution evidence
Req: REQ-FR-16, REQ-BR-10, REQ-BR-12 | US: US-09 AC1, AC2, AC3
Files: docs/06-testing/playwright-e2e-us09.spec.ts -> frontend/tests/
Dependencies: TASK-017; HD-05 decision
Implementation:
  HD-05=A: keep spec as-is after adding routing and CSS classes to frontend
  HD-05=B: rewrite selectors to match current App.tsx structure
Test: npx playwright test runs; TC-09-01 and TC-09-02 execute
Evidence: Playwright HTML report; screenshots; test output
DoD: E2E spec runs; execution evidence exists; at least 2/3 scenarios PASS

---

### WS-08: Unit & Integration Testing

**TASK-019** — Fix pytest test isolation (BUG-008)
Objective: Tests pass regardless of execution order
Files: new backend/tests/conftest.py; test_business_rules.py; test_all_endpoints.py
Dependencies: None
Implementation: conftest.py with @pytest.fixture(autouse=True) that resets db.prs, db.pos, db.receivings, db.budgets to initial state before each test
Test: Run tests in different orders; all pass consistently
Evidence: pytest -v output showing all PASS in multiple orders
DoD: Tests pass in any order; conftest.py exists

**TASK-020** — Add test for REQ-BR-10 (TC-US09-001)
Objective: TC-US09-001 executed and PASS
Req: REQ-BR-10 | US: US-09 AC2
Files: backend/tests/test_business_rules.py, docs/qa/TEST_CASES_US09.md
Dependencies: TASK-005 (BUG-001 fixed first), TASK-019
Implementation: Create PR (not approved) -> call create_po -> expect ValueError containing status description
Evidence: pytest output; update TC-US09-001 Status from NOT RUN to PASS
DoD: Test PASS; TEST_CASES_US09.md updated with Actual Result and PASS status

**TASK-021** — Add test for REQ-BR-11 (US-11 AC2)
Objective: close_pr() rejects when receiving incomplete
Req: REQ-BR-11 | US: US-11 AC2
Files: backend/tests/test_business_rules.py
Dependencies: TASK-006 (BUG-006 fixed), TASK-019, HD-07
Test: Negative: incomplete receiving -> ValueError; Positive: full receive -> CLOSED
DoD: Both tests PASS with execution evidence

**TASK-022** — Add test for Reject PR
Objective: reject_pr() works and releases budget
Req: REQ-FR-06 | US: US-03 AC3
Files: backend/tests/test_business_rules.py
Dependencies: TASK-007, TASK-019
Test: reject_pr changes status; tempReservedAmount released on rejection
DoD: Test PASS; budget released confirmed

**TASK-023** — Run full test suite and capture evidence
Objective: All tests PASS; execution log exists
Files: docs/07-release/release-notes.md (update test counts)
Dependencies: TASK-019, TASK-020, TASK-021, TASK-022
Implementation: uv run pytest -v --tb=short; capture full output
DoD: Full test run completed; results documented with actual counts; NO false PASS claims

---

### WS-09: Documentation

**TASK-024** — Fix runbook.md and README.md paths (BUG-007)
Files: docs/07-release/runbook.md, README.md
Dependencies: None
Implementation: Replace all d:\THUDDN\group-01-project with d:\LTUD\group-01-project-main
DoD: Team member can follow runbook and start system successfully from scratch

**TASK-025** — Update release-notes.md with accurate results
Files: docs/07-release/release-notes.md
Dependencies: TASK-023
Implementation: Update test counts to match actual pytest output; remove unverified E2E PASS claim
DoD: release-notes.md contains only claims backed by actual execution evidence

**TASK-026** — Fix phantom file references in traceability-matrix.md
Files: docs/06-testing/traceability-matrix.md
Dependencies: All WS-03 tasks (need to know which files get created)
Implementation: Fix DD-01..DD-04 phantom references; update PostgreSQL claims
DoD: No phantom references; all paths lead to existing files

**TASK-027** — Update ai-usage-log.md with implementation phase entries
Files: docs/logs/ai-usage-log.md
Dependencies: Follows each coding task
DoD: ai-usage-log.md has entries for all AI-assisted coding tasks; not empty

**TASK-028** — Create complete traceability matrix for all US-01..US-11
Files: docs/06-testing/traceability-matrix.md
Dependencies: All implementation tasks; TASK-026
DoD: All Must requirements have non-orphaned trace chain; status per requirement accurate

---

### WS-10: AI Prompt Evidence

**TASK-029** — Create docs/ai-evidence/ directory and template
Files: docs/ai-evidence/TEMPLATE.md (new)
Dependencies: None
DoD: Directory exists with TEMPLATE.md containing standard evidence structure

**TASK-030** — Write AI evidence documents per coding task
Files: docs/ai-evidence/TASK-XXX-yyy.md (one per significant coding task)
Dependencies: TASK-029; follows each coding task
Evidence document must contain:
  - Task ID and Requirement IDs
  - AI Tool and Model name
  - Actual prompt (verbatim or accurate summary)
  - AI Response Summary (key points)
  - Files Changed (with line references)
  - Human Verification note
  - Test Command (exact command)
  - Actual Test Result (paste output — NOT fabricated)
  - Follow-up prompt if first attempt failed
  - Git Commit hash and message
DoD: Evidence document per coding task; no unverified PASS claims

---

### WS-11: Final Verification

**TASK-031** — Full workflow smoke test
Objective: Complete PR->Close workflow executes without error
Dependencies: All WS-02..WS-09 tasks
Implementation: Follow demo flow Section 10 step by step; document each step
Evidence: Screenshots of each workflow step; no browser console errors
DoD: Full workflow demonstrated with screenshot evidence

**TASK-032** — Final regression test suite
Objective: All automated tests pass after all changes
Dependencies: All WS-08 tasks
Implementation: uv run pytest -v --tb=short; capture output
DoD: Zero test failures; output captured as evidence

**TASK-033** — Final accurate release notes
Objective: Release notes reflect actual final state
Files: docs/07-release/release-notes.md
Dependencies: TASK-032
DoD: Release notes accurate; reference actual git commits; no unverified claims

---

## 6. AI CODING EVIDENCE PLAN

### Evidence Workflow per Task

```
Human defines objective (Task ID + Requirements)
        |
        v
Human writes prompt (with context, constraints, affected files)
        |
        v
AI analyzes -> proposes plan
        |
        v
Human reviews -> APPROVE or MODIFY
        |
        v
AI generates implementation
        |
        v
Human reviews git diff
        |
        v
Human runs tests manually
        |
  FAIL? |
   YES  v
Human writes follow-up prompt with failure info
        |
        v
AI proposes fix -> Human re-runs tests
        |
  PASS  v
git commit (Task ID in message)
        |
        v
Human creates evidence document in docs/ai-evidence/
```

### Evidence Directory Structure

```
docs/
+-- ai-evidence/
    +-- TEMPLATE.md
    +-- TASK-002-fix-typescript-syntax.md
    +-- TASK-003-fix-standardize-response.md
    +-- TASK-005-fix-bug001-po-status-check.md
    +-- TASK-006-fix-bug006-close-pr-receiving.md
    +-- TASK-007-reject-pr.md
    +-- TASK-008-request-revision.md
    +-- TASK-009-pr-list-filter.md
    +-- TASK-019-test-isolation.md
    +-- TASK-020-test-br10.md
    +-- TASK-021-test-br11.md
    +-- ... (one per significant coding task)
```

### Evidence Template (content for docs/ai-evidence/TEMPLATE.md)

```
# AI Evidence: [TASK-ID] --- [Task Title]

## Task
[TASK-ID] --- [Title]

## Requirement IDs
[REQ-IDs] | [US IDs] | [BR IDs]

## AI Tool & Model
[e.g., Antigravity / gemini-2.5-pro]

## Prompt (Verbatim or Accurate Summary)
[Exact prompt or accurate summary — must be real, not fabricated]

## AI Response Summary
[Key points from AI response]

## Files Changed
- [filename:line]: [what changed]

## Human Verification
[What human reviewed: diff, logic check, requirement comparison]

## Test Command
[exact command, e.g., uv run pytest tests/test_business_rules.py::test_req_br_10 -v]

## Actual Test Result
[Paste actual output --- NOT fabricated]
Status: PASS / FAIL

## Follow-up Prompt (if test failed on first attempt)
[Correction requested]

## Final Result
[Final state after all iterations]

## Git Commit
[commit hash] --- [commit message]
```

### Rules
- KHONG ghi PASS neu test chua chay that
- KHONG tao evidence sau khi code da xong ma khong record trong qua trinh lam
- Prompt phai la prompt thuc su su dung

---

## 7. DEVELOPMENT ORDER

### Phase 1 — Immediate (No HD dependencies)
- TASK-019: Fix test isolation (conftest.py)
- TASK-029: Create ai-evidence directory
- TASK-024: Fix runbook paths
- TASK-002: Fix TypeScript syntax [can parallel with TASK-019]
- TASK-003: Fix standardize response mismatch

### Phase 2 — After HD-04 confirmed
- TASK-005: Fix BUG-001 (PR status check)
- TASK-020: Add test for REQ-BR-10
[Can parallel with Phase 3]

### Phase 3 — After HD-07 confirmed
- TASK-006: Fix BUG-006 (receiving completion)
- TASK-021: Add test for REQ-BR-11

### Phase 4 — After Phase 2+3
- TASK-007: Reject PR
- TASK-008: Request Revision
- TASK-009: PR list filter by role
- TASK-022: Tests for Reject PR
- TASK-004: Fix health check [after HD-01 decision]

### Phase 5 — After HD-01, HD-02 confirmed
- [HD-02=B] TASK-010 -> TASK-011 -> TASK-012 -> TASK-013
- [HD-01=B] TASK-014 -> TASK-015 [parallel with auth]

### Phase 6 — After HD-03 confirmed
- [HD-03=A] TASK-016A
- [HD-03=B] TASK-016B

### Phase 7 — After HD-05 confirmed
- TASK-017: playwright.config.ts
- TASK-018: Move/rewrite E2E spec

### Phase 8 — Documentation (parallel with all)
- TASK-025: Update release notes [after TASK-023]
- TASK-026: Fix phantom references [after all coding tasks]
- TASK-027: Update ai-usage-log.md [continuous]
- TASK-028: Full traceability matrix [after implementation]
- TASK-030: AI evidence documents [continuous, follows each task]

### Phase 9 — Final Verification (last)
- TASK-023: Run full test suite
- TASK-031: Workflow smoke test
- TASK-032: Final regression test
- TASK-033: Final release notes

### Tasks that CAN run in parallel

| Group | Tasks |
|---|---|
| A | TASK-019, TASK-029, TASK-024 (setup, no dependencies) |
| B | TASK-002, TASK-003 (frontend fixes, independent) |
| C | TASK-005+020 in parallel with TASK-006+021 |
| D | TASK-007, TASK-008, TASK-009 (after Phase 2) |
| E | WS-04 in parallel with WS-05 (different team members) |

---

## 8. TEST STRATEGY

### Unit Tests (pytest)

| TC | Test | Req | Status |
|---|---|---|---|
| TC-BR-01 | Budget check blocks exceeding PR | REQ-BR-01 | EXISTS |
| TC-BR-02 | 2-level approval (>50M) | REQ-BR-02 | EXISTS |
| TC-BR-03 | PO price = quotation price | REQ-BR-12 | EXISTS |
| TC-BR-04 | Receiving qty guard | REQ-BR-04 | EXISTS |
| TC-BR-10 | PO blocked when PR not APPROVED | REQ-BR-10 | TASK-020 |
| TC-BR-11-POS | Close PR when fully received | REQ-BR-11 | TASK-021 |
| TC-BR-11-NEG | Close PR blocked when not received | REQ-BR-11 | TASK-021 |
| TC-REJECT | Reject PR + release budget | REQ-FR-06 | TASK-022 |

### API Tests

| TC | Test | Req | Status |
|---|---|---|---|
| TC-API-01 | Health check | --- | EXISTS |
| TC-API-02 | Budget GET | REQ-FR-08 | EXISTS |
| TC-API-03 | AI standardize PR | REQ-FR-03 | EXISTS |
| TC-API-04 | Full 7-step workflow | CON-01 | EXISTS (gap) |
| TC-API-06 | PO when PR=PENDING -> 400 | REQ-BR-10 | TASK-020 |
| TC-API-07 | Close when not received -> 400 | REQ-BR-11 | TASK-021 |
| TC-API-08 | Reject PR -> 200 REJECTED | REQ-FR-06 | TASK-022 |

### Authorization Tests (HD-02=B only)

| TC | Test | Req |
|---|---|---|
| TC-AUTH-01 | No token -> 401 | REQ-NFR-02 |
| TC-AUTH-02 | EMPLOYEE approves -> 403 | REQ-NFR-02 |
| TC-AUTH-03 | PROCUREMENT approves -> 403 | REQ-NFR-02 |
| TC-AUTH-04 | MANAGER approves -> 200 | REQ-NFR-02 |

### Negative Tests

| TC | Test | Req |
|---|---|---|
| TC-NEG-01 | PR exceeds budget -> 400 | REQ-BR-01 |
| TC-NEG-02 | PO for unapproved PR -> 400 | REQ-BR-10 |
| TC-NEG-03 | Receive more than PO qty -> 400 | REQ-BR-04 |
| TC-NEG-04 | Close before receiving -> 400 | REQ-BR-11 |

### E2E Tests (Playwright)

| TC | Test | US |
|---|---|---|
| TC-E2E-01 | Create PO from approved PR (Happy path) | US-09 AC1, AC3 |
| TC-E2E-02 | Block PO for unapproved PR | US-09 AC2 |
| TC-E2E-03 | EMPLOYEE cannot access PO creation | US-09 / REQ-NFR-02 |

---

## 9. FINAL EVIDENCE CHECKLIST

### Git
- [ ] git log --oneline shows meaningful commit history with Task IDs
- [ ] Branch final-delivery contains all work
- [ ] Each feature/fix has own commit

### AI Evidence
- [ ] docs/ai-evidence/ directory exists with TEMPLATE.md
- [ ] Evidence document for each significant AI-assisted task
- [ ] Each document has: actual prompt, actual test output
- [ ] docs/logs/ai-usage-log.md has implementation phase entries (not empty)

### Test Execution
- [ ] pytest -v output file (actual, not fabricated)
- [ ] All claimed PASS have execution log
- [ ] TC-US09-001 Status = PASS (not NOT RUN)
- [ ] Test count in release-notes.md matches actual pytest output

### Screenshots
- [ ] Create PR with AI standardize
- [ ] Budget display (tempReserved, availableAmount)
- [ ] Manager approval + status change
- [ ] Quotation comparison with anomaly warning
- [ ] PO creation with price lock
- [ ] Receiving record
- [ ] Close PR + budget settlement

### API Evidence
- [ ] Swagger UI screenshot (/docs)
- [ ] Budget check rejection (HTTP 400 with detail)
- [ ] PR status check rejection for PO (HTTP 400)

### Auth/RBAC Evidence (if HD-02=B)
- [ ] Login response showing JWT structure
- [ ] 401 response without token
- [ ] 403 response for wrong role

### E2E Evidence
- [ ] npx playwright test output
- [ ] Playwright HTML report
- [ ] Screenshots at key steps

### Documentation
- [ ] runbook.md correct paths; followable
- [ ] release-notes.md verified claims only
- [ ] traceability-matrix.md covers all 11 US; no phantom refs

### Final
- [ ] FINAL_DELIVERY_BASELINE.md in git (DONE)
- [ ] FINAL_DEVELOPMENT_PLAN.md in git (this document)
- [ ] Post-delivery summary after all tasks complete

---

## 10. FINAL DEMO FLOW

Verified workflow (CON-01): Purchase Request -> Approve -> Collect Quotations -> Compare -> PO -> Receive -> Close

```
STEP 1 — Login / Role Setup
  [HD-02=B] Login: employee@company.com / password123
  [HD-02=A] Role selector: chon EMPLOYEE

STEP 2 — Employee: Create PR + AI Standardize (US-01)
  Input raw text: "Can mua 3 laptop Dell 25 trieu cho phong IT"
  Click "Chay AI Chuan Hoa PR"
  AI displays: title, items, estimated price (from API — after TASK-003)
  Budget Indicator shows available amount
  Click "Gui Yeu Cau PR & Kiem Tra Ngan Sach"
  PR created -> status = PENDING_MANAGER_APPROVAL
  Show: tempReservedAmount updated in budget card

STEP 3 — Show PR status tracking (US-02)
  PR list shows PENDING_MANAGER_APPROVAL badge

STEP 4 — Switch to Manager (US-03)
  [HD-02=B] Logout + login as manager@company.com
  [HD-02=A] Change dropdown to MANAGER
  PR list shows PR pending approval
  Click "Duyet PR Buoc 1 (Manager)"
  [PR <= 50M] -> status = APPROVED
  [PR > 50M] -> status = PENDING_FINANCE_APPROVAL (REQ-BR-02)

STEP 5 — Finance: Budget check + approve (US-04) [for >50M PRs]
  Finance sees PENDING_FINANCE_APPROVAL
  Budget display shows remaining amount
  Finance approves -> status = APPROVED

STEP 6 — Procurement: Quotation comparison (US-05..US-08)
  Switch to PROCUREMENT role
  PR shows APPROVED status
  Click "Trich Xuat Bao Gia PDF (AI)"
  AI displays 3 quotations in comparison table
  Show anomaly warning on high-price quotation (>=20%, REQ-FR-15)
  [If TASK-016A done] AI recommendation highlighted (REQ-FR-14)

STEP 7 — Procurement: Create PO (US-09)
  Procurement selects quotation (AI only recommends — REQ-BR-08)
  Click "Khoi tao Purchase Order"
  PO created -> status = PO_CREATED
  Show: PO price = Quotation price exactly (REQ-BR-12)
  [TASK-005 done] Demonstrate rejection when PR not APPROVED (BUG-001 fixed)

STEP 8 — Record Receiving (US-10)
  Record received qty = 3 (matching PO qty)
  Show: qty guard — cannot receive more than PO qty (REQ-BR-04)

STEP 9 — Finance: Close PR (US-11)
  [After HD-07 confirmed] Close PR
  Status -> CLOSED
  Show: budget settled (tempReservedAmount -> spentAmount)

STEP 10 — Security Demo (optional, HD-02=B)
  Show: 401 without token
  Show: 403 for wrong role
```

**Demo Prerequisites:**
- uv run fastapi dev app/main.py (port 8000)
- npm run dev (port 5173)
- [HD-01=B] docker compose up -d
- Browser: Chrome

---

## 11. FINAL DEFINITION OF DONE

### DoD — Per Task
1. Code change exists in file(s)
2. git diff reviewed by human team member
3. Test(s) written for the change
4. Tests executed with actual output
5. Output shows PASS (actual execution, not claimed)
6. AI evidence document created in docs/ai-evidence/
7. Committed with Task ID in commit message

### DoD — Per User Story (Must-have)
1. All ACs have corresponding implementation
2. At least 1 automated test per AC exists and PASSES
3. Test execution log exists (not just test file)
4. Traceability updated: REQ -> US -> Task -> Code -> Test -> Evidence
5. No OPEN critical bug blocks the AC
6. Human team member manually verified the feature

### DoD — Final Delivery

**Build**
- [ ] npm run build exits code 0 (TASK-002)
- [ ] uv run fastapi dev starts without errors
- [ ] GET /api/health returns accurate state (TASK-004)

**Business Logic (minimum requirements)**
- [ ] REQ-BR-01: Budget check blocks exceeding PR — test PASS
- [ ] REQ-BR-02: 2-level approval threshold — test PASS
- [ ] REQ-BR-10: PO blocked when PR not APPROVED — TC-US09-001 = PASS (not NOT RUN)
- [ ] REQ-BR-12: PO price = Quotation price — test PASS
- [ ] REQ-BR-04: Receiving qty guard — test PASS
- [ ] REQ-BR-11: Close PR requires receiving — test PASS (HD-07 confirmed first)

**Testing**
- [ ] All pytest tests PASS — execution log exists
- [ ] Test count >= 12 (8 existing + 4 new minimum)
- [ ] No test reports PASS without execution evidence
- [ ] TC-US09-001 Status = PASS in docs/qa/TEST_CASES_US09.md

**Demo Workflow**
- [ ] Full STEP 1-9 (Section 10) executes without error
- [ ] Screenshots exist for each major step

**Documentation**
- [ ] runbook.md correct paths; followable by another team member
- [ ] release-notes.md verified claims only; references actual test output
- [ ] traceability-matrix.md covers all 11 US; no phantom references
- [ ] ai-usage-log.md has implementation phase entries (not empty)
- [ ] At least 1 evidence document per significant coding task

**Git**
- [ ] final-delivery branch has meaningful commit history with Task IDs
- [ ] No secrets committed

**Human Decisions — All must be confirmed**
- [ ] HD-01 confirmed and implemented
- [ ] HD-02 confirmed and implemented
- [ ] HD-03 confirmed and implemented
- [ ] HD-04 confirmed: if A then TASK-005 done; if B then workaround documented
- [ ] HD-05 confirmed and implemented
- [ ] HD-06: COMPLETED
- [ ] HD-07 confirmed and implemented

---

*Tai lieu nay duoc tao sau khi doc toan bo source code, documentation, va FINAL_DELIVERY_BASELINE.md.*
*Khong co code nao duoc sua doi. Khong co Human Decision nao duoc tu chon boi AI.*

*Phien ban: v1.0 — 2026-09-16 — Branch: final-delivery*

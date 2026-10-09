# Course Deliverable Specification (Output_BaoCao)

This document is derived strictly from the course `Output_BaoCao.xlsx` source. It outlines the grading checklist, mandatory artifacts, and evidence requirements.

## 1. Course Output Overview

- **Source Sheet:** `Output_BaoCao`, `Lich_Bao_Cao`
- **Total Weights:** Bài 1 (10%), Bài 2 (30%), Bài cuối (60%).
- **Nature of Deliverables:** All listed deliverables are mandatory unless stated otherwise.
- **Reporting Format:** Each student reports exactly 2 times. 
  - Lần 1: Bài 1 + Bài 2 (5 phút/SV, 4 phút trình bày + 1 phút Q&A)
  - Lần 2: Bài cuối (5 phút/SV, 4 phút demo + 1 phút Q&A)

## 2. Mandatory Deliverables

The following artifacts are explicitly required in the "DANH SÁCH ARTIFACT PHẢI CÓ" section of `Output_BaoCao`.

**Bài 1 (10%)**
- 1.1 Project Charter (Mandatory)
- 1.2 User Research + Synthesis (Mandatory)
- 1.3 Requirements + Business Rules (Mandatory)
- 1.4 Project Vault (Mandatory)
- 1.5 Vault Q&A Benchmark (Mandatory)
- 1.6 AI Usage Log v1 (Mandatory)

**Bài 2 (30%)**
- 2.1 PRD (Mandatory)
- 2.2 User Flow (Mandatory)
- 2.3 Functional Prototype (Mandatory)
- 2.4 Usability Test (Mandatory)
- 2.5 User Stories + Acceptance Criteria (Mandatory)
- 2.6 Taiga Backlog (Mandatory)
- 2.7 Figma + Design System (Mandatory)
- 2.8 Architecture + ADR (Mandatory)
- 2.9 ERD / Data Model (Mandatory)
- 2.10 API Contract (Mandatory)
- 2.11 Story Specs + Traceability v1 (Mandatory)

**Bài cuối (60%)**
- 3.1 Source Repository (Mandatory)
- 3.2 Release chạy được (Mandatory)
- 3.3 Authentication + Authorization (Mandatory)
- 3.4 Business Workflow (Mandatory)
- 3.5 AI Feature (Mandatory)
- 3.6 Code Review Evidence (Mandatory)
- 3.7 Bug Log (Mandatory)
- 3.8 Automated Tests (Mandatory)
- 3.9 QA Report (Mandatory)
- 3.10 Security + NFR Evidence (Mandatory)
- 3.11 CI/CD + Docker/Deployment (Mandatory)
- 3.12 README + Runbook (Mandatory)
- 3.13 Release Notes + Changelog (Mandatory)
- 3.14 Traceability Final (Mandatory)
- 3.15 AI Usage Log Final + Retrospective (Mandatory)

## 3. Evidence Requirements

**General Rule:** "Không có evidence => xem như chưa hoàn thành, dù có slide mô tả." (Source: Output_BaoCao, Row 1).

**Items Requiring Actual Evidence:**
All 32 deliverables listed in Section 2 require actual evidence. "Slide mô tả" is not accepted as evidence. 

**Items That Cannot Be Claimed Complete Without Execution Evidence:**
- **3.2 Release chạy được:** **COMPLETE**
  - **Public Frontend URL:** `https://group-01-project.vercel.app`
  - **Public Backend URL:** `https://group-01-project-production.up.railway.app`
  - **Git Tag:** `v1.0.0-final` (`9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`)
  - **Release Evidence (AI-089 Public Smoke Test):**
    - Vercel frontend reachable (HTTP 200 OK, SPA asset loaded)
    - Railway backend reachable (HTTP 200 OK)
    - `/api/health` HTTP 200 OK (`status: ok`)
    - Supabase PostgreSQL connected (`PostgreSQL Connected (Prisma)`)
    - Authentication verified (Supabase Auth token -> `/api/auth/me` HTTP 200)
    - RBAC denied unauthorized actions (HTTP 401 unauthenticated, HTTP 403 employee approve PR)
    - Happy path verified (PR-2026-039 -> APPROVED -> quotation -> award -> PO -> receiving 1/1 -> CLOSED)
    - Failure path verified (Close before receiving complete -> HTTP 400 -> "Không thể đóng PR: Hàng chưa được nhận đủ")
    - Persistence verified (PR-2026-039 remains CLOSED in Supabase after re-fetch)
- **3.3 Authentication + Authorization:** "Demo allowed + denied action." (VERIFIED: `/api/auth/me` allowed; unauthenticated 401, employee approve 403 denied).
- **3.4 Business Workflow:** **VERIFIED**
  - **Happy Path:** PASS (Verified scenarios PASS: Full cycle PR Creation -> Manager Approval -> Sourcing Quotation -> Human Award & PO -> Receiving -> Close PR & Budget Settlement)
  - **Failure Path:** PASS (Verified failure guard: Close PR before receiving completion -> HTTP 400 blocked: "Không thể đóng PR: Hàng chưa được nhận đủ")
- 3.5 AI Feature: "Demo 2 case pass + 1 edge/fallback." (Advisory Fallback Heuristic active; Gemini Live unverified).
- 3.8 Automated Tests: "Chạy test hoặc mở CI pass." (133/133 backend pytest PASS, 14/14 browser E2E steps).
- 3.10 Security + NFR Evidence: "Demo unauthorized/invalid case."
- 3.11 CI/CD + Docker/Deployment: "Mở pipeline + deploy." (Railway deployment verified, Vercel frontend deployed).

## 4. AI Development Evidence

**Items Requiring AI Usage Log Evidence:**
- 1.6 AI Usage Log v1: Task, prompt/skill, input context, output, verification, correction.
- 3.15 AI Usage Log Final + Retrospective: Where AI was used, which outputs were corrected, risks, lessons.

**Other AI-Related Requirements:**
- 1.5 Vault Q&A Benchmark: >=20 questions. Must have expected answer/source and pass/fail record.
- 3.5 AI Feature: Business value, context, structured output, validation, fallback, eval set >=20. Not just a generic chatbot.

## 5. Requirements / User Stories / Acceptance Criteria

- **1.3 Requirements + Business Rules:** REQ-xxx format. Functional/non-functional; scope; business rules. Must be testable, non-contradictory.
- **2.1 PRD:** Problem, users, goals, scope, workflow, requirements, metrics. Must be consistent with requirements.
- **2.5 User Stories + Acceptance Criteria:** 8-12 stories; persona/goal/value; Given/When/Then. Stories must be small enough; AC must be testable.

## 6. Design / Figma / Prototype

- **2.2 User Flow:** Happy path + error/alternative path. Diagram walkthrough required.
- **2.3 Functional Prototype:** Prototype URL. Must click/run main workflow. Not just static screenshots.
- **2.4 Usability Test:** >=3 people/cases. Before/after changes required.
- **2.7 Figma + Design System:** Key screens, component states (default/hover/disabled/loading/error/empty), tokens, responsive rules, UX copy. 

## 7. Architecture / Database / API

- **2.8 Architecture + ADR:** Context/container, modules, integration, ADR for main choices. Do not over-engineer.
- **2.9 ERD / Data Model:** Entities, keys, relations, constraints, audit fields.
- **2.10 API Contract:** Endpoints, auth, request/response/error examples. Must match stories, model, and error handling.

## 8. Implementation / Code Review

- **3.1 Source Repository:** Code structure; branch/PR/commit; config example; migration/seed. No secrets.
- **2.11 Story Specs + Traceability v1:** Story -> AC -> screen/API/data -> task.
- **3.6 Code Review Evidence:** Checklist, blocker/major/minor, resolution. PR must link to story/task/test.

## 9. Testing / QA

- **3.7 Bug Log:** Severity, steps, expected/actual, evidence, owner, status. Bug must be reproducible.
- **3.8 Automated Tests:** Unit/integration/API/frontend/E2E appropriate; failure paths. Not just 200 OK.
- **3.9 QA Report:** Scope, environment, result, known issues, risk, sign-off. Release blockers = 0.

## 10. Security / NFR

- **3.3 Authentication + Authorization:** **COMPLETE** (Supabase Auth JWT ES256 JWKS verification via `jwt_service.py` with 5s timeout & fail-closed HTTP 401; Server-Side RBAC via `RoleChecker` covering 100% 19 endpoints; No Self-Approval GOV-01 guard; 100% verified via `test_jwt_auth.py` (12/12 PASS) & `test_rbac.py` (28/28 PASS), tổng 40/40 PASS tại [`docs/evidence/security-jwt-rbac-execution.txt`](file:///d:/LTUD/group-01-project-main/docs/evidence/security-jwt-rbac-execution.txt); Chi tiết tại `docs/07-release/security-nfr.md`).
- **3.10 Security + NFR Evidence:** **COMPLETE** (Hồ sơ an ninh và kiểm thử phi chức năng hoàn chỉnh tại `docs/07-release/security-nfr.md`: Xác thực JWT & Server-side RBAC 19 endpoints 40/40 PASS, No Self-Approval GOV-01, PO creation guard REQ-BR-10 với khóa cứng giá/lượng, Receiving completion guard REQ-BR-11, Budget reservation/settlement guard; Pydantic V2 input validation fail-fast 422; Phòng chống SQL injection ở tầng ứng dụng qua Prisma ORM parameterized queries + Pydantic V2 [không thực thi penetration fuzz test riêng]; Đã quét các file hiện tại bằng `git grep` 0 secret leaks [101 matches an toàn, 0 real secrets/private keys], `.gitignore` & `.env.example` sanitization; Frontend `npm audit --omit=dev` 0 vulnerabilities trên 74 packages; Backend `pip-audit` sau khi nâng cấp PyJWT 2.14.0 lên 2.15.1 đạt 0 lỗ hổng đã biết [exit code 0, evidence: `docs/evidence/python-pip-audit-remediation.txt`]; Đo lường hiệu năng: Vite build 12.43s, bundle gzip 181.79 kB, Railway `/api/health` 1.08s, Vercel frontend 0.78s [FCP/LCP Core Web Vitals chưa đo lường]; A11y baseline đạt chuẩn biểu mẫu/HTML ngữ nghĩa [kiểm thử tự động WCAG 2.1 AA chưa thực thi — SEC-005 limitation]; Logging tập trung 0 stack trace/secret leak; Docker `python:3.11-slim` tối giản [root user — SEC-004 limitation]; AI Advisory-only boundary với deterministic heuristic fallback 78% confidence, 0 autonomous PO creation [Gemini Live duy trì UNVERIFIED]; Sổ bộ khuyết tật SEC-001..SEC-007; Bộ kiểm thử an ninh và nghiệp vụ cốt lõi Pytest 85/85 PASS trong 252.75s; Đồng ký duyệt: Nguyễn Thị Thùy Dung - GOV-01 & Trần Thị Thu Hà - GOV-02).

## 11. CI/CD / Docker / Deployment

- **3.2 Release chạy được:** **COMPLETE** (Public URLs: Frontend `https://group-01-project.vercel.app`, Backend `https://group-01-project-production.up.railway.app` + Git Tag `v1.0.0-final` -> `9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`. Verified end-to-end via AI-089 Public Smoke Test).
- **3.11 CI/CD + Docker/Deployment:** **COMPLETE** (GitHub Actions `.github/workflows/ci.yml` multi-job CI pipeline: `backend-test` with PostgreSQL 16 Service Container + `frontend-build`; Docker packaging in `backend/Dockerfile` & `compose.yaml`; Báo cáo kiểm chứng tại `docs/evidence/CI_CD_PIPELINE_REPORT.md`).
- **3.13 Release Notes + Changelog:** Version, scope, features, fixes, known issues, upgrade notes. Matches v1.0.0-final.

## 12. Traceability

- **2.11 Story Specs + Traceability v1:** Trace 1 REQ end-to-end. No "orphan" stories.
- **3.14 Traceability Final:** REQ -> Story -> Task -> Design/API -> Commit/PR -> Test -> Status. 100% of "Done" scope must be traceable.

## 13. Final Report

- **3.12 README + Runbook:** Setup, env, seed, run, test, deploy, rollback/troubleshooting. Must allow another student to run it without implicit knowledge.
- *Status Report:* Mentioned in `Phuong_Phap_Tool` sheet as "Status report: Tóm tắt Done/Next/Risk/Decision/Blocker có link evidence."

## 14. Individual Viva Evidence

**Items Requiring Individual Student Evidence:**
- **Lần 1 (Bài 1 + Bài 2):** "Mở artifact thật. Chỉ ra: phần mình làm -> evidence -> 1 REQ -> Story -> Prototype/Figma/Spec/Task." (100% cá nhân).
- **Lần 2 (Bài cuối):** "Demo 1 story end-to-end trên release; mở commit/PR, test, traceability; nêu AI đã giúp gì và 1 output AI phải sửa."
- **1.6 AI Usage Log v1:** "Mỗi SV chỉ ra >=1 lần AI sai/được sửa."
- **2.5 User Stories:** "Mỗi SV giải thích story mình sở hữu."
- **3.1 Source Repository:** "Mỗi SV mở commit/PR mình làm."
- **3.12 README + Runbook:** "Một SV khác đọc và giải thích cách chạy."

## 15. Definition of Done / Completion Conditions

"Sinh viên dùng sheet này như Definition of Done. Không có evidence => xem như chưa hoàn thành, dù có slide mô tả." 
All items in the checklist act as the DoD for the project's phases.

## Source Integrity Notes

- This document was extracted entirely from `docs/source/Output_BaoCao.xlsx` (including sheets `Output_BaoCao`, `Lich_Bao_Cao`, `Phuong_Phap_Tool`).
- Information about specific grading percentages, evidence constraints, and item IDs were directly transcribed from the source.
- *Ambiguity Note:* The source specifies "critical-path E2E tests" in the Rubric and Phuong_Phap_Tool, but the main checklist generically mentions "Automated Tests (tests/) Unit/integration/API/frontend/E2E phù hợp; failure path." - SOURCE DOES NOT SPECIFY the exact count or ratio of these tests, only that they must be "phù hợp" (appropriate) and cover failure paths.
- *Ambiguity Note:* "AI Feature" mentions "eval set >=20", but SOURCE DOES NOT SPECIFY the exact format of the evaluation dataset (only that it requires 2 passing cases and 1 edge/fallback for the demo).

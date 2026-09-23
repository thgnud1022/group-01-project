# Project Decision Log
**Project:** AI Procurement & Purchase Approval System  
**Course:** Thực hành lập trình ứng dụng trong doanh nghiệp bằng AI  
**Group:** Group 01 · Branch: `final-delivery`  
**Date:** 2026-09-20  

This log records the authoritative architectural and business decisions for the Final Delivery phase. These decisions freeze the technical direction and resolve ambiguities identified during the cross-source validation phase.

---

## HD-01: Target Database Architecture

- **ID:** HD-01
- **Title:** Migrate from MockDB to Supabase PostgreSQL
- **Status:** **DECIDED**
- **Decision:** The project will use Supabase PostgreSQL as the real production database (mandatory decision), replacing the current in-memory `MockDatabase` python dictionary. The use of Prisma is NOT mandatory yet; its compatibility with the deployment target must be verified first.
- **Decision type:** Architecture
- **Requirement/source:** REQ-NFR-01 (Data consistency), ADR-002, HD Review Context.
- **Reason:** In-memory mock database loses all data upon server restart, which completely fails the persistence and consistency requirements for an enterprise application.
- **Alternatives considered:** Keep MockDB (rejected due to data loss); Use SQLite (rejected as target deployment requires a serverless-compatible DB).
- **Consequences:** Backend data access layer must be updated. Environment variables for DB connection are now mandatory.
- **Implementation implications:** Requires Supabase project setup, migration execution, and backend refactoring. Prisma compatibility must be verified before proceeding with it. Existing unit tests targeting MockDB must be updated or supplemented with real DB integration tests.
- **Verification/evidence required:** Application correctly reads/writes to Supabase DB. Data persists across server restarts. `test_all_endpoints.py` logic passes against the real DB.
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-02: Authentication and Authorization Mechanism

- **ID:** HD-02
- **Title:** Implement Supabase Auth with JWT and Server-Side RBAC
- **Status:** **DECIDED**
- **Decision:** The project will use Supabase Auth. Authentication flow will be: `Verified JWT → user_id → application profile/database → role → RBAC`. The backend must verify the JWT, extract the verified `user_id`, resolve the application role from the application profile/database, and enforce RBAC server-side. Custom JWT claims are only to be used if clearly configured and verified. The backend MUST NOT trust any role sent by the client in the request body. The frontend role dropdown is strictly for UI state.
- **Decision type:** Security / Architecture
- **Requirement/source:** REQ-NFR-02 (Role separation), CON-02.
- **Reason:** The current implementation trusts client-provided payloads (e.g., `approverRole`) implicitly and returns fake JWTs. This is a critical security vulnerability that invalidates the entire approval workflow.
- **Alternatives considered:** Custom JWT signing (rejected to leverage Supabase Auth's robustness); Keep mock auth (rejected due to critical security failure).
- **Consequences:** Frontend must implement real login using Supabase JS SDK. All backend protected routes must add JWT verification middleware and role extraction flow.
- **Implementation implications:** Requires Supabase Auth configuration. Backend must implement the auth flow to resolve the role before processing business logic.
- **Verification/evidence required:** Requests without valid JWTs are rejected (401). Requests by users lacking required roles (e.g., EMPLOYEE trying to approve PR) are rejected (403).
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-03: AI Implementation Strategy

- **ID:** HD-03
- **Title:** Hybrid AI Architecture (LLM + Deterministic Backend Validation)
- **Status:** **DECIDED**
- **Decision:** Use a real LLM API (e.g., Gemini or OpenAI) for language tasks (extraction, comparative analysis, anomaly explanation) while keeping the backend as the absolute authority for business decisions (prices, permissions, status changes).
- **Decision type:** Architecture / Feature Implementation
- **Requirement/source:** REQ-FR-13 (Must), REQ-FR-14, REQ-FR-15, ASM-07, CON-03.
- **Reason:** The current regex-only implementation with hardcoded prices fails to meet the project's requirements for dynamic analysis and recommendation, and cannot extract information from actual quotation files.
- **Alternatives considered:** Keep Regex only (rejected as insufficient for Must requirements); Let LLM write to DB directly (rejected due to security and reliability risks).
- **Consequences:** Requires API key and integration. LLM responses must be strictly validated (e.g., using Pydantic schemas) before use. A fallback to regex should be maintained in case of API failure.
- **Implementation implications:** Refactor `ai_service.py` to make external HTTP calls. Implement file parsing to extract text from Quotation files before sending to LLM.
- **Verification/evidence required:** AI can analyze arbitrary Quotation text/files, not just hardcoded keywords. LLM suggestions do not bypass backend authorization or data constraints.
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-04: Purchase Order Creation Guard

- **ID:** HD-04
- **Title:** Enforce PR "APPROVED" Status for PO Creation (Fix BUG-001)
- **Status:** **REQUIREMENT-MANDATED / MUST FIX**
- **Decision:** A Purchase Order MUST NOT be created unless the related Purchase Request has `status == APPROVED`.
- **Decision type:** Business Rule Implementation
- **Requirement/source:** REQ-BR-10, US-09 AC2.
- **Reason:** This is an explicit, documented business requirement that is currently missing from the code (BUG-001). It is not a subjective preference but a critical defect fix.
- **Alternatives considered:** None. Breaking the business rule is not an option.
- **Consequences:** Any attempt to create a PO from a DRAFT, PENDING_MANAGER_APPROVAL, or PENDING_FINANCE_APPROVAL PR will result in a clear error and rejection.
- **Implementation implications:** Add a guard condition in `create_po()` inside `procurement_service.py`.
- **Verification/evidence required:** Unit test explicitly validating that PO creation is blocked for non-APPROVED PRs.
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-05: Critical-Path E2E Testing Strategy

- **ID:** HD-05
- **Title:** Implement Real Critical-Path E2E Tests via Playwright Matching Target Frontend
- **Status:** **DECIDED**
- **Decision:** E2E testing must match the final, stable frontend architecture. The frontend should be refactored/rebuilt only where required, preserving reusable code (do not blindly rewrite the entire frontend). The current Playwright files are deemed unexecutable documentation.
- **Decision type:** Quality Assurance
- **Requirement/source:** Course Requirement (Section 15.1, Task 4: "Tự động hóa critical path E2E").
- **Reason:** The course explicitly requires automated E2E for the critical path (6/42 points). The current specs query DOM elements that do not exist in the single-page `App.tsx`.
- **Alternatives considered:** Sửa test cho khớp `App.tsx` (rejected as App.tsx needs refactoring anyway); Bỏ qua E2E (rejected as it loses course rubric points).
- **Consequences:** Frontend must be refactored with stable routes and test IDs before E2E can be finalized.
- **Implementation implications:** Install Playwright properly. Define standard flows (PR Create, Approve, PO, Receive). Ensure database seeding allows tests to run predictably.
- **Verification/evidence required:** Playwright HTML report showing passes for at least the core flows (e.g., US-01, US-03, US-09).
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-06: Git Repository Setup

- **ID:** HD-06
- **Title:** Git Initialization and Branching
- **Status:** **DONE**
- **Decision:** The repository is actively tracked in Git on the `final-delivery` branch.
- **Decision type:** Infrastructure
- **Requirement/source:** Standard development practices.
- **Reason:** Confirmed via `git status` and `git branch` (proving local Git state). Note: This evidence only proves local Git initialization and branching, it does not prove GitHub remote push or CI/CD state unless further evidence exists.
- **Alternatives considered:** N/A
- **Consequences:** All future work must be committed to this repository.
- **Implementation implications:** None remaining for setup.
- **Verification/evidence required:** Git history (`git log`).
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-07: "Receiving Complete" Definition for PR Closing

- **ID:** HD-07
- **Title:** Technical Definition of Receiving Completion
- **Status:** **DECIDED**
- **Decision:** "Receiving complete" is technically defined as: `SUM(receivedQty of all related Receiving records) >= PurchaseOrder.quantity`. Closing a PR requires this condition to be met. (Note - CURRENT STATE: `PurchaseOrder.quantity` currently DOES NOT EXIST in the Prisma schema. TARGET STATE: `PurchaseOrder.quantity` is a data-model requirement that MUST be added during implementation/migration to support this HD-07 business rule.)
- **Decision type:** Business Rule Definition
- **Requirement/source:** REQ-BR-11, US-11 AC1, US-11 AC2, ASM-06.
- **Reason:** The requirement mandates that Receiving must be complete before closing. Using the sum of received quantities against the PO ordered quantity provides a deterministic, database-verifiable condition without needing to introduce new PO status enums.
- **Alternatives considered:** Require a specific `PO.status == RECEIVED` (rejected to minimize schema changes); Any single Receiving record (rejected as it ignores partial deliveries).
- **Consequences:** `close_pr()` will query Receiving records, sum their quantities, and reject the closure if the sum is less than the PO quantity.
- **Implementation implications:** Refactor `close_pr()` in `procurement_service.py` to implement this aggregation and validation.
- **Verification/evidence required:** Unit tests demonstrating that `close_pr()` succeeds when sum(qty) >= PO.qty, and fails otherwise.
- **Date:** 2026-09-20
- **Owner:** Group 01

---

## HD-08: Authoritative Server-Side Source for PO Quantity (T-094 Data Model Gap)

- **ID:** HD-08
- **Title:** Authoritative Server-Side Source for PO Quantity (Resolve T-094 Data Model Gap)
- **Status:** **DECIDED**
- **Decision:** Human has formally selected **Option A — Add `Quotation.quantity Int`**. The field `Quotation.quantity` will serve as the authoritative server-side source of truth for `PurchaseOrder.quantity`.
- **Decision type:** Data Model Architecture & Business Rule Implementation
- **Requirement/source:** T-094 (Backlog), REQ-BR-12 (Server-side quotation resolution), REQ-BR-03 (Price lock), US-09 AC3, HD Review / Human Decision Brief (`docs/HUMAN_DECISION_T094_QUANTITY.md`).
- **Reason:** 
  1. `PurchaseOrder.quantity` was added in TASK-002 as a `NOT NULL` integer column in PostgreSQL to support downstream Receiving validation (HD-07 / US-10) and PR closing (US-11).
  2. However, the model `Quotation` in the initial Prisma schema only contained `totalAmount` and lacked a `quantity` field, creating a Data Model Gap where `T-094` ("ensure PO price and quantity match quotation") could not be resolved server-side without a direct quotation source.
  3. Client payloads cannot be trusted for commercial data (REQ-BR-12), and guessing `quantity = 1` or arbitrarily pulling from an entity not specified by T-094 is strictly prohibited.
  4. Option A provides a direct 1:1 authoritative mapping from `Quotation.quantity` to `PurchaseOrder.quantity`, ensures clear traceability for academic evaluation and Viva defense, avoids client-side tampering, and avoids the extreme timeline risks of a full line-items redesign (Option C).
- **Scope Boundary:** This decision solely determines that `Quotation.quantity` will be added and used as the authoritative server-side data source for `PurchaseOrder.quantity`. Whether a default value (e.g. `@default(1)`) is configured in the schema will be decided during implementation based on quotation ingestion flows and requirement specifications, and is NOT mandated as a fixed business rule at this stage.
- **Alternatives considered:**
  - *Option B (Derive quantity from `PRItem.quantity`)*: Rejected by Human in favor of direct quotation traceability under T-094.
  - *Option C (Full redesign with `QuotationItem` line items)*: Rejected due to prohibitive timeline and complexity risk before project submission.
- **Consequences:**
  - Prisma schema will need `quantity Int` added to model `Quotation` in the next implementation step.
  - Database synchronization (`prisma db push`) will be required in that step.
  - `ProcurementService.create_po()` will map `PO.quantity = quotation.quantity` server-side.
  - Test suites and quotation extraction/comparison flows will supply/verify `Quotation.quantity`.
- **Implementation implications:** Implementation is deferred to the next approved implementation task. No schema or code changes are performed in this decision-recording step.
- **Verification/evidence required:** Updated Decision Log (`docs/DECISION_LOG.md`), updated Human Decision Brief (`docs/HUMAN_DECISION_T094_QUANTITY.md`), and updated AI Usage Log (`AI-028`).
- **Date:** 2026-09-21
- **Owner:** Group 01

---

## HD-REQ-05: Seed Data Credentials & Password Hashing Strategy

- **ID:** HD-REQ-05
- **Title:** Seed Data Credentials & Password Hashing Strategy for Demo Accounts
- **Status:** **APPROVED — Option A**
- **Decision:** Human has formally selected **Option A — Keep demo password "password123", store ONLY bcrypt hash in `User.passwordHash`, NO plaintext in database**.
  - Demo password `"password123"` is used for the 5 sample accounts across roles (`employee`, `manager`, `procurement`, `finance`, `admin`).
  - Only the bcrypt hash of `"password123"` is written into the `User.passwordHash` column in PostgreSQL.
  - Plaintext password is NEVER persisted in the database.
  - These credentials are strictly designated for development, demonstration, and automated test environments for this academic project, not production credentials.
  - Preserves compatibility with the existing Runbook (`docs/07-release/runbook.md`) and pre-aligns with TASK-004 JWT/Bcrypt authentication.
- **Decision type:** Security / Data Seeding Architecture
- **Requirement/source:** REQ-NFR-02 (Authentication & Role Separation), `docs/05-technical/data-model.md` (bcrypt specification), `backend/prisma/schema.prisma` (`User.passwordHash String`), `docs/07-release/runbook.md` (role credentials).
- **Reason:**
  1. The Runbook already specifies demo password `"password123"` for the 5 sample accounts.
  2. Prisma `User` schema mandates `passwordHash String` as `NOT NULL`, and `data-model.md` explicitly specifies bcrypt hashing.
  3. Storing only the bcrypt hash complies with database constraints, avoids plain-text exposure risks, maintains 100% backward compatibility with documented team testing procedures, and avoids unnecessary churn.
- **Alternatives considered:**
  - *Option B (Generate random credentials per environment)*: Rejected because it breaks Runbook instructions, complicates manual demo and Viva defense, and introduces secret-management overhead for an academic course project.
  - *Option C (Bypass passwordHash / nullable)*: Rejected because it violates the existing Prisma schema, requires altering database schema, and introduces security gaps.
- **Consequences:**
  - Database seed script (when implemented in STEP 2B) will use `bcrypt` (or `passlib`) to generate the bcrypt hash for `"password123"` before inserting `User` records.
  - No schema changes or migration required.
  - Zero plaintext passwords in database tables.
- **Implementation implications:** Implementation is deferred to STEP 2B (Seed Data Implementation). No seed scripts are created or executed in this step.
- **Verification/evidence required:** Seeded records in Supabase `User` table have valid bcrypt hashes (`$2b$...` or `$2a$...`) in `passwordHash`; auth verification in TASK-004 verifies passwords via `bcrypt.checkpw()`.
- **Date:** 2026-09-22
- **Owner:** Group 01

---

## HD-REQ-06: Initial Budget Period Convention

- **ID:** HD-REQ-06
- **Title:** Initial Budget Period Convention for Database Seeding
- **Status:** **APPROVED — Option A**
- **Decision:** Human has formally selected **Option A — Initial Budget Period: `fiscalYear = 2026`, `quarter = 1`**.
  - Initial budget records seeded for `DEPT-IT` and `DEPT-HR` will use `fiscalYear = 2026` and `quarter = 1`.
  - Supporting evidence: The year `2026` is supported by project naming conventions `PR-2026-xxx` and `PO-2026-xxx`.
  - Quarter 1 is a Human-approved technical convention for initial seed data and integration testing.
  - **IMPORTANT BOUNDARY:** Quarter 1 MUST NOT be described or documented as a confirmed business requirement or enterprise policy. It is strictly a technical seeding convention.
- **Decision type:** Data Seeding / Technical Convention
- **Requirement/source:** `backend/prisma/schema.prisma` (`Budget` model unique constraint `@@unique([departmentId, fiscalYear, quarter])`), PR/PO ID conventions (`PR-2026-xxx`), `docs/01-business/company-policies.md`.
- **Reason:**
  1. The Prisma `Budget` model requires `fiscalYear Int` and `quarter Int` with a composite unique constraint `[departmentId, fiscalYear, quarter]`.
  2. In-memory `MockDatabase` only keyed budgets by department ID (`DEPT-IT`, `DEPT-HR`) without explicit period columns.
  3. A concrete period is required to seed the database and support initial migration and integration tests.
  4. 2026 aligns with established ID conventions, and Q1 provides a consistent initial period.
- **Alternatives considered:**
  - *Option B (Dynamic current year/quarter)*: Rejected because non-deterministic periods make integration tests brittle across quarter boundaries and complicate assertions.
  - *Option C (Full multi-period seed Q1-Q4)*: Rejected to avoid cluttering initial database state with unnecessary test data before basic CRUD is wired.
- **Consequences:**
  - Seed records for `Budget` will populate `fiscalYear = 2026, quarter = 1` for `DEPT-IT` and `DEPT-HR`.
  - `procurement_service.py` budget check refactoring (in later TASK-003 steps) must take `fiscalYear=2026, quarter=1` into account for budget resolution.
  - No schema changes required.
- **Implementation implications:** Implementation is deferred to STEP 2B (Seed Data Implementation). No seed scripts are created or executed in this step.
- **Verification/evidence required:** `Budget` table in Supabase contains rows for `DEPT-IT` and `DEPT-HR` with `fiscal_year = 2026` and `quarter = 1`.
- **Date:** 2026-09-22
- **Owner:** Group 01

---

## HD-REQ-07: User Identifier Resolution in PR & Approval APIs

- **ID:** HD-REQ-07
- **Title:** Server-side Email → User.id Resolution for PR and Approval Entities
- **Status:** **APPROVED — Server-side Email → User.id Resolution**
- **Decision:** In the transition phase prior to TASK-004 (JWT Authentication):
  - Current APIs may continue receiving user identifiers as email addresses (e.g. `employee@company.com`) to maintain 100% backward compatibility with existing API contracts and test suites.
  - The backend/service layer must resolve `User.email → User.id` (UUID in PostgreSQL) before writing to `PurchaseRequest.creatorId` and `Approval.approverId`.
  - The database foreign key columns in PostgreSQL MUST strictly store `User.id` (UUID), NEVER email strings.
  - **CRITICAL RULE:** `approverRole` and `approverName` are NOT database identities. The system MUST NOT use `approverRole → User.id` or `approverName → User.id` as a primary identity mechanism. Role is exclusively used for authorization and business-rule enforcement (`User.email → User.id` for identity, `User.role` for authorization). If an API only provides role/name without a unique identifier, this must remain flagged as a finding without fabricating pseudo-identities.
- **Scope & Limitations:** This is a temporary compatibility decision for the migration phase prior to TASK-004. Once TASK-004 (Real JWT Auth) is implemented, user identity will be extracted securely server-side from verified JWT claims rather than client request bodies.
- **Decision type:** Data Architecture / Identity & Security
- **Requirement/source:** `backend/prisma/schema.prisma` (`PurchaseRequest.creatorId` and `Approval.approverId` reference `User(id)`), REQ-NFR-02 (Role & Identity Separation).
- **Reason:**
  1. Prisma schema mandates foreign keys `PurchaseRequest.creatorId → User.id` and `Approval.approverId → User.id`.
  2. Current API clients send email strings.
  3. `User.email` is `@unique` in the database and seeded, allowing clean server-side lookup without altering client contracts or breaking existing regression suites.
- **Alternatives considered:**
  - *Option B (Require client to send UUID)*: Rejected as it breaks all frontend forms and existing test payloads immediately before authentication is wired.
- **Consequences:**
  - Service methods creating PRs or Approvals in STEP 3B will look up `User` by email to obtain the UUID.
  - Zero raw email strings in PostgreSQL foreign key columns.
- **Date:** 2026-09-22
- **Owner:** Group 01

---

## HD-REQ-08: Active Budget Period Resolution Strategy

- **ID:** HD-REQ-08
- **Title:** Active Budget Period Technical Convention for PR Creation & Budget Resolution
- **Status:** **APPROVED — 2026 Q1 Active Budget Period Technical Convention**
- **Decision:** In the current phase of the project:
  - `fiscalYear = 2026` and `quarter = 1` is used as the **active budget period convention** for runtime budget resolution in the procurement flow.
  - When the backend needs to resolve or verify a Department's budget during PR creation or budget query, it resolves by: `departmentId` + `fiscalYear = 2026` + `quarter = 1`.
  - **CRITICAL BOUNDARY:** `2026 Q1` is a **Human-approved technical convention for the current course project / demo / integration environment**. It is NOT a business requirement, company policy, or permanent production rule. Documentation MUST NOT state that business policy mandates 2026 Q1.
- **Scope & Future Boundary:**
  - Strictly limited to initial seeding, integration tests, and runtime resolution in the course project environment.
  - Does NOT hardcode 2026 Q1 as an immutable business rule across future production deployments. Future phases supporting multiple periods will determine the active period via configuration or business context.
- **Decision type:** Data Architecture / Technical Convention
- **Requirement/source:** `backend/prisma/schema.prisma` (`Budget` composite unique `[departmentId, fiscalYear, quarter]`), HD-REQ-06, REQ-BR-01.
- **Reason:**
  1. The API `POST /api/pr` currently only submits `departmentId`.
  2. Prisma `Budget` requires `[departmentId, fiscalYear, quarter]`.
  3. Database is already seeded with 2026 Q1 per HD-REQ-06.
  4. Resolving to 2026 Q1 avoids expanding API contract scope prematurely while enabling real DB budget checking in STEP 3B.
- **Alternatives considered:**
  - *Option B (Require client to pass fiscalYear & quarter in CreatePRSchema)*: Rejected to avoid scope creep and breaking existing API contracts.
- **Consequences:**
  - `ProcurementService.get_budget(dept_id)` and `create_pr()` in STEP 3B will query `Budget` using `departmentId_fiscalYear_quarter` with `(dept_id, 2026, 1)`.
- **Date:** 2026-09-22
- **Owner:** Group 01

---

## HD-REQ-09: Approver Identity Resolution for PR Approval API

- **ID:** HD-REQ-09
- **Title:** Mandatory `approverEmail` in `ApprovePRSchema` and Server-side Identity & Role Resolution
- **Status:** **APPROVED — OPTION B**
- **Decision:** Human has formally selected **Option B — Approver Email Bắt Buộc**.
  1. `ApprovePRSchema` must require `approverEmail: str` (REQUIRED) and `comments: Optional[str] = "Phê duyệt PR"`.
  2. `approverRole` and `approverName` are strictly NOT database identities and must not be used as identity mechanisms.
  3. The backend resolves `approverEmail → User.id` (UUID) via server-side database lookup.
  4. `Approval.approverId` in PostgreSQL must strictly store `User.id` (UUID).
  5. Role authorization must be checked against `User.role` retrieved from the database, never trusting role strings sent by the client.
  6. NO fallback mapping from role to hardcoded demo users (e.g. `MANAGER → manager@company.com`) is permitted.
  7. Legacy tests and client payloads that previously sent `approverRole` and `approverName` will be updated to send `approverEmail`.
- **Decision type:** Security / Data Architecture / API Contract
- **Requirement/source:** `backend/prisma/schema.prisma` (`Approval.approverId` references `User(id)`), HD-REQ-07, REQ-NFR-02 (Role Separation).
- **Reason:**
  1. Approvers must have a unique identity to populate the mandatory foreign key `Approval.approverId`.
  2. Role and name are insufficient to identify a specific individual in an enterprise audit trail.
  3. Prohibiting hardcoded role-to-demo-user fallback adheres to strict identity integrity principles and prepares directly for TASK-004 JWT authentication.
- **Scope & Limitations:**
  - Governs API identity and migration compatibility for PR approval.
  - Does not change the business approval threshold (> 50,000,000 VND).
  - Does not alter Manager/Finance/Admin approval permissions.
- **Alternatives considered:**
  - *Option A (Optional approverEmail with fallback mapping role to demo users)*: Rejected by Human to preserve strict identity integrity and avoid fabricating identities.
- **Consequences:**
  - `ApprovePRSchema` is updated to require `approverEmail: str`.
  - Service layer resolves `approverEmail → User` row in PostgreSQL and enforces `user.role`.
  - Test suites are updated to pass valid approver emails (e.g. `manager@company.com`, `finance@company.com`).
- **Date:** 2026-09-22
- **Owner:** Group 01

---

## HD-REQ-10: Approval Status Guard

- **ID:** HD-REQ-10
- **Title:** Enforce Valid PR Status Guard for PR Approval (`approve_pr`)
- **Status:** **APPROVED**
- **Decision:** The `approve_pr` operation is ONLY permitted when the `PurchaseRequest` is currently in one of the following pending statuses:
  - `PENDING_MANAGER_APPROVAL`
  or
  - `PENDING_FINANCE_APPROVAL`
  
  If the Purchase Request is in any other status, the approval request MUST be rejected (raising `ValueError`). Specifically:
  - `APPROVED` → REJECT
  - `REJECTED` → REJECT
  - `PO_CREATED` → REJECT
  - `CLOSED` → REJECT
- **Decision type:** Business Rule Implementation / State Machine Integrity
- **Requirement/source:** REQ-BR-02, REQ-FR-06, REQ-FR-07, US-03 AC2/AC4.
- **Reason:**
  1. Prevents duplicate approvals on already approved PRs.
  2. Prevents illegal status transitions or creating invalid `Approval` records when a PR has already progressed past the pending approval phase.
  3. Protects state machine integrity and database audit trails.
- **Scope & Limitations:**
  - Protects PR lifecycle state machine.
  - Does not modify the threshold (> 50,000,000 VND).
  - Does not alter Manager → Finance sequence or Admin privileges.
- **Alternatives considered:**
  - *Permit re-approval (Current MockDB behavior)*: Rejected because it corrupts audit history and violates lifecycle state machine rules.
- **Consequences:**
  - `ProcurementService.approve_pr_prisma()` will validate that current `pr.status` is in `[PENDING_MANAGER_APPROVAL, PENDING_FINANCE_APPROVAL]` before proceeding.
  - Integration tests will verify that re-approving an `APPROVED` PR is blocked.
- **Date:** 2026-09-22
- **Owner:** Group 01

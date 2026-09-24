# AI USAGE TRACEABILITY MATRIX

**Project:** AI Procurement & Purchase Approval System (Group 01)<br>
**Branch:** `final-delivery`<br>
**Ngày cập nhật:** 2026-09-23

---

## 1. Nguyên tắc thiết lập Traceability

Bảng ma trận truy xuất nguồn gốc hai chiều kết nối xuyên suốt chuỗi:
$$\text{AI Activity} \longrightarrow \text{Artifact} \longrightarrow \text{User Story} \longrightarrow \text{T-xxx (Business)} \longrightarrow \text{TASK-xxx (Technical)} \longrightarrow \text{Code Module} \longrightarrow \text{Automated Test} \longrightarrow \text{Evidence} \longrightarrow \text{Git Commit}$$

### Quy ước định danh:
- **`T-xxx`:** Business / User Story Task quy định trong Project Backlog (ví dụ: `T-011`..`T-111` trong Backlog chính, hoặc `T-01`..`T-42` trong Backlog sơ khởi).
- **`TASK-xxx`:** Technical Implementation Task do nhóm kiến trúc kỹ thuật quy hoạch (`TASK-001` đến `TASK-018`).
- **`AI-xxx`:** Phiên làm việc có sự hỗ trợ của AI (AI Usage Session).
- Khi một mắt xích chưa được triển khai hoặc thiếu căn cứ thực nghiệm, ghi nhận chính xác: **`MISSING EVIDENCE`** hoặc **`NOT STARTED`**. Tuyệt đối không tự suy diễn.

---

## 2. Ma trận Traceability chi tiết

### Phần A: Early Phase (Khám phá, Phân tích & Đặc tả Yêu cầu)

| AI Activity ID | Artifact tạo/sửa | User Story liên quan | T-xxx (Business Task) | TASK-xxx (Technical) | Code / Config | Test Suite | Evidence | Git Commit |
|:---:|---|---|---|---|---|---|---|:---:|
| **AI-001 (Early)** | `1.project-charter.md` | Core System Scope | N/A (Project Inception) | N/A | Markdown Doc | Human Review | Problem Statement, Metrics 85%/80%/75% | Historical |
| **AI-002 (Early)** | `2.user-research.md` | Core System Scope | N/A (Research) | N/A | Markdown Doc | Human Review | 8 Evidence items (E-01..E-08) | Historical |
| **AI-003 (Early)** | `2.user-research.md` (chuẩn hóa) | Core System Scope | N/A (Research) | N/A | Markdown Doc | Human Review | Cấu trúc 11 mục mẫu MIS3032 | Historical |
| **AI-004 (Early)** | `requirements.md` | All Stories (US-01..US-11) | N/A (Requirement Inventory) | N/A | Markdown Doc | Traceability check | Danh mục FR-01..18, BR-01..11 | Historical |
| **AI-005 (Early)** | `3.personas-and-jtbd.md` | US-01..US-10 | N/A (Persona analysis) | N/A | Markdown Doc | Human Review | 5 Personas & JTBD | Historical |
| **AI-006 (Early)** | `7.MVP-Scope.md` | All Stories | N/A (Scope) | N/A | Markdown Doc | Human Review | Bảng Must/Should/Could | Historical |
| **AI-013..019 (Early)**| `docs/02-vault/*` | Vault Governance | N/A (Governance) | N/A | Markdown Doc | Benchmark QA-01..04 | Vault Index, Source Priority | Historical |
| **AI-020 (Early)** | `docs/03-product/PRD.md` | All Stories | N/A (Product Def) | N/A | Markdown Doc | Human Review | PRD capabilities | Historical |
| **AI-021 (Early)** | `docs/03-product/epics.md` | All Stories | N/A (Epic Def) | N/A | Markdown Doc | Human Review | 7 Epics E-01..E-07 | Historical |
| **AI-025 (Early)** | `docs/03-product/taiga-backlog.md` | US-01..US-10, GOV-01..02 | T-01 đến T-42 | N/A (Planning) | Markdown Doc | Human Review | 42 Tasks, Estimate, Owner | Historical |
| **AI-026..027 (Early)**| `docs/03-product/usability-*` | US-01, US-04, US-06..10 | T-01..T-06 Usability | N/A (Testing) | Markdown Doc | Human Review | Test Script & Findings template | Historical |
| **AI-036..038 (Early)**| `vault-qa-benchmark.md`, `vault-qa-prompt.md` | Vault Verification | N/A (Q&A System) | N/A | Prompt / Markdown | 22 Q&A Questions | Citation rules, Grounded answers | Historical |

---

### Phần B: Final Delivery Phase (Kỹ thuật, Database Migration & Implementation)

| AI Activity ID | Artifact tạo/sửa | Thành viên phụ trách chính (theo Group-01) | User Story (chuẩn Group-01) | T-xxx (Business Task) | TASK-xxx (Technical) | Code Module | Automated Test | Evidence | Git Commit |
|:---:|---|---|---|---|---|---|---|---|:---:|
| **AI-005** | `FINAL_DELIVERY_BASELINE.md` | Trần Thị Thu Hà (QA / Tester) | All Stories | N/A (Audit) | TASK-000 | Baseline Report | Full suite 28 tests | 10 bugs, 6 security gaps | `72ec674` |
| **AI-006** | `FINAL_DEVELOPMENT_PLAN.md` | Nguyễn Trương Thùy Dương (BA / PO) | All Stories | N/A (Planning) | TASK-000 | Plan Report | N/A | 11 Workstreams, 33 Tasks | `72ec674` |
| **AI-007** | Git Setup | Trần Thị Kiều Giang (Engineering) | All Stories | N/A (DevOps) | TASK-000 | Git Repo | Terminal check | Branch `final-delivery` | `72ec674` |
| **AI-014..024** | Target Architecture & DB Sync | Trần Thị Kiều Giang (Engineering) | All Stories | N/A (Infrastructure) | **TASK-001** | `schema.prisma`, `.venv`, Hatchling | Prisma generate, test connection | 10 tables, 2 enums trên Supabase | `72ec674` |
| **AI-025** | Schema Update (Quantity) | Nguyễn Thị Thùy Dung (Backend) | **US-08** (Tạo PO) | T-26..T-29 / T-094 | **TASK-002** | `schema.prisma` (PO.quantity) | `prisma db push` | Column `quantity` trong table PO | `72ec674` |
| **AI-026** | Fix BUG-001 & Server Resolution | Nguyễn Thị Thùy Dung & Trần Thị Thu Hà | **US-08** (Tạo PO) | T-26..T-29 / T-091..093 | TASK-003 Prep | `procurement_service.py`, `po.py` | `test_us09_po.py` (11 tests) | PR APPROVED Guard, Price Lock | `72ec674` |
| **AI-027..028** | Human Decision Brief & HD-08 | Nguyễn Trương Thùy Dương & Trần Thị Thu Hà | **US-08** (Tạo PO) | T-26..T-29 / T-094 | TASK-002 / TASK-003 | `DECISION_LOG.md` | N/A | HD-08 Option A approved | `72ec674` |
| **AI-029..032** | T-094 Quantity Lock Implementation | Nguyễn Thị Thùy Dung (Backend) | **US-08** (Tạo PO) | T-26..T-29 / T-094 | **TASK-002 / T-094** | `procurement_service.py`, `ai_service.py` | `test_us09_po.py` (14/14 PASS) | Server-side quantity lock 100% | `72ec674` |
| **AI-033..037** | Lifespan & Base Database Seeding | Trần Thị Kiều Giang & Trần Thị Thu Hà | Core System | N/A (Database Setup) | **TASK-003 (Step 1, 2B)** | `db.py`, `main.py`, `seed.py` | `test_all_endpoints.py` | 2 Depts, 3 Sups, 5 Users, 2 Budgets | `4709911` |
| **AI-040** | Data Access Helpers | Trần Thị Kiều Giang & Nguyễn Thị Thùy Dung | **US-01**, **US-04** | T-01..T-03, T-10..T-16 | **TASK-003 (Step 3B.1)** | `data_access.py` | `test_data_access_helpers.py` (10/10 PASS) | UUID Resolution, FY2026 Q1 | `4709911` |
| **AI-043** | PR Creation Migration | Trần Thị Kiều Giang (Frontend/Eng) | **US-01** (Tạo PR) | T-01..T-03 | **TASK-003 (Step 3B.2)** | `procurement_service.py`, `pr.py` | `test_pr_creation_prisma.py` (10/10 PASS) | Row lock, Decimal, Retry ID | `4709911` |
| **AI-046** | PR Approval Migration | Nguyễn Trương Thùy Dương (BA/PO) | **US-04**, **US-05** | T-10..T-16 | **TASK-003 (Step 3B.3)** | `procurement_service.py`, `pr.py` | `test_pr_approval_prisma.py` (15/15 PASS) | 2-level threshold 50M, Status Guard | `4709911` |
| **AI-049** | Supplier & Quotation Migration | Nguyễn Trương Thùy Dương & Nguyễn Trúc Lam | **US-06**, **US-07** | T-17..T-25 | **TASK-003 (Step 3B.4)** | `suppliers.py`, `quotations.py`, `service` | `test_supplier_quotation_prisma.py` (15/15 PASS)| Supplier CRUD, Derived unitPrice, Compare | `4709911` |
| **AI-051** | Purchase Order Migration | Nguyễn Thị Thùy Dung (Backend) | **US-08** (Tạo PO) | T-26..T-29 | **TASK-003 (Step 3B.5)** | `po.py`, `procurement_service.py` | `test_po_prisma.py` (15/15 PASS) | 1-1 PR-PO, Price/Qty lock, Option A poNumber | `5584d68` |
| **AI-052** | Goods Receiving Migration | Nguyễn Thị Thùy Dung (Backend) | **US-09** (Receiving) | T-30..T-33 | **TASK-003 (Step 3B.6)** | `receiving.py`, `procurement_service.py` | `test_receiving_prisma.py` (14/14 PASS) | Cumulative receiving $\le$ PO.quantity, Partial | `b5d00a3` |
| **AI-053** | Close PR & Budget Settlement Migration | Trần Thị Thu Hà (QA/Tester) | **US-10** (Close PR) | T-34..T-36 | **TASK-003 (Step 3B.7)** | `pr.py`, `procurement_service.py` | `test_close_prisma.py` (14/14 PASS) | HD-07 Guard, Budget settlement Decimal | `dfdd7e5` |
| **AI-054** | Schema Identity Binding (authUserId) | Nguyễn Thị Thùy Dung & Nguyễn Trương Thùy Dương | All Stories (Auth) | N/A (Security Infra) | **TASK-004 (Step 3A)** | `schema.prisma` (User.authUserId) | `prisma db push`, `verify_step3a.py` | `authUserId String? @unique` sync CSDL | `6117d39` |
| **AI-055** | JWT/JWKS Authentication Verification | Nguyễn Thị Thùy Dung & Trần Thị Thu Hà | All Stories (Auth) | N/A (Security Infra) | **TASK-004 (Step 3B)** | `jwt_service.py`, `dependencies/auth.py`, `routers/auth.py` | `test_jwt_auth.py` (12/12 PASS) | Supabase JWT, ES256, JWKS, sub->User.authUserId | `[Uncommitted]` |
| **AI-056** | JWKS Timeout Hardening (timeout=5.0s) | Nguyễn Thị Thùy Dung & Trần Thị Thu Hà | All Stories (Auth) | N/A (Security Infra) | **TASK-004 (Step 3B Gap Fix)** | `jwt_service.py` | `test_jwt_auth.py` (12/12 PASS), targeted (23/23 PASS) | Explicit timeout=5.0s on PyJWKClient | `[Uncommitted]` |
| **AI-057** | Server-Side RBAC Implementation | Nguyễn Thị Thùy Dung & Trần Thị Thu Hà | All Stories (RBAC) | T-37, T-38, T-39 | **TASK-005** | `dependencies/rbac.py`, 6 routers, `procurement_service.py` | `test_rbac.py` (28/28 PASS) | 19 endpoints secured, No Self-Approval (GOV-01), zero client injection | `[Uncommitted]` |


---

## 3. Rà soát khoảng trống bằng chứng (Evidence Gaps & Traceability Integrity)

1. **Authentication (TASK-004):** `VERIFIED (STEP 3A & 3B)` — Đã hoàn tất thiết kế HD-12, Step 3A Schema Identity Binding (`authUserId String? @unique` trên Supabase PostgreSQL, evidence tại `docs/evidence/TASK-004-STEP-3A-SCHEMA.md`), và Step 3B JWT/JWKS Authentication Verification (PyJWT + ES256 + JWKS + `sub -> User.authUserId`, evidence tại `docs/evidence/TASK-004-STEP-3B-JWT.md`, 12/12 security test cases PASS). Sẵn sàng cung cấp verified identity cho TASK-005 (RBAC).
2. **RBAC Server-side Middleware (TASK-005):** `VERIFIED` — Đã hoàn tất triển khai `RoleChecker` dependency factory và `get_current_identity` bảo vệ 100% 19 endpoints nghiệp vụ, thực thi No Self-Approval (GOV-01) cho mọi vai trò (kể cả ADMIN), xóa bỏ hoàn toàn client identity injection, kiểm thử an ninh 28/28 test cases PASS (evidence tại `docs/evidence/TASK-005-RBAC.md`).
3. **Real LLM Integration (TASK-009):** `MISSING EVIDENCE` — Chưa gọi API ngoài (Gemini/OpenAI); hiện đang dùng so sánh deterministic.
4. **Frontend Architecture Refactor (TASK-006):** `MISSING EVIDENCE` — Frontend vẫn là file đơn khối `App.tsx`, chưa tách trang theo React Router.
5. **E2E Playwright Execution (TASK-013):** `MISSING EVIDENCE` — Chưa có báo cáo HTML chạy Playwright E2E thực tế trên UI hoàn chỉnh.

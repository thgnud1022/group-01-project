# TASK-005 — FINAL RBAC DESIGN (LOCKED FOR IMPLEMENTATION)

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)
**Tác vụ:** TASK-005 — Implement Server-Side RBAC
**Nhánh:** `final-delivery`
**Giai đoạn:** DESIGN LOCKED — ✅ ALL DECISIONS RESOLVED — READY FOR IMPLEMENTATION
**Cơ sở quyết định:** HD-02, HD-12, HD-REQ-07, HD-REQ-09, GOV-01

---

## A. IDENTITY CONFLICT RESOLUTION

### A.1. Sources Analyzed

| Source | Date | Key Statement | Priority |
| :--- | :--- | :--- | :---: |
| **HD-REQ-07** | 2026-09-22 | "This is a **temporary** compatibility decision for the migration phase **prior to TASK-004**. Once TASK-004 (Real JWT Auth) is implemented, user identity will be extracted securely **server-side from verified JWT claims** rather than client request bodies." | EXPIRED |
| **HD-REQ-09** | 2026-09-22 | "`ApprovePRSchema` must require `approverEmail: str`." — Built on HD-REQ-07 (`Requirement/source: HD-REQ-07`). | EXPIRED |
| **HD-12** | 2026-09-24 | "Backend **tuyệt đối không tin tưởng** role hay email do client gửi trong request body, query parameter, hoặc frontend selector." Flow: `JWT.sub → User.authUserId → User profile → User.role → RBAC`. | **ACTIVE** |
| **HD-02** | 2026-09-20 | "The backend MUST NOT trust any role sent by the client in the request body." Flow: `Verified JWT → user_id → application profile/database → role → RBAC`. | **ACTIVE** |
| **TASK-004** | Commit `19ce38b` | JWT/JWKS authentication verification DONE. `get_current_identity()` returns `AuthenticatedUser` from DB. | **DONE** |

### A.2. Conflict

| Aspect | HD-REQ-09 (2026-09-22) | HD-12 (2026-09-24) |
| :--- | :--- | :--- |
| **Acting approver identity** | `approverEmail` from request body → `User.email` lookup | `JWT.sub` → `User.authUserId` lookup |
| **Temporal scope** | "migration phase **prior to TASK-004**" (inherited from HD-REQ-07) | Permanent post-TASK-004 decision |
| **Client trust** | Trusts email in request body | "tuyệt đối không tin tưởng" client |

### A.3. Resolution

**Answer: A — JWT.sub → User.authUserId**

Reasoning chain:

1. **HD-REQ-07** (parent of HD-REQ-09) explicitly self-scoped as **temporary**: "*for the migration phase prior to TASK-004*".
2. **HD-REQ-07** explicitly states: "*Once TASK-004 is implemented, user identity will be extracted from verified JWT claims*".
3. **TASK-004 IS DONE** (commit `19ce38b`). The migration phase has ended.
4. **HD-REQ-09** inherits HD-REQ-07's temporal scope (`Requirement/source: HD-REQ-07`). HD-REQ-09 is therefore **expired**.
5. **HD-12** (decided 2 days later, 2026-09-24) is the permanent replacement. It explicitly prohibits trusting client-sent email/role.
6. **HD-02** (foundational decision) mandates: `Verified JWT → user_id → profile → role → RBAC`.

**Conclusion:**
- The acting approver of `POST /api/pr/{id}/approve` = **the authenticated user from JWT** (`current_user` from `get_current_identity()`).
- The `approverEmail` field in `ApprovePRSchema` is **OBSOLETE for identity purposes**.
- **No new Human Decision needed.** The sources form a clear, unambiguous chain: HD-REQ-07 (temporary) → TASK-004 DONE → HD-12 (permanent supersession).

### A.4. Consequence for `approve_pr_prisma()`

| Parameter | Current | After TASK-005 |
| :--- | :--- | :--- |
| `approver_email: str` | Required, from client body | **REMOVED** — replaced by `current_user: AuthenticatedUser` |
| Approver identity | `email → User.id` lookup in service | `current_user.id` (already resolved by `get_current_identity`) |
| Approver role | `user.role` from email lookup | `current_user.role` (already resolved by `get_current_identity`) |

---

## B. FINAL ENDPOINT MATRIX

Every business endpoint in the codebase, audited from actual router files:

| # | Router File | Endpoint | Method | Current Auth | Current RBAC | Client-Trust Fields | Current Gap |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `pr.py` | `/api/pr` | POST | ❌ NONE | ❌ NONE | `creatorId` (email) | Identity injection |
| 2 | `pr.py` | `/api/pr` | GET | ❌ NONE | ❌ NONE | — | Open read (MockDB) |
| 3 | `pr.py` | `/api/pr/{id}/approve` | POST | ❌ NONE | ❌ NONE | `approverEmail` (email) | Identity injection |
| 4 | `pr.py` | `/api/pr/{id}/close` | POST | ❌ NONE | ❌ NONE | `finance_user` (query param) | Identity injection |
| 5 | `pr.py` | `/api/pr/{id}/quotations` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 6 | `po.py` | `/api/po` | POST | ❌ NONE | ❌ NONE | `creatorId` (email) | Identity injection |
| 7 | `po.py` | `/api/po` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 8 | `quotations.py` | `/api/quotations` | POST | ❌ NONE | ❌ NONE | — | No role gate |
| 9 | `quotations.py` | `/api/quotations` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 10 | `quotations.py` | `/api/quotations/{id}` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 11 | `quotations.py` | `/api/quotations/compare` | POST | ❌ NONE | ❌ NONE | — | No role gate |
| 12 | `quotations.py` | `/api/purchase-requests/{id}/quotations` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 13 | `receiving.py` | `/api/receiving` | POST | ❌ NONE | ❌ NONE | — | No role gate |
| 14 | `receiving.py` | `/api/receiving` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 15 | `budget.py` | `/api/budget/{dept_id}` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 16 | `budget.py` | `/api/budget` | GET | ❌ NONE | ❌ NONE | — | Open read (all depts) |
| 17 | `suppliers.py` | `/api/suppliers` | POST | ❌ NONE | ❌ NONE | — | No role gate |
| 18 | `suppliers.py` | `/api/suppliers` | GET | ❌ NONE | ❌ NONE | — | Open read |
| 19 | `suppliers.py` | `/api/suppliers/{id}` | GET | ❌ NONE | ❌ NONE | — | Open read |

**Summary:** 19 business endpoints. 0 have authentication. 0 have RBAC. 4 have client-trust identity injection.

---

## C. FINAL RBAC MATRIX

5 roles from `schema.prisma` enum `Role`: EMPLOYEE, MANAGER, PROCUREMENT, FINANCE, ADMIN.

Cell values: **ALLOW** (source-backed) / **DENY** (source-backed) / **OPEN** (no explicit source, needs Human Decision)

| # | Action | EMPLOYEE | MANAGER | PROCUREMENT | FINANCE | ADMIN | Source |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Create PR | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | US-01: "Là Employee" = any company employee; all roles are employees |
| 2 | List PRs | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | US-02: tracking requires visibility |
| 3 | Approve PR (Step 1: Manager) | DENY | ALLOW | DENY | DENY | ALLOW | REQ-BR-02, `approve_pr_prisma()` line 327-328, line 340-342 |
| 4 | Approve PR (Step 2: Finance) | DENY | DENY | DENY | ALLOW | ALLOW | REQ-BR-02, `approve_pr_prisma()` line 330-332 |
| 5 | Close PR | DENY | DENY | DENY | ALLOW | ALLOW | US-10: "Là Finance"; close_pr_prisma takes finance_user |
| 6 | List PR Quotations | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | Read-only, US-02 tracking |
| 7 | Create PO | DENY | DENY | ALLOW | DENY | ALLOW | US-08: "Là Procurement"; T-27 kiểm tra điều kiện |
| 8 | List POs | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-1: ALLOW** — Employee có READ access |
| 9 | Create Quotation | DENY | DENY | ALLOW | DENY | ALLOW | US-06: "Là Procurement"; T-18 Upload/lưu Quotation |
| 10 | List Quotations | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-1: ALLOW** — Employee có READ access |
| 11 | Get Quotation | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-1: ALLOW** — Employee có READ access |
| 12 | Compare Quotations | DENY | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-2: ALLOW** — Manager/Finance có thể trigger compare |
| 13 | Record Receiving | DENY | DENY | ALLOW | DENY | ALLOW | **Human Decision K-3: PROCUREMENT + ADMIN** |
| 14 | List Receivings | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-1: ALLOW** — Employee có READ access |
| 15 | Get Budget (single dept) | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | US-04: Manager xem Budget; US-05: Finance kiểm tra Budget |
| 16 | List All Budgets | DENY | DENY | DENY | ALLOW | ALLOW | Finance role manages budget overview; no source gives Manager/Employee access to ALL depts |
| 17 | Create Supplier | DENY | DENY | ALLOW | DENY | ALLOW | US-06: "Là Procurement"; T-17 Quản lý Supplier |
| 18 | List Suppliers | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-1: ALLOW** — Employee có READ access |
| 19 | Get Supplier | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | **Human Decision K-1: ALLOW** — Employee có READ access |

### C.1. Human Decisions — ALL RESOLVED ✅

| # | Question | Human Decision | Date |
| :---: | :--- | :--- | :--- |
| **K-1** | Employee READ access to PO/Quotation/Receiving/Supplier | **ALLOW** | 2026-09-24 |
| **K-2** | Manager/Finance trigger quotation compare | **ALLOW** | 2026-09-24 |
| **K-3** | Receiving role assignment | **PROCUREMENT + ADMIN** | 2026-09-24 |

> All OPEN cells in the RBAC matrix above have been resolved. Zero remaining policy ambiguity.

---

## D. BUSINESS-CONTEXT AUTHORIZATION

### D.1. Authorization Category Classification

| Category | Definition | Check Location |
| :--- | :--- | :--- |
| **A. Pure Role Permission** | Only `current_user.role ∈ allowed_roles` | Router dependency |
| **B. Role + Business State** | Role check + entity state (e.g., PR status) | Service layer |
| **C. Role + Resource Ownership** | Role check + entity belongs to user/dept | Service layer |
| **D. Role + Approval Stage** | Role check + PR approval stage + threshold | Service layer |
| **E. Role + Self-Approval** | Role check + `current_user.id ≠ PR.creatorId` | Service layer |

### D.2. Per-Endpoint Authorization Classification

| Endpoint | Category | Authorization Logic |
| :--- | :--- | :--- |
| `POST /api/pr` | **A** | Any authenticated user can create PR |
| `GET /api/pr` | **A** (+ optional **C**) | Authenticated; optionally filter by ownership/dept |
| `POST /api/pr/{id}/approve` | **D + E** | Role (MANAGER/FINANCE/ADMIN) + Approval Stage (PENDING_MANAGER vs PENDING_FINANCE) + Threshold (>50M VND) + No Self-Approval (`current_user.id ≠ PR.creatorId`) |
| `POST /api/pr/{id}/close` | **A + B** | Role (FINANCE/ADMIN) + PR must have PO + Receiving complete (HD-07) |
| `GET /api/pr/{id}/quotations` | **A** | Any authenticated user |
| `POST /api/po` | **A + B** | Role (PROCUREMENT/ADMIN) + PR must be APPROVED (T-093) |
| `GET /api/po` | **A** | Authenticated users per RBAC matrix |
| `POST /api/quotations` | **A + B** | Role (PROCUREMENT/ADMIN) + PR must be APPROVED (T-052) |
| `GET /api/quotations` | **A** | Authenticated users per RBAC matrix |
| `GET /api/quotations/{id}` | **A** | Authenticated users per RBAC matrix |
| `POST /api/quotations/compare` | **A** | Authenticated users per RBAC matrix |
| `GET /api/purchase-requests/{id}/quotations` | **A** | Any authenticated user |
| `POST /api/receiving` | **A + B** | Role (PROCUREMENT/ADMIN) + PO exists + qty check (REQ-BR-04) |
| `GET /api/receiving` | **A** | Authenticated users per RBAC matrix |
| `GET /api/budget/{dept_id}` | **A** | Any authenticated user |
| `GET /api/budget` | **A** | Role (FINANCE/ADMIN) |
| `POST /api/suppliers` | **A** | Role (PROCUREMENT/ADMIN) |
| `GET /api/suppliers` | **A** | Authenticated users per RBAC matrix |
| `GET /api/suppliers/{id}` | **A** | Authenticated users per RBAC matrix |

### D.3. Key Finding

**`POST /api/pr/{id}/approve` is the MOST COMPLEX authorization** — it combines:
- Category D: Stage-based role selection
- Category E: No Self-Approval
- Business rule: REQ-BR-02 threshold >50M VND

This CANNOT be reduced to a simple `RoleChecker`. The router dependency provides the basic gate; the service layer enforces stage, threshold, and self-approval.

---

## E. NO SELF-APPROVAL POLICY

### E.1. Source

- **GOV-01 Acceptance Criteria:** "người tạo PR không thể tự Approve PR của mình"
- **T-39:** "Test No Self-Approval"
- **Source text does NOT create an Admin exception.**

### E.2. Policy (Exact)

```
IF current_user.id == PurchaseRequest.creatorId:
    THEN → HTTP 403 Forbidden
    detail: "Không thể phê duyệt PR do chính mình tạo (No Self-Approval — GOV-01)."
```

**Applied to ALL roles:** EMPLOYEE, MANAGER, PROCUREMENT, FINANCE, ADMIN.

No Admin bypass. No exception for any role.

### E.3. Check Location

- **Service layer** (`approve_pr_prisma()`), because:
  - The check requires `PurchaseRequest.creatorId`, which is only available after DB query.
  - Router dependency does not have access to the PR entity.
  - Prevents bypass via direct service call.

### E.4. Test Scenarios

| Actor | Creates PR? | Attempts Approve? | Expected |
| :--- | :--- | :--- | :--- |
| MANAGER (creator) | Yes | Yes (self) | 403 |
| FINANCE (creator) | Yes | Yes (self) | 403 |
| ADMIN (creator) | Yes | Yes (self) | 403 |
| EMPLOYEE (non-creator) | No | Yes | 403 (wrong role) |
| MANAGER (non-creator) | No | Yes (step 1) | 200 |
| FINANCE (non-creator) | No | Yes (step 2) | 200 |
| ADMIN (non-creator) | No | Yes (any step) | 200 |

---

## F. 401 VS 403 CONTRACT

| Condition | HTTP Code | Responsibility | Detail Pattern |
| :--- | :---: | :--- | :--- |
| Missing Authorization header | **401** | `get_current_identity` (TASK-004) | "Yêu cầu xác thực..." |
| Malformed Bearer token | **401** | `get_current_identity` (TASK-004) | "Định dạng Authorization header..." |
| Invalid/expired JWT signature | **401** | `jwt_service` (TASK-004) | "Chữ ký số JWT..." / "...hết hạn..." |
| Valid JWT but user not in DB | **401** | `get_current_identity` (TASK-004) | "Không tìm thấy hồ sơ..." |
| Authenticated but role ∉ allowed_roles | **403** | `RoleChecker` (TASK-005) | "Quyền truy cập bị từ chối..." |
| Authenticated but self-approval | **403** | Service layer (TASK-005) | "Không thể phê duyệt PR do chính mình tạo..." |
| Authenticated but wrong approval stage | **403** | Service layer (TASK-005) | "Vai trò {role} không có quyền duyệt PR ở giai đoạn {stage}." |
| Business validation error (e.g., PR not APPROVED for PO) | **400** | Service layer (existing) | "PR chưa được duyệt..." |
| Resource not found | **404** | Service layer (existing) | "Không tìm thấy..." |

**Rule:** Authorization failures → **403**. Business validation errors → **400**. Never use 400 for authorization.

---

## G. CLIENT IDENTITY INJECTION REMEDIATION

### G.1. Full Inventory

| # | Field | Location | Current Use | Remediation | Rationale |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `creatorId` | `CreatePRSchema.creatorId` | Identity: email → User.id | **IGNORE** — use `current_user.id` from JWT | HD-12: don't trust client identity |
| 2 | `approverEmail` | `ApprovePRSchema.approverEmail` | Identity: email → User.id | **REMOVE** — use `current_user.id` from JWT | HD-12 supersedes HD-REQ-09 (Section A) |
| 3 | `finance_user` | `close_pr` query param | Identity: hardcoded default | **REMOVE** — use `current_user.id` from JWT | HD-12: don't trust client identity |
| 4 | `creatorId` | `CreatePOSchema.creatorId` | Identity: email → User.id | **IGNORE** — use `current_user.id` from JWT | HD-12: don't trust client identity |
| 5 | `approverRole` | Not in current schema | Was removed in STEP 3B.3 | Already remediated | HD-REQ-09 prohibited this |
| 6 | `approverName` | Not in current schema | Was removed in STEP 3B.3 | Already remediated | HD-REQ-09 prohibited this |
| 7 | `comments` | `ApprovePRSchema.comments` | **Business data input** | **KEEP** — this is not identity | Comments are user-provided content, not identity |

### G.2. Classification

| Category | Fields | Action |
| :--- | :--- | :--- |
| **Must remove/ignore for identity** | `creatorId` (PR), `approverEmail`, `finance_user`, `creatorId` (PO) | Server overrides with `current_user.id` |
| **Business data input (keep)** | `comments`, `departmentId`, `title`, `items`, `purchaseRequestId`, `quotationId`, `supplierId`, `totalAmount`, `quantity`, `receivedQty` | Validated but not used for identity |
| **Keep for backward compatibility but ignore** | `CreatePRSchema.creatorId`, `CreatePOSchema.creatorId` | Field stays in schema to avoid frontend crash; value is **silently overwritten** by `current_user.id`; log deprecation warning |

---

## H. SERVICE BYPASS ANALYSIS

### H.1. Threat

If authorization only exists in router dependencies, someone importing `ProcurementService` directly bypasses all RBAC guards.

### H.2. Authorization Location Decision

| Authorization Rule | Router Dependency | Service Layer | Rationale |
| :--- | :--- | :--- | :--- |
| **Role gate** (role ∈ allowed_roles) | ✅ `RoleChecker` | ❌ (redundant) | First line of defense at HTTP boundary |
| **No Self-Approval** | ❌ (no PR data) | ✅ `approve_pr_prisma()` | Requires DB query for `PR.creatorId` |
| **Approval Stage** | ❌ (no PR data) | ✅ `approve_pr_prisma()` | Requires DB query for `PR.status` and threshold |
| **Business State guards** (PR APPROVED for PO, etc.) | ❌ (no entity data) | ✅ (existing) | Already implemented in service |

### H.3. Service Method Signature Changes

To prevent bypass, service methods receiving identity MUST take `AuthenticatedUser` or user_id from trusted source:

| Method | Current Signature | Target Signature |
| :--- | :--- | :--- |
| `create_pr_prisma()` | `creator_id: str` (email) | `creator_user_id: str` (UUID from `current_user.id`) |
| `approve_pr_prisma()` | `approver_email: str` | `current_user: AuthenticatedUser` |
| `create_po_prisma()` | `creator_email: str` | `creator_user_id: str` (UUID from `current_user.id`) |
| `close_pr_prisma()` | `finance_user: str` (email) | `actor_user_id: str` (UUID from `current_user.id`) |

### H.4. `approve_pr_prisma()` Internal Authorization

After signature change, the service method MUST internally enforce:

```python
# 1. No Self-Approval (Category E)
if current_user.id == pr_creator_id:
    raise PermissionError("No Self-Approval — GOV-01")

# 2. Stage-based role authorization (Category D)
# (existing logic, but now uses current_user.role instead of email lookup)
if stage == "PENDING_MANAGER_APPROVAL" and current_user.role not in ["MANAGER", "ADMIN"]:
    raise PermissionError("Stage requires MANAGER/ADMIN")
if stage == "PENDING_FINANCE_APPROVAL" and current_user.role not in ["FINANCE", "ADMIN"]:
    raise PermissionError("Stage requires FINANCE/ADMIN")
```

### H.5. Error Type for Service-Layer Authorization

| Current | Target | Reason |
| :--- | :--- | :--- |
| `raise ValueError(...)` for role mismatch | `raise PermissionError(...)` or custom `AuthorizationError` | Router maps `PermissionError` → 403, `ValueError` → 400 |

---

## I. TEST MATRIX

### I.1. Required Test Cases

| TC | Test Name | Category | Input | Expected | Source |
| :--- | :--- | :--- | :--- | :---: | :--- |
| RBAC-001 | Missing JWT | Auth | No Authorization header | **401** | TASK-004 |
| RBAC-002 | Invalid JWT | Auth | Expired/malformed token | **401** | TASK-004 |
| RBAC-003 | Employee approve PR | Role gate | EMPLOYEE + approve | **403** | GOV-01/T-38 |
| RBAC-004 | Manager approve PR (step 1, non-creator) | Role + Stage | MANAGER + PENDING_MANAGER + different creator | **200** | REQ-BR-02 |
| RBAC-005 | Procurement create PO | Role gate | PROCUREMENT + approved PR | **200** | US-08 |
| RBAC-006 | Finance approve PR (step 2, non-creator) | Role + Stage | FINANCE + PENDING_FINANCE + different creator | **200** | REQ-BR-02 |
| RBAC-007 | Admin approve PR (non-creator) | Role + Stage | ADMIN + any pending stage + different creator | **200** | REQ-BR-02 |
| RBAC-008 | Client role injection ignored | Injection | Valid JWT (EMPLOYEE) + body `{"role": "ADMIN"}` | **403** (role from DB) | HD-02/HD-12 |
| RBAC-009 | Client creatorId injection ignored | Injection | Valid JWT (userA) + body `{"creatorId": "userB"}` | PR.creatorId = userA | HD-12 |
| RBAC-010 | Client approverEmail injection ignored | Injection | Valid JWT (MANAGER) — no approverEmail needed | Approver = JWT user | HD-12 (Section A) |
| RBAC-011 | Employee self-approval | Self-Approval | EMPLOYEE creates PR, tries approve | **403** (role) | GOV-01/T-39 |
| RBAC-012 | Manager self-approval | Self-Approval | MANAGER creates PR, tries approve own PR | **403** (self) | GOV-01/T-39 |
| RBAC-013 | Finance self-approval | Self-Approval | FINANCE creates PR, tries approve own PR | **403** (self) | GOV-01/T-39 |
| RBAC-014 | Procurement self-approval | Self-Approval | PROCUREMENT creates PR, tries approve | **403** (role) | GOV-01/T-39 |
| RBAC-015 | Admin self-approval | Self-Approval | ADMIN creates PR, tries approve own PR | **403** (self) | GOV-01/T-39 |
| RBAC-016 | Wrong approval stage | Stage | FINANCE tries step 1 (PENDING_MANAGER) | **403** | REQ-BR-02 |
| RBAC-017 | DB role used (not cached) | Freshness | Change User.role in DB, next request uses new role | Updated role | HD-02 |
| RBAC-018 | Employee create PO | Role gate | EMPLOYEE + create PO | **403** | US-08 |
| RBAC-019 | Employee create Quotation | Role gate | EMPLOYEE + create quotation | **403** | US-06 |
| RBAC-020 | Employee record Receiving | Role gate | EMPLOYEE + record receiving | **403** | US-09 |
| RBAC-021 | Finance close PR (non-creator) | Role + Business | FINANCE + complete receiving | **200** | US-10 |
| RBAC-022 | Employee close PR | Role gate | EMPLOYEE + close PR | **403** | US-10 |
| RBAC-023 | Employee list all budgets | Role gate | EMPLOYEE + GET /api/budget | **403** | Budget visibility |
| RBAC-024 | Finance list all budgets | Role gate | FINANCE + GET /api/budget | **200** | US-05 |
| RBAC-025 | Employee create supplier | Role gate | EMPLOYEE + create supplier | **403** | US-06 |
| RBAC-026 | Procurement create supplier | Role gate | PROCUREMENT + create supplier | **200** | US-06/T-17 |
| RBAC-027 | Manager approve step 2 (>50M) | Wrong stage role | MANAGER + PENDING_FINANCE | **403** | REQ-BR-02 |
| RBAC-028 | Admin create PO | Role gate | ADMIN + approved PR + quotation | **200** | Admin superuser |

**Total: 28 test cases** covering auth (2), role gate (10), self-approval (5), stage (3), injection (3), business context (3), freshness (1), admin (1).

---

## J. IMPLEMENTATION CONTRACT

### J.1. New Files

| File | Purpose |
| :--- | :--- |
| `backend/app/dependencies/rbac.py` | `RoleChecker` class + `AuthorizationError` exception |
| `backend/tests/test_rbac.py` | ≥28 test cases per Section I |
| `docs/evidence/TASK-005-RBAC.md` | Execution evidence |

### J.2. Modified Files

| File | Changes |
| :--- | :--- |
| `backend/app/routers/pr.py` | Add `Depends(RoleChecker(...))` to all 5 endpoints; remove `creatorId`/`approverEmail`/`finance_user` from identity trust; pass `current_user` to service |
| `backend/app/routers/po.py` | Add `Depends(RoleChecker(...))` to 2 endpoints; remove `creatorId` from identity trust; pass `current_user.id` to service |
| `backend/app/routers/quotations.py` | Add `Depends(RoleChecker(...))` to 5 endpoints |
| `backend/app/routers/receiving.py` | Add `Depends(RoleChecker(...))` to 2 endpoints |
| `backend/app/routers/budget.py` | Add `Depends(RoleChecker(...))` to 2 endpoints |
| `backend/app/routers/suppliers.py` | Add `Depends(RoleChecker(...))` to 3 endpoints |
| `backend/app/services/procurement_service.py` | Change `approve_pr_prisma()` to accept `AuthenticatedUser`; add No Self-Approval check; change `create_pr_prisma()`/`create_po_prisma()`/`close_pr_prisma()` to accept UUID directly; change authorization errors from `ValueError` to `PermissionError`/`AuthorizationError` |

### J.3. `RoleChecker` Class Contract

```python
# FILE: backend/app/dependencies/rbac.py
# CONCEPTUAL SPECIFICATION — NOT EXECUTABLE CODE

class AuthorizationError(Exception):
    """Raised when authenticated user lacks required permission."""
    pass

class RoleChecker:
    """
    FastAPI dependency factory for role-based access control.

    Chain: RoleChecker → get_current_identity → JWT verify → DB lookup

    Usage:
        @router.post("/api/po")
        async def create_po(
            payload: CreatePOSchema,
            current_user: AuthenticatedUser = Depends(RoleChecker(["PROCUREMENT", "ADMIN"]))
        ):
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, current_user: AuthenticatedUser = Depends(get_current_identity)
    ) -> AuthenticatedUser:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Quyền truy cập bị từ chối: Thao tác yêu cầu vai trò {self.allowed_roles}. "
                       f"Vai trò hiện tại của bạn: {current_user.role}."
            )
        return current_user
```

### J.4. Router Wiring Contract (per endpoint)

| # | Endpoint | Dependency | Notes |
| :---: | :--- | :--- | :--- |
| 1 | `POST /api/pr` | `RoleChecker(["EMPLOYEE","MANAGER","PROCUREMENT","FINANCE","ADMIN"])` | All roles; override `creatorId` with `current_user.id` |
| 2 | `GET /api/pr` | `get_current_identity` | All authenticated users |
| 3 | `POST /api/pr/{id}/approve` | `RoleChecker(["MANAGER","FINANCE","ADMIN"])` | Stage + Self-Approval enforced in service |
| 4 | `POST /api/pr/{id}/close` | `RoleChecker(["FINANCE","ADMIN"])` | Override `finance_user` with `current_user.id` |
| 5 | `GET /api/pr/{id}/quotations` | `get_current_identity` | All authenticated users |
| 6 | `POST /api/po` | `RoleChecker(["PROCUREMENT","ADMIN"])` | Override `creatorId` with `current_user.id` |
| 7 | `GET /api/po` | `get_current_identity` | All authenticated users |
| 8 | `POST /api/quotations` | `RoleChecker(["PROCUREMENT","ADMIN"])` | |
| 9 | `GET /api/quotations` | `get_current_identity` | All authenticated users |
| 10 | `GET /api/quotations/{id}` | `get_current_identity` | All authenticated users |
| 11 | `POST /api/quotations/compare` | `get_current_identity` | All authenticated users |
| 12 | `GET /api/purchase-requests/{id}/quotations` | `get_current_identity` | All authenticated users |
| 13 | `POST /api/receiving` | `RoleChecker(["PROCUREMENT","ADMIN"])` | |
| 14 | `GET /api/receiving` | `get_current_identity` | All authenticated users |
| 15 | `GET /api/budget/{dept_id}` | `get_current_identity` | All authenticated users |
| 16 | `GET /api/budget` | `RoleChecker(["FINANCE","ADMIN"])` | |
| 17 | `POST /api/suppliers` | `RoleChecker(["PROCUREMENT","ADMIN"])` | |
| 18 | `GET /api/suppliers` | `get_current_identity` | All authenticated users |
| 19 | `GET /api/suppliers/{id}` | `get_current_identity` | All authenticated users |

### J.5. Service Method Signature Contract

| Method | Current | Target | Error Type |
| :--- | :--- | :--- | :--- |
| `create_pr_prisma()` | `creator_id: str` (email) | `creator_user_id: str` (UUID) | `ValueError` (400) |
| `approve_pr_prisma()` | `approver_email: str` | `current_user: AuthenticatedUser` | `PermissionError` → 403 for auth; `ValueError` → 400 for business |
| `create_po_prisma()` | `creator_email: str` (email) | `creator_user_id: str` (UUID) | `ValueError` (400) |
| `close_pr_prisma()` | `finance_user: str` (email) | `actor_user_id: str` (UUID) | `ValueError` (400) |

### J.6. Router Error Handling Contract

```python
# In each router, add catch for PermissionError → 403
except PermissionError as e:
    raise HTTPException(status_code=403, detail=str(e))
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### J.7. Target Request Flow

```text
HTTP Request + Bearer JWT
  → FastAPI Router
    → get_current_identity() [TASK-004]
      → JWT verify (ES256/JWKS)
      → DB: User by authUserId
      → return AuthenticatedUser
    → RoleChecker(allowed_roles) [TASK-005]
      → role ∈ allowed_roles?
      → YES → return AuthenticatedUser
      → NO  → HTTP 403
    → Router handler
      → pass current_user to service
    → Service method
      → Business-context auth (self-approval, stage)
      → PermissionError → caught in router → HTTP 403
      → Business logic
      → ValueError → caught in router → HTTP 400
      → return result
  → HTTP 200 OK
```

---

## K. HUMAN DECISIONS — ALL RESOLVED ✅

| # | Question | Human Decision | Date | Status |
| :---: | :--- | :--- | :--- | :--- |
| K-1 | Employee READ access to PO/Quotation/Receiving/Supplier | **ALLOW** | 2026-09-24 | ✅ DECIDED |
| K-2 | Manager/Finance trigger quotation compare | **ALLOW** | 2026-09-24 | ✅ DECIDED |
| K-3 | Receiving role assignment | **PROCUREMENT + ADMIN** | 2026-09-24 | ✅ DECIDED |
| K-4 | HD-REQ-09 `approverEmail` superseded by HD-12 JWT identity | **YES** (sources clear) | 2026-09-24 | ✅ RESOLVED (Section A) |

---

## L. TRACEABILITY

### L.1. GOV-01 → TASK-005 Mapping

| Backlog Task | Description | TASK-005 Coverage |
| :--- | :--- | :--- |
| **T-37** | Ma trận RBAC | Section C (RBAC Matrix) + Section B (Endpoint Matrix) |
| **T-38** | Kiểm tra quyền theo action | Section D (Business-Context Authorization) + Section J (Implementation) |
| **T-39** | Test No Self-Approval | Section E (Policy) + Section I (Test Matrix: RBAC-011..015) |

### L.2. Ownership

| Role | Person | Responsibility |
| :--- | :--- | :--- |
| **Primary Owner** | Nguyễn Thị Thùy Dung | GOV-01, US-08, Backend RBAC implementation |
| **Supporting** | Nguyễn Trúc Lam | AI Vault, test collaboration |
| **Supporting** | Trần Thị Thu Hà | QA/Tester, test verification |

### L.3. Dependency Chain

```text
HD-02 (Auth+RBAC Architecture) ─┐
HD-12 (Identity Binding)        ├─► TASK-004 (Auth) [DONE] ─► TASK-005 (RBAC) [THIS]
GOV-01 (RBAC + No Self-Approval)┘
```

---

## READINESS ASSESSMENT

| Gate | Status | Blocker |
| :--- | :--- | :--- |
| Identity conflict resolved (A) | ✅ RESOLVED | — |
| Endpoint matrix complete (B) | ✅ 19/19 endpoints listed | — |
| RBAC matrix defined (C) | ✅ ALL CELLS DECIDED | — |
| Business-context auth classified (D) | ✅ COMPLETE | — |
| No Self-Approval policy locked (E) | ✅ LOCKED | — |
| 401/403 contract locked (F) | ✅ LOCKED | — |
| Client injection remediation (G) | ✅ COMPLETE | — |
| Service bypass analysis (H) | ✅ COMPLETE | — |
| Test matrix defined (I) | ✅ 28 test cases | — |
| Implementation contract defined (J) | ✅ COMPLETE | — |
| Human decisions resolved (K) | ✅ ALL 4 DECIDED | — |
| Traceability mapped (L) | ✅ COMPLETE | — |

### READY FOR GEMINI IMPLEMENTATION = **YES** ✅

All policy questions resolved. All 19 endpoints have definitive ALLOW/DENY assignments.
No remaining ambiguity. Implementation may proceed following Section J contract.

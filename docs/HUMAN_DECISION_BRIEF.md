# Human Decision Brief
**Project:** AI Procurement & Purchase Approval System  
**Course:** Thực hành lập trình ứng dụng trong doanh nghiệp bằng AI  
**Branch:** `final-delivery`  
**Date:** 2026-09-20  
**Status:** AWAITING HUMAN DECISIONS

---

## 1. Purpose

Tài liệu này tổng hợp toàn bộ evidence thực tế từ source code, requirements, user stories, acceptance criteria, test files và Figma spec để trình bày các Human Decisions (HD-01 → HD-07) cần được team quyết định **trước khi bắt đầu implementation**.

Mỗi decision được trình bày trung lập với đầy đủ evidence. Tài liệu này **KHÔNG** tự đưa ra quyết định thay human.

---

## 2. Decision Status Overview

| ID | Decision | Current Status | Blocking Implementation? |
|:---|:---|:---|:---|
| HD-01 | Database | **DECIDED** | No |
| HD-02 | Authentication | **DECIDED** | No |
| HD-03 | AI | **DECIDED** | No |
| HD-04 | `create_po()` approval guard | **DECIDED** | No |
| HD-05 | E2E Strategy | **DECIDED** | No |
| HD-06 | Git Repository Setup | **DONE** | No |
| HD-07 | `close_pr()` condition | **DECIDED** | No |
| HD-08 | PO Quantity Source (T-094) | **DECIDED** | No |
| HD-REQ-05 | Demo Passwords & Bcrypt | **APPROVED (Option A)** | No |
| HD-REQ-06 | Initial Budget Period 2026 Q1 | **APPROVED (Option A)** | No |
| HD-REQ-07 | PR & Approval User Identity | **APPROVED** | No |
| HD-REQ-08 | Active Budget Period 2026 Q1 | **APPROVED** | No |
| HD-REQ-09 | Approver Email Bắt Buộc | **APPROVED (Option B)** | No |
| HD-REQ-10 | Approval Status Guard | **APPROVED** | No |

---

## HD-01 — Database Decision

### Decision Question
Project có migrate runtime từ MockDB/in-memory sang PostgreSQL thật hay không?

### Current Runtime Reality
**FACT.** `backend/app/services/procurement_service.py` định nghĩa class `MockDatabase` — một Python dictionary in-memory. Tất cả dữ liệu (budgets, prs, pos, receivings) được lưu trữ trong RAM và **mất toàn bộ khi server restart**.

```python
# procurement_service.py — Line 3-29 (FACT)
class MockDatabase:
    def __init__(self):
        self.budgets = { "DEPT-IT": {...}, "DEPT-HR": {...} }
        self.prs: Dict[str, Dict[str, Any]] = {}
        self.pos: Dict[str, Dict[str, Any]] = {}
        self.receivings: Dict[str, List[Dict[str, Any]]] = {}

db = MockDatabase()
```

### Documentation Claim
- **ADR-002** (INCONSISTENT): Ghi rõ target database là Supabase PostgreSQL sử dụng Prisma ORM.
- **`backend/.env.example`** (FACT): Có chứa placeholder `DATABASE_URL` nhưng file `.env` thực tế **không tồn tại** trong repository.

### Requirement Evidence
- **REQ-NFR-01:** "Hệ thống phải đảm bảo dữ liệu Purchase Request, Approval, Quotation và Budget được quản lý nhất quán trong toàn bộ quy trình." → In-memory RAM **không đảm bảo** yêu cầu này.

### Code Evidence
- `backend/prisma/schema.prisma` (FACT): Tồn tại schema đầy đủ cho 9 model (`User`, `Department`, `Budget`, `PurchaseRequest`, `PRItem`, `Supplier`, `Quotation`, `PurchaseOrder`, `Receiving`, `Approval`). Schema định nghĩa đúng, nhưng **không được gọi** ở bất cứ nơi nào trong runtime.
- Không có file migration nào tồn tại trong repository.
- `backend/seed.py` tồn tại nhưng nội dung chưa được kiểm tra xem có kết nối database thật không.

### Test Evidence
- `backend/tests/test_all_endpoints.py` (FACT): Chạy ngược lên `TestClient` của FastAPI, sử dụng trực tiếp `MockDatabase` in-memory. Tests PASS với MockDB.
- **UNVERIFIED CLAIM:** Không có test nào chứng minh ứng dụng hoạt động với database PostgreSQL thực.

### Audit Evidence
- `docs/FINAL_DELIVERY_BASELINE.md`: Ghi nhận gap này là một trong những vấn đề kiến trúc cốt lõi.

### Options

#### Option A — Giữ nguyên MockDB
- Tiếp tục dùng `MockDatabase` in-memory.
- Ứng dụng có thể demo được nhưng mất dữ liệu khi restart.
- Tests hiện tại vẫn PASS.
- Không cần cấu hình environment variables.

#### Option B — Migrate sang Supabase PostgreSQL
- Cần cung cấp `DATABASE_URL` trỏ đến Supabase instance thực.
- Cần chạy `prisma generate` và tạo migrations.
- Cần refactor toàn bộ `ProcurementService` để gọi Prisma client thay vì dict.
- Tests hiện tại cần được cập nhật (integration test thay vì unit test trên mock).
- Data sẽ persistent qua các lần restart.

### Impact
| Area | Option A | Option B |
|:---|:---|:---|
| Data Persistence | Mất khi restart | Persistent |
| REQ-NFR-01 | KHÔNG đạt | Đạt |
| Backend refactor scope | Nhỏ | Lớn |
| Tests | Vẫn PASS hiện tại | Cần cập nhật |
| Deployment | Đơn giản | Cần Supabase project + credentials |

### What Remains Unknown
- Supabase project instance đã được tạo chưa?
- Teacher/Course có bắt buộc real database để chấm điểm không?

### Human Decision Required
**Câu hỏi cho Human:** HD-01 — Có chấp nhận migrate runtime từ MockDB sang Supabase PostgreSQL không? Hay giữ nguyên MockDB cho phạm vi Final Delivery?

---

## HD-02 — Authentication Decision

### Decision Question
Project có chuyển từ Mock/Trust-client authentication sang Real Authentication với JWT verification hay không?

### Current Runtime Reality
**FACT.** `backend/app/routers/auth.py`:
- Hardcodes 5 user accounts trong biến `MOCK_USERS`.
- Accepts bất kỳ request nào có email đúng + password `password123`.
- Trả về chuỗi fake token `"mock-jwt-token-for-{email}"` — KHÔNG phải JWT hợp lệ.
- Không có bất kỳ **Dependency hoặc Middleware** nào để verify token trên các protected endpoints.

```python
# auth.py — Line 10-26 (FACT — runtime behavior)
MOCK_USERS = { "employee@company.com": {...}, ... }

def login(payload: LoginSchema):
    user = MOCK_USERS.get(payload.email)
    if not user or payload.password != "password123":
        raise HTTPException(status_code=401, ...)
    return { "access_token": f"mock-jwt-token-for-{payload.email}", ... }
```

**Critical Security Gap (FACT):** `backend/app/routers/pr.py` nhận `approverRole` trực tiếp từ POST request body — bất kỳ client nào có thể gửi `approverRole: "FINANCE"` hoặc `"ADMIN"` để tự duyệt PR của mình mà không bị chặn.

### Documentation Claim
- **ADR-002** (INCONSISTENT): Target direction là Supabase Auth + JWT.
- **REQ-NFR-02** (INCONSISTENT với code): "Hệ thống phải phân quyền chức năng phù hợp với vai trò Employee, Manager, Procurement, Finance và Admin."

### Current Frontend Reality
`frontend/src/App.tsx` sử dụng một `<select>` dropdown để chuyển role — không có login form, không gửi token đến backend API trong các request hiện tại.

### Options

#### Option A — Giữ Mock Authentication
- Giữ nguyên MOCK_USERS và fake token.
- Không có bảo mật thực sự.
- Phù hợp cho demo nhanh.

#### Option B — Implement Supabase Auth + JWT
- Cần Supabase project với Auth được bật.
- Backend cần middleware verify JWT ở mỗi protected route.
- Frontend cần login form thực sự và gửi Bearer token theo mỗi request.
- RBAC được enforce từ token claim thay vì từ client payload.

#### Option C — Custom JWT (không dùng Supabase Auth)
- Tự tạo JWT signing/verification bằng `python-jose` hoặc tương đương.
- Vẫn cần lưu users vào database thực (phụ thuộc HD-01).

### Impact
| Area | Option A | Option B | Option C |
|:---|:---|:---|:---|
| Security | Không có | Đầy đủ | Partial |
| REQ-NFR-02 | KHÔNG đạt (technically) | Đạt | Partial |
| Backend scope | Nhỏ | Lớn | Medium |
| Frontend scope | Không đổi | Cần login form | Cần login form |
| Dependency on HD-01 | Không | Có (cần DB lưu user) | Có |

### What Remains Unknown
- Teacher/Course có yêu cầu real authentication để chấm điểm không?

### Human Decision Required
**Câu hỏi cho Human:** HD-02 — Có sử dụng Supabase Auth + JWT verification không? Nếu có, đây sẽ là dependency của HD-01.

---

## HD-03 — AI Decision

### Decision Question
Project giữ Regex/Mock AI hay sử dụng Real LLM/API?

### Current Runtime Reality
**FACT.** `backend/app/services/ai_service.py` sử dụng Python `re` (regex) để extract thông tin từ text:
- Pattern matching cứng cho các từ khóa tiếng Việt ("laptop", "máy in", "bàn", "ghế").
- Trả về giá cứng hardcoded (ví dụ: 25,000,000 VND cho laptop).
- So sánh quotation bằng giá trị hardcoded `historical_avg_price = 25_000_000`.
- Không gọi bất kỳ external API nào.

```python
# ai_service.py — Line 19-35 (FACT)
qty_match = re.search(r'(\d+)\s*(cái|chiếc|bộ|...)', text_lower)
if "laptop" in text_lower:
    item_name = "Laptop Dell Vostro Workstation"
    unit_price = 25_000_000
```

### Requirement Evidence
- **REQ-FR-03** (Should): "AI hỗ trợ chuẩn hóa Purchase Request và gợi ý các thông tin còn thiếu trước khi Submit."
- **REQ-FR-13** (Must): "Hệ thống cho phép AI hỗ trợ phân tích và hiển thị kết quả so sánh Quotation."
- **REQ-FR-14** (Should): "AI đưa ra Recommendation dựa trên thông tin và tiêu chí của các Quotation."
- **REQ-FR-15** (Should): "AI cảnh báo giá bất thường khi đơn giá cao hơn hoặc bằng 20% so với mức trung bình lịch sử."
- **ASM-07:** "Trong MVP, AI có thể trích xuất thông tin từ file Quotation do Procurement cung cấp."

### Test Evidence
- `test_all_endpoints.py` (FACT): Test AI standardization PASS — bằng cách asserting cụ thể giá trị regex output.
- **UNVERIFIED CLAIM:** Không có test nào chứng minh behavior với LLM API thực.

### Options

#### Option A — Giữ Regex/Mock AI (Fast Fallback)
- Không cần API key.
- Tests hiện tại vẫn PASS.
- Response time < 1 giây, không có failure risk từ external API.
- Khả năng nhận diện hạn chế (chỉ các từ khóa cứng).

#### Option B — Tích hợp Real LLM API (ví dụ: Gemini API, OpenAI)
- Cần API key và billing setup.
- Cần refactor `ai_service.py` để gọi HTTP request đến LLM provider.
- Response time không xác định; có thể có rate limit và timeout.
- Cần xử lý error case khi API không phản hồi.
- Tests cần được cập nhật (mock API call hoặc integration test).

### What Remains Unknown
- Course requirement có bắt buộc real LLM integration để chấm điểm không?
- Nhóm đã có API key nào (Gemini, OpenAI) chưa?

### Human Decision Required
**Câu hỏi cho Human:** HD-03 — AI sử dụng Regex/Mock Fast Fallback hay cần tích hợp Real LLM API (Gemini/OpenAI)?

---

## HD-04 — `create_po()` / BUG-001

### Decision Question
`create_po()` có bắt buộc kiểm tra `PR.status == APPROVED` trước khi tạo PO hay không?

### Requirement Evidence — FACT
**REQ-BR-10 (FACT):** "Purchase Order chỉ được tạo sau khi Purchase Request được Approve và Supplier được lựa chọn."

**US-09 — AC2 (FACT):**
> Given Purchase Request **chưa được Approved**  
> When Procurement cố gắng tạo Purchase Order  
> **Then hệ thống không cho phép tạo Purchase Order.**

Đây là requirement rõ ràng và không mơ hồ từ 2 nguồn độc lập.

### Current Code Reality — FACT
```python
# procurement_service.py — Line 101-124
@staticmethod
def create_po(pr_id: str, quotation: Dict[str, Any], creator_id: str):
    pr = db.prs.get(pr_id)
    if not pr:
        raise ValueError(f"Không tìm thấy PR {pr_id}")
    # ← KHÔNG CÓ CHECK pr["status"] == "APPROVED"
    po_record = { ... }
    pr["status"] = "PO_CREATED"
    return po_record
```

**FACT:** Guard `pr["status"] == "APPROVED"` hoàn toàn vắng mặt. PO có thể được tạo cho PR đang ở bất kỳ trạng thái nào (bao gồm `PENDING_MANAGER_APPROVAL`, `DRAFT`, v.v).

### Test Evidence
- `test_all_endpoints.py` (`test_full_7step_procurement_workflow`): Test gọi Manager approval trước khi tạo PO, nhưng test **không verify** rằng hệ thống từ chối nếu PR chưa được approve. Đây là gap trong test coverage, không phải evidence rằng guard tồn tại.

### Security / Business Impact
- Một Procurement user có thể tạo PO cho PR mà Manager chưa duyệt, bỏ qua approval workflow hoàn toàn.
- Vi phạm trực tiếp REQ-BR-10, US-09 AC2, CON-01.

### Classification
- **Requirement:** FACT — REQ-BR-10 và US-09 AC2 đều xác nhận guard là bắt buộc.
- **Code:** FACT — Guard không tồn tại (BUG-001).
- **Decision scope:** Câu hỏi không phải là "có cần guard không" (requirement đã rõ), mà là **implementation approach và scope fix**.

### Human Decision Required
**Câu hỏi cho Human:** HD-04 — Có xác nhận fix BUG-001 bằng cách thêm guard `pr["status"] == "APPROVED"` vào `create_po()` không? Có cần xử lý thêm (ví dụ: cũng check quotation từ database thay vì từ client payload) không?

---

## HD-05 — E2E Strategy

### Decision Question
Playwright E2E hiện tại nên được sửa, rebuild, hay rewrite sau khi frontend architecture ổn định?

### Current Frontend Reality — FACT
- `frontend/src/App.tsx`: 418 lines, single component, **không có React Router**.
- Toàn bộ giao diện render trên một trang, role switching qua dropdown state.
- Không có route `/login`, `/pr`, `/pr/:id/comparison`.
- Không có CSS classes như `.supplier-card`, `.comparison-table`, `.status-badge`.

### Playwright Test Reality — FACT
File `docs/06-testing/playwright-e2e-us09.spec.ts` tồn tại và kiểm thử:
- `page.goto('http://localhost:5173/login')` — Route này **không tồn tại** trong frontend hiện tại.
- `page.locator('table.comparison-table')` — Selector này **không tồn tại** trong DOM.
- `page.locator('.supplier-card')` — Selector này **không tồn tại** trong DOM.
- `page.locator('span.status-badge')` — Selector này **không tồn tại** trong DOM.

**UNVERIFIED CLAIM:** Không có bằng chứng (screenshot, CI log, test report) cho thấy file này đã từng được execute thành công.

### Figma Evidence
- `docs/FIGMA_IMPLEMENTATION_SPEC.md` (FACT via Figma MCP): Prototype có 20 screens với sidebar navigation, multi-route architecture.
- Figma có màn hình "Suppliers (Flow C)", "Comparison + expiry warning" phù hợp với E2E scenario của US-09.

### Strategies Available

#### Strategy A — Sửa test hiện tại theo DOM hiện tại (App.tsx)
- Cập nhật selectors và flows trong Playwright test cho phù hợp với SPA 1-trang.
- Nhanh nhưng test chất lượng thấp, không theo chuẩn Figma.

#### Strategy B — Rebuild E2E sau khi rewrite Frontend
- Trước tiên implement routing và component structure cho Frontend.
- Sau đó viết E2E test dựa trên DOM mới.
- Đảm bảo test khớp với Figma flows.
- Phụ thuộc vào quyết định về Frontend Architecture (xem Additional Implementation Decision).

#### Strategy C — Giữ file E2E như documentation / defer
- Giữ file như specification (không phải executable test).
- Tập trung vào backend API tests và manual testing.
- E2E defer sang sau khi frontend ổn định.

### What Remains Unknown
- Teacher/Course có bắt buộc Playwright E2E phải PASS để chấm điểm không?

### Human Decision Required
**Câu hỏi cho Human:** HD-05 — Chiến lược nào cho E2E Tests? (A: Sửa test theo SPA hiện tại / B: Rebuild sau khi rewrite Frontend / C: Defer E2E)

---

## HD-06 — Git Repository Setup

### Status: **DONE**

### Evidence
- **FACT:** Git repository đã được khởi tạo trong workspace.
- **FACT:** Branch `final-delivery` đã được tạo và push lên remote: `https://github.com/thgnud1022/group-01-project`.
- **FACT:** Ghi nhận trong `docs/logs/ai-usage-log.md` (AI-007): "Xác nhận branch `final-delivery` đã lên GitHub thành công."
- **FACT:** File `docs/FINAL_DELIVERY_BASELINE.md` và các tài liệu đã được commit và push.

Decision này **đã hoàn thành**. Không mở lại.

---

## HD-07 — `close_pr()` Condition

### Decision Question
Điều kiện chính xác để close Purchase Request là gì? Đặc biệt: Receiving completion có phải điều kiện bắt buộc trước khi close PR hay không?

### Requirement Evidence — FACT
**REQ-BR-11 (FACT):** "Purchase Request chỉ được Close sau khi bước Receiving và các bước mua sắm liên quan hoàn tất."

**US-11 — AC1 (FACT):**
> Given Receiving **và các bước liên quan đã hoàn tất**  
> When người dùng có quyền Close Purchase Request  
> Then hệ thống cho phép Purchase Request chuyển sang Closed.

**US-11 — AC2 (FACT):**
> Given Receiving hoặc các bước liên quan **chưa hoàn tất**  
> When người dùng cố gắng Close Purchase Request  
> **Then hệ thống không cho phép Close.**

### Current Code Reality — FACT
```python
# procurement_service.py — Line 154-168
@staticmethod
def close_pr(pr_id: str, finance_user: str):
    pr = db.prs.get(pr_id)
    if not pr:
        raise ValueError(...)
    # ← KHÔNG CÓ CHECK Receiving completion
    # ← KHÔNG CÓ CHECK PO status
    db.budgets[dept_id]["tempReservedAmount"] -= estimated_val
    db.budgets[dept_id]["spentAmount"] += estimated_val
    pr["status"] = "CLOSED"
    return pr
```

**FACT:** Hàm `close_pr()` cho phép Close PR mà **không kiểm tra** trạng thái Receiving hay PO. Vi phạm trực tiếp REQ-BR-11 và US-11 AC2.

### Ambiguity — NEEDS HUMAN DECISION
Requirement nói "Receiving và các bước liên quan hoàn tất" — nhưng **"hoàn tất"** có nghĩa chính xác là gì?
- Option I: Tổng `receivedQty` >= `po.quantity`?
- Option II: PO phải có status cụ thể (ví dụ: `RECEIVED`)?
- Option III: Chỉ cần có ít nhất một bản ghi Receiving?

Requirement document (REQ-BR-11 và US-11) không đặc tả chính xác điều kiện kỹ thuật.

### Human Decision Required
**Câu hỏi cho Human:** HD-07 — Điều kiện chính xác để cho phép Close PR là gì? Cụ thể, "Receiving hoàn tất" được định nghĩa như thế nào?

---

## Additional Implementation Decision (no HD-ID assigned)

### Frontend Architecture / Layout

**Current State (FACT):** `frontend/src/App.tsx` là Single Page Application, 418 lines, inline styles, không có routing, không phù hợp với Figma prototype (20 screens, sidebar layout).

**Issue:** Quyết định về cách tiếp cận Frontend là downstream của HD-05 (E2E Strategy). Nếu chọn Strategy B (Rebuild E2E sau rewrite Frontend), cần quyết định thêm:

- **Approach 1:** Đập đi xây lại toàn bộ từ đầu theo Figma spec.
- **Approach 2:** Incremental refactor — thêm routing trước, tách component sau.
- **Approach 3:** Screen-by-screen implementation theo thứ tự Flow A → B → C → D từ Figma.

**Đây không phải là Human Decision chính thức (HD-ID).** Quyết định này được chốt sau khi HD-05 được resolved.

---

## Decision Dependencies

| Decision | Depends On | Blocks |
|:---|:---|:---|
| HD-01 (Database) | Supabase project credentials | HD-02 (nếu Option B cần lưu User), Backend refactor |
| HD-02 (Auth) | HD-01 (cần DB để lưu session nếu real auth) | Protected routes, RBAC enforcement |
| HD-03 (AI) | API key availability | `ai_service.py` refactor scope |
| HD-04 (create_po guard) | Không phụ thuộc HD khác | Có thể fix ngay độc lập |
| HD-05 (E2E Strategy) | Frontend architecture decision | Test suite rebuild scope |
| HD-06 (Git) | **DONE** | Không block gì |
| HD-07 (close_pr condition) | Không phụ thuộc HD khác | Có thể fix ngay khi điều kiện được xác nhận |
| Frontend Architecture | HD-05 | E2E test implementation |

---

## Implementation Blockers

Các decision sau phải được chốt **trước khi bắt đầu** implementation tương ứng:

| Blocker | Blocks These Tasks |
|:---|:---|
| HD-01 chưa chốt | Không thể bắt đầu database layer refactor |
| HD-02 chưa chốt | Không thể bắt đầu bảo mật API / RBAC |
| HD-04 chưa chốt | Không nên để BUG-001 tồn tại (fix scope nhỏ, có thể làm ngay khi confirm) |
| HD-07 chưa chốt | Không thể implement close_pr() guard đúng cách |
| HD-05 chưa chốt | Không thể thiết kế E2E test suite hoặc Frontend architecture |

**Note:** HD-04 và HD-07 là các fix nhỏ có thể được thực hiện **ngay sau khi human confirm** mà không cần chờ HD-01, HD-02, hay HD-03.

---

## Questions for Human

Dưới đây là các câu hỏi cụ thể cần human trả lời để unblock implementation:

1. **HD-01:** Có chấp nhận migrate runtime từ MockDB sang Supabase PostgreSQL không? Hay giữ nguyên MockDB cho phạm vi Final Delivery?

2. **HD-02:** Có sử dụng Supabase Auth + JWT verification không? Hay giữ Mock authentication?

3. **HD-03:** AI feature sẽ sử dụng Regex/Mock Fast Fallback hay cần tích hợp Real LLM API (Gemini/OpenAI)?

4. **HD-04 (BUG-001):** Xác nhận thêm guard `pr["status"] == "APPROVED"` vào `create_po()`? Có cần validate quotation source từ DB không?

5. **HD-05:** Chiến lược E2E nào được chọn?
   - A: Sửa test theo SPA `App.tsx` hiện tại
   - B: Rebuild E2E sau khi rewrite Frontend theo Figma
   - C: Defer E2E, tập trung backend tests

6. **HD-07:** Điều kiện "Receiving hoàn tất" được định nghĩa như thế nào?
   - I: `sum(receivedQty) >= po.quantity`
   - II: PO phải ở trạng thái `RECEIVED`
   - III: Có ít nhất một bản ghi Receiving là đủ

7. **Additional — Frontend:** Nếu HD-05 chọn Strategy B, cách tiếp cận nào cho frontend rewrite?
   - Full rewrite theo Figma
   - Incremental (routing first, components later)
   - Screen-by-screen theo Flow A → B → C → D

---

## HD-REQ-09 — Approver Identity Resolution for PR Approval API

### Decision Question
Khi migrate `approve_pr` từ MockDB sang Prisma/PostgreSQL, xử lý định danh người duyệt thế nào khi `Approval.approverId` là Foreign Key bắt buộc tới `User.id` (UUID), trong khi `ApprovePRSchema` hiện tại chỉ nhận `approverRole` và `approverName`?

### Human Decision (2026-09-22)
**APPROVED — OPTION B: APPROVER EMAIL BẮT BUỘC**
1. `ApprovePRSchema` bắt buộc có:
   - `approverEmail: str` — REQUIRED
   - `comments: Optional[str] = "Phê duyệt PR"`
2. Tuyệt đối không dùng `approverRole` hay `approverName` làm database identity.
3. Backend resolve server-side: `approverEmail → User.id`.
4. `Approval.approverId` lưu `User.id` (UUID) trong PostgreSQL.
5. Role authorization lấy từ `User.role` trong database, không tin role client gửi.
6. Không cho phép fallback ngầm từ role sang demo user (e.g. cấm hardcode `MANAGER → manager@company.com`).
7. Các test suite/client cũ sẽ được update sang gửi `approverEmail`.

---

## HD-REQ-10 — Approval Status Guard

### Decision Question
Có cho phép thực thi `approve_pr` trên PR đã duyệt hoặc không ở trạng thái chờ duyệt không?

### Human Decision (2026-09-22)
**APPROVED — APPROVAL STATUS GUARD**
1. `approve_pr` chỉ được thực thi khi PurchaseRequest đang ở trạng thái:
   - `PENDING_MANAGER_APPROVAL` hoặc `PENDING_FINANCE_APPROVAL`.
2. Nếu PR ở bất kỳ trạng thái nào khác (`APPROVED`, `REJECTED`, `PO_CREATED`, `CLOSED`), request approve bắt buộc bị reject (báo lỗi).
3. Không thay đổi quy định REQ-BR-02 (ngưỡng > 50M VND, Manager duyệt bước 1, Finance duyệt bước 2).

---

*Tài liệu này được cập nhật để ghi nhận các Human Decisions đã được phê duyệt chính thức.*

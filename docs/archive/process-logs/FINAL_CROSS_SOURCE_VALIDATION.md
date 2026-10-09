# FINAL CROSS-SOURCE VALIDATION

## 1. PURPOSE
Tài liệu này đối chiếu chéo (cross-validate) toàn bộ các tài liệu requirements, UI/UX (Figma), source code, và test files để xác định Nguồn Sự Thật (Source of Truth) của dự án ở trạng thái runtime thực tế. Mục đích là để làm rõ những gì đã thực sự được implement so với những gì chỉ nằm trên giấy, từ đó chốt lại phạm vi chính xác cho giai đoạn Final Delivery.

## 2. SOURCES EXAMINED

| Source | Exists? | Used? | Purpose |
|---|---|---|---|
| `docs/FINAL_DELIVERY_BASELINE.md` | Yes | Yes | Đọc trạng thái baseline và bugs đã ghi nhận. |
| `docs/FINAL_DEVELOPMENT_PLAN.md` | Yes | Yes | Kiểm tra kế hoạch công việc và các Workstreams dự kiến. |
| `docs/01-discovery/requirements.md` | Yes | Yes | Xác minh Functional Requirements, NFR, BR và ASM. |
| `docs/03-product/user-story.md` | Yes | Yes | Lấy ngữ cảnh luồng tính năng. |
| `docs/FIGMA_IMPLEMENTATION_SPEC.md` | Yes | Yes | Xác minh UX/UI Evidence từ Figma Prototype. |
| `backend/app/routers/*.py` | Yes | Yes | Kiểm tra API routes và authentication runtime thực tế. |
| `backend/app/services/procurement_service.py` | Yes | Yes | Kiểm tra luồng dữ liệu (MockDB) và business rules backend. |
| `backend/app/services/ai_service.py` | Yes | Yes | Kiểm tra cách AI được implement (Fast Fallback regex). |
| `frontend/src/App.tsx` | Yes | Yes | Kiểm tra Frontend runtime, component và routing thực tế. |
| `backend/tests/test_all_endpoints.py` | Yes | Yes | Đánh giá backend test execution và evidence. |
| `docs/06-testing/playwright-e2e-us09.spec.ts` | Yes | Yes | Đánh giá sự tồn tại của Frontend E2E Test. |

## 3. SOURCE-OF-TRUTH RULES
Thứ tự ưu tiên được áp dụng nghiêm ngặt khi xác minh:
1. **Runtime Source Code** (Xác định ứng dụng đang thực sự làm gì)
2. **Test Execution Evidence** (Xác định tính năng nào thực sự hoạt động và PASS)
3. **Teacher/Course Requirements & User Stories** (Xác định cái gì *phải* làm)
4. **Existing Documentation** (Mô tả lý thuyết)
5. **Figma** (Chỉ làm bằng chứng UI/UX, không sinh ra business logic)

## 4. REQUIREMENT CROSS-VALIDATION MATRIX

| Requirement | User Story | Acceptance Criteria | Docs Claim | Code Reality | Test Evidence | Figma Evidence | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| REQ-FR-01 (Tạo PR) | US-01 | Submit đủ thông tin PR | DB Prisma cho PR | MockDB RAM (procurement_service) | PASS (in-memory) | Có form | INCONSISTENT | Code chạy được nhưng không lưu DB thực |
| REQ-FR-03 (AI Chuẩn hóa) | US-02 | AI trích xuất title, qty, price | Dùng LLM API | Regex rule-based (`ai_service`) | PASS (mock rules) | Có UI | INCONSISTENT | Chưa có Real AI integration |
| REQ-FR-07 (Approval Workflow) | US-03,04 | Multi-level (Manager > Finance) | Tự động chuyển status | Đúng chuẩn trong MockDB | PASS (in-memory) | Có screens | FACT | Implement đúng BR-02, ASM-05 (>50tr) |
| REQ-FR-13 (AI So sánh) | US-10 | Phân tích PDF/bất thường | AI LLM | Regex + Random Price Diff | PASS (mock rules) | Có màn hình | INCONSISTENT | AI service chỉ dùng thuật toán mock |
| REQ-FR-16 (Khóa Giá PO) | US-09 | Lấy đúng giá từ Quotation | Khóa 100% | Lấy trực tiếp vào PO DB Mock | PASS (in-memory) | N/A | FACT | Khớp với ASM-04 |
| REQ-NFR-02 (RBAC / Roles) | US-05 | Phân quyền 5 roles | Supabase Auth + JWT | Hardcoded Mock `auth.py`, no JWT check | UNKNOWN | N/A | INCONSISTENT | Thiếu bảo mật API backend thực sự |
| REQ-BR-11 (Receiving) | US-11 | Cập nhật kho, so sánh qty | Ghi nhận Receipt | Có API `receive_goods` (MockDB) | PASS (in-memory) | N/A | FACT | |

## 5. PROCUREMENT REQUEST LIFECYCLE
Luồng thiết kế:
Draft → Submit → PENDING_MANAGER_APPROVAL → PENDING_FINANCE_APPROVAL → APPROVED → COLLECTING_QUOTATIONS → PO_CREATED → PARTIALLY_RECEIVED/RECEIVED → CLOSED

**Thực tế trong code (ProcurementService):**
- Đã tồn tại các trạng thái: `PENDING_MANAGER_APPROVAL`, `PENDING_FINANCE_APPROVAL`, `APPROVED`, `PO_CREATED`, `CLOSED`.
- Code bỏ qua trạng thái `COLLECTING_QUOTATIONS` (PR chuyển thẳng từ APPROVED lên PO_CREATED khi gọi API `/api/po`).
- **Khác biệt (INCONSISTENT):** Lifecycle bị cắt ngắn ở bước gom báo giá. Không có validation Receiving completion trong API `close_pr`.

## 6. ROLE & PERMISSION VALIDATION
- **Documented Roles:** Employee, Manager, Procurement, Finance, Admin.
- **Runtime Rules:** `backend/app/routers/auth.py` có chứa 5 roles này trong biến `MOCK_USERS`.
- **UI Permissions:** Frontend `App.tsx` sử dụng state `role` từ một dropdown box để render các button tương ứng. 
- **Backend Authorization:** KHÔNG TỒN TẠI. API nhận `approverRole` trực tiếp từ payload POST mà không hề check token JWT hay session.
- **Trạng thái:** INCONSISTENT. Tài liệu yêu cầu phân quyền hệ thống nhưng code lại ủy thác phân quyền 100% cho client side (trusting client payload).

## 7. AUTHENTICATION VALIDATION
- **Documented Auth:** Supabase PostgreSQL + Auth JWT.
- **Actual Runtime Auth:** Fake Login API (`/api/auth/login`) so sánh password tĩnh `password123`.
- Trả về token giả (`mock-jwt-token-for-...`).
- Không có bất kỳ Dependency nào để Verify JWT ở các route backend.
- **Trạng thái:** INCONSISTENT.

## 8. DATABASE VALIDATION
- **Documented Database:** Supabase (PostgreSQL) sử dụng Prisma.
- **Configured Database:** Tồn tại `backend/prisma/schema.prisma` đầy đủ các bảng.
- **Runtime Database:** Ứng dụng runtime **không gọi** Prisma. Toàn bộ logic chạy trên `MockDatabase` (Dictionary Python) tại `app/services/procurement_service.py`.
- **Trạng thái:** INCONSISTENT. Runtime architecture đang dùng in-memory state.

## 9. AI VALIDATION
- **Yêu cầu:** AI Standardize PR (REQ-FR-03) và AI Compare Quotations (REQ-FR-13).
- **Thực tế Code:** `backend/app/services/ai_service.py` dùng Regex (`re.search`) để gán cứng kết quả (Fast Fallback).
- **Execution Evidence:** Test chạy Pass đối với Regex cứng.
- **Trạng thái:** NEEDS HUMAN DECISION. (Có cho phép giữ Mock AI để pass môn, hay bắt buộc gọi real LLM API như Gemini/OpenAI?).

## 10. PURCHASE ORDER VALIDATION
- API `create_po()` trong `ProcurementService`:
  - **PR Status Guard:** Không có check `pr["status"] == "APPROVED"`. Bất kỳ lúc nào truyền vào cũng tạo PO được. (INCONSISTENT)
  - **Quotation Source:** Client truyền data trực tiếp qua payload `quotation`, server nhận và nhét vào PO không xác thực lại từ DB. (INCONSISTENT)
  - **Price Lock:** Được thực thi đúng, copy 100% giá trị từ payload vào PO. (FACT)

## 11. PR CLOSE VALIDATION
- API `close_pr()` trong `ProcurementService`:
  - Trừ tiền `tempReservedAmount` và cộng vào `spentAmount` của Budget.
  - **Receiving Guard:** Hoàn toàn KHÔNG kiểm tra PO của PR này đã nhận đủ hàng chưa. Gọi là đóng luôn.
  - **Trạng thái:** INCONSISTENT so với REQ-BR-11 (Purchase Request chỉ được Close sau khi bước Receiving và các bước mua sắm liên quan hoàn tất).

## 12. E2E VALIDATION
- **Frontend App:** Single Page Application không có Route (`react-router-dom` vắng mặt). Toàn bộ nằm ở `App.tsx`.
- **E2E Tests:** Có file `playwright-e2e-us09.spec.ts`.
- **Test Evidence:** UNVERIFIED CLAIM. File test sử dụng selector như `.supplier-card` và `.comparison-table` không hề tồn tại trong DOM của `App.tsx`. Không có bằng chứng test này từng được execute thành công trên code hiện tại.

## 13. DOCUMENTATION DRIFT
| Document | Claim | Actual Reality | Status | Evidence |
|---|---|---|---|---|
| REQ-NFR-02 | Hệ thống phân quyền chặt chẽ | Trust client data, không verify JWT | INCONSISTENT | `pr.py` nhận trực tiếp `approverRole` từ request body. |
| ADR-002 | Supabase + Prisma | Mock Database Python Dictionary | INCONSISTENT | `procurement_service.py` |
| ADR-001 | Tích hợp Generative AI | Regex Regex Fast Fallback | INCONSISTENT | `ai_service.py` |
| Figma | 20 màn hình, dashboard layout | SPA `App.tsx` duy nhất | INCONSISTENT | `frontend/src/App.tsx` (418 lines total). |

## 14. PHANTOM FILES
| Referenced File | Referencing Document | Exists? | Impact |
|---|---|---|---|
| `.env` (Supabase credentials) | Config Database | No (chỉ có `.env.example`) | Không thể connect DB thực. |
| `frontend/src/index.css` (Tailwind) | Codebase assumptions | No | Frontend render giao diện thô inline. |

## 15. CRITICAL GAPS
- **CRITICAL:** Backend Authorization. API mở toang không check token. Bất kỳ user nào cũng có thể gửi request giả mạo `approverRole: "FINANCE"` để tự duyệt PR của mình.
- **CRITICAL:** Real Database. Ứng dụng sẽ mất mọi dữ liệu (Budget, PR, PO) khi reset container/server do đang xài dict.
- **HIGH:** Frontend Layout. SPA thô sơ cần viết lại bằng routing để đáp ứng E2E test.
- **HIGH:** Thiếu business validation trong `create_po` (không check trạng thái PR trước khi tạo) và `close_pr` (không check trạng thái nhận hàng).

## 16. HUMAN DECISIONS REQUIRED

| ID | Decision | Current Evidence | Current Status |
|---|---|---|---|
| HD-01 | Database | MockDB runtime (`procurement_service.py`); target direction Supabase PostgreSQL (`schema.prisma` + ADR-002) | NEEDS HUMAN DECISION |
| HD-02 | Authentication | JWT verification currently missing (`auth.py`); API trusts client-provided role payload; target direction Supabase Auth + JWT | NEEDS HUMAN DECISION |
| HD-03 | AI | Current implementation is regex/rule-based (`ai_service.py`); no real LLM call; no API key configured | NEEDS HUMAN DECISION |
| HD-04 | `create_po()` approval guard (BUG-001) | PR status guard missing in `ProcurementService.create_po()` — PO can be created for an unapproved PR; REQ-BR-10 and REQ-BR-02 require APPROVED status | NEEDS HUMAN DECISION |
| HD-05 | E2E Strategy | Existing `playwright-e2e-us09.spec.ts` references selectors (`.supplier-card`, `.comparison-table`) that do not exist in current `App.tsx`; no execution evidence | NEEDS HUMAN DECISION |
| HD-06 | Git Repository Setup | Git repository initialized, `final-delivery` branch created and pushed to GitHub | **DONE** |
| HD-07 | `close_pr()` condition | `close_pr()` currently skips Receiving guard; REQ-BR-11 states Close requires Receiving completion — exact condition needs confirmation from AC | NEEDS HUMAN DECISION |

**Additional Implementation Decision (no HD-ID assigned):**
- **Frontend Layout / Architecture:** Current frontend is a 1-page SPA (`App.tsx`, 418 lines, inline styles, no router) which does not match the Figma spec (20 screens, sidebar layout). A decision is needed on whether to rewrite with React Router + component architecture before or as part of E2E stabilization. This decision is **downstream of HD-05** and should not be assigned an HD-ID independently.

## 17. RECOMMENDED SEQUENCE
1. **Chốt Human Decisions (HD-01 đến HD-07):** Bắt buộc phải có quyết định từ Product Owner/Tech Lead cho các gap giữa Mock và Real implementations.
2. **Fix BUG-001 / HD-04:** Bổ sung guard `pr.status == APPROVED` vào `create_po()` — đây là sửa rất nhanh, không block các HD khác.
3. **Xác nhận close_pr() condition / HD-07:** Đối chiếu Acceptance Criteria với code để chốt điều kiện Receiving.
4. **Fix Security / HD-02:** Bổ sung JWT middleware nếu chọn phương án bảo mật thực sự.
5. **Database Migration / HD-01:** Chạy `prisma generate` + migrate nếu chọn Supabase PostgreSQL.
6. **Frontend Architecture:** Quyết định sau khi HD-05 (E2E strategy) được chốt.

## 18. FINAL VALIDATION SUMMARY

### Confirmed Facts
- Prisma schema tồn tại và đúng cấu trúc.
- Business rule khóa giá 100% tại bước tạo PO có tồn tại trong MockDB.
- Tests cho backend API (trên môi trường Mock) tồn tại và hoạt động.

### Unresolved Inconsistencies
- Database: Docs yêu cầu Supabase, Code dùng in-memory RAM.
- Backend Security: Yêu cầu JWT, nhưng API trust payload từ client.
- Lifecycle: PO tạo mà không cần PR Approved; PR đóng không cần Receiving.
- AI Logic: Mô tả là AI LLM nhưng code là Regex rules.

### Human Decisions Required
- **HD-01** Database: MockDB vs Supabase PostgreSQL
- **HD-02** Authentication: Mock trust-client vs Supabase Auth + JWT
- **HD-03** AI: Regex Fast Fallback vs Real LLM API
- **HD-04** BUG-001: Fix `create_po()` PR approval guard
- **HD-05** E2E Strategy: Rebuild/rewrite Playwright tests after frontend stabilizes
- **HD-06** Git Setup: **DONE**
- **HD-07** `close_pr()`: Confirm Receiving-completion condition from Acceptance Criteria

### Unverified Claims
- Frontend E2E tests (Playwright) là ảo, không thể pass trên DOM hiện tại.

### Unknowns
- Chưa rõ có bắt buộc phải kết nối AI LLM API thật để pass chấm điểm môn học hay không.

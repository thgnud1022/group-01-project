# Curriculum-Aligned HD Review

**Project:** AI Procurement & Purchase Approval System  
**Branch:** `final-delivery`  
**Date:** 2026-09-20  
**Scope:** HD-03 · HD-05 · HD-07  
**Task type:** REVIEW / ANALYSIS — NO CODE CHANGES

---

## 1. Executive Summary

Tài liệu này phân tích 3 Human Decisions còn mở (HD-03, HD-05, HD-07) bằng cách đối chiếu đa nguồn: Giáo trình thực hành (Giao_trinh.txt), requirements, user stories, source code thực tế, và test files. Phân tích dựa trên evidence đọc trực tiếp từ source, không suy diễn.

**Findings chính:**
- **HD-03 (AI):** Giáo trình KHÔNG bắt buộc Real LLM — chỉ yêu cầu "Automated testing & bug quality" và ghi chú Mock là option hợp lệ. Project requirements dùng từ "AI hỗ trợ" nhưng không chỉ định phải dùng LLM/API cụ thể. Tuy nhiên, 1 requirement (REQ-FR-13 "Must") và ASM-07 có thể không đáp ứng hoàn toàn bằng Regex cứng — cần clarification.
- **HD-05 (E2E):** Giáo trình BẮT BUỘC "Tự động hóa critical path E2E" (Bài cuối task 4, line 621). Playwright spec hiện tại tham chiếu DOM không tồn tại trong `App.tsx`. Đây là gap kép: E2E là course requirement AND spec không executable.
- **HD-07 (Receiving):** REQ-BR-11 và US-11 AC2 đều nói rõ "Receiving hoàn tất" là điều kiện bắt buộc. Tuy nhiên "hoàn tất" chưa được định nghĩa kỹ thuật. Code `close_pr()` bỏ qua hoàn toàn điều kiện này.

---

## 2. Source Classification

| Evidence | Source File / Line | Classification |
|:---|:---|:---|
| "Tự động hóa critical path E2E" | Giao_trinh.txt L621 | COURSE REQUIREMENT |
| "Automated testing & bug quality" (6/60 điểm) | Giao_trinh.txt L639 | COURSE REQUIREMENT |
| "5 critical E2E flows pass" | Giao_trinh.txt L1200 (Case mẫu Voice Commerce) | **CASE MẪU** — KHÔNG phải requirement của nhóm này |
| "LLM_API_KEY (optional if MOCK_ASSISTANT=true)" | Giao_trinh.txt L1850 (Runbook mẫu Voice Commerce) | **CASE MẪU** — KHÔNG phải requirement của nhóm này |
| "LLM không truy cập DB trực tiếp" (ADR mẫu) | Giao_trinh.txt L1567 (Output mẫu Voice Commerce) | **CASE MẪU** — KHÔNG phải requirement của nhóm này |
| "AI hỗ trợ chuẩn hóa PR" | requirements.md REQ-FR-03 (Should) | PROJECT REQUIREMENT |
| "AI hỗ trợ phân tích và hiển thị kết quả so sánh" | requirements.md REQ-FR-13 (Must) | PROJECT REQUIREMENT |
| "AI đưa ra Recommendation" | requirements.md REQ-FR-14 (Should) | PROJECT REQUIREMENT |
| "AI cảnh báo giá bất thường ≥20%" | requirements.md REQ-FR-15 (Should) | PROJECT REQUIREMENT |
| "AI có thể trích xuất thông tin từ Quotation" | requirements.md ASM-07 | PROJECT ASSUMPTION |
| "AI chỉ đóng vai trò hỗ trợ" | requirements.md CON-03 | PROJECT CONSTRAINT |
| US-09 AC2: PR chưa Approved → không tạo PO | user-story.md L307-310 | USER STORY / AC |
| US-11 AC2: Receiving chưa hoàn tất → không Close | user-story.md L368-371 | USER STORY / AC |
| REQ-BR-11: Close sau khi Receiving hoàn tất | requirements.md L54 | PROJECT REQUIREMENT |
| `ai_service.py` dùng `re.search()` regex | backend/app/services/ai_service.py | CODE FACT |
| `create_po()` không check PR status | backend/app/services/procurement_service.py L101-124 | CODE FACT |
| `close_pr()` không check Receiving | backend/app/services/procurement_service.py L154-168 | CODE FACT |
| Playwright spec references `.supplier-card` | docs/06-testing/playwright-e2e-us09.spec.ts L49 | CODE FACT (UNEXECUTABLE) |
| `App.tsx` không có route `/login`, `/pr` | frontend/src/App.tsx | CODE FACT |
| Prisma `Receiving` model: receivedQty + purchaseOrderId | backend/prisma/schema.prisma L133-141 | CODE FACT |
| Prisma `PurchaseOrder` model không có status `RECEIVED` | backend/prisma/schema.prisma L118-131 | CODE FACT |
| Tests PASS cho business rules BR-01..04 | backend/tests/test_business_rules.py | CODE FACT (executed against MockDB) |
| Figma: 20 screens, sidebar layout, multi-route | docs/FIGMA_IMPLEMENTATION_SPEC.md | FIGMA FACT |
| Case mẫu Voice Commerce (Section 18) | Giao_trinh.txt L779-2280 | **CASE MẪU** — minh họa, không phải requirement của project này |

---

## 3. HD-03 — AI Implementation Strategy

### 3.1 Course Requirement

**FACT.** Giao_trinh.txt Section 15.1 (Bài cuối - Nhiệm vụ), Line 621:
> "4. **Tự động hóa critical path E2E; unit/integration cho logic quan trọng.**"

→ Giáo trình yêu cầu **automated testing**, không yêu cầu AI implementation method cụ thể (Regex vs LLM).

**FACT.** Giao_trinh.txt Section 15.2 (Rubric 60%), Line 639:
> "Automated testing & bug quality — **6 điểm**"

→ AI Service implementation type KHÔNG được đề cập trong rubric. Rubric chỉ đo testing quality, không đo "Real AI vs Regex AI".

**FACT.** Giao_trinh.txt Section 18 (Case mẫu Voice Commerce), Line 780:
> "**Đây là chuẩn tham khảo về độ sâu và cách liên kết artifact. Sinh viên không sao chép nguyên đề tài; hãy thay domain, user, business rules, data và test của dự án nhóm mình.**"

→ Mọi chi tiết kỹ thuật (LLM, `LLM_API_KEY`, `MOCK_ASSISTANT=true`) trong Section 18 là **case mẫu** của project Voice Commerce, KHÔNG phải requirement bắt buộc cho project AI Procurement này.

**CONCLUSION (COURSE):** Giáo trình **KHÔNG bắt buộc** Real LLM cho project này. Giáo trình cũng **KHÔNG bắt buộc** Mock/Regex. Đây là implementation choice thuộc về nhóm.

### 3.2 Project Requirement

| Requirement ID | Priority | Wording | LLM Required? |
|:---|:---|:---|:---|
| REQ-FR-03 | **Should** | "AI hỗ trợ chuẩn hóa PR và gợi ý thông tin còn thiếu" | Not specified |
| REQ-FR-13 | **Must** | "AI hỗ trợ phân tích và hiển thị kết quả so sánh Quotation" | Not specified |
| REQ-FR-14 | **Should** | "AI đưa ra Recommendation dựa trên thông tin và tiêu chí" | Not specified |
| REQ-FR-15 | **Should** | "AI cảnh báo giá bất thường khi đơn giá ≥20% so với trung bình lịch sử" | Not specified |
| CON-03 | Constraint | "AI chỉ đóng vai trò hỗ trợ, không thay thế quyết định" | Not specified |
| ASM-07 | Assumption | "AI có thể trích xuất thông tin từ file Quotation" | Not specified |

**OBSERVATION:** Không có requirement nào chỉ định phải dùng LLM/API cụ thể. Wording "AI hỗ trợ" không đồng nghĩa với "Real LLM".

### 3.3 Current Code Evidence

**FACT.** `backend/app/services/ai_service.py`:
```python
# Line 19 — Regex matching
qty_match = re.search(r'(\d+)\s*(cái|chiếc|bộ|hộp|máy|laptop|máy tính)', text_lower)
# Line 23-31 — Hardcoded keyword detection
if "laptop" in text_lower:
    item_name = "Laptop Dell Vostro Workstation"
    unit_price = 25_000_000
```

**FACT.** Anomaly detection (REQ-FR-15):
```python
# Line 56 — Hardcoded historical average
historical_avg_price = 25_000_000
# Line 70 — 20% threshold đúng với requirement
is_anomaly = price_diff_ratio >= 0.20
```

**FACT.** Không có external API call, không có `import openai`, không có `import google.generativeai`, không có HTTP requests đến LLM providers.

### 3.4 Requirement Mapping

| Requirement | Expected Behavior | Current Implementation | Status |
|:---|:---|:---|:---|
| REQ-FR-03 (Should) | Standardize PR, gợi ý thông tin thiếu | Regex extract keywords → hardcoded output | PARTIAL — chỉ nhận ra ~4 từ khóa cố định |
| REQ-FR-13 (Must) | "Phân tích và hiển thị kết quả so sánh Quotation" | So sánh price diff với `historical_avg_price = 25,000,000` cứng | PARTIAL — so sánh có nhưng historical avg không phải dữ liệu thực |
| REQ-FR-14 (Should) | Recommendation dựa trên tiêu chí | Không có Recommendation output rõ ràng trong API response | NOT MET |
| REQ-FR-15 (Should) | Cảnh báo ≥20% vs lịch sử | Logic 20% threshold đúng, nhưng `historical_avg_price` cứng | PARTIAL — logic đúng, data sai |
| ASM-07 | Trích xuất từ file Quotation | Không xử lý file thực (chỉ nhận `files: List[str]` - tên file) | NOT MET — tên file được truyền nhưng không parse |

### 3.5 Gap Analysis

**Gaps của implementation Regex hiện tại:**
1. REQ-FR-03: Chỉ nhận diện 4 loại sản phẩm cứng. Text mô tả tự do không được xử lý đúng.
2. REQ-FR-13: `historical_avg_price` là hằng số 25,000,000 — không phải dữ liệu lịch sử thực tế.
3. REQ-FR-14: Không có Recommendation output trong response schema hiện tại.
4. ASM-07: File Quotation (PDF) không được parse thực sự.

**Điều Regex CÓ THỂ đáp ứng:**
- Logic threshold 20% (REQ-FR-15) — đã implement đúng về cấu trúc.
- Hiển thị kết quả comparison (REQ-FR-13) — đã có output structure.
- Anomaly flag (REQ-FR-15) — `is_anomaly` đã tồn tại.

### 3.6 Human Decision Required

**HD-03 chưa thể tự quyết định vì:**
- Project requirement không chỉ định implementation method.
- Giáo trình không bắt buộc Real LLM.
- Tuy nhiên, REQ-FR-13 (Must) và ASM-07 có thể được teacher đánh giá là "không đủ" với Regex cứng.

**Câu hỏi cụ thể cho human:**
1. REQ-FR-13 được đánh giá là "pass" ở mức Regex so sánh price diff, hay cần AI analysis thực sự?
2. ASM-07 ("AI có thể trích xuất từ file Quotation") có phải implement file parsing không?
3. REQ-FR-14 Recommendation có phải implement không (priority là "Should")?

**Status: NEEDS HUMAN DECISION**

---

## 4. HD-05 — E2E Critical Path Strategy

### 4.1 Course Requirement

**FACT.** Giao_trinh.txt Section 15.1 (Bài cuối), Line 621:
> "4. **Tự động hóa critical path E2E**; unit/integration cho logic quan trọng."

**FACT.** Giao_trinh.txt Section 15.2 Rubric, Line 639:
> "Automated testing & bug quality — **6 điểm** (trong 42 điểm nhóm)"

**FACT.** Giao_trinh.txt Section 16.2 (Báo cáo lần 2), Line 685-686:
> "3:00-4:30: Mở code/PR/test — Evidence: **PR diff + test output**"

**CONCLUSION (COURSE):** E2E testing là **COURSE REQUIREMENT BẮT BUỘC** cho Bài cuối. Phải có automated critical path E2E với execution evidence (test output). Section 18 (Case mẫu) minh họa cụ thể Playwright spec và test strategy — đây là **tham khảo về độ sâu**, không bắt buộc dùng chính xác tool Playwright.

### 4.2 Project Requirement

| User Story | Flow | AC |
|:---|:---|:---|
| US-01 | Employee tạo PR | AC1: Validation hiển thị khi thiếu field. AC3: Submit khi đủ thông tin |
| US-03 | Manager Approve/Reject PR | AC2: Approve ghi nhận và tiếp tục workflow |
| US-09 | Procurement tạo PO từ PR đã Approved | AC1: Cho phép tạo PO. AC2: Chặn nếu PR chưa Approved |
| US-10 | Ghi nhận Receiving | AC2: Chặn qty vượt PO |
| US-11 | Close PR sau khi Receiving hoàn tất | AC1: Cho phép Close. AC2: Chặn nếu chưa hoàn tất |

### 4.3 Current E2E Evidence

**FACT.** File `docs/06-testing/playwright-e2e-us09.spec.ts` tồn tại, 141 lines, viết Playwright syntax chuẩn.

**FACT — UNVERIFIED CLAIM:** Không có execution evidence (test output, CI log, screenshot) chứng minh file này từng được chạy thành công.

**FACT.** `frontend/package.json` — chưa đọc. Playwright có thể chưa được cài.

### 4.4 Frontend/E2E Mismatch

**FACT.** `frontend/src/App.tsx` là Single Page Application, không có React Router.

| Playwright Selector | Exists in App.tsx DOM? | Evidence |
|:---|:---|:---|
| `page.goto('/login')` | NO — route không tồn tại | App.tsx: không có Router |
| `page.goto('/pr')` | NO — route không tồn tại | App.tsx: không có Router |
| `table.comparison-table` | NO — class không tồn tại | App.tsx: không có class này |
| `.supplier-card` | NO — class không tồn tại | App.tsx: không có class này |
| `span.status-badge` | NO — class không tồn tại | App.tsx: không có class này |
| `input[name="unitPrice"][readonly]` | NO — field không tồn tại | App.tsx: không có input này |
| `button:has-text("Đăng xuất")` | UNKNOWN — chưa verify App.tsx đầy đủ | Cần kiểm tra |

**CONCLUSION:** Playwright spec hiện tại **KHÔNG THỂ EXECUTE** trên frontend hiện tại. Đây là UNVERIFIED CLAIM.

### 4.5 Critical Paths

Dựa trên requirements và user stories, các critical paths cần E2E coverage:

| # | Flow | Requirement / User Story | Figma Evidence | Current Frontend Route | Existing E2E Spec | Can Execute Now? | Gap |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | Employee tạo PR | US-01 / REQ-FR-01 | Có màn hình | Không có route `/pr/create` | Không có spec | NO | Không có route, không có spec |
| 2 | Manager Approve PR | US-03 / REQ-FR-06 | Có màn hình Approval | Không có route approval | Không có spec | NO | Không có route, không có spec |
| 3 | Procurement tạo PO (PR đã Approved) | US-09 / REQ-FR-16 | Có flow Quotation+PO | Không có route `/pr/:id/comparison` | `playwright-e2e-us09.spec.ts` | NO | Selectors không match DOM |
| 4 | Ghi nhận Receiving | US-10 / REQ-FR-17 | Có màn hình | Không có route | Không có spec | NO | Không có route, không có spec |
| 5 | Close PR | US-11 / REQ-FR-18 | UNKNOWN | Không có route | Không có spec | NO | Không có route, không có spec |

### 4.6 Gap Analysis

**Gap 1 — Course requirement gap:** Giáo trình bắt buộc "Tự động hóa critical path E2E" nhưng hiện tại **không có E2E nào executable**.

**Gap 2 — Frontend architecture gap:** Toàn bộ Playwright spec giả định multi-route SPA (React Router + `/login`, `/pr`, `/pr/:id/comparison`). Frontend hiện tại không có routing.

**Gap 3 — Chicken-and-egg:** E2E cần route/DOM ổn định → Frontend cần rewrite → Frontend rewrite cần E2E strategy được quyết định trước.

### 4.7 Human Decision Required

Các strategies có evidence support:

**Strategy A — Sửa test theo SPA hiện tại:**
- Cập nhật selectors/flow để match với `App.tsx` state-based UI.
- Có thể execute ngay nhưng test quality thấp (SPA không có URL, khó test navigation).
- Không align với Figma flows.

**Strategy B — Rebuild E2E sau khi rewrite Frontend:**
- Frontend được rewrite với routing trước → E2E được viết lại match DOM thực.
- Đảm bảo execution evidence có giá trị.
- Phụ thuộc vào quyết định Frontend Architecture.
- Timeline dài hơn.

**Strategy C — Defer E2E, tập trung Backend + Manual:**
- Giữ Playwright spec như documentation.
- Chỉ rely vào backend pytest tests (đang PASS).
- **Rủi ro:** Không đáp ứng course requirement "Tự động hóa critical path E2E" (6 điểm).

**Status: NEEDS HUMAN DECISION** — Nhưng lưu ý Strategy C có rủi ro điểm rubric.

---

## 5. HD-07 — Receiving Complete

### 5.1 Requirement Evidence

**FACT.** `requirements.md` REQ-BR-11 (Line 54):
> "Purchase Request chỉ được Close sau khi bước **Receiving và các bước mua sắm liên quan hoàn tất**."

**FACT.** `user-story.md` US-11 AC1 (Line 363-366):
> "Given Receiving **và các bước liên quan đã hoàn tất** / When người dùng có quyền Close / Then hệ thống cho phép chuyển sang Closed."

**FACT.** `user-story.md` US-11 AC2 (Line 368-371):
> "Given Receiving hoặc các bước liên quan **chưa hoàn tất** / When người dùng cố gắng Close / Then hệ thống **không cho phép Close**."

**FACT.** `requirements.md` ASM-06:
> "Trong MVP, tổng số lượng Receiving không được vượt quá số lượng trên PO."

→ ASM-06 định nghĩa điều kiện liên quan đến Receiving quantity.

### 5.2 Schema Evidence

**FACT.** `backend/prisma/schema.prisma` — Model `Receiving` (Lines 133-141):
```prisma
model Receiving {
  id              String        @id @default(uuid())
  purchaseOrderId String
  purchaseOrder   PurchaseOrder @relation(...)
  receivedQty     Int
  receivedItems   String
  receivedDate    DateTime      @default(now())
  fileUrl         String
}
```

**FACT.** Model `PurchaseOrder` (Lines 118-131):
```prisma
model PurchaseOrder {
  status  String  @default("SENT")
  ...
}
```

→ Schema định nghĩa `status` dưới dạng String (không phải Enum), giá trị default là `"SENT"`. Không có giá trị enum `RECEIVED` được định nghĩa trong schema.

**FACT.** MockDB (`procurement_service.py`): PO được tạo với `"status": "SENT"`. Không có logic nào cập nhật PO status sang `RECEIVED` khi nhận đủ hàng.

### 5.3 Code Evidence

**FACT.** `backend/app/services/procurement_service.py` — `receive_goods()` (Lines 127-151):
```python
# Validate: tổng receivedQty không được vượt po["quantity"]  ← ENFORCE ASM-06
if total_already_received + received_qty > po["quantity"]:
    raise ValueError(...)
# Sau khi validate: ghi nhận Receiving record
rec_record = { "id": ..., "poId": po_id, "receivedQty": received_qty, "fileUrl": file_url }
db.receivings[po_id].append(rec_record)
# ← KHÔNG cập nhật po["status"] sang "RECEIVED" khi đủ qty
```

**FACT.** `backend/app/services/procurement_service.py` — `close_pr()` (Lines 154-168):
```python
def close_pr(pr_id: str, finance_user: str):
    pr = db.prs.get(pr_id)
    if not pr:
        raise ValueError(...)
    # ← KHÔNG check: có PO không? PO đã nhận đủ chưa? Receiving records có không?
    db.budgets[dept_id]["tempReservedAmount"] -= estimated_val
    db.budgets[dept_id]["spentAmount"] += estimated_val
    pr["status"] = "CLOSED"
    return pr
```

**FACT.** `backend/tests/test_business_rules.py` — KHÔNG có test case nào kiểm tra việc `close_pr()` bị chặn khi Receiving chưa hoàn tất.

### 5.4 Candidate Definitions

| Candidate Definition | Source Evidence | Supported by Source? | Missing Information |
|:---|:---|:---|:---|
| **A: `sum(receivedQty) >= po.quantity`** | ASM-06 ("tổng số lượng Receiving không vượt quá PO qty") + `receive_goods()` enforce điều này | PARTIAL — ASM-06 là điều kiện prevent over-receiving, không phải điều kiện Close PR | Cần confirm: "đủ qty" có phải điều kiện Close không? |
| **B: `PO.status == "RECEIVED"`** | Schema có `status String` nhưng không có enum `RECEIVED`. MockDB không có transition logic | NOT SUPPORTED — Schema và code không định nghĩa trạng thái này | Schema cần thêm "RECEIVED" status; logic transition cần implement |
| **C: Có ít nhất 1 Receiving record** | Schema và code cho phép nhiều Receiving records theo PO | WEAK SUPPORT — có thể đọc từ `db.receivings.get(po_id, [])` | REQ-BR-11 nói "hoàn tất", không phải "có ít nhất 1" |
| **D: Điều kiện khác (từ Business)** | REQ-BR-11 nói "Receiving và các bước mua sắm liên quan hoàn tất" | AMBIGUOUS — "bước liên quan" chưa được định nghĩa | Cần clarification từ BA/PO về "các bước liên quan" là gì |

### 5.5 Missing Information

1. "Receiving hoàn tất" chưa được định nghĩa kỹ thuật trong requirement hay schema.
2. `PO.status` chưa có transition logic: SENT → PARTIALLY_RECEIVED → RECEIVED.
3. Prisma schema định nghĩa `PRStatus` enum có `PARTIALLY_RECEIVED` và `RECEIVED` — nhưng đây là **PR status**, không phải PO status.
4. Tests hiện tại (test_business_rules.py) KHÔNG cover việc chặn Close PR khi chưa có Receiving.

### 5.6 Human Decision Required

**Câu hỏi cụ thể:**

1. "Receiving hoàn tất" có nghĩa là gì? (A, B, C, hoặc D ở bảng trên?)
2. Có bắt buộc phải implement PO status transition (SENT → PARTIALLY_RECEIVED → RECEIVED) không?
3. "Các bước mua sắm liên quan hoàn tất" (REQ-BR-11) bao gồm những bước nào ngoài Receiving?

**Status: NEEDS HUMAN DECISION / REQUIREMENT CLARIFICATION**

---

## 6. Decisions That Are NOT Actually Open

### HD-04 (create_po guard) — NOT Open

Đây **KHÔNG phải** là open decision về "có cần guard không". Requirement đã rõ:

- **REQ-BR-10 (FACT):** "Purchase Order chỉ được tạo sau khi Purchase Request được Approve."
- **US-09 AC2 (FACT):** "Given PR chưa Approved — Then hệ thống KHÔNG cho phép tạo PO."

**FACT:** Code hiện tại KHÔNG có guard này (BUG-001).

→ **Decision thực sự chỉ là:** Implementation approach cho guard, không phải "có cần guard không". Guard là requirement fact. Chỉ cần human confirm **scope của fix** (chỉ add status check, hay cũng validate quotation từ DB?).

### HD-07 (close_pr) — PARTIALLY open

Requirement rõ ràng rằng Receiving completion là điều kiện. Decision còn mở chỉ là **định nghĩa kỹ thuật của "hoàn tất"**, không phải "có cần check Receiving không".

---

## 7. Recommended Decision Questions

Danh sách câu hỏi cụ thể để HUMAN trả lời:

**HD-03 (AI):**
1. REQ-FR-13 ("Must") — Hệ thống hiển thị kết quả so sánh Quotation: Regex price diff có đủ để đánh giá là "pass" không, hay cần AI analysis thực sự?
2. ASM-07 — "AI trích xuất từ file Quotation" có phải implement file parsing không?
3. REQ-FR-14 ("Should") — Recommendation có phải implement không trong Final Delivery?

**HD-05 (E2E):**
4. Giáo trình yêu cầu "Tự động hóa critical path E2E" (6/42 điểm nhóm). Nhóm chọn strategy nào:
   - A: Sửa Playwright spec cho App.tsx SPA hiện tại?
   - B: Rewrite frontend trước, rồi viết E2E?
   - C: Defer E2E, chỉ dùng backend pytest? (Rủi ro: thiếu 6 điểm rubric)
5. Critical paths nào bắt buộc phải có E2E? (Tối thiểu bao nhiêu flow?)

**HD-07 (close_pr):**
6. "Receiving hoàn tất" được định nghĩa theo cách nào?
   - A: `sum(receivedQty) >= po.quantity`
   - B: PO phải ở status cụ thể (nếu chọn B, cần thêm vào schema và implement transition)
   - C: Có ít nhất 1 Receiving record là đủ
7. "Các bước mua sắm liên quan hoàn tất" (REQ-BR-11) ngoài Receiving còn bước nào không?

---

## 8. Evidence Index

| Evidence Type | File / Location | Section / Function | Used For |
|:---|:---|:---|:---|
| Course requirement (E2E bắt buộc) | Giao_trinh.txt:L621 | Section 15.1 Task 4 | HD-05 |
| Course rubric (6 điểm automated testing) | Giao_trinh.txt:L639 | Section 15.2 | HD-05 |
| Case mẫu (Voice Commerce - LLM optional) | Giao_trinh.txt:L780, L1850 | Section 18 header + Runbook | HD-03 |
| REQ-FR-03 AI standardize (Should) | requirements.md | FR section | HD-03 |
| REQ-FR-13 AI compare (Must) | requirements.md | FR section | HD-03 |
| REQ-FR-14 AI recommendation (Should) | requirements.md | FR section | HD-03 |
| REQ-FR-15 AI anomaly 20% (Should) | requirements.md | FR section | HD-03 |
| REQ-BR-11 Close condition | requirements.md:L54 | BR section | HD-07 |
| ASM-06 Receiving qty limit | requirements.md:L82 | ASM section | HD-07 |
| ASM-07 AI file extraction | requirements.md:L83 | ASM section | HD-03 |
| US-09 AC2 (PO guard) | user-story.md:L307-310 | US-09 | HD-04 reference |
| US-11 AC1/AC2 (Close condition) | user-story.md:L363-371 | US-11 | HD-07 |
| `ai_service.py` regex implementation | backend/app/services/ai_service.py:L1-89 | All functions | HD-03 |
| `create_po()` missing guard | backend/app/services/procurement_service.py:L101-124 | create_po | HD-04 reference |
| `close_pr()` missing receiving check | backend/app/services/procurement_service.py:L154-168 | close_pr | HD-07 |
| `receive_goods()` qty validation | backend/app/services/procurement_service.py:L127-151 | receive_goods | HD-07 |
| Prisma `Receiving` model | backend/prisma/schema.prisma:L133-141 | Model | HD-07 |
| Prisma `PurchaseOrder.status` (String, no enum) | backend/prisma/schema.prisma:L128 | Model | HD-07 |
| Playwright spec selectors | docs/06-testing/playwright-e2e-us09.spec.ts:L41-98 | Test scenarios | HD-05 |
| App.tsx no-router | frontend/src/App.tsx | Entire file | HD-05 |
| test_business_rules.py no Close test | backend/tests/test_business_rules.py:L1-75 | All tests | HD-07 |

---

## 9. Verification Limitations

Những gì **KHÔNG THỂ XÁC MINH** từ source hiện tại:

1. **E2E execution:** Playwright tests chưa được execute (không có test output, CI log, hay screenshot).
2. **Backend tests trên real DB:** `test_all_endpoints.py` và `test_business_rules.py` chỉ chạy trên MockDB. Không thể verify behavior với PostgreSQL thực.
3. **AI output quality:** Không có benchmark test nào đo accuracy của AI standardization so với real-world input.
4. **Frontend package.json (Playwright):** Chưa đọc file này để xác minh Playwright có được cài không.
5. **Figma screen details:** Figma MCP không accessible trực tiếp trong session này; chỉ dựa vào `FIGMA_IMPLEMENTATION_SPEC.md` đã được tạo trước.
6. **Course teacher intent:** Không thể xác minh teacher có bắt buộc Real LLM hay chấp nhận Regex cho project AI Procurement cụ thể này.

---

*Tài liệu này được tạo bằng AI (Antigravity) sau khi đọc trực tiếp: Giao_trinh.txt (2280 lines), requirements.md, user-story.md, ai_service.py, procurement_service.py, schema.prisma, test_business_rules.py, test_all_endpoints.py, playwright-e2e-us09.spec.ts, App.tsx (thông qua previous session), FIGMA_IMPLEMENTATION_SPEC.md, FINAL_CROSS_SOURCE_VALIDATION.md, HUMAN_DECISION_BRIEF.md. Không có source code nào bị thay đổi.*

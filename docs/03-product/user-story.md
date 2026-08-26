
### Epic → User Story → Requirement

| **Epic**    | **Epic Name**            | **User Story**                                     | **Requirement IDs**                   |
| ----------- | ------------------------ | -------------------------------------------------- | ------------------------------------- |
| **EPIC-01** | **Purchase Request**     | **US-01:** Tạo và chuẩn hóa Purchase Request       | `REQ-FR-01`, `REQ-FR-02`, `REQ-FR-03` |
|             |                          | **US-02:** Theo dõi Purchase Request               | `REQ-FR-04`                           |
| **EPIC-02** | **Approval & Budget**    | **US-03:** Xem và xử lý Approval                   | `REQ-FR-05`, `REQ-FR-06`, `REQ-FR-07` |
|             |                          | **US-04:** Kiểm tra Budget                         | `REQ-FR-08`, `REQ-FR-09`              |
| **EPIC-03** | **Supplier & Quotation** | **US-05:** Quản lý Supplier và thu thập Quotation  | `REQ-FR-10`, `REQ-FR-11`              |
|             |                          | **US-06:** So sánh Quotation                       | `REQ-FR-12`                           |
|             |                          | **US-07:** AI phân tích và Recommendation          | `REQ-FR-13`, `REQ-FR-14`              |
|             |                          | **US-08:** AI cảnh báo bất thường                  | `REQ-FR-15`,            |
| **EPIC-04** | **Purchase Order**       | **US-09:** Lựa chọn Supplier và tạo Purchase Order | `REQ-FR-16`                           |
| **EPIC-05** | **Receiving & Close**    | **US-10:** Ghi nhận Receiving                      | `REQ-FR-17`                           |
|             |                          | **US-11:** Close Purchase Request                  | `REQ-FR-18`                           |


### 5 Epic theo workflow

**EPIC-01 — Purchase Request**

> FR-01 → FR-04

**EPIC-02 — Approval & Budget**

> FR-05 → FR-09

**EPIC-03 — Supplier & Quotation**

> FR-10 → FR-14

**EPIC-04 — Purchase Order**

> FR-15

**EPIC-05 — Receiving & Close**

> FR-16 → FR-17

Và thứ tự Epic cũng khớp hoàn toàn với workflow bắt buộc:

**Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close** (`CON-01`). 

### Các requirement không nên biến thành User Story riêng

* **NFR-01 → NFR-03**: yêu cầu phi chức năng, nên áp dụng xuyên suốt các Epic.
* **BR-01 → BR-11**: Business Rules, dùng làm điều kiện/Acceptance Criteria cho các Story tương ứng.
* **CON-01 → CON-06**: Constraints, áp dụng cho toàn project.
* **ASM-01 → ASM-08**: Assumptions, dùng làm cơ sở triển khai MVP.  
* **Q-01 → Q-05**: Open Questions, chưa nên biến thành Story cho đến khi được validation.



# EPIC-01 — Purchase Request

## US-01 — Tạo và chuẩn hóa Purchase Request

**Là một Employee, tôi muốn tạo và hoàn thiện Purchase Request với sự hỗ trợ của AI, để tôi có thể gửi yêu cầu mà không bị thiếu thông tin cần thiết.**

**Context:**
Bao gồm `REQ-FR-01`, `REQ-FR-02`, `REQ-FR-03` và `REQ-BR-01`. Employee có thể gặp khó khăn trong việc xác định những thông tin cần thiết khi tạo Purchase Request. AI hỗ trợ chuẩn hóa và gợi ý thông tin còn thiếu trước khi Submit.

**Acceptance Criteria:**

**AC1**
**Given** Employee đang tạo một Purchase Request
**When** có thông tin bắt buộc bị thiếu
**Then** hệ thống xác định thông tin còn thiếu trước khi Submit.

**AC2**
**Given** Purchase Request có thông tin bị thiếu
**When** Employee sử dụng chức năng hỗ trợ của AI
**Then** AI gợi ý những thông tin cần được bổ sung.

**AC3**
**Given** Purchase Request đã có đầy đủ thông tin cần thiết
**When** Employee Submit request
**Then** hệ thống cho phép Purchase Request được gửi đi.

**Out of Scope:**
Approval; thu thập Quotation; cấu hình Budget.

**Dependencies:**
Cấu trúc dữ liệu Purchase Request; AI Standardization.

**Estimate:** 3 pts

---

## US-02 — Theo dõi trạng thái Purchase Request

**Là một Employee, tôi muốn theo dõi trạng thái Purchase Request của mình, để tôi biết tiến độ của yêu cầu trong quy trình mua sắm.**

**Context:**
Bao gồm `REQ-FR-04`. Employee cần theo dõi trạng thái hiện tại của Purchase Request trong quá trình xử lý.

**Acceptance Criteria:**

**AC1**
**Given** Employee có một Purchase Request
**When** Employee xem request
**Then** hệ thống hiển thị trạng thái hiện tại của request.

**AC2**
**Given** Purchase Request tiến triển qua các bước của workflow
**When** Employee xem request
**Then** hệ thống hiển thị trạng thái hiện tại của quy trình.

**Out of Scope:**
Thay đổi trạng thái Purchase Request thủ công.

**Dependencies:**
Purchase Request Workflow.

**Estimate:** 2 pts

---

# EPIC-02 — Approval & Budget

## US-03 — Xem xét và xử lý Approval của Purchase Request

**Là một Manager, tôi muốn xem xét và xử lý Purchase Request, để tôi có thể đưa ra quyết định Approval đối với các request thuộc phạm vi của mình.**

**Context:**
Bao gồm `REQ-FR-05`, `REQ-FR-06`, `REQ-FR-07` và `REQ-BR-03`. Manager xem xét thông tin Purchase Request và có thể Approve, Reject hoặc yêu cầu chỉnh sửa.

**Acceptance Criteria:**

**AC1**
**Given** một Purchase Request đang chờ Approval
**When** Manager mở request
**Then** hệ thống hiển thị thông tin của Purchase Request.

**AC2**
**Given** Manager đang xem xét một Purchase Request thuộc phạm vi của mình
**When** Manager chọn Approve
**Then** hệ thống ghi nhận quyết định Approval và tiếp tục Approval Workflow.

**AC3**
**Given** Manager đang xem xét một Purchase Request
**When** Manager chọn Reject hoặc yêu cầu chỉnh sửa
**Then** hệ thống ghi nhận quyết định tương ứng.

**AC4**
**Given** Purchase Request đang trong Approval Workflow
**When** cần thực hiện bước Approval tiếp theo
**Then** hệ thống thực hiện theo Approval Workflow đã được cấu hình.

**Out of Scope:**
Xác định Approval hierarchy thực tế.

**Dependencies:**
Approval Workflow; vai trò Manager.

**Estimate:** 3 pts

---

## US-04 — Kiểm tra Purchase Request với Budget

**Là một Finance, tôi muốn kiểm tra Purchase Request với Budget, để tôi có thể xác định những request vượt quá Budget được cho phép.**

**Context:**
Bao gồm `REQ-FR-08`, `REQ-FR-09`, `REQ-BR-04`, `REQ-BR-05`. Finance kiểm tra Purchase Request với Budget trước khi hoàn thành bước Approval yêu cầu kiểm tra Budget.

**Acceptance Criteria:**

**AC1**
**Given** Purchase Request yêu cầu kiểm tra Budget
**When** Finance thực hiện kiểm tra request
**Then** hệ thống kiểm tra request với thông tin Budget khả dụng.

**AC2**
**Given** giá trị Purchase Request vượt quá Budget được cho phép
**When** thực hiện Budget Check
**Then** hệ thống hiển thị cảnh báo về Budget.

**Out of Scope:**
Xác định tiêu chí hoặc threshold cụ thể của Budget.

**Dependencies:**
Dữ liệu Budget; vai trò Finance.

**Estimate:** 2 pts

---

# EPIC-03 — Supplier & Quotation

## US-05 — Quản lý Supplier và thu thập Quotation

**Là một Procurement, tôi muốn quản lý thông tin Supplier và thu thập nhiều Quotation cho một Purchase Request, để tôi có đủ thông tin phục vụ việc so sánh.**

**Context:**
Bao gồm `REQ-FR-10`, `REQ-FR-11` và `REQ-BR-06`, `REQ-BR-07`. Procurement thu thập và so sánh Quotation sau khi Purchase Request được Approval. Thông tin Quotation được chuẩn hóa để phục vụ so sánh.

**Acceptance Criteria:**

**AC1**
**Given** Purchase Request đã được Approved
**When** Procurement thu thập Quotation
**Then** các Quotation có thể được liên kết với Purchase Request tương ứng.

**AC2**
**Given** có nhiều Quotation được thu thập cho một Purchase Request
**When** hệ thống xử lý các Quotation
**Then** thông tin của chúng được chuẩn hóa để phục vụ so sánh.

**Out of Scope:**
Supplier Portal.

**Dependencies:**
Purchase Request đã được Approved; dữ liệu Supplier và Quotation.

**Estimate:** 3 pts

---

## US-06 — So sánh Quotation

**Là một Procurement, tôi muốn so sánh Quotation từ nhiều Supplier, để tôi có thể đánh giá các lựa chọn Supplier hiện có.**

**Context:**
Bao gồm `REQ-FR-12`. User Research xác định việc so sánh thủ công nhiều Quotation là một khó khăn của Procurement. Hệ thống hỗ trợ so sánh các Quotation.

**Acceptance Criteria:**

**AC1**
**Given** có nhiều Quotation cho một Purchase Request
**When** Procurement mở chức năng Quotation Comparison
**Then** hệ thống hiển thị các Quotation để so sánh.

**AC2**
**Given** có Quotation từ nhiều Supplier
**When** Procurement thực hiện so sánh
**Then** hệ thống cho phép so sánh các Quotation dựa trên thông tin hiện có.

**Out of Scope:**
AI Recommendation; tự động lựa chọn Supplier.

**Dependencies:**
`US-05` — Thu thập và chuẩn hóa Quotation.

**Estimate:** 3 pts

---

## US-07 — AI phân tích và Recommendation Supplier

**Là một Procurement, tôi muốn AI phân tích kết quả so sánh Quotation và đưa ra Recommendation, để tôi có thể sử dụng thông tin Quotation nhằm hỗ trợ lựa chọn Supplier.**

**Context:**
Bao gồm `REQ-FR-13`, `REQ-FR-14`, `REQ-BR-08`, `REQ-BR-09`. AI phân tích kết quả so sánh Quotation và đưa ra Recommendation dựa trên thông tin và tiêu chí được sử dụng để so sánh. AI không đưa ra quyết định Supplier cuối cùng.

**Acceptance Criteria:**

**AC1**
**Given** nhiều Quotation đã được chuẩn bị để so sánh
**When** Procurement yêu cầu AI phân tích
**Then** AI hiển thị kết quả phân tích so sánh Quotation.

**AC2**
**Given** có thông tin Quotation và các tiêu chí so sánh
**When** AI tạo Recommendation
**Then** hệ thống hiển thị Recommendation dựa trên thông tin và các tiêu chí đó.

**AC3**
**Given** AI đã đưa ra Recommendation
**When** Procurement lựa chọn Supplier
**Then** quyết định lựa chọn Supplier cuối cùng vẫn thuộc về Procurement.

**Out of Scope:**
AI tự động lựa chọn Supplier.

**Dependencies:**
`US-05`; `US-06`; AI Analysis.

**Estimate:** 3 pts

---

# EPIC-04 — Purchase Order

## US-08 — Lựa chọn Supplier và tạo Purchase Order

**Là một Procurement, tôi muốn lựa chọn Supplier và tạo Purchase Order sau khi Purchase Request được Approval, để tôi có thể chuyển sang bước đặt hàng.**

**Context:**
Bao gồm `REQ-FR-15`, `REQ-BR-10` và `ASM-04`. Procurement lựa chọn Supplier và tạo Purchase Order chỉ sau khi Purchase Request được Approved.

**Acceptance Criteria:**

**AC1**
**Given** Purchase Request đã được Approved và Supplier đã được lựa chọn
**When** Procurement tạo Purchase Order
**Then** hệ thống cho phép tạo Purchase Order.

**AC2**
**Given** Purchase Request chưa được Approved
**When** Procurement cố gắng tạo Purchase Order
**Then** hệ thống không cho phép tạo Purchase Order.

**AC3**
**Given** thông tin Quotation đã được lựa chọn cho Purchase Order
**When** Purchase Order được tạo
**Then** AI không thay đổi thông tin Quotation đã được lựa chọn.

**Out of Scope:**
Tích hợp ERP/Kế toán; thanh toán Supplier.

**Dependencies:**
Purchase Request đã Approved; Supplier và Quotation đã được lựa chọn.

**Estimate:** 3 pts

---

# EPIC-05 — Receiving & Close

## US-09 — Ghi nhận Receiving

**Là một người dùng có quyền, tôi muốn ghi nhận việc Receiving hàng hóa hoặc dịch vụ, để quy trình mua sắm có thể ghi nhận việc giao nhận.**

**Context:**
Bao gồm `REQ-FR-16` và `ASM-06`. Người dùng có quyền phù hợp có thể ghi nhận Receiving. Theo giả định của MVP, tổng số lượng Receiving không được vượt quá số lượng trên PO.

**Acceptance Criteria:**

**AC1**
**Given** đã có Purchase Order
**When** người dùng có quyền ghi nhận Receiving
**Then** hệ thống ghi nhận thông tin Receiving.

**AC2**
**Given** số lượng Receiving sẽ vượt quá số lượng trên Purchase Order
**When** người dùng ghi nhận Receiving
**Then** hệ thống không cho phép tổng số lượng Receiving vượt quá số lượng trên PO.

**Out of Scope:**
Quản lý kho (Inventory Management).

**Dependencies:**
Purchase Order; quyền của người dùng.

**Estimate:** 2 pts

---

## US-10 — Đóng Purchase Request

**Là một người dùng có quyền, tôi muốn đóng Purchase Request sau khi các bước mua sắm hoàn tất, để Purchase Request kết thúc quy trình xử lý.**

**Context:**
Bao gồm `REQ-FR-17` và `REQ-BR-11`. Purchase Request chỉ có thể được Close sau khi Receiving và các bước mua sắm liên quan đã hoàn tất.

**Acceptance Criteria:**

**AC1**
**Given** Receiving và các bước mua sắm liên quan đã hoàn tất
**When** người dùng có quyền đóng Purchase Request
**Then** hệ thống cho phép Purchase Request được chuyển sang Closed.

**AC2**
**Given** Receiving hoặc các bước mua sắm liên quan chưa hoàn tất
**When** người dùng cố gắng Close Purchase Request
**Then** hệ thống không cho phép Purchase Request được Close.

**Out of Scope:**
Thanh toán Supplier; Quản lý kho (Inventory Management).

**Dependencies:**
Receiving đã hoàn tất.

**Estimate:** 2 pts



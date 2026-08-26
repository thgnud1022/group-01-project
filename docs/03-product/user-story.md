
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

Được. Dưới đây là bản **User Story tiếng Việt**, giữ đúng **cấu trúc mẫu trước đó**, đồng thời **bám sát bảng Epic → User Story → Requirement IDs bạn vừa chốt**. Không bổ sung requirement ngoài danh sách.

---

# EPIC-01 — Purchase Request

## US-01 — Tạo và chuẩn hóa Purchase Request

**Là một Employee, tôi muốn tạo và hoàn thiện Purchase Request với sự hỗ trợ của AI, để có thể gửi yêu cầu mà không thiếu thông tin cần thiết.**

**Context:**
Bao gồm `REQ-FR-01`, `REQ-FR-02`, `REQ-FR-03`. Employee có thể gặp khó khăn khi xác định thông tin cần cung cấp khi tạo Purchase Request. AI hỗ trợ chuẩn hóa và gợi ý thông tin còn thiếu trước khi Submit.

**Acceptance Criteria:**

**AC1**
Given Employee đang tạo Purchase Request
When có trường thông tin bắt buộc chưa được điền
Then hệ thống xác định và hiển thị thông tin còn thiếu trước khi Submit.

**AC2**
Given Purchase Request còn thiếu thông tin
When Employee sử dụng AI hỗ trợ
Then AI gợi ý thông tin cần được bổ sung.

**AC3**
Given Purchase Request đã có đầy đủ thông tin cần thiết
When Employee Submit
Then hệ thống cho phép gửi Purchase Request.

**Out of Scope:** Approval; Quotation; cấu hình Budget.

**Dependencies:** Purchase Request data structure; AI hỗ trợ chuẩn hóa.

**Estimate:** 3 pts

---

## US-02 — Theo dõi Purchase Request

**Là một Employee, tôi muốn theo dõi trạng thái Purchase Request, để biết yêu cầu của mình đang ở bước nào trong quy trình mua sắm.**

**Context:**
Bao gồm `REQ-FR-04`. Employee cần theo dõi trạng thái hiện tại của Purchase Request trong quá trình xử lý.

**Acceptance Criteria:**

**AC1**
Given Employee có một Purchase Request
When Employee xem Purchase Request
Then hệ thống hiển thị trạng thái hiện tại.

**AC2**
Given Purchase Request thay đổi trạng thái trong quy trình
When Employee xem lại Purchase Request
Then hệ thống hiển thị trạng thái mới nhất.

**Out of Scope:** Employee tự thay đổi trạng thái Purchase Request.

**Dependencies:** Purchase Request workflow.

**Estimate:** 2 pts

---

# EPIC-02 — Approval & Budget

## US-03 — Xem và xử lý Approval

**Là một Manager, tôi muốn xem và xử lý Purchase Request, để đưa ra quyết định Approval đối với các yêu cầu thuộc phạm vi của mình.**

**Context:**
Bao gồm `REQ-FR-05`, `REQ-FR-06`, `REQ-FR-07`. Manager xem thông tin Purchase Request và có thể Approve, Reject hoặc Request Revision.

**Acceptance Criteria:**

**AC1**
Given Purchase Request đang chờ Approval
When Manager mở Purchase Request
Then hệ thống hiển thị thông tin của Purchase Request.

**AC2**
Given Manager đang xem Purchase Request thuộc phạm vi xử lý
When Manager chọn Approve
Then hệ thống ghi nhận quyết định Approval và tiếp tục Approval Workflow.

**AC3**
Given Manager đang xem Purchase Request
When Manager chọn Reject hoặc Request Revision
Then hệ thống ghi nhận quyết định tương ứng.

**AC4**
Given Purchase Request đang trong Approval Workflow
When cần thực hiện bước Approval tiếp theo
Then hệ thống chuyển Purchase Request theo workflow được cấu hình.

**Out of Scope:** Thiết lập Approval hierarchy.

**Dependencies:** Approval Workflow; Manager role.

**Estimate:** 3 pts

---

## US-04 — Kiểm tra Budget

**Là một Finance user, tôi muốn kiểm tra Purchase Request với Budget, để xác định yêu cầu có vượt ngân sách hay không.**

**Context:**
Bao gồm `REQ-FR-08`, `REQ-FR-09`. Finance kiểm tra giá trị Purchase Request với thông tin Budget khi cần thực hiện Budget Review.

**Acceptance Criteria:**

**AC1**
Given Purchase Request cần được kiểm tra Budget
When Finance thực hiện Budget Check
Then hệ thống kiểm tra Purchase Request với thông tin Budget khả dụng.

**AC2**
Given Purchase Request vượt Budget
When Budget Check được thực hiện
Then hệ thống hiển thị cảnh báo Budget.

**Out of Scope:** Cấu hình tiêu chí hoặc hạn mức Budget.

**Dependencies:** Budget data; Finance role.

**Estimate:** 2 pts

---

# EPIC-03 — Supplier & Quotation

## US-05 — Quản lý Supplier và thu thập Quotation

**Là một Procurement user, tôi muốn quản lý thông tin Supplier và thu thập nhiều Quotation cho Purchase Request, để có đủ thông tin phục vụ việc so sánh.**

**Context:**
Bao gồm `REQ-FR-10`, `REQ-FR-11`. Procurement thu thập Quotation sau khi Purchase Request được Approval và thông tin Quotation được chuẩn hóa để phục vụ so sánh.

**Acceptance Criteria:**

**AC1**
Given Purchase Request đã được Approved
When Procurement thu thập Quotation
Then Quotation được liên kết với Purchase Request tương ứng.

**AC2**
Given có nhiều Quotation cho một Purchase Request
When hệ thống xử lý các Quotation
Then thông tin Quotation được chuẩn hóa theo cấu trúc thống nhất.

**Out of Scope:** Supplier Portal.

**Dependencies:** Approved Purchase Request; Supplier và Quotation data.

**Estimate:** 3 pts

---

## US-06 — So sánh Quotation

**Là một Procurement user, tôi muốn so sánh các Quotation từ nhiều Supplier, để đánh giá các phương án Supplier hiện có.**

**Context:**
Bao gồm `REQ-FR-12`. User Research xác định việc thu thập và so sánh nhiều Quotation là khó khăn đối với Procurement. Hệ thống hỗ trợ tổng hợp và so sánh các Quotation.

**Acceptance Criteria:**

**AC1**
Given có nhiều Quotation cho một Purchase Request
When Procurement mở chức năng Quotation Comparison
Then hệ thống hiển thị các Quotation để so sánh.

**AC2**
Given có Quotation từ nhiều Supplier
When Procurement thực hiện so sánh
Then hệ thống cho phép đối chiếu các thông tin của Quotation.

**Out of Scope:** AI Recommendation; tự động lựa chọn Supplier.

**Dependencies:** Quotation collection và standardization.

**Estimate:** 3 pts

---

## US-07 — AI phân tích và Recommendation

**Là một Procurement user, tôi muốn AI phân tích các Quotation và đưa ra Recommendation, để hỗ trợ tôi đánh giá và lựa chọn Supplier.**

**Context:**
Bao gồm `REQ-FR-13`, `REQ-FR-14`. AI phân tích thông tin Quotation và đưa ra Recommendation dựa trên các tiêu chí được sử dụng trong quá trình so sánh. AI không tự quyết định Supplier cuối cùng.

**Acceptance Criteria:**

**AC1**
Given có nhiều Quotation đã được chuẩn bị để so sánh
When Procurement yêu cầu AI phân tích
Then AI hiển thị kết quả phân tích Quotation.

**AC2**
Given có thông tin Quotation và các tiêu chí so sánh
When AI tạo Recommendation
Then hệ thống hiển thị Recommendation dựa trên các thông tin và tiêu chí đó.

**AC3**
Given AI đã đưa ra Recommendation
When Procurement lựa chọn Supplier
Then quyết định Supplier cuối cùng vẫn thuộc về Procurement.

**Out of Scope:** AI tự động lựa chọn Supplier.

**Dependencies:** Quotation Comparison; AI analysis.

**Estimate:** 3 pts

---

## US-08 — AI cảnh báo bất thường

**Là một Procurement user, tôi muốn AI phát hiện và cảnh báo các giá báo bất thường, để tôi có thể xem xét trước khi lựa chọn Supplier.**

**Context:**
Bao gồm `REQ-FR-15`. AI hỗ trợ phát hiện trường hợp giá báo có dấu hiệu bất thường dựa trên thông tin được sử dụng trong hệ thống.

**Acceptance Criteria:**

**AC1**
Given có Quotation được đưa vào phân tích
When AI kiểm tra thông tin giá
Then hệ thống xác định trường hợp giá bất thường theo tiêu chí đã được xác định.

**AC2**
Given AI phát hiện giá bất thường
When kết quả phân tích được hiển thị
Then hệ thống hiển thị cảnh báo để Procurement xem xét.

**AC3**
Given AI hiển thị cảnh báo bất thường
When Procurement đánh giá Quotation
Then Procurement vẫn là người đưa ra quyết định cuối cùng.

**Out of Scope:** AI tự động loại Supplier hoặc tự động quyết định Supplier.

**Dependencies:** Quotation data; AI analysis.

**Estimate:** 2 pts

---

# EPIC-04 — Purchase Order

## US-09 — Lựa chọn Supplier và tạo Purchase Order

**Là một Procurement user, tôi muốn lựa chọn Supplier và tạo Purchase Order sau khi Purchase Request được Approval, để tiếp tục bước đặt hàng.**

**Context:**
Bao gồm `REQ-FR-16`. Procurement lựa chọn Supplier và tạo Purchase Order sau khi Purchase Request đã được Approval.

**Acceptance Criteria:**

**AC1**
Given Purchase Request đã được Approved và Supplier đã được lựa chọn
When Procurement tạo Purchase Order
Then hệ thống cho phép tạo Purchase Order.

**AC2**
Given Purchase Request chưa được Approved
When Procurement cố gắng tạo Purchase Order
Then hệ thống không cho phép tạo Purchase Order.

**AC3**
Given thông tin Quotation đã được lựa chọn cho Purchase Order
When Purchase Order được tạo
Then thông tin được sử dụng để tạo PO được giữ nguyên.

**Out of Scope:** ERP/Accounting integration; Supplier Payment.

**Dependencies:** Approved Purchase Request; selected Supplier và Quotation.

**Estimate:** 3 pts

---

# EPIC-05 — Receiving & Close

## US-10 — Ghi nhận Receiving

**Là một người dùng có quyền, tôi muốn ghi nhận Receiving cho hàng hóa hoặc dịch vụ, để hệ thống ghi nhận việc nhận hàng trong quy trình mua sắm.**

**Context:**
Bao gồm `REQ-FR-17`. Người dùng có quyền có thể ghi nhận Receiving trong quá trình xử lý Purchase Order.

**Acceptance Criteria:**

**AC1**
Given có Purchase Order
When người dùng có quyền ghi nhận Receiving
Then hệ thống ghi nhận thông tin Receiving.

**AC2**
Given số lượng Receiving vượt quá số lượng trên Purchase Order
When người dùng ghi nhận Receiving
Then hệ thống không cho phép tổng số lượng Receiving vượt quá số lượng trên PO.

**Out of Scope:** Inventory Management.

**Dependencies:** Purchase Order; user permission.

**Estimate:** 2 pts

---

## US-11 — Đóng Purchase Request

**Là một người dùng có quyền, tôi muốn đóng Purchase Request sau khi các bước mua sắm hoàn tất, để Purchase Request kết thúc quy trình.**

**Context:**
Bao gồm `REQ-FR-18`. Purchase Request chỉ được Close sau khi Receiving và các bước liên quan đã hoàn tất.

**Acceptance Criteria:**

**AC1**
Given Receiving và các bước liên quan đã hoàn tất
When người dùng có quyền Close Purchase Request
Then hệ thống cho phép Purchase Request chuyển sang Closed.

**AC2**
Given Receiving hoặc các bước liên quan chưa hoàn tất
When người dùng cố gắng Close Purchase Request
Then hệ thống không cho phép Close.

**Out of Scope:** Supplier Payment; Inventory Management.

**Dependencies:** Receiving completion.

**Estimate:** 2 pts






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
| **EPIC-04** | **Purchase Order**       | **US-08:** Lựa chọn Supplier và tạo Purchase Order | `REQ-FR-15`                           |
| **EPIC-05** | **Receiving & Close**    | **US-09:** Ghi nhận Receiving                      | `REQ-FR-16`                           |
|             |                          | **US-10:** Close Purchase Request                  | `REQ-FR-17`                           |


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

Được. Mình sẽ giữ **đúng format của mẫu US-VC-05**, đồng thời **chỉ sử dụng thông tin đã có trong User Research + Project Charter + Requirements Inventory**. Những chỗ nguồn chưa xác định thì để **TBD**, không tự bịa.

# 18.14. Output #14 — Detailed User Stories

---

## US-PR-01 — Create and standardize Purchase Request

**As an Employee, I want to create and complete a Purchase Request with AI assistance, so that I can submit a request without missing necessary information.**

**Context:**
Covers `REQ-FR-01`, `REQ-FR-02`, `REQ-FR-03` and `REQ-BR-01`. Employee may have difficulty knowing which information is necessary when creating a Purchase Request. AI supports standardization and suggests missing information before Submit. 

**Acceptance Criteria:**

**AC1**
Given Employee is creating a Purchase Request
When required information is missing
Then the system identifies the missing information before Submit.

**AC2**
Given the Purchase Request has missing information
When Employee uses AI assistance
Then AI suggests the information that should be completed.

**AC3**
Given the Purchase Request contains the necessary information
When Employee submits the request
Then the system allows the Purchase Request to be submitted.

**Out of Scope:**
Approval; Quotation collection; Budget configuration.

**Dependencies:**
Purchase Request data structure; AI standardization.

**Estimate:** 3 pts

---

## US-PR-02 — Track Purchase Request status

**As an Employee, I want to track the status of my Purchase Request, so that I can know its progress in the procurement process.**

**Context:**
Covers `REQ-FR-04`. Employee needs to follow the current status of the Purchase Request during the process. 

**Acceptance Criteria:**

**AC1**
Given Employee has a Purchase Request
When Employee views the request
Then the system displays its current status.

**AC2**
Given the Purchase Request progresses through the workflow
When Employee views the request
Then the system displays its current process status.

**Out of Scope:**
Changing the Purchase Request status manually.

**Dependencies:**
Purchase Request workflow.

**Estimate:** 2 pts

---

# EPIC-02 — Approval & Budget

## US-AP-01 — Review and process Purchase Request Approval

**As a Manager, I want to review and process Purchase Requests, so that I can make an Approval decision for requests within my scope.**

**Context:**
Covers `REQ-FR-05`, `REQ-FR-06`, `REQ-FR-07` and `REQ-BR-03`. Manager reviews Purchase Request information and can Approve, Reject or request modification.  

**Acceptance Criteria:**

**AC1**
Given a Purchase Request is waiting for Approval
When Manager opens the request
Then the system displays the Purchase Request information.

**AC2**
Given Manager is reviewing a Purchase Request within their scope
When Manager selects Approve
Then the system records the Approval decision and continues the Approval Workflow.

**AC3**
Given Manager is reviewing a Purchase Request
When Manager selects Reject or requests modification
Then the system records the corresponding decision.

**AC4**
Given a Purchase Request is in the Approval Workflow
When the next approval step is required
Then the system follows the configured Approval Workflow.

**Out of Scope:**
Defining the actual Approval hierarchy.

**Dependencies:**
Approval Workflow; Manager role.

**Estimate:** 3 pts

---

## US-BG-01 — Check Purchase Request against Budget

**As a Finance user, I want to check a Purchase Request against the Budget, so that I can identify requests that exceed the permitted Budget.**

**Context:**
Covers `REQ-FR-08`, `REQ-FR-09`, `REQ-BR-04`, `REQ-BR-05`. Finance checks the Purchase Request against Budget before completing an approval step that requires Budget review.  

**Acceptance Criteria:**

**AC1**
Given a Purchase Request requires Budget checking
When Finance checks the Purchase Request
Then the system checks the request against the available Budget information.

**AC2**
Given the Purchase Request exceeds the permitted Budget
When the Budget check is performed
Then the system displays a Budget warning.

**Out of Scope:**
Defining the actual Budget criteria or threshold.

**Dependencies:**
Budget data; Finance role.

**Estimate:** 2 pts

---

# EPIC-03 — Supplier & Quotation

## US-QT-01 — Manage Supplier and collect Quotations

**As a Procurement user, I want to manage Supplier information and collect multiple Quotations for a Purchase Request, so that I can gather the information needed for comparison.**

**Context:**
Covers `REQ-FR-10`, `REQ-FR-11` and `REQ-BR-06`, `REQ-BR-07`. Procurement collects and compares Quotations after the Purchase Request is approved. Quotation information is standardized for comparison.  

**Acceptance Criteria:**

**AC1**
Given a Purchase Request has been Approved
When Procurement collects Quotations
Then the Quotations can be associated with the corresponding Purchase Request.

**AC2**
Given multiple Quotations are collected for a Purchase Request
When the system processes the Quotations
Then their information is standardized for comparison.

**Out of Scope:**
Supplier Portal.

**Dependencies:**
Approved Purchase Request; Supplier and Quotation data.

**Estimate:** 3 pts

---

## US-QT-02 — Compare Quotations

**As a Procurement user, I want to compare Quotations from multiple Suppliers, so that I can evaluate the available Supplier options.**

**Context:**
Covers `REQ-FR-12`. The User Research identifies manual comparison of multiple Quotations as a difficulty for Procurement. The system therefore supports comparison between Quotations. 

**Acceptance Criteria:**

**AC1**
Given multiple Quotations are available for a Purchase Request
When Procurement opens Quotation Comparison
Then the system displays the Quotations for comparison.

**AC2**
Given Quotations from multiple Suppliers are available
When Procurement compares them
Then the system allows the Quotations to be compared using their available information.

**Out of Scope:**
AI Recommendation; automatic Supplier selection.

**Dependencies:**
`US-QT-01` Quotation collection and standardization.

**Estimate:** 3 pts

---

## US-QT-03 — AI analysis and Supplier Recommendation

**As a Procurement user, I want AI to analyze Quotation comparisons and provide a Recommendation, so that I can use the available Quotation information to support my Supplier selection.**

**Context:**
Covers `REQ-FR-13`, `REQ-FR-14`, `REQ-BR-08`, `REQ-BR-09`. AI analyzes Quotation comparison results and provides a Recommendation based on the information and criteria used for comparison. AI does not make the final Supplier decision.  

**Acceptance Criteria:**

**AC1**
Given multiple Quotations have been prepared for comparison
When Procurement requests AI analysis
Then AI displays the Quotation comparison analysis.

**AC2**
Given Quotation information and comparison criteria are available
When AI generates a Recommendation
Then the system displays the Recommendation based on that information and criteria.

**AC3**
Given AI has provided a Recommendation
When Procurement makes the Supplier selection
Then the final Supplier decision remains with Procurement.

**Out of Scope:**
AI automatically selecting the Supplier.

**Dependencies:**
`US-QT-01`; `US-QT-02`; AI analysis.

**Estimate:** 3 pts

---

# EPIC-04 — Purchase Order

## US-PO-01 — Select Supplier and create Purchase Order

**As a Procurement user, I want to select a Supplier and create a Purchase Order after Purchase Request approval, so that I can proceed to the ordering step.**

**Context:**
Covers `REQ-FR-15`, `REQ-BR-10` and `ASM-04`. Procurement selects the Supplier and creates a Purchase Order only after the Purchase Request is approved.   

**Acceptance Criteria:**

**AC1**
Given the Purchase Request has been Approved and a Supplier has been selected
When Procurement creates a Purchase Order
Then the system allows the Purchase Order to be created.

**AC2**
Given the Purchase Request has not been Approved
When Procurement attempts to create a Purchase Order
Then the system does not allow the Purchase Order to be created.

**AC3**
Given Quotation information has been selected for the Purchase Order
When the Purchase Order is created
Then AI does not change the selected Quotation information.

**Out of Scope:**
ERP/Accounting integration; Supplier Payment.

**Dependencies:**
Approved Purchase Request; selected Supplier and Quotation.

**Estimate:** 3 pts

---

# EPIC-05 — Receiving & Close

## US-RC-01 — Record Receiving

**As an authorized user, I want to record Receiving for goods or services, so that the procurement process can record the receipt.**

**Context:**
Covers `REQ-FR-16` and `ASM-06`. Users with appropriate permissions can record Receiving. In the MVP assumption, the total Receiving quantity cannot exceed the quantity on the PO.  

**Acceptance Criteria:**

**AC1**
Given a Purchase Order exists
When an authorized user records Receiving
Then the system records the Receiving information.

**AC2**
Given the Receiving quantity would exceed the quantity on the Purchase Order
When the user records Receiving
Then the system does not allow the total Receiving quantity to exceed the PO quantity.

**Out of Scope:**
Inventory Management.

**Dependencies:**
Purchase Order; user permission.

**Estimate:** 2 pts

---

## US-CL-01 — Close Purchase Request

**As an authorized user, I want to close a Purchase Request after the procurement steps are completed, so that the Purchase Request reaches the end of the workflow.**

**Context:**
Covers `REQ-FR-17` and `REQ-BR-11`. A Purchase Request can only be closed after Receiving and related procurement steps are completed.  

**Acceptance Criteria:**

**AC1**
Given Receiving and the related procurement steps are completed
When an authorized user closes the Purchase Request
Then the system allows the Purchase Request to be Closed.

**AC2**
Given Receiving or related procurement steps are not completed
When an authorized user attempts to Close the Purchase Request
Then the system does not allow the Purchase Request to be Closed.

**Out of Scope:**
Supplier Payment; Inventory Management.

**Dependencies:**
Receiving completion.

**Estimate:** 2 pts

---

## Tổng cấu trúc sau khi chốt

| **Epic**                           | **User Stories**             | **FR được cover** |
| ---------------------------------- | ---------------------------- | ----------------- |
| **EPIC-01 — Purchase Request**     | US-PR-01, US-PR-02           | FR-01 → FR-04     |
| **EPIC-02 — Approval & Budget**    | US-AP-01, US-BG-01           | FR-05 → FR-09     |
| **EPIC-03 — Supplier & Quotation** | US-QT-01, US-QT-02, US-QT-03 | FR-10 → FR-14     |
| **EPIC-04 — Purchase Order**       | US-PO-01                     | FR-15             |
| **EPIC-05 — Receiving & Close**    | US-RC-01, US-CL-01           | FR-16 → FR-17     |


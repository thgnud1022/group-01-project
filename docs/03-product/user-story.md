
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

Cách này mapping **1-1 với Functional Requirements FR-01 → FR-17**, không bỏ requirement nào. 

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

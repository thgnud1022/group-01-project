# Business Rules - ProcureAI

> **Nguồn:** `docs/01-discovery/requirements.md`
>
> Tài liệu này chuẩn hóa các Business Rules đã có trong Requirements cho domain workflow. Không bổ sung rule mới ngoài nguồn đã được xác nhận.

## 1. Quy tắc nghiệp vụ

| ID | Business Rule | Đối tượng/Vai trò liên quan | Điểm áp dụng |
|:---|:---|:---|:---|
| **REQ-BR-01** | Purchase Request phải được tạo đầy đủ thông tin cần thiết trước khi được Submit. | Employee, Purchase Request | Request / Submit |
| **REQ-BR-02** | Purchase Request phải được Approve trước khi chuyển sang bước Collect Quotations. | Manager, Finance, Purchase Request | Approval → Collect Quotations |
| **REQ-BR-03** | Manager là người xem xét và đưa ra quyết định Approval đối với Purchase Request thuộc phạm vi của mình. | Manager, Purchase Request | Manager Review |
| **REQ-BR-04** | Finance kiểm tra Purchase Request với Budget trước khi hoàn tất bước phê duyệt có yêu cầu kiểm tra ngân sách; Manager có thể chuyển PR sang Finance thay vì tự phê duyệt khi cần kiểm tra ngân sách. | Manager, Finance, Budget, Purchase Request | Budget Check / Approval |
| **REQ-BR-05** | Purchase Request vượt giới hạn Budget phải được cảnh báo. | Finance, Manager, Budget, Purchase Request | Budget Check |
| **REQ-BR-06** | Procurement thực hiện thu thập và đối chiếu Quotation sau khi Purchase Request được Approve. | Procurement, Quotation, Purchase Request | Collect Quotations / Compare |
| **REQ-BR-07** | Các Quotation được thu thập phải được liên kết với Purchase Request tương ứng để phục vụ so sánh. | Procurement, Quotation, Purchase Request | Quotation Collection |
| **REQ-BR-08** | AI chỉ đưa ra Recommendation, không tự quyết định Supplier thay cho Procurement (Human-in-the-loop). | AI, Procurement, Supplier | Compare / Supplier Selection |
| **REQ-BR-09** | AI Recommendation dựa trên thông tin và tiêu chí được sử dụng để so sánh Quotation. | AI, Quotation, Supplier, Procurement | Quotation Comparison |
| **REQ-BR-10** | Purchase Order chỉ được tạo sau khi Purchase Request được Approve và Supplier được lựa chọn. | Procurement, Purchase Order, Supplier, Purchase Request | PO Creation |
| **REQ-BR-11** | Purchase Request chỉ được Close sau khi bước Receiving và các bước mua sắm liên quan hoàn tất. | Receiving, Purchase Request | Receiving → Close |

## 2. Quy trình bắt buộc

Quy trình MVP phải tuân theo thứ tự:

```text
Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close
```

Các bước không được bỏ qua:

- PR phải được Approve trước khi Collect Quotations.
- Supplier phải được lựa chọn trước khi tạo PO.
- Receiving phải hoàn tất trước khi Close.

## 3. Constraints liên quan đến domain

| ID | Constraint |
|:---|:---|
| **CON-01** | Quy trình nghiệp vụ phải tuân theo thứ tự: **Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close**. |
| **CON-02** | MVP tập trung vào 5 vai trò: **Employee, Manager, Procurement, Finance và Admin**. |
| **CON-03** | AI chỉ đóng vai trò **hỗ trợ**, không thay thế quyết định Approval hoặc quyết định lựa chọn Supplier của người dùng. |
| **CON-04** | MVP được triển khai trên **nền tảng web**. |
| **CON-05** | MVP không tích hợp trực tiếp với hệ thống **ERP hoặc kế toán tổng hợp**. |
| **CON-06** | Các chức năng **Inventory, Supplier Payment, Contract Management, ERP/Accounting Integration, Mobile App, Supplier Portal và Demand Forecasting** nằm ngoài phạm vi MVP. |

## 4. Assumptions cần lưu ý khi triển khai

Các mục sau là Assumptions trong Requirements, chưa phải Business Rules đã được xác nhận đầy đủ:

| ID | Assumption | Trạng thái |
|:---|:---|:---|
| **ASM-02** | Approval hierarchy và Budget threshold trong MVP là giả định và cần validation với doanh nghiệp thực tế. | Cần xác nhận |
| **ASM-03** | AI trong MVP chỉ đóng vai trò decision support, không thay thế quyết định của Manager, Finance hoặc Procurement. | Theo Human-in-the-loop |
| **ASM-05** | PR có giá trị trên 50 triệu VND được giả định cần cả Manager và Finance approval. | Cần xác nhận |
| **ASM-06** | Tổng số lượng Receiving không được vượt quá số lượng trên PO. | Cần xác nhận trong Business Rule chi tiết |
| **ASM-07** | AI có thể trích xuất thông tin từ file Quotation PDF/Excel do Procurement cung cấp. | Phụ thuộc dữ liệu đầu vào |

## 5. Open Questions ảnh hưởng Business Rules

| ID | Open Question |
|:---|:---|
| **Q-01** | Approval Workflow thực tế gồm những cấp phê duyệt nào? |
| **Q-03** | Budget được kiểm tra theo tiêu chí và giới hạn nào trong quy trình thực tế? |
| **Q-04** | Những tiêu chí nào được sử dụng để AI Recommendation Supplier từ các Quotation? |
| **Q-05** | Procurement cần những thông tin nào từ Supplier/Quotation để thực hiện việc so sánh và lựa chọn? |

## 6. Traceability

| Domain artifact | Requirements source |
|:---|:---|
| Purchase Request validation | REQ-BR-01 |
| Approval route | REQ-BR-02, REQ-BR-03, REQ-BR-04, REQ-BR-05 |
| Quotation collection and comparison | REQ-BR-06, REQ-BR-07, REQ-BR-08, REQ-BR-09 |
| Purchase Order creation | REQ-BR-10 |
| Receiving and Close | REQ-BR-11 |
| Workflow and AI constraints | CON-01, CON-02, CON-03 |

 ## AI Procurement & Purchase Approval System

Dựa trên các **User Stories, Functional Requirements và Business Rules** đã cung cấp.

Tập trung kiểm chứng 4 flow có rủi ro cao:

### FLOW A — Create & Standardize Purchase Request

Employee tạo Purchase Request
→ nhập thông tin
→ AI hỗ trợ chuẩn hóa Purchase Request
→ kiểm tra thông tin bắt buộc
→ nếu thiếu, AI gợi ý thông tin cần bổ sung
→ Submit Purchase Request
→ hiển thị Request Status.

### FLOW B — Approval & Budget Review

Purchase Request được Submit
→ Manager xem xét Purchase Request
→ Approve / Reject / Request Revision
→ nếu cần Budget Review → Finance kiểm tra Purchase Request với Budget
→ hiển thị Budget Warning nếu Purchase Request vượt Budget
→ tiếp tục Approval Workflow
→ hiển thị trạng thái Purchase Request.

### FLOW C — Quotation Collection & Comparison

Purchase Request đã Approved
→ Procurement quản lý Supplier
→ thu thập nhiều Quotation
→ liên kết Quotation với Purchase Request
→ chuẩn hóa thông tin Quotation
→ hiển thị bảng Quotation Comparison
→ Procurement đánh giá các Supplier.

### FLOW D — AI Analysis, Recommendation & Anomaly Alert

Có nhiều Quotation
→ Procurement yêu cầu AI phân tích
→ AI hiển thị kết quả phân tích / so sánh
→ AI đưa ra Recommendation
→ AI hiển thị Anomaly Alert khi phát hiện giá bất thường
→ Procurement xem kết quả
→ Procurement tự lựa chọn Supplier
→ tạo Purchase Order.

Prototype phải thể hiện rõ:

* Purchase Request form
* AI hỗ trợ chuẩn hóa Purchase Request
* AI suggestion cho thông tin còn thiếu
* Request status
* Approval decision
* Budget check / Budget warning
* Supplier information
* Quotation information
* Quotation comparison
* AI analysis
* AI Recommendation
* AI Anomaly Alert
* Quyền quyết định cuối cùng của Procurement

Bắt buộc có các state:

`draft`, `submitted`, `pending-approval`, `revision-required`, `approved`, `rejected`, `budget-warning`, `quotation-comparison`, `ai-recommendation`, `error`.

Không cho AI tự quyết định **Approval** hoặc **Supplier cuối cùng**. AI chỉ đưa ra **Recommendation** và **Anomaly Alert** để hỗ trợ người dùng.

Không tự tạo, sửa hoặc suy diễn dữ liệu **Supplier, Quotation, Budget** ngoài dữ liệu mẫu được cung cấp.

Prototype phải phản ánh đúng workflow:

**Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close**

Không đưa các chức năng ngoài phạm vi MVP vào prototype như:

* Inventory Management
* Supplier Payment
* Contract Management
* ERP/Accounting Integration
* Mobile App
* Supplier Portal
* Demand Forecasting

Trước khi tạo prototype, hãy **liệt kê riêng các Prototype Assumptions còn thiếu hoặc cần xác nhận**. Không đưa các assumption vào Requirements và không tự suy diễn các thông tin chưa được xác định.

Sau khi liệt kê assumptions, tạo prototype theo đúng các flow, role, requirement và business rules đã cung cấp. 

[Link Prototype](https://www.magicpatterns.com/c/utapnp7s8wvsxbtcfalh2b/preview?hideToolbar=true&path=%2Frequests%2FPR-2026-041)

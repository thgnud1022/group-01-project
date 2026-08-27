PRD - AI Procurement & Purchase Approval System

Status: Draft

1. Problem

Trong quy trình mua sắm nội bộ, Employee có thể gặp khó khăn khi tạo Purchase Request do thiếu thông tin cần thiết và phải bổ sung hoặc chỉnh sửa. Manager cần xem xét các thông tin của Purchase Request trước khi đưa ra quyết định Approval. Procurement phải thu thập và đối chiếu thông tin từ nhiều Quotation trước khi lựa chọn Supplier. Finance cần kiểm tra giá trị Purchase Request và Budget trước khi phê duyệt.

Các vấn đề trên được xác định từ Project Charter và User Research; kết quả User Research hiện sử dụng Stakeholder Proxy và business-process assumptions, vì vậy chưa được xem là insight đã được validation với người dùng thực tế.

2. Goals

G1. Chuẩn hóa quy trình mua sắm nội bộ theo luồng:
Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close.

G2. Hỗ trợ Employee tạo Purchase Request đầy đủ thông tin và theo dõi trạng thái của request.

G3. Hỗ trợ Manager và Finance trong quá trình Approval và Budget Review.

G4. Hỗ trợ Procurement quản lý Supplier, thu thập và so sánh nhiều Quotation.

G5. Sử dụng AI để hỗ trợ chuẩn hóa Purchase Request, phân tích/so sánh Quotation, đưa ra Recommendation và cảnh báo giá bất thường.

G6. Đảm bảo AI chỉ đóng vai trò hỗ trợ; quyết định Approval và lựa chọn Supplier cuối cùng vẫn do người dùng có thẩm quyền thực hiện.

3. Non-goals

Inventory Management.

Supplier Payment.

Contract Management.

ERP/Accounting Integration.

Mobile App.

Supplier Portal.

Demand Forecasting.

4. Users

Employee: Tạo và quản lý Purchase Request, cung cấp đầy đủ thông tin cần thiết và theo dõi trạng thái xử lý của request.

Manager: Xem xét thông tin Purchase Request và đưa ra quyết định Approve, Reject hoặc Request Revision đối với các request thuộc phạm vi quyền hạn.

Procurement: Sau khi Purchase Request được phê duyệt, thực hiện quản lý Supplier, thu thập và đối chiếu Quotation, đánh giá các lựa chọn Supplier và tạo Purchase Order.

Finance:  Kiểm tra giá trị Purchase Request với Budget và xác định request có nằm trong ngân sách cho phép trước khi thực hiện bước phê duyệt thuộc Finance.

Admin: quản lý người dùng, vai trò và cấu hình quy trình.



5. Functional Scope

Purchase Request

REQ-FR-01..04

Approval & Budget

REQ-FR-05..09

Supplier & Quotation

REQ-FR-10..12

AI Analysis & Recommendation

REQ-FR-13..15

Purchase Order

REQ-FR-16

Receiving

REQ-FR-17

Close Purchase Request

REQ-FR-18

Supporting Non-Functional Requirements

REQ-NFR-01..03

6. Business Rules

REQ-BR-01..11

Các rule chính bao gồm:

Purchase Request phải đầy đủ thông tin trước khi Submit.

Purchase Request phải được Approve trước khi Collect Quotations.

Manager thực hiện Approval đối với Purchase Request thuộc phạm vi của mình.

Finance kiểm tra Purchase Request với Budget khi có yêu cầu Budget Review.

Purchase Request vượt giới hạn Budget phải được cảnh báo.

Quotation phải được liên kết với Purchase Request tương ứng.

AI chỉ đưa ra Recommendation và không tự quyết định Supplier.

Purchase Order chỉ được tạo sau khi Purchase Request được Approve và Supplier được lựa chọn.

Purchase Request chỉ được Close sau khi Receiving và các bước mua sắm liên quan hoàn tất.

7. UX Principles

Các tài liệu hiện tại chưa xác định một bộ UX Principles riêng. Khi thiết kế giao diện, các nguyên tắc UX cụ thể cần được xác định và validation, không suy diễn thành yêu cầu nghiệp vụ.

Các màn hình và luồng UX cần phản ánh đúng workflow và quyền của từng role, đồng thời không để AI thay thế quyết định của người dùng.

8. Metrics / Acceptance Signals

≥80% Purchase Request được AI chuẩn hóa chính xác.

Giảm ít nhất 40% thời gian phê duyệt so với quy trình thủ công.

Giảm ít nhất 60% thời gian so sánh báo giá.

AI phát hiện ≥80% trường hợp giá bất thường trong bộ dữ liệu kiểm thử.

Người dùng đánh giá mức hài lòng ≥4/5.

Chỉ tiêu “AI phát hiện ≥80% trường hợp giá bất thường” được tách khỏi Budget Alert để tránh gộp chức năng AI với chức năng kiểm tra Budget của hệ thống.

9. Risks

Approval hierarchy chưa được xác định và cần validation.

Budget threshold và tiêu chí kiểm tra Budget chưa được xác định đầy đủ.

Các tiêu chí dùng cho AI Recommendation Supplier chưa được xác định.

Thông tin bắt buộc của Purchase Request chưa được xác định đầy đủ.

Thông tin cần thiết từ Supplier/Quotation để so sánh và lựa chọn chưa được xác định đầy đủ.

Dữ liệu Supplier, Quotation và Budget có thể phải sử dụng mock/sample trong MVP nếu chưa có dữ liệu doanh nghiệp thực tế.

Kết quả User Research hiện dựa trên Stakeholder Proxy và business-process assumptions, cần validation với người dùng thực tế.

AI không được tự ý thay đổi thông tin Quotation đã được lựa chọn khi tạo PO.

Tổng số lượng Receiving không được vượt quá số lượng trên PO trong phạm vi giả định của MVP.

10. Release Slice

MVP

MVP bao gồm toàn bộ luồng:

Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close

với các chức năng:

Tạo và quản lý Purchase Request.

Xem xét và phê duyệt Purchase Request.

Finance kiểm tra Purchase Request với Budget.

Quản lý Supplier và Quotation.

AI hỗ trợ chuẩn hóa Purchase Request.

AI hỗ trợ phân tích/so sánh Quotation và Recommendation.

AI cảnh báo giá bất thường.

Lựa chọn Supplier và tạo Purchase Order.

Ghi nhận Receiving.

Close Purchase Request.

MVP được triển khai trên nền tảng web và không tích hợp trực tiếp với ERP hoặc hệ thống kế toán.

Dependencies / Open Questions: Q-01..Q-05 cần được validation trước khi chốt các chi tiết nghiệp vụ tương ứng.

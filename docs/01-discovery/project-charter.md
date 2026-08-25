# PROJECT CHARTER: AI Procurement & Purchase Approval System

## 1. Thông Tin Tổng Quan
* **Tên dự án:** AI Procurement & Purchase Approval System
* **Nhóm thực hiện:** Nhóm 1 (5 thành viên)
* **Khóa học:** Thực hành Lập trình Ứng dụng Doanh nghiệp (MIS3032_1 - 2026)
* **Thời gian thực hiện:** 14 tuần

## 2. Bối Cảnh & Tuyên Bố Vấn Đề (Problem Statement)
Quy trình mua sắm nội bộ doanh nghiệp hiện tại bị phân mảnh, phụ thuộc vào xử lý thủ công qua email/giấy tờ, thiếu kiểm soát ngân sách theo thời gian thực và tiêu tốn nhiều giờ làm việc cho việc đọc hiểu, so sánh các bản báo giá phi cấu trúc.

1. **Đối với Nhân viên (Employee):** Khó khăn khi mô tả thông số kỹ thuật thiết bị chuẩn hóa và theo dõi trạng thái phê duyệt PR.
2. **Đối với Chuyên viên Thu mua (Procurement Specialist):** Mất nhiều thời gian đọc hiểu file PDF/ảnh báo giá từ nhiều nhà cung cấp và lập bảng đối chiếu thủ công, dễ bỏ sót nâng giá/gian lận.
3. **Đối với Quản lý & Finance (Manager & Finance Specialist):** Rủi ro phê duyệt dồn dập vượt hạn mức ngân sách phòng ban do thiếu công cụ kiểm tra tự động theo thời gian thực.

## 3. Định Vị Giá Trị (Value Proposition)
Tự động hóa thông minh quy trình thu mua từ khâu khởi tạo PR đến thanh quyết toán; tích hợp AI hỗ trợ chuẩn hóa PR từ văn bản thô, tự động trích xuất so sánh báo giá PDF, phát hiện bất thường đơn giá >= 20% , bảo vệ 100% ngân sách phòng ban theo thời gian thực.

## 4. Các Bên Liên Quan & Phân Quyền (Stakeholders)
* `EMPLOYEE`: Khởi tạo PR bằng voice/text, theo dõi trạng thái PR.
* `MANAGER`: Phê duyệt PR bước 1 <= 50 triệu VND).
* `PROCUREMENT`: Upload báo giá PDF, xem bảng so sánh AI, phát hành PO.
* `FINANCE`: Phê duyệt PR bước 2 (> 50 triệu VND), quản lý ngân sách phòng ban, đóng hồ sơ mua sắm.
* `ADMIN`: Quản trị người dùng, phòng ban, danh mục.

## 5. Tiêu Chí Thành Công (Success Signals)
1. 100% PR được kiểm tra ngân sách phòng ban tự động trước khi gửi duyệt.
2. Độ chính xác của AI khi bóc tách báo giá PDF đạt 90% trên tập câu hỏi benchmark.
3. 100% luồng duyệt giá trị lớn (> 50 triệu VND) bắt buộc qua bước duyệt thứ hai của Finance.
4. Thời gian trích xuất & so sánh báo giá của AI < 3.5 giây trong môi trường demo.

## 6. Ràng Buộc (Constraints)
* Bàn giao MVP trong 14 tuần học.
* Chỉ xử lý đơn vị tiền tệ VND.
* Không tích hợp cổng thanh toán ngân hàng thật.

# REQUIREMENTS INVENTORY: AI Procurement & Purchase Approval System

## A. Yêu Cầu Chức Năng (Functional Requirements - FR)

* **REQ-FR-01 (Must):** Hệ thống cho phép Employee khởi tạo PR bằng văn bản thô/giọng nói, AI hỗ trợ bóc tách, chuẩn hóa thành các trường thông tin: Tên hàng, Số lượng, Đơn giá dự kiến, Ngày mong muốn nhận hàng.
* **REQ-FR-02 (Must):** Hệ thống tự động kiểm tra ngân sách (Budget Check) phòng ban khả dụng ngay khi Employee bấm nút tạo PR và đưa ra cảnh báo trực quan nếu số tiền vượt hạn mức.
* **REQ-FR-03 (Must):** Manager có quyền duyệt hoặc từ chối PR kèm theo lý do cụ thể.
* **REQ-FR-04 (Must):** Luồng duyệt đa cấp tự động kích hoạt: PR có giá trị $> 50$ triệu VND sau khi Manager duyệt xong bắt buộc phải chuyển tiếp đến Finance để ký duyệt bước hai.
* **REQ-FR-05 (Must):** Procurement tải lên tối đa 3 file báo giá (PDF/ảnh) từ các nhà cung cấp khác nhau cho một mã PR.
* **REQ-FR-06 (Must):** AI thực hiện trích xuất dữ liệu từ các file báo giá và tự động lập bảng so sánh chi tiết: Tổng chi phí, Đơn giá, Chi phí vận chuyển, Thời gian giao hàng, Điều khoản bảo hành.
* **REQ-FR-07 (Must):** AI phân tích giá trị báo giá so với lịch sử thu mua và đưa ra cảnh báo bất thường (Anomaly Alert) nếu đơn giá cao vượt $\geq 20\%$ so với đơn giá trung bình lịch sử của sản phẩm cùng loại.
* **REQ-FR-08 (Must):** Procurement chọn báo giá tối ưu và bấm nút khởi tạo PO. Hệ thống tự động sao chép chính xác thông tin đơn giá, số lượng từ báo giá được chọn sang PO, trạng thái PR chuyển sang `PO_Created`.
* **REQ-FR-09 (Must):** Hệ thống ghi nhận biên bản nhận hàng thực tế (Goods Receipt), hỗ trợ nhận hàng một phần (Partially Received).
* **REQ-FR-10 (Must):** Finance thực hiện bấm nút đóng hồ sơ mua sắm (Close PR), hệ thống chính thức hạch toán trừ tiền thực tế vào ngân sách phòng ban và chuyển trạng thái PR sang `Closed`.
* **REQ-FR-11 (Must):** Quản lý ngân sách phòng ban cho phép Finance cấu hình hạn mức ngân sách theo năm/quý cho từng phòng ban.
* **REQ-FR-12 (Should):** Quản lý danh bạ nhà cung cấp (Supplier CRUD) và lịch sử giao dịch.
* **REQ-FR-13 (Must):** Phân quyền người dùng nghiêm ngặt dựa trên vai trò (Role-Based Access Control - RBAC) cho 5 vai trò: `EMPLOYEE`, `MANAGER`, `PROCUREMENT`, `FINANCE`, `ADMIN`.

## B. Yêu Cầu Phi Chức Năng (Non-Functional Requirements - NFR)

* **REQ-NFR-01 (Should):** Latency xử lý trích xuất và chuẩn hóa báo giá của AI phải $\leq 3.5$ giây trong môi trường demo.
* **REQ-NFR-02 (Must):** Bảo mật dữ liệu tài chính: Toàn bộ API cập nhật ngân sách hoặc trạng thái phê duyệt phải được xác thực bằng JWT và kiểm tra quyền ở backend.
* **REQ-NFR-03 (Must):** Audit Logging: Ghi nhật ký hệ thống chi tiết cho mọi hành động phê duyệt, từ chối, cập nhật ngân sách và các cảnh báo bất thường từ AI.
* **REQ-NFR-04 (Should):** Responsive Web hiển thị tối ưu trên Desktop và di động.
* **REQ-NFR-05 (Must):** Mật khẩu người dùng được băm bảo mật bằng thuật toán mạnh (bcrypt) trước khi ghi vào cơ sở dữ liệu.

## C. Quy Tắc Nghiệp Vụ (Business Rules - BR)

* **REQ-BR-01:** Ràng buộc ngân sách: Một PR chỉ được gửi đi khi ngân sách phòng ban khả dụng lớn hơn hoặc bằng giá trị ước tính của PR.
* **REQ-BR-02:** Quy tắc phân cấp duyệt: PR có giá trị $\leq 50$ triệu VND do Manager duyệt trực tiếp. PR $> 50$ triệu VND cần đồng thuận của cả Manager và Finance.
* **REQ-BR-03:** Tính nhất quán dữ liệu PO: Đơn giá và số lượng trên PO được khởi tạo tự động phải khớp $100\%$ với báo giá (Quotation) gốc đã được lưu trong DB. AI hoàn toàn không có quyền tự ý sửa đổi đơn giá PO để chống ảo giác giá cả.
* **REQ-BR-04:** Giới hạn nhận hàng: Tổng số lượng hàng ghi nhận trên tất cả các biên bản nhận hàng (Receiving) không được phép vượt quá số lượng đặt trên PO.
* **REQ-BR-05:** Quyền hạn ngân sách: Chỉ có người dùng có vai trò Finance hoặc Admin mới được phép thao tác các API điều chỉnh hạn mức ngân sách phòng ban.

## D. Ràng Buộc & Giả Định (Constraints & Assumptions)

* **CON-01:** Phải bàn giao phiên bản MVP chạy được trong vòng 14 tuần của môn học.
* **CON-02:** Quá trình Receiving thực hiện nhập liệu qua giao diện web kèm tải file PDF biên bản đối soát.
* **ASM-01:** Dữ liệu nhà cung cấp ban đầu được cung cấp thông qua dữ liệu mẫu (Seed Data) trong DB.
* **ASM-02:** Hệ thống giả định việc gửi email PO cho Supplier được mock qua dịch vụ giả lập SMTP.

## E. Câu Hỏi Mở (Open Questions)

* **Q-01:** Có cần cổng thông tin (Supplier Portal) riêng cho Supplier tự upload báo giá? -> *Xác nhận:* Không, Procurement Specialist sẽ trực tiếp nhận file báo giá và tải lên hệ thống.
* **Q-02:** Hệ thống có tự động quy đổi ngoại tệ khi so sánh báo giá bằng ngoại tệ không? -> *Xác nhận:* Không, phiên bản MVP chỉ xử lý duy nhất đơn vị tiền tệ là VND.

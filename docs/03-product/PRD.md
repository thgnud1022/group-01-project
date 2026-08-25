# PRODUCT REQUIREMENTS DOCUMENT (PRD): AI Procurement & Purchase Approval System
**Status:** Approved for MVP  
**Version:** 1.0.0  

## 1. Problem Statement
Quy trình thu mua và phê duyệt vật tư doanh nghiệp hiện tại gặp nhiều khó khăn: nhân viên mất nhiều thời gian mô tả yêu cầu thiết bị, phòng thu mua vất vả đối chiếu các file báo giá PDF phi cấu trúc, còn cấp quản lý và tài chính đối mặt với rủi ro phê duyệt dồn dập vượt hạn mức ngân sách phòng ban.

## 2. Goals & Success Metrics
* **G1:** 100% PR được kiểm tra hạn mức ngân sách khả dụng theo thời gian thực trước khi gửi duyệt.
* **G2:** AI bóc tách báo giá PDF chính xác $\geq 90\%$ trên tập 20-Q&A Benchmark.
* **G3:** 100% luồng duyệt giá trị lớn ($> 50$ triệu VND) được chuyển duyệt 2 cấp (Manager $\rightarrow$ Finance).
* **G4:** Độ trễ phản hồi của AI $\leq 3.5$ giây trong môi trường demo.

## 3. User Roles & Key Journeys
1. **Employee (Người yêu cầu):** Khởi tạo PR bằng giọng nói/văn bản thô $\rightarrow$ AI bóc tách danh mục $\rightarrow$ Kiểm tra ngân sách $\rightarrow$ Gửi PR.
2. **Manager (Người duyệt bước 1):** Xem danh sách PR cần duyệt $\rightarrow$ Kiểm tra ngân sách khả dụng $\rightarrow$ Bấm Phê duyệt / Từ chối.
3. **Procurement Specialist (Chuyên viên Thu mua):** Tiếp nhận PR đã duyệt $\rightarrow$ Upload tối đa 3 file PDF báo giá $\rightarrow$ AI lập bảng so sánh & cảnh báo nâng giá $\rightarrow$ Chọn báo giá & Khởi tạo PO.
4. **Finance Specialist (Kiểm soát ngân sách):** Duyệt PR bước 2 ($> 50$tr VND) $\rightarrow$ Cấu hình ngân sách phòng ban $\rightarrow$ Phê duyệt đóng hồ sơ quyết toán (Close PR).
5. **Admin:** Quản trị người dùng, phòng ban, vai trò RBAC.

## 4. Feature Release Slices (MVP Scope)
* **MVP-1 (Must-Have):** Đầy đủ 7 bước quy trình thu mua; AI bóc tách PR & So sánh báo giá PDF; Cảnh báo giá cao $\geq 20\%$; Kiểm soát ngân sách tự động; Phân quyền RBAC 5 vai trò.
* **MVP-2 (Should-Have):** Gửi email thông báo tự động (Mock SMTP); Biểu đồ trực quan sử dụng ngân sách.

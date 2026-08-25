# QUY CHẾ THU MUA VÀ THẨM QUYỀN PHÊ DUYỆT NỘI BỘ

## 1. Phân Cấp Thẩm Quyền Phê Duyệt Mua Sắm (PR Approval Thresholds)
* **Yêu cầu mua sắm $\leq 50.000.000$ VND:**
  * Cần 01 cấp duyệt: **Trưởng phòng (Manager)** của bộ phận khởi tạo.
  * Thời gian phê duyệt tối đa: 24 giờ làm việc.
* **Yêu cầu mua sắm $> 50.000.000$ VND:**
  * Cần 02 cấp duyệt: **Trưởng phòng (Manager)** duyệt bước 1 $\rightarrow$ **Phòng Tài chính (Finance)** duyệt bước 2.
  * Không thể bypass bước duyệt của Finance dưới mọi hình thức.

## 2. Quy Định Quản Lý Ngân Sách Phòng Ban (Budget Control)
* Ngân sách phòng ban được cấp theo từng Quý trong Năm tài chính.
* Ngân sách khả dụng = (Hạn mức Quý) - (Đã chi) - (Khoản tạm tính của các PR đang PENDING/APPROVED).
* Mọi PR vượt quá Ngân sách khả dụng đều bị hệ thống tự động chặn gửi đi (`REQ-BR-01`).

## 3. Quy Định Thu Thập & So Sánh Báo Giá (Procurement Quotations)
* Mỗi PR sau khi được duyệt bắt buộc phải thu thập tối thiểu báo giá từ 03 Nhà cung cấp độc lập.
* Chuyên viên Thu mua tải file PDF/ảnh báo giá lên hệ thống để AI kiểm tra và bóc tách.
* Cảnh báo bất thường đơn giá tự động kích hoạt khi giá báo cao hơn $\geq 20\%$ so với đơn giá lịch sử.

## 4. Quy Định Khởi Tạo PO & Biên Bản Nhận Hàng (PO & Receiving)
* Đơn giá và số lượng trên PO do hệ thống sinh ra từ báo giá đã duyệt là cố định ($100\%$ match), nghiêm cấm chỉnh sửa thủ công.
* Tổng số lượng giao nhận thực tế không được vượt quá số lượng ghi trên PO (`REQ-BR-04`).


# QUY CHẾ THU MUA VÀ THẨM QUYỀN PHÊ DUYỆT NỘI BỘ

## 1. Phân cấp thẩm quyền phê duyệt mua sắm (PR Approval Thresholds)

* **Purchase Request ≤ 50.000.000 VND**

  * Cần **01 cấp phê duyệt**: Manager của bộ phận khởi tạo Purchase Request.
  * Thời gian phê duyệt tối đa: **24 giờ làm việc**.

* **Purchase Request > 50.000.000 VND**

  * Cần **02 cấp phê duyệt**:

    1. Manager phê duyệt bước 1.
    2. Finance phê duyệt bước 2.
  * Purchase Request không được bỏ qua bước phê duyệt của Finance.

* Manager có thể **Approve, Reject hoặc Request Revision** đối với Purchase Request thuộc phạm vi quyền hạn.

---

## 2. Quy định quản lý ngân sách phòng ban (Budget Control)

* Ngân sách phòng ban được quản lý theo **Quý trong Năm tài chính**.
* **Ngân sách khả dụng** được xác định theo:

> **Ngân sách khả dụng = Hạn mức Quý − Đã chi − Khoản tạm tính của các PR đang Pending/Approved**

* Purchase Request phải được kiểm tra với Budget trước khi hoàn tất quá trình phê duyệt.
* Purchase Request **vượt Ngân sách khả dụng** phải được hệ thống cảnh báo và **không được gửi đi**.
* Finance là role thực hiện kiểm tra tình trạng Budget trong quy trình.
* Approval Workflow và Budget Threshold trong MVP được xác định theo quy chế này và cần được validation với quy trình thực tế của doanh nghiệp.

---

## 3. Quy định thu thập và so sánh báo giá (Procurement Quotations)

* Procurement chỉ được thu thập Quotation sau khi Purchase Request đã được Approval theo workflow.
* Mỗi Purchase Request sau khi được duyệt phải thu thập **tối thiểu 03 Quotation từ các Supplier độc lập**.
* Procurement tải các file Quotation lên hệ thống để hệ thống chuẩn hóa và hỗ trợ trích xuất thông tin.
* Hệ thống hỗ trợ so sánh Quotation giữa các Supplier.
* AI hỗ trợ phân tích kết quả so sánh và đưa ra **Recommendation** dựa trên các tiêu chí được sử dụng trong quá trình so sánh.
* AI có thể phát hiện **Anomaly Alert** khi đơn giá báo giá cao hơn **≥20% so với đơn giá lịch sử** theo quy định của MVP.
* AI chỉ đưa ra Recommendation; **Procurement là người đưa ra quyết định lựa chọn Supplier cuối cùng**.

---

## 4. Quy định khởi tạo Purchase Order (PO)

* Purchase Order chỉ được tạo sau khi:

  1. Purchase Request đã được Approval.
  2. Supplier đã được lựa chọn.
  3. Quotation tương ứng đã được lựa chọn trong quy trình.

* PO phải sử dụng thông tin Supplier và Quotation đã được lựa chọn.

* **Đơn giá và số lượng trên PO phải khớp 100% với Quotation được lựa chọn.**

* AI không được tự ý thay đổi đơn giá hoặc số lượng khi tạo PO.

* Procurement không được tự ý thay đổi đơn giá và số lượng đã được lấy từ Quotation được lựa chọn.

---

## 5. Quy định Receiving

* Người dùng có quyền thực hiện ghi nhận **Receiving** khi hàng hóa/dịch vụ được bàn giao.
* **Tổng số lượng thực tế đã Receive không được vượt quá số lượng trên PO.**
* Purchase Request chỉ được chuyển sang **Close** sau khi Receiving và các bước mua sắm liên quan đã hoàn tất.

---

## 6. Quy trình nghiệp vụ tổng thể

Toàn bộ quy trình mua sắm nội bộ được thực hiện theo thứ tự:

**Purchase Request**
↓
**Approve**
↓
**Collect Quotations**
↓
**Compare**
↓
**Select Supplier**
↓
**Purchase Order**
↓
**Receive**
↓
**Close**

### Nguyên tắc AI

AI chỉ đóng vai trò **Decision Support**, tập trung vào:

* Chuẩn hóa **Purchase Request**.
* Hỗ trợ **Quotation Extraction/Standardization**.
* Phân tích và **Quotation Comparison**.
* Phát hiện **Anomaly Alert**.
* Đưa ra **AI Recommendation**.

AI **không thay thế quyết định của Manager, Finance hoặc Procurement**.

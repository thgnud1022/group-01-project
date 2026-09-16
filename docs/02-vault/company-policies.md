# QUY CHẾ THU MUA VÀ THẨM QUYỀN PHÊ DUYỆT NỘI BỘ

## 1. Phân cấp thẩm quyền phê duyệt Purchase Request

* Purchase Request được thực hiện phê duyệt theo workflow được cấu hình.
*Vượt Budget:

  * Cần **02 cấp phê duyệt**:

    1. Manager phê duyệt bước 1.
    2. Finance phê duyệt bước 2.
  * Không được bỏ qua bước phê duyệt của Finance.
* Manager có thể thực hiện một trong các quyết định:

  * **Approve**
  * **Reject**
  * **Request Revision**
* Employee không tự thực hiện quyết định Approval đối với Purchase Request của chính mình.

---

## 2. Quy định quản lý Budget

* Budget của phòng ban được quản lý theo **Quý trong Năm tài chính**.
* **Budget khả dụng** được xác định theo:

> **Budget khả dụng = Hạn mức Quý − Đã chi − Khoản tạm tính của các PR đang Pending/Approved**

* Purchase Request phải được kiểm tra với Budget trong quá trình Approval khi có yêu cầu Budget Review.
* Nếu Purchase Request **vượt Budget khả dụng**, hệ thống phải:

  * Hiển thị **Budget Warning**.
  * Không cho phép Purchase Request được gửi đi.
* **Finance** là role thực hiện kiểm tra tình trạng Budget trong quy trình.
* Approval Workflow và Budget Threshold được sử dụng trong MVP theo quy định này và cần được validation với quy trình thực tế của doanh nghiệp.

---

## 3. Quy định thu thập và quản lý Quotation

* Procurement chỉ được thu thập Quotation sau khi Purchase Request đã được Approval theo workflow.
* Mỗi Purchase Request sau khi được duyệt phải thu thập **tối thiểu 03 Quotation từ các Supplier độc lập**.
* Procurement tải Quotation lên hệ thống để hệ thống hỗ trợ trích xuất và chuẩn hóa thông tin.
* Các Quotation phải được liên kết với **Purchase Request tương ứng**.
* Thông tin Quotation được chuẩn hóa để phục vụ việc so sánh giữa các Supplier.
* Hệ thống hỗ trợ Procurement so sánh các Quotation dựa trên thông tin có trong Quotation.

---

## 4. Quy định AI trong phân tích Quotation

AI được sử dụng với vai trò **Decision Support**, bao gồm:

* Hỗ trợ chuẩn hóa thông tin của **Purchase Request**.
* Hỗ trợ **Quotation Extraction/Standardization**.
* Hỗ trợ **Quotation Comparison**.
* Phân tích kết quả so sánh Quotation.
* Đưa ra **AI Recommendation** dựa trên các tiêu chí được sử dụng trong quá trình so sánh.
* Phát hiện **Anomaly Alert** khi đơn giá báo giá cao **≥20% so với đơn giá lịch sử** theo quy định của MVP.

AI **không được**:

* Tự quyết định Approval của Purchase Request.
* Tự quyết định Supplier cuối cùng.
* Thay thế quyết định của Manager, Finance hoặc Procurement.

**Procurement là người đưa ra quyết định cuối cùng về Supplier.**

---

## 5. Quy định lựa chọn Supplier và tạo Purchase Order

Purchase Order chỉ được tạo khi:

1. Purchase Request đã được Approval.
2. Supplier đã được lựa chọn.
3. Quotation tương ứng đã được lựa chọn trong quy trình.

Khi tạo Purchase Order:

* PO phải sử dụng thông tin Supplier và Quotation đã được lựa chọn.
* **Đơn giá và số lượng trên PO phải khớp 100% với Quotation được lựa chọn.**
* Procurement không được tự ý thay đổi đơn giá hoặc số lượng được lấy từ Quotation.
* AI không được tự ý thay đổi đơn giá hoặc số lượng khi tạo PO.

---

## 6. Quy định Receiving

* Người dùng có quyền được phép ghi nhận **Receiving** khi hàng hóa/dịch vụ được bàn giao.
* Hệ thống phải đảm bảo **tổng số lượng đã Receive không vượt quá số lượng trên PO**.
* Receiving có thể được ghi nhận theo quá trình nhận hàng thực tế.

---

## 7. Quy định Close Purchase Request

Purchase Request chỉ được chuyển sang trạng thái **Close/Closed** khi:

* Receiving đã hoàn tất.
* Các bước mua sắm liên quan đã hoàn tất.

Việc Close Purchase Request thuộc phạm vi quyền của người dùng được hệ thống phân quyền.

---

## 8. Quy trình nghiệp vụ tổng thể

Quy trình mua sắm nội bộ được thực hiện theo thứ tự:

**Purchase Request**
↓
**Approve**
↓
**Collect Quotations**
↓
**Compare Quotations**
↓
**Select Supplier**
↓
**Purchase Order**
↓
**Receive**
↓
**Close Purchase Request**

---

## 9. Nguyên tắc về vai trò người dùng

* **Employee:** Tạo, hoàn thiện và theo dõi Purchase Request.
* **Manager:** Xem xét và đưa ra quyết định Approval đối với Purchase Request thuộc phạm vi quyền hạn.
* **Finance:** Kiểm tra Purchase Request với Budget và thực hiện bước phê duyệt Finance khi workflow yêu cầu.
* **Procurement:** Quản lý Supplier, thu thập và so sánh Quotation, lựa chọn Supplier và tạo Purchase Order.
* **Admin:** Quản lý người dùng, vai trò và cấu hình quy trình.

---

## 10. Nguyên tắc chung của hệ thống

* AI chỉ đóng vai trò **hỗ trợ quyết định**, không thay thế người dùng có thẩm quyền.
* Các quyết định **Approval** thuộc về Manager/Finance theo workflow.
* Quyết định **Supplier cuối cùng** thuộc về Procurement.
* Hệ thống phải tuân thủ thứ tự của quy trình mua sắm và không cho phép thực hiện các bước khi điều kiện nghiệp vụ trước đó chưa hoàn tất.
* Các thông tin Supplier, Quotation và Budget chưa được xác định đầy đủ trong dữ liệu doanh nghiệp có thể sử dụng **mock/sample data trong MVP** theo các giả định đã được xác định.

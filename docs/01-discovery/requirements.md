
# REQUIREMENTS INVENTORY

## AI Procurement & Purchase Approval System

### A. Functional Requirements (FR)

| **ID**        | **Loại** | **Yêu cầu**                                                                                         | **P**  |
| ------------- | -------- | --------------------------------------------------------------------------------------------------- | ------ |
| **REQ-FR-01** | FR       | Employee có thể tạo và quản lý Purchase Request.                                                    | Must   |
| **REQ-FR-02** | FR       | Hệ thống phải kiểm tra các thông tin cần thiết của Purchase Request trước khi Submit.               | Must   |
| **REQ-FR-03** | FR       | AI hỗ trợ chuẩn hóa Purchase Request và gợi ý các thông tin còn thiếu trước khi Submit.             | Should |
| **REQ-FR-04** | FR       | Employee có thể theo dõi trạng thái của Purchase Request trong quy trình.                           | Must   |
| **REQ-FR-05** | FR       | Manager có thể xem thông tin Purchase Request trước khi phê duyệt.                                  | Must   |
| **REQ-FR-06** | FR       | Manager có thể Approve, Reject hoặc yêu cầu chỉnh sửa Purchase Request.                             | Must   |
| **REQ-FR-07** | FR       | Hệ thống hỗ trợ Approval Workflow cho Purchase Request.                                             | Must   |
| **REQ-FR-08** | FR       | Finance có thể kiểm tra Purchase Request với Budget trước khi phê duyệt.                            | Must   |
| **REQ-FR-09** | FR       | Hệ thống cảnh báo khi Purchase Request có giá trị vượt Budget được phép.                            | Must   |
| **REQ-FR-10** | FR       | Procurement có thể quản lý Supplier và thu thập nhiều Quotation cho Purchase Request.               | Must   |
| **REQ-FR-11** | FR       | Hệ thống chuẩn hóa thông tin từ các Quotation để phục vụ việc đối chiếu.                            | Should |
| **REQ-FR-12** | FR       | Hệ thống cho phép so sánh các Quotation giữa nhiều Supplier.                                        | Must   |
| **REQ-FR-13** | FR       | AI hỗ trợ phân tích và hiển thị kết quả so sánh Quotation.                                          | Must   |
| **REQ-FR-14** | FR       | AI đưa ra Recommendation dựa trên thông tin và tiêu chí của các Quotation.                          | Should |
| **REQ-FR-15** | FR       | AI cảnh báo giá bất thường khi đơn giá cao hơn hoặc bằng 20% so với mức trung bình lịch sử của sản phẩm cùng loại. | Should |
| **REQ-FR-16** | FR       | Procurement có thể lựa chọn Supplier và tạo Purchase Order sau khi Purchase Request được phê duyệt. | Must   |
| **REQ-FR-17** | FR       | Người dùng có quyền có thể ghi nhận Receiving đối với hàng hóa/dịch vụ.                             | Must   |
| **REQ-FR-18** | FR       | Hệ thống cho phép Close Purchase Request sau khi các bước mua sắm hoàn tất.                         | Must   |

---

# B. Non-Functional Requirements (NFR)

| **ID**         | **Loại** | **Yêu cầu**                                                                                                                   | **P** |
| -------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------- | ----- |
| **REQ-NFR-01** | NFR      | Hệ thống phải đảm bảo dữ liệu Purchase Request, Approval, Quotation và Budget được quản lý nhất quán trong toàn bộ quy trình. | Must  |
| **REQ-NFR-02** | NFR      | Hệ thống phải phân quyền chức năng phù hợp với vai trò Employee, Manager, Procurement, Finance và Admin.                             | Must  |
| **REQ-NFR-03** | NFR      | Hệ thống phải ghi nhận thông tin cần thiết để theo dõi quá trình xử lý và Approval của Purchase Request.                      | Must  |


# C. Business Rules (BR)

| **ID**        | **Rule**                                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------------------- |
| **REQ-BR-01** | Purchase Request phải được tạo đầy đủ thông tin cần thiết trước khi được Submit.                              |
| **REQ-BR-02** | Purchase Request phải được Approve trước khi chuyển sang bước Collect Quotations.                             |
| **REQ-BR-03** | Manager là người xem xét và đưa ra quyết định Approval đối với Purchase Request thuộc phạm vi của mình.       |
| **REQ-BR-04** | Finance kiểm tra Purchase Request với Budget trước khi hoàn tất bước phê duyệt có yêu cầu kiểm tra ngân sách. |
| **REQ-BR-05** | Purchase Request vượt giới hạn Budget phải được cảnh báo.                                                     |
| **REQ-BR-06** | Procurement thực hiện thu thập và đối chiếu Quotation sau khi Purchase Request được Approve.                  |
| **REQ-BR-07** | Các Quotation được thu thập phải được liên kết với Purchase Request tương ứng để phục vụ so sánh.             |
| **REQ-BR-08** | AI chỉ đưa ra Recommendation, không tự quyết định Supplier thay cho Procurement.                              |
| **REQ-BR-09** | AI Recommendation dựa trên thông tin và tiêu chí được sử dụng để so sánh Quotation.                           |
| **REQ-BR-10** | Purchase Order chỉ được tạo sau khi Purchase Request được Approve và Supplier được lựa chọn.                  |
| **REQ-BR-11** | Purchase Request chỉ được Close sau khi bước Receiving và các bước mua sắm liên quan hoàn tất.                |

---

# D. Constraints (CON)

| **ID**     | **Constraint**                                                                                                                                                           |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **CON-01** | Quy trình nghiệp vụ phải tuân theo thứ tự: **Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close**.                                         |
| **CON-02** | MVP tập trung vào các vai trò **Employee, Manager, Procurement, Finance và Admin**.                                                                                             |
| **CON-03** | AI chỉ đóng vai trò **hỗ trợ**, không thay thế quyết định Approval hoặc quyết định lựa chọn Supplier của người dùng.                                                     |
| **CON-04** | MVP được triển khai trên **nền tảng web**.                                                                                                                               |
| **CON-05** | MVP không tích hợp trực tiếp với hệ thống **ERP hoặc kế toán**.                                                                                                          |
| **CON-06** | Các chức năng **Inventory, Supplier Payment, Contract Management, ERP/Accounting Integration, Mobile App, Supplier Portal và Demand Forecasting** nằm ngoài phạm vi MVP. |

---

# E. Assumptions (ASM)


| **ID**     | **Assumption**                                                                                                                    |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **ASM-01** | MVP sử dụng dữ liệu Supplier, Quotation và Budget ở dạng mock/sample nếu chưa có dữ liệu doanh nghiệp thực tế.                    |
| **ASM-02** | Approval hierarchy và Budget threshold trong MVP là giả định và cần được validation với doanh nghiệp thực tế.                     |
| **ASM-03** | AI trong MVP chỉ đóng vai trò decision support, không thay thế quyết định của Manager, Finance hoặc Procurement.                  |
| **ASM-04** | AI không được tự ý thay đổi thông tin Quotation đã được lựa chọn khi tạo PO.                                                      |
| **ASM-05** | Đối với MVP, PR có giá trị trên 50 triệu VND được giả định cần Manager và Finance approval.                                 |
| **ASM-06** | Trong MVP, tổng số lượng Receiving không được vượt quá số lượng trên PO.                                                      |
| **ASM-07** | Trong MVP, AI có thể trích xuất thông tin từ file Quotation do Procurement cung cấp.                                  |



# F. Open Questions (Q)

| **ID**   | **Open Question**                                                                                |
| -------- | ------------------------------------------------------------------------------------------------ |
| **Q-01** | Approval Workflow thực tế gồm những cấp phê duyệt nào?                                           |
| **Q-02** | Những thông tin nào là bắt buộc khi Employee tạo Purchase Request?                               |
| **Q-03** | Budget được kiểm tra theo tiêu chí và giới hạn nào trong quy trình thực tế?                      |
| **Q-04** | Những tiêu chí nào được sử dụng để AI Recommendation Supplier từ các Quotation?                  |
| **Q-05** | Procurement cần những thông tin nào từ Supplier/Quotation để thực hiện việc so sánh và lựa chọn? |


## Mapping với Project Charter

| **Project Charter**                    | **Requirements tương ứng** |
| -------------------------------------- | -------------------------- |
| Employee tạo PR                        | FR-01 → FR-04              |
| Manager Approval                       | FR-05 → FR-07              |
| Finance kiểm tra Budget                | FR-08 → FR-09              |
| Procurement quản lý Supplier/Quotation | FR-10 → FR-12              |
| AI chuẩn hóa PR                        | FR-03                      |
| AI so sánh Quotation                   | FR-13                      |
| AI Recommendation                      | FR-14                      |
| Purchase Order                         | FR-15                      |
| Receiving                              | FR-17                      |
| Close                                  | FR-18                      |
| Workflow bắt buộc                      | CON-01 / BR-02 → BR-11     |
| AI chỉ hỗ trợ                          | CON-03 / BR-08             |
| Web MVP                                | CON-04                     |
| Không ERP/Accounting                   | CON-05                     |
| Out of Scope                           | CON-06                     |
| Stakeholder Proxy                      | ASM-01 → ASM-02            |


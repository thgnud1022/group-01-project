 **Stakeholder Proxy / giả định nghiên cứu cần validation**

# Research Question

> Trong quy trình mua sắm nội bộ (Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close), người dùng gặp khó khăn ở bước nào và AI có thể hỗ trợ như thế nào?

| **P**                | **Observation / Quote rút gọn**                                                                                              | **Insight**                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **P1 – Employee**    | Purchase Request có thể bị thiếu thông tin cần thiết, dẫn đến việc phải bổ sung hoặc chỉnh sửa trước khi tiếp tục quy trình. | AI có thể hỗ trợ chuẩn hóa Purchase Request và kiểm tra các thông tin còn thiếu trước khi gửi.       |
| **P2 – Manager**     | Manager cần xem xét Purchase Request và các thông tin liên quan trước khi đưa ra quyết định phê duyệt.                       | Hệ thống cần tập trung thông tin của request và các thông tin cần thiết cho quá trình approval.      |
| **P3 – Procurement** | Procurement phải thu thập nhiều quotation từ Supplier và đối chiếu các thông tin trong quotation trước khi lựa chọn.         | AI có thể hỗ trợ chuẩn hóa và so sánh các quotation để giảm thao tác đối chiếu thủ công.             |
| **P4 – Finance**     | Finance cần kiểm tra giá trị Purchase Request và ngân sách liên quan trước khi phê duyệt.                                    | Hệ thống cần hiển thị thông tin ngân sách và cảnh báo khi request có vấn đề liên quan đến ngân sách. |

# Research Synthesis

### Theme A – Purchase Request chưa được chuẩn hóa

**Evidence**

* **Stakeholder Proxy – P1 Employee:** Purchase Request có thể thiếu thông tin và cần được bổ sung hoặc chỉnh sửa.

**Insight**
AI có thể hỗ trợ chuẩn hóa nội dung Purchase Request và kiểm tra các thông tin cần thiết trước khi gửi.

**Requirement**
**FR-01:** Employee shall be able to create a standardized Purchase Request with AI assistance.

---

### Theme B – Approval cần thông tin tập trung

**Evidence**

* **Stakeholder Proxy – P2 Manager:** Manager cần xem xét thông tin Purchase Request trước khi đưa ra quyết định approval.

**Insight**
Hệ thống cần cung cấp đầy đủ thông tin liên quan đến Purchase Request trên màn hình Approval để hỗ trợ Manager ra quyết định.

**Requirement**
**FR-02:** Manager shall be able to review and approve Purchase Requests with complete request information.

---

### Theme C – So sánh báo giá còn thủ công

**Evidence**

* **Stakeholder Proxy – P3 Procurement:** Procurement phải thu thập và đối chiếu thông tin từ nhiều Quotation trước khi lựa chọn Supplier.

**Insight**
AI có thể hỗ trợ chuẩn hóa và so sánh các Quotation để Procurement dễ dàng đánh giá các phương án.

**Requirement**
**FR-03:** AI shall compare supplier quotations and provide a recommendation based on the available quotation information.

---

### Theme D – Kiểm soát ngân sách trong Approval

**Evidence**

* **Stakeholder Proxy – P4 Finance:** Finance cần kiểm tra giá trị Purchase Request và ngân sách liên quan trước khi phê duyệt.

**Insight**
Hệ thống cần cung cấp thông tin Budget cùng Purchase Request và cảnh báo các trường hợp liên quan đến giới hạn ngân sách.

**Requirement**
**FR-04:** Finance shall be able to review Purchase Requests against the available budget before approval.

---

**Limitation:** The research uses stakeholder proxies and business-process assumptions because the team has limited access to real procurement users. Therefore, these findings should not be treated as validated user insights and require validation through real-user interviews or observations.

---

# Persona – JTBD – Pain Point – Success

| **Persona**                     | **JTBD**                                                                                                                                | **Pain point**                                                                      | **Success**                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Employee – Requester**        | Khi cần mua sản phẩm/dịch vụ phục vụ công việc, tôi muốn tạo **Purchase Request** đầy đủ để request có thể tiếp tục được xử lý.         | Purchase Request có thể thiếu thông tin cần thiết và phải bổ sung hoặc chỉnh sửa.   | Tạo được Purchase Request đầy đủ và hạn chế việc phải bổ sung thông tin.                   |
| **Manager – Approver**          | Khi nhận **Purchase Request**, tôi muốn xem các thông tin cần thiết để đưa ra quyết định **Approve/Reject**.                            | Thông tin cần thiết cho việc approval cần được xem xét trước khi đưa ra quyết định. | Có thể xem thông tin Purchase Request tập trung và thực hiện approval.                     |
| **Procurement – Buyer**         | Khi cần lựa chọn Supplier, tôi muốn thu thập và so sánh nhiều **Quotation** để lựa chọn phương án phù hợp.                              | Phải đối chiếu thông tin từ nhiều Quotation trước khi lựa chọn Supplier.            | Có thể so sánh các Quotation trên hệ thống và có AI hỗ trợ đánh giá.                       |
| **Finance – Budget Controller** | Khi Purchase Request được gửi đến, tôi muốn kiểm tra giá trị request và **Budget** để đảm bảo việc mua sắm nằm trong phạm vi ngân sách. | Thông tin Purchase Request và Budget cần được xem xét cùng nhau.                    | Có thể kiểm tra request với Budget và nhận cảnh báo khi có vấn đề liên quan đến ngân sách. |



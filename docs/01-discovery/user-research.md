
# USER RESEARCH & SYNTHESIS

## 1. Research Question & Observations

**Research Question:** *Trong quy trình mua sắm nội bộ ($\text{Purchase Request} \rightarrow \text{Approve} \rightarrow \text{Collect Quotations} \rightarrow \text{Compare} \rightarrow \text{PO} \rightarrow \text{Receive} \rightarrow \text{Close}$), người dùng gặp khó khăn ở bước nào và AI có thể hỗ trợ như thế nào?*

| P (Participant) | Observation / Quote rút gọn | Insight |
| --- | --- | --- |
| **P1 – Employee** | Khi tạo Purchase Request, tôi thường không biết phải mô tả yêu cầu mua hàng như thế nào cho đầy đủ. Nếu thiếu thông tin thì yêu cầu bị trả về để sửa. | AI nên chuẩn hóa Purchase Request và gợi ý các thông tin còn thiếu trước khi gửi. |
| **P2 – Manager** | Tôi phải duyệt nhiều Purchase Request mỗi ngày nhưng khó biết yêu cầu nào cần ưu tiên hoặc có vượt ngân sách hay không. | Hệ thống cần hiển thị đầy đủ thông tin, trạng thái và cảnh báo trước khi phê duyệt. |
| **P3 – Procurement** | Việc thu thập nhiều báo giá rồi so sánh bằng Excel mất rất nhiều thời gian, đặc biệt khi mỗi Supplier gửi một định dạng khác nhau. | AI nên chuẩn hóa và so sánh báo giá để hỗ trợ lựa chọn Supplier phù hợp. |

---

## 2. Research Synthesis

### **Theme A – Purchase Request chưa được chuẩn hóa**

* **Evidence:** Stakeholder Proxy – P1 (Employee) thường bị trả lại Purchase Request do thiếu thông tin.
* **Insight:** AI có thể hỗ trợ chuẩn hóa nội dung và kiểm tra các trường bắt buộc trước khi gửi.
* **Requirement:** `FR-001`: Employee shall be able to create a standardized Purchase Request with AI assistance.

### **Theme B – Approval cần nhiều thông tin hơn**

* **Evidence:** Stakeholder Proxy – P2 (Manager) khó đánh giá nhanh yêu cầu nào cần ưu tiên hoặc có rủi ro.
* **Insight:** Hệ thống cần cung cấp trạng thái, thông tin ngân sách và lịch sử phê duyệt ngay trên màn hình Approval.
* **Requirement:** `FR-002`: Manager shall be able to review and approve Purchase Requests with complete request information.

### **Theme C – So sánh báo giá còn thủ công**

* **Evidence:** Stakeholder Proxy – P3 (Procurement) phải tổng hợp thông tin từ nhiều quotation có định dạng khác nhau vào Excel để đối chiếu giá và các điều kiện của Supplier.
* **Insight:** AI nên tự động so sánh các Quotation theo giá, thời gian giao hàng, bảo hành và đề xuất Supplier phù hợp.
* **Requirement:** `FR-003`: AI shall compare supplier quotations and recommend the best option.

> **Limitation:** The research uses stakeholder proxies because the team has limited access to real procurement users. Therefore, the findings are assumptions that require validation through real-user interviews or observations.

---

## 3. User Personas & JTBD

| Persona | Job To Be Done (JTBD) | Pain Point | Success Criteria |
| --- | --- | --- | --- |
| **Employee**<br>

<br>*(Requester)* | Khi cần mua sản phẩm/dịch vụ phục vụ công việc, tôi muốn tạo Purchase Request đầy đủ và nhanh để yêu cầu không bị trả lại do thiếu thông tin. | Không biết cần cung cấp những thông tin nào; request có thể bị trả về để bổ sung hoặc sửa. | Tạo được request đầy đủ ngay lần đầu; giảm số request bị trả về do thiếu thông tin. |
| **Manager**<br>

<br>*(Approver)* | Khi nhận Purchase Request, tôi muốn nhanh chóng xem thông tin yêu cầu, ngân sách và trạng thái để đưa ra quyết định Approve/Reject. | Phải xem nhiều request; khó xác định request nào cần ưu tiên và khó biết request có vượt ngân sách hay không. | Có thể xem đầy đủ thông tin và đưa ra quyết định approval nhanh, không cần trao đổi nhiều lần. |
| **Procurement**<br>

<br>*(Buyer)* | Khi cần lựa chọn nhà cung cấp, tôi muốn thu thập và so sánh nhiều Quotation để chọn phương án phù hợp. | Phải thu thập và so sánh quotation thủ công bằng Excel; các supplier có thể gửi quotation với định dạng khác nhau. | So sánh được quotation trên một màn hình; giảm thời gian phân tích và lựa chọn supplier. |
| **Finance**<br>

<br>*(Budget Controller)* | Khi Purchase Request được gửi đến, tôi muốn kiểm tra ngân sách và giá trị request trước khi phê duyệt để đảm bảo chi tiêu nằm trong giới hạn. | Khó kiểm tra ngân sách nếu thông tin request và budget không được tập trung. | Xác định được request có nằm trong ngân sách trước khi approval; có cảnh báo khi vượt hạn mức. |

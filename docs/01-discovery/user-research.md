

**Research question:** "Trong tình huống nào các bên liên quan (Requester, Manager, Procurement/QA) muốn sử dụng trợ lý AI/Voice trong quy trình thu mua, và họ cần mức độ kiểm soát/xác nhận nào trước khi phê duyệt tài chính và khởi tạo đơn hàng?"

| P | Observation / quote rút gọn | Insight |
| --- | --- | --- |
| **P1 - Requester (Nhân viên tạo PR)** | Thường xuyên nộp yêu cầu mua sắm bằng lời nói/văn bản thô khi đang đi công trường/di chuyển; ngại điền form thủ công rườm rà. | Voice/Text thô có giá trị cao ở bước khởi tạo & bóc tách PR, nhưng cần hiển thị lại kết quả Pydantic schema để xác nhận thông tin. |
| **P2 - Manager (Trưởng phòng duyệt PR)** | Sợ bấm nhầm nút duyệt nhanh làm duyệt vượt ngân sách; không muốn tự tra cứu số dư khả dụng thủ công từ hệ thống khác. | Mọi hành động duyệt có tác động ngân sách cần bước kiểm tra Real-time và hiển thị cảnh báo rõ ràng trước khi xác nhận Approve. |
| **P3 - Procurement & QA Specialist** | Sợ AI trích xuất sai đơn giá từ file PDF/ảnh báo giá hoặc tự động chỉ định Nhà cung cấp không qua kiểm duyệt. | Cần AI cảnh báo bất thường đơn giá $\ge 20\%$và bắt buộc con người xem bảng so sánh, xác nhận khóa đơn giá trước khi phát hành PO. |

---

### **RESEARCH SYNTHESIS**

* **Theme A - Hands-free & Text-to-PR Convenience:** 3/3 người tham gia thấy hữu ích khi AI tự động bóc tách yêu cầu mua sắm từ Voice/Văn bản thô thành PR chuẩn hóa.
* **Theme B - Financial Control & Real-time Budgeting:** 3/3 người tham gia yêu cầu hệ thống phải kiểm tra và hiển thị số dư ngân sách khả dụng theo thời gian thực trước khi cho phép bấm nút duyệt PR.
* **Theme C - Human-in-the-Loop & Fraud Prevention:** 3/3 không chấp nhận để AI tự động phê duyệt hoặc tự tạo PO; 2/3 kỳ vọng AI phát hiện cảnh báo lệch giá $\ge 20\%$ để con người ra quyết định cuối cùng.

---

* **Product implication:**
* Ưu tiên tích hợp **VoiceComposer UI** ở bước tạo PR với cơ chế text fallback và hiển thị transcript rõ ràng.
* Tích hợp bắt buộc **Real-time Budget Check API** vào nút Approve ở cả Frontend và Backend.
* Thiết kế vai trò AI ở mức **hỗ trợ trích xuất, lập bảng so sánh PDF và cảnh báo lỗi/bất thường đơn giá**, tuyệt đối không cấp quyền duyệt tự động.

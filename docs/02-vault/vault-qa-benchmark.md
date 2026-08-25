# VAULT Q&A BENCHMARK: Bộ 20 Câu Hỏi Kiểm Định AI

Bộ câu hỏi benchmark dưới đây dùng để chạy kiểm thử đánh giá năng lực phản hồi chính xác của AI dựa trên dữ liệu tri thức Vault, đảm bảo AI trả lời đúng nguồn và phản hồi `"KHÔNG ĐỦ DỮ LIỆU"` khi thông tin không có trong Vault.

| ID | Dạng câu hỏi | Câu hỏi kiểm thử (Query) | Phản hồi chuẩn (Expected Grounded Answer) | Nguồn tham chiếu (Source ID) | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q-01** | Fact | AI có quyền tự ý thay đổi đơn giá trên PO không? | Không. Đơn giá PO phải khớp 100% với báo giá gốc được duyệt. | `REQ-BR-03` | PASS |
| **Q-02** | Rule | Hệ thống xử lý thế nào khi Employee tạo PR vượt ngân sách của phòng ban? | Hệ thống tự động chặn và hiển thị cảnh báo đỏ, không cho gửi PR đi. | `REQ-BR-01` | PASS |
| **Q-03** | Rule | Quy trình duyệt cho một PR trị giá 75 triệu VND diễn ra thế nào? | Bắt buộc phải qua 2 cấp duyệt: Manager duyệt trước, sau đó Finance duyệt. | `REQ-BR-02` | PASS |
| **Q-04** | Edge | Dự án có tích hợp thanh toán qua cổng Visa/Mastercard thật không? | Không hỗ trợ trong phạm vi MVP (Out of Scope). | `Project Charter` | PASS |
| **Q-05** | Fact | Chuyên viên Thu mua có thể nhập trực tiếp đơn giá PO mới không? | Không, đơn giá phải lấy chính xác từ báo giá đã được lưu trong DB. | `REQ-BR-03` | PASS |
| **Q-06** | Fact | Làm thế nào để biết hệ thống đã ghi nhận đúng giọng nói của Employee? | Hệ thống bắt buộc phải hiển thị văn bản thô (transcript) ngay trên giao diện. | `REQ-FR-01` | PASS |
| **Q-07** | Rule | Số lượng hàng nhận thực tế có được lớn hơn số lượng trên PO không? | Không, hệ thống sẽ chặn không cho nhập số lượng nhận lớn hơn số lượng PO. | `REQ-BR-04` | PASS |
| **Q-08** | Unknown | Lịch sử cuộc trò chuyện (Conversation History) có được lưu giữ 30 ngày không? | KHÔNG ĐỦ DỮ LIỆU (Chính sách lưu trữ history chưa được cấu hình cho MVP). | `Open Questions` | PASS |
| **Q-09** | Rule | Ai là người duy nhất có quyền cấu hình hạn mức ngân sách phòng ban? | Người dùng có vai trò Finance hoặc Admin. | `REQ-BR-05` | PASS |
| **Q-10** | Edge | Hệ thống có hỗ trợ so sánh báo giá bằng USD không? | Không, MVP chỉ hỗ trợ duy nhất một đơn vị tiền tệ là VND. | `Open Questions` | PASS |
| **Q-11** | Fact | Khi nào PR được chuyển trạng thái sang `Closed`? | Khi Finance thực hiện bấm nút đóng hồ sơ mua sắm và quyết toán xong. | `REQ-FR-10` | PASS |
| **Q-12** | Fact | AI trích xuất thông tin báo giá từ tệp tin nào? | Các tệp báo giá định dạng PDF/hình ảnh do Procurement tải lên. | `REQ-FR-05` | PASS |
| **Q-13** | Edge | Có tính năng nhận diện sinh trắc học giọng nói (Voice Biometrics) không? | Không hỗ trợ trong MVP (Out of Scope). | `Project Charter` | PASS |
| **Q-14** | Fact | Mức chênh lệch giá bao nhiêu thì AI sẽ kích hoạt cảnh báo đỏ? | Chênh lệch giá trị $\geq 20\%$ so với đơn giá trung bình lịch sử thu mua. | `REQ-FR-07` | PASS |
| **Q-15** | Unknown | Hệ thống có tự động gửi PO sang hệ thống SAP của công ty đối tác không? | KHÔNG ĐỦ DỮ LIỆU / Out of Scope (Không tích hợp hệ thống ERP ngoài). | `Project Charter` | PASS |
| **Q-16** | Rule | Nếu hóa đơn của nhà cung cấp có giá khác PO thì sao? | Chặn giao dịch. Giá trên PO là cố định và không được thay đổi. | `REQ-BR-03` | PASS |
| **Q-17** | Edge | Employee có thể tự ý sửa đổi PR của mình sau khi đã được duyệt không? | Không, PR đã duyệt thì khóa sửa đổi, chỉ được phép xem trạng thái. | `REQ-FR-03` | PASS |
| **Q-18** | Fact | Ai có quyền xem ngân sách khả dụng còn lại của bộ phận? | Employee thấy lúc tạo PR, Manager thấy lúc duyệt, Finance/Admin quản lý. | `REQ-FR-02` | PASS |
| **Q-19** | Unknown | Hệ thống có tự động mua hàng khi tồn kho của công ty xuống thấp không? | KHÔNG ĐỦ DỮ LIỆU (Đây là hệ thống duyệt mua sắm nội bộ, không tự mua sắm). | `Project Charter` | PASS |
| **Q-20** | Unknown | Chi phí sử dụng token API LLM hàng tháng của hệ thống được tính thế nào? | KHÔNG ĐỦ DỮ LIỆU (Tài liệu hiện tại chưa cấu hình phương án chi phí AI). | `Constraints` | PASS |

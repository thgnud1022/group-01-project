# User Stories - ProcureAI

> Draft backlog linked to confirmed Requirements. Acceptance Criteria are intentionally limited to confirmed behavior.

| ID | User Story | Acceptance Criteria | Traceability |
|---|---|---|---|
| US-01 | Là Employee, tôi muốn tạo PR với các trường bắt buộc để gửi yêu cầu hợp lệ. | Không thể Submit khi thiếu trường bắt buộc. | REQ-FR-01, REQ-FR-02, REQ-BR-01 |
| US-02 | Là Employee, tôi muốn theo dõi trạng thái PR để biết yêu cầu đang ở bước nào. | Trạng thái PR được hiển thị trong workflow. | REQ-FR-04 |
| US-03 | Là Employee, tôi muốn review gợi ý AI để hoàn thiện mô tả PR. | Có thể xác nhận hoặc chỉnh sửa gợi ý trước Submit. | REQ-FR-03 |
| US-04 | Là Manager, tôi muốn xem PR và Budget trước khi quyết định. | Có thể Approve, Reject, yêu cầu chỉnh sửa hoặc chuyển Finance. | REQ-FR-05, REQ-FR-06, REQ-BR-03, REQ-BR-04 |
| US-05 | Là Finance, tôi muốn kiểm tra PR với Budget để kiểm soát chi phí. | PR vượt Budget được cảnh báo; quyết định do Finance thực hiện theo policy. | REQ-FR-08, REQ-FR-09, REQ-BR-05 |
| US-06 | Là Procurement, tôi muốn liên kết nhiều Quotation với PR để so sánh. | Quotation được gắn đúng PR và hiển thị theo ma trận so sánh. | REQ-FR-10 đến REQ-FR-12, REQ-BR-06, REQ-BR-07 |
| US-07 | Là Procurement, tôi muốn review dữ liệu AI extraction để sửa lỗi trước khi chọn Supplier. | Dữ liệu có thể xem file gốc và chỉnh sửa; AI chỉ Recommendation. | REQ-FR-13 đến REQ-FR-15, REQ-BR-08, REQ-BR-09 |
| US-08 | Là Procurement, tôi muốn tạo PO từ PR đã duyệt và Supplier đã chọn. | PO không được tạo khi thiếu Approval hoặc Supplier. | REQ-FR-16, REQ-BR-10 |
| US-09 | Là người có quyền, tôi muốn ghi nhận Receiving và sai lệch thực tế. | Hỗ trợ nhận đủ, nhận một phần hoặc phát hiện sai lệch. | REQ-FR-17, ASM-06 |
| US-10 | Là Finance, tôi muốn Close chỉ xảy ra sau khi Receiving hoàn tất. | Close bị từ chối nếu chưa hoàn tất bước Receiving liên quan. | REQ-FR-18, REQ-BR-11 |

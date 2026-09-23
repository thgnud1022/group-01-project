# Usability Test Script - ProcureAI

> **Status:** Draft script. Chưa có kết quả test thực tế.

## Objective

Kiểm tra người dùng có hiểu workflow và hoàn thành các task MVP chính hay không.

## Participants

Chưa chốt số lượng và profile participant. Cần tuyển đại diện Employee, Manager, Procurement và Finance; Admin có thể kiểm tra riêng RBAC/Audit Trail.

## Tasks

| ID | Task | Expected behavior | Traceability |
|---|---|---|---|
| T-01 | Tạo PR cho một thiết bị có thông số chưa đầy đủ. | Employee nhận diện gợi ý AI, review và hoàn thiện trước Submit. | REQ-FR-01 đến REQ-FR-03 |
| T-02 | Xem một PR đang chờ phê duyệt. | Manager đọc được thông tin chuẩn hóa và Budget Check. | REQ-FR-05, REQ-FR-09 |
| T-03 | Xử lý PR vượt Budget. | Manager Reject hoặc chuyển Finance; AI không tự quyết định. | REQ-FR-06, REQ-FR-08, REQ-BR-04 |
| T-04 | So sánh các Quotation. | Procurement review dữ liệu extraction, sửa nếu cần và chọn Supplier. | REQ-FR-10 đến REQ-FR-15 |
| T-05 | Ghi nhận Receiving thiếu số lượng. | Hệ thống ghi nhận sai lệch và chưa cho Close. | REQ-FR-17, REQ-FR-18, REQ-BR-11 |
| T-06 | Thử tự phê duyệt PR do chính mình tạo. | Hệ thống chặn self-approval và ghi Audit Trail. | REQ-NFR-02, REQ-NFR-03 |

## Measures

- Task completion rate.
- Critical error count.
- Time on task.
- Participant confidence and comprehension notes.

## Findings policy

Không điền kết quả trước khi test được thực hiện. Kết quả phải ghi trong `usability-findings.md` với ngày, participant profile và evidence quan sát được.

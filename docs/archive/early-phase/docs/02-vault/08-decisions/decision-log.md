# Decision Log - ProcureAI

> **Status:** Draft register. Chỉ các quyết định có xác nhận của nhóm mới được chuyển thành Decision chính thức.

| ID | Decision | Status | Source / owner |
|---|---|---|---|
| DEC-001 | MVP dùng workflow Request → Approve → Collect Quotations → Compare → PO → Receive → Close. | Confirmed in Charter/Requirements | `CON-01`, Project Charter |
| DEC-002 | AI không tự Approve, Reject, chọn Supplier hoặc thay thế quyết định của người có thẩm quyền. | Confirmed in Charter/Requirements | `CON-03`, `REQ-BR-08` |
| DEC-003 | PR vượt Budget có thể được Manager Reject hoặc chuyển Finance kiểm tra/phê duyệt. | Confirmed in current project docs | `REQ-FR-06`, `REQ-BR-04` |
| DEC-004 | MVP đối soát `PR ↔ PO ↔ Receiving`; Invoice và đối soát kế toán chi tiết để phase sau. | Confirmed in Charter/Persona risk review | Project Charter, Persona/JTBD |
| DEC-005 | Số quotation tối thiểu trước Compare. | Open | `Q-01`/open decision cần bổ sung vào Requirements |
| DEC-006 | Approval threshold và policy Budget chi tiết. | Open | `ASM-02`, `ASM-05`, `Q-03` |
| DEC-007 | Nguồn dữ liệu lịch sử và xử lý khi thiếu dữ liệu anomaly. | Open | User Research, `REQ-FR-15` |

## Decision protocol

Quyết định mới phải có người xác nhận, ngày xác nhận và nguồn tham chiếu trước khi được nâng thành Business Rule.

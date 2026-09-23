# Prototype Brief - ProcureAI

> **Status:** Draft planning brief. Không phải source-of-truth nghiệp vụ.

## Prototype objective

Kiểm tra các luồng quan trọng nhất của MVP bằng prototype web có thể tương tác.

## Critical screens

| Screen | User | Purpose | Traceability |
|---|---|---|---|
| PR Creation | Employee | Nhập PR, xem AI suggestion và Submit. | REQ-FR-01 đến REQ-FR-04 |
| Manager Approval | Manager | Xem PR, Budget và quyết định. | REQ-FR-05 đến REQ-FR-09 |
| Quotation Comparison | Procurement | Review extraction, so sánh và chọn Supplier. | REQ-FR-10 đến REQ-FR-15 |
| PO Creation | Procurement | Tạo PO từ PR và Supplier đã chọn. | REQ-FR-16 |
| Receiving | Người dùng có quyền | Ghi nhận nhận đủ, một phần hoặc sai lệch. | REQ-FR-17 |
| Workflow Dashboard | Các role liên quan | Theo dõi trạng thái và Audit Trail. | REQ-FR-04, REQ-NFR-03 |

## Prototype states to demonstrate

- PR thiếu trường bắt buộc.
- AI suggestion cần human review.
- PR vượt Budget và nhánh chuyển Finance.
- Quotation extraction có thể chỉnh sửa.
- Receiving có sai lệch và không được Close ngay.
- Self-Approval bị chặn.

## Not decided yet

Visual design system, navigation model, responsive breakpoints và dữ liệu demo chưa được xác nhận.

# Product Requirements Document - ProcureAI

> **Status:** Draft interpretation. Source of truth remains Requirements and Business Rules.

## 1. Product goal

Cung cấp một nền tảng web khép kín quy trình mua sắm nội bộ từ Request đến Close, giúp chuẩn hóa PR, kiểm soát ngân sách, so sánh báo giá và truy vết quyết định.

## 2. Primary users

Employee, Manager, Procurement, Finance và Admin. Chi tiết persona và evidence nằm trong [Personas & JTBD](../01-discovery/3.personas-and-jtbd.md).

## 3. Critical workflow

`Request → Approve → Collect Quotations → Compare → PO → Receive → Close`

## 4. MVP capabilities

| Capability | Requirement traceability |
|---|---|
| Purchase Request and validation | REQ-FR-01, REQ-FR-02 |
| PR Standardizer | REQ-FR-03 |
| PR status tracking | REQ-FR-04 |
| Manager and Finance approval | REQ-FR-05 đến REQ-FR-09 |
| Supplier and Quotation management | REQ-FR-10 đến REQ-FR-12 |
| AI comparison and anomaly alert | REQ-FR-13 đến REQ-FR-15 |
| PO creation | REQ-FR-16 |
| Receiving and Close | REQ-FR-17, REQ-FR-18 |
| RBAC and Audit Trail | REQ-NFR-02, REQ-NFR-03 |

## 5. Product principles

- Human-in-the-loop cho mọi AI extraction, recommendation và approval support.
- Requirement và Business Rule đã xác nhận được ưu tiên hơn prototype hoặc product interpretation.
- Cảnh báo AI phải hiển thị lý do và dữ liệu đối sánh.
- Không self-approval.

## 6. Open decisions

Số quotation tối thiểu, approval threshold chi tiết, nguồn dữ liệu lịch sử và policy xử lý thiếu dữ liệu vẫn cần được xác nhận trong Decision Log.

# User Flow - ProcureAI

## Main flow

```mermaid
flowchart LR
    A[Employee tạo PR] --> B[Review AI suggestion]
    B --> C[Manager Review]
    C -->|Approve| D[Collect Quotations]
    C -->|Chuyển Finance| E[Finance Budget Check]
    C -->|Reject / Revision| X[End or sửa PR]
    E -->|Approve| D
    E -->|Reject / Revision| X
    D --> F[Compare Quotations]
    F --> G[Procurement chọn Supplier]
    G --> H[Tạo PO]
    H --> I[Receiving]
    I -->|Nhận đủ| J[Close]
    I -->|Sai lệch| K[Receiving Exception]
    K --> I
```

## Role flows

| Role | Primary flow |
|---|---|
| Employee | Tạo PR → Review AI → Submit → Theo dõi trạng thái → Phối hợp Receiving |
| Manager | Xem PR → Budget visibility → Approve / Reject / Revision / Chuyển Finance |
| Finance | Kiểm tra Budget → Approve hoặc Reject theo policy |
| Procurement | Thu thập Quotation → Review extraction → Compare → Chọn Supplier → Tạo PO |
| Admin | Quản lý RBAC, danh mục, Budget và Audit Trail |

## Flow constraints

- Không Collect Quotations trước khi PR được Approve.
- Không tạo PO trước khi PR được Approve và Supplier được chọn.
- Không Close trước khi Receiving và đối soát `PR ↔ PO ↔ Receiving` hoàn tất.
- AI không thay thế quyết định của người có thẩm quyền.

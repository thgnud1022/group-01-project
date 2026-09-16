# TEST CASES — US-09

## TC-US09-001

### Title
Không cho phép tạo PO khi PR chưa APPROVED

### Preconditions
PR tồn tại.

PR status:
PENDING_MANAGER_APPROVAL

### Steps

1. Chọn PR.
2. Chọn quotation.
3. Thực hiện Create PO.

### Expected Result

Hệ thống từ chối tạo PO.

PO không được tạo.

PR không chuyển sang PO_CREATED.

### Actual Result

CHƯA EXECUTE

### Status

NOT RUN
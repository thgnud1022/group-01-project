# DATA MODEL & PRISMA SCHEMA SPECIFICATION

Mô hình dữ liệu thực thể của dự án được định nghĩa chính xác trong tệp `backend/prisma/schema.prisma`.

## Các Thực Thể Chính & Ràng Buộc (Entities & Rules)

1. **`User`**: Quản lý tài khoản người dùng và phân quyền RBAC.
   * `role`: Enum `[EMPLOYEE, MANAGER, PROCUREMENT, FINANCE, ADMIN]`
   * Khoản mật khẩu băm bảo mật bằng bcrypt.

2. **`Department` & `Budget`**: Quản lý hạn mức chi tiêu phòng ban theo năm/quý.
   * `allocatedAmount`: Hạn mức được cấp (Decimal 18,2).
   * `spentAmount`: Số tiền đã chi thực tế sau khi Close PR (Decimal 18,2).
   * `tempReservedAmount`: Số tiền tạm tính bị khóa từ các PR đang xử lý (Decimal 18,2).
   * Ràng buộc duy nhất: `[departmentId, fiscalYear, quarter]`.

3. **`PurchaseRequest` & `PRItem`**: Yêu cầu mua sắm và chi tiết vật tư.
   * `estimatedValue`: Tổng giá trị dự kiến.
   * `status`: Enum `[DRAFT, PENDING_MANAGER_APPROVAL, PENDING_FINANCE_APPROVAL, APPROVED, COLLECTING_QUOTATIONS, PO_CREATED, PARTIALLY_RECEIVED, RECEIVED, CLOSED, REJECTED]`.

4. **`Supplier` & `Quotation`**: Báo giá nhà cung cấp do AI trích xuất.
   * `isAnomaly`: Cờ báo hiệu bất thường đơn giá ($\geq 20\%$).
   * `anomalyReason`: Lý do chi tiết do AI sinh ra.

5. **`PurchaseOrder` & `Receiving`**: Đơn đặt hàng và biên bản giao nhận.
   * Ràng buộc BR-03: Đơn giá PO lấy $100\%$ từ Quotation được chọn.
   * Ràng buộc BR-04: `receivedQty` tích lũy không vượt quá `quantity` của PO.

6. **`Approval`**: Nhật ký lưu vết phê duyệt/từ chối kèm bình luận.

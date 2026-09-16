import { test, expect } from '@playwright/test';

/**
 * BẰNG CHỨNG KIỂM THỬ TỰ ĐỘNG E2E (AUTOMATED TEST EVIDENCE)
 * User Story: US-09 - Lựa chọn Supplier và tạo Purchase Order
 * Quy tắc truy vết: REQ-FR-16, REQ-BR-12, ASM-04 (Khóa 100% đơn giá & số lượng)
 */

test.describe('US-09: Lựa chọn Supplier và tạo Purchase Order (E2E Procurement Flow)', () => {

  // Định nghĩa các hằng số kiểm thử theo tài khoản Seed từ Runbook.md
  const USER_PROCUREMENT = 'procurement@company.com';
  const PASSWORD_DEFAULT = 'password123';

  // Dữ liệu mock phục vụ kiểm tra tính bất biến của đơn giá (ASM-04 / REQ-BR-12)
  const SELECTED_SUPPLIER = 'Công ty Phong Vũ';
  const EXPECTED_PRODUCT_NAME = 'Laptop Dell';
  const EXPECTED_QTY = 1;
  const EXPECTED_PRICE_RAW = 25000000; // 25.000.000đ
  const EXPECTED_PRICE_DISPLAY = '25.000.000';

  test.beforeEach(async ({ page }) => {
    // 1. Điều hướng đến trang login và đăng nhập với vai trò Procurement (REQ-NFR-02)
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill(USER_PROCUREMENT);
    await page.locator('input[type="password"]').fill(PASSWORD_DEFAULT);
    await page.locator('button[type="submit"]').click();

    // Xác nhận đã đăng nhập thành công và chuyển hướng đến Dashboard của Procurement
    await expect(page).toHaveURL(/.*dashboard|.*pr/);
  });

  /**
   * KỊCH BẢN 1 (AC1 & AC3): Luồng chuẩn - PR đã duyệt -> Chọn báo giá -> Tạo PO thành công & Khóa đơn giá
   */
  test('TC-09-01: Tạo PO thành công khi PR đã Approved và báo giá được chọn (Khóa đơn giá 100%)', async ({ page }) => {
    // 1. Điều hướng đến danh sách PR của Procurement và chọn một PR có trạng thái APPROVED/COLLECTING_QUOTATIONS
    await page.goto('http://localhost:5173/pr');

    // Định vị PR đã APPROVED và click xem chi tiết
    const prRow = page.locator('tr:has-text("APPROVED"), tr:has-text("COLLECTING_QUOTATIONS")').first();
    await expect(prRow).toBeVisible();
    await prRow.locator('button:has-text("Xem chi tiết"), a').click();

    // 2. Kiểm tra giao diện so sánh báo giá (ComparisonTable) từ 3 Supplier độc lập (REQ-FR-12 / REQ-BR-06)
    await expect(page.locator('table.comparison-table, div#comparison-section')).toBeVisible();

    // Xác minh thông tin Báo giá của Supplier mong muốn có hiển thị trên UI
    const supplierCard = page.locator(`.supplier-card:has-text("${SELECTED_SUPPLIER}")`);
    await expect(supplierCard).toBeVisible();
    await expect(supplierCard).toContainText(EXPECTED_PRODUCT_NAME);
    await expect(supplierCard).toContainText(EXPECTED_PRICE_DISPLAY);

    // 3. Tiến hành CHỌN BÁO GIÁ (Select Supplier) - AI chỉ gợi ý, Procurement trực tiếp bấm chọn (REQ-BR-08)
    const selectButton = supplierCard.locator('button:has-text("Chọn báo giá"), button:has-text("Lựa chọn")');
    await selectButton.click();

    // Xác nhận nút đổi sang trạng thái đã chọn (Visual Feedback)
    await expect(supplierCard.locator('badge:has-text("Đã chọn"), span:has-text("Đã chọn")').first()).toBeVisible();

    // 4. Click nút "Khởi tạo đơn đặt hàng PO" (Create PO)
    const createPoButton = page.locator('button:has-text("Khởi tạo Purchase Order"), button:has-text("Tạo PO")');
    await expect(createPoButton).toBeEnabled();
    await createPoButton.click();

    // 5. Xác minh xuất hiện Modal Xác nhận tạo PO ghi rõ quy định KHÓA ĐƠN GIÁ (DESIGN.md UX Copy Table)
    const confirmModal = page.locator('div.modal, div.confirm-dialog');
    await expect(confirmModal).toBeVisible();
    await expect(confirmModal).toContainText(`Xác nhận tạo Đơn đặt hàng`);
    await expect(confirmModal).toContainText(`Đơn giá trên PO được khóa cố định 100%`);

    // Click xác nhận tạo PO trên Modal (Explicit Confirmation)
    await confirmModal.locator('button:has-text("Xác nhận"), button:has-text("Đồng ý")').click();

    // 6. Kiểm tra Toast Notification báo thành công
    const toastSuccess = page.locator('.toast-success, div:has-text("thành công")').first();
    await expect(toastSuccess).toBeVisible();

    // 7. Quay lại trang chi tiết PR và kiểm tra xem StatusBadge đã cập nhật trạng thái mới hay chưa (DESIGN.md Component)
    await expect(page).toHaveURL(/.*pr\/\d+/);
    const statusBadge = page.locator('span.status-badge, .badge');
    await expect(statusBadge).toContainText('PO_CREATED');

    // 8. KIỂM TRA CHỐNG GIAN LẬN/HALLUCINATION (AC3 / REQ-BR-12 / ASM-04): 
    // Kiểm tra xem ô Đơn giá và Số lượng trên màn hình PO hiển thị đã bị KHÓA CỨNG (disabled/readOnly)
    const poItemsTable = page.locator('table#po-items-table, .po-details-table');
    await expect(poItemsTable).toBeVisible();

    const unitPriceInput = poItemsTable.locator('input[name="unitPrice"]').first();
    const quantityInput = poItemsTable.locator('input[name="quantity"]').first();

    // Khẳng định chắc chắn rằng giao diện khóa cứng không cho phép chỉnh sửa đơn giá/số lượng thủ công
    await expect(unitPriceInput).toHaveAttribute('readonly', '');
    await expect(quantityInput).toHaveAttribute('readonly', '');

    // Đảm bảo dữ liệu đơn giá và số lượng khớp 100% không lệch 1 xu so với Quotation
    await expect(unitPriceInput).toHaveValue(EXPECTED_PRICE_RAW.toString());
    await expect(quantityInput).toHaveValue(EXPECTED_QTY.toString());
  });

  /**
   * KỊCH BẢN 2 (AC2): Chặn tạo PO khi PR chưa APPROVED (Vướng rào cản quy trình)
   */
  test('TC-09-02: Hệ thống chặn đứng hành động tạo PO nếu PR chưa được Approved', async ({ page }) => {
    // 1. Cố ý điều hướng trực tiếp bằng URL tới trang tạo PO cho một PR vẫn đang ở trạng thái PENDING_MANAGER_APPROVAL
    const pendingPrId = 'pr-pending-test-id-123';
    await page.goto(`http://localhost:5173/pr/${pendingPrId}/create-po`);

    // 2. Hệ thống phải nhận diện PR chưa APPROVED và hiển thị lỗi cảnh báo nghiệp vụ ngay trên UI
    const errorAlert = page.locator('.error-banner, .alert-danger, div:has-text("chưa được phê duyệt")');
    await expect(errorAlert).toBeVisible();
    await expect(errorAlert).toContainText('chưa được phê duyệt');

    // 3. Nút bấm submit PO trên trang này (nếu có) phải bị vô hiệu hóa hoặc ẩn đi
    const submitPoButton = page.locator('button:has-text("Xác nhận tạo PO"), button:has-text("Lưu PO")');
    await expect(submitPoButton).toBeDisabled();
  });

  /**
   * KỊCH BẢN 3: Kiểm thử phi chức năng - Phân quyền RBAC (REQ-NFR-02)
   * Đảm bảo tài khoản vai trò Employee bình thường không thể truy cập trái phép luồng Lựa chọn Supplier/Tạo PO
   */
  test('TC-09-03: Tài khoản Employee bình thường bị cấm truy cập tính năng lựa chọn báo giá và tạo PO', async ({ page }) => {
    // Đăng xuất tài khoản Procurement hiện tại
    await page.locator('button:has-text("Đăng xuất"), .logout-btn').click();

    // Đăng nhập lại dưới vai trò Employee thường
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('employee@company.com');
    await page.locator('input[type="password"]').fill(PASSWORD_DEFAULT);
    await page.locator('button[type="submit"]').click();

    // Cố gắng truy cập vào đường dẫn quản lý báo giá và tạo PO của PR
    await page.goto('http://localhost:5173/pr/some-approved-pr-id/comparison');

    // Hệ thống phải đá người dùng về trang chủ hoặc hiện màn hình 403 Forbidden
    const forbiddenMessage = page.locator('div:has-text("403"), div:has-text("Không có quyền truy cập"), .forbidden-banner');
    await expect(forbiddenMessage).toBeVisible();
  });
});

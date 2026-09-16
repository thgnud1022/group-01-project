# DESIGN SYSTEM & UI HANDOFF: AI Procurement System

## 1. Design Tokens
* **Primary Color (Brand):** `#1E3A8A` (Deep Navy Blue - Thể hiện tính doanh nghiệp & tin cậy)
* **Success Color:** `#15803D` (Emerald Green - Ngân sách đủ, Duyệt thành công)
* **Warning Color:** `#B45309` (Amber Gold - Cần Finance duyệt bước 2, Đang bóc tách AI)
* **Danger/Anomaly Color:** `#B91C1C` (Ruby Red - Vượt ngân sách, Cảnh báo nâng giá $\geq 20\%$)
* **Neutral Dark:** `#1F2937` (Gray-800 - Text chính)
* **Border Radius:** `8px` (Thống nhất cho Cards, Inputs, Modals)

## 2. Component Inventory
* **`VoiceComposer`:** Nút ghi âm micro + Text fallback + Transcript hiển thị trực tiếp.
* **`BudgetIndicator`:** Thanh tiến trình ngân sách phòng ban (Đã chi, Tạm tính, Khả dụng).
* **`ComparisonTable`:** Bảng so sánh 3 báo giá tự động sinh từ AI với highlight dòng đơn giá thấp nhất và badge đỏ cảnh báo bất thường.
* **`StatusBadge`:** Badge hiển thị các trạng thái PR (`DRAFT`, `PENDING_MANAGER`, `PENDING_FINANCE`, `APPROVED`, `PO_CREATED`, `CLOSED`).

## 3. UX Copy Table
| Context | Microcopy / Notification |
| :--- | :--- |
| **Vượt ngân sách** | `"Không thể tạo PR: Giá trị ước tính (75.000.000đ) vượt quá Ngân sách khả dụng còn lại của Phòng Kế toán (50.000.000đ)."` |
| **Cảnh báo bất thường giá** | `"CẢNH BÁO AI: Đơn giá 31.000.000đ/cái cao hơn 24% so với đơn giá trung bình lịch sử thu mua thiết bị tương tự (25.000.000đ)."` |
| **Phát hành PO** | `"Xác nhận tạo Đơn đặt hàng PO-2026-001 từ báo giá của Công ty Phong Vũ. Đơn giá trên PO được khóa cố định 100%."` |

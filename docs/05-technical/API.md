# API CONTRACT SPECIFICATION: REST Endpoints & RBAC Auth

Tất cả API ngoại trừ `/api/auth/login` đều bắt buộc đính kèm Header: `Authorization: Bearer <JWT_TOKEN>`.

## 1. Authentication & System Health
* `POST /api/auth/login`: Đăng nhập hệ thống, trả về JWT Token chứa `userId`, `role`, `departmentId`.
* `GET /api/health`: Healthcheck endpoint kiểm tra dịch vụ Backend và kết nối PostgreSQL.

## 2. AI Assistant Endpoints
* `POST /api/assistant/standardize-pr`
  * **Auth:** `EMPLOYEE`
  * **Input:** `{ "raw_text": "Cần mua 3 laptop Dell 25tr cho dev" }`
  * **Output:** JSON chuẩn hóa `{ "title": "...", "items": [...], "estimatedValue": 75000000 }`
* `POST /api/quotations/compare`
  * **Auth:** `PROCUREMENT`
  * **Input:** `{ "purchaseRequestId": "PR-001", "files": ["q1.pdf", "q2.pdf"] }`
  * **Output:** JSON so sánh báo giá + Cảnh báo bất thường `isAnomaly` & `anomalyReason`.

## 3. Purchase Request (PR) Endpoints
* `POST /api/pr`: Tạo PR mới (Tự động trigger Budget Check `REQ-BR-01`).
* `GET /api/pr`: Lấy danh sách PR (Filter theo vai trò & phòng ban).
* `POST /api/pr/:id/approve`
  * **Auth:** `MANAGER` / `FINANCE`
  * **Behavior:** PR $> 50$tr sau khi Manager duyệt sẽ chuyển trạng thái `PENDING_FINANCE_APPROVAL`.

## 4. Purchase Order (PO) & Receiving Endpoints
* `POST /api/po`
  * **Auth:** `PROCUREMENT`
  * **Behavior:** Sao chép $100\%$ đơn giá từ Quotation được chọn sang PO (`REQ-BR-03`).
* `POST /api/receiving`
  * **Auth:** `PROCUREMENT` / `EMPLOYEE`
  * **Behavior:** Nhập số lượng hàng thực nhận kèm ảnh biên bản, kiểm tra không vượt quá PO (`REQ-BR-04`).
* `POST /api/pr/:id/close`
  * **Auth:** `FINANCE`
  * **Behavior:** Trừ tiền chính thức vào `spentAmount`, giải phóng `tempReservedAmount`, chuyển PR sang `CLOSED`.

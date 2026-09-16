# STRATEGY & SUITE KIỂM THỬ: Automated & E2E Testing Plan

## 1. Tháp Kiểm Thử (Testing Pyramid)
* **Unit & API Testing (`pytest`):** Bao phủ 60-70% logic nghiệp vụ (Budget check, Duyệt 2 cấp, Anomaly alert, PO lock price).
* **Integration Testing:** 15-25% phối hợp giữa FastAPI, PostgreSQL DB và AI Parser Service.
* **End-to-End Testing (`Playwright`):** 5-15% bao phủ 100% luồng mua sắm chính từ lúc tạo PR đến khi Close PR.

## 2. Danh Sách Kịch Bản Kiểm Thử Tự Động (Test Cases Inventory)

| ID | Tên Kịch Bản | Cấp độ | Quy tắc truy vết | Kết quả kỳ vọng |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Tạo PR trong hạn mức ngân sách | API | `REQ-FR-01`, `REQ-BR-01` | Tạo PR thành công, trạng thái `PENDING_MANAGER_APPROVAL`. |
| **TC-02** | Chặn tạo PR vượt quá ngân sách | API | `REQ-BR-01` | HTTP 400 Bad Request, báo lỗi vượt ngân sách. |
| **TC-03** | Duyệt PR $\leq 50$ triệu VND | API | `REQ-BR-02` | Trạng thái chuyển thẳng sang `APPROVED`. |
| **TC-04** | Duyệt PR $> 50$ triệu VND | API | `REQ-BR-02` | Manager duyệt $\rightarrow$ Status = `PENDING_FINANCE_APPROVAL`. |
| **TC-05** | Phê duyệt PR bước 2 bởi Finance | API | `REQ-BR-02` | Status chuyển sang `APPROVED`. |
| **TC-06** | AI bóc tách và so sánh báo giá PDF | Integration | `REQ-FR-05`, `REQ-FR-06` | Trích xuất thành công 3 báo giá, tính tổng chi phí. |
| **TC-07** | Phát hiện bất thường đơn giá $\geq 20\%$ | Integration | `REQ-FR-07` | Trả về `isAnomaly = True` kèm lý do chi tiết. |
| **TC-08** | Khởi tạo PO khóa cố định 100% đơn giá | API | `REQ-BR-03` | PO được tạo với đơn giá khớp chính xác với Báo giá. |
| **TC-09** | Chặn nhận hàng vượt quá số lượng PO | API | `REQ-BR-04` | HTTP 400 Bad Request khi `receivedQty` > PO `quantity`. |
| **TC-10** | Finance đóng hồ sơ hạch toán ngân sách | API | `REQ-FR-10` | Status = `CLOSED`, `spentAmount` được cập nhật chính xác. |
| **TC-11** | E2E Playwright: Full 7-Step Procurement Journey | E2E | All REQs | Toàn bộ luồng UI chạy thông suốt 0 lỗi. |

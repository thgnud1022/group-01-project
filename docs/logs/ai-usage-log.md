# AI USAGE LOG: Nhật Ký Sử Dụng AI Có Kiểm Chứng (Nhóm 1)

Nhật ký ghi nhận quá trình con người làm việc phối hợp cùng AI, đánh giá các đề xuất của AI và thực hiện kiểm chứng độc lập theo quy định môn học.

| Entry ID | Thành viên | Task / Story | Prompt / Skill | AI Output | Human Verification & Decision | Impact / Value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A-01** | BA Lead (TV1) | REQ-FR-01: Chuẩn hóa PR | PRD Writer / Requirement Reviewer | Đề xuất cho phép AI tự động chọn Nhà cung cấp tốt nhất khi tạo PR. | **Từ chối đề xuất.** Quy trình thu mua bắt buộc qua bước duyệt Manager và thu thập báo giá độc lập trước khi chọn NCC. Thêm `REQ-BR-03`. | Ngăn ngừa việc chọn nhà thầu tự động không có kiểm soát. |
| **A-02** | AI Specialist (TV2) | Vault Q&A Benchmark | Vault Q&A Benchmark Generator | Tạo 20 câu hỏi benchmark, trong đó AI tự bịa câu trả lời cho chính sách lưu trữ history 30 ngày. | **Sửa câu trả lời Q-08 thành "KHÔNG ĐỦ DỮ LIỆU"**. Cập nhật system prompt ép AI chỉ trả lời từ Vault context. | Đảm bảo AI tuân thủ nguyên tắc 0% hallucination. |
| **A-03** | UI/UX Designer (TV3) | Design System | Component State Generator | Gợi ý thiết kế nút "Duyệt nhanh PR" bỏ qua bước kiểm tra ngân sách. | **Từ chối nút Duyệt nhanh.** Tất cả nút Approve bắt buộc gọi API kiểm tra ngân sách thời gian thực ở Backend. | Bảo vệ tính toàn vẹn của ngân sách phòng ban. |
| **A-04** | Lead Dev (TV4) | API & Data Model | Prisma Schema Generator | Đề xuất dùng kiểu `Float` cho trường `estimatedUnitPrice` và `allocatedAmount`. | **Đổi sang `Decimal(18,2)`**. Tránh lỗi làm tròn số thực (floating point imbalance) khi tính toán tiền tệ VND. | Đảm bảo độ chính xác tài chính 100%. |
| **A-05** | QA Engineer (TV5) | Playwright E2E Test | E2E Test Scenario Designer | Kịch bản E2E cho phép tạo PO mà không cần đính kèm file báo giá. | **Sửa kịch bản E2E.** Thêm bước upload file PDF báo giá gốc và verify đơn giá PO khớp $100\%$. | Đạt chuẩn Definition of Done cấp Release. |

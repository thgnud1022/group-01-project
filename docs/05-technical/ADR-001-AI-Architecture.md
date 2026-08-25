# ADR-001: Kiến Trúc Xử Lý AI & Mô Hình Phân Trích Báo Giá (AI Architecture & Fallback)

* **Trạng thái:** Accepted
* **Ngày quyết định:** 2026-08-25
* **Người quyết định:** AI Specialist (Thành viên 2) & cả Nhóm 1

## Bối Cảnh (Context)
Dự án cần xử lý 2 tác vụ AI chính: (1) Chuẩn hóa văn bản thô PR thành JSON và (2) Trích xuất/so sánh file PDF báo giá từ nhiều nhà cung cấp. Yêu cầu môn học đòi hỏi độ trễ phản hồi $\leq 3.5$ giây trong demo, không hallucinate giá cả/ngân sách và sẵn sàng phản hồi chính xác khi chấm bảo cáo.

## Quyết Định (Decision)
Xây dựng lớp **AI Assistant Service Layer** theo mô hình Hybrid Orchestration:
1. **Output Schema Cố Định:** Mọi kết quả từ LLM bắt buộc phải tuân theo Pydantic Schema ở Backend. LLM không có quyền trực tiếp thao tác Database hay tự sinh giá PO.
2. **Multi-Provider Fallback:**
   * **Primary Provider:** Google Gemini / OpenAI API cho môi trường kết nối internet.
   * **Local / Deterministic Mock Service:** Tích hợp bộ Mock AI Parser chuẩn dựa trên Regex & PDF Plumber Rule-based Parser. Bộ Parser này phản hồi cực nhanh ($\leq 0.5$s), đảm bảo 100% không bao giờ lỗi kết nối mạng hay hết quota API trong quá trình báo cáo Demo Viva với Giảng viên.

## Hậu Quả & Đánh Giá (Consequences)
* **Tích cực:** Tốc độ phản hồi cực nhanh, 0% rủi ro hallucinate giá tài chính, đảm bảo demo 100% mượt mà.
* **Hạn chế:** Cần bảo trì Pydantic schema validation ở Backend.

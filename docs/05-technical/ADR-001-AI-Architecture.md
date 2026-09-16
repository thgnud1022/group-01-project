# ADR-001: Kiến Trúc Xử Lý AI & Mô Hình Phân Trích Báo Giá (AI Architecture & Fallback)

* **Trạng thái:** Accepted
* **Ngày quyết định:** 2026-08-25
* **Người quyết định:** AI Specialist (Thành viên 2) & cả Nhóm 1

## Bối Cảnh (Context)
Dự án cần xử lý các tác vụ AI chính: (1) Chuẩn hóa Purchase Request và gợi ý thông tin còn thiếu, (2) Trích xuất và chuẩn hóa thông tin từ file Quotation, (3) Phân tích và so sánh Quotation, (4) đưa ra Recommendation, và (5) phát hiện Anomaly Alert đối với đơn giá cao hơn hoặc bằng 20% so với mức trung bình lịch sử của sản phẩm cùng loại. Hệ thống cần kiểm soát kết quả AI để tránh hallucination đối với dữ liệu giá và ngân sách.

## Quyết Định (Decision)
Xây dựng lớp **AI Assistant Service Layer** theo mô hình Hybrid Orchestration:
1. **Output Schema Cố Định:** Mọi kết quả từ LLM bắt buộc phải tuân theo Pydantic Schema ở Backend. LLM không có quyền trực tiếp thao tác Database hay tự sinh giá PO.
2. **Multi-Provider Fallback:**
   * **Primary Provider:** Google Gemini / OpenAI API cho môi trường kết nối internet.
   * **Local / Deterministic Mock Service:** Tích hợp bộ Mock AI Parser chuẩn dựa trên Regex & PDF Plumber Rule-based Parser. Bộ Parser này phản hồi cực nhanh ($\leq 0.5$s), đảm bảo 100% không bao giờ lỗi kết nối mạng hay hết quota API trong quá trình báo cáo Demo Viva với Giảng viên.
   * AI Procurement Functions: AI Assistant Service Layer hỗ trợ các chức năng chuẩn hóa Purchase Request, trích xuất/chuẩn hóa Quotation, so sánh Quotation, đưa ra Recommendation và phát hiện Anomaly Alert khi đơn giá cao hơn hoặc bằng 20% so với mức trung bình lịch sử của sản phẩm cùng loại.

## Hậu Quả & Đánh Giá (Consequences)
Tích cực: Tăng tính ổn định của hệ thống, giảm phụ thuộc vào API bên ngoài, kiểm soát output AI thông qua schema validation và hỗ trợ phát hiện các trường hợp giá bất thường.

Hạn chế: Cần duy trì Pydantic schema validation và Mock Parser; kết quả AI vẫn cần được người dùng kiểm tra trước khi đưa ra quyết định nghiệp vụ.

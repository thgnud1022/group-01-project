# QUY TẮC GIẢI QUYẾT MÂU THUẪN NGUỒN (SOURCE PRIORITY)

Khi xảy ra không đồng nhất dữ liệu giữa các tài liệu, quy tắc phân xử mâu thuẫn được áp dụng nghiêm ngặt theo thứ tự ưu tiên giảm dần từ Mức 1 đến Mức 6:

1. **Mức 1 (Ưu tiên cao nhất):** Business Rules (`REQ-BR-*`) và Requirements (`REQ-FR-*`) đã được phê duyệt mới nhất trong `docs/01-discovery/requirements.md`.
2. **Mức 2:** Các quyết định kiến trúc kỹ thuật đã ký duyệt trong Decision Log (`docs/05-technical/ADR-*.md`).
3. **Mức 3:** Đặc tả sản phẩm chính thức hiện tại (`docs/03-product/PRD.md`).
4. **Mức 4:** Đặc tả User Story và Acceptance Criteria đang triển khai trong Sprint.
5. **Mức 5:** Bản thiết kế Figma và UX Copy trong `docs/04-design/DESIGN.md` (Chỉ tham khảo giao diện, không tự ý sinh quy tắc nghiệp vụ mới).
6. **Mức 6 (Ưu tiên thấp nhất):** Đầu ra thô của AI hoặc ghi chú thảo luận chưa tích hợp vào Vault.

> [!WARNING]
> **Quy tắc bắt buộc đối với AI Agent:** AI tuyệt đối không được tự ý lựa chọn nguồn có ưu tiên thấp hơn để ghi đè nguồn có ưu tiên cao hơn. Nếu phát hiện xung đột, AI phải trả về phản hồi cảnh báo và yêu cầu con người xác nhận.

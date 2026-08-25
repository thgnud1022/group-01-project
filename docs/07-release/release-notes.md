# RELEASE NOTES: AI Procurement & Purchase Approval System v1.0.0

**Ngày phát hành:** 2026-08-25  
**Trạng thái:** Golden Sample Release Candidate  

## Các Tính Năng Đã Hoàn Thành (Added Features)
* **Voice & Text PR Standardization:** Nhập liệu PR bằng giọng nói/văn bản thô, AI tự bóc tách sản phẩm, số lượng, đơn giá ước tính.
* **Real-time Budget Guard:** Tự động kiểm tra ngân sách khả dụng của phòng ban trước khi cho phép gửi PR.
* **Multi-level Approval Workflow:** Tự động phân cấp luồng duyệt 1 cấp ($\leq 50$tr) hoặc 2 cấp ($> 50$tr với chữ ký duyệt của Finance).
* **AI Quotation Extraction & Comparison:** Tải lên tối đa 3 file PDF báo giá, AI tự động lập bảng so sánh và đưa ra cảnh báo đơn giá bất thường $\geq 20\%$.
* **PO Lock Price Enforcement:** Tự động khóa $100\%$ đơn giá từ báo giá sang PO để chống gian lận/hallucination.
* **Goods Receipt & Budget Close:** Ghi nhận hàng thực nhận kèm ảnh biên bản, Finance chính thức hạch toán đóng hồ sơ mua sắm.

## Kết Quả Kiểm Thử Chất Lượng (Quality Gates)
* **API Unit Tests:** 10/10 PASS (`pytest`).
* **E2E Integration Tests:** 1/1 PASS (`Playwright`).
* **20-Q&A Benchmark Accuracy:** 20/20 PASS ($100\%$ grounded, $0\%$ hallucination).

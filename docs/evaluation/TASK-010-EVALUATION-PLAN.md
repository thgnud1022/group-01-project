# TASK-010: AI EVALUATION PLAN
- **Project:** AI Procurement & Purchase Approval System (Group 01)
- **Branch:** `final-delivery`
- **Task Type:** Quality Benchmark & AI Evaluation
- **Reference Requirement:** `REQ-FR-13`, `REQ-FR-14`, `REQ-FR-15`, `HD-03`, `TASK-010` in [`docs/IMPLEMENTATION_PLAN.md`](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md#L638)

---

## 1. Mục tiêu (Objectives)
1. Đo lường có hệ thống chất lượng và độ ổn định của các chức năng AI (PR Standardization và Quotation Recommendation) đã triển khai trong TASK-009.
2. Xây dựng bộ dữ liệu đánh giá gồm **24 evaluation cases** đại diện cho các kịch bản thực tế trong quy trình mua sắm doanh nghiệp.
3. Áp dụng Rubric đánh giá định lượng 5 chiều (0–100 điểm) để xác định tỷ lệ thành công (Pass Rate), tính hợp lý của đề xuất và khả năng kiểm soát ảo giác (Hallucination).
4. Phân định rõ ràng giữa chế độ Live LLM và chế độ Fallback/Heuristic Runtime hiện tại.
5. Bảo đảm tính tái hiện (Reproducibility) thông qua script tự động `run_eval.py`.

---

## 2. Phạm vi đánh giá (Evaluation Scope)
Hệ thống AI được đánh giá bao gồm 2 năng lực cốt lõi:
1. **Năng lực A — PR Standardization (`standardize_pr`)**:
   - Khả năng chuẩn hóa tiêu đề và trích xuất danh mục hàng hóa (`itemName`, `quantity`, `estimatedUnitPrice`).
   - Khả năng tính toán tổng giá trị ước tính (`total_estimated_value`).
   - Khả năng xử lý input đa dạng: chuẩn, thiếu trường, mơ hồ, nhiễu, không dấu, và chuỗi rỗng.
2. **Năng lực B — Quotation Recommendation (`recommend_quotations`)**:
   - Khả năng phân tích bảng báo giá so sánh.
   - Khả năng xếp hạng (`rankings`) và chấm điểm (`score`).
   - Khả năng bóc tách ưu điểm (`pros`) và nhược điểm/rủi ro (`cons`).
   - Khả năng giải thích lý do đề xuất (`reasoning`).
   - Đảm bảo ranh giới **Decision Support**: không tự động duyệt PR, không tự tạo PO, không mutate database.
   - Khả năng ngăn chặn Hallucination: không bịa đặt nhà cung cấp hoặc đơn giá không có trong input.

---

## 3. Thiết kế Bộ Dữ Liệu (Dataset Design)
Dataset gồm 24 cases được chia làm 2 nhóm:
- **Group 1 (`EVAL-STD-001` đến `EVAL-STD-012`)**: Đánh giá chuẩn hóa Purchase Request.
- **Group 2 (`EVAL-REC-001` đến `EVAL-REC-012`)**: Đánh giá đề xuất và xếp hạng Báo giá.

Mỗi case trong file `TASK-010-DATASET.json` bao gồm:
- `case_id`: Định danh duy nhất.
- `task_type`: `standardize_pr` hoặc `recommend_quotations`.
- `category`: Happy path, Missing fields, Ambiguity, Anomaly, Trade-off, Anti-hallucination, v.v.
- `input`: Dữ liệu đầu vào thực tế.
- `expected_output`: Kỳ vọng chuẩn được xây dựng **trước** khi chạy evaluation.
- `criteria`: Các tiêu chí kiểm tra cụ thể theo Rubric.
- `traceability`: Liên kết với User Story và Yêu cầu nghiệp vụ (`US-01`, `US-07`, `REQ-FR-01`, `REQ-FR-14`, v.v.).

---

## 4. Quy trình Thực thi (Execution Protocol)
1. Script `run_eval.py` nạp file `TASK-010-DATASET.json`.
2. Lần lượt gửi từng case vào phương thức xử lý tương ứng của `AIService`:
   - `AIService.standardize_pr_async(raw_text)`
   - `AIService.recommend_quotations_async(req)`
3. Ghi nhận toàn bộ Actual Output thực tế.
4. Chấm điểm theo 5 tiêu chí Rubric (mỗi tiêu chí 0–20 điểm, tổng 100 điểm).
5. Xác định trạng thái `PASS` (Tổng điểm $\ge 70$) hoặc `FAIL` (Tổng điểm $< 70$).
6. Xuất kết quả chi tiết ra `TASK-010-RESULTS.md` và tổng hợp vào `TASK-010-REPORT.md`.

---

## 5. Giới hạn & Quy định Đạo đức (Limitations & Ethical Constraints)
- **Zero Circular Verification**: Kỳ vọng đầu ra (Expected Output) được xây dựng dựa trên đặc tả nghiệp vụ, tuyệt đối không lấy kết quả sinh ra của AI làm kỳ vọng.
- **Honest Reporting**: Báo cáo trung thực các trường hợp AI chưa tối ưu; không sửa code production chỉ để làm đẹp điểm số.
- **Backend Rule Authority**: Kết quả đề xuất của AI chỉ mang tính tham khảo hỗ trợ người dùng, các quy tắc backend (ngân sách, phê duyệt, anomaly $\ge 20\%$) luôn nắm thẩm quyền tuyệt đối.

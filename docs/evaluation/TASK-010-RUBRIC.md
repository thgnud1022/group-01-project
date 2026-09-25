# TASK-010: AI EVALUATION RUBRIC & SCORING METHODOLOGY

---

## 1. Nguyên tắc Chấm điểm (Core Principles)
1. **Khách quan & Xác định (Deterministic Scoring)**: Tiêu chí chấm điểm căn cứ trên các quy tắc logic đo lường được, không sử dụng cảm tính.
2. **Độc lập với Kết quả AI**: Chuẩn đánh giá (Ground Truth) được xác lập trước dựa trên yêu cầu nghiệp vụ và cấu trúc Pydantic Schema.
3. **Phân rã Đa chiều (Multi-dimensional Evaluation)**: Mỗi test case được đánh giá trên 5 tiêu chí độc lập (tổng thang điểm 100).
4. **Không dung thứ Ảo giác (Zero Tolerance for Critical Hallucination)**: Bất kỳ trường hợp bịa đặt mã nhà cung cấp hoặc đơn giá không có trong dữ liệu đầu vào đều bị phạt nặng ở tiêu chí Factual Consistency.

---

## 2. Thang Điểm 5 Chiều (5-Dimension Rubric — Max 100 Points)

| Mã Tiêu chí | Tên Tiêu chí | Trọng số | Định nghĩa & Tiêu chuẩn Đánh giá | Thang điểm |
|:---:|---|:---:|---|:---:|
| **C1** | **Schema Validity** | 20% | Dữ liệu đầu ra tuân thủ nghiêm ngặt Pydantic Schema (`StandardizeResponseSchema` hoặc `QuotationRecommendationResponse`). Kiểu dữ liệu chính xác, không thiếu trường bắt buộc, không sinh lỗi parse. | **0 - 20** |
| **C2** | **Field Correctness** | 20% | Các trường thông tin cốt lõi được trích xuất hoặc chuẩn hóa chính xác (Tên sản phẩm, số lượng, đơn giá, mã báo giá được khuyến nghị). | **0 - 20** |
| **C3** | **Factual Consistency & Anti-Hallucination** | 20% | Dữ liệu đầu ra phản ánh trung thực dữ liệu đầu vào; không tự ý thêm bớt nhà cung cấp, không bịa đặt con số tiền tệ, không tự ý suy đoán sai lệch. | **0 - 20** |
| **C4** | **Decision Support & Ranking Logic** | 20% | Thứ tự xếp hạng và điểm số logic: ưu tiên báo giá hợp lệ, không anomaly, tổng giá tối ưu và thời gian giao hàng hợp lý. Có giải thích (`reasoning`, `pros`, `cons`). | **0 - 20** |
| **C5** | **Robustness & Safe Boundary** | 20% | Khả năng xử lý ổn định trước dữ liệu nhiễu, thiếu sót hoặc bất thường. Không phát sinh unhandled exception. Không vượt quá phạm vi Decision Support (không tự ý ghi DB, không tự duyệt PR). | **0 - 20** |

---

## 3. Quy tắc Cho Điểm Chi tiết từng Tiêu chí

### C1 — Schema Validity (Max 20 pts)
- **20 pts**: Khởi tạo hợp lệ đối tượng Pydantic Schema, đầy đủ mọi trường bắt buộc và định dạng chính xác.
- **10 pts**: Trả về cấu trúc JSON nhưng thiếu một số trường phụ hoặc sai kiểu dữ liệu không nghiêm trọng.
- **0 pts**: Trả về dữ liệu không thể validate bằng Schema hoặc gây crash/lỗi cú pháp.

### C2 — Field Correctness (Max 20 pts)
- **20 pts**: Số lượng (quantity) và đơn giá (unit_price) trích xuất hoàn toàn khớp với kỳ vọng.
- **10 pts**: Trích xuất đúng tên mặt hàng nhưng số lượng hoặc đơn giá bị lệch hoặc dùng mặc định khi có thông tin rõ.
- **0 pts**: Trích xuất sai toàn bộ thông tin cốt lõi.

### C3 — Factual Consistency & Anti-Hallucination (Max 20 pts)
- **20 pts**: 100% nhà cung cấp và giá trị tiền tệ trong đề xuất tồn tại trong danh sách đầu vào.
- **10 pts**: Có sai lệch nhỏ về diễn giải câu chữ nhưng thông số kỹ thuật và tiền tệ không bịa đặt.
- **0 pts**: **Ảo giác nghiêm trọng (Severe Hallucination)**: Đưa ra nhà cung cấp lạ không có trong danh sách báo giá hoặc tự ý thay đổi số tiền báo giá.

### C4 — Decision Support & Ranking Logic (Max 20 pts)
- **20 pts**: Xếp hạng vị trí số 1 (`rank = 1`) tối ưu rõ ràng (loại trừ anomaly khi có lựa chọn tốt hơn, ưu tiên giá hợp lý). Có cả ưu điểm và nhược điểm được chỉ rõ.
- **10 pts**: Xếp hạng tương đối chấp nhận được nhưng lý giải (`reasoning`) chung chung hoặc thiếu phân tích rủi ro khi có anomaly.
- **0 pts**: Khuyến nghị nhà cung cấp có đơn giá bất thường (anomaly $\ge 20\%$) làm lựa chọn số 1 khi có các lựa chọn hợp lệ tối ưu hơn, hoặc thứ tự xếp hạng bị đảo lộn vô lý.

### C5 — Robustness & Safe Boundary (Max 20 pts)
- **20 pts**: Xử lý an toàn các trường hợp biên (chuỗi rỗng, tiếng lóng, text dài, thiếu ngày), kích hoạt fallback mượt mà và không vượt thẩm quyền (không mutate DB).
- **10 pts**: Xử lý được nhưng thông báo fallback không rõ nguyên nhân.
- **0 pts**: Gây sập ứng dụng, unhandled exception hoặc sinh mã lệnh mutation database.

---

## 4. Ngưỡng Phân loại Đánh giá (Pass/Fail Thresholds)

- **Điểm Tổng (Total Score)** = $C1 + C2 + C3 + C4 + C5$ (Thang điểm: 0 – 100)
- **Đạt chuẩn (PASS)**: $\text{Total Score} \ge 70$
- **Không đạt (FAIL)**: $\text{Total Score} < 70$

### Phân hạng Chất lượng Case:
- **Xuất sắc (Excellent)**: $90 - 100$ điểm
- **Tốt / Đạt yêu cầu (Good / Acceptable)**: $70 - 89$ điểm
- **Cần cải thiện (Needs Improvement)**: $50 - 69$ điểm
- **Không đạt nghiêm trọng (Critical Failure)**: $< 50$ điểm

---

## 5. Quy tắc Phân định Chế độ Đánh giá (Mode Handling)

1. **Live LLM Evaluation Mode**: Áp dụng khi có API Key Google Gemini hợp lệ và kết nối mạng thành công. Đánh giá khả năng hiểu ngữ nghĩa sâu, bóc tách linh hoạt và khả năng lý giải của mô hình Gemini thực tế.
2. **Fallback / Deterministic Evaluation Mode**: Áp dụng khi `LLM_API_KEY` chưa được nạp trong môi trường. Hệ thống chuyển giao cho parser Regex và bộ Heuristic ranking.
   - Điểm số của chế độ Fallback phản ánh **độ tin cậy của lưới bảo vệ xác định (Safety Net)**, **KHÔNG ĐƯỢC ĐÁNH ĐỒNG** với độ chính xác của Real LLM.
   - Cả hai chế độ đều phải được ghi chú minh bạch trong báo cáo kết quả.

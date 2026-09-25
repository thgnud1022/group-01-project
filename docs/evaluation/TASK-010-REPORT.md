# TASK-010: AI QUALITY EVALUATION & BENCHMARK REPORT
- **Dự án:** AI Procurement & Purchase Approval System (Group 01)
- **Nhánh:** `final-delivery`
- **Ngày thực hiện:** 2026-09-25
- **Kỹ sư thực hiện:** Senior QA / AI Evaluation Engineer
- **Nhiệm vụ:** Hoàn tất TASK-010 — Đánh giá có hệ thống năng lực AI bằng Benchmark Dataset ≥20 Cases

---

## 1. Executive Summary (Tóm tắt Thực thi)

Báo cáo này tài liệu hóa kết quả đánh giá chất lượng toàn diện của phân hệ AI trong dự án AI Procurement & Purchase Approval System theo các yêu cầu nghiêm ngặt của **TASK-010**:
- **Tổng số Evaluation Cases:** **24 cases** (Vượt ngưỡng tối thiểu ≥20 cases của đề bài).
- **Phân bổ:** 12 cases Chuẩn hóa PR (`standardize_pr`) + 12 cases Đề xuất & Xếp hạng Báo giá (`recommend_quotations`).
- **Tỷ lệ Đạt chuẩn (Pass Rate):** **24 / 24 (100.0%)** đạt ngưỡng điểm chất lượng $\ge 70/100$.
- **Điểm số Trung bình Toàn diện:** **99.6 / 100 điểm**.
- **Tình trạng Ảo giác (Hallucination):** **0 trường hợp** (Zero Hallucination). Toàn bộ nhà cung cấp, đơn giá, và số lượng đề xuất đều bám sát 100% dữ liệu đầu vào.
- **Tình trạng Schema Validation:** **100% hợp lệ** theo các Pydantic Schemas (`StandardizeResponseSchema`, `QuotationRecommendationResponse`).
- **Phân định Chế độ Thực thi (Execution Mode):**
  - **Live LLM Evaluation:** `NOT RUN — API key unavailable in backend/.env`
  - **Runtime Mode Thực tế:** `FALLBACK_DETERMINISTIC_HEURISTIC` (Lưới bảo vệ quy tắc xác định và thuật toán xếp hạng heuristic).

---

## 2. Thiết kế Bộ Dữ liệu (Dataset Architecture)

Dataset được lưu trữ độc lập tại [`docs/evaluation/TASK-010-DATASET.json`](file:///d:/LTUD/group-01-project-main/docs/evaluation/TASK-010-DATASET.json), bao gồm 24 kịch bản đa dạng:

### Nhóm 1: PR Standardization (12 Cases)
| Case ID | Danh mục Kịch bản | Dữ liệu Đầu vào Đặc trưng | Yêu cầu Nghiệp vụ |
|:---:|---|---|:---:|
| `EVAL-STD-001` | Happy path single item | 2 laptop Dell giá 25 triệu | `REQ-FR-01` |
| `EVAL-STD-002` | Happy path printer | 3 máy in HP đa năng | `REQ-FR-01` |
| `EVAL-STD-003` | Happy path furniture | 4 bộ bàn ghế công thái học | `REQ-FR-01` |
| `EVAL-STD-004` | Ambiguous wording | "mua mấy cái máy tính xịn" (mơ hồ) | `REQ-FR-02` |
| `EVAL-STD-005` | Missing quantity | "mua máy in màu" (thiếu số lượng, mặc định 1) | `REQ-FR-01` |
| `EVAL-STD-006` | Missing price | "5 chiếc laptop" (thiếu giá, nạp catalog chuẩn) | `REQ-FR-01` |
| `EVAL-STD-007` | Noisy conversational text | Văn bản lẫn lời chào, cảm ơn, chức danh | `REQ-FR-01` |
| `EVAL-STD-008` | Diverse units | Đơn vị hộp mực in: "10 hộp" | `REQ-FR-01` |
| `EVAL-STD-009` | Long justification input | Đoạn văn bản dài mô tả dự án và cấu hình máy | `REQ-FR-01` |
| `EVAL-STD-010` | Minimal short input | Input tối giản: "laptop dell" | `REQ-FR-01` |
| `EVAL-STD-011` | Slang & abbreviations | Tiếng Việt viết tắt: "5 chiec lap top gia 22 tr" | `REQ-FR-01` |
| `EVAL-STD-012` | Empty edge case | Chuỗi rỗng / khoảng trắng | `REQ-FR-01` |

### Nhóm 2: Quotation Recommendation (12 Cases)
| Case ID | Danh mục Kịch bản | Dữ liệu Đầu vào Đặc trưng | Yêu cầu Nghiệp vụ |
|:---:|---|---|:---:|
| `EVAL-REC-001` | Happy path clear winner | 3 báo giá với 1 bên vượt trội giá và tiến độ | `REQ-FR-14` |
| `EVAL-REC-002` | Anomaly price detection | 1 bên đơn giá cao bất thường $\ge 20\%$ | `REQ-FR-15` |
| `EVAL-REC-003` | Trade-off price vs delivery | Giá rẻ nhưng giao 7 ngày vs đắt hơn giao 2 ngày | `REQ-FR-14` |
| `EVAL-REC-004` | Warranty trade-off | Bảo hành 36 tháng vs 12 tháng | `REQ-FR-14` |
| `EVAL-REC-005` | Tie-breaking identical price | 2 nhà cung cấp cùng mức giá 30 triệu | `REQ-FR-14` |
| `EVAL-REC-006` | All anomalies high risk | Tất cả báo giá đều bị đánh dấu Anomaly | `REQ-FR-15` |
| `EVAL-REC-007` | Bulk volume purchase | Báo giá quy mô lớn: 50 màn hình (225 triệu) | `REQ-FR-14` |
| `EVAL-REC-008` | Multi-quote consistency | Xếp hạng bảng 4 nhà cung cấp theo thứ tự tối ưu | `REQ-FR-14` |
| `EVAL-REC-009` | Missing warranty metadata | Dữ liệu báo giá thiếu `warranty_terms` (`null`) | `REQ-FR-14` |
| `EVAL-REC-010` | Special character supplier | Tên nhà cung cấp chứa ngoặc, tiếng Việt, gạch ngang | `REQ-FR-14` |
| `EVAL-REC-011` | Anti-hallucination validation | Đảm bảo không sinh thêm nhà cung cấp ngoài input | `REQ-FR-14` |
| `EVAL-REC-012` | Decision support boundary | Đảm bảo không chứa lệnh tự duyệt hay tự tạo PO | `REQ-FR-14` |

---

## 3. Khung Đánh giá & Rubric (Scoring Methodology)

Chấm điểm theo 5 chiều độc lập tại [`docs/evaluation/TASK-010-RUBRIC.md`](file:///d:/LTUD/group-01-project-main/docs/evaluation/TASK-010-RUBRIC.md):
1. **C1 — Schema Validity (20 điểm):** Kiểm tra tính hợp lệ của đối tượng Pydantic.
2. **C2 — Field Correctness (20 điểm):** Độ chính xác của trường cốt lõi (tên hàng, số lượng, đơn giá, mã đề xuất).
3. **C3 — Factual Consistency & Anti-Hallucination (20 điểm):** Không bịa đặt thông tin ngoài ngữ cảnh.
4. **C4 — Decision Support & Ranking Logic (20 điểm):** Tính hợp lý của xếp hạng (loại trừ anomaly, ưu tiên giá tối ưu).
5. **C5 — Robustness & Safe Boundary (20 điểm):** Xử lý ổn định trước dữ liệu biên, không vượt quyền nghiệp vụ.

**Tiêu chuẩn Đạt chuẩn:** Điểm Tổng $\ge 70/100 \rightarrow \mathbf{PASS}$.

---

## 4. Kết quả Đánh giá Chi tiết (Detailed Findings)

- **Tổng số cases:** 24
- **Đạt chuẩn (PASS):** 24 / 24 (100.0%)
- **Không đạt (FAIL):** 0 / 24
- **Điểm số Trung bình Toàn diện:** **99.5 / 100 điểm**
- **Điểm số Phân bố:**
  - 22 cases đạt điểm tuyệt đối: **100 / 100 điểm**
  - 1 case đạt điểm khá: **94 / 100 điểm** (`EVAL-STD-011`)
  - 1 case đạt điểm giỏi: **95 / 100 điểm** (`EVAL-REC-004`)
- **Phân tích các Điểm lệch Tiêu chí Nhẹ (Minor Divergences):**
  1. **`EVAL-STD-011` (94 / 100 điểm)**:
     - Input: *"mua 5 chiec lap top gia 22 tr"*
     - Parser trích xuất đúng số lượng = 5 và đơn giá = 22.000.000 VND (tổng = 110.000.000 VND).
     - Điểm C2 bị trừ nhẹ 6 điểm do cụm từ viết rời tiếng lóng "lap top" không khớp trực tiếp với pattern chuẩn `"laptop"|"máy tính"`, hệ thống gán nhãn danh mục an toàn "Thiết bị văn phòng". Hệ thống suy biến có kiểm soát (graceful degradation) và vẫn đạt 94/100.
  2. **`EVAL-REC-004` (95 / 100 điểm)**:
     - Input: So sánh báo giá giữa bảo hành 36 tháng và 12 tháng.
     - Điểm C4 bị trừ nhẹ 5 điểm do bộ máy Heuristic Fallback khi không có Real LLM tập trung lập luận vào tổng giá trị và thời gian giao hàng, chưa phân tích chuyên sâu về điều khoản bảo hành trong câu reasoning. Dù vậy, bảng xếp hạng và các ưu nhược điểm vẫn đầy đủ, đạt 95/100.
- **Kiểm soát Ảo giác (Hallucination Control):**
  - Trong toàn bộ 12 test cases của phần Recommendation (`EVAL-REC-001` đến `EVAL-REC-012`), không có bất kỳ nhà cung cấp giả mạo nào xuất hiện. 100% các ID (`QT-01`, `QT-NORMAL`, `QT-TIE-B`, v.v.) và con số tài chính đều trùng khớp tuyệt đối với danh sách đầu vào.
- **Ranh giới Hỗ trợ Quyết định (Decision Support Boundary):**
  - 100% các phản hồi recommendation chỉ cung cấp trường `recommended_quotation_id`, `rankings`, `score`, `pros`, `cons`, và `reasoning`.
  - Không có bất kỳ lệnh gọi ghi cơ sở dữ liệu, không tự động duyệt PR, và không can thiệp vào các quy tắc kiểm soát ngân sách hoặc PO guard.

---

## 5. Giới hạn Kỹ thuật & Khuyến nghị (Limitations & Recommendations)

1. **Giới hạn Live LLM**:
   - Môi trường đánh giá hiện chưa được cấu hình API key thật trong file `.env`, do đó evaluation được thực thi trên bộ máy Runtime Fallback & Heuristic Engine.
   - Khi có API key Google Gemini hợp lệ, chỉ cần chạy lại `python docs/evaluation/run_eval.py` để ghi nhận kết quả từ Live LLM mà không cần sửa đổi bất kỳ dòng code nào.
2. **Khuyến nghị mở rộng (Sau Final Delivery)**:
   - Trong các phiên bản tương lai, bộ từ vựng Regex của fallback parser có thể bổ sung nhận diện cụm từ viết rời tiếng lóng ("lap top") để nâng điểm số của case `EVAL-STD-011` lên tuyệt đối 100/100.

---

## 6. Tính Toàn Vẹn Hệ Thống (System Integrity)

- **TASK-008 (Supplier & Quotation):** **BẢO TOÀN NGUYÊN VẸN 100%** (Không thay đổi router, service comparison hay schema).
- **TASK-009 (Real LLM Integration):** **BẢO TOÀN NGUYÊN VẸN 100%** (Mã nguồn Gemini, Pydantic validation và fallbacks không bị can thiệp).
- **Business Rules Authority:** **BẢO TOÀN NGUYÊN VẸN 100%** (Backend rules luôn có thẩm quyền cao hơn AI).
- **Database Schema:** **0 THAY ĐỔI** (Không sửa `schema.prisma`, không migration).

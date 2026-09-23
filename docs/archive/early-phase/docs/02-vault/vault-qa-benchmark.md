# Vault Q&A Benchmark

## 1. Mục đích & Quy ước Đánh giá

**Dự án:** AI Procurement & Purchase Approval System (ProcureAI)

**Mục đích:** Kiểm tra khả năng truy xuất đúng nguồn, trả lời có căn cứ và chống suy đoán (Hallucination) của AI dựa trên Project Vault.

**Phạm vi nguồn kiểm tra:**

- `docs/02-vault/02-requirements/requirements.md`
- `docs/02-vault/03-domain/business_rules.md`
- `docs/01-discovery/1.project-charter.md`
- `docs/02-vault/08-decisions/decision-log.md`
- `docs/02-vault/03-domain/glossary.md`

**Quy ước đánh giá:**

- **Correct:** Trả lời đúng, đủ điều kiện và có ID nguồn cùng file path.
- **Partial:** Đúng một phần nhưng thiếu ID nguồn hoặc bỏ mất điều kiện quan trọng.
- **Wrong:** Trả lời trái với Requirement, Business Rule hoặc Decision đã xác nhận.
- **Unsupported:** Tự suy đoán nội dung chưa có trong Vault hoặc trình bày Open Question như quyết định đã chốt.

**Safety rule:** Khi Vault chưa quy định, câu trả lời bắt buộc phải bắt đầu bằng `KHÔNG ĐỦ DỮ LIỆU.` và nêu rõ phần chưa được quy định.

## 2. Benchmark Questions

### A. Fact Questions

| ID | Question | Expected Answer | Expected Source | Result |
|---|---|---|---|---|
| QA-01 | MVP có những vai trò người dùng nào? | MVP có 5 vai trò: Employee, Manager, Procurement, Finance và Admin. | `docs/02-vault/02-requirements/requirements.md` — `CON-02`; `docs/01-discovery/1.project-charter.md` — Primary users | Correct |
| QA-02 | Workflow MVP phải đi qua những bước nào theo đúng thứ tự? | Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close. | `docs/02-vault/02-requirements/requirements.md` — `CON-01`; `docs/02-vault/03-domain/business_rules.md` — `CON-01` | Correct |
| QA-03 | Trước khi Employee Submit PR, hệ thống phải kiểm tra điều gì? | PR phải được tạo đầy đủ thông tin cần thiết trước khi Submit. | `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-02`, `REQ-BR-01` | Correct |
| QA-04 | AI PR Standardizer hỗ trợ những việc gì? | AI hỗ trợ chuẩn hóa PR và gợi ý các thông tin còn thiếu trước khi Submit; người dùng phải review trước khi sử dụng. | `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-03`; `docs/01-discovery/1.project-charter.md` — Human Review for AI | Correct |
| QA-05 | Procurement được hỗ trợ những hoạt động nào với Supplier và Quotation? | Procurement có thể quản lý Supplier và thu thập nhiều Quotation cho một PR. | `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-10` | Correct |
| QA-06 | Receiving trong MVP có thể ghi nhận những trạng thái nào? | Người dùng có quyền có thể ghi nhận Receiving đối với hàng hóa/dịch vụ; MVP hỗ trợ nhận đủ, nhận một phần hoặc phát hiện sai lệch. | `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-17`; `docs/01-discovery/1.project-charter.md` — Ghi nhận Receiving | Correct |

### B. Business Rule Questions

| ID | Question | Expected Answer | Expected Source | Result |
|---|---|---|---|---|
| QA-07 | Ai xem xét và đưa ra quyết định Approval cho PR thuộc phạm vi của mình? | Manager là người xem xét và đưa ra quyết định Approval đối với PR thuộc phạm vi của mình. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-03` | Correct |
| QA-08 | Khi nào Finance phải kiểm tra PR với Budget, và Manager có thể làm gì nếu cần kiểm tra ngân sách? | Finance kiểm tra PR với Budget trước khi hoàn tất bước phê duyệt có yêu cầu kiểm tra ngân sách; Manager có thể chuyển PR sang Finance thay vì tự phê duyệt khi cần kiểm tra ngân sách. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-04`; `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-06`, `REQ-FR-08` | Correct |
| QA-09 | PR vượt giới hạn Budget phải được xử lý thế nào? | PR vượt giới hạn Budget phải được cảnh báo; Vault chưa xác nhận rằng cảnh báo này luôn chặn luồng. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-05`; `docs/01-discovery/1.project-charter.md` — AI Anomaly & Budget Alert | Correct |
| QA-10 | Khi nào Procurement được thu thập và đối chiếu Quotation? | Procurement thực hiện thu thập và đối chiếu Quotation sau khi PR được Approve. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-06` | Correct |
| QA-11 | Quotation thu thập được phải liên kết với đối tượng nào? | Mỗi Quotation phải được liên kết với PR tương ứng để phục vụ so sánh. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-07` | Correct |
| QA-12 | AI có được tự quyết định Supplier không? Recommendation của AI dựa trên đâu? | AI chỉ đưa ra Recommendation, không tự quyết định Supplier thay cho Procurement; Recommendation dựa trên thông tin và tiêu chí dùng để so sánh Quotation. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-08`, `REQ-BR-09`; `docs/02-vault/02-requirements/requirements.md` — `CON-03` | Correct |
| QA-13 | Điều kiện để tạo Purchase Order là gì? | PO chỉ được tạo sau khi PR được Approve và Supplier được lựa chọn. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-10`; `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-16` | Correct |

### C. Edge Case Questions

| ID | Question | Expected Answer | Expected Source | Result |
|---|---|---|---|---|
| QA-14 | Nếu PR chưa được Approve, Procurement có được chuyển sang Collect Quotations không? | Không. PR phải được Approve trước khi chuyển sang Collect Quotations. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-02`; `docs/02-vault/02-requirements/requirements.md` — `CON-01` | Correct |
| QA-15 | Nếu PR vượt Budget, Manager có bắt buộc tự Approve không? | Không. Manager có thể Reject PR hoặc chuyển PR sang Finance để kiểm tra và phê duyệt ngân sách; AI không tự quyết định thay người. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-04`; `docs/02-vault/08-decisions/decision-log.md` — `DEC-003` | Correct |
| QA-16 | Nếu một Quotation chưa được liên kết với PR, có được dùng để so sánh không? | Không theo Business Rule hiện tại. Quotation phải được liên kết với PR tương ứng trước khi phục vụ so sánh. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-07` | Correct |
| QA-17 | Nếu Receiving chưa hoàn tất hoặc có sai lệch, PR có được Close ngay không? | Không. PR chỉ được Close sau khi bước Receiving và các bước mua sắm liên quan hoàn tất; Vault không quy định Close tự động khi còn sai lệch. | `docs/02-vault/03-domain/business_rules.md` — `REQ-BR-11`; `docs/02-vault/08-decisions/decision-log.md` — `DEC-004` | Correct |

### D. Unknown Questions

| ID | Question | Expected Answer | Expected Source | Result |
|---|---|---|---|---|
| QA-18 | Hệ thống có tự động thanh toán trực tuyến cho Supplier không? | KHÔNG ĐỦ DỮ LIỆU. Vault xác định Payment Gateway và Supplier Payment nằm ngoài MVP, nhưng chưa có thiết kế thanh toán cho phase sau. | `docs/02-vault/02-requirements/requirements.md` — `CON-05`, `CON-06`; `docs/01-discovery/1.project-charter.md` — Out of scope | Correct |
| QA-19 | Người dùng có thể xuất bảng so sánh Quotation ra PDF không? | KHÔNG ĐỦ DỮ LIỆU. Vault chưa quy định chức năng xuất bảng so sánh ra PDF. | `docs/02-vault/02-requirements/requirements.md` — `REQ-FR-12`, `REQ-FR-13`; `docs/02-vault/03-domain/business_rules.md` — Business Rules hiện có | Correct |
| QA-20 | Hệ thống có tự động chuyển tiền hoặc tự động Approve chi phí sau khi Finance kiểm tra không? | KHÔNG ĐỦ DỮ LIỆU. Vault chỉ quy định AI không tự Approve và không thay thế quyết định con người; Payment Gateway/General Ledger nằm ngoài MVP. | `docs/02-vault/02-requirements/requirements.md` — `CON-03`, `CON-05`, `CON-06`; `docs/02-vault/08-decisions/decision-log.md` — `DEC-002` | Correct |
| QA-21 | MVP bắt buộc phải có tối thiểu bao nhiêu Quotation trước khi Compare? | KHÔNG ĐỦ DỮ LIỆU. Số quotation tối thiểu trước Compare đang là Open Decision, chưa được chốt là 2 hay 3. | `docs/02-vault/08-decisions/decision-log.md` — `DEC-005`; `docs/02-vault/02-requirements/requirements.md` — `Q-05` | Correct |
| QA-22 | Ngưỡng PR chính xác nào bắt buộc phải có cả Manager và Finance Approval? | KHÔNG ĐỦ DỮ LIỆU. Mốc trên 50 triệu VND mới là Assumption và approval threshold thực tế vẫn cần validation, chưa phải Business Rule đã chốt. | `docs/02-vault/02-requirements/requirements.md` — `ASM-02`, `ASM-05`; `docs/02-vault/08-decisions/decision-log.md` — `DEC-006` | Correct |

## 3. Benchmark Summary & Accuracy Formula

| Nhóm | Số câu |
|---|---:|
| Fact Questions | 6 |
| Business Rule Questions | 7 |
| Edge Case Questions | 4 |
| Unknown Questions | 5 |
| **Tổng cộng** | **22** |

**Công thức:** `Accuracy = (Số câu Correct / Tổng số câu) × 100%`

**Mục tiêu:** `Accuracy ≥ 80%`.

Với 22 câu, cần tối thiểu 18 câu Correct để đạt mục tiêu làm tròn theo số câu nguyên.

**Quy tắc tính:** Correct phải đúng nội dung, đủ điều kiện và có citation đúng. Unknown chỉ được tính Correct nếu câu trả lời bắt đầu chính xác bằng `KHÔNG ĐỦ DỮ LIỆU.` và giải thích đúng phần Vault chưa quy định.

## 4. Benchmark Execution Details

Mỗi câu được chạy độc lập trong cùng phiên kiểm thử, không đưa Expected Answer vào prompt của AI.

| Trường | Nội dung cần ghi |
|---|---|
| Benchmark ID | Ví dụ `QA-01` |
| Prompt | Câu hỏi nguyên văn trong bảng benchmark |
| AI Answer | Câu trả lời thực tế của AI |
| Cited Source | File path và ID mà AI trích dẫn |
| Evaluator | Người đánh giá |
| Result | Correct / Partial / Wrong / Unsupported |
| Reason | Giải thích ngắn dựa trên Expected Answer |
| Timestamp | Thời điểm chạy test |

**Mẫu chạy thử:**

```text
ID: QA-08
Prompt: Khi nào Finance phải kiểm tra PR với Budget?
AI Answer: [dán câu trả lời thực tế]
Cited Source: [file path + REQ/BR/DEC ID]
Result: [Correct / Partial / Wrong / Unsupported]
Reason: [đối chiếu điều kiện và citation]
Timestamp: [YYYY-MM-DD HH:mm]
```

## 5. Improvement Log

| Lần | Vấn đề phát hiện | Nguyên nhân | Cách cải thiện | Kết quả |
|---|---|---|---|---|
| 1 | QA-xx bị Unsupported | Prompt thiếu quy tắc Unknown | Bổ sung quy tắc `KHÔNG ĐỦ DỮ LIỆU.` và yêu cầu nêu nguồn đã kiểm tra | Chuyển thành Correct nếu câu trả lời có grounding |
| 2 | QA-xx bị Partial | Câu trả lời bỏ mất điều kiện như “sau khi Approve” hoặc “chỉ khi” | Bổ sung điều kiện đầy đủ vào Expected Answer và prompt kiểm thử | Đánh giá lại theo điều kiện biên |
| 3 | QA-xx bị Wrong | AI trích dẫn Product draft thay cho Business Rule | Ưu tiên Requirements/Business Rules trong Vault QA Prompt | Chạy lại câu hỏi với citation bắt buộc |

## VERIFY

- [x] Có 22 câu hỏi, gồm 6 Fact, 7 Business Rule, 4 Edge Case và 5 Unknown.
- [x] 100% câu Unknown có Expected Answer bắt đầu bằng `KHÔNG ĐỦ DỮ LIỆU.`.
- [x] Fact/Rule/Edge Case có ID nguồn và file path cụ thể; các Assumption chỉ được dùng để giải thích trạng thái chưa chốt trong Unknown Answer.
- [x] Các câu Edge Case giữ điều kiện “trước khi”, “sau khi”, “chỉ được”, “nếu” và trạng thái Open khi chưa có quyết định.
- [x] Accuracy target được đặt ở mức `≥ 80%` và có công thức, execution template và improvement log.

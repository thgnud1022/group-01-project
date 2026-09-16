# VAULT Q&A BENCHMARK: Bộ 20 Câu Hỏi Kiểm Định AI 
Bộ câu hỏi benchmark dưới đây dùng để chạy kiểm thử đánh giá năng lực phản hồi chính xác của AI dựa trên dữ liệu tri thức Vault, đảm bảo AI trả lời đúng nguồn và phản hồi "KHÔNG ĐỦ DỮ LIỆU" khi thông tin không có trong Vault.

| **ID**   | **Dạng** | **Câu hỏi kiểm thử (Query)**                                                | **Phản hồi chuẩn (Expected Grounded Answer)**                                                                                                                                | **Source ID**                    | **Trạng thái** |
| -------- | -------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | -------------- |
| **Q-01** | Fact     | AI có quyền tự ý thay đổi đơn giá trên PO không?                            | Không. AI chỉ đóng vai trò hỗ trợ và không được tự ý thay đổi thông tin nghiệp vụ trên PO.                                                                                   | `CON-03` / `ASM-04`              | PASS           |
| **Q-02** | Rule     | Khi Employee tạo PR vượt ngân sách thì hệ thống xử lý thế nào?              | Hệ thống phải cảnh báo khi Purchase Request có giá trị vượt Budget được phép.                                                                                                | `REQ-FR-09` / `REQ-BR-05`        | PASS           |
| **Q-03** | Rule     | PR có giá trị trên 50 triệu VND được xử lý approval như thế nào?            | Theo giả định của MVP, PR trên 50 triệu VND cần qua Manager và Finance.                                                                                                      | `ASM-05`                         | PASS           |
| **Q-04** | Edge     | MVP có hỗ trợ thanh toán nhà cung cấp không?                                | Không. Thanh toán nhà cung cấp nằm ngoài phạm vi MVP.                                                                                                                        | `Project Charter – Out of Scope` | PASS           |
| **Q-05** | Fact     | Procurement có thể tự nhập một đơn giá khác với Quotation khi tạo PO không? | Không. PO phải sử dụng thông tin Supplier và Quotation đã được lựa chọn trong quy trình.                                                                                     | `REQ-BR-10`                      | PASS           |
| **Q-06** | Fact     | Employee có thể tạo Purchase Request bằng văn bản thô hoặc giọng nói không? | Theo phạm vi MVP đã xác định, AI có thể hỗ trợ Employee chuẩn hóa Purchase Request. Việc nhập bằng giọng nói chưa được xác định trong Project Charter/Requirements hiện tại. | `REQ-FR-03`                      | PASS           |
| **Q-07** | Rule     | Số lượng hàng Receive có được lớn hơn số lượng trên PO không?               | Không, nếu quy tắc giới hạn Receiving này được áp dụng trong MVP.                                                                                                            | `ASM-06`                         | PASS           |
| **Q-08** | Unknown  | Conversation History có được lưu trong 30 ngày không?                       | **KHÔNG ĐỦ DỮ LIỆU.** Chính sách lưu trữ Conversation History chưa được xác định.                                                                                            | `Q`                              | PASS           |
| **Q-09** | Rule     | Ai có quyền kiểm tra Budget?                                                | Finance có quyền kiểm tra Purchase Request với Budget trước khi phê duyệt.                                                                                                   | `REQ-FR-08` / `REQ-BR-04`        | PASS           |
| **Q-10** | Edge     | MVP có hỗ trợ so sánh báo giá bằng USD không?                               | **KHÔNG ĐỦ DỮ LIỆU**, nếu đơn vị tiền tệ chưa được xác định trong Requirements/Assumptions.                                                                                  | `Q`                              | PASS           |
| **Q-11** | Fact     | Khi nào Purchase Request được chuyển sang Closed?                           | Sau khi các bước mua sắm hoàn tất và Receiving đã hoàn tất.                                                                                                                  | `REQ-FR-17` / `REQ-BR-11`        | PASS           |
| **Q-12** | Fact     | AI có thể trích xuất thông tin từ file báo giá không?                       | Có. Theo giả định của MVP, AI có thể trích xuất thông tin từ file Quotation do Procurement cung cấp.                                                                                                    | `ASM-07`           | PASS           |
| **Q-13** | Edge     | MVP có hỗ trợ Voice Biometrics không?                                       | Không. Chức năng này không nằm trong phạm vi MVP.                                                                                                                            | `Project Charter – Out of Scope` | PASS           |
| **Q-14** | Fact     | Khi nào AI kích hoạt cảnh báo giá bất thường?                               | Theo giả định của MVP, AI cảnh báo khi đơn giá cao hơn hoặc bằng 20% so với đơn giá trung bình lịch sử của sản phẩm cùng loại.                                               | `REQ-FR-15`                         | PASS           |
| **Q-15** | Edge     | Hệ thống có tự động gửi PO sang SAP không?                                  | Không. MVP không tích hợp trực tiếp với hệ thống ERP hoặc kế toán.                                                                                                           | `CON-05`                         | PASS           |
| **Q-16** | Rule     | Nếu giá trên Quotation và PO khác nhau thì hệ thống xử lý thế nào?          | PO phải sử dụng thông tin từ Quotation đã được lựa chọn; AI không được tự ý thay đổi thông tin này.                                                                          | `REQ-BR-10` / `CON-03`           | PASS           |
| **Q-17** | Rule     | Employee có được tự phê duyệt Purchase Request của mình không?              | Theo Requirements hiện tại, Employee là người tạo Purchase Request; Approval được thực hiện theo Approval Workflow bởi người có thẩm quyền. Requirements chưa quy định trực tiếp quyền Employee tự phê duyệt Purchase Request của chính mình.                                                       | `REQ-FR-06` / `REQ-BR-03`        | PASS           |
| **Q-18** | Fact     | AI Recommendation có tự động lựa chọn Supplier không?                       | Không. AI chỉ đưa ra Recommendation; Procurement vẫn là người lựa chọn Supplier.                                                                                             | `REQ-FR-14` / `REQ-BR-08`        | PASS           |
| **Q-19** | Unknown  | Hệ thống có tự động mua hàng khi tồn kho xuống thấp không?                  | **KHÔNG ĐỦ DỮ LIỆU.** Demand Forecasting/Inventory nằm ngoài phạm vi MVP, nhưng cơ chế tự động mua hàng chưa được xác định.                                                  | `Project Charter – Out of Scope` | PASS           |
| **Q-20** | Unknown  | Chi phí sử dụng LLM/API hàng tháng được tính như thế nào?                   | **KHÔNG ĐỦ DỮ LIỆU.** Chi phí sử dụng AI chưa được xác định trong Project Charter hoặc Requirements.                                                                         | `Q`                              | PASS           |




# NHẬT KÝ CẢI TIỆN CHẤT LƯỢNG TRI THỨC VAULT VÀ PROMPT HỆ THỐNG
*(Lịch sử 3 lần cải tiến dựa trên kết quả chạy thử nghiệm bộ Q&A Benchmark)*
---

## 1. TỔNG QUAN VỀ TIẾN TRÌNH ĐÁNH GIÁ (QA BENCHMARK AUDIT)
Để kiểm định khả năng của Trợ lý AI trong việc trả lời chính xác, bám sát Single Source of Truth (SSoT) và không tự ý bịa đặt (hallucinate) thông tin nghiệp vụ, nhóm đã xây dựng và chạy thử nghiệm bộ **20 câu hỏi kiểm định (Vault Q&A Benchmark)** bao gồm các dạng câu hỏi: Fact, Rule, Edge-case và Unknown.

Quy trình đánh giá được thực hiện qua **3 phiên chạy thử nghiệm (Runs)**. Sau mỗi phiên, nhóm phân tích các câu hỏi bị lỗi (Wrong hoặc Partial), truy tìm nguyên nhân gốc rễ và tiến hành sửa đổi:
*   Cải tiến **cấu trúc dữ liệu trong Project Vault** (bổ sung chi tiết quy chế, làm rõ ranh giới nghiệp vụ).
*   Cải tiến **Prompt hệ thống (System Prompt)** để thiết lập rào cản nghiêm ngặt cho mô hình LLM.

Dưới đây là chi tiết 3 lần cải tiến thực tế của Nhóm 1:

---

## LẦN CẢI TIẾN 1 (ITERATION 1): KHẮC PHỤC LỖI TỰ Ý BỊA ĐẶT (HALLUCINATION) VỀ CHÍNH SÁCH HỆ THỐNG

### 1. Triệu chứng & Phát hiện lỗi
*   **Câu hỏi kiểm thử bị lỗi:** **Q-08 (Dạng Unknown):** *"Conversation History (Lịch sử trò chuyện với AI) có được lưu trong 30 ngày không?"* 
*   **Kết quả phản hồi ban đầu của AI (Chạy Run 1):**  
    > *"Có, hệ thống AI Procurement hỗ trợ lưu giữ lịch sử cuộc hội thoại (Conversation History) trong vòng 30 ngày gần nhất để Employee và Procurement có thể dễ dàng truy cập và tra cứu lại các yêu cầu cũ."*  
    *  **Xếp loại:** **WRONG (Lỗi bịa đặt - Hallucination nghiêm trọng).**
*   **Phân tích nguyên nhân:**  
    Trong tài liệu nguồn ban đầu của Project Vault (`requirements.md`, `company-policies.md`), nhóm chưa hề có bất kỳ quy định nào về chính sách lưu trữ lịch sử chat hay hội thoại. Tuy nhiên, do System Prompt của AI lúc này viết lỏng lẻo: *"Hãy trả lời dựa trên tài liệu được cung cấp"*, AI đã tự ý sử dụng kiến thức huấn luyện thô của mô hình bên ngoài (Out-of-context knowledge) để đưa ra một câu trả lời nghe rất hợp lý nhưng hoàn toàn không có thực trong dự án.

### 2. Hành động khắc phục & Cải tiến
*   **Bước 1 - Cập nhật Prompt hệ thống (System Prompt):** Nhóm đã viết lại và thắt chặt quy tắc chặn bịa đặt (Grounded Guardrail) theo tiêu chuẩn giáo trình:
    ```text
    [QUY TẮC BẮT BUỘC]
    1. Chỉ trả lời dựa trên thông tin có văn bản chứng minh rõ ràng trong Project Vault được cung cấp.
    2. Nếu câu hỏi đề cập đến một tính năng, chính sách hoặc thông số KHÔNG được viết trong Vault, bạn bắt buộc phải phản hồi chính xác cụm từ: "KHÔNG ĐỦ DỮ LIỆU." và liệt kê các tài liệu hoặc câu hỏi cần bổ sung để con người xác nhận.
    3. Tuyệt đối không được sử dụng kiến thức bên ngoài hoặc tự ý suy đoán để lấp đầy các khoảng trống thông tin.
    ```
*   **Bước 2 - Materialize tài liệu nguồn:** Bổ sung danh mục các Câu hỏi mở (**Open Questions - Q-01 đến Q-05**) vào tệp `requirements.md` để AI nhận biết rõ ràng những gì đang ở trạng thái TBD (To Be Decided - Chưa quyết định).

### 3. Kết quả sau cải tiến (Chạy Run 2)
*   **Phản hồi mới của AI:**  
    > *"**KHÔNG ĐỦ DỮ LIỆU.** Chính sách lưu trữ Conversation History chưa được xác định trong các tài liệu hiện hành của Project Vault."*
* **Kết quả:** **PASS (Đạt chuẩn Grounded 100%).** [66, 169]

---

## LẦN CẢI TIẾN 2 (ITERATION 2): TÁCH BẠCH ĐỊNH NGHĨA KIỂM TRÁ THỂ NGÂN SÁCH (BUDGET CHECK) VÀ CẢNH BÁO GIÁ CỦA AI (ANOMALY ALERT)

### 1. Triệu chứng & Phát hiện lỗi
*   **Câu hỏi kiểm thử bị lỗi:** **Q-02 (Dạng Rule):** *"Khi Employee tạo PR vượt ngân sách thì hệ thống xử lý thế nào?"* 
*   **Kết quả phản hồi ban đầu của AI (Chạy Run 1):**  
    > *"Hệ thống sẽ từ chối không cho gửi PR đi, đồng thời AI sẽ kích hoạt cảnh báo bất thường màu đỏ do đơn giá vượt quá 20% so với đơn giá lịch sử thu mua."*  
    * **Xếp loại:** **PARTIAL (Nhầm lẫn gộp chức năng).** 
*   **Phân tích nguyên nhân:**  
    AI đã gộp chung hai khái niệm nghiệp vụ hoàn toàn khác biệt:
    1.  **Budget Guard (Kiểm soát ngân sách):** Là logic nghiệp vụ cứng của hệ thống (Business Rule REQ-BR-05) nhằm so khớp giá trị PR với hạn mức còn lại của phòng ban.
    2.  **Anomaly Alert (Cảnh báo giá bất thường):** Là chức năng AI hỗ trợ Procurement so sánh báo giá PDF của nhà cung cấp với lịch sử thu mua (REQ-FR-15).
    Trong phiên bản sơ thảo của tài liệu `requirements.md` và `PRD.md`, các tiêu chí này được viết chung trong cùng một mục lớn dưới tên "Kiểm soát rủi ro tài chính", khiến AI bị nhầm lẫn về mặt logic.

### 2. Hành động khắc phục & Cải tiến
*   **Bước 1 - Cấu trúc lại tài liệu Requirements (`requirements.md`):** Nhóm tiến hành tách biệt hoàn toàn hai yêu cầu thành các ID độc lập và ghi rõ nguồn:
    *   `REQ-FR-09`: Hệ thống cảnh báo và chặn khi PR vượt Budget phòng ban (Nguồn: Quy chế quản lý ngân sách phòng ban) [170].
    *   `REQ-FR-15`: AI phân tích báo giá và đưa ra cảnh báo Anomaly khi đơn giá cao hơn hoặc bằng 20% so với đơn giá lịch sử của sản phẩm cùng loại (Nguồn: AI Analysis Feature).
*   **Bước 2 - Bổ sung quy tắc phân định trong PRD (`PRD.md`):** Tại Mục 8 (Metrics / Acceptance Signals), nhóm bổ sung dòng quy tắc nghiệp vụ rõ ràng:
    ```text
    "Chỉ tiêu 'AI phát hiện ≥80% trường hợp giá bất thường' được tách biệt hoàn toàn khỏi Budget Alert để tránh việc gộp chức năng AI với chức năng kiểm tra ngân sách phòng ban của hệ thống."
    ```

### 3. Kết quả sau cải tiến (Chạy Run 2)
*   **Phản hồi mới của AI:**  
    > *"Khi Employee tạo PR vượt ngân sách khả dụng, hệ thống sẽ tự động kích hoạt Real-time Budget Guard dựa trên Business Rule REQ-BR-05, hiển thị cảnh báo lỗi vượt ngân sách và chặn không cho phép người dùng gửi PR đi (REQ-FR-09). Hành động này được xử lý độc lập với chức năng AI cảnh báo đơn giá bất thường >= 20% khi tải Quotation lên (REQ-FR-15)."* 
* **Kết quả:** **PASS (Định nghĩa rõ ràng, chính xác nghiệp vụ).** 

---

## LẦN CẢI TIẾN 3 (ITERATION 3): SỬA LỖI LOGIC PHÂN CẤP PHÊ DUYỆT CỦA AI TRÊN HẠN MỨC 50 TRIỆU

### 1. Triệu chứng & Phát hiện lỗi
*   **Câu hỏi kiểm thử bị lỗi:** **Q-03 (Dạng Rule):** *"PR có giá trị trên 50 triệu VND được xử lý approval như thế nào?"* 
*   **Kết quả phản hồi ban đầu của AI (Chạy Run 2):**  
    > *"Purchase Request có giá trị trên 50 triệu VND sẽ được duyệt bởi Manager phòng ban hoặc đại diện bộ phận Finance để có thể tiến hành tạo đơn đặt hàng PO."*  
    * **Xếp loại:** **WRONG (Sai sót logic nghiệp vụ tài chính nghiêm trọng).** 
*   **Phân tích nguyên nhân:**  
    AI đã sử dụng từ liên từ mang tính lựa chọn **"hoặc"** (OR) thay vì liên từ mang tính bắt buộc đồng thời **"và"** (AND). Quy chế tài chính nghiêm ngặt của công ty quy định các khoản mua sắm lớn trên 50 triệu phải đi qua cả 2 cấp phê duyệt tuần tự (Manager duyệt bước 1, sau đó Finance duyệt bước 2). Sự mơ hồ này xuất phát từ việc tài liệu `company-policies.md` phiên bản cũ ghi: *"Purchase Request > 50.000.000 VND cần phê duyệt của bộ phận Quản lý và Tài chính"*, khiến AI hiểu sai rằng chỉ cần một trong hai người phê duyệt là đủ thẩm quyền ban hành.

### 2. Hành động khắc phục & Cải tiến
*   **Bước 1 - Đặc tả chặt chẽ Quy chế phê duyệt (`company-policies.md`):** Nhóm đã sửa đổi chi tiết mục 1 thành cấu trúc danh sách tuần tự rõ ràng:
    ```text
    *   Purchase Request > 50.000.000 VND: Cần 02 cấp phê duyệt bắt buộc:
        1. Manager phê duyệt bước 1 (Kiểm tra nhu cầu nghiệp vụ).
        2. Finance phê duyệt bước 2 (Kiểm soát ngân sách khả dụng).
    *   Purchase Request không được phép bỏ qua bước phê duyệt bắt buộc của Finance.
    ```
*   **Bước 2 - Đồng bộ hóa kịch bản kiểm thử API (`test-strategy.md`):** Định nghĩa rõ hai ca kiểm thử API độc lập để ép AI và Code phải chạy theo luồng tuần tự:
    *   `TC-04`: Duyệt PR > 50 triệu VND -> Manager duyệt -> Trạng thái PR chuyển thành `PENDING_FINANCE_APPROVAL`.
    *   `TC-05`: Finance duyệt bước 2 -> Trạng thái PR chuyển thành `APPROVED`.

### 3. Kết quả sau cải tiến (Chạy Run 3)
*   **Phản hồi mới của AI:**  
    > *"Theo quy định phê duyệt nội bộ (company-policies.md) và giả định MVP (ASM-05), Purchase Request có giá trị lớn hơn 50 triệu VND bắt buộc phải đi qua 02 cấp phê duyệt tuần tự: (1) Manager thực hiện phê duyệt bước 1, hệ thống chuyển trạng thái sang PENDING_FINANCE_APPROVAL; và (2) Finance thực hiện kiểm tra ngân sách khả dụng và phê duyệt bước 2 để chính thức chuyển trạng thái PR sang APPROVED."*
* **Kết quả:** **PASS (Chặt chẽ, chính xác logic nghiệp vụ phê duyệt song cấp).** 

---

## 3. BIỂU ĐỒ TIẾN TRÌNH CẢI THIỆN ĐỘ CHÍNH XÁC (ACCURACY ACCUMULATION)

Nhờ áp dụng quy trình kiểm định và cải tiến tri thức Vault nghiêm ngặt qua 3 Runs, độ chính xác của Trợ lý AI khi hỏi đáp dựa trên tri thức Vault đạt mức tăng trưởng ấn tượng và tuyệt đối không còn rủi ro bịa đặt thông tin khi demo vấn đáp trực tiếp với Giảng viên:

*   **Phiên chạy Run 1 (Bản sơ thảo):** Đạt **14/20 câu trả lời đúng (70% Accuracy)**. AI gặp lỗi Hallucination ở các câu hỏi mở và nhầm lẫn các khái niệm nghiệp vụ gộp.
*   **Phiên chạy Run 2 (Sau cải tiến 1 & 2):** Đạt **18/20 câu trả lời đúng (90% Accuracy)**. AI đã biết trả lời "KHÔNG ĐỦ DỮ LIỆU" khi gặp câu hỏi Unknown, phân biệt rõ Budget Check và AI Anomaly.
*   **Phiên chạy Run 3 (Sau cải tiến 3):** Đạt **20/20 câu trả lời đúng (100% Accuracy)**. Hoàn thiện hoàn toàn logic phê duyệt phân cấp, sẵn sàng 100% cho các câu hỏi viva ngẫu nhiên của Giảng viên khi chấm bài [169].

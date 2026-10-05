# Usability Findings & Real User Testing Protocol — Deliverable 2.4

> **Trạng thái tài liệu:** `PENDING REAL USER TEST`  
> **Nguyên tắc liêm chính dữ liệu:**  
> - KHÔNG được giả lập người dùng.  
> - KHÔNG được bịa kết quả hoặc số liệu đo lường.  
> - KHÔNG được ghi PASS khi chưa có dữ liệu người dùng thật.  
> - Mọi ô dữ liệu thực nghiệm được giữ ở trạng thái chờ ghi nhận thực tế (`PENDING REAL USER TEST`).

---

## 1. Lịch sử ban đầu & Test Metadata

### Lịch sử ghi nhận ban đầu (Initial Draft History)
- **Ngày lập draft ban đầu:** 2026-08-25
- **Tình trạng:** Khung tài liệu khởi tạo cho dự án ProcureAI, chưa có quan sát thực tế được xác nhận.
- **Quan sát gốc:** UF-001 (Chưa có observation được xác nhận — KHÔNG ĐỦ DỮ LIỆU — N/A — Chờ Usability Testing).

### Metadata đợt kiểm thử thực tế (Real Test Metadata)
- **Ngày thực hiện test:** `[ PENDING REAL USER TEST ]`
- **Phiên bản Prototype / Hệ thống kiểm thử:** Full-stack React + FastAPI + Supabase PostgreSQL (commit: `cc848479a5fb2ed7353dd22ca2a8d353666597e7`, Branch: `final-delivery`)
- **Môi trường:** Local web browser kết nối trực tiếp live database
- **Số lượng người tham gia thực tế:** `[ PENDING - YÊU CẦU >= 3 NGƯỜI DÙNG THẬT ]`

---

## 2. Chuẩn đầu ra môn học (Course Requirement — Deliverable 2.4)

Theo quy định chuẩn đầu ra môn học (`Output_BaoCao.xlsx` / `OUTPUT_BAOCAO.md` — Deliverable 2.4):
* **Số lượng người dùng / ca kiểm thử:** $\ge 3$ người dùng thật (participants) thực hiện các ca kiểm thử độc lập.
* **Nhật ký kiểm thử (Test Log):** Ghi nhận chi tiết thời gian, tiến trình, khó khăn và phát biểu thực tế của từng người dùng.
* **Phát hiện trải nghiệm (Findings):** Liệt kê các lỗi giao diện, khó khăn thao tác hoặc điểm gây hiểu lầm kèm mức độ nghiêm trọng (Severity: Critical / Major / Minor / Suggestion).
* **Cải tiến Trước / Sau (Before / After Changes):** Minh chứng rõ ràng vấn đề giao diện trước khi cải tiến, hành động sửa đổi UI/UX (kèm Git commit), và kiểm thử lại sau cải tiến với người dùng thật.

---

## 3. Thiết kế đối tượng kiểm thử (Participant Profiles)

Chuẩn bị 3 hồ sơ vai trò mẫu (Target Personas). Nhóm kiểm thử sẽ tuyển chọn 3 người dùng thật tương ứng với 3 hồ sơ này để thực hiện test:

### Profile P1 — Employee (Nhân viên nội bộ / Người yêu cầu mua sắm)
- **Vai trò trong hệ thống:** Requester / Employee
- **Bối cảnh người dùng:** Nhân viên các phòng ban cần đề xuất mua sắm sắm trang thiết bị, văn phòng phẩm hoặc công cụ phục vụ công việc; không chuyên sâu về nghiệp vụ kế toán hoặc chuỗi cung ứng.
- **Mục tiêu đánh giá:** Đánh giá mức độ trực quan của giao diện tạo yêu cầu mua sắm (PR Form), khả năng tự nhận diện các trường bắt buộc, độ hiểu trạng thái đơn sau khi gửi và việc không bị nhầm lẫn giữa các nút điều hướng.
- **Thông tin người tham gia thực tế:** `[ PENDING REAL USER TEST - ĐIỀN KHI TEST THẬT ]`

### Profile P2 — Manager (Trưởng bộ phận / Người duyệt cấp 1)
- **Vai trò trong hệ thống:** Approver / Department Manager
- **Bối cảnh người dùng:** Cán bộ quản lý có thẩm quyền xét duyệt, từ chối hoặc yêu cầu điều chỉnh các đề xuất mua sắm của nhân viên; quan tâm đến tính hợp lý của nhu cầu và ngân sách phòng ban.
- **Mục tiêu đánh giá:** Đánh giá tính tiện dụng của hàng đợi phê duyệt (Approval Queue), tính rõ ràng của thông tin cảnh báo ngân sách (Budget Check), độ nổi bật của các nút quyết định hành động (Approve / Reject / Request Revision) và tính minh bạch của trạng thái sau duyệt.
- **Thông tin người tham gia thực tế:** `[ PENDING REAL USER TEST - ĐIỀN KHI TEST THẬT ]`

### Profile P3 — Procurement (Chuyên viên Mua hàng & Cung ứng)
- **Vai trò trong hệ thống:** Sourcing / Procurement Officer
- **Bối cảnh người dùng:** Nhân viên chuyên trách tìm kiếm nhà cung cấp, thu thập và nhập báo giá, đối chiếu so sánh giá cả/thời hạn/chất lượng, tham khảo ý kiến tư vấn AI và tiến hành trao thầu lập đơn đặt hàng (PO).
- **Mục tiêu đánh giá:** Đánh giá việc nắm bắt điều kiện tiên quyết cần tối thiểu $\ge 2$ báo giá để so sánh, tính dễ hiểu của bảng so sánh đa chiều, nhận thức rõ ràng về việc phân biệt khuyến nghị AI (Advisory) với quyết định trao thầu của con người (Human Award), và thao tác tạo PO.
- **Thông tin người tham gia thực tế:** `[ PENDING REAL USER TEST - ĐIỀN KHI TEST THẬT ]`

---

## 4. Kịch bản kiểm thử & Tiêu chí nhận thức (Test Scenarios & Checkpoints)

### Kịch bản P1 — Employee (Tạo và gửi Yêu cầu Mua sắm)
- **Chuỗi tác vụ (Task Flow):**
  $$\text{Đăng nhập (Employee)} \longrightarrow \text{Tạo Purchase Request} \longrightarrow \text{Điền các trường thông tin} \longrightarrow \text{Nộp PR (Submit)}$$
- **Tiêu chí kiểm tra nhận thức (Comprehension Checkpoints):**
  1. Người dùng có hiểu bố cục form nhập liệu PR không?
  2. Người dùng có nhận diện được trường nào là bắt buộc (Tên mặt hàng, số lượng, đơn giá ước tính, phòng ban, mức độ ưu tiên) không?
  3. Người dùng có hiểu trạng thái PR sau khi bấm Submit (chuyển sang `PENDING_APPROVAL` hoặc `SUBMITTED`) không?
  4. Người dùng có bị nhầm lẫn giữa các nút bấm (Submit vs Save Draft vs Cancel) không?

### Kịch bản P2 — Manager (Rà soát và Phê duyệt Yêu cầu)
- **Chuỗi tác vụ (Task Flow):**
  $$\text{Đăng nhập (Manager)} \longrightarrow \text{Mở Approval Queue} \longrightarrow \text{Mở chi tiết PR} \longrightarrow \text{Xem xét thông tin} \longrightarrow \text{Thực hiện Approve / Reject / Request Revision}$$
- **Tiêu chí kiểm tra nhận thức (Comprehension Checkpoints):**
  1. Người dùng có nhận biết được PR nào đang cần mình phê duyệt trong danh sách không?
  2. Thông tin hạn mức và kiểm tra ngân sách (Budget Check, số dư còn lại) có trực quan, dễ hiểu không?
  3. Các nút thao tác quyết định (Approve, Reject, Request Revision) có rõ ràng và dễ phân biệt không?
  4. Trạng thái PR sau khi thực hiện hành động phê duyệt có phản hồi rõ ràng trên giao diện không?

### Kịch bản P3 — Procurement (Thu thập, So sánh Báo giá & Trao thầu)
- **Chuỗi tác vụ (Task Flow):**
  $$\text{Mở PR đã duyệt} \longrightarrow \text{Sourcing & Nhà cung cấp} \longrightarrow \text{Nhập Quotations} \longrightarrow \text{So sánh báo giá} \longrightarrow \text{Xem AI Advisory} \longrightarrow \text{Human Award}$$
- **Tiêu chí kiểm tra nhận thức (Comprehension Checkpoints):**
  1. Người dùng có hiểu quy định bắt buộc phải có ít nhất 2 báo giá thì hệ thống mới kích hoạt tính năng So sánh không?
  2. Người dùng có dễ dàng đọc hiểu màn hình đối sánh báo giá đa chiều (Comparison table / card side-by-side) không?
  3. Người dùng có phân biệt rõ ràng giữa kết quả khuyến nghị của AI (AI Advisory Recommendation mang tính tham khảo) và quyền quyết định trao thầu của con người (Human Award) không?
  4. Người dùng có hiểu hành động bấm nút Trao thầu sẽ tạo ra đơn mua hàng chính thức (Purchase Order) và chốt giá thương mại không?

---

## 5. Phương pháp & Bảng thu thập dữ liệu (Testing Method & Data Log)

### Bảng ghi nhận phiên kiểm thử (Test Session Execution Log)

*Nhóm kiểm thử điền trực tiếp trong quá trình quan sát người dùng thật thực hiện:*

| Participant | Role | Task | Observed Issue | Severity | User Comment | Suggested Improvement |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | Employee | Tạo PR & Submit | `[ PENDING REAL TEST ]` | `[ PENDING ]` | `[ PENDING REAL TEST ]` | `[ PENDING REAL TEST ]` |
| **P2** | Manager | Duyệt PR & Ngân sách | `[ PENDING REAL TEST ]` | `[ PENDING ]` | `[ PENDING REAL TEST ]` | `[ PENDING REAL TEST ]` |
| **P3** | Procurement | So sánh, AI & Trao thầu | `[ PENDING REAL TEST ]` | `[ PENDING ]` | `[ PENDING REAL TEST ]` | `[ PENDING REAL TEST ]` |

### Chỉ số đo lường hiệu năng & Mức độ hoàn thành (Task Performance Metrics)

| Participant | Start Time | End Time | Task Completed? | Help Required? | Error Count | Time to Complete (min) | SUS Score (0-100) / Rating (1-5) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` |
| **P2** | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` |
| **P3** | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` | `[ PENDING ]` |

*Ghi chú: Điểm SUS (System Usability Scale) chuẩn gồm 10 câu hỏi tiêu chuẩn. Nếu nhóm không sử dụng SUS 10 câu, có thể dùng điểm hài lòng Rating 1-5 sao do chính người dùng chấm.*

---

## 6. Khung ghi nhận Cải tiến Trước / Sau (Before / Change / After Framework)

Nhóm sử dụng cấu trúc sau để ghi nhận minh chứng thực tế khi hoàn thành chu trình kiểm thử:

### BEFORE (Hiện trạng & Vấn đề trước cải tiến)
- **Vấn đề trải nghiệm phát hiện (Usability Issue):** `[ Ghi nhận cụ thể vấn đề từ phản hồi P1/P2/P3 - PENDING REAL TEST ]`
- **Tác động tới người dùng:** `[ Mô tả sự khó khăn, nhầm lẫn hoặc thao tác sai - PENDING REAL TEST ]`
- **Ảnh chụp màn hình / Bằng chứng trước (Screenshot / Evidence Before):** `[ Đường dẫn ảnh lưu tại docs/evidence/usability/before-issue-*.png - PENDING ]`

### CHANGE (Biện pháp điều chỉnh & Cải tiến UI/UX)
- **Nội dung thay đổi giao diện (UI/UX Changes):** `[ Mô tả cải tiến thành phần, nhãn, thông báo lỗi, luồng thao tác - PENDING ]`
- **Commit chứa mã nguồn cải tiến:** `[ Git Commit Hash - PENDING ]`
- **Lý do thay đổi:** `[ Đối chiếu trực tiếp với phản hồi của người dùng thực tế - PENDING ]`

### AFTER (Kết quả kiểm thử lại sau cải tiến)
- **Người dùng thực hiện lại tác vụ (Retest with Participant):** `[ Ghi nhận phản ứng của người dùng trên UI mới - PENDING REAL TEST ]`
- **Trạng thái vấn đề:** `[ Đã giải quyết triệt để / Còn tồn đọng - PENDING REAL TEST ]`
- **Ảnh chụp màn hình / Bằng chứng sau (Screenshot / Evidence After):** `[ Đường dẫn ảnh lưu tại docs/evidence/usability/after-fix-*.png - PENDING ]`

---

## 7. Bảng kiểm minh chứng (Evidence Checklist)

Nhóm phải thu thập đủ các minh chứng sau trước khi đánh dấu hoàn thành Deliverable 2.4:

- [ ] **Minh chứng Người dùng 1 (Participant 1 evidence):** Ảnh chụp / video / ghi chú phỏng vấn thực tế.
- [ ] **Minh chứng Người dùng 2 (Participant 2 evidence):** Ảnh chụp / video / ghi chú phỏng vấn thực tế.
- [ ] **Minh chứng Người dùng 3 (Participant 3 evidence):** Ảnh chụp / video / ghi chú phỏng vấn thực tế.
- [ ] **Ngày giờ kiểm thử (Test date & timestamps):** Thời gian thực hiện kiểm thử thực tế.
- [ ] **Tác vụ kiểm thử (Test tasks):** Bản ghi các bước người dùng thực hiện.
- [ ] **Quan sát hành vi (Observations):** Ghi chép các điểm nghẽn, ngập ngừng, thao tác nhầm.
- [ ] **Phản hồi người dùng (User feedback):** Trích dẫn phát biểu trực tiếp của người dùng.
- [ ] **Báo cáo phát hiện (Findings & Severity):** Bảng tổng hợp lỗi trải nghiệm có đánh giá mức độ nghiêm trọng.
- [ ] **Ảnh chụp trước cải tiến (Before screenshot / evidence):** Minh chứng giao diện gây lỗi/khó dùng.
- [ ] **Hành động cải tiến (Improvement action):** Mô tả chi tiết việc chỉnh sửa giao diện.
- [ ] **Ảnh chụp sau cải tiến (After screenshot / evidence):** Minh chứng giao diện đã được khắc phục.
- [ ] **Git commit cho cải tiến (Git commit for improvement):** Commit hash chính thức lưu trữ thay đổi UI/UX.

---

## 8. Kết luận & Trạng thái hiện tại

* **Trạng thái hiện tại:** `PENDING REAL USER TEST` (Chưa thực hiện kiểm thử trên người dùng thật).
* **Cam kết liêm chính:** Tuyệt đối không tự điền kết quả giả định, không tự tạo trích dẫn phản hồi người dùng, không tự cho điểm usability khi chưa tổ chức test với người thật.

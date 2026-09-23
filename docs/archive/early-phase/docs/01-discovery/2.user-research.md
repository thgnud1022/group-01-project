# 2 – User Research Mini-study

## 1. Research Question

> Trong quy trình mua sắm nội bộ (Purchase Request → Approve → Collect Quotations → Compare → PO → Receive → Close), nhân viên, quản lý, bộ phận thu mua, kế toán tài chính và quản trị viên gặp những khó khăn gì trong việc tạo yêu cầu, theo dõi tiến độ, gom báo giá, kiểm soát ngân sách và đối soát? Họ mong muốn AI hỗ trợ ra sao và có những lo ngại gì về an toàn hệ thống?

---

## 2. Research Method

**Phương pháp:** Mini-interview (Phỏng vấn sâu cá nhân 1-1)

**Đối tượng nghiên cứu:** 5 vai trò tác nghiệp cốt lõi theo phân quyền RBAC của hệ thống ProcureAI:
- **Employee** (Người tạo yêu cầu mua sắm)
- **Manager** (Người phê duyệt nghiệp vụ phòng ban)
- **Procurement** (Chuyên viên thu mua & quản lý báo giá)
- **Finance** (Kế toán chi phí & kiểm soát ngân sách)
- **Admin** (Quản trị viên hệ thống & phân quyền)

**Tổng số participants:** 5 người

**Mục đích:** Thu thập bằng chứng thực tế (evidence) về điểm nghẽn quy trình mua sắm thủ công, từ đó xác định yêu cầu tính năng (Requirements), quy tắc nghiệp vụ (Business Rules) và các nguyên tắc kiểm soát AI (AI Governance).

---

## 3. Research Participants

| ID | Vai trò hệ thống | Người tham gia | Vị trí / Đơn vị công tác | Thâm niên |
|---|---|---|---|---|
| **P1** | Employee | Lê Hoàng Nam | Chuyên viên IT – FPT Software | 3 năm |
| **P2** | Manager | Trần Việt Anh | Trưởng phòng Marketing – Vinamilk | 6 năm |
| **P3** | Procurement | Nguyễn Mai Phương | Chuyên viên Thu mua Senior – Tập đoàn Hòa Phát | 5 năm |
| **P4** | Finance | Phạm Thanh Hà | Kế toán trưởng chi phí – Tập đoàn Sunhouse | 7 năm |
| **P5** | Admin | Vũ Đức Thắng | IT System Administrator – Masan Group | 4 năm |

---

# 4. Interview Questions

## 4.1. Dành cho Employee (P1)
### Q1. Hiện tại bạn đang tạo yêu cầu mua sắm (Purchase Request - PR) cho công việc bằng cách nào?
### Q2. Bạn thường gặp khó khăn gì khi mô tả thông số kỹ thuật, cấu hình hoặc phân loại danh mục sản phẩm cần mua?
### Q3. Sau khi gửi yêu cầu mua sắm, bạn theo dõi tiến độ phê duyệt và tình trạng đơn hàng bằng cách nào?
### Q4. Khi hàng hóa/dịch vụ được giao về, bạn xác nhận và nghiệm thu (Receiving) ra sao?
### Q5. Nếu có công cụ AI hỗ trợ khi lập PR, bạn mong muốn AI giúp gì nhất?

---

## 4.2. Dành cho Manager (P2)
### Q1. Anh/chị thường dựa vào những thông tin nào để quyết định Approve hoặc Reject một Purchase Request của nhân viên?
### Q2. Anh/chị có gặp khó khăn khi nhân viên mô tả yêu cầu mua sắm quá chung chung hoặc thiếu thông số không?
### Q3. Tại thời điểm bấm duyệt PR, anh/chị có nắm được hạn mức ngân sách còn lại của phòng ban mình không?
### Q4. Anh/chị mong muốn hệ thống hỗ trợ thông tin gì trên màn hình phê duyệt để ra quyết định nhanh hơn?

---

## 4.3. Dành cho Procurement (P3)
### Q1. Sau khi nhận được PR đã duyệt, anh/chị thu thập báo giá (Quotations) từ các nhà cung cấp (Suppliers) bằng cách nào?
### Q2. Việc đối chiếu và gộp dữ liệu từ nhiều file báo giá (PDF, Excel, Zalo) có gây phiền phức hoặc mất thời gian không?
### Q3. Anh/chị lập bảng so sánh báo giá để chọn nhà cung cấp dựa trên các tiêu chí nào?
### Q4. Anh/chị nghĩ sao về việc AI tự động đọc file báo giá (PDF/Excel) và lập bảng so sánh ma trận tiêu chí?
### Q5. Anh/chị có lo ngại gì nếu AI tự động đưa ra đề xuất chọn Nhà cung cấp (AI Recommendation) không?

---

## 4.4. Dành cho Finance (P4)
### Q1. Bộ phận Tài chính kiểm tra hạn mức ngân sách (Budget Check) phòng ban tại bước nào trong quy trình mua sắm?
### Q2. Chuyện gì xảy ra nếu đơn mua sắm bị chi vượt ngân sách hoặc giá mua cao bất thường so với lịch sử?
### Q3. Việc đối soát 3 chiều (3-Way Matching: PR ↔ PO ↔ Biên bản nhận hàng Receiving) hiện tại gặp khó khăn gì?
### Q4. Quan điểm của anh/chị về việc ứng dụng AI trong quản lý chi tiêu và phê duyệt ngân sách?

---

## 4.5. Dành cho Admin (P5)
### Q1. Việc phân quyền người dùng và kiểm soát quyền hạn giữa các phòng ban hiện tại cần tuân thủ nguyên tắc gì?
### Q2. Hệ thống cần ghi nhận nhật ký kiểm toán (Audit Trail) như thế nào để phục vụ thanh tra và truy vết sau này?

---

# 5. Employee Research Evidence (P1)

| **P** | **Observation / Quote rút gọn** | **Insight** |
|---|---|---|
| **P1 – Lê Hoàng Nam** | Mỗi lần tạo PR mua thiết bị, toàn ghi tự do như "laptop cấu hình mạnh". Bên thu mua lại gửi email hỏi lại thông số, mất cả tuần trao đổi. | Yêu cầu mua sắm đầu vào không chuẩn hóa làm kéo dài thời gian xử lý toàn quy trình. |
| **P1** | Nộp đơn xong không biết đơn đang ở bước nào (sếp duyệt chưa, phòng thu mua đã làm PO chưa), phải nhắn tin hỏi riêng. | Người dùng bị rơi vào "điểm mù" thông tin do thiếu giao diện theo dõi tiến độ thời gian thực. |
| **P1** | Khi nhận hàng về, chỉ ký vào giấy giao hàng của bên shipper mà không đối soát khớp với đơn đặt hàng ban đầu. | Quy trình nhận hàng (Receiving) còn rời rạc, thiếu liên kết dữ liệu với PO. |
| **P1** | Muốn AI tự nhận diện từ câu viết tự do và gợi ý chính xác cấu hình, mã danh mục (Category) cùng thông số kỹ thuật chuẩn. | AI PR Standardizer giúp rút ngắn 80% thời gian làm rõ thông tin giữa Requester và Buyer. |

---

# 6. Manager & Procurement Research Evidence (P2 & P3)

| **P** | **Observation / Quote rút gọn** | **Insight** |
|---|---|---|
| **P2 – Trần Việt Anh** | Phải nhắm mắt duyệt PR vì thông tin nhân viên viết chung chung, không biết mua loại đó có bị đắt hay có đúng tiêu chuẩn không. | Manager cần màn hình hiển thị đầy đủ thông tin chuẩn hóa và ngân sách khả dụng trước khi Approve. |
| **P2** | Không nhớ ngân sách phòng còn bao nhiêu. Cuối tháng Kế toán báo vượt ngân sách thì việc đã rồi, lại phải làm đơn giải trình. | Cần có tính năng kiểm tra hạn mức ngân sách (Budget Check) thời gian thực tại thời điểm duyệt. |
| **P3 – Nguyễn Mai Phương** | Ám ảnh nhất là ngồi mở 4-5 file PDF/Excel báo giá của các NCC, copy từng dòng đơn giá, phí vận chuyển, thuế vào file Excel tổng hợp để so sánh. | Khâu gom và nhập liệu báo giá thủ công ngốn nhiều thời gian và rất dễ gõ nhầm số liệu. |
| **P3** | Nhiều khi không nhớ năm ngoái mua mặt hàng này giá bao nhiêu nên bị NCC báo giá cao hơn 20-30% mà không biết. | Cần AI tự động phát hiện cảnh báo bất thường (Anomaly Alert) khi đơn giá vọt cao hơn lịch sử. |
| **P3** | AI trích xuất báo giá phải cho phép tôi xem file gốc và sửa tay nếu AI đọc sai. AI chỉ gợi ý, người quyết định chọn NCC vẫn phải là người. | AI Quotation Comparison phải đảm bảo nguyên tắc Human-in-the-loop và Editable extracted data. |

---

# 7. Finance & Admin Research Evidence (P4 & P5)

| **P** | **Observation / Quote rút gọn** | **Insight** |
|---|---|---|
| **P4 – Phạm Thanh Hà** | Rất sợ đứt gãy đối soát: PO đặt 10 cái ghế nhưng thực tế kho chỉ nhận 8 cái (Receiving), nếu Kế toán không kiểm tra kỹ sẽ thanh toán đủ 100% hóa đơn. | Bắt buộc phải khép kín luồng 3-Way Matching giữa PR ↔ PO ↔ Receiving trước khi Close đơn mua sắm. |
| **P4** | Tuyệt đối không cho phép AI tự động bấm duyệt chi ngân sách (No Auto-Approval). Quyết định tài chính phải do con người thực hiện. | AI chỉ đóng vai trò hỗ trợ cảnh báo vượt hạn mức và trích xuất dữ liệu, không có quyền Approve. |
| **P5 – Vũ Đức Thắng** | Hệ thống phải chặn tuyệt đối trường hợp người tạo PR tự bấm duyệt PR của chính mình (No Self-Approval). | Cần thiết lập phân quyền RBAC nghiêm ngặt 5 vai trò và ghi nhận 100% Audit Trail cho mọi thao tác. |

---

# 8. Research Synthesis

## Theme A – Purchase Request Standardization (Chuẩn hóa PR)
**Evidence:** P1 mất thời gian làm rõ thông số; P2 duyệt tù mù vì mô tả tự do thiếu chuẩn mực.  
**Insight:** Yêu cầu mua sắm không chuẩn hóa gây nghẽn luồng phê duyệt và làm khó bộ phận thu mua.  
**Product Implication:** Xây dựng **AI PR Standardizer** hỗ trợ tự động gợi ý danh mục, làm sạch câu chữ và bắt buộc điền đủ thông số kỹ thuật trước khi nộp.

---

## Theme B – Real-time Budget Visibility & Approval Control (Kiểm soát ngân sách)
**Evidence:** P2 không nắm được ngân sách phòng ban còn lại; P4 cảnh báo rủi ro bội chi chi tiêu cuối kỳ.  
**Insight:** Phê duyệt không có dữ liệu ngân sách thời gian thực dẫn đến nguy cơ vượt hạn mức tài chính.  
**Product Implication:** Tích hợp **Budget Check** hiển thị hạn mức khả dụng thời gian thực ngay trên màn hình Approval của Manager và Finance; hiển thị cảnh báo khi giá trị PR vượt ngân sách.

---

## Theme C – Automated Quotation Extraction & Comparison (So sánh báo giá)
**Evidence:** P3 tốn nhiều giờ gõ lại dữ liệu từ các file PDF/Excel báo giá rời rạc và khó phát hiện chênh lệch giá lịch sử.  
**Insight:** Khâu xử lý báo giá thủ công chiếm nhiều công sức và dễ phát sinh sai sót dữ liệu.  
**Product Implication:** Phát triển **AI Quotation Comparison** tự động đọc dữ liệu PDF/Excel, lập ma trận so sánh đa tiêu chí và cảnh báo đơn giá chênh lệch cao bất thường ($\ge 20\%$) so với lịch sử.

---

## Theme D – 3-Way Matching & Process Continuity (Khép kín luồng & Đối soát)
**Evidence:** P1 không theo dõi được tiến độ; P4 gặp rủi ro thanh toán sai lệch do biên bản nhận hàng không khớp PO.  
**Insight:** Thiếu tính liên tục và đứt gãy đối soát giữa Đặt hàng (PO) và Giao nhận (Receiving) gây thất thoát tài chính.  
**Product Implication:** Hiện thực hóa luồng 7 bước bắt buộc `Request → Approve → Collect quotations → Compare → PO → Receive → Close`. Yêu cầu đối soát chi tiết giữa PO và Biên bản Receiving trước khi hoàn tất Close.

---

## Theme E – AI Governance & Security Rules (An toàn hệ thống & Quyền hạn AI)
**Evidence:** P3 yêu cầu cho phép chỉnh sửa dữ liệu AI trích xuất; P4 kiên quyết không cho AI tự động duyệt chi; P5 yêu cầu chặn tự duyệt đơn.  
**Insight:** Người dùng chỉ tin tưởng AI khi AI transparent, có căn cứ trích dẫn và con người giữ quyền quyết định cuối cùng.  
**Product Implication:** Áp dụng nguyên tắc **Human-in-the-loop**, **Strict No Self-Approval**, không cấp quyền Auto-approval cho AI, và 100% dữ liệu AI trích xuất phải cho phép rà soát/chỉnh sửa thủ công.

---

# 9. Research Conclusion

Từ 5 phỏng vấn sâu với 5 vai trò đại diện, nghiên cứu rút ra 5 phát hiện cốt lõi:
1. **Yêu cầu mua sắm bị phân tán và thiếu chuẩn hóa.**
2. **Thiếu thông tin ngân sách thời gian thực tại các mốc phê duyệt.**
3. **Xử lý và so sánh báo giá thủ công tiêu tốn nhiều nhân lực.**
4. **Cần khép kín luồng đối soát 3 chiều giữa PR ↔ PO ↔ Receiving.**
5. **AI đóng vai trò trợ lý phân tích/cảnh báo, con người giữ quyền quyết định phê duyệt.**

Các kết quả này làm cơ sở thực chứng vững chắc để xây dựng **Requirement Inventory (`requirements.md`)** và **Business Rules** cho ProcureAI.

---

# 10. Fact vs Assumption

### Fact (Đã được xác nhận)
- Các phát hiện trên được tổng hợp từ câu trả lời trực tiếp của **5 participants** thuộc đúng 5 vai trò của hệ thống.
- Khó khăn trong xử lý báo giá PDF/Excel và đứt gãy đối soát PO-Receiving là có thực.

### Assumption (Giả định cần kiểm chứng tiếp)
- Người dùng sẽ tin tưởng và sử dụng AI Quotation Comparison thường xuyên.
- AI trích xuất file PDF báo giá đạt độ chính xác từ 80-85% trên mọi mẫu định dạng báo giá tiếng Việt.
- Ngưỡng duyệt PR > 50 triệu VND cần cả Manager và Finance duyệt là phù hợp cho mọi quy mô doanh nghiệp.

---

# 11. Research Limitation

Nghiên cứu hiện tại thực hiện trên 5 participants đại diện cho 5 vai trò (n=5). Dù đã bao phủ đầy đủ các vai trò trong phạm vi RBAC của MVP, số lượng mẫu chưa đủ lớn để đại diện cho tất cả các mô hình doanh nghiệp đặc thù (như sản xuất nặng, bán lẻ chuỗi). Do đó, các kết quả được sử dụng để định hình phạm vi MVP cốt lõi và sẽ tiếp tục được kiểm chứng qua giai đoạn Usability Testing của Prototype.

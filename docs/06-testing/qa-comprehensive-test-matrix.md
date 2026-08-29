# BẢNG MA TRẬN KIỂM THỬ TOÀN DIỆN (QA COMPREHENSIVE TEST MATRIX)
**Dự án:** AI Procurement & Purchase Approval System (Hệ thống Thu mua và Phê duyệt Mua sắm hỗ trợ bởi AI)  
**Vai trò:** QA Engineer / Software Tester  
**Phiên bản tài liệu:** v1.0.0  
**Ngày cập nhật:** 2026-08-27  

---

## I. DANH SÁCH TEST SCENARIOS (KỊCH BẢN KIỂM THỬ TỔNG QUAN)

Dưới đây là danh mục kịch bản kiểm thử tổng quan được xây dựng trực tiếp từ luồng nghiệp vụ thực tế của hệ thống, bao phủ toàn bộ 11 User Stories thuộc 5 Epics chính.

| Scenario ID | Tên Kịch Bản (Scenario Name) | User Story liên kết | Requirement liên kết | Feature / Chốt chặn nghiệp vụ | Mức độ ưu tiên |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TS-01** | Tạo và hoàn thiện Purchase Request (PR) với AI hỗ trợ | **US-01** | REQ-FR-01, REQ-FR-02, REQ-FR-03 | Voice/Text PR Standardization & Auto-fill | High |
| **TS-02** | Theo dõi trạng thái và tiến trình xử lý của PR | **US-02** | REQ-FR-04 | PR Status Tracking (StatusBadge) | Medium |
| **TS-03** | Phê duyệt PR phân cấp theo hạn mức | **US-03** | REQ-FR-05, REQ-FR-06, REQ-FR-07 | Multi-level Approval Workflow ($\\leq 50$tr vs $> 50$tr) | High |
| **TS-04** | Kiểm soát ngân sách phòng ban và cảnh báo vượt hạn mức | **US-04** | REQ-FR-08, REQ-FR-09, REQ-BR-04, REQ-BR-05 | Real-time Budget Guard | High |
| **TS-05** | Quản lý Supplier và tải file báo giá (Quotation) lên hệ thống | **US-05** | REQ-FR-10, REQ-FR-11, REQ-BR-06, REQ-BR-07 | AI Quotation Extraction & Database Linking | Medium |
| **TS-06** | Xem và đối chiếu thông tin các báo giá tập trung | **US-06** | REQ-FR-12 | Quotation Comparison Table UI | Medium |
| **TS-07** | Nhận phân tích so sánh và đề xuất từ AI (AI Recommendation) | **US-07** | REQ-FR-13, REQ-FR-14, REQ-BR-08, REQ-BR-09 | AI Decision Support (Khuyến nghị không tự quyết) | High |
| **TS-08** | Nhận diện và cảnh báo đơn giá bất thường tăng cao | **US-08** | REQ-FR-15 | AI Anomaly Alert (Cảnh báo lệch giá $\geq 20\%$) | High |
| **TS-09** | Chọn báo giá và khởi tạo đơn đặt hàng PO khóa cứng đơn giá | **US-09** | REQ-FR-16, REQ-BR-10, REQ-BR-12, ASM-04 | PO Lock Price Enforcement (Chống sửa đổi từ client) | High |
| **TS-10** | Ghi nhận giao nhận hàng thực tế và kiểm soát số lượng nhận | **US-10** | REQ-FR-17, ASM-06 | Goods Receipt Guard (Tổng thực nhận $\leq$ Số lượng PO) | High |
| **TS-11** | Quyết toán ngân sách và đóng hồ sơ mua sắm PR | **US-11** | REQ-FR-18, REQ-BR-11 | Budget Close & Fund Release (`tempReserved` -> `spent`) | High |

---

## II. DANH SÁCH END-TO-END FLOWS (LUỒNG NGHIỆP VỤ LIÊN HOÀN)

Các luồng kiểm thử liên hoàn E2E này giả lập trực tiếp các kịch bản sử dụng thực tế của doanh nghiệp, đi xuyên suốt qua nhiều vai trò khác nhau trong hệ thống.

### **E2E-01: Luồng mua sắm tiêu chuẩn dưới hạn mức (Happy Path PR $\leq$ 50M)**
*   **Starting Role:** Employee (`employee@company.com`)
*   **Starting State:** Phòng ban có đủ ngân sách khả dụng; có sẵn Supplier trong cơ sở dữ liệu.
*   **Quy trình xử lý (Steps):**
    1. **Employee** đăng nhập, sử dụng giọng nói thông qua `VoiceComposer` nhập yêu cầu: *"Cần mua 1 laptop Dell 25tr cho dev"* [11].
    2. AI bóc tách thông tin [11], tự động điền Form PR gồm: Tên SP = "Laptop Dell", Số lượng = 1, Đơn giá ước tính = 25.000.000 VND [11].
    3. Employee kiểm tra Form, xác nhận thông tin và bấm **Submit PR**. Hệ thống tự động kiểm tra ngân sách (Budget Check) [12], tạm khóa số tiền 25.000.000 VND vào trường `tempReservedAmount` của phòng ban [171], và tạo PR với trạng thái `PENDING_MANAGER_APPROVAL` [171].
    4. **Manager** đăng nhập [183], mở danh sách PR chờ duyệt, kiểm tra thông tin laptop tập trung và bấm **Approve** [165]. Vì giá trị PR = 25 triệu ($\leq 50$ triệu) nên PR chuyển thẳng sang trạng thái `COLLECTING_QUOTATIONS` (hoặc `APPROVED`) [165, 171].
    5. **Procurement** đăng nhập [183], điều hướng tới PR, tải lên 3 file PDF báo giá độc lập từ các nhà cung cấp [167]. AI bóc tách dữ liệu và đồng bộ vào bảng so sánh [167].
    6. Procurement mở bảng so sánh (`ComparisonTable`) [14], đọc khuyến nghị của AI (AI Recommendation) [167]. Procurement bấm chọn báo giá của nhà cung cấp rẻ nhất và click **Tạo PO** [167, 168].
    7. Hệ thống tự động khởi tạo đơn hàng PO [168], sao chép và khóa cố định 100% đơn giá từ báo giá gốc vào bảng `POItem` [168, 171]. Trạng thái PR chuyển sang **`PO_CREATED`** [171].
    8. **Employee** nhận hàng thực tế, đăng nhập vào giao diện ghi nhận hàng [169], nhập số lượng thực nhận = 1, tải lên ảnh biên bản bàn giao [12], hệ thống cho phép ghi nhận và cập nhật trạng thái [169].
    9. **Finance** đăng nhập [183], kiểm tra hồ sơ và bấm **Close PR** [12]. Hệ thống thực hiện transaction cuối cùng [12]: Trừ tiền chính thức vào cột `spentAmount` (+25 triệu), giải phóng cột `tempReservedAmount` (-25 triệu) và chuyển PR sang trạng thái **`CLOSED`** [12, 171].
*   **Expected End State:** PR có trạng thái `CLOSED` [171].
*   **Database/API cần kiểm tra:** `POST /api/pr` [12], `POST /api/po` [12], `POST /api/receiving` [12], `POST /api/pr/:id/close` [12], các trường trong bảng `Budget` [171].
*   **Evidence cần thu thập:** Playwright E2E test logs [186], PostgreSQL query logs cho thấy sự biến động của `tempReservedAmount` và `spentAmount` [171].

### **E2E-02: Luồng mua sắm lớn cần duyệt song cấp (Happy Path PR > 50M)**
*   **Starting Role:** Employee (`employee@company.com`)
*   **Starting State:** Phòng ban có đủ ngân sách; PR yêu cầu mua thiết bị giá trị 75.000.000 VND.
*   **Quy trình xử lý (Steps):**
    1. **Employee** đăng nhập, tạo PR trị giá 75.000.000 VND [195]. Hệ thống tự động kiểm tra ngân sách, khóa tạm tính `tempReservedAmount` (+75.000.000) [171]. PR chuyển trạng thái `PENDING_MANAGER_APPROVAL` [171].
    2. **Manager** đăng nhập, mở chi tiết PR và bấm **Approve** [165]. Do giá trị PR = 75 triệu (> 50 triệu) nên hệ thống tự động chuyển PR sang trạng thái trung gian **`PENDING_FINANCE_APPROVAL`** [12, 171].
    3. **Finance** đăng nhập [183], mở PR cần kiểm soát ngân sách lớn, kiểm tra thông tin so sánh với Budget khả dụng của phòng ban [166]. Finance đồng ý và bấm **Approve** lần 2 [165, 166]. PR chuyển sang trạng thái `COLLECTING_QUOTATIONS` [171].
    4. **Procurement** đăng nhập, thu thập 3 báo giá PDF [167], tiến hành đối chiếu so sánh, chọn báo giá, khởi tạo đơn PO và nhận hàng đầy đủ tương tự luồng E2E-01 [167, 168, 169].
    5. **Finance** thực hiện đóng PR kết thúc quy trình [12].
*   **Expected End State:** PR hoàn tất khép kín và chuyển trạng thái sang `CLOSED` [171].
*   **Database/API cần kiểm tra:** `POST /api/pr/:id/approve` (Manager duyệt) [12], `POST /api/pr/:id/approve` (Finance duyệt lần 2) [12].
*   **Evidence cần thu thập:** Playwright test run results cho luồng duyệt song cấp [186].

### **E2E-03: Luồng trả duyệt và chỉnh sửa khi có sai sót (Revision Flow)**
*   **Starting Role:** Employee (`employee@company.com`)
*   **Starting State:** Employee tạo PR nhưng thông tin mô tả laptop chưa rõ ràng hoặc giá ước tính quá cao.
*   **Quy trình xử lý (Steps):**
    1. **Employee** tạo và submit PR laptop trị giá 30.000.000 VND [195].
    2. **Manager** xem xét PR, nhận thấy đơn giá laptop Dell i5 30 triệu là quá cao so với mặt bằng thị trường doanh nghiệp. Manager bấm chọn **Request Revision** (Yêu cầu chỉnh sửa) [165], nhập bình luận: *"Vui lòng chọn cấu hình i5 tầm giá dưới 20 triệu để tiết kiệm ngân sách"* [165, 171].
    3. Hệ thống ghi nhận quyết định phê duyệt [199], lưu lịch sử ý kiến vào bảng `Approval` [171], và cập nhật trạng thái PR thành **`REVISION_REQUESTED`** (*NEEDS CLARIFICATION* - hoặc trạng thái tương đương được định nghĩa trong codebase).
    4. **Employee** nhận được thông báo yêu cầu sửa đổi [134], mở lại PR đang ở trạng thái chỉnh sửa, cập nhật lại đơn giá ước tính xuống còn 18.000.000 VND và submit lại [134].
    5. Hệ thống cập nhật lại số tiền tạm khóa `tempReservedAmount` trong bảng `Budget` từ 30 triệu xuống 18 triệu [171], chuyển trạng thái PR quay lại `PENDING_MANAGER_APPROVAL` [171].
    6. **Manager** mở lại PR, đồng ý với mức giá mới và bấm **Approve** để tiếp tục quy trình mua sắm [165].
*   **Expected End State:** PR được duyệt thành công sang trạng thái tiếp theo (`COLLECTING_QUOTATIONS`) [171].
*   **Database/API cần kiểm tra:** API cập nhật PR sau chỉnh sửa, bảng dữ liệu `Approval` ghi nhận ý kiến phản hồi [171].

---

## III. DANH SÁCH CÁC POSITIVE CASES (HAPPY PATHS - LUỒNG CHẠY THÀNH CÔNG)

Các ca kiểm thử Happy Path nhằm xác nhận các tính năng chính chạy đúng thiết kế khi người dùng nhập dữ liệu chuẩn xác và đầy đủ.

### **Epic 1: Purchase Request (Yêu cầu mua sắm)**
*   **TC-POS-01: Tạo PR thành công trong hạn mức ngân sách phòng ban**
    *   *Trace:* REQ-FR-01 $\rightarrow$ Feature: Create PR $\rightarrow$ `backend/app/routers/pr.py` & `backend/app/services/pr_service.py` [11, 12]
    *   *Precondition:* Tài khoản Employee đăng nhập [183], ngân sách khả dụng của phòng ban IT còn 100.000.000 VND [183].
    *   *Test Data:* Laptop Dell, số lượng = 1, giá ước tính = 25.000.000 VND.
    *   *Steps:* Nhập đầy đủ thông tin vào Form, bấm Submit.
    *   *Expected Result:* PR được tạo thành công, database bảng `PurchaseRequest` lưu bản ghi mới với status `PENDING_MANAGER_APPROVAL` [171]. `tempReservedAmount` của phòng IT tăng thêm 25.000.000 VND [171].
*   **TC-POS-02: Theo dõi trạng thái PR thay đổi trực quan**
    *   *Trace:* REQ-FR-04 $\rightarrow$ Feature: PR Tracking $\rightarrow$ `frontend/src/pages/PRList.tsx` [197]
    *   *Precondition:* Employee có PR vừa được tạo [197].
    *   *Steps:* Mở màn hình "Danh sách PR cá nhân" để quan sát [197].
    *   *Expected Result:* PR hiển thị trạng thái hiện tại dưới dạng Badge màu sắc trực quan (ví dụ: Màu vàng hổ phách cho trạng thái chờ duyệt) [13]. Khi trạng thái thay đổi ở Backend, UI tự động cập nhật trạng thái mới nhất [197].

### **Epic 2: Approval & Budget (Phê duyệt & Ngân sách)**
*   **TC-POS-03: Phê duyệt PR nhỏ hơn hoặc bằng 50 triệu VND (01 cấp duyệt)**
    *   *Trace:* REQ-FR-06, REQ-FR-07 $\rightarrow$ Feature: Approval Workflow $\rightarrow$ `backend/app/routers/pr.py` (endpoint `/api/pr/:id/approve`) [12, 165]
    *   *Precondition:* Có một PR trị giá 25.000.000 VND đang ở trạng thái chờ duyệt [165].
    *   *Steps:* Manager đăng nhập, nhấn **Approve** PR [165].
    *   *Expected Result:* Hệ thống ghi nhận quyết định duyệt, PR chuyển trạng thái thẳng sang `COLLECTING_QUOTATIONS` [171] (hoặc `APPROVED` tùy codebase). Lịch sử duyệt ghi vết vào bảng `Approval` [171].
*   **TC-POS-04: Phê duyệt PR lớn hơn 50 triệu VND (Duyệt song cấp - Bước 1)**
    *   *Trace:* REQ-FR-06, REQ-FR-07 $\rightarrow$ Feature: Multi-level Approval $\rightarrow$ `backend/app/routers/pr.py` [12, 165]
    *   *Precondition:* Có một PR trị giá 75.000.000 VND đang chờ duyệt [165].
    *   *Steps:* Manager đăng nhập, nhấn **Approve** [165].
    *   *Expected Result:* PR được ghi nhận duyệt bước 1, trạng thái cập nhật thành **`PENDING_FINANCE_APPROVAL`** [12, 171]. Hệ thống không tự ý nhảy cóc sang Approved [165].
*   **TC-POS-05: Phê duyệt PR lớn hơn 50 triệu VND (Duyệt song cấp - Bước 2 bởi Finance)**
    *   *Trace:* REQ-FR-08 $\rightarrow$ Feature: Finance Approval $\rightarrow$ `backend/app/routers/pr.py` [12, 165]
    *   *Precondition:* PR trị giá 75.000.000 VND đang ở trạng thái `PENDING_FINANCE_APPROVAL` [12, 171].
    *   *Steps:* Finance đăng nhập, mở PR và nhấn **Approve** [165].
    *   *Expected Result:* PR được phê duyệt hoàn toàn, trạng thái cập nhật thành `COLLECTING_QUOTATIONS` (APPROVED) [171], cho phép Procurement tiến hành thu thập báo giá [167].

### **Epic 3: Supplier & Quotation (Báo giá & So sánh)**
*   **TC-POS-06: Tải lên và bóc tách báo giá PDF thành công**
    *   *Trace:* REQ-FR-11 $\rightarrow$ Feature: AI Quotation Extraction $\rightarrow$ `backend/app/routers/quotations.py` & `backend/app/services/ai_service.py` [11, 167]
    *   *Precondition:* PR đã được duyệt [167]. Procurement chuẩn bị file PDF báo giá thô [167].
    *   *Steps:* Procurement tải lên file PDF báo giá của nhà cung cấp Phong Vũ.
    *   *Expected Result:* AI Service bóc tách chính xác thông tin nhà cung cấp, sản phẩm, số lượng, đơn giá, thời hạn giao hàng và ghi dữ liệu an toàn vào bảng `Quotation`, `QuotationItem` liên kết với PR [167, 171].
*   **TC-POS-07: Hiển thị bảng đối chiếu và đề xuất lựa chọn tối ưu từ AI**
    *   *Trace:* REQ-FR-12, REQ-FR-14 $\rightarrow$ Feature: AI Comparison & Recommendation $\rightarrow$ `frontend/src/modules/quotations/components/ComparisonTable.tsx` [14, 176]
    *   *Precondition:* Có đủ 3 báo giá PDF đã được tải lên và trích xuất dữ liệu [167].
    *   *Steps:* Procurement mở chức năng "Quotation Comparison" [204].
    *   *Expected Result:* Hệ thống hiển thị bảng so sánh cột dọc trực quan giữa 3 nhà cung cấp [14]. Dòng chứa đơn giá thấp nhất được highlight màu xanh lá (`#15803D`) [13]. Panel hiển thị rõ ràng nội dung khuyến nghị từ AI dựa trên các tiêu chí (giá cả, bảo hành, thời gian giao hàng) [167, 170].

### **Epic 4: Purchase Order (Đơn đặt hàng PO)**
*   **TC-POS-08: Khởi tạo PO thành công và khóa cố định đơn giá**
    *   *Trace:* REQ-FR-16, REQ-BR-12 $\rightarrow$ Feature: PO Lock Price Enforcement $\rightarrow$ `backend/app/services/po_service.py` [12, 168]
    *   *Precondition:* Procurement chọn một nhà cung cấp trong bảng so sánh [168].
    *   *Steps:* PROCUREMENT bấm **Tạo PO** [168].
    *   *Expected Result:* Đơn hàng PO được tạo thành công [168]. Hệ thống tự động truy vấn đơn giá gốc từ database bảng `QuotationItem` và ghi đè cố định vào bảng `POItem` [171]. Trên giao diện, các ô nhập đơn giá, số lượng bị khóa cứng (`readonly`), không cho phép bất kỳ hành vi chỉnh sửa nào từ phía người dùng [168]. Trạng thái PR chuyển sang `PO_CREATED` [171].

### **Epic 5: Receiving & Close (Giao nhận & Quyết toán)**
*   **TC-POS-09: Ghi nhận nhận hàng thực tế thành công**
    *   *Trace:* REQ-FR-17 $\rightarrow$ Feature: Goods Receipt $\rightarrow$ `backend/app/routers/receiving.py` [12, 169]
    *   *Precondition:* PO đã được phát hành [169], hàng hóa được giao nhận thực tế [169].
    *   *Steps:* Employee nhập số lượng thực nhận bằng đúng số lượng đặt trên PO, tải ảnh biên bản bàn giao, submit.
    *   *Expected Result:* Hệ thống ghi nhận biên bản nhận hàng thành công, tạo mới bản ghi trong bảng `Receiving` [171], cập nhật trạng thái PR thành `RECEIVED` (hoặc trạng thái tương đương) [171].
*   **TC-POS-10: Finance quyết toán đóng PR giải phóng ngân sách**
    *   *Trace:* REQ-FR-18, REQ-BR-11 $\rightarrow$ Feature: Budget Close $\rightarrow$ `backend/app/routers/pr.py` (endpoint `/api/pr/:id/close`) [12, 178]
    *   *Precondition:* Hàng hóa đã được nhận đầy đủ [169].
    *   *Steps:* Finance đăng nhập, bấm chọn **Close PR** [12].
    *   *Expected Result:* Hệ thống đóng PR thành công, trạng thái PR chuyển sang **`CLOSED`** [12, 171]. Ngân sách phòng ban cập nhật chính xác: Trừ vĩnh viễn khoản tạm khóa `tempReservedAmount` và cộng số tiền này vào thực chi `spentAmount` trong bảng `Budget` [171].

---

## IV. DANH SÁCH CÁC NEGATIVE CASES (LUỒNG CHẶN & LỖI NGHIỆP VỤ)

Các ca kiểm thử Negative nhằm đảm bảo hệ thống có khả năng tự vệ cao, chặn đứng các hành động vi phạm quy tắc nghiệp vụ hoặc dữ liệu biên sai lệch.

### **Epic 1 & Epic 2: Purchase Request & Budget Control**
*   **TC-NEG-01: Chặn gửi PR khi Form thiếu thông tin bắt buộc**
    *   *Trace:* REQ-FR-02, REQ-BR-01 $\rightarrow$ Feature: PR Validation $\rightarrow$ `frontend/src/pages/CreatePR.tsx` [176, 178]
    *   *Precondition:* Employee đang điền Form tạo PR [195].
    *   *Test Data:* Form PR để trống trường "Tên sản phẩm" hoặc "Đơn giá ước tính" = 0 hoặc rỗng.
    *   *Steps:* Để trống trường bắt buộc, bấm Submit PR.
    *   *Expected Result:* Hệ thống chặn ngay tại giao diện frontend, highlight đỏ các trường thiếu và hiển thị thông báo lỗi yêu cầu hoàn thiện dữ liệu [195]. Nút Submit không kích hoạt gửi API.
*   **TC-NEG-02: Chặn tạo PR vượt hạn mức ngân sách phòng ban (Budget Guard)**
    *   *Trace:* REQ-FR-09, REQ-BR-05 $\rightarrow$ Feature: Real-time Budget Guard $\rightarrow$ `backend/app/services/pr_service.py` [12, 166]
    *   *Precondition:* Ngân sách khả dụng còn lại của phòng IT là 20.000.000 VND [166].
    *   *Test Data:* Nhập yêu cầu mua laptop trị giá 25.000.000 VND.
    *   *Steps:* Điền đầy đủ thông tin, bấm Submit PR.
    *   *Expected Result:* API Backend kiểm tra ngân sách, chặn đứng hành động lưu DB, trả về mã lỗi HTTP 400 Bad Request [186]. Giao diện hiển thị Banner cảnh báo đỏ nổi bật với nội dung thông tin chi tiết: *"Không thể tạo PR: Giá trị ước tính (25.000.000đ) vượt quá Ngân sách khả dụng còn lại..."* [14].

### **Epic 3: Supplier & Quotation**
*   **TC-NEG-03: Chặn thu thập báo giá khi PR chưa được Approve**
    *   *Trace:* REQ-BR-02, REQ-BR-06 $\rightarrow$ Feature: Quotation Upload Guard $\rightarrow$ `backend/app/routers/quotations.py` [167, 178]
    *   *Precondition:* PR có trạng thái `PENDING_MANAGER_APPROVAL` [171].
    *   *Steps:* Cố tình dùng công cụ Postman gửi request upload file báo giá lên API liên kết với PR này.
    *   *Expected Result:* API Backend chặn xử lý, trả về lỗi HTTP 400 Bad Request kèm thông báo: *"Purchase Request chưa được phê duyệt đầy đủ, không cho phép thu thập báo giá."* (*NEEDS CLARIFICATION* - về microcopy lỗi chính xác ở backend).

### **Epic 4: Purchase Order**
*   **TC-NEG-04: Chặn tạo PO đối với PR chưa APPROVED**
    *   *Trace:* REQ-BR-10 $\rightarrow$ Feature: PO Creation Guard $\rightarrow$ `backend/app/services/po_service.py` [12, 178]
    *   *Precondition:* PR đang ở trạng thái `REJECTED` hoặc `PENDING_FINANCE_APPROVAL` [171].
    *   *Steps:* Cố tình gửi request tạo PO thông qua Postman đến endpoint `POST /api/po` kèm ID của PR này [12].
    *   *Expected Result:* Backend chặn đứng transaction, trả về lỗi HTTP 400 Bad Request, không tạo bất kỳ bản ghi PO nào dưới cơ sở dữ liệu [12].
*   **TC-NEG-05: Chặn hành vi cố tình gửi sửa đơn giá PO từ Client**
    *   *Trace:* REQ-BR-12, ASM-04 $\rightarrow$ Feature: Anti-Fraud Guard $\rightarrow$ `backend/app/services/po_service.py` [12, 168]
    *   *Precondition:* Báo giá của Phong Vũ được chọn có đơn giá laptop là 25.000.000 VND [14].
    *   *Test Data:* Gửi payload tạo PO chứa trường chỉnh sửa đơn giá: `{ "purchaseRequestId": "PR-001", "quotationId": "Q-01", "customUnitPrice": 20000000 }` (cố tình dìm giá).
    *   *Steps:* Thao tác hack payload gửi lên API `POST /api/po` [12].
    *   *Expected Result:* Backend hoàn toàn phớt lờ tham số đơn giá truyền lên từ client, tự động đọc giá gốc từ bảng `QuotationItem` dưới DB để khởi tạo POItem với đúng giá 25.000.000 VND [168, 171].

### **Epic 5: Receiving & Close**
*   **TC-NEG-06: Chặn nhận hàng vượt quá số lượng đặt trên PO (Over-Receiving Guard)**
    *   *Trace:* REQ-FR-17, ASM-06 $\rightarrow$ Feature: Goods Receipt Guard $\rightarrow$ `backend/app/routers/receiving.py` [12, 169]
    *   *Precondition:* PO được phê duyệt đặt mua 01 laptop Dell [168].
    *   *Test Data:* Nhập số lượng thực nhận = 2.
    *   *Steps:* Nhập số lượng nhận, bấm Submit.
    *   *Expected Result:* Hệ thống chặn ngay lập tức, trả về lỗi HTTP 400 Bad Request [186]. Giao diện hiển thị cảnh báo đỏ ngăn chặn hành động: *"Tổng số lượng thực nhận không được phép vượt quá số lượng trên đơn đặt hàng PO"* (*NEEDS CLARIFICATION* - về microcopy hiển thị chính xác của lỗi này).
*   **TC-NEG-07: Chặn quyết toán đóng PR khi hàng hóa chưa được nhận đầy đủ**
    *   *Trace:* REQ-FR-18, REQ-BR-11 $\rightarrow$ Feature: Close PR Guard $\rightarrow$ `backend/app/routers/pr.py` [12, 178]
    *   *Precondition:* PO đặt mua 05 cái laptop, nhưng số lượng nhận trong bảng `Receiving` lũy kế mới chỉ có 3 cái [171].
    *   *Steps:* Finance cố tình bấm nút **Close PR** trên giao diện chi tiết [12].
    *   *Expected Result:* Hệ thống chặn hành động, trả về lỗi báo nghiệp vụ: *"Không thể đóng PR: Quá trình nhận hàng giao tế chưa hoàn tất (mới nhận 3/5 sản phẩm)."* (*NEEDS CLARIFICATION* - về microcopy thông báo lỗi cụ thể).

---

## V. DANH SÁCH CÁC PERMISSION CASES (KIỂM THỬ PHÂN QUYỀN RBAC)

Đảm bảo hệ thống phân quyền chặt chẽ theo đúng vai trò người dùng bám sát yêu cầu `REQ-NFR-02` [177]. Mọi API (ngoại trừ login và health) đều phải kiểm soát token và từ chối các vai trò không hợp lệ với mã lỗi HTTP 403 Forbidden [11, 12].

| User Role | API Endpoint thực thi | Quyền Kỳ Vọng | Test Case xác minh phân quyền (RBAC Case) |
| :--- | :--- | :---: | :--- |
| **EMPLOYEE** | `POST /api/pr` | **ALLOW** | **TC-PERM-01:** Tạo PR thành công [12]. |
| | `POST /api/pr/:id/approve` | **DENY** | **TC-PERM-02:** Trả về lỗi **HTTP 403 Forbidden**. Employee không được tự duyệt PR của mình [165]. |
| | `POST /api/quotations/compare` | **DENY** | **TC-PERM-03:** Trả về lỗi **HTTP 403 Forbidden** [11]. |
| | `POST /api/po` | **DENY** | **TC-PERM-04:** Trả về lỗi **HTTP 403 Forbidden** [12]. |
| **MANAGER** | `POST /api/pr/:id/approve` | **ALLOW** | **TC-PERM-05:** Phê duyệt PR thành công [12]. |
| | `POST /api/po` | **DENY** | **TC-PERM-06:** Trả về lỗi **HTTP 403 Forbidden** [12]. |
| | `POST /api/pr/:id/close` | **DENY** | **TC-PERM-07:** Trả về lỗi **HTTP 403 Forbidden** [12]. |
| **PROCUREMENT**| `POST /api/quotations/compare` | **ALLOW** | **TC-PERM-08:** Thực hiện so sánh báo giá thành công [11]. |
| | `POST /api/po` | **ALLOW** | **TC-PERM-09:** Khởi tạo PO thành công [12]. |
| | `POST /api/pr/:id/approve` | **DENY** | **TC-PERM-10:** Trả về lỗi **HTTP 403 Forbidden** [12]. |
| **FINANCE** | `POST /api/pr/:id/approve` | **ALLOW** | **TC-PERM-11:** Phê duyệt PR lớn (>50tr) ở bước 2 thành công [12, 165]. |
| | `POST /api/pr/:id/close` | **ALLOW** | **TC-PERM-12:** Thực hiện hạch toán đóng PR thành công [12]. |
| | `POST /api/po` | **DENY** | **TC-PERM-13:** Trả về lỗi **HTTP 403 Forbidden** [12]. |

---

## VI. DANH SÁCH CÁC ERROR CASES (LỖI KỸ THUẬT & HỆ THỐNG)

Các ca kiểm thử lỗi kỹ thuật nhằm đánh giá khả năng chịu lỗi (Resilience), khôi phục và hiển thị thông tin xử lý sự cố thân thiện với người dùng cuối, tránh treo hoặc gãy ứng dụng.

### **1. Lỗi kết nối Cơ sở dữ liệu (Database Connection Drop)**
*   **Scenario ID:** TC-ERR-01
*   **Mô tả:** Cơ sở dữ liệu PostgreSQL 18 đột ngột mất kết nối hoặc bị stop container trong lúc người dùng đang thực hiện duyệt tiền hoặc tạo PO.
*   **API kiểm chứng:** `GET /api/health` [11], `POST /api/po` [12]
*   **Expected Result:** 
    *   Endpoint `/api/health` trả về JSON trạng thái lỗi: `{ "status": "unhealthy", "database": "disconnected" }` (*NEEDS CLARIFICATION* - về cấu trúc response lỗi healthcheck chi tiết).
    *   Hệ thống Backend FastAPI tự động bắt lỗi DB exception, không bị sập tiến trình, trả về mã lỗi HTTP 500 Internal Server Error và ghi log sự cố có cấu trúc (Structured Logging) [44].
    *   UI Frontend không bị treo trắng màn hình, hiển thị hộp thoại cảnh báo: *"Hệ thống đang gặp sự cố kết nối cơ sở dữ liệu. Vui lòng thử lại sau ít phút."* [75]

### **2. Lỗi Race Condition khi trừ tiền ngân sách phòng ban đồng thời**
*   **Scenario ID:** TC-ERR-02
*   **Mô tả:** Hai Employee của cùng một phòng ban bấm Submit 2 PR khác nhau ở cùng một mili-giây, trong khi số dư ngân sách khả dụng chỉ còn đủ cho 1 PR duyệt.
*   **API kiểm chứng:** `POST /api/pr` [12]
*   **Expected Result:** 
    *   Backend FastAPI bắt buộc phải xử lý transaction ở mức cô lập an toàn (Isolation Level / Select for Update) để khóa dòng ngân sách của phòng ban lại.
    *   Giao dịch đầu tiên được thực hiện thành công, ghi DB và khóa ngân sách tạm tính [171].
    *   Giao dịch thứ hai ngay sau đó bị chặn lại do kiểm tra thấy số dư khả dụng thực tế đã bị thay đổi và không còn đủ tiền, trả về lỗi HTTP 400 Bad Request [186]. Hệ thống không được phép để xảy ra tình trạng ngân sách khả dụng bị âm.

### **3. Lỗi gọi API Trí tuệ nhân tạo (LLM Gateway Timeout / Quota Limit)**
*   **Scenario ID:** TC-ERR-03
*   **Mô tả:** Trong lúc Employee đang tạo PR bằng voice hoặc Procurement đang phân tích PDF báo giá, dịch vụ đám mây OpenAI/Gemini bị quá tải hoặc mất mạng internet [6].
*   **API kiểm chứng:** `POST /api/assistant/standardize-pr` [11], `POST /api/quotations/compare` [11]
*   **Expected Result:**
    *   Hệ thống kích hoạt cơ chế **Multi-Provider Fallback** trong vòng tối đa 3 giây [6, 7].
    *   Hệ thống chuyển sang sử dụng dịch vụ local dự phòng (**Local Deterministic Mock Service** dựa trên Regex Parser và PDF Plumber) [7].
    *   Xử lý bóc tách thành công dữ liệu thô dới 0.5 giây và phản hồi an toàn cho người dùng, đảm bảo quá trình demo Viva diễn ra 100% mượt mà không có lỗi [7].

---

## VII. DANH SÁCH CÁC AI FEATURE TEST CASES (KIỂM THỬ TÍNH NĂNG AI)

Kiểm thử đặc thù cho các tính năng AI để chứng minh năng lực bóc tách dữ liệu chính xác, xử lý các tình huống dữ liệu mờ, ngăn chặn lỗi bịa đặt (Hallucination) và thực thi đúng vai trò hỗ trợ quyết định (Decision Support) [170].

### **1. AI chuẩn hóa PR từ giọng nói (Voice PR Standardization)**
*   **TC-AI-01: Bóc tách thành công văn bản thô đầy đủ**
    *   *Input:* `"Cần mua 1 laptop Dell 25tr cho dev"` [11]
    *   *Expected Result:* Trả về JSON bóc tách khớp schema: Tên SP = "Laptop Dell", Số lượng = 1, Đơn giá = 25.000.000, Tổng giá = 25.000.000 [11].
*   **TC-AI-02: Bóc tách văn bản bị thiếu thông tin số lượng (Clarification State)**
    *   *Input:* `"Mua hộ vài cái máy in Canon gấp"`
    *   *Expected Result:* AI không được tự ý bịa số lượng (mặc định = 1) [23]. AI trả về mã trạng thái yêu cầu làm rõ (`CLARIFY`) [77], giao diện hiển thị câu hỏi tương tác: *"Hệ thống ghi nhận bạn muốn mua Máy in Canon, vui lòng bổ sung số lượng cụ thể cần mua?"* [14, 77]
*   **TC-AI-03: Nhập ký tự Unicode lạ và Emoji**
    *   *Input:* `"Mua 🚀 2 cái ghế xoay văn phòng giá 1.5M/cái nhé 👍"`
    *   *Expected Result:* AI xử lý mượt mà, tự động lọc bỏ emoji, trích xuất chính xác: Tên SP = "Ghế xoay văn phòng", Số lượng = 2, Đơn giá = 1.500.000.

### **2. AI trích xuất và đối chiếu báo giá PDF (PDF Quotation Extraction)**
*   **TC-AI-04: Trích xuất trọn vẹn dữ liệu từ báo giá PDF chuẩn**
    *   *Input:* Tải lên file PDF báo giá chứa thông tin của Supplier Phong Vũ [14].
    *   *Expected Result:* Trích xuất đúng 100% tên nhà cung cấp, danh mục vật tư, số lượng, đơn giá, thời gian bảo hành và giao hàng, không lệch một chữ số so với bản PDF gốc [174, 180].
*   **TC-AI-05: Chặn lỗi bịa đặt (Hallucination Prevention Guard)**
    *   *Input:* Tải lên một file PDF báo giá bị mờ nhòe phần Đơn giá sản phẩm, hoặc file văn bản rác không liên quan.
    *   *Expected Result:* AI **tuyệt đối không được tự đoán** hoặc tự sinh ra một đơn giá hợp lý [23]. AI phải trả về trạng thái lỗi bóc tách và yêu cầu người dùng: *"Không thể trích xuất đơn giá từ báo giá này. Vui lòng nhập thủ công giá trị hoặc tải lên file PDF rõ nét hơn."* [75]

### **3. AI phát hiện giá bất thường (Anomaly Alert)**
*   **TC-AI-06: Kích hoạt cảnh báo khi đơn giá tăng cao bất thường $\geq 20\%$**
    *   *Input:* Tải lên báo giá có đơn giá laptop Dell là 31.000.000 VND [14]. Đơn giá trung bình thu mua lịch sử lưu trong bảng `POItem` của thiết bị tương tự là 25.000.000 VND [14].
    *   *Tỷ lệ lệch tính toán:* $\frac{31.000.000 - 25.000.000}{25.000.000} = 24\% \ge 20\%$ [14].
    *   *Expected Result:* AI tự động phát hiện lệch giá, gắn cờ `isAnomaly = True` [171]. Trên giao diện hiển thị huy hiệu Badge đỏ cảnh báo nổi bật kèm Microcopy ghi rõ: *"CẢNH BÁO AI: Đơn giá 31.000.000đ/cái cao hơn 24% so với đơn giá trung bình lịch sử thu mua thiết bị tương tự (25.000.000đ)."* [14]
*   **TC-AI-07: Không cảnh báo khi đơn giá dao động trong mức cho phép ($< 20\%$)**
    *   *Input:* Báo giá laptop Dell là 27.000.000 VND. Giá lịch sử là 25.000.000 VND (Lệch 8% $< 20\%$).
    *   *Expected Result:* Hệ thống hiển thị bình thường, không gắn cờ bất thường, không hiển thị Badge cảnh báo nguy hiểm màu đỏ [13, 171].
*   **TC-AI-08: Đảm bảo quyền quyết định thuộc về con người (Human-in-the-loop)**
    *   *Input:* Báo giá của nhà cung cấp Phong Vũ bị gắn cờ cảnh báo bất thường giá cao hơn 24% [14].
    *   *Expected Result:* Mặc dù có cảnh báo bất thường màu đỏ, hệ thống **không được tự ý vô hiệu hóa** hoặc tự động loại bỏ báo giá này [208]. Nút chọn nhà cung cấp Phong Vũ vẫn khả dụng để Procurement có thể bấm chọn nếu nhà cung cấp này có các ưu thế khác vượt trội (như giao hàng ngay trong ngày hoặc bảo hành 5 năm) [208]. AI chỉ đóng vai trò hỗ trợ thông tin, không can thiệp vào quyền quyết định của con người [170, 173].

---

## VIII. GHI CHÚ CHƯA XÁC ĐỊNH (NEEDS CLARIFICATION & UNKNOWN)

Để đảm bảo tính trung thực tuyệt đối của hồ sơ kiểm thử, dưới đây là các điểm kỹ thuật hiện trạng mã nguồn hoặc tài liệu chưa xác định rõ nét:

1.  **Trạng thái chỉnh sửa PR:** Khi Manager yêu cầu chỉnh sửa PR (Request Revision), hệ thống chuyển PR sang trạng thái chính xác nào? (`REVISION_REQUESTED`, `DRAFT` hay quay về `PENDING_REVISION`?) $\rightarrow$ **NEEDS CLARIFICATION** (Cần kiểm tra file code router `/backend/app/routers/pr.py` hoặc hỏi Developer của nhóm để chốt nhãn trạng thái đồng nhất).
2.  **Đặc tả UI upload Quotation:** Màn hình upload Quotation được viết ở file frontend nào cụ thể? (`CollectQuotations.tsx` hay viết chung trong màn hình PR Detail?) $\rightarrow$ **NEEDS CLARIFICATION** (QA cần đối chiếu thực tế cấu trúc thư mục frontend của nhóm).
3.  **Tên file router Quotation:** API `/api/quotations/compare` được xử lý ở file backend nào? (`backend/app/routers/quotations.py` hay `backend/app/routers/compare.py`?) $\rightarrow$ **NEEDS CLARIFICATION** (QA cần kiểm tra cấu trúc router trong backend).
4.  **Cấu trúc JSON báo lỗi db:** Cấu trúc chi tiết của response khi gọi API `/api/health` gặp lỗi database là gì? $\rightarrow$ **NEEDS CLARIFICATION** (Cần mở file `backend/app/routers/health.py` hoặc file tương đương để lấy đúng cấu trúc JSON thực tế).
5.  **Cấu hình Hạn mức Ngân sách (Budget):** Hệ thống có giao diện UI để Admin hoặc Finance cấu hình hạn mức ngân sách phòng ban theo từng quý hay không, hay dữ liệu này hoàn toàn được Seed cứng bằng SQL/Migration dưới DB? $\rightarrow$ **NEEDS CLARIFICATION** (Theo requirements hiện tại, việc cấu hình Budget nằm ngoài phạm vi MVP nên khả năng cao là seed cứng dưới DB, tuy nhiên cần kiểm chứng thực tế).

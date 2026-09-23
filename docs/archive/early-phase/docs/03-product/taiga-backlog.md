# Taiga Backlog - ProcureAI

> **Status:** Draft backlog chi tiết theo Epic và User Story.
>
> **Nguồn ưu tiên:** Requirements và Business Rules đã xác nhận. Estimate, Assignee, Sprint và Status dưới đây là kế hoạch đề xuất để nhóm review.

## 1. Backlog conventions

| Trường | Quy ước |
|---|---|
| Epic | Nhóm năng lực sản phẩm, mã `E-01` đến `E-07`. |
| User Story | Story đã có trong `docs/03-product/user-stories.md`, mã `US-01` đến `US-10`. |
| Task | Đơn vị triển khai đề xuất, mã `T-01` đến `T-42`; không tạo Business Rule mới. |
| Priority | Lấy theo cột P trong Requirements; AI hỗ trợ giữ `Should` khi nguồn quy định `Should`. |
| Status | `Ready` khi story đủ source và acceptance criteria; `Planned` khi còn phụ thuộc hoặc cần policy. |
| Estimate | Story points đề xuất theo độ phức tạp: 3, 5 hoặc 8. |
| Primary Owner | Một người chịu trách nhiệm chính cho từng User Story; mỗi thành viên có ít nhất một story chính. |
| Assignee | Các thành viên phối hợp triển khai ngoài Primary Owner. |
| Sprint | Kế hoạch 4 sprint tuần tự theo dependency, cần nhóm xác nhận trước khi nhập Taiga. |

## 2. Epic and User Story Backlog

### E-01 - Purchase Request

**Goal:** Employee tạo PR hợp lệ, được hỗ trợ chuẩn hóa và theo dõi trạng thái.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| US-01 | Must | Là Employee, tôi muốn tạo PR với các trường bắt buộc để gửi yêu cầu hợp lệ. | Không thể Submit khi thiếu trường bắt buộc; PR hợp lệ được lưu và gửi vào workflow. | T-01 Thiết kế form PR; T-02 Kiểm tra trường bắt buộc; T-03 Submit PR và ghi trạng thái | REQ-FR-01, REQ-FR-02, REQ-BR-01 | 5 SP | Trần Thị Kiều Giang (Frontend) | Nguyễn Thị Thùy Dung (Backend) | Sprint 1 | Ready |
| US-02 | Must | Là Employee, tôi muốn theo dõi trạng thái PR để biết yêu cầu đang ở bước nào. | Trạng thái PR được hiển thị trong workflow; trạng thái phản ánh bước xử lý hiện tại. | T-04 Thiết kế trạng thái PR; T-05 Hiển thị timeline/status; T-06 Liên kết trạng thái với Audit Trail | REQ-FR-04, REQ-NFR-03 | 3 SP | Nguyễn Thị Thùy Dung (Backend) | Trần Thị Kiều Giang (Frontend) | Sprint 1 | Planned |
| US-03 | Should | Là Employee, tôi muốn review gợi ý AI để hoàn thiện mô tả PR. | AI chỉ gợi ý; Employee có thể xác nhận hoặc chỉnh sửa gợi ý trước Submit; không có AI tự Submit. | T-07 Hiển thị AI suggestion; T-08 Cho phép chỉnh sửa; T-09 Ghi nhận human review | REQ-FR-03, REQ-BR-01, CON-03 | 5 SP | Nguyễn Trúc Lam (AI Vault) | Nguyễn Thị Thùy Dung (Backend) + Trần Thị Kiều Giang (Frontend) | Sprint 1 | Planned |

### E-02 - Approval and Budget

**Goal:** Manager và Finance ra quyết định Approval có căn cứ, giữ đúng nhánh Budget.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| US-04 | Must | Là Manager, tôi muốn xem PR và Budget trước khi quyết định. | Manager xem được PR; có thể Approve, Reject, yêu cầu chỉnh sửa hoặc chuyển Finance; lý do Reject/chỉnh sửa/chuyển bước được ghi nhận. | T-10 Màn hình Manager Review; T-11 Các action Approval; T-12 Nhánh chuyển Finance; T-13 Ghi Audit Trail | REQ-FR-05, REQ-FR-06, REQ-FR-07, REQ-BR-03, REQ-BR-04 | 8 SP | Nguyễn Trương Thùy Dương (BA/PO) | Trần Thị Kiều Giang (Frontend) + Nguyễn Thị Thùy Dung (Backend) | Sprint 2 | Planned |
| US-05 | Must | Là Finance, tôi muốn kiểm tra PR với Budget để kiểm soát chi phí. | Finance kiểm tra PR với Budget trước khi hoàn tất phê duyệt có yêu cầu; PR vượt Budget hiển thị cảnh báo; quyết định không do AI thực hiện. | T-14 Hiển thị Budget Check; T-15 Cảnh báo vượt Budget; T-16 Finance Approval/Reject theo policy được xác nhận | REQ-FR-08, REQ-FR-09, REQ-BR-04, REQ-BR-05, ASM-02 | 5 SP | Nguyễn Trương Thùy Dương (BA/PO) | Nguyễn Thị Thùy Dung (Backend) | Sprint 2 | Planned - phụ thuộc policy Budget |

### E-03 - Supplier and Quotation

**Goal:** Procurement thu thập và liên kết dữ liệu báo giá để sẵn sàng so sánh.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| US-06 | Must | Là Procurement, tôi muốn liên kết nhiều Quotation với PR để so sánh. | Chỉ xử lý Quotation sau khi PR được Approve; mỗi Quotation được liên kết với PR tương ứng; dữ liệu nhiều Supplier hiển thị để so sánh. | T-17 Quản lý Supplier; T-18 Upload/lưu Quotation; T-19 Liên kết Quotation với PR; T-20 Chuẩn hóa dữ liệu so sánh | REQ-FR-10, REQ-FR-11, REQ-FR-12, REQ-BR-02, REQ-BR-06, REQ-BR-07 | 8 SP | Nguyễn Trương Thùy Dương (BA/PO) | Nguyễn Thị Thùy Dung (Backend) + Trần Thị Kiều Giang (Frontend) | Sprint 2 | Planned |

### E-04 - AI Quotation Comparison

**Goal:** Hỗ trợ Procurement trích xuất, so sánh và đánh giá báo giá nhưng vẫn giữ human-in-the-loop.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| US-07 | Must/Should | Là Procurement, tôi muốn review dữ liệu AI extraction để sửa lỗi trước khi chọn Supplier. | AI hỗ trợ phân tích và hiển thị so sánh; dữ liệu extraction có thể review/chỉnh sửa; Recommendation dựa trên tiêu chí Quotation; AI không tự chọn Supplier; cảnh báo giá bất thường theo ngưỡng `≥20%` khi có dữ liệu lịch sử. | T-21 Trích xuất PDF/Excel; T-22 Màn hình review dữ liệu gốc; T-23 Ma trận so sánh; T-24 Recommendation; T-25 Anomaly Alert và lý do đối sánh | REQ-FR-13, REQ-FR-14, REQ-FR-15, REQ-BR-08, REQ-BR-09, ASM-03, ASM-07 | 8 SP | Nguyễn Trúc Lam (AI Vault) | Nguyễn Thị Thùy Dung (Backend) + Trần Thị Kiều Giang (Frontend) | Sprint 3 | Planned - phụ thuộc dữ liệu mẫu |

### E-05 - Purchase Order

**Goal:** Procurement tạo PO đúng điều kiện sau Approval và Supplier Selection.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| US-08 | Must | Là Procurement, tôi muốn tạo PO từ PR đã duyệt và Supplier đã chọn. | PO không được tạo khi PR chưa Approve hoặc chưa chọn Supplier; PO liên kết với PR và Quotation/Supplier được chọn; AI không tự thay đổi dữ liệu đã chọn. | T-26 Tạo PO từ PR; T-27 Kiểm tra điều kiện Approval/Supplier; T-28 Lưu liên kết PO; T-29 Chặn thay đổi ngoài human review | REQ-FR-16, REQ-BR-10, ASM-04 | 5 SP | Nguyễn Thị Thùy Dung (Backend) | Trần Thị Kiều Giang (Frontend) + Nguyễn Trương Thùy Dương (BA/PO) | Sprint 3 | Planned |

### E-06 - Receiving and Close

**Goal:** Ghi nhận giao nhận thực tế và chỉ Close khi các bước liên quan hoàn tất.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| US-09 | Must | Là người có quyền, tôi muốn ghi nhận Receiving và sai lệch thực tế. | Receiving hỗ trợ nhận đủ, nhận một phần hoặc phát hiện sai lệch; người dùng có quyền mới được ghi nhận; tổng số lượng không vượt PO theo Assumption hiện tại. | T-30 Form Receiving; T-31 Trạng thái nhận đủ/một phần/sai lệch; T-32 Kiểm tra quyền; T-33 Kiểm tra số lượng theo ASM-06 | REQ-FR-17, ASM-06 | 5 SP | Nguyễn Thị Thùy Dung (Backend) | Trần Thị Kiều Giang (Frontend) | Sprint 4 | Planned |
| US-10 | Must | Là Finance, tôi muốn Close chỉ xảy ra sau khi Receiving hoàn tất. | PR chỉ Close sau Receiving và các bước mua sắm liên quan hoàn tất; dữ liệu PR, PO và Receiving phải có liên kết để đối soát; không tự động Close khi còn điều kiện chưa hoàn tất. | T-34 Đối soát PR-PO-Receiving; T-35 Điều kiện Close; T-36 Audit Trail khi Close | REQ-FR-18, REQ-BR-11, REQ-NFR-01 | 5 SP | Trần Thị Thu Hà (QA/Tester) | Nguyễn Trương Thùy Dương (BA/PO) + Nguyễn Thị Thùy Dung (Backend) | Sprint 4 | Planned - phụ thuộc Receiving |

### E-07 - Governance, RBAC and Audit Trail

**Goal:** Bảo vệ quyền truy cập, No Self-Approval và khả năng truy vết.

| Story | Priority | User Story | Acceptance Criteria | Tasks | Traceability | Estimate | Primary Owner | Assignee | Sprint | Status |
|---|---|---|---|---|---|---:|---|---|---|
| GOV-01 | Must | Là Admin, tôi muốn phân quyền 5 vai trò để người dùng chỉ thực hiện thao tác được cấp. | RBAC hỗ trợ Employee, Manager, Procurement, Finance và Admin; người tạo PR không thể tự Approve PR của mình. | T-37 Ma trận RBAC; T-38 Kiểm tra quyền theo action; T-39 Test No Self-Approval | REQ-NFR-02, CON-02, CON-03, Project Charter — No Self-Approval | 5 SP | Nguyễn Thị Thùy Dung (Backend) | Nguyễn Trúc Lam (AI Vault) + Trần Thị Thu Hà (QA/Tester) | Sprint 1 | Planned |
| GOV-02 | Must | Là Admin/QA, tôi muốn Audit Trail ghi nhận các thao tác quan trọng để truy vết. | Ghi nhận người thực hiện, thời điểm, action, thay đổi trạng thái và các quyết định Approval; mọi thay đổi phải có thể truy vết. | T-40 Audit event model; T-41 Ghi log Approval/Reject/Finance/AI review; T-42 Màn hình/lần truy vết Audit | REQ-NFR-03, Project Charter — Audit Trail | 5 SP | Trần Thị Thu Hà (QA/Tester) | Nguyễn Thị Thùy Dung (Backend) + Trần Thị Kiều Giang (Frontend) | Sprint 4 | Planned |

## 3. Epic Dependency Map

| Epic | Phụ thuộc |
|---|---|
| E-01 Purchase Request | Không |
| E-02 Approval and Budget | E-01 |
| E-03 Supplier and Quotation | E-02, chỉ sau khi PR được Approve |
| E-04 AI Quotation Comparison | E-03 |
| E-05 Purchase Order | E-02, E-03, E-04 và Supplier được chọn |
| E-06 Receiving and Close | E-05 |
| E-07 Governance | Xuyên suốt E-01 đến E-06 |

## 4. Planning Fields Pending

| Field | Status |
|---|---|
| Estimate | Đã gán sơ bộ theo story points; cần nhóm xác nhận trong estimation session. |
| Assignee | Đã gán owner chính theo phân công 5 thành viên; cần xác nhận capacity. |
| Sprint/Iteration | Đã đề xuất Sprint 1–4 theo dependency; cần xác nhận lịch thực tế. |
| Taiga issue ID | TBD - chưa tạo issue trên Taiga |
| Definition of Done | TBD - cần QA/Dev thống nhất |
| Số quotation tối thiểu trước Compare | Open Decision `DEC-005` |
| Approval threshold và policy Budget | Open Decision `DEC-006` |
| Nguồn dữ liệu lịch sử cho anomaly alert | Open Decision `DEC-007` |

## 5. Proposed Sprint Plan

| Sprint | Mục tiêu | Epic/Story chính | Vai trò dẫn dắt |
|---|---|---|---|
| Sprint 1 | Nền tảng PR, trạng thái và quyền truy cập | E-01: US-01, US-02, US-03; E-07: GOV-01 | Frontend + Backend |
| Sprint 2 | Approval, Budget và dữ liệu Quotation | E-02: US-04, US-05; E-03: US-06 | BA/PO + Backend |
| Sprint 3 | AI Comparison và tạo PO | E-04: US-07; E-05: US-08 | AI Vault + Backend + Frontend |
| Sprint 4 | Receiving, Close, Audit và verification | E-06: US-09, US-10; E-07: GOV-02 | Backend + QA |

## 6. Team Allocation

| Thành viên | Vai trò | Phạm vi backlog chính |
|---|---|---|
| Nguyễn Trương Thùy Dương | BA / PO | Scope, acceptance criteria, Approval/Budget, PO/Close decisions |
| Nguyễn Trúc Lam | AI Vault | AI PR/Quotation governance, citation, anomaly/recommendation constraints |
| Nguyễn Thị Thùy Dung | Backend Developer | Data model, REST/API, workflow state, Budget, PO, Receiving, Audit Trail |
| Trần Thị Kiều Giang | Frontend Developer | PR, Approval, Quotation, PO, Receiving UI và prototype flow |
| Trần Thị Thu Hà | QA / Tester | Acceptance review, RBAC tests, workflow tests, usability và verification |

## 7. Traceability Summary

- `US-01` đến `US-10` được phân bổ vào E-01 đến E-06.
- `GOV-01` và `GOV-02` bao phủ RBAC, No Self-Approval và Audit Trail thuộc E-07.
- Functional Requirements `REQ-FR-01` đến `REQ-FR-18` được tham chiếu trong các story tương ứng.
- NFR `REQ-NFR-01` đến `REQ-NFR-03` được bao phủ bởi US-02, US-10, GOV-01 và GOV-02.
- Các Assumption/Open Decision được đánh dấu riêng, không trình bày như Acceptance Criteria đã được chốt.

## 8. Primary Owner Coverage

| Thành viên | User Story chính | Epic | Trách nhiệm chính |
|---|---|---|---|
| Nguyễn Trương Thùy Dương (BA/PO) | `US-04` | E-02 Approval and Budget | Acceptance criteria, approval route và quyết định nghiệp vụ. |
| Nguyễn Trúc Lam (AI Vault) | `US-07` | E-04 AI Quotation Comparison | AI governance, extraction review, recommendation và anomaly constraints. |
| Nguyễn Thị Thùy Dung (Backend) | `US-08` | E-05 Purchase Order | API/data flow tạo PO và kiểm tra điều kiện nghiệp vụ. |
| Trần Thị Kiều Giang (Frontend) | `US-01` | E-01 Purchase Request | UI tạo PR, validation feedback và luồng Submit. |
| Trần Thị Thu Hà (QA/Tester) | `US-10` | E-06 Receiving and Close | Acceptance verification, đối soát Close và test evidence. |

> **Kiểm tra phân công:** 5/5 thành viên có ít nhất một User Story phụ trách chính. Các story còn lại có owner phối hợp trong cột `Assignee`.

# AI Usage Log

## Project
AI Procurement & Purchase Approval System

## Purpose

AI was used as a supporting tool during requirements analysis, workflow
design, architecture, implementation discussion, and review.

The project follows the principle:

> AI supports the team; humans make the final decisions.

---

# A-01 — Requirements Analysis

### Context
Nhóm cần xác định các vấn đề chính trong quy trình mua sắm nội bộ.

### AI Input
Phân tích quy trình:

Request → Approve → Collect Quotations → Compare → PO → Receive → Close

và xác định các vấn đề AI có thể hỗ trợ.

### AI Output
AI đề xuất các nhóm vấn đề:

- Purchase Request chưa được chuẩn hóa.
- Approval cần thông tin tập trung.
- So sánh Quotation còn thủ công.
- Cần kiểm soát Budget.
- Cần theo dõi trạng thái và lịch sử xử lý.

### Human Review
Nhóm đối chiếu các đề xuất với user research và scope của project.

### Human Decision
Giữ các vấn đề phù hợp với scope của hệ thống và không mở rộng
sang các chức năng ngoài MVP.

### Evidence
- `user-research.md`
- `research-synthesis.md`
- `requirements.md`

---

# A-02 — Requirement → User Story

### Context
Nhóm chuyển Requirement thành User Story và Acceptance Criteria.

### AI Input
Đề xuất User Story cho các actor:

- Employee
- Manager
- Procurement
- Finance

### AI Output
AI đề xuất các User Story liên quan đến:

- Tạo Purchase Request.
- Xem và xử lý Approval.
- Thu thập và so sánh Quotation.
- Kiểm tra Budget.
- Tạo Purchase Order.
- Receiving và Close.

### Human Review
Nhóm kiểm tra User Story với Requirements và Persona/JTBD.

### Human Decision
Chỉ giữ các User Story thuộc phạm vi MVP.

### Evidence
- `user-story.md`
- `requirements.md`
- `persona-jtbd.md`

---

# A-03 — US-01: Create Purchase Request

### Context
US-01 yêu cầu Employee tạo Purchase Request đầy đủ và được
chuẩn hóa.

### AI Input
Đề xuất workflow cho việc tạo Purchase Request.

### AI Output
AI đề xuất flow:

Employee creates PR
→ AI supports standardization
→ Validate information
→ Complete?
→ Submit PR

Nếu thông tin chưa đầy đủ, PR được đưa về bước chỉnh sửa.

### Human Review
Nhóm kiểm tra flow với Acceptance Criteria của US-01.

### Human Decision
Giữ AI ở vai trò hỗ trợ chuẩn hóa.
Employee vẫn chịu trách nhiệm về nội dung và việc Submit Purchase Request.

### Evidence
- `user-story.md`
- BPMN / workflow diagram
- `requirements.md`

---

# A-04 — US-03: Approval Workflow

### Context
US-03 yêu cầu Manager xem và xử lý Purchase Request.

### AI Input
Đề xuất implementation cho Approval Workflow.

### AI Output
AI đề xuất:

Manager reviews Purchase Request
→ Approval Decision
→ Approve / Reject / Request Revision

Sau quyết định, hệ thống ghi nhận trạng thái và chuyển PR
theo workflow.

### Human Review
Nhóm kiểm tra đề xuất với Acceptance Criteria:

- AC1 — Review PR
- AC2 — Approve
- AC3 — Reject / Request Revision
- AC4 — Approval Workflow

### Human Decision
Không cho AI tự đưa ra quyết định Approval.

Manager là người có thẩm quyền quyết định:

- Approve
- Reject
- Request Revision

Hệ thống chỉ ghi nhận quyết định và chuyển workflow.

### Evidence
- `user-story.md`
- `requirements.md`
- `architecture.md`
- BPMN / workflow diagram

---

# A-05 — US-04: Budget Control

### Context
Purchase Request cần được kiểm tra với Budget trước khi tiếp tục
quy trình mua sắm.

### AI Input
Đề xuất cách thể hiện Budget Check trong workflow.

### AI Output
AI đề xuất flow:

Purchase Request
→ Check Budget
→ Budget within limit?
→ Continue / Budget Alert

### Human Review
Nhóm kiểm tra logic với Business Rule về Budget.

### Human Decision
Budget Check được thực hiện trước khi Purchase Request tiếp tục
sang các bước mua sắm phù hợp.

AI có thể hỗ trợ phát hiện và cảnh báo bất thường nhưng không tự
quyết định thay Finance hoặc người có thẩm quyền.

### Evidence
- `business-rules.md`
- `requirements.md`
- BPMN / workflow

---

# A-06 — US-05: Quotation Comparison

### Context
Procurement phải thu thập và đối chiếu thông tin từ nhiều Quotation
trước khi lựa chọn Supplier.

### AI Input
Đề xuất cách sử dụng AI để hỗ trợ so sánh Quotation.

### AI Output
AI đề xuất:

Collect Quotations
→ Extract quotation information
→ Compare quotations
→ Provide recommendation
→ Procurement selects Supplier

### Human Review
Nhóm kiểm tra recommendation của AI với requirement:

> AI shall compare supplier quotations and provide a recommendation
> based on the available quotation information.

### Human Decision
AI chỉ đưa ra recommendation.

Procurement vẫn là người quyết định Supplier cuối cùng.

### Evidence
- `requirements.md`
- `user-story.md`
- `architecture.md`

---

# A-07 — Architecture Review

### Context
Nhóm cần thiết kế architecture phù hợp với scope của project.

### AI Input
Đề xuất module và cách phân chia responsibility.

### AI Output
AI đề xuất các module chính:

- Purchase Request Module
- Approval Workflow Module
- Budget Module
- Quotation / Supplier Module
- Purchase Order Module
- Receiving / Close Module
- AI Support Module

### Human Review
Nhóm kiểm tra khả năng triển khai và tránh over-engineering.

### Human Decision
Chỉ giữ các module cần thiết cho MVP.

AI được thiết kế như một supporting capability thay vì để AI
kiểm soát toàn bộ business workflow.

### Evidence
- `architecture.md`
- ADR

---

# A-08 — Workflow / BPMN Review

### Context
Nhóm cần kiểm tra BPMN end-to-end workflow.

### AI Input
Review workflow:

Request
→ Approve
→ Collect Quotations
→ Compare
→ PO
→ Receive
→ Close

### AI Output
AI hỗ trợ kiểm tra:

- Sequence Flow.
- Gateway.
- Các nhánh Approve / Reject / Request Revision.
- Luồng quay lại khi cần chỉnh sửa.
- Điểm kết thúc workflow.

### Human Review
Nhóm kiểm tra lại BPMN để tránh:

- Task bị lửng.
- Gateway không có flow vào.
- Sequence Flow sai.
- Nhánh workflow không có điểm kết thúc hoặc điểm quay lại rõ ràng.

### Human Decision
Nhóm chỉnh lại BPMN theo workflow nghiệp vụ thực tế.

### Evidence
- BPMN diagram
- `architecture.md`
- Workflow walkthrough

---

# A-09 — Architecture Trade-off Review

### Context
Nhóm cần giải thích một trade-off trong architecture.

### AI Input
Phân tích trade-off giữa tự động hóa Approval bằng AI và
human approval.

### AI Output
AI chỉ ra:

### Option 1
AI tự động Approval.

Ưu điểm:
- Tự động hóa cao.
- Giảm thao tác của Manager.

Nhược điểm:
- Rủi ro quyết định sai.
- Khó kiểm soát business decision.
- Không phù hợp với nguyên tắc human oversight.

### Option 2
AI hỗ trợ nhưng Manager quyết định.

Ưu điểm:
- Có human oversight.
- Manager kiểm soát quyết định.
- Phù hợp với scope và business process.

Nhược điểm:
- Vẫn cần Manager tham gia.
- Mức độ tự động hóa thấp hơn.

### Human Decision
Nhóm chọn:

> AI hỗ trợ, con người quyết định cuối.

### Decision
Không cho AI tự Approve hoặc Reject Purchase Request.

### Evidence
- `architecture.md`
- ADR
- `user-story.md`

---

# A-10 — Final Human Review

### Context
Review toàn bộ AI-generated suggestions trước khi hoàn thiện tài liệu.

### AI Input
Kiểm tra consistency giữa:

Requirements
→ User Stories
→ Acceptance Criteria
→ Tasks
→ Architecture
→ BPMN

### AI Output
AI hỗ trợ phát hiện các điểm có khả năng không nhất quán.

### Human Review
Nhóm kiểm tra lại từng điểm với tài liệu nguồn.

### Human Decision
Chỉ chấp nhận thay đổi sau khi nhóm xác nhận rằng thay đổi phù hợp
với requirement và scope.

### Final Principle

> AI output is a suggestion, not an authoritative decision.

Human team members remain responsible for the final requirements,
architecture, workflow, and implementation decisions.

### Evidence
- `requirements.md`
- `user-story.md`
- `architecture.md`
- BPMN
- ADR
- Backlog

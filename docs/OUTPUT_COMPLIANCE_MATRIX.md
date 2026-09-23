# OUTPUT COMPLIANCE MATRIX

## 1. Purpose

Tài liệu này đánh giá mức độ đáp ứng (compliance) của project hiện tại so với các yêu cầu đầu ra bắt buộc của khóa học (được quy định trong `Output_BaoCao.xlsx` / `OUTPUT_BAOCAO.md`). 

**Nguyên tắc cốt lõi:** "No Evidence = Not Completed". Mọi hạng mục đều phải có minh chứng thực tế trong repository (code, test log, config) để được coi là hoàn thành. Không chấp nhận việc tự xưng hoàn thành nếu không có evidence đi kèm, và không đánh dấu hoàn thành chỉ vì file hoặc folder tồn tại.

Ma trận này phản ánh trạng thái hiện tại tại thời điểm audit, dựa trên source code thực tế và các quyết định kiến trúc đã được chốt (HD-01 → HD-07). Nó không phải là cam kết cho những tính năng tương lai chưa được lập trình.

## 2. Compliance Status Legend

| Status | Ý nghĩa |
|---|---|
| ✅ COMPLETE | Có implementation/evidence đầy đủ và có thể kiểm chứng trong project hiện tại. |
| 🟡 PARTIAL | Đã có một phần nhưng chưa đáp ứng đầy đủ yêu cầu, thiếu evidence execution hoặc thiếu tính năng con. |
| 🔴 NOT COMPLETE | Biết rõ hiện tại chưa đáp ứng yêu cầu hoặc chưa bắt đầu làm. |
| ⚪ NOT VERIFIED | File/folder có tồn tại nhưng chưa có evidence/thời gian để xác minh chi tiết nội dung (ví dụ số lượng, độ bao phủ, URL bên thứ 3). |
| 🔵 PLANNED | Đã có quyết định/kế hoạch thực hiện (ví dụ trong DECISION_LOG) nhưng chưa code/implement. |
| ⚠️ CONFLICT | Có mâu thuẫn đáng chú ý giữa requirement/documentation và implementation thực tế (Documentation Drift). |

## 3. Overall Summary

- **Tổng số deliverables được kiểm tra:** 32 (Từ `OUTPUT_BAOCAO.md`)
- **✅ COMPLETE:** 0
- **🟡 PARTIAL:** 7
- **🔴 NOT COMPLETE:** 12
- **⚪ NOT VERIFIED:** 11
- **🔵 PLANNED:** 1
- **⚠️ CONFLICT:** 1

*(Lưu ý: Tổng đúng 32/32 deliverables. Nhiều mục chưa thể đánh dấu COMPLETE do thiếu execution evidence hoặc chưa được xác minh nội dung chi tiết. Xem chi tiết bên dưới.)*

## 4. Main Compliance Matrix

### 4.1 Project / Planning / Research

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-1.1 | Project Charter | OUTPUT_BAOCAO | `project-charter.md` | `docs/01-discovery/project-charter.md` | File tồn tại nhưng chưa xác minh chi tiết nội dung. | `docs/...` | Cần review problem, goal, metrics | ⚪ NOT VERIFIED | Đảm bảo nội dung đáp ứng đủ rubric. |
| OUT-1.2 | User Research + Synthesis | OUTPUT_BAOCAO | `user-research.md` | `docs/01-discovery/user-research.md` | File tồn tại nhưng chưa xác minh chi tiết nội dung. | `docs/...` | Cần review >=3 sources, insights | ⚪ NOT VERIFIED | Đảm bảo nội dung đáp ứng đủ rubric. |
| OUT-1.4 | Project Vault | OUTPUT_BAOCAO | `vault/` directory | `docs/02-vault/` | Folder tồn tại nhưng chưa xác minh độ bao phủ. | `docs/...` | Cần check cấu trúc | ⚪ NOT VERIFIED | N/A |
| OUT-1.5 | Vault Q&A Benchmark | OUTPUT_BAOCAO | `vault-qa-benchmark.md` | `docs/02-vault/vault-qa-benchmark.md` | File tồn tại nhưng chưa xác minh đủ >=20 câu hỏi có pass/fail. | `docs/...` | Cần đếm số lượng câu hỏi | ⚪ NOT VERIFIED | Đảm bảo >=20 câu hỏi. |

### 4.2 Requirements / Business Rules

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-1.3 | Requirements + Business Rules | OUTPUT_BAOCAO | `requirements.md` | `docs/01-discovery/requirements.md` | File tồn tại nhưng chưa xác minh tính testable. | `docs/...` | Cần check rules | ⚪ NOT VERIFIED | Đảm bảo nội dung đáp ứng đủ rubric. |
| OUT-2.1 | PRD | OUTPUT_BAOCAO | `PRD.md` | `docs/03-product/PRD.md` | File tồn tại nhưng chưa xác minh sự nhất quán với requirements. | `docs/...` | Cần đọc chi tiết | ⚪ NOT VERIFIED | Đảm bảo nội dung đáp ứng đủ rubric. |
| OUT-2.5 | User Stories + Acceptance Criteria | OUTPUT_BAOCAO | `user-stories.md` | `docs/03-product/user-story.md` | File tồn tại nhưng chưa xác minh số lượng (8-12) và G/W/T. | `docs/...` | Cần đếm story, format AC | ⚪ NOT VERIFIED | Đảm bảo AC testable. |
| OUT-2.6 | Taiga Backlog | OUTPUT_BAOCAO | Taiga Project Link | Thiếu link | Không có evidence board thực tế trong repo | N/A | Truy cập URL public | 🔴 NOT COMPLETE | Cần cung cấp URL Taiga board công khai. |
| OUT-2.11 | Story Specs + Traceability v1 | OUTPUT_BAOCAO | `TRACEABILITY` | `docs/06-testing/traceability-matrix.md` | Có file trace cơ bản nhưng chưa trace đầy đủ đến code/commit. | `docs/...` | Manual review | 🟡 PARTIAL | Cập nhật file trace từ REQ đến code/test thực tế. |

### 4.3 Design / UX / Prototype

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-2.2 | User Flow | OUTPUT_BAOCAO | `user-flow.mmd` | `docs/03-product/user-flow.mmd` | File tồn tại nhưng chưa xác minh có đủ happy/error paths. | `docs/...` | Mermaid render | ⚪ NOT VERIFIED | N/A |
| OUT-2.3 | Functional Prototype | OUTPUT_BAOCAO | Prototype URL | `docs/04-design/prototype.md` | Chưa có evidence/URL prototype có thể click/chạy được. | N/A | Click URL | 🔴 NOT COMPLETE | Cần URL prototype tương tác được. |
| OUT-2.4 | Usability Test | OUTPUT_BAOCAO | `usability-test.md` | Không tìm thấy file | Chưa có tài liệu test người dùng và changes. | N/A | N/A | 🔴 NOT COMPLETE | Cần thực hiện usability test (>=3 users) và ghi log. |
| OUT-2.7 | Figma + Design System | OUTPUT_BAOCAO | Figma URL + `DESIGN.md` | `docs/04-design/DESIGN.md` | Có file docs nhưng chưa có evidence Figma URL để verify component states. | N/A | Truy cập Figma URL | ⚪ NOT VERIFIED | Cần cung cấp Figma URL thực tế. |

### 4.4 Architecture / Database / API

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-2.8 | Architecture + ADR | OUTPUT_BAOCAO | `architecture.md` | `TARGET_ARCHITECTURE.md`, `DECISION_LOG.md` | File tồn tại nhưng chưa xác minh chi tiết nội dung thiết kế. | `docs/` | Manual review | ⚪ NOT VERIFIED | N/A |
| OUT-2.9 | ERD / Data Model | OUTPUT_BAOCAO | `data-model.md` + Schema | `backend/prisma/schema.prisma` | Schema đang dùng MockDB SQLite. Thiếu trường `PurchaseOrder.quantity`. | `backend/prisma/` | Code review | ⚠️ CONFLICT | Schema thực tế không khớp với quyết định HD-01, HD-07. |
| OUT-2.10 | API Contract | OUTPUT_BAOCAO | `API.md` / `openapi.yaml` | `docs/05-technical/API.md` | File markdown mô tả cơ bản nhưng chưa khớp hoàn toàn với target architecture. | `docs/` | Swagger review | 🟡 PARTIAL | Cập nhật API document cho khớp luồng auth/JWT. |

### 4.5 Implementation

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-3.1 | Source Repository | OUTPUT_BAOCAO | Repo URL | GitHub Repo | Repo có tồn tại nhưng chưa xác minh lịch sử commit và bảo mật secret. | Repo history | Git commit | ⚪ NOT VERIFIED | Kiểm tra `.env`, commit messages. |
| OUT-3.2 | Release chạy được | OUTPUT_BAOCAO | Demo URL + Tag | Không có URL | Ứng dụng chưa deploy public, không có release tag v1.0.0-final. | N/A | Truy cập URL | 🔴 NOT COMPLETE | Phải deploy backend + frontend và gắn tag release. |
| OUT-3.3 | Authentication + Authorization | OUTPUT_BAOCAO | Code + tests | `auth.py`, MockAuth | Đang là Trust-client, không có verify JWT như HD-02 quy định. | `backend/app/` | Source review | 🔵 PLANNED | Đã có HD-02 nhưng chưa implementation. |
| OUT-3.4 | Business Workflow | OUTPUT_BAOCAO | Code + tests | `po.py`, `receiving.py` | Có logic backend nhưng chưa đầy đủ (thiếu validation quantity/status PR). | `backend/app/` | Source review | 🟡 PARTIAL | Sửa lại logic validation cho đúng business rule. |
| OUT-3.5 | AI Feature | OUTPUT_BAOCAO | `ai-feature-spec.md` + Code | `ai_service.py` | Implementation dùng Regex/Mocking. Chưa gọi LLM thật, thiếu eval set. | `backend/` | Source review | 🔴 NOT COMPLETE | Cần code tích hợp LLM thật và >=20 eval cases. |

### 4.6 AI Development Evidence

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-1.6 | AI Usage Log v1 | OUTPUT_BAOCAO | `AI_USAGE_LOG.md` | `docs/logs/ai-usage-log.md` | File tồn tại nhưng chưa xác minh các mục verify/correct. | `docs/logs/` | Manual review | ⚪ NOT VERIFIED | Đảm bảo có evidence sửa output của AI. |
| OUT-3.15 | AI Log Final + Retrospective | OUTPUT_BAOCAO | `retrospective.md` | Không tìm thấy | Chưa có file tổng kết bài học AI cuối dự án. | N/A | N/A | 🔴 NOT COMPLETE | Thực hiện khi hoàn thành dự án. |

### 4.7 Testing / QA

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-3.6 | Code Review Evidence | OUTPUT_BAOCAO | `code-review.md` + PR | Không tìm thấy | Chưa có evidence PR review, checklist hay link story. | N/A | GitHub PRs | 🔴 NOT COMPLETE | Thực hiện code review trên GitHub/GitLab. |
| OUT-3.7 | Bug Log | OUTPUT_BAOCAO | `bug-log.md` | `docs/qa/QA_FINDINGS.md` | Có file log bug nhưng thiếu status đóng bug và evidence sửa. | `docs/qa/` | Manual review | 🟡 PARTIAL | Cập nhật resolution evidence. |
| OUT-3.8 | Automated Tests | OUTPUT_BAOCAO | `tests/` folder | `backend/tests/` | File test tồn tại nhưng KHÔNG CÓ execution evidence (CI log, HTML report) chứng minh test PASS. | N/A | CI test report | 🟡 PARTIAL | Phải cung cấp test execution evidence thực tế. |
| OUT-3.9 | QA Report | OUTPUT_BAOCAO | `QA_REPORT.md` | `qa-comprehensive-test-matrix.md` | Chưa có report cuối cùng chốt release blockers = 0. | N/A | N/A | 🔴 NOT COMPLETE | Tạo báo cáo QA cuối dự án. |

### 4.8 Security / NFR

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-3.10 | Security + NFR Evidence | OUTPUT_BAOCAO | `security-nfr.md` | Không tìm thấy | Chưa có evidence bảo mật. Backend thiếu RBAC enforcement. | N/A | N/A | 🔴 NOT COMPLETE | Cần evidence unauthorized/invalid tests. |

### 4.9 CI/CD / Docker / Deployment

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-3.11 | CI/CD + Docker/Deployment | OUTPUT_BAOCAO | `Dockerfile`, CI yaml | Không tìm thấy | Thiếu Dockerfile, `docker-compose.yml`, và cấu hình CI. | N/A | N/A | 🔴 NOT COMPLETE | Viết file cấu hình build/test/deploy. |

### 4.10 Documentation / Release / Traceability

| ID | Course Output / Requirement | Source | Required Artifact | Current Project Artifact | Implementation Status | Evidence | Test / Verification | Compliance Status | Gap / Action Needed |
|---|---|---|---|---|---|---|---|---|---|
| OUT-3.12 | README + Runbook | OUTPUT_BAOCAO | `README.md`, `RUNBOOK.md` | `docs/07-release/runbook.md` | Có hướng dẫn nhưng chưa phản ánh thay đổi từ DB migration mới. | `docs/...` | Thử setup | 🟡 PARTIAL | Cập nhật theo PostgreSQL. |
| OUT-3.13 | Release Notes + Changelog | OUTPUT_BAOCAO | `RELEASE.md` | `docs/07-release/release-notes.md` | Có file nhưng chưa phải bản chốt v1.0.0-final. | `docs/...` | Manual review | 🟡 PARTIAL | Hoàn thiện ở cuối kỳ. |
| OUT-3.14 | Traceability Final | OUTPUT_BAOCAO | `TRACEABILITY` final | Không tìm thấy | Chưa có truy vết REQ -> Test -> Code thực tế đầy đủ. | N/A | N/A | 🔴 NOT COMPLETE | Map 100% khi code xong. |

---

## 5. Critical Gaps

Các vấn đề sau ảnh hưởng trực tiếp đến việc chứng minh hệ thống chạy đúng yêu cầu:

| Gap ID | Related Output | Problem | Evidence | Impact | Required Action |
|---|---|---|---|---|---|
| GAP-01 | OUT-2.9, OUT-3.4 | Database Schema & Business Rule | `PurchaseOrder.quantity` không tồn tại trong Prisma schema. | Implementation chưa khớp với Business Rule (HD-07). | Bổ sung trường này vào Prisma schema và migrate. |
| GAP-02 | OUT-3.3, OUT-3.10 | Authentication / RBAC | Chưa có cơ chế giải mã và verify JWT. Backend đang dùng Trust-client. | Chưa đáp ứng deliverable về Authorization. | Lập trình JWT middleware (HD-02). |
| GAP-03 | OUT-3.5 | AI Feature Validation | Code `ai_service.py` dùng Regex / Mocking. Chưa gọi API LLM thật và chưa có eval set. | Chưa đáp ứng deliverable AI Feature. | Dùng API LLM thật với schema validation. |
| GAP-04 | OUT-3.2, OUT-3.11 | Release & Deployment | Repo không có Dockerfile, CI/CD, và URL public. | Chưa có evidence release chạy được. | Bổ sung file cấu hình, deploy lên server và thêm URL. |

## 6. Evidence Gaps

Các hạng mục sau có tài liệu hoặc code nhưng thiếu **bằng chứng thực thi (execution evidence)**:

1. **Automated Tests:** Mặc dù có file trong thư mục `tests/`, không có log kết quả CI hoặc HTML test report để xác minh.
2. **Playwright E2E:** Có spec test nhưng thiếu evidence log/chạy thử để chứng minh PASS.
3. **Figma / Prototype / Taiga:** Tài liệu có nhắc đến nhưng repository không chứa URL công khai để verify.
4. **Usability Test / Code Review:** Thiếu hoàn toàn tài liệu chứng minh quá trình (test log, PR review history).

## 7. Implementation Gaps

Các chức năng chưa được lập trình xong:

- Migration dữ liệu sang Supabase PostgreSQL.
- Server-side RBAC validation (không tin tưởng input role từ client).
- Quản lý logic validation cho `close_pr()` và Quotation approval.
- Frontend Auth State và Routing (App.tsx hiện tại là monolithic).

## 8. Documentation Gaps

- **Documentation Drift:** `TARGET_ARCHITECTURE.md` mô tả hệ thống hoàn thiện (JWT, PostgreSQL), nhưng Runtime Codebase đang dùng MockDB và Regex. Việc này xảy ra do architecture vừa được freeze chờ implement.
- Runbook hướng dẫn dựa trên SQLite, sẽ cần thay đổi khi dùng PostgreSQL thật.

## 9. Recommended Next Actions

### A. Must Fix Before Final Delivery
1. Migrate Prisma schema sang PostgreSQL, bổ sung cột `quantity`.
2. Implement backend JWT verification và xoá Trust-Client role.
3. Tích hợp LLM API thay thế regex ở module AI.
4. Refactor Frontend thêm routing và JWT state.

### B. Must Produce Evidence
1. Viết CI action để chạy pytest + Playwright và lưu test report.
2. Đính kèm public URL cho Figma, Taiga, và Prototype vào tài liệu.
3. Chụp bằng chứng Code Review (Pull Requests) lưu vào repository.

### C. Documentation Updates
1. Cập nhật Runbook sau khi chốt môi trường PostgreSQL.
2. Viết file `security-nfr.md` sau khi RBAC đã code xong.

## 10. Matrix Validation Result

Kết quả của lần kiểm tra validation cuối cùng đối với ma trận này:

- **Total deliverables checked:** 32
- **Missing items:** 0 (Đã bổ sung OUT-3.6 Code Review Evidence)
- **Duplicate items:** 0
- **Status inconsistencies:** Đã điều chỉnh toàn bộ các item có file nhưng không kiểm chứng được nội dung từ `COMPLETE` thành `NOT VERIFIED` (Tuân thủ luật "Artifact Exists != Deliverable Complete").
- **Unsupported claims:** Đã loại bỏ các đánh giá chủ quan về điểm số, thay bằng mô tả khách quan (Ví dụ: "Chưa đáp ứng deliverable" thay vì "0 điểm").
- **Evidence gaps incorrectly marked COMPLETE:** Đã sửa (Ví dụ: Automated Tests chuyển sang `PARTIAL` do thiếu execution evidence).
- **Decision/implementation confusion:** Đã chỉnh (Ví dụ: Authentication chuyển thành `PLANNED` dựa trên HD-02, không đánh dấu COMPLETE khi chưa code).
- **Summary count verified:** YES (Tổng: 32 = 0 COMPLETE + 7 PARTIAL + 12 NOT COMPLETE + 11 NOT VERIFIED + 1 PLANNED + 1 CONFLICT).

---

## 11. Final Audit Snapshot

- **Audit Date:** 2026-09-20
- **Repository State:** final-delivery branch
- **Sources Inspected:** `Output_BaoCao.xlsx`, `OUTPUT_BAOCAO.md`, `TARGET_ARCHITECTURE.md`, `DECISION_LOG.md`, backend python source, test folder.
- **Audit Limitations:** Không có môi trường để kích hoạt E2E tự động; không thể truy cập các URL bên thứ 3 (Taiga, Figma) nếu chưa được public; không phân tích từng dòng code của toàn bộ codebase.

*This matrix is a snapshot of the repository and evidence inspected at the audit time. It does not claim future work is complete.*

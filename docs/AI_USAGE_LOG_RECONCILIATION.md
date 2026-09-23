# AI USAGE LOG RECONCILIATION REPORT

**Ngày thực hiện:** 2026-09-23<br>
**Dự án:** AI Procurement & Purchase Approval System (Group 01)<br>
**Tài liệu hiện hành (Current):** `docs/logs/ai-usage-log.md` (53 entries: AI-001 đến AI-053)<br>
**Tài liệu nhập khẩu (Import):** `_IMPORT_EARLY_PHASE/group-01/docs/02-vault/AI_USAGE_LOG.md` (38 entries: AI-001 đến AI-038)<br>
**Bản tóm tắt cũ trong Vault:** `docs/02-vault/AI Usage Log.md` (10 entries tóm tắt sơ khai dạng A-01..A-10)

---

## 1. Nguyên tắc quản trị AI Log (AI Governance)

1. **Bảo toàn nguyên bản (Strict Preservation):** Toàn bộ nội dung prompt, người thực hiện, ngữ cảnh đầu vào, kết quả AI, quy trình rà soát và lịch sử sửa lỗi trong file import PHẢI ĐƯỢC GIỮ NGUYÊN 100%. Không tóm tắt, không viết lại, không paraphrase, không bịa đặt prompt hay timestamp.
2. **Minh bạch phân loại bằng chứng:**
   - **`DIRECT EVIDENCE`**: Nhật ký được ghi nhận trực tiếp từ quá trình làm việc thực tế với AI (cả Early Phase và Final Delivery Phase).
   - **`RETROSPECTIVE`**: Bản ghi hồi cứu có căn cứ dựa trên artifact còn lại, không phải prompt trực tiếp.
   - **`UNKNOWN / MISSING ORIGINAL AI EVIDENCE`**: Khi không còn dấu vết hoặc prompt thực tế, tuyệt đối không tự bịa đặt.
3. **Giải quyết xung đột mã định danh (ID Collision Resolution):** Không ghi đè làm mất mát lịch sử của một trong hai giai đoạn. Hai tập log đại diện cho hai giai đoạn độc lập được phân định ranh giới rõ ràng.

---

## 2. Phân tích đối chiếu giữa Current và Import Log

### A. Nhóm Entry đồng nhất (Duplicate / Shared Baseline: AI-001 đến AI-004)
Cả hai tập tài liệu đều ghi nhận 4 hoạt động đầu tiên của giai đoạn phân tích nghiệp vụ ban đầu:

| Entry ID | Tác vụ | Thành viên | Mức độ tương đồng | Bằng chứng đối chiếu | Quyết định xử lý |
|:---:|---|---|:---:|---|---|
| **AI-001** | Xây dựng Project Charter | Nguyễn Trương Thùy Dương (BA/PO) | 100% Khớp | `docs/01-discovery/1.project-charter.md`, Metrics 85%/80%/75% | Giữ nguyên bản đầy đủ, không duplicate |
| **AI-002** | Tổng hợp User Research & Evidence | Nguyễn Trúc Lam (AI Vault) | 100% Khớp | `docs/01-discovery/2.user-research.md`, 8 Evidence E-01..E-08 | Giữ nguyên bản đầy đủ, không duplicate |
| **AI-003** | Chuẩn hóa User Research theo mẫu | Nguyễn Trương Thùy Dương (BA/PO) | 100% Khớp | Báo cáo 11 mục, câu hỏi phỏng vấn Q1-Q5 | Giữ nguyên bản đầy đủ, không duplicate |
| **AI-004** | Xây dựng Requirement Inventory | Nguyễn Trương Thùy Dương (BA/PO) | 100% Khớp | `requirements.md` (FR-01..18, BR-01..11) | Giữ nguyên bản đầy đủ, không duplicate |

*Đánh giá:* **DIRECT EVIDENCE**. Cả hai bản đều thống nhất 100%.

---

### B. Nhóm Xung đột mã định danh (ID Collision: AI-005 đến AI-038)
Đây là điểm mâu thuẫn quan trọng nhất được phát hiện:

| Mã ID | Bản ghi trong IMPORT LOG (`_IMPORT_EARLY_PHASE`) | Bản ghi trong CURRENT LOG (`docs/logs/ai-usage-log.md`) | Bản chất khác biệt |
|:---:|---|---|---|
| **AI-005** | Chốt rủi ro Persona/JTBD & MVP Scope (Dương) | System Audit & Baseline Generation (Hà) | Early Discovery vs Final Delivery Audit |
| **AI-006** | Tạo và lưu tài liệu MVP Scope (Dương) | Final Development Plan Generation (Dương) | MVP Scope vs Final Development Plan |
| **AI-007** | Tạo README.md dự án (Dương) | Git Init, Branching & Push (Giang) | Project Introduction vs Git Repository Setup |
| **AI-008** | Tạo docs/00-project-index.md (Dương) | Phân tích Figma Prototype & tạo Spec (Dung) | Documentation Index vs UI/UX Figma Analysis |
| **AI-009** | Chuẩn hóa 4.glossary.md (Dương) | Cross-Source Validation (Hà) | Glossary vs Cross-Source Validation |
| **AI-010** | Chuẩn hóa 5.requirements.md (Dương) | Tạo Human Decision Brief (Dương) | Requirements Rename vs HD Brief Generation |
| **AI-011** | Chuẩn hóa 6.business-rules.md (Dương) | Curriculum-Aligned HD Review (Hà) | Business Rules Rename vs Syllabus Review |
| **AI-012** | Chuẩn hóa 7.MVP-Scope.md (Dương) | Finalize Architecture & Decision Log (Group) | MVP Scope Rename vs Target Architecture |
| **AI-013..019** | Xây dựng Vault Index, Workflows, Decision Log, QA Benchmark & Prompt (Lam, Hà) | Kiến trúc Backend, Setup Virtualenv, Hatchling build fix (Giang) | Vault Governance vs Backend Environment Setup |
| **AI-020..025** | Xây dựng PRD, Epics, Prototype Brief, User Flow, User Stories, Taiga Backlog (Dương, Giang, Hà) | Prisma Generator Python, Decimal flag, Supabase Connection, Push DB (Giang) | Product & Backlog vs Database Schema Synchronization |
| **AI-026..028** | Xây dựng Usability Test Script, Usability Findings, Prototype README (Hà, Giang) | US-09 Backend Core Fix BUG-001, Server Quotation Resolution, HD-08 T-094 Gap Brief (Hà, Giang) | Usability Design vs Business Rules Fix & T-094 Gap Brief |
| **AI-029..035** | Xây dựng Placeholders cho Design, Tech, Test, Release, Logs, gitkeep (Dung, Hà, Giang) | Đồng bộ Quotation.quantity lên Supabase, Lưu trữ/truy xuất quantity, Test maintenance, Khóa số lượng PO.quantity (Giang, Hà) | Early Scaffolding vs T-094 Server-Side Quantity Lock |
| **AI-036..038** | Xây dựng Vault QA Benchmark 22 câu, Prompt System, Budget Check Q&A (Hà, Lam) | TASK-003 Step 0 Read-Only Audit MockDB, Step 1 Shared Prisma Client, Step 2A Seed Data Audit (Giang, Hà) | Vault Q&A System vs TASK-003 Database Migration Steps |

*Phân tích nguyên nhân:*
- Khi bắt đầu giai đoạn Final Delivery (`final-delivery` branch), nhóm đã tái sử dụng file log bắt đầu từ `AI-005` để ghi lại toàn bộ hành trình triển khai kỹ thuật từ Audit, Plan, Setup DB đến Code Backend.
- Trong khi đó, nhóm làm lại giai đoạn đầu đã hoàn thành và chi tiết hóa 38 entries của toàn bộ giai đoạn Discovery và Vault cũng với dải mã `AI-001` đến `AI-038`.
- Cả hai tập log đều là **DIRECT EVIDENCE** hợp lệ của từng giai đoạn tương ứng.

*Phương án giải quyết chuẩn mực:*
1. **Tuyệt đối KHÔNG ghi đè** `docs/logs/ai-usage-log.md` bằng log import, vì sẽ làm mất toàn bộ 53 entries minh chứng của giai đoạn Final Delivery (gồm cả bằng chứng của TASK-001, TASK-002, T-094, TASK-003 Steps 3B.1 đến 3B.7).
2. **Khôi phục nguyên bản 100%** log của Early Phase vào đúng vị trí của nó: `docs/02-vault/AI_USAGE_LOG.md` (thay thế bản tóm tắt sơ khai `AI Usage Log.md` 8KB bằng bản đầy đủ 24.7KB).
3. Tại `docs/logs/ai-usage-log.md`, giữ nguyên vẹn 53 entries của Final Delivery và bổ sung phần ghi chú liên kết (Cross-Reference) dẫn tới `docs/02-vault/AI_USAGE_LOG.md` cho 38 entries của Early Phase.

---

### C. Đánh giá tính xác thực (Authenticity Assessment)

| Tập Log | Nguồn gốc | Đánh giá | Trạng thái xác thực |
|---|---|---|:---:|
| **Early Phase Log (AI-001..038)** | `_IMPORT_EARLY_PHASE/group-01/docs/02-vault/AI_USAGE_LOG.md` | Có đầy đủ 38 prompts, context đầu vào, kết quả AI, verification và lịch sử chỉnh sửa lỗi (Section 3). | **DIRECT EVIDENCE — 100% VALID** |
| **Final Delivery Log (AI-001..053)** | `docs/logs/ai-usage-log.md` | Có đầy đủ 53 sessions, đối chiếu commit Git, terminal outputs, pytest logs và Supabase queries. | **DIRECT EVIDENCE — 100% VALID** |
| **Vault Log sơ khai cũ (A-01..A-10)** | `docs/02-vault/AI Usage Log.md` (cũ) | Bản tóm tắt dạng tóm lược, thiếu prompt chi tiết và thiếu bảng lỗi AI. | **RETROSPECTIVE / SUPERSEDED** |

---

## 3. Kết luận và Kế hoạch thực thi

1. **Khôi phục:** Khôi phục `docs/02-vault/AI_USAGE_LOG.md` với đầy đủ 38 entries gốc và toàn bộ phần Error History / Corrections.
2. **Bảo toàn:** Giữ nguyên vẹn toàn bộ 53 entries trong `docs/logs/ai-usage-log.md`.
3. **Minh bạch:** Không thay đổi bất kỳ prompt hay timestamp nào của cả hai bản ghi.

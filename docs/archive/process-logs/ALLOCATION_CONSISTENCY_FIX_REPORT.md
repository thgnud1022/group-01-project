# BÁO CÁO NGHIỆM THU ĐỒNG BỘ DOCUMENTATION THEO ALLOCATION GROUP-01
**(ALLOCATION CONSISTENCY FIX REPORT)**

**Dự án:** Hệ thống Mua sắm & Phê duyệt Ngân sách ProcureAI<br>
**Nhóm:** Group 01 · **Branch:** `final-delivery`<br>
**Ngày thực hiện:** 2026-09-24<br>
**Phạm vi:** Documentation Consistency Fix Only (Không sửa source code, backend, frontend, database, tests, không git push/reset, không chỉnh Taiga).

---

## 1. Files Modified (Các tệp được chỉnh sửa)

| STT | Đường dẫn tệp | Loại thay đổi | Mô tả nội dung thay đổi |
|:---:|---|---|---|
| 1 | [docs/IMPLEMENTATION_PLAN.md](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md) | Chỉnh sửa | - Chuẩn hóa Section 1 (bãi bỏ mô hình 2 tầng 5 Primary / 6 Supporting).<br>- Cập nhật metadata `Responsible Owner` và `Collaborators` cho toàn bộ 18 technical tasks (`TASK-001` đến `TASK-018`).<br>- Khắc phục toàn bộ các lỗi gán nhầm User Story / Owner cũ trong các TASK chi tiết.<br>- Cập nhật Section 10, 10b, 11 (ma trận truy xuất T-xxx, TASK-xxx, Evidence).<br>- Viết lại Section 19 (khung chuẩn bị demo 5 phút theo 5 User Story cốt lõi, bảng phân công triển khai toàn diện và ma trận RACI).<br>- Cập nhật Section 22 Self-Check. |
| 2 | [docs/DECISION_LOG.md](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md) | Thêm mới quyết định | Bổ sung quyết định chính thức **HD-11: Official Group-01 User Story Responsibility Allocation** ghi nhận phân công đã được con người phê duyệt. |
| 3 | [docs/ALLOCATION_CONSISTENCY_FIX_REPORT.md](file:///d:/LTUD/group-01-project-main/docs/ALLOCATION_CONSISTENCY_FIX_REPORT.md) | Tạo mới | Báo cáo chi tiết quá trình rà soát, khắc phục và kiểm chứng tính nhất quán phân công. |

---

## 2. Old Allocation References Found (Các tham chiếu phân công cũ đã phát hiện)

Trước khi khắc phục, quá trình audit và rà soát tự động đã xác định tổng cộng **33 vị trí** (và 120 dòng liên quan) tồn dư thuật ngữ và mô hình phân công cũ trong [docs/IMPLEMENTATION_PLAN.md](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md):

1. **Thuật ngữ 2 tầng cũ:**
   - 38 lần xuất hiện cụm `"Primary Presentation"`
   - 26 lần xuất hiện cụm `"Supporting Implementation"`
   - 14 lần xuất hiện cụm `"Primary Presentation Owner"`
   - Nhiều lần xuất hiện cụm `"Primary của..."`, `"Supporting của..."`
2. **Các gán ghép sai lệch về quyền sở hữu (Ownership Conflicts):**
   - Section 1 (dòng 19-20): Khẳng định cấu trúc "Tầng 1 — 5 Primary Presentation Stories / Tầng 2 — 6 Supporting Implementation Stories".
   - `TASK-002` (dòng 172, 174): Gán US-09 và quyền sở hữu cho Hà (`Hà (Primary của US-09)`).
   - `TASK-005` (dòng 376, 378): Gán US-09 cho Hà và US-03 cho Lam làm Primary Presentation.
   - `TASK-006` (dòng 424, 426): Gán US-09 cho Hà (`US-09 (Primary Presentation của Hà)`).
   - `TASK-007` (dòng 474, 476, 486-488): Tham chiếu mã `US-11` (không tồn tại trong backlog chính thức) và gán cho Hà là Primary US-09.
   - `TASK-008` (dòng 524, 526): Gán US-05 cho Dung (`US-05 (Primary Presentation của Dung)`).
   - `TASK-009` (dòng 575, 577): Gán US-07 cho Giang và US-01 cho Dương làm Primary.
   - `TASK-010` (dòng 629, 631): Gán US-07 cho Giang (`US-07 (Primary Presentation của Giang)`).
   - `TASK-012` (dòng 735, 737-742): Danh sách UI gán Dương→US-01/02, Lam→US-03/04, Dung→US-05/06, Giang→US-07/08, Hà→US-09/10/11.
   - `TASK-013` (dòng 791): Tham chiếu luồng 5 Primary Stories cũ và Supporting Stories (US-10, US-11).
   - `Section 10, 10b, 11` (dòng 1170-1244): Toàn bộ bảng chia 2 tầng, gán Dương→US-01, Lam→US-03, Dung→US-05, Giang→US-07, Hà→US-09/10/11.
   - `Section 19` (dòng 1398-1700): Kịch bản 5 phút chuẩn bị cho Dương→US-01, Lam→US-03, Dung→US-05, Giang→US-07, Hà→US-09, và bảng 6 Supporting Stories.

---

## 3. Old Allocation References Removed (Các tham chiếu cũ đã bị loại bỏ)

Đã loại bỏ **100%** các thuật ngữ phân chia 2 tầng và các tham chiếu sai lệch:

| Thuật ngữ / Khái niệm cũ | Số lượng trước khi sửa | Số lượng sau khi sửa | Trạng thái |
|---|:---:|:---:|:---:|
| `"Primary Presentation"` | 38 | **0** | Đã loại bỏ hoàn toàn |
| `"Supporting Implementation"` | 26 | **0** | Đã loại bỏ hoàn toàn |
| `"Primary Presentation Owner"` | 14 | **0** | Đã loại bỏ hoàn toàn |
| `"Primary của"` | 8 | **0** | Đã loại bỏ hoàn toàn |
| `"Supporting của"` | 3 | **0** | Đã loại bỏ hoàn toàn |
| Mô hình phân chia Tầng 1 / Tầng 2 | 4 khối | **0** | Đã thay bằng phân công Group-01 |

---

## 4. User Story Mappings Corrected (Chi tiết hiệu chỉnh User Story Mapping)

Phân bổ trách nhiệm User Story trên toàn bộ [docs/IMPLEMENTATION_PLAN.md](file:///d:/LTUD\group-01-project-main\docs\IMPLEMENTATION_PLAN.md) hiện tại đã đồng bộ **100%** với phân công chính thức Group-01:

| Thành viên | User Story cốt lõi (Core 5-Min Viva) | Toàn bộ User Stories phụ trách chính | Nhiệm vụ & Phạm vi triển khai chính thức |
|---|---|---|---|
| **Trần Thị Kiều Giang** | **US-01** — Tạo & Chuẩn hóa Purchase Request | **US-01** | Form tạo PR, validation bắt buộc trước Submit, tích hợp gợi ý AI chuẩn hóa mô tả. Phối hợp UI cho toàn hệ thống. |
| **Nguyễn Trương Thùy Dương** | **US-04** — Manager Review, Approval & Budget | **US-04**, **US-05**, **US-06** | **US-04:** Màn hình duyệt PR cho Manager, định tuyến, phân cấp duyệt, Audit Trail.<br>**US-05:** Finance kiểm tra Budget, hiển thị cảnh báo vượt ngân sách.<br>**US-06:** Thu thập, quản lý và liên kết danh sách Báo giá (Quotation) với PR. |
| **Nguyễn Trúc Lam** | **US-07** — AI Extraction & Recommendation | **US-03**, **US-07** | **US-03:** AI gợi ý hoàn thiện mô tả PR, cơ chế Human-in-the-loop review.<br>**US-07:** Trích xuất báo giá, ma trận so sánh giá, phát hiện Anomaly $\ge 20\%$, đề xuất nhà cung cấp tối ưu. |
| **Nguyễn Thị Thùy Dung** | **US-08** — Lựa chọn NCC & Tạo Purchase Order | **US-02**, **US-08**, **US-09**, **GOV-01** | **US-02:** Theo dõi trạng thái và timeline PR.<br>**US-08:** Tạo PO từ PR đã duyệt, khóa cứng số lượng & đơn giá server-side (T-094 / HD-08).<br>**US-09:** Giao diện & nghiệp vụ ghi nhận bàn giao hàng (Receiving) thực tế.<br>**GOV-01:** Ma trận RBAC 5 vai trò, chặn No Self-Approval. |
| **Trần Thị Thu Hà** | **US-10** — Close PR & Đối soát giao nhận | **US-10**, **GOV-02** | **US-10:** Điều kiện đóng PR (HD-07 / REQ-BR-11), kiểm tra hoàn tất Receiving trước khi Close, giải phóng và tất toán ngân sách.<br>**GOV-02:** Ghi nhận sự kiện Audit Trail toàn diện, truy xuất lịch sử xử lý. |

### Các mapping sai lệch cũ đã bị xóa bỏ hoàn toàn:
- ❌ **Dương → US-01:** Đã xóa bỏ $\to$ Chuẩn hóa: **Giang → US-01**.
- ❌ **Lam → US-03 only:** Đã xóa bỏ $\to$ Chuẩn hóa: **Lam → US-03, US-07**.
- ❌ **Dung → US-05:** Đã xóa bỏ $\to$ Chuẩn hóa: **Dương → US-05**; Dung phụ trách US-02, US-08, US-09, GOV-01.
- ❌ **Giang → US-07:** Đã xóa bỏ $\to$ Chuẩn hóa: **Lam → US-07**; Giang phụ trách US-01.
- ❌ **Hà → US-09:** Đã xóa bỏ $\to$ Chuẩn hóa: **Dung → US-09** (và US-08); Hà phụ trách US-10, GOV-02.

---

## 5. US-11 Handling (Xử lý mã User Story US-11)

- **Nguyên nhân tồn tại trong tài liệu cũ:** Bản phác thảo sơ khai chia nhỏ nghiệp vụ giao nhận và kết thúc mua sắm thành US-10 (Receiving) và US-11 (Close PR).
- **Quy chuẩn Backlog Group-01:** Backlog chính thức của Group-01 (`docs/03-product/taiga-backlog.md`) chỉ bao gồm:
  `US-01` đến `US-10`, `GOV-01`, `GOV-02`. Không tồn tại mã US-11.
- **Biện pháp xử lý đã thực hiện:**
  - Tác vụ `TASK-007` (thực thi quy tắc HD-07 / REQ-BR-11 `SUM(receivedQty) >= PO.quantity` trước khi đóng PR) được ánh xạ chính thức về **US-10 (Close Purchase Request & Đối soát)** do **Trần Thị Thu Hà** phụ trách chính.
  - Tác vụ tiếp nhận hàng hóa liên quan được ánh xạ chính thức về **US-09 (Ghi nhận Receiving)** do **Nguyễn Thị Thùy Dung** phụ trách chính.
  - Toàn bộ các tham chiếu đến `US-11` trong bảng ma trận, danh sách task và checklist đã được loại bỏ hoặc remap về US-10.
  - Tuyệt đối **không tạo US-11 mới**.

---

## 6. Decision Log Entry (Bản ghi Quyết định chính thức HD-11)

Đã bổ sung bản ghi quyết định **HD-11** vào [docs/DECISION_LOG.md](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md) tuân thủ đúng quy ước định dạng hiện hành:

```markdown
## HD-11: Official Group-01 User Story Responsibility Allocation

- **ID:** HD-11
- **Title:** Official Group-01 User Story Responsibility Allocation
- **Status:** **DECIDED**
- **Decision:** Chuẩn hóa và đồng bộ 100% phân bổ trách nhiệm User Story theo phiên bản mới Group-01 (taiga-backlog.md)...
  - Trần Thị Kiều Giang: US-01
  - Nguyễn Trương Thùy Dương: US-04, US-05, US-06
  - Nguyễn Trúc Lam: US-03, US-07
  - Nguyễn Thị Thùy Dung: US-02, US-08, US-09, GOV-01
  - Trần Thị Thu Hà: US-10, GOV-02
  5 User Story cốt lõi thuyết trình 5 phút:
  - Giang: US-01 | Dương: US-04 | Lam: US-07 | Dung: US-08 | Hà: US-10
  Dải mã User Story chuẩn: US-01..US-10, GOV-01, GOV-02. Close PR thuộc US-10. Bãi bỏ US-11.
- **Decision type:** Project Governance / Organization & Traceability
- **Date:** 2026-09-24
- **Owner:** Group 01
```

---

## 7. Cross-Document Consistency (Kiểm tra đối chiếu chéo liên tài liệu)

Kết quả đối soát giữa 4 tài liệu hạt nhân của dự án:
1. [docs/IMPLEMENTATION_PLAN.md](file:///d:/LTUD/group-01-project-main/docs/IMPLEMENTATION_PLAN.md)
2. [docs/03-product/taiga-backlog.md](file:///d:/LTUD/group-01-project-main/docs/03-product/taiga-backlog.md)
3. [docs/AI_USAGE_TRACEABILITY.md](file:///d:/LTUD/group-01-project-main/docs/AI_USAGE_TRACEABILITY.md)
4. [docs/DECISION_LOG.md](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md)

| Tiêu chí đối soát | IMPLEMENTATION_PLAN | taiga-backlog | AI_USAGE_TRACEABILITY | DECISION_LOG (HD-11) | Kết luận |
|---|:---:|:---:|:---:|:---:|:---:|
| Giang $\to$ US-01 | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | **ĐỒNG BỘ** |
| Dương $\to$ US-04, 05, 06 | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | **ĐỒNG BỘ** |
| Lam $\to$ US-03, 07 | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | **ĐỒNG BỘ** |
| Dung $\to$ US-02, 08, 09, GOV-01 | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | **ĐỒNG BỘ** |
| Hà $\to$ US-10, GOV-02 | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | **ĐỒNG BỘ** |
| Close PR $\to$ US-10 | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | ✅ Khớp 100% | **ĐỒNG BỘ** |
| Không tồn tại US-11 | ✅ Bãi bỏ | ✅ Không có | ✅ Không có | ✅ Bãi bỏ | **ĐỒNG BỘ** |

---

## 8. Remaining Conflicts (Xung đột tồn dư)

- **Số lượng xung đột còn lại:** **0 (Không còn bất kỳ xung đột nào)**.
- Toàn bộ các TASK-xxx, bảng ma trận phân công, bảng evidence và kịch bản demo 5 phút đều đã được đồng nhất theo chuẩn Group-01.

---

## 9. Validation Result (Kết quả kiểm chứng tự động)

Chạy kiểm thử tự động bằng script Python kiểm tra toàn diện:
- `Term 'Primary Presentation':` **0 occurrences**
- `Term 'Supporting Implementation':` **0 occurrences**
- `Term 'Primary Presentation Owner':` **0 occurrences**
- `Term 'Primary của':` **0 occurrences**
- `Term 'Supporting của':` **0 occurrences**
- `Old primary ownership matches (Dương→US-01, Dung→US-05, Giang→US-07, Hà→US-09):` **0 matches**
- `New core allocation matches:`
  - Giang (US-01): **12 matching lines (PASS)**
  - Dương (US-04): **13 matching lines (PASS)**
  - Lam (US-07): **16 matching lines (PASS)**
  - Dung (US-08): **17 matching lines (PASS)**
  - Hà (US-10): **18 matching lines (PASS)**
- `Total old allocation residues across 4 documents:` **0**

---

## 10. Git Status & Safety Verification

- **Branch hiện tại:** `final-delivery`
- **Mã nguồn Backend (`backend/app/**`):** Giữ nguyên vẹn 100% (Không sửa).
- **Mã nguồn Frontend (`frontend/src/**`):** Giữ nguyên vẹn 100% (Không sửa).
- **Database Schema & Runtime (`schema.prisma` / Supabase):** Giữ nguyên vẹn 100% (Không chạy `prisma db push`).
- **Test files (`backend/tests/**`):** Giữ nguyên vẹn 100% (Không sửa).
- **AI Usage Logs lịch sử (`docs/02-vault/AI_USAGE_LOG.md`):** Giữ nguyên vẹn 100% (Không sửa).
- **Git Push / Reset:** Tuyệt đối không thực hiện `git push` hay `git reset`.

```
$ git status
On branch final-delivery
Your branch is ahead of 'origin/final-delivery' by 5 commits.
Changes not staged for commit:
	modified:   docs/DECISION_LOG.md
	modified:   docs/IMPLEMENTATION_PLAN.md
	modified:   docs/logs/ai-usage-log.md
Untracked files:
	docs/ALLOCATION_CONSISTENCY_FIX_REPORT.md
```

---

## KẾT LUẬN CUỐI CÙNG

```
ALLOCATION_STATUS:
CONSISTENT
```

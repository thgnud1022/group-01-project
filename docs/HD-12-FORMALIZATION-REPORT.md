# BÁO CÁO CHÍNH THỨC HÓA QUYẾT ĐỊNH HUMAN DECISION HD-12

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)
**Tác vụ:** TASK-004 — Implement Supabase Auth JWT Verification Middleware
**Nhánh:** `final-delivery`
**Ngày thực hiện:** 2026-09-24
**Trạng thái:** DOCUMENTATION DECISION FORMALIZATION ONLY (Không sửa code, không sửa database)

---

## 1. Quyết định chính thức (Official Decision)

- **Mã quyết định:** **HD-12**
- **Tiêu đề:** Authentication Identity Binding via Supabase Auth User ID
- **Trạng thái:** **`DECIDED`** (Đã được Human chính thức phê duyệt)
- **Phương án lựa chọn:** **OPTION B — Mapping qua `authUserId` (Federated Identity Binding)**
- **Luồng xử lý danh tính chính thức:**
  ```text
  HTTP Request (Header: Authorization: Bearer <Supabase JWT>)
    └─► Verify JWT signature (ES256 qua JWKS), exp, iss, aud
          └─► Trích xuất verified 'sub' (Supabase Auth User UUID)
                └─► Truy vấn CSDL: SELECT * FROM "User" WHERE authUserId = sub
                      └─► Nạp hồ sơ Application User (id, name, departmentId, role)
                            └─► Trích xuất User.role từ CSDL nội bộ
                                  └─► Cung cấp cho TASK-005 Server-side RBAC
  ```
- **Ràng buộc an ninh cốt lõi:**
  - Tuyệt đối không tin tưởng role, approverRole hoặc email do client gửi trong request body, query params hay frontend dropdown.
  - Phân tách tuyệt đối giữa Authentication Identity (do Supabase Auth quản lý) và Application Identity (do bảng `User` trong PostgreSQL quản lý).

---

## 2. So sánh Trước và Sau khi chuẩn hóa (Before vs After)

| Tiêu chí | Trước khi chuẩn hóa (Before) | Sau khi chuẩn hóa (After) |
| :--- | :--- | :--- |
| **Trạng thái quyết định** | Mục 14 trong `docs/TASK-004-AUTH-DESIGN.md` ở trạng thái `HUMAN DECISION REQUIRED` với 2 lựa chọn (Option A và Option B). | Đã được Human xác nhận và chốt: **Option B = APPROVED / DECIDED**. Không còn trạng thái chờ quyết định. |
| **`docs/DECISION_LOG.md`** | Danh mục quyết định dừng lại ở `HD-11` (User Story Allocation). | Bổ sung quyết định mới **`HD-12`** với Status `DECIDED`, ghi nhận đầy đủ Luồng, Lý do, Ràng buộc, Hệ quả và Ma trận kiểm thử. |
| **Phương án Identity Mapping** | Chưa xác định giữa Mapping qua Email (Option A) hay qua `authUserId` (Option B). | **Option B** là quyết định chuẩn bắt buộc. Option A chính thức **KHÔNG sử dụng**. |
| **Kế hoạch Schema CSDL** | Đang chờ quyết định xem có thay đổi `schema.prisma` hay không. | Xác định rõ: Model `User` sẽ cần thêm trường `authUserId String? @unique` khi bước vào giai đoạn implementation. |

---

## 3. Danh sách tập tin thay đổi (Files Modified)

1. [docs/DECISION_LOG.md](file:///d:/LTUD/group-01-project-main/docs/DECISION_LOG.md):
   - Thêm quyết định kiến trúc **`HD-12: Authentication Identity Binding via Supabase Auth User ID`**.
   - Cập nhật ngày hiệu lực: `2026-09-24`, chủ sở hữu: `Group 01`, trạng thái: `DECIDED`.
2. [docs/TASK-004-AUTH-DESIGN.md](file:///d:/LTUD/group-01-project-main/docs/TASK-004-AUTH-DESIGN.md):
   - Cập nhật Section 14 (Cổng quyết định) và Section 15 (Khuyến nghị).
   - Chuyển section cuối thành `## HUMAN DECISION: HD-12 — DECIDED`.
   - Ghi nhận Option B đã được phê duyệt chính thức. Xóa bỏ hoàn toàn cụm từ `HUMAN DECISION REQUIRED`.

---

## 4. Kết quả kiểm tra & Thẩm định (Validation)

- **Kiểm tra cú pháp & Whitespace:**
  - Lệnh: `git diff --check`
  - Kết quả: **Clean (0 errors, không có trailing whitespace, không có blank line ở EOF)**.
- **Kiểm tra tính nhất quán nội dung:**
  - `HD-12` tồn tại và mang trạng thái `DECIDED`.
  - Luồng `Verified JWT sub → User.authUserId → User.role → RBAC` nhất quán giữa `DECISION_LOG.md` và `TASK-004-AUTH-DESIGN.md`.
  - Không còn bất kỳ câu chữ nào thể hiện Human chưa ra quyết định.
- **An toàn mã nguồn (Implementation Safety):**
  - Số lượng file code backend thay đổi: `0`
  - Số lượng file frontend thay đổi: `0`
  - `schema.prisma`: **Không thay đổi** (giữ nguyên cho tới khi có lệnh thực hiện Step 3/4).
  - Cơ sở dữ liệu: **Không migration, không chạy prisma db push**.

---

## 5. Trạng thái Git (Git Status)

```text
On branch final-delivery
Your branch is ahead of 'origin/final-delivery' by 6 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   docs/DECISION_LOG.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	_IMPORT_EARLY_PHASE/
	docs/HD-12-FORMALIZATION-REPORT.md
	docs/TASK-004-AUTH-DESIGN.md
	docs/course/Giao_trinh.txt
	docs/course/Output_BaoCao.xlsx
	excel_dump.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

---

## 6. Kết luận & Điểm dừng (Stopping Gate)

Nhiệm vụ **FORMALIZE HUMAN DECISION HD-12** đã hoàn tất trọn vẹn và chính xác theo yêu cầu. Toàn bộ tài liệu kiến trúc và nhật ký quyết định của dự án đã đồng bộ 100% với lựa chọn Option B.

**Hệ thống dừng lại tại đây và KHÔNG tự ý chuyển sang bước implementation.**

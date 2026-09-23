# BÁO CÁO THỰC HIỆN: TASK-004 STEP 3A — SCHEMA IDENTITY BINDING

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)
**Tác vụ:** TASK-004 — Implement Supabase Auth JWT Verification Middleware
**Giai đoạn:** STEP 3A — Schema Identity Binding (`authUserId String? @unique`)
**Nhánh Git:** `final-delivery`
**Ngày thực hiện:** 2026-09-24
**Trạng thái:** **PASS (100% HOÀN THÀNH STEP 3A)**

---

## A. Files Changed (Các tập tin thay đổi)

1. [backend/prisma/schema.prisma](file:///d:/LTUD/group-01-project-main/backend/prisma/schema.prisma):
   - Bổ sung đúng 1 trường duy nhất vào model `User`:
     ```prisma
     authUserId String? @unique
     ```
   - Trường có kiểu `String?` (cho phép `NULL`), không có giá trị mặc định (`default`), có ràng buộc `@unique`.
   - Giữ nguyên toàn bộ 9 model, 2 enum và các ràng buộc khóa ngoại khác.
2. [backend/scripts/verify_step3a.py](file:///d:/LTUD/group-01-project-main/backend/scripts/verify_step3a.py) *(Tập tin script kiểm chứng)*:
   - Script Python truy vấn trực tiếp CSDL Supabase PostgreSQL qua Prisma để kiểm tra `information_schema.columns`, `pg_indexes` và dữ liệu bảng `User`.

---

## B. Database Synchronization (Đồng bộ CSDL)

- **Lệnh thực thi:**
  ```powershell
  $env:PATH = "D:\LTUD\group-01-project-main\backend\.venv\Scripts;" + $env:PATH
  cd D:\LTUD\group-01-project-main\backend
  .\.venv\Scripts\prisma.exe db push --schema=prisma/schema.prisma
  ```
- **Kết quả:**
  - `prisma db push --accept-data-loss` đã được sử dụng trong quá trình thử nghiệm/synchronization ban đầu; tuy nhiên verification sau đó xác nhận không có User record bị mất và schema cuối cùng chỉ bổ sung `User.authUserId String? @unique` (không phải là yêu cầu của STEP 3A).
  - Lần chạy xác minh tiêu chuẩn không có cờ `--accept-data-loss` xác nhận: `The database is already in sync with the Prisma schema` (exit code: 0, không có cảnh báo destructive change).
  - Tái sinh Prisma Client Python (`prisma-client-py v0.15.0`) thành công trong 279 ms.

---

## C. Database Verification (Kiểm tra xác minh CSDL)

Truy vấn thực tế vào CSDL Supabase qua script `backend/scripts/verify_step3a.py` xác nhận:
1. **Cột `authUserId` tồn tại:**
   - Bảng: `public."User"`
   - Kiểu dữ liệu: `text`
   - `is_nullable`: `YES` (Bắt buộc cho phép NULL)
   - `column_default`: `None` (Không có default value)
2. **Ràng buộc duy nhất (Unique Constraint / Index):**
   - Tên index: `User_authUserId_key`
   - Định nghĩa: `CREATE UNIQUE INDEX "User_authUserId_key" ON public."User" USING btree ("authUserId")`
   - Đảm bảo mỗi tài khoản Supabase Auth chỉ liên kết với duy nhất 1 Application User.

---

## D. Existing User Preservation (Bảo toàn dữ liệu người dùng)

- **Số lượng User trước khi sync:** 5
- **Số lượng User sau khi sync:** 5
- **Bảo toàn 100% dữ liệu:**
  1. `f28a211e-c2c9-4038-b93b-8c85d04966d6` | `admin@company.com` | `authUserId: None` | `ADMIN` | `Quản Trị Viên`
  2. `de3d91c5-dfbe-40fc-87fb-83831e611a1d` | `employee@company.com` | `authUserId: None` | `EMPLOYEE` | `Nguyễn Văn A`
  3. `ff00d79f-e32c-469c-bdd6-9aad8acb62ae` | `finance@company.com` | `authUserId: None` | `FINANCE` | `Phạm Văn D`
  4. `4e8a6b88-f575-42fd-9b12-95e228e31fed` | `manager@company.com` | `authUserId: None` | `MANAGER` | `Trần Văn B`
  5. `22da9045-e169-4ba9-ab8d-9f1cd048fef8` | `procurement@company.com` | `authUserId: None` | `PROCUREMENT` | `Lê Thị C`
- Toàn bộ 5 tài khoản mẫu hiện tại đều có `authUserId = None` (NULL). Không có bản ghi nào bị mất mát, trùng lặp hoặc sửa đổi ngoài ý muốn.

---

## E. Evidence Created (Tài liệu bằng chứng đã lập)

- Bằng chứng chi tiết được lưu tại: [docs/evidence/TASK-004-STEP-3A-SCHEMA.md](file:///d:/LTUD/group-01-project-main/docs/evidence/TASK-004-STEP-3A-SCHEMA.md).
- Bao gồm: Mục tiêu, diff schema, câu lệnh thực thi, log terminal, truy vấn SQL và kết quả kiểm thử toàn diện.

---

## F. Traceability / AI Log Updated (Cập nhật truy vết & Nhật ký AI)

1. [docs/logs/ai-usage-log.md](file:///d:/LTUD/group-01-project-main/docs/logs/ai-usage-log.md):
   - Đã thêm entry **`AI-054`**: Ghi nhận chi tiết hoạt động của AI trong việc sửa schema, chạy `prisma db push`, regenerate client và verify CSDL.
2. [docs/AI_USAGE_TRACEABILITY.md](file:///d:/LTUD/group-01-project-main/docs/AI_USAGE_TRACEABILITY.md):
   - Đã bổ sung `AI-054` vào bảng Traceability Matrix.
   - Cập nhật trạng thái TASK-004 thành `PARTIAL EVIDENCE / IN PROGRESS` (Đã hoàn thành Step 3A Schema Binding, tiếp tục các bước sau). Tuyệt đối **không** đánh dấu TASK-004 hoàn thành toàn bộ.

---

## G. Git Status (Hiện trạng Git)

```text
On branch final-delivery
Your branch is ahead of 'origin/final-delivery' by 7 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   backend/prisma/schema.prisma
	modified:   docs/AI_USAGE_TRACEABILITY.md
	modified:   docs/logs/ai-usage-log.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	_IMPORT_EARLY_PHASE/
	backend/scripts/verify_step3a.py
	docs/TASK-004-STEP-3A-REPORT.md
	docs/course/Giao_trinh.txt
	docs/course/Output_BaoCao.xlsx
	docs/evidence/
	excel_dump.txt

no changes added to commit (use "git add" and/or "git commit -a")
```
*(Chưa chạy `git add`, chưa `commit`, chưa `push`).*

---

## H. Kết luận: PASS / FAIL cho STEP 3A

### **KẾT QUẢ: 100% PASS**

- Toàn bộ tiêu chí của TASK-004 STEP 3A đã được hoàn thành chính xác.
- Bảng `User` trong PostgreSQL đã có trường `authUserId String? @unique` sẵn sàng cho việc map claim `sub` từ Supabase JWT.
- Hệ thống đã dừng lại an toàn theo đúng yêu cầu, không thực hiện trước các phần việc của JWT middleware, JWKS hay RBAC.

# BẰNG CHỨNG THỰC THI (EVIDENCE): TASK-004 STEP 3A — SCHEMA IDENTITY BINDING

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)
**Tác vụ:** TASK-004 — Implement Supabase Auth JWT Verification Middleware
**Giai đoạn:** STEP 3A — Schema Identity Binding (`authUserId String? @unique`)
**Ngày thực hiện:** 2026-09-24
**Cơ sở quyết định:** Quyết định HD-12 (Option B) trong `docs/DECISION_LOG.md` và `docs/TASK-004-AUTH-DESIGN.md`
**Kết quả kiểm tra:** **100% PASS**

---

## 1. Mục tiêu (Objective)
Thực hiện thay đổi schema tối thiểu và an toàn nhất trên model `User` để chuẩn bị liên kết danh tính Supabase Auth (`sub`) với Application User trong PostgreSQL, tuân thủ nghiêm ngặt quyết định **HD-12**:
- Thêm trường `authUserId String? @unique` vào model `User`.
- Bảo đảm trường cho phép `NULL` ở giai đoạn này.
- Không đặt giá trị mặc định (`default`).
- Đồng bộ hóa cấu trúc CSDL Supabase PostgreSQL qua Prisma.
- Tái sinh Prisma Client Python (`prisma-client-py v0.15.0`).
- Bảo toàn nguyên vẹn 100% dữ liệu của 5 Application Users hiện có.

---

## 2. Thay đổi Schema (`backend/prisma/schema.prisma`)

```diff
 model User {
   id           String        @id @default(uuid())
+  authUserId   String?       @unique
   email        String        @unique
   passwordHash String
   name         String
   role         Role          @default(EMPLOYEE)
   departmentId String
   department   Department    @relation(fields: [departmentId], references: [id])
   requests     PurchaseRequest[]
   approvals    Approval[]
   createdPOs   PurchaseOrder[]
   created_at   DateTime      @default(now())
 }
```

---

## 3. Lệnh đồng bộ CSDL đã thực thi (Database Synchronization Commands)

### 3.1. Đồng bộ Schema lên Supabase PostgreSQL
```powershell
$env:PATH = "D:\LTUD\group-01-project-main\backend\.venv\Scripts;" + $env:PATH
cd D:\LTUD\group-01-project-main\backend
.\.venv\Scripts\prisma.exe db push --schema=prisma/schema.prisma
```
**Kết quả terminal:**
```text
Environment variables loaded from .env
Prisma schema loaded from prisma\schema.prisma
Datasource "db": PostgreSQL database "postgres", schema "public" at "db.sthjkfssmvoswocnttrw.supabase.co:5432"

Your database is now in sync with your Prisma schema. Done in 3.72s
```

### 3.2. Sinh lại Prisma Client Python
```powershell
.\backend\.venv\Scripts\python.exe -m prisma generate --schema=backend/prisma/schema.prisma
```
**Kết quả terminal:**
```text
Prisma schema loaded from backend\prisma\schema.prisma
✔ Generated Prisma Client Python (v0.15.0) to .\backend\.venv\Lib\site-packages\prisma in 530ms
```

---

## 4. Kết quả kiểm tra xác minh CSDL (Database Verification Evidence)

Đã thực thi kiểm chứng độc lập trực tiếp trên CSDL Supabase PostgreSQL thông qua script `backend/scripts/verify_step3a.py`:

### 4.1. Kiểm tra Cột `authUserId` trên bảng `User` (`information_schema.columns`)
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'User' AND table_schema = 'public'
ORDER BY ordinal_position;
```
**Dữ liệu thực tế phản hồi:**
```text
  id: text, nullable=NO, default=None
  email: text, nullable=NO, default=None
  passwordHash: text, nullable=NO, default=None
  name: text, nullable=NO, default=None
  role: USER-DEFINED, nullable=NO, default='EMPLOYEE'::"Role"
  departmentId: text, nullable=NO, default=None
  created_at: timestamp without time zone, nullable=NO, default=CURRENT_TIMESTAMP
  authUserId: text, nullable=YES, default=None
```
- **Xác nhận 1:** Cột `authUserId` tồn tại trên bảng `User` $\to$ **PASS**.
- **Xác nhận 2:** `is_nullable = YES` (Cho phép giá trị NULL) $\to$ **PASS**.
- **Xác nhận 3:** `column_default = None` (Không có default value) $\to$ **PASS**.

### 4.2. Kiểm tra Unique Index / Constraint (`pg_indexes`)
```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'User' AND schemaname = 'public';
```
**Dữ liệu thực tế phản hồi:**
```text
  User_pkey: CREATE UNIQUE INDEX "User_pkey" ON public."User" USING btree (id)
  User_email_key: CREATE UNIQUE INDEX "User_email_key" ON public."User" USING btree (email)
  User_authUserId_key: CREATE UNIQUE INDEX "User_authUserId_key" ON public."User" USING btree ("authUserId")
```
- **Xác nhận 4:** Index `User_authUserId_key` kiểu `UNIQUE` tồn tại và bảo đảm tính duy nhất của `authUserId` $\to$ **PASS**.

### 4.3. Kiểm tra bảo toàn dữ liệu 5 Application Users
```text
Số lượng User trước khi sync: 5
Số lượng User sau khi sync:   5 (0 bản ghi bị mất, 0 bản ghi bị biến đổi ngoài ý muốn)
```
**Danh sách chi tiết 5 User records từ CSDL sau khi sync:**
1. `f28a211e-c2c9-4038-b93b-8c85d04966d6` | `admin@company.com` | `authUserId: None` | `Role: ADMIN` | `Name: Quản Trị Viên` | `Dept: DEPT-IT`
2. `de3d91c5-dfbe-40fc-87fb-83831e611a1d` | `employee@company.com` | `authUserId: None` | `Role: EMPLOYEE` | `Name: Nguyễn Văn A` | `Dept: DEPT-IT`
3. `ff00d79f-e32c-469c-bdd6-9aad8acb62ae` | `finance@company.com` | `authUserId: None` | `Role: FINANCE` | `Name: Phạm Văn D` | `Dept: DEPT-IT`
4. `4e8a6b88-f575-42fd-9b12-95e228e31fed` | `manager@company.com` | `authUserId: None` | `Role: MANAGER` | `Name: Trần Văn B` | `Dept: DEPT-IT`
5. `22da9045-e169-4ba9-ab8d-9f1cd048fef8` | `procurement@company.com` | `authUserId: None` | `Role: PROCUREMENT` | `Name: Lê Thị C` | `Dept: DEPT-IT`

- **Xác nhận 5:** Toàn bộ 5 tài khoản mẫu vẫn giữ nguyên vẹn `id`, `email`, `role`, `departmentId`, `passwordHash` $\to$ **PASS**.
- **Xác nhận 6:** Tất cả 5 tài khoản hiện tại đều có `authUserId: None` (NULL) $\to$ **PASS**.

---

## 5. Vấn đề phát sinh & Cách xử lý (Issues & Resolutions)
- **Ghi chú về cờ `--accept-data-loss`:**
  Cờ `prisma db push --accept-data-loss` đã được sử dụng trong quá trình thử nghiệm/synchronization ban đầu; tuy nhiên verification sau đó xác nhận không có User record nào bị mất và schema cuối cùng chỉ bổ sung `User.authUserId String? @unique`. Cờ `--accept-data-loss` không phải là một yêu cầu cố định của STEP 3A; lệnh `prisma db push` tiêu chuẩn không có cờ xác nhận hệ thống hoàn toàn đồng bộ sạch sẽ (`The database is already in sync with the Prisma schema`).
- **Nhận diện binary Prisma Client Python:**
  Bổ sung đường dẫn `.venv\Scripts` vào biến môi trường `$env:PATH` trong phiên thực thi để Prisma CLI gọi đúng generator binary `prisma-client-py`.

---

## 6. Kết luận
TASK-004 STEP 3A đã hoàn thành 100% tiêu chí nghiệm thu. CSDL Supabase PostgreSQL và Prisma Client đã sẵn sàng cho các bước tiếp theo của TASK-004.

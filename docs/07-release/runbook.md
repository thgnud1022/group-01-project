# RUNBOOK & DEPLOYMENT GUIDE: Hướng Dẫn Vận Hành & Khởi Chạy Hệ Thống

> **Dự án:** AI Procurement & Purchase Approval System (Group 01)  
> **Phiên bản:** `v1.0.0-final`  
> **Nhánh:** `final-delivery`  
> **Trạng thái Thẩm định:** Release Ready & Verified on Public Cloud  

---

## 1. Yêu Cầu Tiền Trạm (Prerequisites)

Để thiết lập và vận hành hệ thống thành công, máy trạm phát triển cần đáp ứng các điều kiện kỹ thuật tối thiểu sau:

* **Hệ điều hành:** Windows 10/11 (PowerShell / Command Prompt), macOS, hoặc Linux (Ubuntu 22.04+).
* **Node.js:** Phiên bản `>= 18.x` (Khuyến nghị `20.x` hoặc `24.x` LTS) kèm trình quản lý gói `npm`.
* **Python:** Phiên bản `>= 3.11` (Khuyến nghị `3.11.x` hoặc `3.12.x`) kèm `pip`.
* **Git:** Phiên bản `>= 2.30` để quản lý phiên bản mã nguồn.
* **Trình duyệt Web:** Google Chrome hoặc Microsoft Edge (yêu cầu để chạy bộ test tự động E2E với Puppeteer).
* *(Tùy chọn)* **Docker & Docker Compose:** Chỉ cần thiết nếu bạn muốn khởi chạy PostgreSQL local qua tệp `compose.yaml`. Nếu kết nối Supabase Cloud PostgreSQL, không bắt buộc cài Docker.

---

## 2. Sao Chép Mã Nguồn (Clone Repository)

Mở terminal/dòng lệnh và thực hiện:

```bash
# Clone kho mã nguồn chính thức
git clone https://github.com/thgnud1022/group-01-project.git

# Di chuyển vào thư mục dự án
cd group-01-project

# Chuyển sang nhánh release chính thức
git checkout final-delivery
```

---

## 3. Cấu Hình Biến Môi Trường (Configure Environment)

Hệ thống tách biệt cấu hình giữa máy chủ (Backend) và máy khách (Frontend). Sao chép và thiết lập các tệp môi trường từ các tệp mẫu có sẵn:

### 3.1. Cấu hình Backend (`backend/.env`)
```bash
cd backend
cp .env.example .env
```
Mở tệp `backend/.env` và điền các thông số:
- `DATABASE_URL`: Chuỗi kết nối PostgreSQL (khuyến nghị dùng Supabase Pooler IPv4).
  - Định dạng: `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?pgbouncer=true`
- `SUPABASE_URL`: Địa chỉ gốc của dự án Supabase, ví dụ: `https://[PROJECT-REF].supabase.co`
- `LLM_API_KEY`: *(Tùy chọn)* Khóa Google Gemini API. Nếu không điền, hệ thống sẽ tự động dùng bộ phân tích Fallback Heuristic có trọng số chuẩn.
- `AI_PROVIDER`: Đặt `"gemini"` hoặc `"mock"` (mặc định: `"gemini"`).

### 3.2. Cấu hình Frontend (`frontend/.env`)
Mở terminal tại thư mục gốc dự án:
```bash
cd frontend
cp .env.example .env
```
Mở tệp `frontend/.env` và điền các thông số:
- `VITE_SUPABASE_URL`: Địa chỉ gốc dự án Supabase.
- `VITE_SUPABASE_ANON_KEY`: Khóa công khai ẩn danh lấy từ Supabase Dashboard (`Project Settings -> API`).
- `VITE_API_URL`: *(Tùy chọn khi chạy local)* Điền `http://localhost:8000` nếu muốn frontend local kết nối trực tiếp backend local. Mặc định frontend trỏ về URL backend production trên Railway.

---

## 4. Thiết Lập Cơ Sở Dữ Liệu (Database Setup)

Dự án sử dụng CSDL quan hệ PostgreSQL quản lý bởi Prisma ORM.

### Lựa chọn 1: Sử dụng Supabase Cloud PostgreSQL (Khuyến nghị chuẩn)
- Đảm bảo dự án Supabase đã được tạo trên Supabase Cloud.
- Đảm bảo các bảng dữ liệu đã được khởi tạo theo schema (`backend/prisma/schema.prisma`).
- Tuyệt đối **không thực hiện lệnh drop, reset hoặc migration mang tính phá hủy dữ liệu** trên database production.

### Lựa chọn 2: Sử dụng Docker Local PostgreSQL
Nếu muốn chạy một database độc lập tại máy cá nhân:
```bash
# Từ thư mục gốc dự án
docker compose up -d

# Kiểm tra container đang chạy cổng 5432
docker compose ps
```
Cập nhật `DATABASE_URL="postgresql://app:app-local-password@localhost:5432/procurement_db"` vào `backend/.env`, sau đó đẩy schema:
```bash
cd backend
prisma db push
```

---

## 5. Khởi Chạy Máy Chủ Backend (Start Backend)

```bash
cd backend

# 1. Tạo môi trường ảo Python độc lập
python -m venv .venv

# 2. Kích hoạt môi trường ảo:
# Trên Windows:
.venv\Scripts\activate
# Trên Linux / macOS:
source .venv/bin/activate

# 3. Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# 4. Sinh mã nguồn Prisma Client Python
prisma generate

# 5. Đồng bộ ánh xạ người dùng authUserId (Idempotent seed)
python scripts/seed_auth_users.py

# 6. Khởi chạy HTTP Server qua Uvicorn
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*Điểm kiểm tra:*
- Máy chủ sẽ lắng nghe tại: `http://localhost:8000`
- Giao diện tài liệu Swagger tương tác: `http://localhost:8000/docs`

---

## 6. Khởi Chạy Giao Diện Frontend (Start Frontend)

Mở một cửa sổ terminal mới từ thư mục gốc dự án:

```bash
cd frontend

# 1. Cài đặt các gói npm
npm install

# 2. Khởi chạy máy chủ phát triển Vite
npm run dev
```

*Điểm kiểm tra:*
- Giao diện Web Application mở tại: `http://localhost:5173`
- Để kiểm tra đóng gói sản phẩm (Production build): `npm run build`

---

## 7. Kiểm Tra Trạng Thái Sức Khỏe (Verify Health)

Sau khi backend khởi động, bạn có thể kiểm tra trạng thái hoạt động:

```bash
# Kiểm tra endpoint sức khỏe qua cURL
curl http://127.0.0.1:8000/api/health
```
Kết quả trả về chuẩn HTTP 200:
```json
{"status": "ok", "database": "connected"}
```

---

## 8. Hướng Dẫn Đăng Nhập & Phân Quyền (Login & Role Governance)

Hệ thống bảo vệ dữ liệu bằng cơ chế kiểm soát máy chủ nghiêm ngặt (**Server-Side RBAC**). Mã định danh người dùng được xác thực qua JWT token do Supabase cấp, ánh xạ trực tiếp sang bảng `User` trong PostgreSQL.

### Danh sách tài khoản thử nghiệm chuẩn:

| Tài khoản Email | Mật khẩu | Vai trò (Role) | Bộ phận | Chức năng kiểm thử chính |
|---|---|---|---|---|
| `employee@company.com` | `password123` | `EMPLOYEE` | Phòng CNTT | Tạo yêu cầu mua sắm mới (PR) |
| `manager@company.com` | `password123` | `MANAGER` | Phòng CNTT | Phê duyệt / Từ chối PR (Áp dụng No Self-Approval) |
| `procurement@company.com` | `password123` | `PROCUREMENT` | Ban Mua sắm | Quản lý nhà cung cấp, nhập báo giá, so sánh, nhận tư vấn AI, tạo PO |
| `finance@company.com` | `password123` | `FINANCE` | Ban Tài chính | Giám sát hạn mức ngân sách và quyết toán |
| `admin@company.com` | `password123` | `ADMIN` | Hệ thống | Toàn quyền quản trị hệ thống |

---

## 9. Khởi Chạy Kiểm Thử Tự Động (Run Automated Tests)

Toàn bộ các bộ kiểm thử dưới đây đã được nhóm kiểm chứng 100% Green trước khi phát hành:

### 9.1. Kiểm thử Hồi quy Backend (Backend Regression Pytest)
Bao phủ 133 test cases kiểm tra RBAC, JWT, khóa giao dịch PO và nghiệp vụ nhận hàng:
```bash
cd backend
pytest -v
```
*Kết quả kỳ vọng:* `133 passed` trong khoảng 400 - 450 giây trên live database.

### 9.2. Kiểm thử Trình duyệt Toàn chu trình (Browser E2E Lifecycle)
Kịch bản 14 bước thực thi tự động từ tạo PR đến đóng PR và quyết toán:
```bash
cd frontend
node scripts/test_final_full_lifecycle_e2e.js
```
*Ghi chú kỹ thuật:* Bộ kiểm thử này sử dụng **Puppeteer** (`puppeteer-core`) kết nối tới trình duyệt Chrome/Chromium cục bộ. Các đặc tả Playwright có sẵn trong thư mục nhưng chưa được nghiệm thu độc lập.

### 9.3. Kiểm thử Khói Môi trường Đám mây Công cộng (Public Smoke Test)
Kiểm thử 9 tiêu chí vận hành trên domain live Vercel & Railway:
```bash
python scratch/ai089_public_smoke.py
```
*Kết quả kỳ vọng:* `9/9 criteria PASSED (100%)`.

---

## 10. Thông Tin Triển Khai Công Cộng & Vận Hành Đám Mây (Public Deployment Reference)

Hệ thống được thiết lập cơ chế triển khai tự động liên tục (Continuous Deployment) từ nhánh `final-delivery`:

* **Frontend SPA:** Triển khai trên **Vercel**
  - URL: [https://group-01-project.vercel.app](https://group-01-project.vercel.app)
  - Cấu hình điều hướng: Tệp `frontend/vercel.json` định tuyến toàn bộ request tĩnh về `/index.html`.
* **Backend API:** Triển khai trên **Railway**
  - URL: [https://group-01-project-production.up.railway.app](https://group-01-project-production.up.railway.app)
  - Khởi động: Tệp `backend/start.sh` tự động thực thi `prisma generate`, `python scripts/seed_auth_users.py`, và khởi chạy Uvicorn trên biến cổng `$PORT`.
* **Cơ sở dữ liệu:** **Supabase Cloud PostgreSQL**
  - Chế độ kết nối: IPv4 Transaction Pooler (cổng 6543).

### Quy trình Khôi phục & Sự cố (Rollback & Incident Handling):
- Trong trường hợp deploy mới trên Railway gặp lỗi, cơ chế khởi động an toàn trong `start.sh` ghi nhận lỗi non-fatal và tiếp tục khởi chạy Uvicorn.
- Để khôi phục về phiên bản ổn định đã được gắn tag, thực hiện checkout commit gắn tag `v1.0.0-final` (`9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`).

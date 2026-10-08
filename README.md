# AI Procurement & Purchase Approval System

> **Dự án Môn học:** Thực hành Lập trình Ứng dụng Doanh nghiệp (MIS3032_1 - Phiên bản 2026)  
> **Nhóm thực hiện:** Group 01  
> **Phiên bản:** `v1.0.0-final` (Git Tag: `v1.0.0-final`)  
> **Nhánh phát triển:** `final-delivery`  

---

## 🌐 1. Public Demo & Trực tuyến

Hệ thống đã được triển khai hoàn chỉnh và kiểm chứng trên hạ tầng đám mây công cộng:

| Thành phần | Nền tảng | Địa chỉ truy cập / Endpoint | Trạng thái |
|---|---|---|---|
| **Frontend Web App** | Vercel | [https://group-01-project.vercel.app](https://group-01-project.vercel.app) | `LIVE (200 OK)` |
| **Backend REST API** | Railway | [https://group-01-project-production.up.railway.app](https://group-01-project-production.up.railway.app) | `LIVE (200 OK)` |
| **API Healthcheck** | Railway | [https://group-01-project-production.up.railway.app/api/health](https://group-01-project-production.up.railway.app/api/health) | `{"status":"ok","database":"connected"}` |
| **API Documentation** | Railway / Swagger | [https://group-01-project-production.up.railway.app/docs](https://group-01-project-production.up.railway.app/docs) | `Interactive OpenAPI` |
| **Database & Auth** | Supabase Cloud | PostgreSQL 15+ (kết nối qua IPv4 Connection Pooler) | `CONNECTED` |

---

## 📖 2. Giới thiệu Dự án (Project Overview)

**AI Procurement & Purchase Approval System** là giải pháp số hóa toàn diện quy trình mua sắm và phê duyệt đơn hàng nội bộ doanh nghiệp. Hệ thống tích hợp trí tuệ nhân tạo (AI) trong vai trò **Trợ lý Tư vấn Quyết định (Decision Advisory)**, kết hợp cơ chế kiểm soát ngân sách thời gian thực và phân quyền máy chủ nghiêm ngặt (Zero-Trust Server-Side RBAC).

### Chu trình nghiệp vụ chính (End-to-End Procurement Lifecycle):
1. **Khởi tạo Yêu cầu Mua sắm (Purchase Request - PR):** Nhân viên lập PR với danh mục hàng hóa, đơn giá dự kiến, chọn phòng ban và mức độ ưu tiên.
2. **Phê duyệt & Giữ Ngân sách (Approval & Budget Guard):** Quản lý bộ phận xét duyệt; hệ thống tự động kiểm tra hạn mức ngân sách và tạm giữ ngân sách (`tempReservedAmount`). Thực thi quy tắc **Không tự phê duyệt (No Self-Approval — GOV-01)**.
3. **Tìm nguồn & Thu thập Báo giá (Sourcing & Quotation Collection):** Chuyên viên mua sắm quản lý nhà cung cấp, thu thập nhiều báo giá kèm tài liệu đính kèm (hỗ trợ kéo thả).
4. **Đối sánh Báo giá Đa chiều (Side-by-Side Comparison):** Màn hình trực quan so sánh đơn giá, tổng tiền, bảo hành, thời gian giao hàng và thời hạn báo giá.
5. **Tư vấn AI Phân tích Báo giá (AI Quotation Advisory):** AI chấm điểm đa tiêu chí, phân tích đánh đổi (trade-offs) về chi phí, rủi ro và chất lượng (Advisory Only — con người giữ quyền quyết định, AI không tự tạo PO).
6. **Trao thầu & Khóa Đơn đặt hàng (Human Award & PO Creation):** Chuyên viên mua sắm trao thầu; hệ thống sinh mã PO chuẩn (`PO-NUM-YYYY-YYYYMMDD-XXXXXXXX`) và khóa cứng 100% đơn giá.
7. **Nhận hàng Từng phần / Toàn bộ (Goods Receiving):** Ghi nhận biên bản nhận hàng thực tế.
8. **Đóng PR & Quyết toán Ngân sách (Close PR & Budget Settlement):** Chặn đóng PR nếu chưa nhận đủ 100% số lượng (`REQ-BR-11`); hoàn ứng ngân sách tạm giữ và ghi nhận chi phí thực tế (`spentAmount`).

---

## 🏛️ 3. Kiến trúc Hệ thống (Architecture)

```
                    ┌────────────────────────────────────────┐
                    │      Trình duyệt Người dùng (Client)   │
                    └───────────────────┬────────────────────┘
                                        │ HTTPS / WSS
                                        ▼
             ┌────────────────────────────────────────────────────┐
             │       Frontend SPA (Vercel / React 18 + Vite)      │
             │   - TypeScript, Tailwind CSS, Lucide Icons         │
             │   - Supabase Client SDK (Xác thực người dùng)     │
             └─────────────┬────────────────────────┬─────────────┘
                           │ Bearer JWT             │ Auth Login / Session
                           ▼                        ▼
┌───────────────────────────────────────┐  ┌───────────────────────────────────┐
│     Backend API (Railway / FastAPI)   │  │       Supabase Auth Service       │
│  - Python 3.11, Uvicorn, Pydantic v2  │  │   - Cấp JWT token (ES256)         │
│  - PyJWT + JWKS Verification (5.0s)   │  │   - Public JWKS Endpoint          │
│  - Server-Side RBAC (19 endpoints)    │  └─────────────────┬─────────────────┘
│  - AI Advisory Engine (Heuristic /    │                    │
│    Gemini fallback)                   │                    │
│  - Prisma Client Python v0.15.0       │                    │
└──────────────────┬────────────────────┘                    │
                   │ Transaction / Row Locks (SELECT FOR UPDATE)
                   ▼                                         │
┌─────────────────────────────────────────────────────────┐  │
│        Supabase Cloud PostgreSQL Database               │◄─┘
│  - Bảng User, Department, PR, Quotation, PO, Receiving  │
│  - Ánh xạ authUserId <-> Supabase Auth UID              │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 4. Yêu cầu Môi trường (Prerequisites)

Để chạy dự án ở môi trường cục bộ (Local Development), máy tính cần cài đặt:

- **Node.js:** Phiên bản `>= 18.x` (Khuyến nghị `20.x` hoặc `24.x` LTS) và `npm`.
- **Python:** Phiên bản `>= 3.11` (Khuyến nghị `3.11.x` hoặc `3.12.x`).
- **Git:** Để quản lý mã nguồn.
- **Trình duyệt Chrome / Chromium:** Để chạy kiểm thử giao diện tự động.
- *(Tùy chọn)* **Docker & Docker Compose:** Chỉ cần thiết nếu muốn chạy PostgreSQL local thay vì kết nối Supabase Cloud.

---

## 🔑 5. Biến Môi trường (Environment Variables)

Hệ thống sử dụng các tệp `.env` riêng biệt cho frontend và backend. **Tuyệt đối không lưu trữ thông tin mật (API Keys bí mật) lên kho mã nguồn công khai.**

### 5.1. Backend (`backend/.env`)

Tham khảo mẫu tại [`backend/.env.example`](backend/.env.example):

| Tên biến | Mục đích | Bắt buộc / Tùy chọn | Giá trị mẫu / Ghi chú |
|---|---|---|---|
| `DATABASE_URL` | Chuỗi kết nối PostgreSQL (Session mode hoặc Pooler) | **Bắt buộc** | `postgresql://postgres:[PASS]@[HOST]:[PORT]/postgres` |
| `SUPABASE_URL` | Địa chỉ gốc dự án Supabase để tải khóa công khai JWKS | **Bắt buộc** | `https://[PROJECT-REF].supabase.co` |
| `LLM_API_KEY` | Khóa API Google Gemini cho tính năng tư vấn | *Tùy chọn* | Nếu không có, hệ thống tự động kích hoạt Heuristic Fallback (78% confidence) |
| `AI_PROVIDER` | Bộ xử lý AI (`gemini` hoặc `mock`) | *Tùy chọn* | Mặc định: `gemini` |
| `PORT` | Cổng lắng nghe của máy chủ HTTP | *Tùy chọn* | Mặc định: `8000` (Local) hoặc do Railway cấp tự động |

### 5.2. Frontend (`frontend/.env`)

Tham khảo mẫu tại [`frontend/.env.example`](frontend/.env.example):

| Tên biến | Mục đích | Bắt buộc / Tùy chọn | Giá trị mẫu / Ghi chú |
|---|---|---|---|
| `VITE_SUPABASE_URL` | Địa chỉ dự án Supabase để đăng nhập | **Bắt buộc** | `https://[PROJECT-REF].supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Khóa Public Anonymous của Supabase | **Bắt buộc** | Lấy từ Supabase Dashboard -> Project API |
| `VITE_API_URL` | Địa chỉ Backend API | *Tùy chọn* | Mặc định trỏ Cloud Railway hoặc `http://localhost:8000` khi chạy backend local |

---

## 🚀 6. Hướng dẫn Cài đặt & Chạy Cục bộ (Local Setup)

### Bước 1: Sao chép kho mã nguồn
```bash
git clone https://github.com/thgnud1022/group-01-project.git
cd group-01-project
git checkout final-delivery
```

### Bước 2: Cài đặt và Khởi chạy Backend
```bash
cd backend

# Khởi tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo:
# Trên Windows (PowerShell/CMD):
.venv\Scripts\activate
# Trên Linux / macOS:
source .venv/bin/activate

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Cấu hình biến môi trường
cp .env.example .env
# Chỉnh sửa backend/.env với DATABASE_URL và SUPABASE_URL của bạn

# Sinh mã nguồn Prisma Client
prisma generate

# Ánh xạ tài khoản người dùng Supabase với CSDL (Idempotent seed)
python scripts/seed_auth_users.py

# Khởi động máy chủ phát triển
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs tương tác: [http://localhost:8000/docs](http://localhost:8000/docs)
- Kiểm tra trạng thái: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Bước 3: Cài đặt và Khởi chạy Frontend
Mở một cửa sổ dòng lệnh mới từ thư mục gốc dự án:
```bash
cd frontend

# Cài đặt gói npm
npm install

# Cấu hình biến môi trường
cp .env.example .env
# Chỉnh sửa frontend/.env nếu cần trỏ VITE_API_URL về http://localhost:8000

# Khởi chạy giao diện phát triển
npm run dev
```
- Mở trình duyệt tại: [http://localhost:5173](http://localhost:5173)

---

## 🔐 7. Xác thực & Tài khoản Demo (Authentication & Roles)

Hệ thống áp dụng mô hình phân quyền bảo mật máy chủ nghiêm ngặt (**Zero-Trust Server-Side RBAC**). Dropdown chọn vai trò ở giao diện chỉ hỗ trợ chuyển đổi ngữ cảnh trải nghiệm; mọi thao tác ghi dữ liệu đều được máy chủ kiểm tra đối chiếu qua JWT:

| Tài khoản Email | Mật khẩu mẫu | Vai trò (Role) | Phòng ban | Quyền hạn chính |
|---|---|---|---|---|
| `employee@company.com` | `password123` | `EMPLOYEE` | Phòng CNTT | Tạo yêu cầu mua sắm (PR), xem danh sách PR của mình |
| `manager@company.com` | `password123` | `MANAGER` | Phòng CNTT | Phê duyệt / Từ chối / Yêu cầu chỉnh sửa PR phòng mình (No Self-Approval) |
| `procurement@company.com` | `password123` | `PROCUREMENT` | Mua sắm | Quản lý nhà cung cấp, thu thập báo giá, so sánh, nhận tư vấn AI, trao thầu, tạo PO |
| `finance@company.com` | `password123` | `FINANCE` | Tài chính | Giám sát ngân sách phòng ban, kiểm tra hóa đơn và quyết toán |
| `admin@company.com` | `password123` | `ADMIN` | Quản trị | Quản trị hệ thống, giám sát toàn diện |

---

## 🧪 8. Hướng dẫn Chạy Kiểm thử (Automated Testing)

Toàn bộ các bộ kiểm thử dưới đây đã được thẩm định độc lập và đạt kết quả 100% Green trên live stack:

### 8.1. Kiểm thử Hồi quy Backend (Backend Pytest)
Đạt **133 / 133 PASSED** trên toàn bộ 9 test suites (RBAC, JWT, PO Guards, Lifecycle, Quotations, AI Service):
```bash
cd backend
pytest -v
```

### 8.2. Kiểm thử Tự động Chu trình Giao diện (Browser E2E Lifecycle)
Đạt **14 / 14 bước nghiệp vụ PASSED** sử dụng trình điều khiển Puppeteer (`puppeteer-core`):
```bash
cd frontend
node scripts/test_final_full_lifecycle_e2e.js
```
*Lưu ý:* Bằng chứng 8 ảnh chụp màn hình tương ứng được lưu trữ tại thư mục [`docs/evidence/browser/`](docs/evidence/browser/). Kịch bản Playwright có tồn tại trong mã nguồn nhưng chưa được kiểm chứng độc lập trong đợt nghiệm thu này.

### 8.3. Kiểm thử Khói Môi trường Công khai (Public Cloud Smoke Test)
Đạt **9 / 9 tiêu chí PASSED** trực tiếp trên URL công khai Vercel & Railway:
```bash
python scratch/ai089_public_smoke.py
```

---

## 🛠️ 9. Xử lý Sự cố Thường gặp (Troubleshooting)

- **Lỗi `401 Unauthorized` hoặc `"User not found in system"`:**
  - *Nguyên nhân:* Tài khoản Supabase Auth chưa được ánh xạ vào trường `authUserId` của bảng `User` trong PostgreSQL.
  - *Khắc phục:* Chạy kịch bản `python scripts/seed_auth_users.py` từ thư mục `backend`. Trên Railway, bước này đã được tích hợp tự động vào `start.sh`.
- **Lỗi `502 Bad Gateway` hoặc không kết nối được CSDL:**
  - *Nguyên nhân:* Sai cấu hình `DATABASE_URL` hoặc kết nối trực tiếp bị chặn tường lửa IPv4.
  - *Khắc phục:* Sử dụng chuỗi kết nối qua Supabase IPv4 Connection Pooler (cổng 6543) với tham số `?pgbouncer=true`.
- **Lỗi CORS trên Trình duyệt:**
  - *Nguyên nhân:* Backend chặn Origin của Frontend hoặc dùng wildcard `allow_origins=["*"]` xung đột với `allow_credentials=True`.
  - *Khắc phục:* Đã được chuẩn hóa trong `backend/app/main.py` với danh sách explicit allowed origins (`ALLOWED_ORIGINS`).
- **Giao diện báo `DNS_HOSTNAME_RESOLVE_FAILED` trên Vercel:**
  - *Nguyên nhân:* Vercel proxy không tìm thấy host backend.
  - *Khắc phục:* Đặt biến môi trường `VITE_API_URL=https://group-01-project-production.up.railway.app` trong Vercel Project Settings để frontend gọi trực tiếp Railway API.
- **Lỗi F5 trang trắng hoặc 404 khi điều hướng tĩnh:**
  - *Khắc phục:* Đảm bảo tệp `frontend/vercel.json` có quy tắc rewrite toàn bộ route về `/index.html`.

---

## 📚 10. Hồ sơ Nghiệm thu & Tài liệu Dự án

- **Release Notes & Changelog:** [`docs/07-release/release-notes.md`](docs/07-release/release-notes.md)
- **Vận hành & Khởi chạy Chi tiết:** [`docs/07-release/runbook.md`](docs/07-release/runbook.md)
- **Báo cáo Kiểm toán Chất lượng Độc lập (Final QA Gate):** [`docs/evidence/FINAL_QA_GATE_REPORT.md`](docs/evidence/FINAL_QA_GATE_REPORT.md)
- **Báo cáo Tuân thủ Môn học (Course Compliance):** [`docs/OUTPUT_BAOCAO.md`](docs/OUTPUT_BAOCAO.md)
- **Ma trận Truy xuất Nguồn gốc AI:** [`docs/AI_USAGE_TRACEABILITY.md`](docs/AI_USAGE_TRACEABILITY.md)
- **Nhật ký Sử dụng AI & Retrospective:** [`docs/logs/ai-usage-log.md`](docs/logs/ai-usage-log.md)

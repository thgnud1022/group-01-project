# RUNBOOK & DEPLOYMENT GUIDE: Hướng Dẫn Vận Hành & Khởi Chạy Hệ Thống

## 1. Yêu Cầu Tiền Trạm (Prerequisites)
* Docker Desktop & Docker Compose (Đang chạy WSL2 trên Windows).
* Node.js 24.x LTS & `npm`.
* Python 3.13 & `uv` package manager.

## 2. Các Bước Khởi Chạy Nhanh (Quick Start in 3 Minutes)

### Bước 1: Khởi động Database PostgreSQL
```bash
cd d:\THUDDN\group-01-project
docker compose up -d
```
*Kiểm tra:* `docker compose ps` phải thấy container `db` ở trạng thái `running` (Cổng 5432).

### Bước 2: Setup & Khởi chạy Backend FastAPI
```bash
cd d:\THUDDN\group-01-project\backend
uv sync
uv run python seed.py
uv run fastapi dev app/main.py
```
* Backend sẽ lắng nghe tại: `http://localhost:8000`
* Swagger OpenAPI Docs tại: `http://localhost:8000/docs`

### Bước 3: Setup & Khởi chạy Frontend React + Vite
```bash
cd d:\THUDDN\group-01-project\frontend
npm install
npm run dev
```
* Web Application mở tại: `http://localhost:5173`

## 3. Kiểm Trụ & Chạy Automated Tests

### Chạy API Unit Tests
```bash
cd d:\THUDDN\group-01-project\backend
uv run pytest -v
```

### Chạy Playwright E2E Tests
```bash
cd d:\THUDDN\group-01-project\frontend
npx playwright test
```

## 4. Tài Khoản Seed Demo Khởi Tạo Sẵn (Seed Credentials)
* `employee@company.com` / `password123` (Role: EMPLOYEE - Phong IT)
* `manager@company.com` / `password123` (Role: MANAGER - Phong IT)
* `procurement@company.com` / `password123` (Role: PROCUREMENT)
* `finance@company.com` / `password123` (Role: FINANCE)
* `admin@company.com` / `password123` (Role: ADMIN)

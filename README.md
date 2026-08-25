# AI Procurement & Purchase Approval System (Group 01)

Dự án môn học **Thực hành Lập trình Ứng dụng Doanh nghiệp (MIS3032_1 - Phiên bản 2026)**.

## 🚀 Quick Start (Hướng dẫn chạy nhanh)

1. **Khởi chạy Database PostgreSQL:**
   ```bash
   docker compose up -d
   ```

2. **Chạy Backend FastAPI:**
   ```bash
   cd backend
   uv sync
   uv run python seed.py
   uv run fastapi dev app/main.py
   ```
   * Access API Docs: `http://localhost:8000/docs`

3. **Chạy Frontend React:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   * Access App: `http://localhost:5173`

4. **Chạy Kiểm Thử:**
   * Backend Unit Tests: `cd backend && uv run pytest -v`
   * Frontend E2E Tests: `cd frontend && npx playwright test`

## 📚 Project Vault & Documentation
Toàn bộ tài liệu tri thức, sơ đồ kiến trúc và nhật ký AI được lưu trữ tại thư mục [`docs/`](file:///d:/THUDDN/group-01-project/docs/00-project-index.md).

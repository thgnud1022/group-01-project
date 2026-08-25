# ADR-002: Kiến Trúc Backend FastAPI & PostgreSQL Container (Backend Stack)

* **Trạng thái:** Accepted
* **Ngày quyết định:** 2026-08-25
* **Người quyết định:** Lead Developer (Thành viên 4) & cả Nhóm 1

## Bối Cảnh (Context)
Dự án cần một backend hiệu năng cao, hỗ trợ tốt cho việc xử lý bất đồng bộ (async), tích hợp thư viện xử lý tài liệu PDF/AI và kiểm soát nghiêm ngặt các Business Rules về ngân sách tài chính.

## Quyết Định (Decision)
1. **Framework:** Python 3.13 + FastAPI.
2. **Package Manager:** `uv` (tốc độ cài đặt package cực nhanh, quản lý `.venv` và `pyproject.toml` thống nhất).
3. **Database & ORM:** PostgreSQL 18 vận hành qua Docker Compose & Prisma Client (`prisma-client-js` / `prisma-py`).
4. **Auth & Security:** JWT Token + bcrypt password hashing.

## Hậu Quả & Đánh Giá (Consequences)
* **Tích cực:** Tuân thủ 100% quy định Môi trường chuẩn của môn học, dễ dàng viết API test với `pytest` và E2E test với `Playwright`.
* **Hạn chế:** Thành viên nhóm cần nắm vững async/await và Prisma migration workflow.

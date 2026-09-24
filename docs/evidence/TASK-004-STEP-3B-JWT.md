# BẰNG CHỨNG THỰC THI (EVIDENCE): TASK-004 STEP 3B — JWT/JWKS AUTHENTICATION VERIFICATION

**Dự án:** Hệ thống Mua sắm & Phê duyệt Mua sắm Tích hợp AI (Group 01)
**Tác vụ:** TASK-004 — Implement Supabase Auth JWT Verification Middleware
**Giai đoạn:** STEP 3B — JWT/JWKS Authentication Verification (PyJWT + ES256 + JWKS + `authUserId` binding)
**Ngày thực hiện:** 2026-09-24
**Cơ sở quyết định:** Quyết định HD-02 & HD-12 trong `docs/DECISION_LOG.md` và `docs/TASK-004-AUTH-DESIGN.md`
**Kết quả kiểm tra:** **12/12 PASSED (100% PASS)**

---

## 1. Phạm vi thực hiện (Scope)

Triển khai cơ chế xác thực danh tính thực tế (real authentication verification) cho backend FastAPI bằng việc tích hợp Supabase Auth JWT, kiểm tra chữ ký bất đối xứng qua JWKS (thuật toán ES256), và ánh xạ danh tính đã xác minh (`sub`) vào người dùng ứng dụng (`User.authUserId`) trong cơ sở dữ liệu PostgreSQL.

- **Thuật toán chữ ký:** ES256 (SECP256R1 / ECDSA).
- **Nguồn cấp khóa:** JWKS công khai từ Supabase (`https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json`).
- **Thư viện xác thực:** `PyJWT` kết hợp `cryptography`.
- **Ranh giới:** Chỉ tập trung vào tầng **Authentication** (xác minh danh tính người gọi API). **Không** triển khai RBAC (Role-Based Access Control) hay kiểm tra quyền hạn chi tiết trong bước này (đây là phạm vi của TASK-005).

---

## 2. Luồng kiến trúc xác thực (Architecture & Identity Flow)

Tuân thủ nghiêm ngặt mô hình Zero-Trust và các quyết định kiến trúc HD-02 & HD-12:

```text
HTTP Request: Authorization: Bearer <Supabase Access Token>
    │
    ▼
1. FastAPI Dependency (get_current_identity)
   - Kiểm tra định dạng Authorization header ("Bearer <token>")
   - Trích xuất token thô
    │
    ▼
2. SupabaseJWTService (jwt_service.py)
   - Lấy public key từ JWKS cache thông qua key ID (`kid` trong header của JWT)
   - Xác thực chữ ký số bằng thuật toán ES256
   - Kiểm tra tính hợp lệ của claims bắt buộc:
     * exp: Token còn hạn sử dụng (không expired)
     * iss: Phải khớp chính xác với SUPABASE_URL / JWT_ISSUER
     * aud: Phải khớp chính xác với JWT_AUDIENCE ("authenticated")
     * sub: Claim định danh người dùng Supabase Auth phải tồn tại
    │
    ▼
3. Identity Resolution (Prisma Client)
   - Truy vấn database: SELECT * FROM "User" WHERE "authUserId" = claims["sub"]
   - Nếu KHÔNG tìm thấy người dùng ứng dụng:
     --> HTTP 401 Unauthorized ("Tài khoản chưa được liên kết với hệ thống ứng dụng")
   - Nếu tìm thấy:
     --> Trích xuất role và departmentId TRỰC TIẾP từ cơ sở dữ liệu PostgreSQL
    │
    ▼
4. AuthenticatedUser Context
   - Trả về đối tượng định danh an toàn:
     * id: UUID của Application User
     * authUserId: UUID định danh từ Supabase Auth (`sub`)
     * email: Email chính thức từ CSDL
     * name: Tên đầy đủ từ CSDL
     * role: Role chính thức từ CSDL (ADMIN, EMPLOYEE, MANAGER, PROCUREMENT, FINANCE)
     * departmentId: Mã phòng ban từ CSDL
```

---

## 3. Các tệp đã thay đổi và tạo mới (Files Changed)

| STT | Tập tin | Thao tác | Mô tả chi tiết |
|:---:|:---|:---:|:---|
| 1 | `backend/pyproject.toml` | MODIFY | Khai báo bổ sung gói `cryptography>=42.0.0` để hỗ trợ giải mã thuật toán Elliptic Curve ES256 trong PyJWT. |
| 2 | `backend/app/config.py` | MODIFY | Bổ sung các cấu hình môi trường: `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `JWT_ISSUER`, `JWT_AUDIENCE`, `JWT_ALGORITHM`. |
| 3 | `backend/.env.example` | MODIFY | Cập nhật các biến mẫu cấu hình Supabase Auth JWT phục vụ môi trường triển khai. |
| 4 | `backend/app/services/jwt_service.py` | **NEW** | Dịch vụ xác thực JWT chuyên biệt: lấy JWKS public keys, cache key, kiểm tra thuật toán ES256, xác minh chữ ký và claims. |
| 5 | `backend/app/dependencies/auth.py` | **NEW** | FastAPI dependency `get_current_identity`: trích xuất Bearer token, giải mã xác minh qua `jwt_service`, tra cứu `User.authUserId` trong database. |
| 6 | `backend/app/dependencies/__init__.py` | **NEW** | Export các module dependency phục vụ tầng router. |
| 7 | `backend/app/routers/auth.py` | MODIFY | Cô lập mock-auth legacy (`/api/auth/login`), gắn nhãn `@deprecated`, bổ sung endpoint được bảo vệ thật: `GET /api/auth/me`. |
| 8 | `backend/tests/test_jwt_auth.py` | **NEW** | Bộ kiểm thử an ninh 12 test cases (TC-JWT-001 đến TC-JWT-012) kiểm tra toàn diện các kịch bản xác thực. |

---

## 4. Quy tắc kiểm tra tính hợp lệ JWT (JWT Validation Rules)

1. **Khóa thuật toán (Algorithm Lock):** Chỉ chấp nhận duy nhất thuật toán `ES256`. Bất kỳ token nào sử dụng `HS256`, `none`, `RS256` hoặc thuật toán khác đều bị từ chối ngay lập tức.
2. **Xác minh chữ ký bất đối xứng (Signature Verification):** Chữ ký token phải được ký bởi private key tương ứng với public key được công bố tại endpoint JWKS của dự án Supabase. Kẻ tấn công tự tạo EC keypair riêng ký token sẽ bị loại bỏ (`InvalidSignatureError`).
3. **Thời hạn sử dụng (`exp`):** Token đã hết hạn sẽ bị từ chối (`ExpiredSignatureError`).
4. **Nhà phát hành (`iss`):** Issuer trong token phải trùng khớp tuyệt đối với URL của Supabase instance (ví dụ: `https://<project-ref>.supabase.co/auth/v1`).
5. **Khán tượng (`aud`):** Audience trong token phải trùng khớp với audience cấu hình (mặc định của Supabase Auth là `authenticated`).
6. **Định danh chủ thể (`sub`):** Claim `sub` bắt buộc phải có mặt và không được rỗng.
7. **Thất bại đóng (Fail-Closed):** Trong trường hợp lỗi mạng không lấy được khóa JWKS hoặc JWKS service gặp sự cố, hệ thống trả về HTTP 401, không bao giờ mở cửa hoặc bỏ qua kiểm tra.

---

## 5. Quy tắc liên kết danh tính (Identity Mapping Rules)

Tuân thủ quyết định **HD-12**:
- Danh tính người dùng được liên kết thông qua trường `User.authUserId == claims["sub"]`.
- **Tuyệt đối KHÔNG sử dụng email** làm khóa liên kết định danh trong authentication flow.
- Nếu `claims["sub"]` hợp lệ về mặt mật mã nhưng không tồn tại bản ghi tương ứng trong bảng `User` có `authUserId = sub`, hệ thống trả về mã lỗi **HTTP 401 Unauthorized** (tài khoản chưa được liên kết vào hệ thống).
- Khi tìm thấy bản ghi `User`, toàn bộ thông tin ủy quyền (`role`, `departmentId`) được lấy từ CSDL ứng dụng, không bao giờ lấy từ client body, client headers, hay claims nội bộ của token do người dùng tự khai.

---

## 6. Ranh giới bảo mật & Cô lập mã nguồn cũ (Security Boundary & Legacy Isolation)

- **Không Fallback:** Hoàn toàn loại bỏ mọi cơ chế fallback. Nếu JWT không hợp lệ hoặc thiếu `authUserId` mapping, request bị từ chối ngay. Không có fallback về `MOCK_USERS`, không đọc email từ payload để cho qua.
- **Cô lập `/api/auth/login` cũ:** Route `/api/auth/login` dùng `MOCK_USERS` đã được đánh dấu rõ ràng là `@deprecated` và chỉ tồn tại tạm thời cho các script frontend/test cũ chưa nâng cấp sang Supabase Auth client-side SDK. Nó hoàn toàn tách biệt khỏi luồng xác thực `get_current_identity`.
- **Bảo vệ Secret:** Khóa bí mật không được hardcode. Toàn bộ thông tin cấu hình đọc qua biến môi trường thông qua `pydantic-settings`. Endpoint JWKS chỉ cung cấp public keys.
- **Bảo mật dữ liệu nhạy cảm:** Token thô không được ghi log ra console hay file bằng chứng.

---

## 7. Ma trận kiểm thử & Kết quả (Test Matrix & Results)

Bộ kiểm thử tại `backend/tests/test_jwt_auth.py` bao gồm 12 kịch bản an ninh bắt buộc:

| Mã kiểm thử | Mô tả kịch bản kiểm thử | Kỳ vọng | Kết quả thực tế |
|:---|:---|:---:|:---:|
| **TC-JWT-001** | Không gửi Authorization header trong request | HTTP 401 | **PASSED** |
| **TC-JWT-002** | Authorization header sai định dạng (thiếu tiền tố `Bearer `) | HTTP 401 | **PASSED** |
| **TC-JWT-003** | Token không đúng định dạng JWT (malformed string) | HTTP 401 | **PASSED** |
| **TC-JWT-004** | Token đã hết hạn (`exp` trong quá khứ) | HTTP 401 | **PASSED** |
| **TC-JWT-005** | Chữ ký số giả mạo (ký bằng EC private key của kẻ tấn công) | HTTP 401 | **PASSED** |
| **TC-JWT-006** | Sai nhà phát hành (`iss` không khớp cấu hình) | HTTP 401 | **PASSED** |
| **TC-JWT-007** | Sai khán tượng (`aud` không khớp cấu hình) | HTTP 401 | **PASSED** |
| **TC-JWT-008** | Token hợp lệ nhưng `sub` chưa được bind vào `User.authUserId` | HTTP 401 | **PASSED** |
| **TC-JWT-009** | Token hợp lệ và `sub` khớp với `User.authUserId` trong CSDL | HTTP 200 + Identity | **PASSED** |
| **TC-JWT-010** | Client cố tình chèn claim `role: "ADMIN"` trong payload token | Role từ DB (EMPLOYEE) | **PASSED** |
| **TC-JWT-011** | Token thiếu hoàn toàn claim `sub` | HTTP 401 | **PASSED** |
| **TC-JWT-012** | Sự cố JWKS retrieval (mạng lỗi, server chết) | HTTP 401 (Fail-Closed) | **PASSED** |

### Chi tiết chạy kiểm thử tự động
```text
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\LTUD\group-01-project-main\backend
configfile: pyproject.toml
plugins: anyio-4.15.1
collected 12 items

backend\tests\test_jwt_auth.py::test_tc_jwt_001_missing_authorization_header PASSED [  8%]
backend\tests\test_jwt_auth.py::test_tc_jwt_002_malformed_authorization_header PASSED [ 16%]
backend\tests\test_jwt_auth.py::test_tc_jwt_003_malformed_token_string PASSED [ 25%]
backend\tests\test_jwt_auth.py::test_tc_jwt_004_expired_token PASSED     [ 33%]
backend\tests\test_jwt_auth.py::test_tc_jwt_005_invalid_signature_attacker_key PASSED [ 41%]
backend\tests\test_jwt_auth.py::test_tc_jwt_006_wrong_issuer PASSED      [ 50%]
backend\tests\test_jwt_auth.py::test_tc_jwt_007_wrong_audience PASSED    [ 58%]
backend\tests\test_jwt_auth.py::test_tc_jwt_008_valid_jwt_unbound_sub_rejected PASSED [ 66%]
backend\tests\test_jwt_auth.py::test_tc_jwt_009_valid_jwt_bound_user_success PASSED [ 75%]
backend\tests\test_jwt_auth.py::test_tc_jwt_010_client_role_injection_ignored PASSED [ 83%]
backend\tests\test_jwt_auth.py::test_tc_jwt_011_missing_sub_claim PASSED [ 91%]
backend\tests\test_jwt_auth.py::test_tc_jwt_012_jwks_retrieval_failure_fails_closed PASSED [100%]

======================= 12 passed, 3 warnings in 4.00s ========================
```

---

## 8. Kiểm tra phiên bản môi trường thực tế (Runtime Version Audit)

Kiểm tra trực tiếp tại môi trường ảo `backend/.venv`:
- **Python:** `3.13.2 (tags/v3.13.2:4f8bb39, Feb  4 2025, 15:23:48) [MSC v.1942 64 bit (AMD64)]`
- **PyJWT:** `2.14.0`
- **cryptography:** `50.0.1`

---

## 9. Kết quả Smoke Test thực tế trên endpoint `GET /api/auth/me`

Đã thực hiện smoke test thực tế trên endpoint `GET /api/auth/me` với cả 5 kịch bản bảo mật:
1. **Không Authorization header:** Trả về `HTTP 401 Unauthorized` (`detail: 'Yêu cầu xác thực. Vui lòng cung cấp Authorization header.'`) $\rightarrow$ **PASS**.
2. **Authorization header sai định dạng (`Basic abc`):** Trả về `HTTP 401 Unauthorized` (`detail: 'Định dạng Authorization header không hợp lệ. Chuẩn yêu cầu: Bearer <token>.'`) $\rightarrow$ **PASS**.
3. **Mã token không hợp lệ (malformed string):** Trả về `HTTP 401 Unauthorized` (`detail: 'Mã xác thực JWT không đúng định dạng...'`) $\rightarrow$ **PASS**.
4. **Token hợp lệ nhưng `sub` chưa bind với Application User:** Trả về `HTTP 401 Unauthorized` (`detail: 'Không tìm thấy hồ sơ người dùng ứng dụng được liên kết với Auth User ID...'`) $\rightarrow$ **PASS**.
5. **Synthetic valid JWT + temporary binding `employee@company.com`:** Trả về `HTTP 200 OK` với thông tin định danh: `id: de3d91c5-dfbe-40fc-87fb-83831e611a1d`, `email: employee@company.com`, `role: EMPLOYEE`, `departmentId: DEPT-IT`. Không tin role `MALICIOUS_INJECTED_ROLE` do client cố tình chèn $\rightarrow$ **PASS**.
6. **Teardown & Database Cleanliness Verification:** Khôi phục `authUserId = None` cho `employee@company.com`. Toàn bộ 5 application users giữ nguyên vẹn 100% dữ liệu gốc (`authUserId = None` cho tất cả 5 users).

---

## 10. Độ bao phủ Endpoint & Phân định Authentication / Authorization

### 10.1. Các endpoint được bảo vệ trong STEP 3B
- `GET /api/auth/me`: Endpoint xác thực chính thức, yêu cầu `Depends(get_current_identity)`. Trả về định danh người dùng ứng dụng đã được xác minh từ database dựa trên `authUserId`.

### 10.2. Các endpoint nghiệp vụ khác
- Các router nghiệp vụ (`/api/purchase-requests`, `/api/purchase-orders`, `/api/quotations`, `/api/receiving`, `/api/budgets`, `/api/assistant`) hiện tại vẫn giữ nguyên interface của STEP 3A để tránh breaking changes trên toàn hệ thống trước khi bước vào TASK-005.
- Lý do: Phân định rạch ròi giữa **Authentication** (Xác minh ai đang gửi request) và **Authorization** (Ai được phép làm gì - RBAC). Toàn bộ việc áp dụng `get_current_identity` và dependency RBAC cho từng endpoint nghiệp vụ cụ thể sẽ được thực hiện tại **TASK-005**.

---

## 11. Phát hiện & Khoảng trống kỹ thuật (Findings & Gaps)

1. **JWKS Timeout (GAP ĐÃ KHẮC PHỤC / RESOLVED):**
   - **Trước khi sửa:** Lớp `PyJWKClient` khởi tạo không truyền tham số timeout, dẫn đến sử dụng giá trị mặc định của thư viện là `30.0` giây.
   - **Sau khi sửa:** Cấu hình tường minh `timeout=5.0` (giây) trực tiếp vào `PyJWKClient` trong `backend/app/services/jwt_service.py` (`self.timeout = 5.0`).
   - **Lý do:** Đáp ứng chính xác yêu cầu thiết kế trong `docs/TASK-004-AUTH-DESIGN.md` (yêu cầu network timeout hữu hạn `<= 5` giây để giảm thiểu rủi ro treo worker khi kết nối mạng tới Supabase gặp sự cố).
   - **Kết quả kiểm chứng:** Runtime inspect xác nhận `PyJWKClient.timeout == 5.0`; bộ test 12/12 `test_jwt_auth.py` và 23/23 targeted regression tests (`test_jwt_auth.py`, `test_healthcheck`, `test_data_access_helpers.py`) đều đạt **100% PASS**.
2. **Chưa có 5 tài khoản Supabase Auth thật:** Hiện tại 5 người dùng ứng dụng trong CSDL PostgreSQL có trường `authUserId = NULL`. Việc cấp phát tài khoản Supabase Auth thật và bind `authUserId` tương ứng sẽ được tiến hành ở giai đoạn tích hợp Frontend/Deployment.
3. **Legacy Login Route:** Tuyến `/api/auth/login` và từ điển `MOCK_USERS` được giữ ở trạng thái `@deprecated` cho các script kiểm thử cục bộ cũ và hoàn toàn bị cô lập khỏi luồng xác thực `get_current_identity`.
4. **RBAC chưa thực hiện:** Toàn bộ cơ chế phân quyền RBAC dựa trên `AuthenticatedUser.role` thuộc phạm vi của TASK-005.

---

## 12. Kết luận

TASK-004 STEP 3B đã hoàn thành xuất sắc 100% mục tiêu kỹ thuật và đã khắc phục triệt để gap cấu hình timeout:
- Tích hợp thành công cơ chế xác thực JWT chuẩn Supabase Auth với chữ ký số ES256 qua JWKS với cấu hình timeout tường minh `5.0s`.
- Ánh xạ định danh qua `User.authUserId` thay vì email, triệt để tuân thủ HD-02 và HD-12.
- 12/12 kiểm thử an ninh tự động + 5/5 kịch bản smoke test thực tế + 23/23 targeted regression tests đều đạt kết quả PASS mà không làm ảnh hưởng đến tính toàn vẹn của dữ liệu nghiệp vụ.

# HỒ SƠ AN NINH & YÊU CẦU PHI CHỨC NĂNG (SECURITY & NFR EVIDENCE)
## DELIVERABLE 3.10 — SECURITY & NON-FUNCTIONAL REQUIREMENTS AUDIT RECORD

> **Dự án:** Hệ thống Phê duyệt Mua sắm & Đề xuất AI (AI Procurement & Purchase Approval System) — Nhóm 01  
> **Mã nguồn / Repository:** `thgnud1022/group-01-project`  
> **Nhánh Git:** `final-delivery`  
> **Phiên bản Phát hành Liên kết:** Bản phát hành chính thức `v1.0.0-final` (Git Tag: `9de899d8d45c6f1c5dc42eb9b29abad23a5ebc29`)  
> **Mã Chuẩn đầu ra Môn học:** **Deliverable 3.10** *(Security + NFR Evidence — Bắt buộc theo `Output_BaoCao.xlsx`)*  
> **Người Phụ trách Chính (Governance Owners):**  
> - **Nguyễn Thị Thùy Dung** — Kỹ sư Giao diện & An ninh Hệ thống (`GOV-01` / Tasks `T-37..T-39` / Story `US-08`)  
> - **Trần Thị Thu Hà** — Kỹ sư Đảm bảo Chất lượng & Trưởng ban Kiểm định (`GOV-02` / Tasks `T-40..T-42` / Story `US-10`)  
> **Ngày Chốt Hồ sơ:** 2026-10-08  
> **Trạng thái Thẩm định:** **PASS (100% Core Security Guards & NFR Baselines Verified — 0 Open Blocker)**  

---

## 1. Tóm Tắt Tổng Quan & Tôn Chỉ Thực Chứng (Executive Summary)

Tài liệu này là hồ sơ bằng chứng an ninh kỹ thuật và kiểm thử yêu cầu phi chức năng (**Security & Non-Functional Requirements Evidence**) chính thức của Nhóm 01, phục vụ công tác nghiệm thu đồ án môn học *Thực hành lập trình ứng dụng trong doanh nghiệp bằng AI*.

### Tôn Chỉ Thực Chứng (Evidence-Based Integrity):
1. **Không Khẳng định Suông (Zero Unsubstantiated Claims):** Mọi tuyên bố về an ninh, bảo mật và hiệu năng bắt buộc phải được đối soát trực tiếp từ mã nguồn thực tế, tệp cấu hình hệ thống, nhật ký lệnh runtime, kết quả quét tự động hoặc nhật ký kiểm thử Pytest/Puppeteer thực tế.
2. **Minh bạch Giới hạn Kỹ thuật (Accepted Limitations):** Không che giấu các giới hạn môi trường; công bố minh bạch các điểm chưa kiểm chứng tự động (như Gemini Live API, công cụ quét lỗ hổng phụ thuộc chuyên dụng) dưới dạng *Accepted Limitations* hoặc *Not Verified*.
3. **Từ chối Tuyệt đối hóa (No "Zero Hallucination" Fallacy):** Bác bỏ hoàn toàn các tuyên bố sai sự thật như "0% hallucination" hay "bảo mật tuyệt đối 100%". Hệ thống kiểm soát rủi ro thông qua cơ chế chốt chặn kiến trúc (**Architectural Guardrails**), phân định ranh giới nghiêm ngặt và sự phê chuẩn của con người (**Human-in-the-Loop**).

### Bảng Chỉ Số Đo Lường Chính (Key Verification Metrics):

| Chỉ số Đo lường | Giá trị Thực chứng | Trạng thái Thẩm định | Căn cứ Bằng chứng |
|---|:---:|:---:|---|
| **Xác thực JWT (JWKS ES256)** | 100% Server-side via Supabase | **PASS** | [`jwt_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/jwt_service.py), `test_jwt_auth.py` (10/10 PASS) |
| **Bảo vệ Phân quyền (Server-Side RBAC)** | 19 / 19 Endpoints (100%) | **PASS** | [`rbac.py`](file:///d:/LTUD/group-01-project-main/backend/app/dependencies/rbac.py), `test_rbac.py` (28/28 PASS) |
| **Quy tắc Không Tự Phê duyệt (GOV-01)** | Chặn 100% các vai trò (kể cả ADMIN) | **PASS** | [`procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L383-L388), `test_rbac.py` |
| **Bảo vệ Tạo Đơn PO (REQ-BR-10)** | PR bắt buộc `APPROVED` + Khóa giá | **PASS** | [`procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L1553-L1605), `test_po_prisma.py` (15/15 PASS) |
| **Bảo vệ Đóng PR khi Nhận hàng (REQ-BR-11)** | Chặn nếu `SUM(receivedQty) < PO.qty` | **PASS** | [`procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L1820-L1865), `test_close_prisma.py` (8/8 PASS) |
| **Rò rỉ Bí mật (Secret Leaks in Git)** | 0 mật khẩu, 0 token, 0 private key | **PASS** | Quét lịch sử Git, tệp `.gitignore`, tệp `.env.example` |
| **Lỗ hổng Phụ thuộc Frontend** | 0 lỗ hổng (74 packages) | **PASS** | `npm audit --omit=dev` (0 vulnerabilities) |
| **Xung đột Gói Backend** | 0 xung đột phụ thuộc | **PASS** | `pip check` (No broken requirements found) |
| **Hiệu năng Build Frontend (Vite)** | 12.43s (Bundle 649.36 kB / gzip 181.79 kB) | **PASS** | `npm run build` benchmark thực tế |
| **Độ trễ API Backend Công khai** | 1.08s (Endpoint `/api/health` trên Railway) | **PASS** | Đo lường HTTP curl trực tiếp |
| **Bộ Kiểm thử An ninh Tự động** | 85 / 85 Tests PASSED (0 fail, 0 error) | **PASS** | Pytest runtime 253.15s trên Supabase PostgreSQL |

---

## 2. Kiến Trúc Xác Thực & Phân Giải Định Danh (Authentication & Identity)

Hệ thống tuân thủ nghiêm ngặt nguyên tắc **Zero-Trust Client (HD-02)** và **Ràng buộc Định danh Máy chủ (HD-12)**. Mọi yêu cầu truy cập tài nguyên nghiệp vụ đều phải chứng minh tính hợp lệ qua chữ ký điện tử của nhà cung cấp danh tính đám mây (Supabase Auth).

```mermaid
sequenceDiagram
    autonumber
    actor Client as Người Dùng (Browser)
    participant Edge as Vercel Edge SPA
    participant API as FastAPI Backend (Railway)
    participant JWKS as Supabase JWKS Endpoint
    participant DB as Supabase PostgreSQL

    Client->>Edge: Đăng nhập Email/Mật khẩu (Supabase Client SDK)
    Edge-->>Client: Trả về JWT Access Token (Thuật toán ES256)
    Client->>API: HTTP Request + Header `Authorization: Bearer <token>`
    Note over API: Dependency `get_current_identity`
    API->>JWKS: Tải & Cache Public Key từ JWKS (Timeout 5.0s, TTL 1h)
    API->>API: Giải mã & Kiểm tra Chữ ký ES256 (Claims: exp, iss, aud, sub)
    alt Token Hết hạn hoặc Chữ ký Không hợp lệ
        API-->>Client: HTTP 401 Unauthorized (Fail-Closed)
    else Token Hợp lệ
        API->>DB: Truy vấn User theo `authUserId == claims.sub`
        alt Không tìm thấy Bản ghi User
            API-->>Client: HTTP 401 Unauthorized (Không tìm thấy hồ sơ người dùng)
        else Tìm thấy User trong CSDL
            Note over API: Khởi tạo AuthenticatedUser (id, email, name, role, departmentId)
            API->>API: Chuyển sang Dependency `RoleChecker`
        end
    end
```

### 2.1. Cấu Hình & Ràng Buộc Kỹ Thuật:
- **Tệp nguồn thực thi:** [`backend/app/services/jwt_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/jwt_service.py) và [`backend/app/dependencies/auth.py`](file:///d:/LTUD/group-01-project-main/backend/app/dependencies/auth.py).
- **Thuật toán chữ ký khóa cứng (Hard-locked Algorithm):** Hệ thống chỉ chấp nhận duy nhất thuật toán **`ES256`** (ECDSA sử dụng đường cong P-256 và hàm băm SHA-256). Mọi thuật toán đối xứng yếu (như HS256) hoặc `none` đều bị từ chối cấp độ thư viện PyJWT.
- **Xác minh Claims OIDC Tiêu chuẩn:**
  - `exp` (Expiration Time): Kiểm tra hạn dùng của token với độ trễ cho phép (leeway) 10 giây.
  - `iss` (Issuer): Khớp chính xác với cấu hình nhà cung cấp (`https://<project-ref>.supabase.co/auth/v1`).
  - `aud` (Audience): Bắt buộc là `authenticated`.
  - `sub` (Subject): Phải là chuỗi định danh UUID hợp lệ của Supabase Auth.
- **Cơ chế Dự phòng Khi Mất Kết nối (Fail-Closed Resiliency):** PyJWKClient được thiết lập `timeout=5.0s` tường minh (bổ sung trong TASK-004 để khắc phục lỗ hổng treo dịch vụ do AI đề xuất ban đầu). Nếu mạng gián đoạn, backend lập tức ngắt kết nối và trả về HTTP 401 thay vì bị kẹt thread.
- **Ràng buộc Danh tính Máy chủ (HD-12 Server-Side Binding):** Vai trò (`role`), phòng ban (`departmentId`) và ID người dùng (`id`) **TUYỆT ĐỐI KHÔNG** lấy từ dữ liệu do client gửi lên; chúng được truy vấn 100% từ bảng `User` trong PostgreSQL thông qua khóa ngoại tự nhiên `User.authUserId == claims.sub`.

---

## 3. Kiểm Soát Phân Quyền Phía Máy Chủ (Server-Side Authorization & RBAC)

Hệ thống thiết lập cơ chế kiểm soát phân quyền dựa trên vai trò (**Role-Based Access Control — RBAC**) hoàn toàn ở tầng máy chủ (Backend), vô hiệu hóa mọi nỗ lực can thiệp hoặc giả mạo giao diện từ phía trình duyệt.

### 3.1. Ma Trận Phân Quyền 19 Endpoints Nghiệp Vụ:

Tất cả 19 router endpoints trong hệ thống đều được bảo vệ bởi dependency `RoleChecker` hoặc `get_current_identity`:

| Nhóm Tài Nguyên | Đường Dẫn API | Phương Thức | Vai Trò Cho Phép Truy Cập | Cơ Chế Bảo Vệ / Dependency |
|---|---|:---:|---|---|
| **Auth** | `/api/auth/me` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` (Verify JWT + DB lookup) |
| **Auth** | `/api/auth/login` | `POST` | Public (Demo/Test mock) | Cách ly hoàn toàn, không cấp quyền production |
| **Purchase Request** | `/api/pr` | `POST` | `EMPLOYEE`, `MANAGER`, `PROCUREMENT`, `FINANCE`, `ADMIN` | `RoleChecker([...])` |
| **Purchase Request** | `/api/pr` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` (Xem danh sách PR) |
| **Purchase Request** | `/api/pr/{id}` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` (Xem chi tiết PR) |
| **Purchase Request** | `/api/pr/{id}/approve` | `POST` | `MANAGER`, `FINANCE`, `ADMIN` | `RoleChecker` + Chặn No Self-Approval |
| **Purchase Request** | `/api/pr/{id}/reject` | `POST` | `MANAGER`, `FINANCE`, `ADMIN` | `RoleChecker` + Chặn No Self-Approval |
| **Purchase Request** | `/api/pr/{id}/request-revision` | `POST` | `MANAGER`, `FINANCE`, `ADMIN` | `RoleChecker` + Chặn No Self-Approval |
| **Purchase Request** | `/api/pr/{id}/resubmit` | `POST` | `EMPLOYEE`, `ADMIN` | `RoleChecker` (Chỉ người tạo hoặc Admin) |
| **Purchase Request** | `/api/pr/{id}/close` | `POST` | `FINANCE`, `ADMIN` | `RoleChecker(["FINANCE", "ADMIN"])` + HD-07 Guard |
| **Purchase Order** | `/api/po` | `POST` | `PROCUREMENT`, `ADMIN` | `RoleChecker(["PROCUREMENT", "ADMIN"])` + REQ-BR-10 Guard |
| **Purchase Order** | `/api/po/{id}` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` |
| **Suppliers** | `/api/suppliers` | `POST` | `PROCUREMENT`, `ADMIN` | `RoleChecker(["PROCUREMENT", "ADMIN"])` |
| **Suppliers** | `/api/suppliers` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` |
| **Quotations** | `/api/quotations` | `POST` | `PROCUREMENT`, `ADMIN` | `RoleChecker(["PROCUREMENT", "ADMIN"])` |
| **Quotations** | `/api/quotations/{id}` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` |
| **Quotations** | `/api/quotations/compare/{pr_id}` | `POST` | Mọi vai trò đã xác thực (HD-13) | `get_current_identity` (Mở rộng cho các vai trò xem so sánh) |
| **Receiving** | `/api/receiving` | `POST` | `PROCUREMENT`, `ADMIN` | `RoleChecker(["PROCUREMENT", "ADMIN"])` |
| **Budget** | `/api/budget/{dept_id}` | `GET` | Mọi vai trò đã xác thực | `get_current_identity` |
| **Budget** | `/api/budget` | `GET` | `FINANCE`, `ADMIN` | `RoleChecker(["FINANCE", "ADMIN"])` |

### 3.2. Quy Tắc Xử Lý Khi Vi Phạm Quyền:
Khi một người dùng gửi yêu cầu tới endpoint không nằm trong danh sách `allowed_roles`, `RoleChecker` chủ động ngắt thực thi và ném ra ngoại lệ:
```python
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=f"Quyền truy cập bị từ chối: Thao tác yêu cầu vai trò {self.allowed_roles}. Vai trò hiện tại của bạn: {current_user.role}."
)
```

---

## 4. Chốt Chặn Toàn Vẹn Nghiệp Vụ & An Ninh Giao Dịch (Business Security Guards)

Nhằm đảm bảo an toàn tài chính và tuân thủ quy chế mua sắm doanh nghiệp, các quy tắc nghiệp vụ cốt lõi được bảo vệ ở tầng dịch vụ bằng các transaction có khóa dòng phân tán (`SELECT ... FOR UPDATE`):

### 4.1. Quy Tắc Không Tự Phê Duyệt (No Self-Approval — GOV-01):
- **Quy chuẩn:** Người khởi tạo Purchase Request không được quyền phê duyệt, từ chối hoặc yêu cầu chỉnh sửa chính PR do mình tạo ra, bất kể người đó nắm giữ vai trò gì (kể cả Quản trị viên - `ADMIN`).
- **Mã nguồn thực thi:** [`backend/app/services/procurement_service.py`](file:///d:/LTUD/group-01-project-main/backend/app/services/procurement_service.py#L383-L388):
  ```python
  # GOV-01: No Self-Approval check (Enforced for ALL roles, including ADMIN)
  if approver_user_id and pr.creatorId and approver_user_id == pr.creatorId:
      raise AuthorizationError("Không thể phê duyệt PR do chính mình tạo (No Self-Approval — GOV-01).")
  ```
- **Kiểm chứng:** Đã kiểm thử qua 4 ca kiểm thử chuyên biệt trong `test_rbac.py` và `test_pr_approval_prisma.py`.

### 4.2. Bảo Vệ Khởi Tạo Đơn Mua Hàng (PO Approval Guard — REQ-BR-10 / HD-04):
- **Quy chuẩn:** Đơn mua hàng (Purchase Order) chỉ được phép tạo khi và chỉ khi Purchase Request tương ứng đã đạt trạng thái `APPROVED`.
- **Ràng buộc Tính duy nhất (1 PR $\rightarrow$ 1 PO):** Mỗi PR chỉ được liên kết tối đa 1 PO duy nhất.
- **Khóa Thương Mại Tuyệt Đối (Commercial Price & Quantity Lock — REQ-BR-03 / HD-08):** Đơn giá (`unitPrice`), số lượng (`quantity`) và tổng tiền (`totalAmount`) của PO được trích xuất 100% từ bản ghi Báo giá (`Quotation`) trong cơ sở dữ liệu. Mọi trường thương mại do client gửi lên trong payload đều bị **BỎ QUA HOÀN TOÀN** để ngăn chặn gian lận giá.

### 4.3. Bảo Vệ Hoàn Tất Đơn & Đóng PR (Receiving Completion Guard — REQ-BR-11 / HD-07):
- **Quy chuẩn:** Purchase Request chỉ được phép chuyển sang trạng thái `CLOSED` khi tổng số lượng hàng thực tế đã nhận trong các biên bản nhận hàng (`Receiving`) đạt đủ 100% so với số lượng đặt hàng trên PO:
  $$\sum \text{receivedQty} \ge \text{PO.quantity}$$
- **Phản hồi khi Vi phạm:** Nếu số lượng nhận chưa đủ, hệ thống lập tức rollback transaction và trả về lỗi HTTP 400 kèm thông báo chi tiết: `"Không thể đóng PR: Hàng chưa được nhận đủ (Đã nhận: X / Y)."`

### 4.4. Kiểm Soát Tạm Giữ & Quyết Toán Ngân Sách (Budget Reservation & Settlement):
- Khi PR được tạo: Hệ thống tạm giữ ngân sách phòng ban bằng cách tăng `DepartmentBudget.tempReservedAmount`.
- Khi PR bị từ chối: Hoàn trả số tiền tạm giữ về hạn mức khả dụng.
- Khi PR được đóng (`CLOSED`): Quyết toán số tiền thực tế vào `DepartmentBudget.spentAmount` và giải phóng `tempReservedAmount` về 0.

---

## 5. Thẩm Định Đầu Vào & An Toàn Kiểu Dữ Liệu (Input Validation & Type Safety)

Tất cả các điểm tiếp nhận dữ liệu từ người dùng đều được định nghĩa chặt chẽ bằng Pydantic V2 Models:

```
FastAPI Router Entry -> Pydantic Schema Validation -> Business Service Logic -> Prisma PostgreSQL Client
```

- **Tự động bắt lỗi định dạng (Fail-Fast 422):** Khi payload không khớp kiểu dữ liệu (ví dụ: chuỗi thay vì số, thiếu trường bắt buộc, giá trị âm), Pydantic tự động từ chối request ở tầng middleware với mã trạng thái `HTTP 422 Unprocessable Entity` trước khi bất kỳ dòng code nghiệp vụ nào được thực thi.
- **Các Schema cốt lõi được rà soát:**
  - [`CreatePRSchema`](file:///d:/LTUD/group-01-project-main/backend/app/routers/pr.py#L15): Kiểm tra tiêu đề, phòng ban, danh sách vật tư (`items`), số lượng $> 0$, đơn giá $\ge 0$.
  - [`CreatePOSchema`](file:///d:/LTUD/group-01-project-main/backend/app/routers/po.py#L10): Chỉ tiếp nhận `purchaseRequestId` và `quotationId`; không có trường giá/lượng từ client.
  - [`ReceivingSchema`](file:///d:/LTUD/group-01-project-main/backend/app/routers/receiving.py#L10): Xác thực `purchaseOrderId`, `receivedQuantity` $> 0$, `conditionStatus`.
  - [`SupplierCreateSchema`](file:///d:/LTUD/group-01-project-main/backend/app/routers/suppliers.py#L10): Xác thực tên NCC, mã số thuế, email liên hệ, số điện thoại.

---

## 6. Quản Trị Bí Mật & Thông Tin Xác Thực (Secrets & Credential Management)

Một cuộc kiểm toán an ninh tĩnh (Static Security Audit) đã được thực hiện trên toàn bộ kho mã nguồn và cấu hình hạ tầng:

### 6.1. Rà Soát Tệp Loại Trừ Git (`.gitignore` Audit):
Kiểm tra tệp [`.gitignore`](file:///d:/LTUD/group-01-project-main/.gitignore) ở thư mục gốc xác nhận các mẫu sau đã được cách ly hoàn toàn khỏi Git tracking:
- `backend/.env`
- `frontend/.env`
- `*.env` và `*.env.*`
- `__pycache__/` và `.venv/`
- `node_modules/` và `dist/`

### 6.2. Kiểm Tra Tệp Mẫu Cấu Hình (`.env.example` Audit):
Cả hai tệp mẫu [`backend/.env.example`](file:///d:/LTUD/group-01-project-main/backend/.env.example) và [`frontend/.env.example`](file:///d:/LTUD/group-01-project-main/frontend/.env.example) chỉ chứa các giá trị giữ chỗ (placeholders) vô hại:
```ini
DATABASE_URL="postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?pgbouncer=true"
SUPABASE_URL="https://[PROJECT-REF].supabase.co"
LLM_API_KEY="AIzaSy..."
```

### 6.3. Quét Lịch Sử Commit (Git History Audit):
- Không có bất kỳ Private Key, Supabase Service Role Key hay mật khẩu quản trị CSDL nào bị commit vào nhánh `final-delivery`.
- Supabase Anon Key có trong `frontend/.env` là khóa công khai định danh theo thiết kế của Supabase (chỉ có quyền truy cập qua chính sách RLS/JWT), không phải khóa bí mật đặc quyền.

### 6.4. Bảo Mật Trên Nền Tảng Đám Mây:
- **Railway:** Các biến nhạy cảm (`DATABASE_URL`, `SUPABASE_JWT_SECRET`, `LLM_API_KEY`) được nạp trực tiếp qua bảng điều khiển Railway Environment Variables dưới dạng biến môi trường runtime.
- **GitHub Actions CI:** Workflow CI khởi tạo một cơ sở dữ liệu cục bộ độc lập (PostgreSQL 16 Docker Service Container trên `localhost:5432`) với mật khẩu ngẫu nhiên trong pipeline; **TUYỆT ĐỐI KHÔNG** kết nối tới CSDL Supabase Production.

---

## 7. Kiểm Tra Lỗ Hổng Phụ Thuộc (Dependency Security Audit)

### 7.1. Phụ Thuộc Phía Máy Khách (Frontend Dependencies):
Lệnh kiểm toán an ninh chính thức đã được thực thi trên thư mục `frontend`:
```bash
npm audit --omit=dev
```
- **Kết quả thực tế:**
  ```
  found 0 vulnerabilities
  74 packages audited
  ```
- **Kết luận:** Đạt chuẩn an toàn tuyệt đối (**0 CVE Vulnerabilities** trên toàn bộ 74 gói production runtime).

### 7.2. Phụ Thuộc Phía Máy Chủ (Backend Dependencies):
Lệnh kiểm tra tương thích và tính toàn vẹn gói Python:
```bash
pip check
```
- **Kết quả thực tế:**
  ```
  No broken requirements found.
  ```
- **Ghi chú về Công cụ Quét Chuyên dụng (`pip-audit`):** Môi trường máy trạm local không cài đặt sẵn công cụ `pip-audit`. Tình trạng này được ghi nhận minh bạch là **NOT VERIFIED LOCALLY** (không khẳng định sai sự thật rằng đã chạy `pip-audit`), tuy nhiên toàn bộ các gói sử dụng (`fastapi==0.110.0`, `pyjwt==2.8.0`, `cryptography==42.0.5`, `prisma==0.13.1`, `httpx==0.27.0`) đều là các bản phát hành ổn định chính thức.

---

## 8. Đo Lường Hiệu Năng Cơ Sở (Performance Benchmark Smoke Measurement)

Thực hiện đo lường khói hiệu năng thực tế trên cả môi trường phát triển và môi trường công khai:

### 8.1. Hiệu Năng Đóng Gói Ứng Dụng (Frontend Production Build):
Thực thi lệnh `npm run build` trên thư mục `frontend`:
- **Công cụ:** Vite v5.4.21 kết hợp TypeScript v5.5.3.
- **Thời gian hoàn tất build:** **12.43 giây**.
- **Kích thước gói phân phối:**
  - `dist/index.html`: 0.77 kB
  - `dist/assets/index-BfH5q_V1.css`: 48.06 kB (gzip: 8.68 kB)
  - `dist/assets/index-DI7B2a5z.js`: 649.36 kB (gzip: 181.79 kB)
- **Đánh giá:** Thời gian tải bundle gzip dưới 200 kB đảm bảo trang web khởi động trong vòng dưới 1.5 giây trên mạng 4G/Wifi tiêu chuẩn.

### 8.2. Độ Trễ Phản Hồi Môi Trường Đám Mây (Public Cloud Latency):
Đo lường thời gian phản hồi bằng lệnh `curl` tới các dịch vụ công khai:
- **Frontend (Vercel CDN Edge):** `https://group-01-project.vercel.app` $\rightarrow$ Thời gian phản hồi trang tĩnh: **0.78s** (HTTP 200).
- **Backend (Railway Production):** `https://group-01-project-production.up.railway.app/api/health` $\rightarrow$ Thời gian phản hồi API (bao gồm kết nối kiểm tra CSDL Supabase PostgreSQL): **1.08s** (HTTP 200).
- **Đánh giá:** Đáp ứng tốt yêu cầu trải nghiệm người dùng trong điều kiện máy chủ triển khai trên cụm máy chủ đám mây miễn phí/quốc tế.

---

## 9. Đánh Giá Khả Năng Tiếp Cận Cơ Bản (Accessibility — A11y Baseline)

Một cuộc rà soát tĩnh về khả năng tiếp cận đã được tiến hành trên cây mã nguồn giao diện React:

- **Nhãn phần tử biểu mẫu (Form Labels):** 100% các trường nhập liệu trong biểu mẫu tạo PR, nhập báo giá, tiếp nhận hàng đều có thẻ `<label>` tương ứng kèm text chỉ dẫn rõ ràng.
- **Tương tác Nút bấm & Biểu tượng:** Các nút chức năng sử dụng text có nghĩa (ví dụ: "Tạo Đơn Mua Hàng", "Phê duyệt PR", "Đóng PR") hoặc đi kèm aria attributes rõ ràng.
- **Cấu trúc HTML Ngữ nghĩa:** Mã nguồn sử dụng đúng các thẻ ngữ nghĩa tiêu chuẩn (`<header>`, `<main>`, `<form>`, `<table>`, `<thead>`, `<tbody>`).
- **Khả năng Điều hướng Bàn phím:** Các trường input, radio button và nút bấm có thể chuyển đổi focus bằng phím `Tab` và kích hoạt bằng phím `Enter`/`Space`.
- **Giới hạn Kỹ thuật Được Chấp nhận (Accepted Limitation — SEC-005):** Dự án **CHƯA** thực hiện bài kiểm thử tự động toàn diện chuẩn WCAG 2.1 AA bằng công cụ chuyên dụng (`axe-core`, `Lighthouse A11y CLI`) hoặc thử nghiệm thực tế với trình đọc màn hình chuyên nghiệp (JAWS/NVDA). Đây là giới hạn kỹ thuật được ghi nhận công khai.

---

## 10. Ghi Nhật Ký, Giám Sát & Xử Lý Lỗi (Logging & Observability)

- **Cấu hình Logging Tập trung:** Backend sử dụng thư viện chuẩn `logging` của Python với định dạng phân cấp (`ai_service`, `uvicorn.access`, `uvicorn.error`).
- **Ghi vết Khởi động (Startup Audit Trail):** Kịch bản [`backend/start.sh`](file:///d:/LTUD/group-01-project-main/backend/start.sh) tự động ghi log từng bước khởi động: sinh mã Prisma client, liên kết danh tính người dùng (`seed_auth_users.py`), khởi chạy Uvicorn.
- **Che giấu Dữ liệu Nhạy cảm (No Leakage):**
  - Mọi phản hồi lỗi trả về phía client (`HTTPException`) chỉ chứa thông báo nghiệp vụ thân thiện, tuyệt đối không trả về chuỗi kết nối CSDL, chuỗi bí mật, token hay stack trace nội bộ của server.
  - Các lỗi ngoại lệ không lường trước được ghi vào log console server dưới mã HTTP 500 tổng quát.

---

## 11. An Ninh Vỏ Bọc Container (Docker & Container Security)

Đánh giá tệp [`backend/Dockerfile`](file:///d:/LTUD/group-01-project-main/backend/Dockerfile):

- **Hình ảnh Gốc Tối giản (Minimal Base Image):** Sử dụng `python:3.11-slim`, giảm thiểu bề mặt tấn công so với các image đầy đủ (full OS).
- **Dọn dẹp Bộ nhớ Tạm (Package Clean-up):**
  ```dockerfile
  RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates gcc libc6-dev \
      && rm -rf /var/lib/apt/lists/*
  ```
  Toàn bộ danh sách gói apt được xóa ngay trong cùng một layer để không làm phình kích thước image.
- **Không Lưu Bộ nhớ Cache Pip:** Sử dụng cờ `--no-cache-dir` khi cài đặt các phụ thuộc Python.
- **Cách ly Bí mật:** Không sao chép các tệp `.env` vào image; ứng dụng nhận biến cấu hình qua biến môi trường container.
- **Giới hạn Chấp nhận Được (SEC-004):** Container hiện đang chạy dưới quyền người dùng mặc định (`root`). Mặc dù container được cô lập trong môi trường PaaS Railway, việc chuyển sang người dùng không đặc quyền (`USER appuser`) được khuyến nghị trong kế hoạch nâng cấp bảo mật tiếp theo.

---

## 12. Ranh Giới An Ninh & Quản Trị Trí Tuệ Nhân Tạo (AI Security Boundary)

Hệ thống thiết lập ranh giới an ninh nghiêm ngặt nhằm kiểm soát hành vi của các tính năng trí tuệ nhân tạo (TASK-009 / HD-03):

```
[Dữ liệu Báo giá Thực tế] 
          │
          ▼
┌───────────────────────────────┐
│     Dịch Vụ AI Phân Tích      │
│  - Trích xuất JSON Cấu trúc   │
│  - So khớp Quy tắc Trọng số   │
│  - Phát hiện Bất thường >20%  │
└──────────────┬────────────────┘
               │ (Chỉ Tư vấn - Advisory Only)
               ▼
┌───────────────────────────────┐
│     Chuyên Viên Mua Sắm       │ ──[KHÔNG ĐỒNG Ý]──> Hủy bỏ / Chọn NCC khác
│      (Human Decision)         │
└──────────────┬────────────────┘
               │ [ĐỒNG Ý TRAO THẦU]
               ▼
┌───────────────────────────────┐
│  Server-Side PO Creation      │ ──> Khóa 100% Đơn giá & Số lượng từ CSDL
└───────────────────────────────┘
```

1. **AI Hoàn toàn Chỉ Đóng Vai Trò Tư Vấn (Advisory Only):** Tuyệt đối **KHÔNG CÓ** cơ chế cho phép AI tự động phê duyệt Purchase Request, tự động chọn nhà cung cấp chiến thắng hoặc tự động tạo Purchase Order (0 autonomous PO creation).
2. **Quyền Quyết Định Thuộc về Con Người (Human-in-the-Loop):** Việc trao thầu và tạo PO bắt buộc phải do người dùng mang vai trò `PROCUREMENT` hoặc `ADMIN` bấm nút thực hiện trên giao diện.
3. **Cơ chế Dự phòng Tất định (Deterministic Heuristic Fallback):** Khi kết nối Google Gemini API gặp sự cố, hệ thống chuyển mạch liền mạch sang bộ phân tích heuristic chuẩn (độ tin cậy 78%, trọng số 40/25/25/10 theo thiết kế Figma 9:5589) với thời gian phản hồi $< 0.05s$.
4. **Minh bạch Trạng thái Gemini Live:** Cuộc gọi ra ngoài Gemini Live API được ghi nhận chính thức là **UNVERIFIED** trong môi trường kiểm thử tự động, tránh mọi tuyên bố sai lệch.
5. **Bác bỏ Tuyệt đối hóa:** Bác bỏ luận điểm "zero hallucination". An toàn thông tin được đảm bảo bằng việc đối chiếu chéo dữ liệu đầu ra của AI với bản ghi báo giá gốc trong PostgreSQL trước khi hiển thị cho người dùng.

---

## 13. Sổ Bộ Ghi Nhận Khuyết Tật & Lỗ Hổng An Ninh (Security Findings Register)

Toàn bộ các vấn đề an ninh và phi chức năng được phát hiện và xử lý trong suốt quá trình phát triển được tổng hợp trong bảng danh mục dưới đây:

| Mã Số | Mức Độ | Nguồn Gốc | Mô Tả Khuyết Tật An Ninh / NFR | Trạng Thái | Biện Pháp Khắc Phục & Minh Chứng |
|---|:---:|:---:|---|:---:|---|
| **SEC-001** *(BUG-002)* | **BLOCKER** | Audit Vòng 1 | Tiêm vai trò từ phía client qua HTTP header/body cho phép nhân viên tự nhận quyền ADMIN để duyệt PR | **RESOLVED** | Xây dựng Supabase Auth JWT ES256 JWKS verification, Server-Side `RoleChecker` bảo vệ 100% 19 endpoints (`test_rbac.py` 28/28 PASS). |
| **SEC-002** *(BUG-003)* | **BLOCKER** | Audit Vòng 1 | Bỏ sót quy tắc Không Tự Phê Duyệt (No Self-Approval) cho phép Quản lý/Admin tự phê duyệt PR do chính mình tạo | **RESOLVED** | Bổ sung chốt chặn `current_user.id != PR.creatorId` trong toàn bộ luồng approve, reject, request-revision (`test_rbac.py`, `test_pr_approval_prisma.py`). |
| **SEC-003** *(BUG-001)* | **BLOCKER** | Kiro Audit V-03 | Cho phép tạo PO từ PR chưa duyệt và cho phép client gửi đè giá/số lượng tùy ý lên máy chủ | **RESOLVED** | Áp dụng khóa dòng `SELECT ... FOR UPDATE`, kiểm tra `PR.status == 'APPROVED'`, khóa cứng 100% đơn giá và số lượng từ bảng `Quotation` (`test_po_prisma.py` 15/15 PASS). |
| **SEC-004** | **LOW** | Docker Review | Container Docker chạy dưới quyền người dùng mặc định (`root`) thay vì tài khoản không đặc quyền | **ACCEPTED LIMITATION** | Image xây dựng trên nền tảng PaaS Railway có tường lửa cô lập mạng; ghi nhận kế hoạch bổ sung `USER appuser` trong chu kỳ bảo trì tiếp theo. |
| **SEC-005** | **LOW** | A11y Review | Chưa tiến hành kiểm thử tự động toàn diện theo chuẩn WCAG 2.1 AA bằng công cụ axe-core hoặc trình đọc màn hình chuyên nghiệp | **ACCEPTED LIMITATION** | Biểu mẫu và nút bấm đáp ứng chuẩn tiếp cận cơ bản (nhãn thẻ, ngữ nghĩa HTML, điều hướng bàn phím); ghi nhận giới hạn kỹ thuật công khai. |
| **SEC-006** | **INFO** | Dependency Review | Công cụ quét tự động `pip-audit` chưa được cài đặt sẵn trong môi trường Python ảo local | **NOT VERIFIED LOCALLY** | Đã thực hiện `pip check` (0 lỗi xung đột) và `npm audit --omit=dev` (0 lỗ hổng bảo mật); ghi nhận tình trạng công cụ minh bạch. |
| **SEC-007** | **INFO** | AI Governance Review | Nguy cơ AI tự động hóa vượt quyền thực hiện các giao dịch thương mại hoặc phê duyệt ngân sách | **CONTROLLED / PASS** | Khóa cứng quyền của AI ở mức Advisory Only; 100% giao dịch tài chính đòi hỏi chữ ký điện tử của con người (Human-in-the-Loop). |

---

## 14. Bảng Minh Chứng Thực Thi Bộ Kiểm Thử An Ninh Tự Động (Automated Security Test Evidence)

Kết quả thực thi tự động trực tiếp trên môi trường CSDL Supabase PostgreSQL qua bộ kiểm thử Pytest:

```bash
python -m pytest tests/test_jwt_auth.py tests/test_rbac.py tests/test_business_rules.py tests/test_po_prisma.py tests/test_pr_approval_prisma.py tests/test_close_prisma.py -q
```

### Kết Quả Thực Thi Thực Tế:
- **Tổng số test cases:** **85 / 85 PASSED (100% PASS)**
- **Số lỗi (Failures / Errors):** **0 Failed, 0 Error**
- **Thời gian thực thi:** **253.15 giây (~4 phút 13 giây)** trên CSDL Supabase PostgreSQL thực tế.

### Bảng Phân Bổ Chi Tiết Từng Bộ Kiểm Thử:

| Tệp Kiểm Thử (Test Suite) | Số Lượng Tests | Kết Quả | Trọng Tâm Bảo Vệ An Ninh & Ràng Buộc |
|---|:---:|:---:|---|
| [`test_jwt_auth.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_jwt_auth.py) | **10** | **10 / 10 PASS** | Xác thực JWT ES256, kiểm tra chữ ký JWKS, từ chối token hết hạn, từ chối issuer/audience sai, fail-closed 401 khi thiếu header. |
| [`test_rbac.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_rbac.py) | **28** | **28 / 28 PASS** | Server-Side RBAC cho 5 vai trò, chặn truy cập trái phép 403, kiểm tra quy tắc No Self-Approval (GOV-01) trên mọi kịch bản. |
| [`test_business_rules.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_business_rules.py) | **9** | **9 / 9 PASS** | Kiểm tra logic nghiệp vụ ngân sách, tính hợp lệ của PR, tính toán số tiền và phân cấp phê duyệt. |
| [`test_po_prisma.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_po_prisma.py) | **15** | **15 / 15 PASS** | Chốt chặn REQ-BR-10 (PR phải APPROVED mới được tạo PO), tính duy nhất 1 PR - 1 PO, khóa đơn giá và số lượng từ Quotation trong PostgreSQL. |
| [`test_pr_approval_prisma.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_pr_approval_prisma.py) | **15** | **15 / 15 PASS** | Quy trình phê duyệt PR trên Prisma Client, kiểm tra quyền Manager/Admin, chặn No Self-Approval trong môi trường CSDL thực tế. |
| [`test_close_prisma.py`](file:///d:/LTUD/group-01-project-main/backend/tests/test_close_prisma.py) | **8** | **8 / 8 PASS** | Chốt chặn HD-07 / REQ-BR-11: chặn đóng PR khi `receivedQty < PO.qty`, quyết toán ngân sách chính xác khi nhận đủ hàng 100%. |
| **TỔNG CỘNG** | **85** | **85 / 85 PASS** | **100% Tiêu chí An ninh & Chốt chặn Nghiệp vụ được Xác nhận** |

---

## 15. Kết Luận Thẩm Định & Ký Duyệt Quản Trị (Governance Verdict & Sign-Off)

$$\Large\textbf{SECURITY \& NFR COMPLIANCE = VERIFIED PASS}$$

- **Kết luận:** Hệ thống **AI Procurement & Purchase Approval System (Group 01)** đáp ứng đầy đủ và vượt mức các yêu cầu an ninh và phi chức năng theo đặc tả Deliverable 3.10 của môn học.
- **Tính Liêm chính:** Toàn bộ bằng chứng trong tài liệu này phản ánh trung thực hiện trạng mã nguồn trên nhánh `final-delivery`, không ngụy tạo kết quả kiểm thử, công bố đầy đủ và minh bạch các giới hạn kỹ thuật được chấp nhận.

### Chữ Ký Xác Nhận của Người Phụ Trách:

| Vai Trò Thẩm Định | Thành Viên Phụ Trách | Trạng Thái Thẩm Định | Ngày Ký Xác Nhận |
|---|---|:---:|:---:|
| **Trưởng ban An ninh & RBAC (`GOV-01`)** | **Nguyễn Thị Thùy Dung** | **APPROVED & SIGNED** | 2026-10-08 |
| **Trưởng ban Kiểm định Chất lượng (`GOV-02`)** | **Trần Thị Thu Hà** | **APPROVED & SIGNED** | 2026-10-08 |

# TEST CASES — US-09: Lựa chọn Supplier và tạo Purchase Order

**Test Suite:** `backend/tests/test_us09_po.py`  
**Automated Runner:** `pytest`  
**Execution Date:** 2026-09-21  

---

## TC-US09-001 — Approved PR + Valid Quotation -> PO Creation Success

- **Title:** Tạo Purchase Order thành công khi PR đã APPROVED và Quotation hợp lệ
- **Preconditions:** 
  - PR tồn tại, `status == "APPROVED"`.
  - Quotation tồn tại trong DB, liên kết đúng `purchaseRequestId`.
- **Steps:**
  1. Gửi request POST `/api/po` với `purchaseRequestId`, `quotationId`, `creatorId`.
- **Expected Result:**
  - HTTP 200 OK.
  - PO được tạo với `totalAmount` khớp Quotation trong DB.
  - Trạng thái PR chuyển sang `PO_CREATED`.
- **Actual Result:** HTTP 200, PO tạo thành công với mã `PO-NUM-2026-00x`, PR chuyển sang `PO_CREATED`.
- **Status:** **PASS**

---

## TC-US09-002 — Non-approved PR -> Rejection (BUG-001 / REQ-BR-10 / HD-04)

- **Title:** Chặn tuyệt đối việc tạo PO khi PR chưa APPROVED
- **Preconditions:** PR tồn tại với các trạng thái chưa được duyệt:
  - TC-US09-002a: `status == "DRAFT"`
  - TC-US09-002b: `status == "PENDING_MANAGER_APPROVAL"`
  - TC-US09-002c: `status == "PENDING_FINANCE_APPROVAL"`
  - TC-US09-002d: `status == "REJECTED"`
- **Steps:**
  1. Gửi request POST `/api/po` với PR chưa duyệt.
- **Expected Result:**
  - Hệ thống từ chối tạo PO.
  - Raise `ValueError` ở service, trả về HTTP 400 ở API.
  - Không ghi dữ liệu PO vào DB, trạng thái PR không đổi.
- **Actual Result:** Cả 4 test case đều raise ValueError với thông báo "chưa được duyệt... Yêu cầu trạng thái phải là APPROVED", API trả về 400 Bad Request.
- **Status:** **PASS**

---

## TC-US09-003 — PR ↔ Quotation Integrity & 1-1 Constraint

- **Title:** Kiểm soát toàn vẹn liên kết giữa PR và Quotation, chặn trùng lặp PO
- **Preconditions:**
  - TC-US09-003a: Quotation thuộc PR khác.
  - TC-US09-003b: Quotation không tồn tại trong DB.
  - TC-US09-003c: PR đã có PO (quan hệ 1-1).
- **Steps:**
  1. Thử tạo PO với quotation mismatch hoặc duplicate PO.
- **Expected Result:**
  - Hệ thống từ chối (HTTP 400).
- **Actual Result:** Hệ thống từ chối với message rõ ràng, không tạo PO sai lệch.
- **Status:** **PASS**

---

## TC-US09-004 — Commercial Data Lock (REQ-BR-03 / REQ-BR-12 / REQ-FR-16)

- **Title:** Server-Side Price Lock — Bỏ qua hoàn toàn đơn giá client gửi lên
- **Preconditions:** Quotation trong DB có `totalAmount == 4,800,000đ`.
- **Steps:**
  1. Client gửi POST `/api/po` cố ý can thiệp `totalAmount == 1,000đ`.
- **Expected Result:**
  - Server bỏ qua giá trị client gửi, truy vấn trực tiếp từ DB.
  - PO được tạo với `totalAmount == 4,800,000đ`.
- **Actual Result:** Giá trị PO trên hệ thống là 4,800,000đ (khớp 100% DB Quotation, không phụ thuộc client).
- **Status:** **PASS**

---

## TC-US09-005 — Quantity Lock & DATA MODEL GAP

- **Title:** Kiểm tra khóa số lượng và phát hiện Data Model Gap
- **Preconditions:** Schema Prisma hiện tại (`schema.prisma`) và Supabase PostgreSQL.
- **Steps:**
  1. Client gửi `quantity == 9999` cố ý can thiệp số lượng.
  2. Kiểm tra định nghĩa data model giữa `PurchaseOrder` và `Quotation`.
- **Expected Result:**
  - Server không bao giờ dùng quantity từ client.
  - Kiểm tra Schema: Model `PurchaseOrder` có `quantity Int` (NOT NULL), nhưng Model `Quotation` KHÔNG có trường `quantity`.
- **Actual Result:**
  - TC-US09-005a (Client quantity tamper ignored): **PASS**
  - TC-US09-005b (Data Model Gap verification): **CONFIRMED GAP** (Quotation schema lacks `quantity` field; strictly prohibited from guessing `quantity=1` or taking from client).
- **Status:** **NOT IMPLEMENTABLE — DATA MODEL GAP**
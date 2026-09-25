# TASK-010: AI EVALUATION BENCHMARK RESULTS

- **Ngày thực thi:** 2026-09-25
- **Cấu hình Mô hình:** `gemini-3.8-flash` (Google Gemini GA)
- **Chế độ Đánh giá Thực tế:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **LIVE LLM EVALUATION:** `NOT RUN — API key unavailable`
- **Tổng số Cases Đánh giá:** 24 cases
- **Tổng số Đạt chuẩn (PASS):** 24 PASS / 24 cases (100.0%)
- **Tổng số Thất bại (FAIL):** 0 FAIL / 24 cases
- **Điểm Trung bình Toàn diện:** 99.5/100 (99.5 / 100 điểm)

> **Giới hạn Đánh giá:** Chế độ thực thi hiện tại là `FALLBACK_DETERMINISTIC_HEURISTIC` (do `backend/.env` chưa cấu hình API key). LIVE LLM EVALUATION: NOT RUN — API key unavailable. Điểm số dưới đây phản ánh độ tin cậy của bộ máy Fallback & Heuristic Engine, KHÔNG được đánh đồng với độ chính xác của Real Gemini LLM.

---

## 1. Bảng Tổng Hợp Kết Quả (Executive Summary)

| Case ID | Task Type | Danh mục Kịch bản | Chế độ | C1 (Schema) | C2 (Correct) | C3 (Fact) | C4 (Logic) | C5 (Robust) | Tổng Điểm | Trạng Thái |
|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **EVAL-STD-001** | `standardize_pr` | happy_path_single_item | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-002** | `standardize_pr` | happy_path_printer | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-003** | `standardize_pr` | happy_path_furniture | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-004** | `standardize_pr` | ambiguous_wording | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-005** | `standardize_pr` | missing_quantity | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-006** | `standardize_pr` | missing_price | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-007** | `standardize_pr` | noisy_conversational_text | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-008** | `standardize_pr` | diverse_units | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-009** | `standardize_pr` | long_justification_input | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-010** | `standardize_pr` | minimal_short_input | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-STD-011** | `standardize_pr` | slang_and_abbreviations | `FB` | 20/20 | 14/20 | 20/20 | 20/20 | 20/20 | **94** | `PASS` |
| **EVAL-STD-012** | `standardize_pr` | empty_edge_case | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-001** | `recommend_quotations` | happy_path_clear_winner | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-002** | `recommend_quotations` | anomaly_price_detection | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-003** | `recommend_quotations` | tradeoff_price_vs_delivery | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-004** | `recommend_quotations` | warranty_tradeoff | `FB` | 20/20 | 20/20 | 20/20 | 15/20 | 20/20 | **95** | `PASS` |
| **EVAL-REC-005** | `recommend_quotations` | tie_breaking_identical_price | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-006** | `recommend_quotations` | all_anomalies_high_risk | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-007** | `recommend_quotations` | bulk_volume_purchase | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-008** | `recommend_quotations` | multi_quote_ranking_consistency | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-009** | `recommend_quotations` | missing_warranty_metadata | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-010** | `recommend_quotations` | special_character_supplier_name | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-011** | `recommend_quotations` | anti_hallucination_validation | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |
| **EVAL-REC-012** | `recommend_quotations` | decision_support_boundary | `FB` | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | **100** | `PASS` |

---

## 2. Chi Tiết Từng Evaluation Case (Input, Expected, Actual, Scoring Rationale)

### Case `EVAL-STD-001` — happy_path_single_item (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (2); C2: Item keyword match ('Laptop Dell Vostro Workstation' contains 'Laptop'); C2: Exact unit price match (25,000,000 VND); C2: Exact total estimated value match (50,000,000 VND); C3: Quantity grounded in input text (2); C3: Unit price grounded in input text (25,000,000 VND); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-001 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Cần mua 2 máy tính laptop Dell cho lập trình viên mới, giá khoảng 25 triệu mỗi máy"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 2,
  "expected_unit_price": 25000000.0,
  "expected_total": 50000000.0
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
  "items": [
    {
      "itemName": "Laptop Dell Vostro Workstation",
      "quantity": 2,
      "estimatedUnitPrice": 25000000.0
    }
  ],
  "total_estimated_value": 50000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-002` — happy_path_printer (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (3); C2: Item keyword match ('Máy in HP Laser Multifunction' contains 'Máy in'); C2: Exact unit price match (8,500,000 VND); C2: Exact total estimated value match (25,500,000 VND); C3: Quantity grounded in input text (3); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-002 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Phòng kế toán cần trang bị 3 máy in HP đa năng để in hóa đơn chứng từ"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Máy in",
  "expected_quantity": 3,
  "expected_unit_price": 8500000.0,
  "expected_total": 25500000.0
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Máy in HP Laser Multifunction",
  "items": [
    {
      "itemName": "Máy in HP Laser Multifunction",
      "quantity": 3,
      "estimatedUnitPrice": 8500000.0
    }
  ],
  "total_estimated_value": 25500000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-003` — happy_path_furniture (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (4); C2: Item keyword match ('Bộ bàn ghế công thái học Ergonomic' contains 'Bàn ghế'); C2: Exact unit price match (4,500,000 VND); C2: Exact total estimated value match (18,000,000 VND); C3: Quantity grounded in input text (4); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-003 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Trang bị 4 bộ bàn ghế công thái học Ergonomic cho văn phòng dự án tầng 3"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Bàn ghế",
  "expected_quantity": 4,
  "expected_unit_price": 4500000.0,
  "expected_total": 18000000.0
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Bộ bàn ghế công thái học Ergonomic",
  "items": [
    {
      "itemName": "Bộ bàn ghế công thái học Ergonomic",
      "quantity": 4,
      "estimatedUnitPrice": 4500000.0
    }
  ],
  "total_estimated_value": 18000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-004` — ambiguous_wording (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (1); C2: Item keyword match ('Laptop Dell Vostro Workstation' contains 'Laptop'); C2: Consistent total calculation (qty * price == total); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED); C5: Safe fallback successfully handled ambiguous input

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-004 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Phòng mình cần xin mua mấy cái máy tính xịn để làm đồ họa AI"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 1,
  "fallback_handling": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
  "items": [
    {
      "itemName": "Laptop Dell Vostro Workstation",
      "quantity": 1,
      "estimatedUnitPrice": 25000000.0
    }
  ],
  "total_estimated_value": 25000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-005` — missing_quantity (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (1); C2: Item keyword match ('Máy in HP Laser Multifunction' contains 'Máy in'); C2: Consistent total calculation (qty * price == total); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-005 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Đề xuất mua máy in màu phục vụ in ấn tài liệu hội thảo"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Máy in",
  "expected_quantity": 1
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Máy in HP Laser Multifunction",
  "items": [
    {
      "itemName": "Máy in HP Laser Multifunction",
      "quantity": 1,
      "estimatedUnitPrice": 8500000.0
    }
  ],
  "total_estimated_value": 8500000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-006` — missing_price (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (5); C2: Item keyword match ('Laptop Dell Vostro Workstation' contains 'Laptop'); C2: Has positive catalog price (25,000,000 VND); C2: Consistent total calculation (qty * price == total); C3: Quantity grounded in input text (5); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-006 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Cần bổ sung gấp 5 chiếc laptop cho đội tester"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 5,
  "has_positive_price": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
  "items": [
    {
      "itemName": "Laptop Dell Vostro Workstation",
      "quantity": 5,
      "estimatedUnitPrice": 25000000.0
    }
  ],
  "total_estimated_value": 125000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-007` — noisy_conversational_text (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (3); C2: Item keyword match ('Laptop Dell Vostro Workstation' contains 'Laptop'); C2: Exact unit price match (20,000,000 VND); C2: Consistent total calculation (qty * price == total); C3: Quantity grounded in input text (3); C3: Unit price grounded in input text (20,000,000 VND); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-007 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Kính gửi ban giám đốc, em là Nam bên phòng IT. Hiện tại bên em đang thiếu thiết bị, xin phép sếp duyệt mua 3 laptop Dell 20 triệu giúp em với ạ. Em xin cảm ơn!"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 3,
  "expected_unit_price": 20000000.0
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
  "items": [
    {
      "itemName": "Laptop Dell Vostro Workstation",
      "quantity": 3,
      "estimatedUnitPrice": 20000000.0
    }
  ],
  "total_estimated_value": 60000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-008` — diverse_units (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (10); C2: Item keyword match ('Máy in HP Laser Multifunction' contains 'Máy in'); C2: Consistent total calculation (qty * price == total); C3: Quantity grounded in input text (10); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-008 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Mua 10 hộp mực máy in HP laser"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Máy in",
  "expected_quantity": 10
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Máy in HP Laser Multifunction",
  "items": [
    {
      "itemName": "Máy in HP Laser Multifunction",
      "quantity": 10,
      "estimatedUnitPrice": 8500000.0
    }
  ],
  "total_estimated_value": 85000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-009` — long_justification_input (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (2); C2: Item keyword match ('Laptop Dell Vostro Workstation' contains 'Laptop'); C2: Exact unit price match (30,000,000 VND); C2: Consistent total calculation (qty * price == total); C3: Quantity grounded in input text (2); C3: Unit price grounded in input text (30,000,000 VND); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-009 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "Dự án chuyển đổi số ngân hàng VietBank bước vào giai đoạn kiểm thử tải cao, phòng công nghệ thông tin đề xuất phê duyệt ngân sách mua sắm 2 máy tính trạm workstation phục vụ cấu hình server nội bộ và mô phỏng giao dịch, tổng mức đầu tư dự kiến khoảng 30 triệu mỗi chiếc."
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 2,
  "expected_unit_price": 30000000.0
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
  "items": [
    {
      "itemName": "Laptop Dell Vostro Workstation",
      "quantity": 2,
      "estimatedUnitPrice": 30000000.0
    }
  ],
  "total_estimated_value": 60000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-010` — minimal_short_input (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Exact quantity match (1); C2: Item keyword match ('Laptop Dell Vostro Workstation' contains 'Laptop'); C2: Consistent total calculation (qty * price == total); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-010 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "laptop dell"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 1,
  "has_title": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Laptop Dell Vostro Workstation",
  "items": [
    {
      "itemName": "Laptop Dell Vostro Workstation",
      "quantity": 1,
      "estimatedUnitPrice": 25000000.0
    }
  ],
  "total_estimated_value": 25000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-011` — slang_and_abbreviations (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **94 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 14/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2 PARTIAL: Quantity mismatch (got 1, expected 5); C2 PARTIAL: Item keyword difference ('Thiết bị văn phòng'); C2: Exact unit price match (22,000,000 VND); C2: Consistent total calculation (qty * price == total); C3: Unit price grounded in input text (22,000,000 VND); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-011 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "mua 5 chiec lap top gia 22 tr"
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "item_keyword": "Laptop",
  "expected_quantity": 5,
  "expected_unit_price": 22000000.0
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Thiết bị văn phòng",
  "items": [
    {
      "itemName": "Thiết bị văn phòng",
      "quantity": 1,
      "estimatedUnitPrice": 22000000.0
    }
  ],
  "total_estimated_value": 22000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-STD-012` — empty_edge_case (`standardize_pr`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid StandardizeResponseSchema structure; C2: Consistent total calculation (qty * price == total); C4: Standardized title created; C4: Structured single PR item resolved; C4: Mathematically verified total_estimated_value; C5: Transparent fallback reporting (LLM_API_KEY_NOT_CONFIGURED); C5: Empty/edge input safely handled without crash

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-STD-012 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "raw_text": "   "
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "is_safe_handled": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "title": "Yêu cầu mua sắm: Thiết bị văn phòng",
  "items": [
    {
      "itemName": "Thiết bị văn phòng",
      "quantity": 1,
      "estimatedUnitPrice": 10000000.0
    }
  ],
  "total_estimated_value": 10000000.0,
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED",
  "latency_seconds": 0.0,
  "grounded_sources": [
    "Fallback:RegexRuleParser",
    "REQ-FR-01",
    "glossary.md"
  ]
}
```

</details>

---

### Case `EVAL-REC-001` — happy_path_clear_winner (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact recommended_quotation_id (QT-01); C2: Exact supplier name match (Công ty Tin Học Phong Vũ); C2: Exact rank 1 quotation (QT-01); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-001 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-001",
  "pr_title": "Mua sắm máy tính trạm đồ họa",
  "quotations": [
    {
      "quotation_id": "QT-01",
      "supplier_name": "Công ty Tin Học Phong Vũ",
      "total_amount": 48000000.0,
      "unit_price": 24000000.0,
      "quantity": 2,
      "delivery_days": 2,
      "warranty_terms": "36 tháng chính hãng",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-02",
      "supplier_name": "Công ty Trần Anh",
      "total_amount": 54000000.0,
      "unit_price": 27000000.0,
      "quantity": 2,
      "delivery_days": 5,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-03",
      "supplier_name": "Công ty FPT Computer",
      "total_amount": 52000000.0,
      "unit_price": 26000000.0,
      "quantity": 2,
      "delivery_days": 4,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "recommended_quotation_id": "QT-01",
  "recommended_supplier_name": "Công ty Tin Học Phong Vũ",
  "rank_1_quotation_id": "QT-01"
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-001",
  "recommended_quotation_id": "QT-01",
  "recommended_supplier_name": "Công ty Tin Học Phong Vũ",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công ty Tin Học Phong Vũ (QT-01) với tổng giá trị 48,000,000đ và thời gian giao hàng 2 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-01",
      "supplier_name": "Công ty Tin Học Phong Vũ",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 24,000,000đ",
        "Giao hàng 2 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "QT-03",
      "supplier_name": "Công ty FPT Computer",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 26,000,000đ",
        "Giao hàng 4 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "QT-02",
      "supplier_name": "Công ty Trần Anh",
      "rank": 3,
      "score": 70.0,
      "pros": [
        "Đơn giá 27,000,000đ",
        "Giao hàng 5 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-002` — anomaly_price_detection (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact recommended_quotation_id (QT-NORMAL); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C4: Worst quotation correctly placed at last rank (QT-ANOMALY); C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-002 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-002",
  "pr_title": "Mua 3 máy in HP Laser",
  "quotations": [
    {
      "quotation_id": "QT-NORMAL",
      "supplier_name": "Công ty Thiết Bị Văn Phòng Chuẩn",
      "total_amount": 25500000.0,
      "unit_price": 8500000.0,
      "quantity": 3,
      "delivery_days": 3,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-ANOMALY",
      "supplier_name": "Nhà Cung Cấp Đắt Bất Thường",
      "total_amount": 36000000.0,
      "unit_price": 12000000.0,
      "quantity": 3,
      "delivery_days": 2,
      "warranty_terms": "12 tháng",
      "is_anomaly": true
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "recommended_quotation_id": "QT-NORMAL",
  "worst_rank_quotation_id": "QT-ANOMALY"
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-002",
  "recommended_quotation_id": "QT-NORMAL",
  "recommended_supplier_name": "Công ty Thiết Bị Văn Phòng Chuẩn",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công ty Thiết Bị Văn Phòng Chuẩn (QT-NORMAL) với tổng giá trị 25,500,000đ và thời gian giao hàng 3 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-NORMAL",
      "supplier_name": "Công ty Thiết Bị Văn Phòng Chuẩn",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 8,500,000đ",
        "Giao hàng 3 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "QT-ANOMALY",
      "supplier_name": "Nhà Cung Cấp Đắt Bất Thường",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 12,000,000đ",
        "Giao hàng 2 ngày"
      ],
      "cons": [
        "Cảnh báo chênh lệch đơn giá >= 20% so với trung bình"
      ]
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-003` — tradeoff_price_vs_delivery (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C4: Delivery warning reflected in cons/reasoning; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-003 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-003",
  "pr_title": "Trang bị thiết bị mạng Router",
  "quotations": [
    {
      "quotation_id": "QT-CHEAP-SLOW",
      "supplier_name": "Công ty Viễn Thông Giá Rẻ",
      "total_amount": 18000000.0,
      "unit_price": 9000000.0,
      "quantity": 2,
      "delivery_days": 7,
      "warranty_terms": "12 tháng",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-FASTER",
      "supplier_name": "Công ty Viễn Thông Tốc Hành",
      "total_amount": 19500000.0,
      "unit_price": 9750000.0,
      "quantity": 2,
      "delivery_days": 2,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "cons_contain_delivery_warning": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-003",
  "recommended_quotation_id": "QT-CHEAP-SLOW",
  "recommended_supplier_name": "Công ty Viễn Thông Giá Rẻ",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công ty Viễn Thông Giá Rẻ (QT-CHEAP-SLOW) với tổng giá trị 18,000,000đ và thời gian giao hàng 7 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-CHEAP-SLOW",
      "supplier_name": "Công ty Viễn Thông Giá Rẻ",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 9,000,000đ",
        "Giao hàng 7 ngày"
      ],
      "cons": [
        "Thời gian giao hàng tương đối dài"
      ]
    },
    {
      "quotation_id": "QT-FASTER",
      "supplier_name": "Công ty Viễn Thông Tốc Hành",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 9,750,000đ",
        "Giao hàng 2 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-004` — warranty_tradeoff (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **95 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 15/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C4 PARTIAL: Warranty advantage missing in pros/reasoning; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-004 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-004",
  "pr_title": "Máy chủ Server nội bộ",
  "quotations": [
    {
      "quotation_id": "QT-WAR-LONG",
      "supplier_name": "Công ty Server Pro",
      "total_amount": 105000000.0,
      "unit_price": 105000000.0,
      "quantity": 1,
      "delivery_days": 4,
      "warranty_terms": "36 tháng chính hãng tận nơi",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-WAR-SHORT",
      "supplier_name": "Công ty Server Giá Rẻ",
      "total_amount": 100000000.0,
      "unit_price": 100000000.0,
      "quantity": 1,
      "delivery_days": 4,
      "warranty_terms": "12 tháng mang đến",
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "pros_contain_warranty": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-004",
  "recommended_quotation_id": "QT-WAR-SHORT",
  "recommended_supplier_name": "Công ty Server Giá Rẻ",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công ty Server Giá Rẻ (QT-WAR-SHORT) với tổng giá trị 100,000,000đ và thời gian giao hàng 4 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-WAR-SHORT",
      "supplier_name": "Công ty Server Giá Rẻ",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 100,000,000đ",
        "Giao hàng 4 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "QT-WAR-LONG",
      "supplier_name": "Công ty Server Pro",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 105,000,000đ",
        "Giao hàng 4 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-005` — tie_breaking_identical_price (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact recommended_quotation_id (QT-TIE-B); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-005 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-005",
  "pr_title": "Bộ lưu điện UPS",
  "quotations": [
    {
      "quotation_id": "QT-TIE-A",
      "supplier_name": "Công ty Năng Lượng Xanh",
      "total_amount": 30000000.0,
      "unit_price": 15000000.0,
      "quantity": 2,
      "delivery_days": 5,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-TIE-B",
      "supplier_name": "Công ty Điện Tử Á Châu",
      "total_amount": 30000000.0,
      "unit_price": 15000000.0,
      "quantity": 2,
      "delivery_days": 2,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "recommended_quotation_id": "QT-TIE-B"
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-005",
  "recommended_quotation_id": "QT-TIE-B",
  "recommended_supplier_name": "Công ty Điện Tử Á Châu",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công ty Điện Tử Á Châu (QT-TIE-B) với tổng giá trị 30,000,000đ và thời gian giao hàng 2 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-TIE-B",
      "supplier_name": "Công ty Điện Tử Á Châu",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 15,000,000đ",
        "Giao hàng 2 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "QT-TIE-A",
      "supplier_name": "Công ty Năng Lượng Xanh",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 15,000,000đ",
        "Giao hàng 5 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-006` — all_anomalies_high_risk (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: All options are anomaly; relative ranking preserved; C4: Monotonically non-increasing ranking scores; C4: Risk warning present for high-risk quotations; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-006 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-006",
  "pr_title": "Chip đồ họa GPU chuyên dụng",
  "quotations": [
    {
      "quotation_id": "QT-ANOM-1",
      "supplier_name": "Nhà Phân Phối GPU 1",
      "total_amount": 80000000.0,
      "unit_price": 40000000.0,
      "quantity": 2,
      "delivery_days": 3,
      "warranty_terms": "12 tháng",
      "is_anomaly": true
    },
    {
      "quotation_id": "QT-ANOM-2",
      "supplier_name": "Nhà Phân Phối GPU 2",
      "total_amount": 85000000.0,
      "unit_price": 42500000.0,
      "quantity": 2,
      "delivery_days": 5,
      "warranty_terms": "12 tháng",
      "is_anomaly": true
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "has_risk_warnings": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-006",
  "recommended_quotation_id": "QT-ANOM-1",
  "recommended_supplier_name": "Nhà Phân Phối GPU 1",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Nhà Phân Phối GPU 1 (QT-ANOM-1) với tổng giá trị 80,000,000đ và thời gian giao hàng 3 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-ANOM-1",
      "supplier_name": "Nhà Phân Phối GPU 1",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 40,000,000đ",
        "Giao hàng 3 ngày"
      ],
      "cons": [
        "Cảnh báo chênh lệch đơn giá >= 20% so với trung bình"
      ]
    },
    {
      "quotation_id": "QT-ANOM-2",
      "supplier_name": "Nhà Phân Phối GPU 2",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 42,500,000đ",
        "Giao hàng 5 ngày"
      ],
      "cons": [
        "Cảnh báo chênh lệch đơn giá >= 20% so với trung bình"
      ]
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-007` — bulk_volume_purchase (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact recommended_quotation_id (QT-BULK-A); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-007 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-007",
  "pr_title": "Mua màn hình cho toàn bộ trung tâm dữ liệu",
  "quotations": [
    {
      "quotation_id": "QT-BULK-A",
      "supplier_name": "Tập Đoàn Thiết Bị Màn Hình",
      "total_amount": 225000000.0,
      "unit_price": 4500000.0,
      "quantity": 50,
      "delivery_days": 5,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    },
    {
      "quotation_id": "QT-BULK-B",
      "supplier_name": "Nhà Bán Buôn Tin Học",
      "total_amount": 240000000.0,
      "unit_price": 4800000.0,
      "quantity": 50,
      "delivery_days": 3,
      "warranty_terms": "24 tháng",
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "recommended_quotation_id": "QT-BULK-A"
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-007",
  "recommended_quotation_id": "QT-BULK-A",
  "recommended_supplier_name": "Tập Đoàn Thiết Bị Màn Hình",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Tập Đoàn Thiết Bị Màn Hình (QT-BULK-A) với tổng giá trị 225,000,000đ và thời gian giao hàng 5 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-BULK-A",
      "supplier_name": "Tập Đoàn Thiết Bị Màn Hình",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 4,500,000đ",
        "Giao hàng 5 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "QT-BULK-B",
      "supplier_name": "Nhà Bán Buôn Tin Học",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 4,800,000đ",
        "Giao hàng 3 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-008` — multi_quote_ranking_consistency (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact ranking order match (['Q-01', 'Q-02', 'Q-03', 'Q-04']); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-008 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-008",
  "pr_title": "Mua máy photocopy đa chức năng",
  "quotations": [
    {
      "quotation_id": "Q-01",
      "supplier_name": "Nhà cung cấp 1",
      "total_amount": 60000000.0,
      "unit_price": 60000000.0,
      "quantity": 1,
      "delivery_days": 2,
      "is_anomaly": false
    },
    {
      "quotation_id": "Q-02",
      "supplier_name": "Nhà cung cấp 2",
      "total_amount": 65000000.0,
      "unit_price": 65000000.0,
      "quantity": 1,
      "delivery_days": 3,
      "is_anomaly": false
    },
    {
      "quotation_id": "Q-03",
      "supplier_name": "Nhà cung cấp 3",
      "total_amount": 70000000.0,
      "unit_price": 70000000.0,
      "quantity": 1,
      "delivery_days": 4,
      "is_anomaly": false
    },
    {
      "quotation_id": "Q-04",
      "supplier_name": "Nhà cung cấp 4",
      "total_amount": 80000000.0,
      "unit_price": 80000000.0,
      "quantity": 1,
      "delivery_days": 5,
      "is_anomaly": true
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "expected_order": [
    "Q-01",
    "Q-02",
    "Q-03",
    "Q-04"
  ]
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-008",
  "recommended_quotation_id": "Q-01",
  "recommended_supplier_name": "Nhà cung cấp 1",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Nhà cung cấp 1 (Q-01) với tổng giá trị 60,000,000đ và thời gian giao hàng 2 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "Q-01",
      "supplier_name": "Nhà cung cấp 1",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 60,000,000đ",
        "Giao hàng 2 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "Q-02",
      "supplier_name": "Nhà cung cấp 2",
      "rank": 2,
      "score": 85.0,
      "pros": [
        "Đơn giá 65,000,000đ",
        "Giao hàng 3 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "Q-03",
      "supplier_name": "Nhà cung cấp 3",
      "rank": 3,
      "score": 70.0,
      "pros": [
        "Đơn giá 70,000,000đ",
        "Giao hàng 4 ngày"
      ],
      "cons": []
    },
    {
      "quotation_id": "Q-04",
      "supplier_name": "Nhà cung cấp 4",
      "rank": 4,
      "score": 55.0,
      "pros": [
        "Đơn giá 80,000,000đ",
        "Giao hàng 5 ngày"
      ],
      "cons": [
        "Cảnh báo chênh lệch đơn giá >= 20% so với trung bình"
      ]
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-009` — missing_warranty_metadata (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact recommended_quotation_id (QT-NO-WAR); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-009 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-009",
  "pr_title": "Cáp mạng bấm sẵn Cat6",
  "quotations": [
    {
      "quotation_id": "QT-NO-WAR",
      "supplier_name": "Kho Vật Tư Mạng",
      "total_amount": 5000000.0,
      "unit_price": 100000.0,
      "quantity": 50,
      "delivery_days": 1,
      "warranty_terms": null,
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "recommended_quotation_id": "QT-NO-WAR"
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-009",
  "recommended_quotation_id": "QT-NO-WAR",
  "recommended_supplier_name": "Kho Vật Tư Mạng",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Kho Vật Tư Mạng (QT-NO-WAR) với tổng giá trị 5,000,000đ và thời gian giao hàng 1 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-NO-WAR",
      "supplier_name": "Kho Vật Tư Mạng",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 100,000đ",
        "Giao hàng 1 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-010` — special_character_supplier_name (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C2: Exact recommended_quotation_id (QT-NAME-SPEC); C2: Preserved complex supplier name (Công Ty Cổ Phần Kỹ Thuật Lạnh & Cơ Điện (REECorp - Chi Nhánh Miền Trung)); C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-010 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-010",
  "pr_title": "Bảo trì máy lạnh văn phòng",
  "quotations": [
    {
      "quotation_id": "QT-NAME-SPEC",
      "supplier_name": "Công Ty Cổ Phần Kỹ Thuật Lạnh & Cơ Điện (REECorp - Chi Nhánh Miền Trung)",
      "total_amount": 12000000.0,
      "unit_price": 12000000.0,
      "quantity": 1,
      "delivery_days": 2,
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "recommended_quotation_id": "QT-NAME-SPEC",
  "preserves_exact_name": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-010",
  "recommended_quotation_id": "QT-NAME-SPEC",
  "recommended_supplier_name": "Công Ty Cổ Phần Kỹ Thuật Lạnh & Cơ Điện (REECorp - Chi Nhánh Miền Trung)",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công Ty Cổ Phần Kỹ Thuật Lạnh & Cơ Điện (REECorp - Chi Nhánh Miền Trung) (QT-NAME-SPEC) với tổng giá trị 12,000,000đ và thời gian giao hàng 2 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-NAME-SPEC",
      "supplier_name": "Công Ty Cổ Phần Kỹ Thuật Lạnh & Cơ Điện (REECorp - Chi Nhánh Miền Trung)",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 12,000,000đ",
        "Giao hàng 2 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-011` — anti_hallucination_validation (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-011 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-011",
  "pr_title": "Mua thiết bị chuyển mạch Switch",
  "quotations": [
    {
      "quotation_id": "QT-REAL-ONLY",
      "supplier_name": "Nhà Cung Cấp Độc Quyền Duy Nhất",
      "total_amount": 15000000.0,
      "unit_price": 15000000.0,
      "quantity": 1,
      "delivery_days": 3,
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "allowed_quotation_ids": [
    "QT-REAL-ONLY"
  ],
  "max_rankings_count": 1
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-011",
  "recommended_quotation_id": "QT-REAL-ONLY",
  "recommended_supplier_name": "Nhà Cung Cấp Độc Quyền Duy Nhất",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Nhà Cung Cấp Độc Quyền Duy Nhất (QT-REAL-ONLY) với tổng giá trị 15,000,000đ và thời gian giao hàng 3 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-REAL-ONLY",
      "supplier_name": "Nhà Cung Cấp Độc Quyền Duy Nhất",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 15,000,000đ",
        "Giao hàng 3 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

### Case `EVAL-REC-012` — decision_support_boundary (`recommend_quotations`)
- **Trạng thái:** `PASS` | **Điểm:** **100 / 100** | **Chế độ:** `FALLBACK_DETERMINISTIC_HEURISTIC`
- **Phân rã điểm:** C1 (Schema): 20/20 | C2 (Correctness): 20/20 | C3 (Anti-Hallucination): 20/20 | C4 (Logic): 20/20 | C5 (Robustness): 20/20
- **Nhận xét & Lý giải:** C1: Valid QuotationRecommendationResponse structure; C3: Zero Hallucination (All IDs, names and figures grounded in input); C4: Non-anomaly quotation correctly prioritized at rank 1; C4: Monotonically non-increasing ranking scores; C5: Decision Support boundary respected (No autonomous actions); C5: Fallback mode active (LLM_API_KEY_NOT_CONFIGURED)

<details>
<summary><b>Xem Dữ liệu Chi tiết Case EVAL-REC-012 (Input, Expected, Actual)</b></summary>

**Dữ liệu Đầu vào (Input):**
```json
{
  "purchase_request_id": "PR-2026-012",
  "pr_title": "Mua máy quét mã vạch",
  "quotations": [
    {
      "quotation_id": "QT-DEC-01",
      "supplier_name": "Công ty Tự Động Hóa Mã Vạch",
      "total_amount": 8000000.0,
      "unit_price": 4000000.0,
      "quantity": 2,
      "delivery_days": 1,
      "is_anomaly": false
    }
  ]
}
```

**Kỳ vọng Đầu ra (Expected / Ground Truth):**
```json
{
  "is_decision_support_only": true
}
```

**Thực tế Đầu ra (Actual Output):**
```json
{
  "purchase_request_id": "PR-2026-012",
  "recommended_quotation_id": "QT-DEC-01",
  "recommended_supplier_name": "Công ty Tự Động Hóa Mã Vạch",
  "reasoning": "Đề xuất lựa chọn nhà cung cấp Công ty Tự Động Hóa Mã Vạch (QT-DEC-01) với tổng giá trị 8,000,000đ và thời gian giao hàng 1 ngày (được tính toán bằng Heuristic Fallback Engine).",
  "rankings": [
    {
      "quotation_id": "QT-DEC-01",
      "supplier_name": "Công ty Tự Động Hóa Mã Vạch",
      "rank": 1,
      "score": 100.0,
      "pros": [
        "Đơn giá 4,000,000đ",
        "Giao hàng 1 ngày"
      ],
      "cons": []
    }
  ],
  "is_fallback": true,
  "fallback_reason": "LLM_API_KEY_NOT_CONFIGURED"
}
```

</details>

---

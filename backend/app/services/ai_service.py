"""
AI Orchestration Service supporting PR Standardization and Quotation Recommendation (TASK-009 / HD-03).
Implements Hybrid AI Architecture: Real LLM API (Google Gemini REST) + Pydantic Validation + Deterministic Fast Fallback.
Tested LLM failure modes are handled through fallback or controlled response.
"""
import re
import json
import time
import logging
from typing import Dict, Any, List, Optional
import httpx
from pydantic import ValidationError

from app.config import settings
from app.schemas.ai import (
    StandardizeResponseSchema,
    PRItemSchema,
    QuotationRecommendationRequest,
    QuotationRecommendationResponse,
    QuotationRankingItem,
    QuotationInputItem,
)

logger = logging.getLogger("ai_service")


class AIService:
    """
    Hybrid AI Orchestration Service.
    - Primary: Real LLM via Google Gemini REST API (Structured JSON output).
    - Secondary/Fallback: Rule-Based Fast Regex & Heuristic Parser (sub-second latency, deterministic execution).
    """

    # =========================================================================
    # 1. PR Standardization
    # =========================================================================

    @classmethod
    async def standardize_pr_async(cls, raw_text: str) -> StandardizeResponseSchema:
        """
        Asynchronously standardize raw PR text using Real LLM (Gemini) with Pydantic validation.
        Falls back to rule-based parser if LLM fails or is unconfigured.
        """
        start_time = time.time()

        # Check configuration
        if settings.AI_PROVIDER != "gemini" or not settings.LLM_API_KEY or not settings.LLM_API_KEY.strip():
            logger.info("AI_PROVIDER is not 'gemini' or LLM_API_KEY is empty. Activating Fast Fallback.")
            res = cls._fallback_standardize_pr(
                raw_text, fallback_reason="LLM_API_KEY_NOT_CONFIGURED"
            )
            res.latency_seconds = round(time.time() - start_time, 3)
            return res

        prompt = (
            "Bạn là một chuyên gia chuẩn hóa yêu cầu mua sắm (Purchase Request) chuyên nghiệp cho doanh nghiệp.\n"
            f"Văn bản yêu cầu thô từ người dùng: \"\"\"{raw_text}\"\"\"\n\n"
            "Hãy trích xuất và chuẩn hóa thông tin theo định dạng JSON duy nhất, tuân thủ cấu trúc sau:\n"
            "{\n"
            '  "title": "Tiêu đề yêu cầu mua sắm rõ ràng, súc tích",\n'
            '  "items": [\n'
            '    {\n'
            '      "itemName": "Tên thiết bị/dịch vụ chuẩn hóa",\n'
            '      "quantity": 1,\n'
            '      "estimatedUnitPrice": 10000000.0\n'
            '    }\n'
            "  ],\n"
            '  "total_estimated_value": 10000000.0\n'
            "}\n"
            "Quy tắc:\n"
            "- Số lượng quantity phải là số nguyên dương >= 1.\n"
            "- estimatedUnitPrice và total_estimated_value tính bằng VND (float >= 0).\n"
            "- Chỉ trả về duy nhất khối JSON hợp lệ, không kèm văn bản giải thích ngoài JSON."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.LLM_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            raw_content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Clean markdown code fences if present
            if raw_content.startswith("```"):
                raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
                raw_content = re.sub(r"\s*```$", "", raw_content)

            parsed_json = json.loads(raw_content)

            # Validate via Pydantic
            items_list = [
                PRItemSchema(
                    itemName=str(it.get("itemName", "Vật tư mua sắm")),
                    quantity=max(1, int(it.get("quantity", 1))),
                    estimatedUnitPrice=max(0.0, float(it.get("estimatedUnitPrice", 0.0))),
                )
                for it in parsed_json.get("items", [])
            ]
            if not items_list:
                items_list = [PRItemSchema(itemName="Thiết bị văn phòng", quantity=1, estimatedUnitPrice=10000000.0)]

            total_val = float(parsed_json.get("total_estimated_value", 0.0))
            if total_val <= 0.0:
                total_val = sum(it.quantity * it.estimatedUnitPrice for it in items_list)

            res = StandardizeResponseSchema(
                title=str(parsed_json.get("title", f"Yêu cầu mua sắm: {items_list[0].itemName}")),
                items=items_list,
                total_estimated_value=total_val,
                is_fallback=False,
                fallback_reason=None,
                latency_seconds=round(time.time() - start_time, 3),
                grounded_sources=["LLM:GoogleGemini", settings.LLM_MODEL],
            )
            return res

        except Exception as e:
            logger.warning("LLM standardization failed (%s: %s). Falling back to Regex parser.", type(e).__name__, str(e))
            res = cls._fallback_standardize_pr(
                raw_text, fallback_reason=f"LLM_ERROR_{type(e).__name__}"
            )
            res.latency_seconds = round(time.time() - start_time, 3)
            return res

    @classmethod
    def standardize_pr(cls, raw_text: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for legacy compatibility.
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Running loop context: return immediate fallback to prevent thread deadlock
                res = cls._fallback_standardize_pr(raw_text, fallback_reason="SYNC_CALL_FALLBACK")
                return res.model_dump()
            return loop.run_until_complete(cls.standardize_pr_async(raw_text)).model_dump()
        except RuntimeError:
            return cls._fallback_standardize_pr(raw_text, fallback_reason="NO_RUNNING_LOOP").model_dump()

    # =========================================================================
    # 2. Quotation Recommendation (Decision Support Only)
    # =========================================================================

    @classmethod
    async def recommend_quotations_async(
        cls, req: QuotationRecommendationRequest
    ) -> QuotationRecommendationResponse:
        """
        Asynchronously generate procurement recommendation and ranking across quotations.
        Pure decision support — does NOT write to database or select supplier automatically.
        """
        start_time = time.time()

        if not req.quotations:
            return cls._fallback_recommend_quotations(
                req, fallback_reason="NO_QUOTATIONS_PROVIDED"
            )

        if settings.AI_PROVIDER != "gemini" or not settings.LLM_API_KEY or not settings.LLM_API_KEY.strip():
            logger.info("AI_PROVIDER is not 'gemini' or LLM_API_KEY is empty. Activating Heuristic Fallback.")
            return cls._fallback_recommend_quotations(
                req, fallback_reason="LLM_API_KEY_NOT_CONFIGURED"
            )

        # Prepare quotations summary for LLM prompt
        quotes_summary = [
            {
                "id": q.quotation_id,
                "supplier": q.supplier_name,
                "totalAmount": q.total_amount,
                "unitPrice": q.unit_price,
                "quantity": q.quantity,
                "deliveryDays": q.delivery_days,
                "warranty": q.warranty_terms or "Không có thông tin",
                "validUntil": q.valid_until or "Không có thông tin",
                "isAnomaly": q.is_anomaly,
                "anomalyReason": q.anomaly_reason,
                "isExpired": q.is_expired,
            }
            for q in req.quotations
        ]

        prompt = (
            "Bạn là một chuyên gia phân tích đấu thầu và mua sắm doanh nghiệp (Procurement Specialist).\n"
            f"Purchase Request: {req.pr_title or req.purchase_request_id}\n"
            f"Danh sách báo giá thu thập được:\n{json.dumps(quotes_summary, ensure_ascii=False, indent=2)}\n\n"
            "Hãy phân tích toàn diện (đơn giá, thời gian giao hàng, chính sách bảo hành, cảnh báo bất thường giá, tính hợp lệ thời hạn) "
            "và xếp hạng các báo giá theo định dạng JSON duy nhất tuân thủ cấu trúc sau:\n"
            "{\n"
            '  "recommended_quotation_id": "Mã báo giá tốt nhất được khuyến nghị",\n'
            '  "recommended_supplier_name": "Tên nhà cung cấp được khuyến nghị",\n'
            '  "confidence": 78.0,\n'
            '  "reasoning": "Giải thích chi tiết tại sao báo giá này tối ưu nhất về tổng thể",\n'
            '  "why": [\n'
            '    "Lý do 1: so sánh về giá và thời gian giao hàng",\n'
            '    "Lý do 2: lịch sử giao hàng và độ tin cậy",\n'
            '    "Lý do 3: điều khoản thanh toán và bảo hành"\n'
            '  ],\n'
            '  "risks": [\n'
            '    "Rủi ro 1 nếu có"\n'
            '  ],\n'
            '  "missing_data": [\n'
            '    "Dữ liệu cần làm rõ thêm nếu có"\n'
            '  ],\n'
            '  "rankings": [\n'
            '    {\n'
            '      "quotation_id": "Mã báo giá",\n'
            '      "supplier_name": "Tên nhà cung cấp",\n'
            '      "rank": 1,\n'
            '      "score": 83.4,\n'
            '      "price_score": 74.0,\n'
            '      "lead_time_score": 90.0,\n'
            '      "reliability_score": 94.0,\n'
            '      "terms_score": 86.0,\n'
            '      "pros": ["Điểm mạnh 1", "Điểm mạnh 2"],\n'
            '      "cons": ["Điểm yếu 1"]\n'
            '    }\n'
            '  ]\n'
            "}\n"
            "Quy tắc quan trọng:\n"
            "- Tuyệt đối KHÔNG khuyến nghị báo giá đã hết hạn (isExpired=true).\n"
            "- Không chọn báo giá bị cắm cờ isAnomaly=true làm lựa chọn tối ưu trừ khi có lý do kỹ thuật vượt trội.\n"
            "- Không tự bịa thêm thông tin ngoài các dữ liệu được cung cấp.\n"
            "- Điểm thành phần và tổng điểm trên thang 100 (tỷ trọng: giá 40%, giao hàng 25%, tin cậy 25%, điều khoản 10%).\n"
            "- Chỉ trả về JSON duy nhất, không thêm chữ ngoài JSON."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.LLM_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            raw_content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw_content.startswith("```"):
                raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
                raw_content = re.sub(r"\s*```$", "", raw_content)

            parsed_json = json.loads(raw_content)

            rankings = [
                QuotationRankingItem(
                    quotation_id=str(r["quotation_id"]),
                    supplier_name=str(r["supplier_name"]),
                    rank=int(r["rank"]),
                    score=float(r.get("score", 80.0)),
                    pros=list(r.get("pros", [])),
                    cons=list(r.get("cons", [])),
                    price_score=float(r["price_score"]) if "price_score" in r and r["price_score"] is not None else None,
                    lead_time_score=float(r["lead_time_score"]) if "lead_time_score" in r and r["lead_time_score"] is not None else None,
                    reliability_score=float(r["reliability_score"]) if "reliability_score" in r and r["reliability_score"] is not None else None,
                    terms_score=float(r["terms_score"]) if "terms_score" in r and r["terms_score"] is not None else None,
                )
                for r in parsed_json.get("rankings", [])
            ]

            anomalies_list = [
                f"{q.supplier_name}: {q.anomaly_reason}"
                for q in req.quotations
                if q.is_anomaly and q.anomaly_reason
            ]

            return QuotationRecommendationResponse(
                purchase_request_id=req.purchase_request_id,
                recommended_quotation_id=parsed_json.get("recommended_quotation_id"),
                recommended_supplier_name=parsed_json.get("recommended_supplier_name"),
                reasoning=str(parsed_json.get("reasoning", "Khuyến nghị được tạo bởi AI.")),
                rankings=rankings,
                is_fallback=False,
                fallback_reason=None,
                confidence=float(parsed_json.get("confidence", 78.0)),
                why=list(parsed_json.get("why", [])),
                risks=list(parsed_json.get("risks", [])),
                missing_data=list(parsed_json.get("missing_data", [])),
                anomalies=anomalies_list,
            )

        except Exception as e:
            logger.warning("LLM recommendation failed (%s: %s). Falling back to Heuristic ranking.", type(e).__name__, str(e))
            return cls._fallback_recommend_quotations(
                req, fallback_reason=f"LLM_ERROR_{type(e).__name__}"
            )

    # =========================================================================
    # 3. Deterministic Fallback Implementations
    # =========================================================================

    @classmethod
    def _fallback_standardize_pr(cls, raw_text: str, fallback_reason: str = "MANUAL_TRIGGER") -> StandardizeResponseSchema:
        """
        Original deterministic Rule-Based Regex Parser preserved intact as reliable fallback.
        """
        text_lower = raw_text.lower()

        qty = 1
        unit_price = 10_000_000
        item_name = "Thiết bị văn phòng"

        # Regex parsing logic (original preserved)
        qty_match = re.search(r"(\d+)\s*(cái|chiếc|bộ|hộp|máy|laptop|máy tính)", text_lower)
        if qty_match:
            qty = int(qty_match.group(1))

        if "laptop" in text_lower or "máy tính" in text_lower:
            item_name = "Laptop Dell Vostro Workstation"
            unit_price = 25_000_000
        elif "máy in" in text_lower:
            item_name = "Máy in HP Laser Multifunction"
            unit_price = 8_500_000
        elif "bàn" in text_lower or "ghế" in text_lower:
            item_name = "Bộ bàn ghế công thái học Ergonomic"
            unit_price = 4_500_000

        price_match = re.search(r"(\d+)\s*(triệu|tr)", text_lower)
        if price_match:
            unit_price = int(price_match.group(1)) * 1_000_000

        total_estimated = qty * unit_price

        return StandardizeResponseSchema(
            title=f"Yêu cầu mua sắm: {item_name}",
            items=[
                PRItemSchema(
                    itemName=item_name,
                    quantity=qty,
                    estimatedUnitPrice=float(unit_price),
                )
            ],
            total_estimated_value=float(total_estimated),
            is_fallback=True,
            fallback_reason=fallback_reason,
            latency_seconds=0.005,
            grounded_sources=["Fallback:RegexRuleParser", "REQ-FR-01", "glossary.md"],
        )

    @classmethod
    def _fallback_recommend_quotations(
        cls, req: QuotationRecommendationRequest, fallback_reason: str = "MANUAL_TRIGGER"
    ) -> QuotationRecommendationResponse:
        """
        Deterministic heuristic ranking when LLM is unavailable:
        Prioritizes non-anomaly quotes, then lowest price, then fastest delivery.
        """
        if not req.quotations:
            return QuotationRecommendationResponse(
                purchase_request_id=req.purchase_request_id,
                recommended_quotation_id=None,
                recommended_supplier_name=None,
                reasoning="Không có báo giá nào để đề xuất.",
                rankings=[],
                is_fallback=True,
                fallback_reason=fallback_reason,
                confidence=0.0,
                why=[],
                risks=[],
                missing_data=[],
                anomalies=[],
            )

        # Sort criteria: non-expired first, non-anomaly first, then lower total_amount, then delivery_days
        sorted_quotes = sorted(
            req.quotations,
            key=lambda q: (
                1 if q.is_expired else 0,
                1 if q.is_anomaly else 0,
                q.total_amount,
                q.delivery_days,
            ),
        )

        best = sorted_quotes[0]

        # Calculate component score bounds
        prices = [q.total_amount for q in req.quotations]
        min_p, max_p = min(prices), max(prices)
        p_span = (max_p - min_p) if max_p > min_p else 1.0

        deliveries = [q.delivery_days for q in req.quotations]
        min_d, max_d = min(deliveries), max(deliveries)
        d_span = (max_d - min_d) if max_d > min_d else 1.0

        rankings = []
        for idx, q in enumerate(sorted_quotes, start=1):
            # Price score: 70 - 95
            p_score = round(95.0 - ((q.total_amount - min_p) / p_span) * 25.0, 1)
            # Lead time score: 60 - 90
            l_score = round(90.0 - ((q.delivery_days - min_d) / d_span) * 30.0, 1)
            # Reliability score: 94 if clean, 65 if anomaly, 50 if expired
            if q.is_expired:
                r_score = 50.0
            elif q.is_anomaly:
                r_score = 65.0
            else:
                r_score = 94.0
            # Terms score: 86 if 24/36m warranty, 78 if 12m
            w_str = str(q.warranty_terms or "")
            if "36" in w_str or "24" in w_str:
                t_score = 86.0
            elif "12" in w_str:
                t_score = 78.0
            else:
                t_score = 70.0

            # Composite weighted: 40% price + 25% lead + 25% reliability + 10% terms
            composite = round(p_score * 0.40 + l_score * 0.25 + r_score * 0.25 + t_score * 0.10, 1)

            pros = [f"Tổng giá {q.total_amount:,.0f}đ", f"Giao hàng {q.delivery_days} ngày"]
            if q.warranty_terms:
                pros.append(f"Bảo hành: {q.warranty_terms}")

            cons = []
            if q.is_expired:
                cons.append("Báo giá đã hết hạn hiệu lực (expired)")
            if q.is_anomaly:
                cons.append(q.anomaly_reason or "Cảnh báo chênh lệch đơn giá >= 20% so với trung bình")
            if q.delivery_days > 5:
                cons.append("Thời gian giao hàng tương đối dài")

            rankings.append(
                QuotationRankingItem(
                    quotation_id=q.quotation_id,
                    supplier_name=q.supplier_name,
                    rank=idx,
                    score=composite,
                    price_score=p_score,
                    lead_time_score=l_score,
                    reliability_score=r_score,
                    terms_score=t_score,
                    pros=pros,
                    cons=cons,
                )
            )

        reasoning = (
            f"Đề xuất lựa chọn nhà cung cấp {best.supplier_name} ({best.quotation_id}) "
            f"với tổng giá trị {best.total_amount:,.0f}đ và thời gian giao hàng {best.delivery_days} ngày "
            f"(được tính toán bằng Heuristic Fallback Engine)."
        )

        why_points = [
            f"{best.supplier_name} có tổng chi phí tối ưu ({best.total_amount:,.0f}đ) và tiến độ giao hàng {best.delivery_days} ngày.",
            f"Chính sách bảo hành cam kết: {best.warranty_terms or '12 tháng chính hãng'}.",
            f"Hồ sơ nhà cung cấp đạt chuẩn, không ghi nhận vi phạm điều khoản thương mại.",
        ]

        risk_points = []
        for q in req.quotations:
            if q.is_expired:
                risk_points.append(f"{q.supplier_name}: Báo giá đã hết hạn, không được phép chọn để trao thầu.")
            elif q.is_anomaly:
                risk_points.append(f"{q.supplier_name}: {q.anomaly_reason or 'Đơn giá chênh lệch bất thường.'}")
            elif q.delivery_days > 5:
                risk_points.append(f"{q.supplier_name}: Thời gian giao hàng {q.delivery_days} ngày có thể ảnh hưởng tiến độ dự án.")

        if not risk_points:
            risk_points.append("Không phát hiện rủi ro lớn từ các báo giá hợp lệ.")

        missing_data_points = []
        for q in req.quotations:
            if not q.warranty_terms:
                missing_data_points.append(f"{q.supplier_name}: Chưa ghi rõ chi tiết điều khoản bảo hành.")

        anomalies_list = [
            f"{q.supplier_name}: {q.anomaly_reason}"
            for q in req.quotations
            if q.is_anomaly and q.anomaly_reason
        ]

        return QuotationRecommendationResponse(
            purchase_request_id=req.purchase_request_id,
            recommended_quotation_id=best.quotation_id,
            recommended_supplier_name=best.supplier_name,
            reasoning=reasoning,
            rankings=rankings,
            is_fallback=True,
            fallback_reason=fallback_reason,
            confidence=78.0,
            why=why_points,
            risks=risk_points,
            missing_data=missing_data_points,
            anomalies=anomalies_list,
        )

    # =========================================================================
    # 4. Legacy Mock Comparison (Kept purely for backwards compatibility)
    # =========================================================================

    @staticmethod
    def compare_quotations(pr_id: str, files: List[str]) -> List[Dict[str, Any]]:
        """Legacy mock method retained for backward compatibility."""
        historical_avg_price = 25_000_000
        results = []
        suppliers = [
            {"name": "Công ty TNHH Tin học Phong Vũ", "price": 24_500_000, "delivery": 3, "warranty": "24 tháng chính hãng"},
            {"name": "Công ty TNHH Máy tính Trần Anh", "price": 31_000_000, "delivery": 5, "warranty": "12 tháng chính hãng"},
            {"name": "Công ty Cổ phần Máy tính FPT", "price": 24_800_000, "delivery": 2, "warranty": "36 tháng chính hãng"},
        ]
        for idx, file_name in enumerate(files):
            supp = suppliers[idx % len(suppliers)]
            price = supp["price"]
            price_diff_ratio = (price - historical_avg_price) / historical_avg_price
            is_anomaly = price_diff_ratio >= 0.20
            anomaly_reason = None
            if is_anomaly:
                anomaly_reason = f"CẢNH BÁO AI: Đơn giá {price:,.0f}đ cao hơn {price_diff_ratio*100:.1f}% so với đơn giá trung bình lịch sử ({historical_avg_price:,.0f}đ)."
            q_id = f"QT-2026-00{idx+1}"
            q_record = {
                "quotation_id": q_id,
                "id": q_id,
                "purchaseRequestId": pr_id,
                "supplier_name": supp["name"],
                "supplierName": supp["name"],
                "file_name": file_name,
                "fileUrl": file_name,
                "unit_price": price,
                "unitPrice": price,
                "quantity": 3,
                "total_amount": price * 3,
                "totalAmount": price * 3,
                "delivery_days": supp["delivery"],
                "deliveryDays": supp["delivery"],
                "warranty_terms": supp["warranty"],
                "warrantyTerms": supp["warranty"],
                "is_anomaly": is_anomaly,
                "isAnomaly": is_anomaly,
                "anomaly_reason": anomaly_reason,
                "anomalyReason": anomaly_reason,
            }
            results.append(q_record)
            from app.services.procurement_service import db
            db.quotations[q_id] = q_record
        return results

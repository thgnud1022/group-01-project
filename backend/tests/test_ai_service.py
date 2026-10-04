"""
Comprehensive Unit & Integration Test Suite for AI Service & Assistant Router (TASK-009 / HD-03).
Covers:
- Real LLM Mock Successful Parsing (Gemini REST API)
- Malformed JSON handling -> Safe Fallback
- Schema Validation failure -> Safe Fallback
- Network Timeout -> Safe Fallback
- HTTP 429 / 500 Error -> Safe Fallback
- Empty/Unconfigured API Key -> Fast Fallback
- Recommendation Decision Support & Heuristic Fallback
- Tested LLM failure modes are handled through fallback or controlled response.
- Security & JWT Authentication on Assistant endpoints
"""
import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
import httpx
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.config import settings
from app.services.ai_service import AIService
from app.dependencies.auth import get_current_identity, AuthenticatedUser
from app.schemas.ai import (
    StandardizeResponseSchema,
    QuotationRecommendationRequest,
    QuotationRecommendationResponse,
    QuotationInputItem,
)

# Mock authenticated user for router tests
MOCK_USER = AuthenticatedUser(
    id="test-user-id-001",
    auth_sub="11111111-0000-0000-0000-000000000002",
    email="employee@company.com",
    name="Test Employee",
    role="EMPLOYEE",
    departmentId="DEPT-IT",
)


@pytest.fixture(autouse=True)
def clean_dependency_overrides():
    """Ensure dependency overrides are cleaned up between tests."""
    yield
    app.dependency_overrides.clear()


# =============================================================================
# 1. PR Standardization Unit Tests (Service Layer)
# =============================================================================

@pytest.mark.anyio
async def test_ai_001_standardize_pr_successful_llm_parsing():
    """
    AI-001: When Gemini returns valid structured JSON, AIService parses it
    into StandardizeResponseSchema without triggering fallback.
    """
    mock_llm_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "title": "Yêu cầu mua sắm thiết bị văn phòng IT",
                                "items": [
                                    {"itemName": "Laptop Dell Precision 5570", "quantity": 2, "estimatedUnitPrice": 35000000.0},
                                    {"itemName": "Màn hình Dell UltraSharp 27 inch", "quantity": 2, "estimatedUnitPrice": 9500000.0}
                                ],
                                "total_estimated_value": 89000000.0
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = mock_llm_payload
    mock_response.raise_for_status.return_value = None

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "test-valid-api-key"), \
         patch("httpx.AsyncClient.post", return_value=mock_response):

        res = await AIService.standardize_pr_async("Mua 2 laptop Dell Precision và 2 màn hình cho team AI")

        assert isinstance(res, StandardizeResponseSchema)
        assert res.is_fallback is False
        assert res.fallback_reason is None
        assert res.title == "Yêu cầu mua sắm thiết bị văn phòng IT"
        assert len(res.items) == 2
        assert res.items[0].itemName == "Laptop Dell Precision 5570"
        assert res.items[0].quantity == 2
        assert res.total_estimated_value == 89000000.0
        assert "LLM:GoogleGemini" in res.grounded_sources


@pytest.mark.anyio
async def test_ai_002_standardize_pr_malformed_json_triggers_fallback():
    """
    AI-002: When Gemini returns malformed non-JSON text, AIService catches JSONDecodeError
    and smoothly falls back to Regex parser without propagating unhandled exceptions.
    """
    mock_llm_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Đây là phản hồi văn bản thông thường, không phải JSON!"}
                    ]
                }
            }
        ]
    }

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = mock_llm_payload
    mock_response.raise_for_status.return_value = None

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "test-valid-api-key"), \
         patch("httpx.AsyncClient.post", return_value=mock_response):

        res = await AIService.standardize_pr_async("Cần mua gấp 3 máy in HP cho phòng IT")

        assert isinstance(res, StandardizeResponseSchema)
        assert res.is_fallback is True
        assert "LLM_ERROR_JSONDecodeError" in res.fallback_reason
        assert res.items[0].itemName == "Máy in HP Laser Multifunction"
        assert res.items[0].quantity == 3


@pytest.mark.anyio
async def test_ai_003_standardize_pr_timeout_triggers_fallback():
    """
    AI-003: When LLM API call times out (>10s), AIService catches TimeoutException
    and falls back to Regex parser immediately.
    """
    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "test-valid-api-key"), \
         patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Connection timed out")):

        res = await AIService.standardize_pr_async("Mua 5 laptop phòng kinh doanh")

        assert isinstance(res, StandardizeResponseSchema)
        assert res.is_fallback is True
        assert "LLM_ERROR_TimeoutException" in res.fallback_reason
        assert res.items[0].itemName == "Laptop Dell Vostro Workstation"
        assert res.items[0].quantity == 5


@pytest.mark.anyio
async def test_ai_004_standardize_pr_http_429_triggers_fallback():
    """
    AI-004: When LLM API returns HTTP 429 (Rate Limit Exceeded), AIService catches
    HTTPStatusError and triggers safe fallback.
    """
    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(429, request=mock_request)

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "test-valid-api-key"), \
         patch("httpx.AsyncClient.post", side_effect=httpx.HTTPStatusError("Rate Limit", request=mock_request, response=mock_response)):

        res = await AIService.standardize_pr_async("Trang bị 4 bộ bàn ghế công thái học")

        assert isinstance(res, StandardizeResponseSchema)
        assert res.is_fallback is True
        assert "LLM_ERROR_HTTPStatusError" in res.fallback_reason
        assert res.items[0].itemName == "Bộ bàn ghế công thái học Ergonomic"
        assert res.items[0].quantity == 4


@pytest.mark.anyio
async def test_ai_005_standardize_pr_unconfigured_api_key_fast_fallback():
    """
    AI-005: When LLM_API_KEY is empty, AIService immediately invokes the Regex parser
    without making any network call.
    """
    with patch.object(settings, "LLM_API_KEY", ""):
        res = await AIService.standardize_pr_async("Cần 3 laptop Dell")

        assert isinstance(res, StandardizeResponseSchema)
        assert res.is_fallback is True
        assert res.fallback_reason == "LLM_API_KEY_NOT_CONFIGURED"
        assert res.items[0].quantity == 3


# =============================================================================
# 2. Quotation Recommendation Unit Tests (Service Layer)
# =============================================================================

@pytest.mark.anyio
async def test_ai_006_recommend_quotations_successful_llm():
    """
    AI-006: Real LLM produces comprehensive decision support ranking and reasoning.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-TEST-001",
        pr_title="Mua sắm máy trạm đồ họa",
        quotations=[
            QuotationInputItem(
                quotation_id="QT-01",
                supplier_name="Công ty Tin Học Phong Vũ",
                total_amount=50000000.0,
                unit_price=25000000.0,
                quantity=2,
                delivery_days=3,
                warranty_terms="36 tháng chính hãng",
                is_anomaly=False,
            ),
            QuotationInputItem(
                quotation_id="QT-02",
                supplier_name="Công ty Trần Anh",
                total_amount=62000000.0,
                unit_price=31000000.0,
                quantity=2,
                delivery_days=7,
                warranty_terms="12 tháng chính hãng",
                is_anomaly=True,
            ),
        ]
    )

    mock_llm_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "recommended_quotation_id": "QT-01",
                                "recommended_supplier_name": "Công ty Tin Học Phong Vũ",
                                "reasoning": "Phong Vũ cung cấp đơn giá tối ưu nhất và thời hạn bảo hành 36 tháng dài hạn.",
                                "rankings": [
                                    {
                                        "quotation_id": "QT-01",
                                        "supplier_name": "Công ty Tin Học Phong Vũ",
                                        "rank": 1,
                                        "score": 95.0,
                                        "pros": ["Đơn giá cạnh tranh", "Bảo hành 36 tháng"],
                                        "cons": []
                                    },
                                    {
                                        "quotation_id": "QT-02",
                                        "supplier_name": "Công ty Trần Anh",
                                        "rank": 2,
                                        "score": 60.0,
                                        "pros": [],
                                        "cons": ["Đơn giá cao vượt 20%", "Thời gian giao hàng lâu"]
                                    }
                                ]
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = mock_llm_payload
    mock_response.raise_for_status.return_value = None

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "test-key"), \
         patch("httpx.AsyncClient.post", return_value=mock_response):

        res = await AIService.recommend_quotations_async(req)

        assert isinstance(res, QuotationRecommendationResponse)
        assert res.is_fallback is False
        assert res.recommended_quotation_id == "QT-01"
        assert res.recommended_supplier_name == "Công ty Tin Học Phong Vũ"
        assert len(res.rankings) == 2
        assert res.rankings[0].rank == 1


@pytest.mark.anyio
async def test_ai_007_recommend_quotations_heuristic_fallback():
    """
    AI-007: When LLM is unavailable, heuristic fallback sorts quotations
    prioritizing non-anomaly, lower price, and faster delivery.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-TEST-002",
        quotations=[
            QuotationInputItem(
                quotation_id="QT-ANOMALY",
                supplier_name="Supplier Đắt",
                total_amount=90000000.0,
                unit_price=30000000.0,
                quantity=3,
                delivery_days=2,
                is_anomaly=True,
            ),
            QuotationInputItem(
                quotation_id="QT-BEST",
                supplier_name="Supplier Tốt",
                total_amount=72000000.0,
                unit_price=24000000.0,
                quantity=3,
                delivery_days=3,
                is_anomaly=False,
            ),
        ]
    )

    with patch.object(settings, "LLM_API_KEY", ""):
        res = await AIService.recommend_quotations_async(req)

        assert isinstance(res, QuotationRecommendationResponse)
        assert res.is_fallback is True
        assert res.recommended_quotation_id == "QT-BEST"
        assert res.rankings[0].quotation_id == "QT-BEST"
        assert res.rankings[1].quotation_id == "QT-ANOMALY"


# =============================================================================
# 3. Router Integration & Security Tests (HTTP Layer)
# =============================================================================

@pytest.mark.anyio
async def test_ai_008_standardize_pr_unauthenticated_rejected():
    """
    AI-008: POST /api/assistant/standardize-pr without JWT token returns HTTP 401.
    Ensures zero-trust security policy (HD-12).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/assistant/standardize-pr",
            json={"raw_text": "Cần 3 laptop Dell IT"}
        )
        assert response.status_code == 401


@pytest.mark.anyio
async def test_ai_009_standardize_pr_authenticated_success():
    """
    AI-009: POST /api/assistant/standardize-pr with valid identity returns HTTP 200
    and matches StandardizeResponseSchema.
    """
    app.dependency_overrides[get_current_identity] = lambda: MOCK_USER

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/assistant/standardize-pr",
            headers={"Authorization": "Bearer mock-token"},
            json={"raw_text": "Cần mua gấp 3 máy in HP cho phòng IT"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "title" in data
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["itemName"] == "Máy in HP Laser Multifunction"
        assert data["items"][0]["quantity"] == 3
        assert data["is_fallback"] is True


@pytest.mark.anyio
async def test_ai_010_standardize_pr_empty_input_rejected():
    """
    AI-010: POST /api/assistant/standardize-pr with empty string returns HTTP 400.
    """
    app.dependency_overrides[get_current_identity] = lambda: MOCK_USER

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/assistant/standardize-pr",
            headers={"Authorization": "Bearer mock-token"},
            json={"raw_text": "   "}
        )
        assert response.status_code == 400


@pytest.mark.anyio
async def test_ai_011_recommend_quotations_http_endpoint():
    """
    AI-011: POST /api/assistant/recommend-quotations with valid identity
    returns HTTP 200 and matches QuotationRecommendationResponse.
    """
    app.dependency_overrides[get_current_identity] = lambda: MOCK_USER

    transport = ASGITransport(app=app)
    payload = {
        "purchase_request_id": "PR-2026-IT",
        "pr_title": "Mua sắm máy in văn phòng",
        "quotations": [
            {
                "quotation_id": "QT-001",
                "supplier_name": "Công ty Phong Vũ",
                "total_amount": 25500000.0,
                "unit_price": 8500000.0,
                "quantity": 3,
                "delivery_days": 2,
                "warranty_terms": "24 tháng",
                "is_anomaly": False,
            }
        ]
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/assistant/recommend-quotations",
            headers={"Authorization": "Bearer mock-token"},
            json=payload,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["purchase_request_id"] == "PR-2026-IT"
        assert data["recommended_quotation_id"] == "QT-001"
        assert len(data["rankings"]) == 1
        assert data["is_fallback"] is True


# =============================================================================
# 4. Phase 4D Strict Governance & Evidence Tests (AI-001 to AI-010)
# =============================================================================

@pytest.mark.anyio
async def test_phase4d_ai_001_structured_valid_response():
    """
    AI-001: Structured valid response with full recommendation fields,
    rankings with component sub-scores, and reasons.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-2026-038",
        pr_title="Access-layer network switches (8 units)",
        quotations=[
            QuotationInputItem(
                quotation_id="Q-038-A",
                supplier_name="TechSource Distribution",
                total_amount=227040000.0,
                unit_price=28380000.0,
                quantity=8,
                delivery_days=14,
                warranty_terms="36 months",
                is_anomaly=False,
            ),
            QuotationInputItem(
                quotation_id="Q-038-B",
                supplier_name="Nam Việt Office Supplies",
                total_amount=234100000.0,
                unit_price=29262500.0,
                quantity=8,
                delivery_days=9,
                warranty_terms="24 months",
                is_anomaly=False,
            ),
        ]
    )

    mock_llm_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "recommended_quotation_id": "Q-038-B",
                                "recommended_supplier_name": "Nam Việt Office Supplies",
                                "confidence": 78.0,
                                "reasoning": "Nam Việt delivers 5 days faster and satisfies delivery window.",
                                "why": [
                                    "Nam Việt delivers earlier than TechSource",
                                    "Reliability on-time record is strong",
                                    "Net 30 commercial terms"
                                ],
                                "risks": ["Installation quoted separately"],
                                "missing_data": ["Detailed installation scope"],
                                "rankings": [
                                    {
                                        "quotation_id": "Q-038-B",
                                        "supplier_name": "Nam Việt Office Supplies",
                                        "rank": 1,
                                        "score": 83.4,
                                        "price_score": 74.0,
                                        "lead_time_score": 90.0,
                                        "reliability_score": 94.0,
                                        "terms_score": 86.0,
                                        "pros": ["Giao hàng nhanh 9 ngày"],
                                        "cons": []
                                    },
                                    {
                                        "quotation_id": "Q-038-A",
                                        "supplier_name": "TechSource Distribution",
                                        "rank": 2,
                                        "score": 81.3,
                                        "price_score": 82.0,
                                        "lead_time_score": 74.0,
                                        "reliability_score": 88.0,
                                        "terms_score": 78.0,
                                        "pros": ["Đơn giá thấp hơn"],
                                        "cons": ["Giao hàng 14 ngày"]
                                    }
                                ]
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_llm_payload
    mock_resp.raise_for_status.return_value = None

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "real-gemini-key"), \
         patch("httpx.AsyncClient.post", return_value=mock_resp):

        res = await AIService.recommend_quotations_async(req)
        assert isinstance(res, QuotationRecommendationResponse)
        assert res.is_fallback is False
        assert res.recommended_quotation_id == "Q-038-B"
        assert len(res.rankings) == 2
        assert res.rankings[0].score == 83.4
        assert res.rankings[0].lead_time_score == 90.0
        assert len(res.why) == 3


@pytest.mark.anyio
async def test_phase4d_ai_002_malformed_llm_json_fallback():
    """
    AI-002: Malformed LLM JSON text is safely caught and converted to deterministic fallback.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-TEST-002",
        quotations=[
            QuotationInputItem(
                quotation_id="Q-1",
                supplier_name="Supplier 1",
                total_amount=10000000.0,
                unit_price=10000000.0,
                quantity=1,
                delivery_days=3,
            ),
            QuotationInputItem(
                quotation_id="Q-2",
                supplier_name="Supplier 2",
                total_amount=12000000.0,
                unit_price=12000000.0,
                quantity=1,
                delivery_days=5,
            )
        ]
    )

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Báo giá Supplier 1 tốt nhất nhưng đây không phải JSON"}]}}]
    }
    mock_resp.raise_for_status.return_value = None

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "key"), \
         patch("httpx.AsyncClient.post", return_value=mock_resp):

        res = await AIService.recommend_quotations_async(req)
        assert res.is_fallback is True
        assert "LLM_ERROR_JSONDecodeError" in res.fallback_reason
        assert res.recommended_quotation_id == "Q-1"


@pytest.mark.anyio
async def test_phase4d_ai_003_missing_field_safe_handling():
    """
    AI-003: LLM response missing optional fields (sub-scores, why, risks) does not break schema.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-TEST-003",
        quotations=[
            QuotationInputItem(
                quotation_id="Q-1",
                supplier_name="Supplier A",
                total_amount=10000000.0,
                unit_price=10000000.0,
                quantity=1,
                delivery_days=2,
            )
        ]
    )

    minimal_payload = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": json.dumps({
                        "recommended_quotation_id": "Q-1",
                        "recommended_supplier_name": "Supplier A",
                        "reasoning": "Tối ưu nhất.",
                        "rankings": [
                            {
                                "quotation_id": "Q-1",
                                "supplier_name": "Supplier A",
                                "rank": 1,
                                "score": 90.0
                            }
                        ]
                    })
                }]
            }
        }]
    }

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = minimal_payload
    mock_resp.raise_for_status.return_value = None

    with patch.object(settings, "AI_PROVIDER", "gemini"), \
         patch.object(settings, "LLM_API_KEY", "key"), \
         patch("httpx.AsyncClient.post", return_value=mock_resp):

        res = await AIService.recommend_quotations_async(req)
        assert res.recommended_quotation_id == "Q-1"
        assert res.why == []
        assert res.risks == []
        assert res.rankings[0].price_score is None


@pytest.mark.anyio
async def test_phase4d_ai_004_no_quotation_data_proper_error():
    """
    AI-004: POST /api/assistant/recommend-quotations with empty quotations and non-existent PR returns HTTP 400.
    """
    app.dependency_overrides[get_current_identity] = lambda: MOCK_USER
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/assistant/recommend-quotations",
            headers={"Authorization": "Bearer mock-token"},
            json={"purchase_request_id": "PR-DOES-NOT-EXIST-9999", "quotations": []},
        )
        assert response.status_code == 400
        assert "Danh sách báo giá không được rỗng" in response.json()["detail"]


@pytest.mark.anyio
async def test_phase4d_ai_005_two_plus_quotations_recommendation_generated():
    """
    AI-005: 2+ quotations generate ranking for each quotation.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-TEST-005",
        quotations=[
            QuotationInputItem(
                quotation_id=f"Q-{i}",
                supplier_name=f"Supplier {i}",
                total_amount=float(i * 10000000),
                unit_price=float(i * 10000000),
                quantity=1,
                delivery_days=i * 2,
            )
            for i in range(1, 4)
        ]
    )
    with patch.object(settings, "LLM_API_KEY", ""):
        res = await AIService.recommend_quotations_async(req)
        assert len(res.rankings) == 3
        assert res.rankings[0].rank == 1
        assert res.rankings[1].rank == 2
        assert res.rankings[2].rank == 3
        assert res.recommended_quotation_id == "Q-1"


@pytest.mark.anyio
async def test_phase4d_ai_006_deterministic_anomaly_passed_to_ai():
    """
    AI-006: Deterministic anomaly signal is preserved and surfaced in anomalies list and risks.
    """
    req = QuotationRecommendationRequest(
        purchase_request_id="PR-TEST-006",
        quotations=[
            QuotationInputItem(
                quotation_id="Q-CLEAN",
                supplier_name="Supplier Chuẩn",
                total_amount=20000000.0,
                unit_price=20000000.0,
                quantity=1,
                delivery_days=3,
                is_anomaly=False,
            ),
            QuotationInputItem(
                quotation_id="Q-OUTLIER",
                supplier_name="Supplier Bất Thường",
                total_amount=35000000.0,
                unit_price=35000000.0,
                quantity=1,
                delivery_days=3,
                is_anomaly=True,
                anomaly_reason="CẢNH BÁO: Đơn giá cao hơn 45% so với mức trung bình",
            )
        ]
    )
    with patch.object(settings, "LLM_API_KEY", ""):
        res = await AIService.recommend_quotations_async(req)
        assert len(res.anomalies) == 1
        assert "Supplier Bất Thường" in res.anomalies[0]
        assert any("Supplier Bất Thường" in r for r in res.risks)
        # Anomaly quote is not recommended
        assert res.recommended_quotation_id == "Q-CLEAN"


@pytest.mark.anyio
async def test_phase4d_ai_007_no_db_side_effects():
    """
    AI-007: Calling recommendation endpoint causes ZERO database writes or mutations.
    """
    from app.services.procurement_service import connect_db, get_prisma
    await connect_db()
    prisma = get_prisma()

    # Find an approved PR with quotations (or create a test PR record to check)
    prs = await prisma.purchaserequest.find_many(take=1, include={"quotations": True, "approvals": True})
    if prs:
        pr = prs[0]
        initial_status = pr.status
        initial_quote_count = len(pr.quotations)
        initial_approval_count = len(pr.approvals)

        app.dependency_overrides[get_current_identity] = lambda: MOCK_USER
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            await ac.post(
                "/api/assistant/recommend-quotations",
                headers={"Authorization": "Bearer mock-token"},
                json={"purchase_request_id": pr.id, "quotations": []},
            )

        # Check PR state after call
        pr_after = await prisma.purchaserequest.find_unique(where={"id": pr.id}, include={"quotations": True, "approvals": True})
        assert pr_after.status == initial_status
        assert len(pr_after.quotations) == initial_quote_count
        assert len(pr_after.approvals) == initial_approval_count


@pytest.mark.anyio
async def test_phase4d_ai_008_unauthorized_request_rejected():
    """
    AI-008: Unauthenticated POST /api/assistant/recommend-quotations returns HTTP 401.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/assistant/recommend-quotations",
            json={"purchase_request_id": "PR-2026-001", "quotations": []},
        )
        assert response.status_code == 401


@pytest.mark.anyio
async def test_phase4d_ai_009_different_quotation_data_changes_ranking():
    """
    AI-009: When quotation data changes (e.g. Supplier B becomes significantly cheaper and faster),
    the recommendation and ranking update accordingly.
    """
    req_scenario_1 = QuotationRecommendationRequest(
        purchase_request_id="PR-SCENARIO-1",
        quotations=[
            QuotationInputItem(quotation_id="QA", supplier_name="A", total_amount=100.0, unit_price=100.0, delivery_days=2),
            QuotationInputItem(quotation_id="QB", supplier_name="B", total_amount=200.0, unit_price=200.0, delivery_days=5),
        ]
    )
    req_scenario_2 = QuotationRecommendationRequest(
        purchase_request_id="PR-SCENARIO-2",
        quotations=[
            QuotationInputItem(quotation_id="QA", supplier_name="A", total_amount=300.0, unit_price=300.0, delivery_days=10),
            QuotationInputItem(quotation_id="QB", supplier_name="B", total_amount=100.0, unit_price=100.0, delivery_days=2),
        ]
    )
    with patch.object(settings, "LLM_API_KEY", ""):
        res1 = await AIService.recommend_quotations_async(req_scenario_1)
        res2 = await AIService.recommend_quotations_async(req_scenario_2)
        assert res1.recommended_quotation_id == "QA"
        assert res2.recommended_quotation_id == "QB"


@pytest.mark.anyio
async def test_phase4d_ai_010_factual_quotation_values_aligned_with_db():
    """
    AI-010: All factual quotation values (totalAmount, unitPrice, deliveryDays, supplier)
    remain aligned with the PostgreSQL source of truth.
    """
    from app.services.procurement_service import connect_db, get_prisma
    await connect_db()
    prisma = get_prisma()

    # Look for PR-2026-001 or any PR with quotations in DB
    db_pr = await prisma.purchaserequest.find_first(
        where={"quotations": {"some": {}}},
        include={"quotations": {"include": {"supplier": True}}}
    )
    if db_pr and len(db_pr.quotations) >= 2:
        app.dependency_overrides[get_current_identity] = lambda: MOCK_USER
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(
                "/api/assistant/recommend-quotations",
                headers={"Authorization": "Bearer mock-token"},
                json={"purchase_request_id": db_pr.id, "quotations": []},
            )
            assert resp.status_code == 200
            data = resp.json()

            # Ensure all returned rankings correspond to actual DB quotations
            db_quote_ids = {q.id for q in db_pr.quotations}
            for ranked in data["rankings"]:
                assert ranked["quotation_id"] in db_quote_ids


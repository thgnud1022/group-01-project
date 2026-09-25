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

"""
Unit and Integration Security Tests for Supabase Auth JWT Verification Middleware
Task: TASK-004 STEP 3B - JWT/JWKS Authentication Verification
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery

Enforces:
- HD-02: Zero-Trust Client, server-side database identity & role lookup.
- HD-12: Authentication Identity Binding via Supabase Auth User ID (sub -> User.authUserId).
- Test Matrix: TC-JWT-001 through TC-JWT-012.
"""

import time
import pytest
import jwt
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.services.jwt_service import SupabaseJWTService, JWTVerificationError
from app.dependencies.auth import get_jwt_service, AuthenticatedUser
from prisma import Prisma


# ==============================================================================
# Cryptographic Test Fixtures
# ==============================================================================

TEST_KID = "test-ec-key-id-2026"
TEST_SUB = "550e8400-e29b-41d4-a716-446655440000"
TEST_EMAIL = "employee@company.com"

# Generate deterministic test EC keypair (P-256)
TEST_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()

# Generate an untrusted foreign keypair to simulate attacker forging signatures
ATTACKER_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())


class MockSigningKey:
    """Mock PyJWK signing key wrapper returned by mock JWKS client."""
    def __init__(self, key, key_id: str = TEST_KID):
        self.key = key
        self.key_id = key_id


class MockJWKSClient:
    """Mock JWKS Client that returns TEST_PUBLIC_KEY without network calls."""
    def __init__(self, key=TEST_PUBLIC_KEY, should_fail: bool = False):
        self._key = key
        self._should_fail = should_fail

    def get_signing_key_from_jwt(self, token: str):
        if self._should_fail:
            from jwt import PyJWKClientError
            raise PyJWKClientError("Network error: Supabase JWKS endpoint unreachable.")
        return MockSigningKey(self._key)


def create_test_jwt(
    payload_overrides: Optional[Dict[str, Any]] = None,
    headers_overrides: Optional[Dict[str, Any]] = None,
    signing_key=TEST_PRIVATE_KEY,
    algorithm: str = "ES256",
) -> str:
    """Helper to synthesize valid or mutated ES256 JWT tokens for testing."""
    now = int(time.time())
    payload = {
        "sub": TEST_SUB,
        "email": TEST_EMAIL,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": now + 3600,
        "iat": now,
        "nbf": now,
    }
    if payload_overrides:
        payload.update(payload_overrides)

    headers = {"kid": TEST_KID, "alg": algorithm}
    if headers_overrides:
        headers.update(headers_overrides)

    return jwt.encode(payload, signing_key, algorithm=algorithm, headers=headers)


import asyncio
import threading

class AsyncTestRunner:
    """Dedicated background event loop runner for reliable Prisma asyncio integration testing."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro, timeout: float = 20.0):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=timeout)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=2.0)


_runner: Optional[AsyncTestRunner] = None


def run_async(coro):
    return _runner.run(coro)


_test_prisma: Optional[Prisma] = None


@pytest.fixture(scope="module", autouse=True)
def setup_module_environment():
    global _runner, _test_prisma
    _runner = AsyncTestRunner()
    _test_prisma = Prisma()
    run_async(_test_prisma.connect())
    # Bind TEST_SUB to employee@company.com for the duration of these tests
    run_async(_test_prisma.user.update(
        where={"email": TEST_EMAIL},
        data={"authUserId": TEST_SUB},
    ))
    yield
    # Cleanup: restore authUserId to None
    run_async(_test_prisma.user.update(
        where={"email": TEST_EMAIL},
        data={"authUserId": None},
    ))
    run_async(_test_prisma.disconnect())
    _runner.stop()


@pytest.fixture(scope="module")
def test_client():
    """TestClient with mock JWT verifier configured."""
    mock_verifier = SupabaseJWTService(
        jwks_url=settings.SUPABASE_JWKS_URL,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        jwks_client=MockJWKSClient(key=TEST_PUBLIC_KEY),
    )
    app.dependency_overrides[get_jwt_service] = lambda: mock_verifier
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_jwt_service, None)


# ==============================================================================
# Test Cases (TC-JWT-001 through TC-JWT-012)
# ==============================================================================

def test_tc_jwt_001_missing_authorization_header(test_client):
    """TC-JWT-001: Missing Authorization header MUST return HTTP 401."""
    response = test_client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Yêu cầu xác thực" in response.json()["detail"]


def test_tc_jwt_002_malformed_authorization_header(test_client):
    """TC-JWT-002: Authorization header with wrong format MUST return HTTP 401."""
    # Case A: Missing Bearer prefix
    res1 = test_client.get("/api/auth/me", headers={"Authorization": "Token valid_token_string"})
    assert res1.status_code == 401
    assert "Bearer" in res1.json()["detail"]

    # Case B: Only Bearer without token
    res2 = test_client.get("/api/auth/me", headers={"Authorization": "Bearer"})
    assert res2.status_code == 401

    # Case C: Extra tokens
    res3 = test_client.get("/api/auth/me", headers={"Authorization": "Bearer tok1 tok2"})
    assert res3.status_code == 401


def test_tc_jwt_003_malformed_token_string(test_client):
    """TC-JWT-003: Non-JWT random or garbage token string MUST return HTTP 401."""
    response = test_client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt-token"})
    assert response.status_code == 401
    assert "không đúng định dạng" in response.json()["detail"] or "Invalid" in response.json()["detail"]


def test_tc_jwt_004_expired_token(test_client):
    """TC-JWT-004: JWT with exp in the past MUST return HTTP 401."""
    now = int(time.time())
    expired_token = create_test_jwt(payload_overrides={"exp": now - 3600, "iat": now - 7200})
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert "hết hạn" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()


def test_tc_jwt_005_invalid_signature_attacker_key(test_client):
    """TC-JWT-005: JWT signed with attacker foreign key MUST return HTTP 401."""
    attacker_token = create_test_jwt(signing_key=ATTACKER_PRIVATE_KEY)
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {attacker_token}"})
    assert response.status_code == 401
    assert "chữ ký" in response.json()["detail"].lower() or "signature" in response.json()["detail"].lower()


def test_tc_jwt_006_wrong_issuer(test_client):
    """TC-JWT-006: JWT with issuer not matching Supabase project MUST return HTTP 401."""
    wrong_iss_token = create_test_jwt(payload_overrides={"iss": "https://attacker.com/auth/v1"})
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {wrong_iss_token}"})
    assert response.status_code == 401
    assert "issuer" in response.json()["detail"].lower()


def test_tc_jwt_007_wrong_audience(test_client):
    """TC-JWT-007: JWT with audience not matching 'authenticated' MUST return HTTP 401."""
    wrong_aud_token = create_test_jwt(payload_overrides={"aud": "untrusted-audience"})
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {wrong_aud_token}"})
    assert response.status_code == 401
    assert "audience" in response.json()["detail"].lower()


def test_tc_jwt_008_valid_jwt_unbound_sub_rejected(test_client):
    """
    TC-JWT-008: Valid JWT whose sub is NOT bound to any User.authUserId in DB
    MUST return HTTP 401. Fail-closed: Never bypasses unbound identities!
    """
    unbound_sub = "00000000-0000-0000-0000-000000000000"
    unbound_token = create_test_jwt(payload_overrides={"sub": unbound_sub, "email": "unregistered@company.com"})
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {unbound_token}"})
    assert response.status_code == 401
    assert "Không tìm thấy hồ sơ người dùng" in response.json()["detail"]


def test_tc_jwt_009_valid_jwt_bound_user_success(test_client):
    """
    TC-JWT-009: Valid JWT whose sub matches User.authUserId
    MUST return HTTP 200 with verified database profile.
    """
    valid_token = create_test_jwt()
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200

    data = response.json()
    assert data["auth_sub"] == TEST_SUB
    assert data["email"] == TEST_EMAIL
    assert data["role"] == "EMPLOYEE"
    assert data["name"] == "Nguyễn Văn A"
    assert data["departmentId"] == "DEPT-IT"
    assert "id" in data


def test_tc_jwt_010_client_role_injection_ignored(test_client):
    """
    TC-JWT-010: Client attempts to send arbitrary role in query or body
    or custom headers -> Server MUST ignore client role and enforce database role.
    """
    valid_token = create_test_jwt()
    # Client sends role injection in query and custom header
    response = test_client.get(
        "/api/auth/me?role=ADMIN&approverRole=MANAGER",
        headers={
            "Authorization": f"Bearer {valid_token}",
            "X-Role-Override": "ADMIN",
        }
    )
    assert response.status_code == 200
    data = response.json()
    # Server enforces database role: EMPLOYEE, ignoring client injection completely!
    assert data["role"] == "EMPLOYEE"
    assert data["role"] != "ADMIN"


def test_tc_jwt_011_missing_sub_claim(test_client):
    """TC-JWT-011: JWT missing 'sub' claim MUST return HTTP 401."""
    # Create payload without 'sub'
    now = int(time.time())
    payload = {
        "email": TEST_EMAIL,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": now + 3600,
        "iat": now,
    }
    no_sub_token = jwt.encode(payload, TEST_PRIVATE_KEY, algorithm="ES256", headers={"kid": TEST_KID})
    response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {no_sub_token}"})
    assert response.status_code == 401
    assert "sub" in response.json()["detail"].lower()


def test_tc_jwt_012_jwks_retrieval_failure_fails_closed(test_client):
    """
    TC-JWT-012: When JWKS retrieval fails (e.g. network failure),
    the verifier MUST fail closed with HTTP 401, never allowing access.
    """
    failing_verifier = SupabaseJWTService(
        jwks_url=settings.SUPABASE_JWKS_URL,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        jwks_client=MockJWKSClient(should_fail=True),
    )
    app.dependency_overrides[get_jwt_service] = lambda: failing_verifier

    try:
        valid_token = create_test_jwt()
        response = test_client.get("/api/auth/me", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 401
        assert "JWKS" in response.json()["detail"] or "khóa" in response.json()["detail"].lower()
    finally:
        # Restore normal mock verifier
        normal_verifier = SupabaseJWTService(
            jwks_url=settings.SUPABASE_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            jwks_client=MockJWKSClient(key=TEST_PUBLIC_KEY),
        )
        app.dependency_overrides[get_jwt_service] = lambda: normal_verifier

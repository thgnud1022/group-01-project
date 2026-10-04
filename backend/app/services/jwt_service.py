"""
Supabase Auth JWT Verification Service via JWKS & ES256
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-004 STEP 3B - JWT/JWKS Authentication Verification

Enforces:
- HD-02: Zero-Trust Client, server-side JWT verification.
- HD-12: Authentication Identity Binding via Supabase Auth User ID (sub).
- Algorithms locked strictly to ES256.
- Required claims: exp, iss, aud, sub.
"""

from typing import Dict, Any, Optional
import jwt
from jwt import PyJWKClient, PyJWKClientError
from jwt.exceptions import (
    PyJWTError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    MissingRequiredClaimError,
    DecodeError,
)
from app.config import settings


class JWTVerificationError(Exception):
    """Base exception for JWT verification failures."""
    pass


class SupabaseJWTService:
    """
    Production-grade JWT verification service for Supabase Auth.
    Fetches and caches public keys from Supabase JWKS endpoint.
    Verifies ECDSA (ES256) signatures and standard OIDC claims.
    """

    def __init__(
        self,
        jwks_url: Optional[str] = None,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
        jwks_client: Optional[PyJWKClient] = None,
    ):
        self.jwks_url = jwks_url or settings.SUPABASE_JWKS_URL
        self.issuer = issuer or settings.JWT_ISSUER
        self.audience = audience or settings.JWT_AUDIENCE
        self.algorithm = "ES256"
        self.timeout = 5.0

        if jwks_client:
            self._jwks_client = jwks_client
        else:
            self._jwks_client = PyJWKClient(
                self.jwks_url,
                cache_jwk_set=True,
                lifespan=3600,
                timeout=self.timeout,
            )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Supabase JWT token:
        1. Validates token format and structure.
        2. Validates header algorithm strictly matches ES256.
        3. Retrieves matching public key from JWKS by 'kid'.
        4. Verifies cryptographic signature using ES256.
        5. Validates standard claims: exp, iss, aud, sub.
        6. Ensures sub claim is non-empty.

        Returns decoded claims dictionary.
        Raises JWTVerificationError if verification fails.
        """
        if not token or not isinstance(token, str) or not token.strip():
            raise JWTVerificationError("Mã xác thực JWT rỗng hoặc không hợp lệ.")

        clean_token = token.strip()

        # 1. Inspect unverified header for algorithm and kid
        try:
            unverified_header = jwt.get_unverified_header(clean_token)
        except DecodeError as e:
            raise JWTVerificationError(f"Mã xác thực JWT không đúng định dạng: {str(e)}")
        except Exception as e:
            raise JWTVerificationError(f"Không thể đọc header của token: {str(e)}")

        alg = unverified_header.get("alg")
        if alg != self.algorithm:
            raise JWTVerificationError(
                f"Thuật toán ký không hợp lệ: '{alg}'. Hệ thống yêu cầu nghiêm ngặt '{self.algorithm}'."
            )

        kid = unverified_header.get("kid")
        if not kid:
            raise JWTVerificationError("Token thiếu trường 'kid' (Key ID) trong header.")

        # 2. Retrieve public key from JWKS (with cache refresh fallback on miss)
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(clean_token)
        except PyJWKClientError:
            try:
                self._jwks_client.get_signing_keys(refresh=True)
                signing_key = self._jwks_client.get_signing_key_from_jwt(clean_token)
            except PyJWKClientError as e:
                raise JWTVerificationError(f"Không thể lấy khóa công khai từ JWKS cho kid '{kid}': {str(e)}")
            except Exception as e:
                raise JWTVerificationError(f"Lỗi khi tra cứu khóa ký từ JWKS: {str(e)}")
        except Exception as e:
            raise JWTVerificationError(f"Lỗi khi tra cứu khóa ký từ JWKS: {str(e)}")

        # 3. Cryptographic Signature & Claim Verification
        try:
            claims = jwt.decode(
                clean_token,
                signing_key.key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "require": ["exp", "iss", "aud", "sub"],
                },
            )
        except ExpiredSignatureError:
            raise JWTVerificationError("Mã xác thực JWT đã hết hạn sử dụng (Token expired).")
        except InvalidAudienceError:
            raise JWTVerificationError(f"Audience không hợp lệ. Yêu cầu: '{self.audience}'.")
        except InvalidIssuerError:
            raise JWTVerificationError(f"Issuer không hợp lệ. Yêu cầu: '{self.issuer}'.")
        except InvalidSignatureError:
            raise JWTVerificationError("Chữ ký số JWT không hợp lệ hoặc nội dung token đã bị chỉnh sửa.")
        except MissingRequiredClaimError as e:
            raise JWTVerificationError(f"Token thiếu claim bắt buộc: {str(e)}")
        except DecodeError as e:
            raise JWTVerificationError(f"Không thể giải mã token: {str(e)}")
        except PyJWTError as e:
            raise JWTVerificationError(f"Lỗi xác thực JWT: {str(e)}")

        # 4. Strict check on subject (sub)
        sub = claims.get("sub")
        if not sub or not isinstance(sub, str) or not sub.strip():
            raise JWTVerificationError("Claim 'sub' (Subject/Auth User ID) không hợp lệ hoặc rỗng.")

        return claims


# Global default instance
jwt_service = SupabaseJWTService()

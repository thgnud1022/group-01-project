"""
FastAPI Authentication Dependency
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-004 STEP 3B - JWT/JWKS Authentication Verification

Enforces:
- HD-02: Zero-Trust Client, role & identity derived from server-side database.
- HD-12: Authentication Identity Binding via Supabase Auth User ID (sub -> User.authUserId).
- Fail-Closed: Rejects unauthenticated requests with HTTP 401.
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends, status
from pydantic import BaseModel
from app.services.jwt_service import SupabaseJWTService, jwt_service, JWTVerificationError
from app.services.db import get_prisma, connect_db


class AuthenticatedUser(BaseModel):
    """
    Verified Identity Object passed to protected routes and authorization guards.
    Strictly populated from database query, NEVER from client payload.
    """
    id: str
    auth_sub: str
    email: str
    name: str
    role: str
    departmentId: str


def get_jwt_service() -> SupabaseJWTService:
    """Dependency provider for JWT service (enables testing override)."""
    return jwt_service


async def get_current_identity(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    verifier: SupabaseJWTService = Depends(get_jwt_service),
) -> AuthenticatedUser:
    """
    FastAPI Dependency to verify Supabase JWT and resolve application identity:
    1. Reads Authorization header.
    2. Enforces 'Bearer <token>' format.
    3. Verifies token signature, exp, iss, aud, sub via Supabase JWT Service.
    4. Queries Application User in database by 'authUserId == sub'.
    5. Raises HTTP 401 if missing header, invalid token, or user unbound in DB.
    6. Returns AuthenticatedUser with database-verified role and department.
    """
    # 1. Check existence of Authorization header
    if not authorization or not authorization.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực. Vui lòng cung cấp Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Check header format
    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Định dạng Authorization header không hợp lệ. Chuẩn yêu cầu: Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_token = parts[1].strip()
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không được để trống.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Cryptographic & Claims Verification
    try:
        claims = verifier.verify_token(raw_token)
    except JWTVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Xác thực danh tính thất bại: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Extract verified sub claim
    auth_sub = claims.get("sub")
    if not auth_sub or not isinstance(auth_sub, str) or not auth_sub.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa Subject (sub) hợp lệ.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 5. Resolve Application User by authUserId (HD-12)
    await connect_db()
    prisma = get_prisma()

    user = await prisma.user.find_unique(where={"authUserId": auth_sub.strip()})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Không tìm thấy hồ sơ người dùng ứng dụng được liên kết với Auth User ID: '{auth_sub}'. Truy cập bị từ chối.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 6. Return database-resolved identity
    return AuthenticatedUser(
        id=user.id,
        auth_sub=auth_sub.strip(),
        email=user.email,
        name=user.name,
        role=str(user.role),
        departmentId=user.departmentId,
    )

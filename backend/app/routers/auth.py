from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.dependencies.auth import get_current_identity, AuthenticatedUser

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginSchema(BaseModel):
    email: str
    password: str

# ==============================================================================
# [LEGACY MOCK AUTH - TEST ONLY]
# NOTE: This dictionary and /login endpoint are strictly isolated for legacy
# local demo/test compatibility. They are NEVER used as a fallback for JWT
# verification. Production authentication is enforced exclusively by get_current_identity.
# Full deprecation is scheduled for TASK-011 (Frontend Supabase Auth integration).
# ==============================================================================
MOCK_USERS = {
    "employee@company.com": {"name": "Nguyễn Văn A", "role": "EMPLOYEE", "departmentId": "DEPT-IT"},
    "manager@company.com": {"name": "Trần Văn B", "role": "MANAGER", "departmentId": "DEPT-IT"},
    "procurement@company.com": {"name": "Lê Thị C", "role": "PROCUREMENT", "departmentId": "DEPT-IT"},
    "finance@company.com": {"name": "Phạm Văn D", "role": "FINANCE", "departmentId": "DEPT-IT"},
    "admin@company.com": {"name": "Quản Trị Viên", "role": "ADMIN", "departmentId": "DEPT-IT"}
}

@router.post("/login")
def login(payload: LoginSchema):
    """Legacy Mock Login. Returns mock token for test suites only."""
    user = MOCK_USERS.get(payload.email)
    if not user or payload.password != "password123":
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")
        
    return {
        "access_token": f"mock-jwt-token-for-{payload.email}",
        "token_type": "bearer",
        "user": {
            "email": payload.email,
            **user
        }
    }


@router.get("/me", response_model=AuthenticatedUser)
async def get_me(current_user: AuthenticatedUser = Depends(get_current_identity)):
    """
    Verified Identity Endpoint (TASK-004 / HD-02 / HD-12).
    Requires a valid Supabase JWT Bearer token signed with ES256.
    Extracts verified 'sub' claim, queries Application User by authUserId,
    and returns database-verified profile and role.
    """
    return current_user

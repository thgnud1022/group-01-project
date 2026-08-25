from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginSchema(BaseModel):
    email: str
    password: str

MOCK_USERS = {
    "employee@company.com": {"name": "Nguyễn Văn A", "role": "EMPLOYEE", "departmentId": "DEPT-IT"},
    "manager@company.com": {"name": "Trần Văn B", "role": "MANAGER", "departmentId": "DEPT-IT"},
    "procurement@company.com": {"name": "Lê Thị C", "role": "PROCUREMENT", "departmentId": "DEPT-IT"},
    "finance@company.com": {"name": "Phạm Văn D", "role": "FINANCE", "departmentId": "DEPT-IT"},
    "admin@company.com": {"name": "Quản Trị Viên", "role": "ADMIN", "departmentId": "DEPT-IT"}
}

@router.post("/login")
def login(payload: LoginSchema):
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

"""
Role-Based Access Control (RBAC) Dependency
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-005 - Server-Side RBAC Implementation

Enforces:
- HD-02: Zero-Trust Client, role resolved from server-side DB.
- HD-12: Identity binding via Supabase Auth User ID (sub -> User.authUserId).
- Role verification: Checks current_user.role in allowed_roles.
- 403 Forbidden on authorization failure.
- Contract: docs/TASK-005-RBAC-DESIGN.md Section J.3.
"""

from typing import List
from fastapi import HTTPException, Depends, status
from app.dependencies.auth import get_current_identity, AuthenticatedUser


class AuthorizationError(PermissionError, ValueError):
    """
    Raised when an authenticated user lacks required permissions or fails authorization policy.
    Inherits from PermissionError (maps to 403) and ValueError for backwards compatibility.
    """
    pass


class RoleChecker:
    """
    FastAPI dependency factory for role-based access control.

    Dependency chain:
        RoleChecker -> get_current_identity -> JWT verify (ES256/JWKS) -> DB User lookup

    Raises:
        HTTPException(403) if current_user.role is not in allowed_roles.
    """

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, current_user: AuthenticatedUser = Depends(get_current_identity)
    ) -> AuthenticatedUser:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Quyền truy cập bị từ chối: Thao tác yêu cầu vai trò {self.allowed_roles}. "
                    f"Vai trò hiện tại của bạn: {current_user.role}."
                ),
            )
        return current_user

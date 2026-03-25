"""
FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.security import decode_token, get_user, UserRole, User
from app.middleware import AuthenticationException, AuthorizationException

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> User:
    """
    Dependency to get the current authenticated user.
    Validates JWT token from Authorization header.
    """
    token = credentials.credentials
    
    token_data = decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )
    
    return User(**user.dict())

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role.
    Use this on routes that only admins can access.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this resource"
        )
    return current_user

async def require_editor(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require editor or admin role.
    Use this on routes that editors/admins can access.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors and administrators can access this resource"
        )
    return current_user

async def require_roles(*roles: UserRole):
    """
    Dependency factory to require specific roles.
    
    Usage:
        @app.get("/api/endpoint")
        async def endpoint(user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))):
            pass
    """
    async def check_roles(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This resource requires one of the following roles: {', '.join([r.value for r in roles])}"
            )
        return current_user
    
    return check_roles

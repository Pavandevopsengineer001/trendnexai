"""
Security and authentication module for TrendNexAI backend.
Handles JWT tokens, password hashing, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from enum import Enum

# Constants
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User roles
class UserRole(str, Enum):
    """User role enums for RBAC"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class TokenData(BaseModel):
    """JWT token payload data"""
    username: str
    role: UserRole
    exp: datetime

class User(BaseModel):
    """User model"""
    username: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True

class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(
    username: str,
    role: UserRole = UserRole.VIEWER,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = {"username": username, "role": role.value}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(username: str) -> str:
    """Create a JWT refresh token"""
    to_encode = {"username": username, "type": "refresh"}
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        role: str = payload.get("role", UserRole.VIEWER.value)
        
        if username is None:
            return None
        
        token_data = TokenData(
            username=username,
            role=UserRole(role),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
        return token_data
    except JWTError:
        return None

# Mock user database (replace with MongoDB query)
MOCK_USERS_DB = {
    os.getenv("ADMIN_USERNAME", "admin"): {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "hashed_password": get_password_hash(os.getenv("ADMIN_PASSWORD", "admin")),
        "role": UserRole.ADMIN,
        "is_active": True
    }
}

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password"""
    user = MOCK_USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return UserInDB(**user)

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    user = MOCK_USERS_DB.get(username)
    if user:
        return UserInDB(**user)
    return None

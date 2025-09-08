"""Authentication and authorization module"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from src.backend.models import UserDB, ApiKeyDB


# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-memory storage (replace with database in production)
users_db: Dict[str, UserDB] = {}
api_keys_db: Dict[str, ApiKeyDB] = {}
refresh_tokens_db: Dict[str, Dict[str, Any]] = {}
rate_limit_db: Dict[str, list] = {}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets complexity requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Store refresh token
    user_email = data.get("sub")
    if user_email:
        if user_email not in refresh_tokens_db:
            refresh_tokens_db[user_email] = {}
        refresh_tokens_db[user_email][encoded_jwt] = {"created_at": datetime.utcnow(), "expires_at": expire}

    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_user_by_email(email: str) -> Optional[UserDB]:
    """Get user by email from database"""
    return users_db.get(email)


def get_user_by_id(user_id: str) -> Optional[UserDB]:
    """Get user by ID from database"""
    for user in users_db.values():
        if user.id == user_id:
            return user
    return None


def create_user(email: str, password: str, full_name: str) -> UserDB:
    """Create a new user"""
    # Check if user exists
    if get_user_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    # Validate password
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)

    # Create user
    user = UserDB(email=email, password_hash=hash_password(password), full_name=full_name)

    users_db[email] = user
    return user


def authenticate_user(email: str, password: str) -> Optional[UserDB]:
    """Authenticate a user"""
    user = get_user_by_email(email)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> UserDB:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[UserDB]:
    """Get current user from JWT token or API key (optional).

    This function is for endpoints that support optional authentication.
    For required authentication, use get_current_user directly.

    Returns:
        UserDB if authenticated, None if no valid credentials provided.

    Note:
        This intentionally returns None instead of raising exceptions
        to support endpoints with optional authentication.
    """
    # Try JWT token first (preferred method)
    if credentials and credentials.credentials:
        try:
            return get_current_user(credentials)
        except HTTPException:
            # Invalid JWT, but might have valid API key
            pass

    # Try API key as fallback
    if api_key:
        user = get_user_by_api_key(api_key)
        if user:
            return user

    # No valid authentication provided - this is acceptable for optional auth
    return None


def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
) -> UserDB:
    """Require authentication via JWT or API key.

    This function requires valid authentication and raises HTTPException if not provided.

    Raises:
        HTTPException: 401 if no valid authentication is provided.
    """
    user = get_current_user_optional(credentials, api_key)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def create_api_key(user_id: str, name: str, expires_at: Optional[datetime] = None) -> tuple[str, ApiKeyDB]:
    """Create an API key for a user"""
    # Generate API key
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Create API key record
    api_key_db = ApiKeyDB(user_id=user_id, name=name, key_hash=key_hash, expires_at=expires_at)

    api_keys_db[key] = api_key_db

    return key, api_key_db


def get_user_by_api_key(api_key: str) -> Optional[UserDB]:
    """Get user by API key"""
    api_key_db = api_keys_db.get(api_key)
    if not api_key_db:
        return None

    # Check expiration
    if api_key_db.expires_at and api_key_db.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has expired")

    # Update last used
    api_key_db.last_used = datetime.utcnow()

    return get_user_by_id(api_key_db.user_id)


def revoke_refresh_token(user_email: str, token: str) -> bool:
    """Revoke a refresh token"""
    if user_email in refresh_tokens_db:
        if token in refresh_tokens_db[user_email]:
            del refresh_tokens_db[user_email][token]
            return True
    return False


def revoke_all_refresh_tokens(user_email: str) -> bool:
    """Revoke all refresh tokens for a user"""
    if user_email in refresh_tokens_db:
        refresh_tokens_db[user_email] = {}
        return True
    return False


def check_rate_limit(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """Check if rate limit has been exceeded"""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    if identifier not in rate_limit_db:
        rate_limit_db[identifier] = []

    # Clean old attempts
    rate_limit_db[identifier] = [attempt for attempt in rate_limit_db[identifier] if attempt > window_start]

    # Check limit
    if len(rate_limit_db[identifier]) >= max_attempts:
        return False

    # Record attempt
    rate_limit_db[identifier].append(now)
    return True


def delete_user(user_id: str) -> bool:
    """Delete a user and all associated data"""
    user = get_user_by_id(user_id)
    if not user:
        return False

    # Delete user
    del users_db[user.email]

    # Delete refresh tokens
    revoke_all_refresh_tokens(user.email)

    # Delete API keys
    keys_to_delete = []
    for key, api_key_db in api_keys_db.items():
        if api_key_db.user_id == user_id:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del api_keys_db[key]

    return True

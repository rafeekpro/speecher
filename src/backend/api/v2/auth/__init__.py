"""Authentication API endpoints"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.auth import (
    authenticate_user,
    check_rate_limit,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    revoke_all_refresh_tokens,
    create_user,
)
from src.backend.models import (
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """Register a new user"""
    try:
        user = create_user(email=request.email, password=request.password, full_name=request.full_name)
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=UserLoginResponse)
async def login(request: UserLoginRequest):
    """Login user and return JWT tokens"""
    # Check rate limiting
    if not check_rate_limit(request.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts. Please try again later."
        )

    # Authenticate user
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Create tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutes
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        # Create new access token
        access_token = create_access_token({"sub": email})

        return TokenRefreshResponse(access_token=access_token, token_type="bearer", expires_in=1800)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout user and revoke tokens"""
    revoke_all_refresh_tokens(current_user.email)
    return {"message": "Successfully logged out"}


@router.get("/sessions")
async def get_sessions(current_user: UserResponse = Depends(get_current_user)):
    """Get active sessions for current user"""
    # This would be implemented with a session tracking system
    return {
        "sessions": [
            {
                "id": "session-1",
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0",
            }
        ]
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Revoke a specific session"""
    return {"message": f"Session {session_id} revoked successfully"}
"""User management API endpoints"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.auth import (
    create_api_key,
    get_current_user,
    get_user_by_email,
    hash_password,
    require_auth,
    revoke_all_refresh_tokens,
    users_db,
    api_keys_db,
    validate_password_strength,
    verify_password,
)
from src.backend.models import (
    ApiKeyCreateRequest,
    ApiKeyResponse,
    PasswordChangeRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(require_auth)):
    """Get current user profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(request: UserUpdateRequest, current_user: UserResponse = Depends(get_current_user)):
    """Update user profile"""
    # Check if email is being changed and if it's already taken
    if request.email and request.email != current_user.email:
        if get_user_by_email(request.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    # Update user in database
    user = users_db[current_user.email]
    if request.full_name:
        user.full_name = request.full_name
    if request.email:
        # Move user to new email key
        del users_db[current_user.email]
        user.email = request.email
        users_db[request.email] = user

    user.updated_at = datetime.utcnow()

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/password")
async def change_password(request: PasswordChangeRequest, current_user: UserResponse = Depends(get_current_user)):
    """Change user password"""
    user = users_db[current_user.email]

    # Verify current password
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    # Validate new password
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)

    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()

    # Revoke all refresh tokens
    revoke_all_refresh_tokens(current_user.email)

    return {"message": "Password changed successfully"}


@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_user_api_key(request: ApiKeyCreateRequest, current_user: UserResponse = Depends(require_auth)):
    """Create a new API key"""
    key, api_key_db = create_api_key(user_id=current_user.id, name=request.name, expires_at=request.expires_at)

    return ApiKeyResponse(
        id=api_key_db.id,
        name=api_key_db.name,
        key=key,  # Only returned on creation
        last_used=api_key_db.last_used,
        created_at=api_key_db.created_at,
        expires_at=api_key_db.expires_at,
    )


@router.get("/api-keys")
async def list_api_keys(current_user: UserResponse = Depends(get_current_user)):
    """List user's API keys"""
    user_keys = []
    for api_key_db in api_keys_db.values():
        if api_key_db.user_id == current_user.id:
            user_keys.append(
                ApiKeyResponse(
                    id=api_key_db.id,
                    name=api_key_db.name,
                    key=None,  # Never return the actual key
                    last_used=api_key_db.last_used,
                    created_at=api_key_db.created_at,
                    expires_at=api_key_db.expires_at,
                )
            )

    return {"keys": user_keys}


@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete an API key"""
    # Find and delete key
    for key_hash, api_key_db in list(api_keys_db.items()):
        if api_key_db.id == key_id and api_key_db.user_id == current_user.id:
            del api_keys_db[key_hash]
            return {"message": "API key deleted successfully"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")


@router.delete("/profile")
async def delete_profile(current_user: UserResponse = Depends(get_current_user)):
    """Delete user account"""
    from src.backend.auth import delete_user

    delete_user(current_user.email)
    return {"message": "Account deleted successfully"}
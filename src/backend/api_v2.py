"""API v2 endpoints for user management and projects"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from typing import Optional, List
from datetime import datetime

from src.backend.models import (
    UserRegisterRequest, UserLoginRequest, UserLoginResponse,
    TokenRefreshRequest, TokenRefreshResponse,
    UserResponse, UserUpdateRequest, PasswordChangeRequest,
    ApiKeyCreateRequest, ApiKeyResponse,
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, ProjectListResponse,
    RecordingCreateRequest, RecordingResponse, RecordingListResponse,
    TagResponse, ErrorResponse
)
from src.backend.auth import (
    create_user, authenticate_user, create_access_token, create_refresh_token,
    decode_token, get_current_user, check_rate_limit, delete_user,
    create_api_key, verify_password, hash_password, validate_password_strength,
    revoke_all_refresh_tokens
)
from src.backend.database import (
    projects_db, recordings_db, tags_db,
    get_project_by_id, get_user_projects, create_project, update_project, delete_project,
    get_project_recordings, add_recording_to_project,
    get_project_tags, add_tags_to_project, remove_tags_from_project
)

# Create routers
auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])
users_router = APIRouter(prefix="/api/users", tags=["users"])
projects_router = APIRouter(prefix="/api/projects", tags=["projects"])

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """Register a new user"""
    try:
        user = create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@auth_router.post("/login", response_model=UserLoginResponse)
async def login(request: UserLoginRequest):
    """Login user and return JWT tokens"""
    # Check rate limiting
    if not check_rate_limit(request.email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Authenticate user
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
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
            updated_at=user.updated_at
        )
    )


@auth_router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Create new access token
        access_token = create_access_token({"sub": email})
        
        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@auth_router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout user and revoke tokens"""
    revoke_all_refresh_tokens(current_user.email)
    return {"message": "Successfully logged out"}


@auth_router.get("/sessions")
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
                "user_agent": "Mozilla/5.0"
            }
        ]
    }


@auth_router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Revoke a specific session"""
    return {"message": f"Session {session_id} revoked successfully"}


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@users_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@users_router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserUpdateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user profile"""
    from src.backend.auth import users_db, get_user_by_email
    
    # Check if email is being changed and if it's already taken
    if request.email and request.email != current_user.email:
        if get_user_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
    
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
        updated_at=user.updated_at
    )


@users_router.put("/password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Change user password"""
    from src.backend.auth import users_db
    
    user = users_db[current_user.email]
    
    # Verify current password
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.utcnow()
    
    # Revoke all refresh tokens
    revoke_all_refresh_tokens(current_user.email)
    
    return {"message": "Password changed successfully"}


@users_router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_user_api_key(
    request: ApiKeyCreateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new API key"""
    key, api_key_db = create_api_key(
        user_id=current_user.id,
        name=request.name,
        expires_at=request.expires_at
    )
    
    return ApiKeyResponse(
        id=api_key_db.id,
        name=api_key_db.name,
        key=key,  # Only returned on creation
        last_used=api_key_db.last_used,
        created_at=api_key_db.created_at,
        expires_at=api_key_db.expires_at
    )


@users_router.get("/api-keys")
async def list_api_keys(current_user: UserResponse = Depends(get_current_user)):
    """List user's API keys"""
    from src.backend.auth import api_keys_db
    
    user_keys = []
    for api_key_db in api_keys_db.values():
        if api_key_db.user_id == current_user.id:
            user_keys.append(ApiKeyResponse(
                id=api_key_db.id,
                name=api_key_db.name,
                key=None,  # Never return the actual key
                last_used=api_key_db.last_used,
                created_at=api_key_db.created_at,
                expires_at=api_key_db.expires_at
            ))
    
    return {"keys": user_keys}


@users_router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete an API key"""
    from src.backend.auth import api_keys_db
    
    # Find and delete key
    key_to_delete = None
    for key, api_key_db in api_keys_db.items():
        if api_key_db.id == key_id and api_key_db.user_id == current_user.id:
            key_to_delete = key
            break
    
    if not key_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    del api_keys_db[key_to_delete]
    return {"message": "API key deleted successfully"}


@users_router.delete("/account")
async def delete_account(
    password: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete user account"""
    from src.backend.auth import users_db
    
    user = users_db[current_user.email]
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect"
        )
    
    # Delete user and all associated data
    if delete_user(current_user.id):
        return {"message": "Account deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


@users_router.get("/activity")
async def get_activity_log(current_user: UserResponse = Depends(get_current_user)):
    """Get user activity log"""
    # This would be implemented with an activity tracking system
    return {
        "activities": [
            {
                "timestamp": datetime.utcnow(),
                "action": "login",
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0"
            }
        ]
    }


# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@projects_router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    request: ProjectCreateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new project"""
    project = create_project(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        tags=request.tags
    )
    
    return project


@projects_router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tag: Optional[List[str]] = Query(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """List user's projects"""
    projects = get_user_projects(current_user.id, search=search, tags=tag)
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_projects = projects[start:end]
    
    return ProjectListResponse(
        projects=paginated_projects,
        total=len(projects),
        page=page,
        per_page=per_page
    )


@projects_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get project details"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return project


@projects_router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update project"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    updated_project = update_project(project_id, request)
    return updated_project


@projects_router.delete("/{project_id}")
async def delete_existing_project(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete project"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    delete_project(project_id)
    return {"message": "Project deleted successfully"}


@projects_router.get("/{project_id}/recordings", response_model=RecordingListResponse)
async def get_recordings(
    project_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get project recordings"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    recordings = get_project_recordings(project_id)
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_recordings = recordings[start:end]
    
    return RecordingListResponse(
        recordings=paginated_recordings,
        total=len(recordings),
        page=page,
        per_page=per_page
    )


@projects_router.post("/{project_id}/recordings", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def add_recording(
    project_id: str,
    request: RecordingCreateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add recording to project"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    recording = add_recording_to_project(
        project_id=project_id,
        user_id=current_user.id,
        filename=request.filename,
        duration=request.duration,
        file_size=request.file_size
    )
    
    return recording


@projects_router.get("/{project_id}/tags")
async def get_tags(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get project tags"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    tags = get_project_tags(project_id)
    return {"tags": tags}


@projects_router.post("/{project_id}/tags")
async def add_tags(
    project_id: str,
    tags: List[str],
    current_user: UserResponse = Depends(get_current_user)
):
    """Add tags to project"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    updated_tags = add_tags_to_project(project_id, tags)
    return {"tags": updated_tags}


@projects_router.delete("/{project_id}/tags")
async def remove_tags(
    project_id: str,
    tags: List[str],
    current_user: UserResponse = Depends(get_current_user)
):
    """Remove tags from project"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    updated_tags = remove_tags_from_project(project_id, tags)
    return {"tags": updated_tags}


@projects_router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get project statistics"""
    project = get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    recordings = get_project_recordings(project_id)
    
    total_duration = sum(r.duration or 0 for r in recordings)
    total_size = sum(r.file_size or 0 for r in recordings)
    
    return {
        "total_recordings": len(recordings),
        "total_duration": total_duration,
        "total_size": total_size,
        "average_duration": total_duration / len(recordings) if recordings else 0
    }
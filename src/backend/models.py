"""Database models for Frontend 2.0"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Enums
class UserRole(str, Enum):
    """User role enumeration"""

    USER = "user"
    ADMIN = "admin"


class ProjectStatus(str, Enum):
    """Project status enumeration"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


# Request/Response Models
class UserRegisterRequest(BaseModel):
    """User registration request model"""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLoginRequest(BaseModel):
    """User login request model"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model"""

    id: str
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponse(BaseModel):
    """User login response model"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""

    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class UserUpdateRequest(BaseModel):
    """User profile update request"""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class PasswordChangeRequest(BaseModel):
    """Password change request"""

    current_password: str
    new_password: str = Field(..., min_length=8)


class ApiKeyCreateRequest(BaseModel):
    """API key creation request"""

    name: str = Field(..., min_length=1, max_length=255)
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    """API key response model"""

    id: str
    name: str
    key: Optional[str] = None  # Only returned on creation
    last_used: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ProjectCreateRequest(BaseModel):
    """Project creation request"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ProjectUpdateRequest(BaseModel):
    """Project update request"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    """Project response model"""

    id: str
    user_id: str
    name: str
    description: Optional[str]
    status: ProjectStatus
    tags: List[str]
    recording_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Project list response"""

    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int


class RecordingCreateRequest(BaseModel):
    """Recording creation request"""

    filename: str
    duration: Optional[float] = None
    file_size: Optional[int] = None


class RecordingResponse(BaseModel):
    """Recording response model"""

    id: str
    project_id: str
    user_id: str
    filename: str
    duration: Optional[float]
    file_size: Optional[int]
    status: str
    transcription: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecordingListResponse(BaseModel):
    """Recording list response"""

    recordings: List[RecordingResponse]
    total: int
    page: int
    per_page: int


class TagsRequest(BaseModel):
    """Request model for adding/removing tags"""

    tags: List[str]


class TagResponse(BaseModel):
    """Tag response model"""

    id: str
    name: str
    color: Optional[str]
    usage_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str
    message: str
    details: Optional[dict] = None


# Database Models (SQLAlchemy would be used in production)
class UserDB(BaseModel):
    """User database model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    password_hash: str
    full_name: str
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectDB(BaseModel):
    """Project database model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKeyDB(BaseModel):
    """API key database model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    name: str
    key_hash: str
    last_used: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class RecordingDB(BaseModel):
    """Recording database model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    user_id: str
    filename: str
    duration: Optional[float] = None
    file_size: Optional[int] = None
    status: str = "pending"
    transcription: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TagDB(BaseModel):
    """Tag database model"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

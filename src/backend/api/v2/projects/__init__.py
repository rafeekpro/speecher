"""Project management API endpoints"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.backend.auth import get_current_user
from src.backend.database import (
    add_recording_to_project,
    add_tags_to_project,
    create_project,
    delete_project,
    get_project_by_id,
    get_project_recordings,
    get_project_tags,
    get_user_projects,
    remove_tags_from_project,
    update_project,
)
from src.backend.models import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    RecordingCreateRequest,
    RecordingListResponse,
    RecordingResponse,
    TagsRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(request: ProjectCreateRequest, current_user: UserResponse = Depends(get_current_user)):
    """Create a new project"""
    project = create_project(
        user_id=current_user.id, name=request.name, description=request.description, tags=request.tags
    )

    return project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tag: Optional[List[str]] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """List user's projects"""
    projects = get_user_projects(current_user.id, search=search, tags=tag)

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_projects = projects[start:end]

    return ProjectListResponse(projects=paginated_projects, total=len(projects), page=page, per_page=per_page)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get project details"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: str, request: ProjectUpdateRequest, current_user: UserResponse = Depends(get_current_user)
):
    """Update project"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updated_project = update_project(project_id, request)
    return updated_project


@router.delete("/{project_id}")
async def delete_existing_project(project_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete project"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    delete_project(project_id)
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/recordings", response_model=RecordingListResponse)
async def get_recordings(
    project_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
):
    """Get project recordings"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    recordings = get_project_recordings(project_id)

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_recordings = recordings[start:end]

    return RecordingListResponse(recordings=paginated_recordings, total=len(recordings), page=page, per_page=per_page)


@router.post("/{project_id}/recordings", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def add_recording(
    project_id: str, request: RecordingCreateRequest, current_user: UserResponse = Depends(get_current_user)
):
    """Add recording to project"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    recording = add_recording_to_project(
        project_id=project_id, title=request.title, file_path=request.file_path, duration=request.duration
    )

    return recording


@router.get("/{project_id}/tags")
async def get_tags(project_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get project tags"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    tags = get_project_tags(project_id)
    return {"tags": tags}


@router.post("/{project_id}/tags")
async def add_tags(project_id: str, request: TagsRequest, current_user: UserResponse = Depends(get_current_user)):
    """Add tags to project"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    add_tags_to_project(project_id, request.tags)
    return {"message": "Tags added successfully"}


@router.delete("/{project_id}/tags")
async def remove_tags(project_id: str, request: TagsRequest, current_user: UserResponse = Depends(get_current_user)):
    """Remove tags from project"""
    project = get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check ownership
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    remove_tags_from_project(project_id, request.tags)
    return {"message": "Tags removed successfully"}
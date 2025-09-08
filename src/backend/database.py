"""Database operations for projects and recordings"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from src.backend.models import (
    ProjectDB,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdateRequest,
    RecordingDB,
    RecordingResponse,
)

# In-memory storage (replace with real database in production)
projects_db: Dict[str, ProjectDB] = {}
recordings_db: Dict[str, RecordingDB] = {}
tags_db: Dict[str, List[str]] = {}  # project_id -> list of tags


def create_project(
    user_id: str, name: str, description: Optional[str] = None, tags: List[str] = None
) -> ProjectResponse:
    """Create a new project"""
    project = ProjectDB(
        id=str(uuid4()), user_id=user_id, name=name, description=description, status=ProjectStatus.ACTIVE
    )

    projects_db[project.id] = project

    # Add tags
    if tags:
        tags_db[project.id] = tags
    else:
        tags_db[project.id] = []

    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        status=project.status,
        tags=tags_db[project.id],
        recording_count=0,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def get_project_by_id(project_id: str) -> Optional[ProjectResponse]:
    """Get project by ID"""
    project = projects_db.get(project_id)
    if not project:
        return None

    # Count recordings
    recording_count = sum(1 for r in recordings_db.values() if r.project_id == project_id)

    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        status=project.status,
        tags=tags_db.get(project.id, []),
        recording_count=recording_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def get_user_projects(
    user_id: str, search: Optional[str] = None, tags: Optional[List[str]] = None
) -> List[ProjectResponse]:
    """Get all projects for a user"""
    user_projects = []

    for project in projects_db.values():
        if project.user_id != user_id:
            continue

        # Filter by search term
        if search:
            search_lower = search.lower()
            if search_lower not in project.name.lower():
                if not project.description or search_lower not in project.description.lower():
                    continue

        # Filter by tags
        project_tags = tags_db.get(project.id, [])
        if tags:
            if not any(tag in project_tags for tag in tags):
                continue

        # Count recordings
        recording_count = sum(1 for r in recordings_db.values() if r.project_id == project.id)

        user_projects.append(
            ProjectResponse(
                id=project.id,
                user_id=project.user_id,
                name=project.name,
                description=project.description,
                status=project.status,
                tags=project_tags,
                recording_count=recording_count,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )

    # Sort by created_at descending
    user_projects.sort(key=lambda x: x.created_at, reverse=True)

    return user_projects


def update_project(project_id: str, update_data: ProjectUpdateRequest) -> ProjectResponse:
    """Update a project"""
    project = projects_db.get(project_id)
    if not project:
        return None

    # Update fields
    if update_data.name is not None:
        project.name = update_data.name

    if update_data.description is not None:
        project.description = update_data.description

    if update_data.status is not None:
        project.status = update_data.status

    if update_data.tags is not None:
        tags_db[project.id] = update_data.tags

    project.updated_at = datetime.utcnow()

    # Count recordings
    recording_count = sum(1 for r in recordings_db.values() if r.project_id == project_id)

    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        status=project.status,
        tags=tags_db.get(project.id, []),
        recording_count=recording_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def delete_project(project_id: str) -> bool:
    """Delete a project"""
    if project_id not in projects_db:
        return False

    # Delete project
    del projects_db[project_id]

    # Delete tags
    if project_id in tags_db:
        del tags_db[project_id]

    # Delete associated recordings
    recordings_to_delete = [rid for rid, rec in recordings_db.items() if rec.project_id == project_id]
    for rid in recordings_to_delete:
        del recordings_db[rid]

    return True


def add_recording_to_project(
    project_id: str, user_id: str, filename: str, duration: Optional[float] = None, file_size: Optional[int] = None
) -> RecordingResponse:
    """Add a recording to a project"""
    recording = RecordingDB(
        id=str(uuid4()),
        project_id=project_id,
        user_id=user_id,
        filename=filename,
        duration=duration,
        file_size=file_size,
        status="pending",
    )

    recordings_db[recording.id] = recording

    return RecordingResponse(
        id=recording.id,
        project_id=recording.project_id,
        user_id=recording.user_id,
        filename=recording.filename,
        duration=recording.duration,
        file_size=recording.file_size,
        status=recording.status,
        transcription=recording.transcription,
        created_at=recording.created_at,
        updated_at=recording.updated_at,
    )


def get_project_recordings(project_id: str) -> List[RecordingResponse]:
    """Get all recordings for a project"""
    project_recordings = []

    for recording in recordings_db.values():
        if recording.project_id == project_id:
            project_recordings.append(
                RecordingResponse(
                    id=recording.id,
                    project_id=recording.project_id,
                    user_id=recording.user_id,
                    filename=recording.filename,
                    duration=recording.duration,
                    file_size=recording.file_size,
                    status=recording.status,
                    transcription=recording.transcription,
                    created_at=recording.created_at,
                    updated_at=recording.updated_at,
                )
            )

    # Sort by created_at descending
    project_recordings.sort(key=lambda x: x.created_at, reverse=True)

    return project_recordings


def get_project_tags(project_id: str) -> List[str]:
    """Get tags for a project"""
    return tags_db.get(project_id, [])


def add_tags_to_project(project_id: str, new_tags: List[str]) -> List[str]:
    """Add tags to a project"""
    if project_id not in tags_db:
        tags_db[project_id] = []

    current_tags = set(tags_db[project_id])
    current_tags.update(new_tags)
    tags_db[project_id] = list(current_tags)

    # Update project updated_at
    if project_id in projects_db:
        projects_db[project_id].updated_at = datetime.utcnow()

    return tags_db[project_id]


def remove_tags_from_project(project_id: str, tags_to_remove: List[str]) -> List[str]:
    """Remove tags from a project"""
    if project_id not in tags_db:
        return []

    current_tags = set(tags_db[project_id])
    for tag in tags_to_remove:
        current_tags.discard(tag)

    tags_db[project_id] = list(current_tags)

    # Update project updated_at
    if project_id in projects_db:
        projects_db[project_id].updated_at = datetime.utcnow()

    return tags_db[project_id]

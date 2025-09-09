"""API v2 main router that combines all sub-routers"""

from fastapi import APIRouter

from src.backend.api.v2.auth import router as auth_router
from src.backend.api.v2.users import router as users_router
from src.backend.api.v2.projects import router as projects_router

# Create main v2 router
api_v2_router = APIRouter()

# Include all sub-routers
api_v2_router.include_router(auth_router)
api_v2_router.include_router(users_router)
api_v2_router.include_router(projects_router)
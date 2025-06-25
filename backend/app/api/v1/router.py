"""
Main API router for version 1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, projects, contracts, comments, ai_suggestions, versions, presence, analytics

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Resource routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(ai_suggestions.router, prefix="/ai-suggestions", tags=["ai-suggestions"])
api_router.include_router(versions.router, prefix="/versions", tags=["versions"])
api_router.include_router(presence.router, prefix="/presence", tags=["presence"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
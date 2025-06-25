"""
Project management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectListResponse, ProjectWithContracts
)
from app.services.project_service import ProjectService

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    project_service = ProjectService(db)
    return await project_service.create_project(project_data, current_user.id)

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    public_only: bool = Query(False),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of projects"""
    project_service = ProjectService(db)
    
    if public_only:
        projects = await project_service.get_public_projects(skip=skip, limit=limit)
        total = await project_service.get_public_project_count()
    else:
        projects = await project_service.get_projects_by_owner(
            current_user.id, skip=skip, limit=limit
        )
        total = await project_service.get_project_count_by_owner(current_user.id)
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=(skip // limit) + 1,
        size=len(projects),
        has_next=(skip + limit) < total
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project by ID"""
    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access permissions
    if not project.is_public and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    project_service = ProjectService(db)
    updated_project = await project_service.update_project(
        project_id, project_data, current_user.id
    )
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return updated_project

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete project"""
    project_service = ProjectService(db)
    success = await project_service.delete_project(project_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive project"""
    project_service = ProjectService(db)
    archived_project = await project_service.archive_project(project_id, current_user.id)
    
    if not archived_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return archived_project
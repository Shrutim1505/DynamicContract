"""
Project service for business logic
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.user import UserResponse

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, project_data: ProjectCreate, owner_id: int) -> ProjectResponse:
        """Create a new project"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=owner_id,
            is_public=project_data.is_public,
            is_template=project_data.is_template,
            color=project_data.color,
            client_name=project_data.client_name,
            project_status=project_data.project_status,
            tags=project_data.tags
        )
        
        self.db.add(db_project)
        await self.db.commit()
        await self.db.refresh(db_project)
        
        # Load owner relationship
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.owner))
            .where(Project.id == db_project.id)
        )
        project_with_owner = result.scalar_one()
        
        response = ProjectResponse.model_validate(project_with_owner)
        if project_with_owner.owner:
            response.owner = UserResponse.model_validate(project_with_owner.owner)
        
        return response

    async def get_project_by_id(self, project_id: int) -> Optional[ProjectResponse]:
        """Get project by ID with owner information"""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.owner))
            .where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
            
        response = ProjectResponse.model_validate(project)
        if project.owner:
            response.owner = UserResponse.model_validate(project.owner)
        
        # Add contract count
        contract_count_result = await self.db.execute(
            select(func.count())
            .select_from(project.contracts.property.mapper.class_)
            .where(project.contracts.property.mapper.class_.project_id == project_id)
        )
        response.contract_count = contract_count_result.scalar() or 0
        
        return response

    async def get_projects_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        """Get projects owned by user"""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.owner))
            .where(Project.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .order_by(Project.updated_at.desc().nulls_last(), Project.created_at.desc())
        )
        projects = result.scalars().all()
        
        responses = []
        for project in projects:
            response = ProjectResponse.model_validate(project)
            if project.owner:
                response.owner = UserResponse.model_validate(project.owner)
            responses.append(response)
        
        return responses

    async def get_public_projects(self, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        """Get public projects"""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.owner))
            .where(Project.is_public == True)
            .offset(skip)
            .limit(limit)
            .order_by(Project.updated_at.desc().nulls_last(), Project.created_at.desc())
        )
        projects = result.scalars().all()
        
        responses = []
        for project in projects:
            response = ProjectResponse.model_validate(project)
            if project.owner:
                response.owner = UserResponse.model_validate(project.owner)
            responses.append(response)
        
        return responses

    async def update_project(self, project_id: int, project_data: ProjectUpdate, user_id: int) -> Optional[ProjectResponse]:
        """Update project (only owner can update)"""
        # Check if user owns the project
        project = await self.get_project_by_id(project_id)
        if not project or project.owner_id != user_id:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        if not update_data:
            return project

        await self.db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(**update_data, updated_at=func.now())
        )
        await self.db.commit()
        
        return await self.get_project_by_id(project_id)

    async def delete_project(self, project_id: int, user_id: int) -> bool:
        """Delete project (only owner can delete)"""
        # Check if user owns the project
        project = await self.get_project_by_id(project_id)
        if not project or project.owner_id != user_id:
            return False

        await self.db.execute(delete(Project).where(Project.id == project_id))
        await self.db.commit()
        return True

    async def archive_project(self, project_id: int, user_id: int) -> Optional[ProjectResponse]:
        """Archive project"""
        project = await self.get_project_by_id(project_id)
        if not project or project.owner_id != user_id:
            return None

        await self.db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(
                project_status="archived",
                archived_at=func.now(),
                updated_at=func.now()
            )
        )
        await self.db.commit()
        
        return await self.get_project_by_id(project_id)

    async def get_project_count_by_owner(self, owner_id: int) -> int:
        """Get total project count for owner"""
        result = await self.db.execute(
            select(func.count(Project.id)).where(Project.owner_id == owner_id)
        )
        return result.scalar() or 0
"""
Contract service for business logic
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.contract import Contract
from app.models.project import Project
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractUpdate, ContractResponse, ContractAnalytics
from app.schemas.user import UserResponse

class ContractService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contract(self, contract_data: ContractCreate, user_id: int) -> ContractResponse:
        """Create a new contract"""
        # Verify user has access to the project
        project_result = await self.db.execute(
            select(Project).where(Project.id == contract_data.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise ValueError("Project not found")
        
        if project.owner_id != user_id and not project.is_public:
            raise ValueError("Access denied to project")

        db_contract = Contract(
            title=contract_data.title,
            content=contract_data.content,
            project_id=contract_data.project_id,
            created_by_id=user_id,
            version=contract_data.version,
            contract_type=contract_data.contract_type,
            priority=contract_data.priority,
            language=contract_data.language,
            jurisdiction=contract_data.jurisdiction,
            word_count=len(contract_data.content.split())
        )
        
        self.db.add(db_contract)
        await self.db.commit()
        await self.db.refresh(db_contract)
        
        return await self.get_contract_by_id(db_contract.id)

    async def get_contract_by_id(self, contract_id: int) -> Optional[ContractResponse]:
        """Get contract by ID with relationships"""
        result = await self.db.execute(
            select(Contract)
            .options(
                selectinload(Contract.created_by),
                selectinload(Contract.project)
            )
            .where(Contract.id == contract_id)
        )
        contract = result.scalar_one_or_none()
        
        if not contract:
            return None
            
        response = ContractResponse.model_validate(contract)
        
        # Add creator information
        if contract.created_by:
            response.created_by = UserResponse.model_validate(contract.created_by)
        
        # Add analytics data
        analytics = ContractAnalytics(
            word_count=contract.word_count,
            reading_level=contract.reading_level,
            risk_score=contract.risk_score,
            completeness_score=contract.completeness_score,
            identified_risks=contract.identified_risks,
            missing_clauses=contract.missing_clauses,
            compliance_issues=contract.compliance_issues
        )
        response.analytics = analytics
        
        # Get comment and suggestion counts
        comment_count_result = await self.db.execute(
            select(func.count()).select_from(contract.comments.property.mapper.class_)
            .where(contract.comments.property.mapper.class_.contract_id == contract_id)
        )
        response.comment_count = comment_count_result.scalar() or 0
        
        suggestion_count_result = await self.db.execute(
            select(func.count()).select_from(contract.ai_suggestions.property.mapper.class_)
            .where(contract.ai_suggestions.property.mapper.class_.contract_id == contract_id)
        )
        response.suggestion_count = suggestion_count_result.scalar() or 0
        
        return response

    async def get_contracts_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> List[ContractResponse]:
        """Get contracts by project"""
        result = await self.db.execute(
            select(Contract)
            .options(selectinload(Contract.created_by))
            .where(Contract.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .order_by(Contract.updated_at.desc().nulls_last(), Contract.created_at.desc())
        )
        contracts = result.scalars().all()
        
        responses = []
        for contract in contracts:
            response = ContractResponse.model_validate(contract)
            if contract.created_by:
                response.created_by = UserResponse.model_validate(contract.created_by)
            responses.append(response)
        
        return responses

    async def get_contracts_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ContractResponse]:
        """Get contracts created by user"""
        result = await self.db.execute(
            select(Contract)
            .options(selectinload(Contract.created_by))
            .where(Contract.created_by_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Contract.updated_at.desc().nulls_last(), Contract.created_at.desc())
        )
        contracts = result.scalars().all()
        
        responses = []
        for contract in contracts:
            response = ContractResponse.model_validate(contract)
            if contract.created_by:
                response.created_by = UserResponse.model_validate(contract.created_by)
            responses.append(response)
        
        return responses

    async def update_contract(self, contract_id: int, contract_data: ContractUpdate, user_id: int) -> Optional[ContractResponse]:
        """Update contract"""
        # Check if user has permission to edit
        contract = await self.get_contract_by_id(contract_id)
        if not contract:
            return None
        
        # Get project to check permissions
        project_result = await self.db.execute(
            select(Project).where(Project.id == contract.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project or (project.owner_id != user_id and contract.created_by_id != user_id):
            return None

        update_data = contract_data.model_dump(exclude_unset=True)
        if not update_data:
            return contract

        # Update word count if content changed
        if 'content' in update_data:
            update_data['word_count'] = len(update_data['content'].split())

        await self.db.execute(
            update(Contract)
            .where(Contract.id == contract_id)
            .values(**update_data, updated_at=func.now())
        )
        await self.db.commit()
        
        return await self.get_contract_by_id(contract_id)

    async def delete_contract(self, contract_id: int, user_id: int) -> bool:
        """Delete contract"""
        contract = await self.get_contract_by_id(contract_id)
        if not contract:
            return False
        
        # Get project to check permissions
        project_result = await self.db.execute(
            select(Project).where(Project.id == contract.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project or (project.owner_id != user_id and contract.created_by_id != user_id):
            return False

        await self.db.execute(delete(Contract).where(Contract.id == contract_id))
        await self.db.commit()
        return True

    async def lock_contract(self, contract_id: int, user_id: int) -> Optional[ContractResponse]:
        """Lock contract for editing"""
        contract = await self.get_contract_by_id(contract_id)
        if not contract:
            return None
        
        if contract.is_locked and contract.is_locked != user_id:
            return None  # Already locked by another user

        await self.db.execute(
            update(Contract)
            .where(Contract.id == contract_id)
            .values(is_locked=user_id, locked_at=func.now())
        )
        await self.db.commit()
        
        return await self.get_contract_by_id(contract_id)

    async def unlock_contract(self, contract_id: int, user_id: int) -> Optional[ContractResponse]:
        """Unlock contract"""
        contract = await self.get_contract_by_id(contract_id)
        if not contract:
            return None
        
        if contract.is_locked and contract.is_locked != user_id:
            return None  # Can only unlock own lock

        await self.db.execute(
            update(Contract)
            .where(Contract.id == contract_id)
            .values(is_locked=None, locked_at=None)
        )
        await self.db.commit()
        
        return await self.get_contract_by_id(contract_id)

    async def search_contracts(self, query: str, user_id: int, filters: Optional[Dict[str, Any]] = None) -> List[ContractResponse]:
        """Search contracts by content and title"""
        # Build base query for contracts user has access to
        base_query = select(Contract).options(selectinload(Contract.created_by))
        
        # Add text search
        search_condition = or_(
            Contract.title.ilike(f"%{query}%"),
            Contract.content.ilike(f"%{query}%")
        )
        
        # Add access control - user can see contracts they created or from public projects they own
        access_condition = or_(
            Contract.created_by_id == user_id,
            Contract.project_id.in_(
                select(Project.id).where(
                    or_(Project.owner_id == user_id, Project.is_public == True)
                )
            )
        )
        
        query_stmt = base_query.where(search_condition).where(access_condition)
        
        # Apply filters if provided
        if filters:
            if 'status' in filters:
                query_stmt = query_stmt.where(Contract.status == filters['status'])
            if 'contract_type' in filters:
                query_stmt = query_stmt.where(Contract.contract_type == filters['contract_type'])
            if 'priority' in filters:
                query_stmt = query_stmt.where(Contract.priority == filters['priority'])
        
        result = await self.db.execute(query_stmt.limit(50))
        contracts = result.scalars().all()
        
        responses = []
        for contract in contracts:
            response = ContractResponse.model_validate(contract)
            if contract.created_by:
                response.created_by = UserResponse.model_validate(contract.created_by)
            responses.append(response)
        
        return responses

    async def get_contract_count_by_project(self, project_id: int) -> int:
        """Get total contract count for project"""
        result = await self.db.execute(
            select(func.count(Contract.id)).where(Contract.project_id == project_id)
        )
        return result.scalar() or 0
"""
Analytics endpoints for contract and platform insights
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/contract/{contract_id}", response_model=Dict[str, Any])
async def get_contract_analytics(
    contract_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics for a specific contract"""
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_contract_analytics(contract_id)
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return analytics

@router.get("/project/{project_id}", response_model=Dict[str, Any])
async def get_project_analytics(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a project"""
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_project_analytics(project_id)
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return analytics

@router.get("/platform", response_model=Dict[str, Any])
async def get_platform_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get platform-wide analytics (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_platform_analytics(days=days)

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_user_dashboard(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized dashboard analytics for current user"""
    analytics_service = AnalyticsService(db)
    
    # Get user's projects and contracts
    from app.services.project_service import ProjectService
    from app.services.contract_service import ContractService
    
    project_service = ProjectService(db)
    contract_service = ContractService(db)
    
    # Get user's projects
    user_projects = await project_service.get_projects_by_owner(current_user.id, limit=10)
    
    # Get user's recent contracts
    user_contracts = await contract_service.get_contracts_by_user(current_user.id, limit=10)
    
    # Aggregate analytics
    total_projects = len(user_projects)
    total_contracts = len(user_contracts)
    
    # Get detailed analytics for recent contracts
    contract_analytics = []
    for contract in user_contracts[:5]:  # Top 5 recent contracts
        contract_data = await analytics_service.get_contract_analytics(contract.id)
        contract_analytics.append(contract_data)
    
    return {
        "user_info": {
            "id": current_user.id,
            "name": current_user.full_name,
            "role": current_user.role
        },
        "summary": {
            "total_projects": total_projects,
            "total_contracts": total_contracts,
            "recent_projects": user_projects,
            "recent_contracts": user_contracts
        },
        "contract_analytics": contract_analytics
    }
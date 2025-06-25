"""
Version management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.version import (
    ContractVersionCreate, ContractVersionUpdate, ContractVersionResponse,
    ContractVersionListResponse, ContractVersionCompareRequest, ContractVersionDiff,
    ContractVersionApproval
)
from app.services.version_service import VersionService

router = APIRouter()

@router.post("/", response_model=ContractVersionResponse)
async def create_version(
    version_data: ContractVersionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contract version"""
    version_service = VersionService(db)
    try:
        return await version_service.create_version(version_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/contract/{contract_id}", response_model=List[ContractVersionResponse])
async def get_contract_versions(
    contract_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get versions for a contract"""
    version_service = VersionService(db)
    return await version_service.get_versions_by_contract(contract_id, skip=skip, limit=limit)

@router.get("/{version_id}", response_model=ContractVersionResponse)
async def get_version(
    version_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get version by ID"""
    version_service = VersionService(db)
    version = await version_service.get_version_by_id(version_id)
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return version

@router.put("/{version_id}", response_model=ContractVersionResponse)
async def update_version(
    version_id: int,
    version_data: ContractVersionUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update version metadata"""
    version_service = VersionService(db)
    updated_version = await version_service.update_version(
        version_id, version_data, current_user.id
    )
    
    if not updated_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return updated_version

@router.delete("/{version_id}")
async def delete_version(
    version_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete version"""
    version_service = VersionService(db)
    success = await version_service.delete_version(version_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found or access denied"
        )
    
    return {"message": "Version deleted successfully"}

@router.post("/{version_id}/approve", response_model=ContractVersionResponse)
async def approve_version(
    version_id: int,
    approval: ContractVersionApproval,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject a version"""
    version_service = VersionService(db)
    approved_version = await version_service.approve_version(
        version_id, approval, current_user.id
    )
    
    if not approved_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return approved_version

@router.post("/compare", response_model=ContractVersionDiff)
async def compare_versions(
    compare_request: ContractVersionCompareRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Compare two versions"""
    version_service = VersionService(db)
    try:
        return await version_service.compare_versions(
            compare_request.base_version_id,
            compare_request.compare_version_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
"""
Contract management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.contract import (
    ContractCreate, ContractUpdate, ContractResponse, 
    ContractListResponse, ContractLockRequest, ContractSearchRequest
)
from app.services.contract_service import ContractService

router = APIRouter()

@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract_data: ContractCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contract"""
    contract_service = ContractService(db)
    try:
        return await contract_service.create_contract(contract_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=ContractListResponse)
async def get_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[int] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of contracts"""
    contract_service = ContractService(db)
    
    if project_id:
        contracts = await contract_service.get_contracts_by_project(
            project_id, skip=skip, limit=limit
        )
        total = await contract_service.get_contract_count_by_project(project_id)
    else:
        contracts = await contract_service.get_contracts_by_user(
            current_user.id, skip=skip, limit=limit
        )
        # Get total count - simplified for now
        total = len(contracts) + skip
    
    return ContractListResponse(
        contracts=contracts,
        total=total,
        page=(skip // limit) + 1,
        size=len(contracts),
        has_next=len(contracts) == limit
    )

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contract by ID"""
    contract_service = ContractService(db)
    contract = await contract_service.get_contract_by_id(contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return contract

@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update contract"""
    contract_service = ContractService(db)
    updated_contract = await contract_service.update_contract(
        contract_id, contract_data, current_user.id
    )
    
    if not updated_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found or access denied"
        )
    
    return updated_contract

@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete contract"""
    contract_service = ContractService(db)
    success = await contract_service.delete_contract(contract_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found or access denied"
        )
    
    return {"message": "Contract deleted successfully"}

@router.post("/{contract_id}/lock", response_model=ContractResponse)
async def lock_contract(
    contract_id: int,
    lock_request: ContractLockRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lock or unlock contract for editing"""
    contract_service = ContractService(db)
    
    if lock_request.action == "lock":
        result = await contract_service.lock_contract(contract_id, current_user.id)
    else:
        result = await contract_service.unlock_contract(contract_id, current_user.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot {lock_request.action} contract"
        )
    
    return result

@router.post("/search", response_model=List[ContractResponse])
async def search_contracts(
    search_request: ContractSearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search contracts by content and metadata"""
    contract_service = ContractService(db)
    
    contracts = await contract_service.search_contracts(
        search_request.query,
        current_user.id,
        search_request.filters
    )
    
    return contracts
"""
Presence management endpoints for real-time collaboration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.presence import (
    PresenceDataCreate, PresenceDataUpdate, PresenceDataResponse,
    PresenceListResponse, PresenceActivityUpdate
)
from app.services.presence_service import PresenceService

router = APIRouter()

@router.post("/", response_model=PresenceDataResponse)
async def upsert_presence(
    presence_data: PresenceDataCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update presence data"""
    # Ensure user can only create presence for themselves
    if presence_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create presence for another user"
        )
    
    presence_service = PresenceService(db)
    return await presence_service.upsert_presence(presence_data)

@router.get("/contract/{contract_id}", response_model=PresenceListResponse)
async def get_contract_presence(
    contract_id: int,
    active_only: bool = Query(True),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get presence data for a contract"""
    presence_service = PresenceService(db)
    return await presence_service.get_presence_by_contract(contract_id, active_only=active_only)

@router.put("/{user_id}/{contract_id}", response_model=PresenceDataResponse)
async def update_presence(
    user_id: int,
    contract_id: int,
    presence_data: PresenceDataUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update presence data"""
    # Ensure user can only update their own presence
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update presence for another user"
        )
    
    presence_service = PresenceService(db)
    updated_presence = await presence_service.update_presence(
        user_id, contract_id, presence_data
    )
    
    if not updated_presence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presence not found"
        )
    
    return updated_presence

@router.delete("/{contract_id}")
async def remove_presence(
    contract_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove user presence from contract"""
    presence_service = PresenceService(db)
    success = await presence_service.remove_presence(current_user.id, contract_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove presence"
        )
    
    return {"message": "Presence removed successfully"}

@router.post("/{contract_id}/deactivate", response_model=PresenceDataResponse)
async def deactivate_presence(
    contract_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark presence as inactive"""
    presence_service = PresenceService(db)
    deactivated_presence = await presence_service.deactivate_presence(
        current_user.id, contract_id
    )
    
    if not deactivated_presence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presence not found"
        )
    
    return deactivated_presence

@router.get("/user/active-contracts", response_model=List[int])
async def get_user_active_contracts(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contracts where user is currently active"""
    presence_service = PresenceService(db)
    return await presence_service.get_user_active_contracts(current_user.id)

@router.post("/activity")
async def broadcast_activity(
    activity: PresenceActivityUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Broadcast user activity update"""
    # Ensure user can only broadcast their own activity
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot broadcast activity for another user"
        )
    
    presence_service = PresenceService(db)
    broadcast_data = await presence_service.broadcast_activity_update(activity)
    
    return {"message": "Activity broadcasted", "data": broadcast_data}

@router.post("/cleanup")
async def cleanup_inactive_presence(
    inactive_threshold_minutes: int = Query(30, ge=5, le=1440),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clean up inactive presence records (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    presence_service = PresenceService(db)
    cleaned_count = await presence_service.cleanup_inactive_presence(inactive_threshold_minutes)
    
    return {"message": f"Cleaned up {cleaned_count} inactive presence records"}
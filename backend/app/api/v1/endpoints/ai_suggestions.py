"""
AI Suggestion management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.ai_suggestion import (
    AISuggestionCreate, AISuggestionUpdate, AISuggestionResponse,
    AISuggestionListResponse, AISuggestionBatchRequest, AISuggestionFeedback
)
from app.services.ai_suggestion_service import AISuggestionService

router = APIRouter()

@router.post("/", response_model=AISuggestionResponse)
async def create_suggestion(
    suggestion_data: AISuggestionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new AI suggestion"""
    suggestion_service = AISuggestionService(db)
    return await suggestion_service.create_suggestion(suggestion_data)

@router.post("/generate", response_model=List[AISuggestionResponse])
async def generate_suggestions(
    batch_request: AISuggestionBatchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI suggestions for a contract"""
    suggestion_service = AISuggestionService(db)
    try:
        return await suggestion_service.generate_suggestions_for_contract(batch_request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/contract/{contract_id}", response_model=List[AISuggestionResponse])
async def get_contract_suggestions(
    contract_id: int,
    status: Optional[str] = Query(None, regex="^(pending|accepted|rejected|implemented)$"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI suggestions for a contract"""
    suggestion_service = AISuggestionService(db)
    return await suggestion_service.get_suggestions_by_contract(contract_id, status=status)

@router.get("/{suggestion_id}", response_model=AISuggestionResponse)
async def get_suggestion(
    suggestion_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI suggestion by ID"""
    suggestion_service = AISuggestionService(db)
    suggestion = await suggestion_service.get_suggestion_by_id(suggestion_id)
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    return suggestion

@router.put("/{suggestion_id}", response_model=AISuggestionResponse)
async def update_suggestion(
    suggestion_id: int,
    suggestion_data: AISuggestionUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update AI suggestion (review, accept, reject)"""
    suggestion_service = AISuggestionService(db)
    updated_suggestion = await suggestion_service.update_suggestion(
        suggestion_id, suggestion_data, current_user.id
    )
    
    if not updated_suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    return updated_suggestion

@router.delete("/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete AI suggestion"""
    suggestion_service = AISuggestionService(db)
    success = await suggestion_service.delete_suggestion(suggestion_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    return {"message": "Suggestion deleted successfully"}

@router.post("/feedback")
async def submit_feedback(
    feedback: AISuggestionFeedback,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback for an AI suggestion"""
    suggestion_service = AISuggestionService(db)
    success = await suggestion_service.submit_feedback(feedback)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit feedback"
        )
    
    return {"message": "Feedback submitted successfully"}

@router.get("/stats/contract/{contract_id}")
async def get_suggestion_stats(
    contract_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI suggestion statistics for a contract"""
    suggestion_service = AISuggestionService(db)
    return await suggestion_service.get_suggestion_statistics(contract_id=contract_id)
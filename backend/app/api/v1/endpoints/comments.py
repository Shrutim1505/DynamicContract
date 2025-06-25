"""
Comment management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserResponse
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse, 
    CommentListResponse, CommentThreadResponse
)
from app.services.comment_service import CommentService

router = APIRouter()

@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new comment"""
    comment_service = CommentService(db)
    try:
        return await comment_service.create_comment(comment_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/contract/{contract_id}", response_model=List[CommentResponse])
async def get_contract_comments(
    contract_id: int,
    include_replies: bool = Query(True),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comments for a contract"""
    comment_service = CommentService(db)
    return await comment_service.get_comments_by_contract(
        contract_id, include_replies=include_replies
    )

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comment by ID"""
    comment_service = CommentService(db)
    comment = await comment_service.get_comment_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    return comment

@router.get("/{comment_id}/thread", response_model=List[CommentResponse])
async def get_comment_thread(
    comment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comment thread (parent + replies)"""
    comment_service = CommentService(db)
    return await comment_service.get_comment_thread(comment_id)

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update comment"""
    comment_service = CommentService(db)
    updated_comment = await comment_service.update_comment(
        comment_id, comment_data, current_user.id
    )
    
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or access denied"
        )
    
    return updated_comment

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete comment"""
    comment_service = CommentService(db)
    success = await comment_service.delete_comment(comment_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or access denied"
        )
    
    return {"message": "Comment deleted successfully"}

@router.post("/{comment_id}/resolve", response_model=CommentResponse)
async def resolve_comment(
    comment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark comment as resolved"""
    comment_service = CommentService(db)
    resolved_comment = await comment_service.resolve_comment(comment_id, current_user.id)
    
    if not resolved_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    return resolved_comment

@router.post("/{comment_id}/unresolve", response_model=CommentResponse)
async def unresolve_comment(
    comment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark comment as unresolved"""
    comment_service = CommentService(db)
    unresolved_comment = await comment_service.unresolve_comment(comment_id)
    
    if not unresolved_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    return unresolved_comment
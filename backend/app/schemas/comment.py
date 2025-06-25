"""
Comment schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.user import UserResponse

class CommentPosition(BaseModel):
    """Schema for comment position in document"""
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    text: Optional[str] = None

class CommentBase(BaseModel):
    """Base comment schema"""
    content: str = Field(..., min_length=1, max_length=5000)
    comment_type: str = Field(default="general", regex="^(general|suggestion|issue|question)$")
    priority: str = Field(default="normal", regex="^(low|normal|high)$")

class CommentCreate(CommentBase):
    """Schema for comment creation"""
    contract_id: int
    parent_id: Optional[int] = None
    position: Optional[CommentPosition] = None
    mentioned_users: Optional[List[int]] = Field(default_factory=list)

class CommentUpdate(BaseModel):
    """Schema for comment updates"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    priority: Optional[str] = Field(None, regex="^(low|normal|high)$")
    is_resolved: Optional[bool] = None

class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: int
    contract_id: int
    user_id: int
    parent_id: Optional[int] = None
    position: Optional[CommentPosition] = None
    is_resolved: bool
    resolved_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    mentioned_users: Optional[List[int]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationship data
    user: Optional[UserResponse] = None
    resolved_by: Optional[UserResponse] = None
    replies: Optional[List["CommentResponse"]] = Field(default_factory=list)
    reply_count: Optional[int] = None

    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    """Schema for paginated comment list"""
    comments: List[CommentResponse]
    total: int
    page: int
    size: int
    has_next: bool

class CommentThreadResponse(BaseModel):
    """Schema for comment thread (parent + replies)"""
    parent: CommentResponse
    replies: List[CommentResponse]
    total_replies: int

# Fix forward reference
CommentResponse.model_rebuild()
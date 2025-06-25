"""
Presence schemas for real-time collaboration
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.schemas.user import UserResponse

class PresencePosition(BaseModel):
    """Schema for cursor position"""
    line: int = Field(..., ge=0)
    character: int = Field(..., ge=0)

class PresenceRange(BaseModel):
    """Schema for selection range"""
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)

class PresenceDataBase(BaseModel):
    """Base presence data schema"""
    is_active: bool = Field(default=True)
    cursor_position: Optional[PresencePosition] = None
    selection_range: Optional[PresenceRange] = None
    current_action: Optional[str] = Field(None, max_length=100)
    editing_section: Optional[str] = Field(None, max_length=255)
    view_mode: str = Field(default="edit", regex="^(edit|review|read-only)$")

class PresenceDataCreate(PresenceDataBase):
    """Schema for presence data creation"""
    user_id: int
    contract_id: int
    session_id: Optional[str] = Field(None, max_length=255)
    user_agent: Optional[str] = Field(None, max_length=512)
    ip_address: Optional[str] = Field(None, max_length=45)

class PresenceDataUpdate(BaseModel):
    """Schema for presence data updates"""
    is_active: Optional[bool] = None
    cursor_position: Optional[PresencePosition] = None
    selection_range: Optional[PresenceRange] = None
    current_action: Optional[str] = Field(None, max_length=100)
    last_activity: Optional[str] = Field(None, max_length=100)
    editing_section: Optional[str] = Field(None, max_length=255)
    view_mode: Optional[str] = Field(None, regex="^(edit|review|read-only)$")

class PresenceDataResponse(PresenceDataBase):
    """Schema for presence data response"""
    id: str
    user_id: int
    contract_id: int
    last_activity: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    joined_at: datetime
    last_seen: datetime
    
    # Relationship data
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class PresenceListResponse(BaseModel):
    """Schema for contract presence list"""
    presence_data: List[PresenceDataResponse]
    active_users: int
    total_users: int

class PresenceActivityUpdate(BaseModel):
    """Schema for real-time presence updates"""
    user_id: int
    contract_id: int
    activity_type: str = Field(..., regex="^(join|leave|typing|cursor_move|selection|idle)$")
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
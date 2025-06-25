"""
User schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="user", regex="^(user|admin|reviewer)$")
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", max_length=10)

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8, max_length=255)
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)

class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    preferences: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    email_notifications: bool
    push_notifications: bool

    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    """Extended user profile with additional information"""
    api_key: Optional[str] = None
    preferences: Optional[str] = None

class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    has_next: bool
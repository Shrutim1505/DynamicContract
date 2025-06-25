"""
Project schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.schemas.user import UserResponse

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    is_public: bool = Field(default=False)
    is_template: bool = Field(default=False)
    color: str = Field(default="#3B82F6", regex="^#[0-9A-Fa-f]{6}$")
    client_name: Optional[str] = Field(None, max_length=255)
    project_status: str = Field(default="active", regex="^(active|archived|completed)$")

class ProjectCreate(ProjectBase):
    """Schema for project creation"""
    tags: Optional[List[str]] = Field(default_factory=list)

class ProjectUpdate(BaseModel):
    """Schema for project updates"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    is_public: Optional[bool] = None
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    client_name: Optional[str] = Field(None, max_length=255)
    project_status: Optional[str] = Field(None, regex="^(active|archived|completed)$")
    tags: Optional[List[str]] = None

class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    owner_id: int
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    
    # Optional relationship data
    owner: Optional[UserResponse] = None
    contract_count: Optional[int] = None

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    """Schema for paginated project list"""
    projects: List[ProjectResponse]
    total: int
    page: int
    size: int
    has_next: bool

class ProjectWithContracts(ProjectResponse):
    """Project with contract details"""
    from app.schemas.contract import ContractResponse
    contracts: List[ContractResponse] = Field(default_factory=list)
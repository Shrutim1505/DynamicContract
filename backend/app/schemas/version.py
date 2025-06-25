"""
Contract Version schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.user import UserResponse

class ContractVersionBase(BaseModel):
    """Base contract version schema"""
    version_number: str = Field(..., min_length=1, max_length=50)
    change_summary: Optional[str] = Field(None, max_length=1000)
    version_type: str = Field(default="minor", regex="^(major|minor|patch|auto)$")
    is_major_version: bool = Field(default=False)

class ContractVersionCreate(ContractVersionBase):
    """Schema for contract version creation"""
    contract_id: int
    content: str = Field(..., min_length=1)
    changes: Optional[List[Dict[str, Any]]] = None
    requires_approval: bool = Field(default=False)
    tags: Optional[List[str]] = None
    release_notes: Optional[str] = None

class ContractVersionUpdate(BaseModel):
    """Schema for contract version updates"""
    change_summary: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    release_notes: Optional[str] = None

class ContractVersionResponse(ContractVersionBase):
    """Schema for contract version response"""
    id: int
    contract_id: int
    content: str
    changes: Optional[List[Dict[str, Any]]] = None
    created_by_id: int
    additions_count: int
    deletions_count: int
    modifications_count: int
    requires_approval: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    release_notes: Optional[str] = None
    created_at: datetime
    
    # Relationship data
    created_by: Optional[UserResponse] = None
    approved_by: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class ContractVersionListResponse(BaseModel):
    """Schema for paginated contract version list"""
    versions: List[ContractVersionResponse]
    total: int
    page: int
    size: int
    has_next: bool

class ContractVersionCompareRequest(BaseModel):
    """Schema for version comparison requests"""
    base_version_id: int
    compare_version_id: int
    comparison_type: str = Field(default="detailed", regex="^(summary|detailed|semantic)$")

class ContractVersionDiff(BaseModel):
    """Schema for version differences"""
    additions: List[Dict[str, Any]]
    deletions: List[Dict[str, Any]]
    modifications: List[Dict[str, Any]]
    summary: str
    statistics: Dict[str, int]

class ContractVersionApproval(BaseModel):
    """Schema for version approval"""
    approved: bool
    approval_notes: Optional[str] = None
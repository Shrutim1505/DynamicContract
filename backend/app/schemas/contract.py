"""
Contract schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.user import UserResponse

class ContractBase(BaseModel):
    """Base contract schema"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    contract_type: Optional[str] = Field(None, max_length=100)
    priority: str = Field(default="medium", regex="^(low|medium|high|urgent)$")
    language: str = Field(default="en", max_length=10)
    jurisdiction: Optional[str] = Field(None, max_length=100)

class ContractCreate(ContractBase):
    """Schema for contract creation"""
    project_id: int
    version: str = Field(default="1.0", max_length=50)

class ContractUpdate(BaseModel):
    """Schema for contract updates"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, regex="^(draft|review|approved|signed|archived)$")
    contract_type: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = Field(None, regex="^(low|medium|high|urgent)$")
    jurisdiction: Optional[str] = Field(None, max_length=100)

class ContractAnalytics(BaseModel):
    """Schema for contract analytics data"""
    word_count: Optional[int] = None
    reading_level: Optional[str] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    identified_risks: Optional[List[Dict[str, Any]]] = None
    missing_clauses: Optional[List[Dict[str, Any]]] = None
    compliance_issues: Optional[List[Dict[str, Any]]] = None

class ContractResponse(ContractBase):
    """Schema for contract response"""
    id: int
    project_id: int
    created_by_id: int
    version: str
    status: str
    is_locked: Optional[int] = None
    locked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    signed_at: Optional[datetime] = None
    
    # Analytics data
    analytics: Optional[ContractAnalytics] = None
    
    # Optional relationship data
    created_by: Optional[UserResponse] = None
    comment_count: Optional[int] = None
    suggestion_count: Optional[int] = None

    class Config:
        from_attributes = True

class ContractListResponse(BaseModel):
    """Schema for paginated contract list"""
    contracts: List[ContractResponse]
    total: int
    page: int
    size: int
    has_next: bool

class ContractLockRequest(BaseModel):
    """Schema for contract lock/unlock requests"""
    action: str = Field(..., regex="^(lock|unlock)$")

class ContractSearchRequest(BaseModel):
    """Schema for contract search requests"""
    query: str = Field(..., min_length=1)
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = Field(default="updated_at")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")
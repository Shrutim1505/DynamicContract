"""
AI Suggestion schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.user import UserResponse

class SuggestionPosition(BaseModel):
    """Schema for suggestion position in document"""
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    line: Optional[int] = Field(None, ge=0)

class AISuggestionBase(BaseModel):
    """Base AI suggestion schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    suggestion_type: str = Field(..., regex="^(clause_addition|text_improvement|risk_mitigation|compliance_check)$")
    category: Optional[str] = Field(None, max_length=100)
    severity: str = Field(default="medium", regex="^(low|medium|high|critical)$")

class AISuggestionCreate(AISuggestionBase):
    """Schema for AI suggestion creation"""
    contract_id: int
    suggested_text: Optional[str] = None
    position: Optional[SuggestionPosition] = None
    affected_text: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_model: Optional[str] = Field(None, max_length=100)
    model_version: Optional[str] = Field(None, max_length=50)
    legal_basis: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None
    jurisdiction_specific: bool = Field(default=False)

class AISuggestionUpdate(BaseModel):
    """Schema for AI suggestion updates"""
    status: Optional[str] = Field(None, regex="^(pending|accepted|rejected|implemented)$")
    review_notes: Optional[str] = None
    user_feedback_score: Optional[int] = Field(None, ge=1, le=5)

class AISuggestionResponse(AISuggestionBase):
    """Schema for AI suggestion response"""
    id: int
    contract_id: int
    suggested_text: Optional[str] = None
    position: Optional[SuggestionPosition] = None
    affected_text: Optional[str] = None
    confidence_score: Optional[float] = None
    ai_model: Optional[str] = None
    model_version: Optional[str] = None
    status: str
    reviewed_by_id: Optional[int] = None
    review_notes: Optional[str] = None
    legal_basis: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None
    jurisdiction_specific: bool
    user_feedback_score: Optional[int] = None
    implementation_impact: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None
    
    # Relationship data
    reviewed_by: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class AISuggestionListResponse(BaseModel):
    """Schema for paginated AI suggestion list"""
    suggestions: List[AISuggestionResponse]
    total: int
    page: int
    size: int
    has_next: bool

class AISuggestionBatchRequest(BaseModel):
    """Schema for batch AI suggestion requests"""
    contract_id: int
    suggestion_types: List[str] = Field(default_factory=list)
    focus_areas: Optional[List[str]] = None
    jurisdiction: Optional[str] = None

class AISuggestionFeedback(BaseModel):
    """Schema for AI suggestion feedback"""
    suggestion_id: int
    feedback_score: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    is_helpful: bool
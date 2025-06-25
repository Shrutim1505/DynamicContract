"""
AI Suggestion model for intelligent contract recommendations
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class AISuggestion(Base):
    """AI Suggestion model for intelligent contract recommendations"""
    __tablename__ = "ai_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # Suggestion content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    suggested_text = Column(Text, nullable=True)  # Suggested replacement text
    
    # Suggestion metadata
    suggestion_type = Column(String(50), nullable=False)  # clause_addition, text_improvement, risk_mitigation, compliance_check
    category = Column(String(100), nullable=True)  # payment_terms, liability, termination, etc.
    severity = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    confidence_score = Column(Float, nullable=True)  # AI confidence level 0.0 to 1.0
    
    # Position in document
    position = Column(JSON, nullable=True)  # {"start": int, "end": int, "line": int}
    affected_text = Column(Text, nullable=True)  # Original text that would be affected
    
    # AI model information
    ai_model = Column(String(100), nullable=True)  # GPT-4, Claude, etc.
    model_version = Column(String(50), nullable=True)
    
    # Suggestion status
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, rejected, implemented
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Legal context
    legal_basis = Column(Text, nullable=True)  # Explanation of legal reasoning
    references = Column(JSON, nullable=True)  # Array of legal references or precedents
    jurisdiction_specific = Column(Boolean, default=False, nullable=False)
    
    # Analytics
    user_feedback_score = Column(Integer, nullable=True)  # 1-5 rating from user
    implementation_impact = Column(String(50), nullable=True)  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    implemented_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    contract = relationship("Contract", back_populates="ai_suggestions")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    
    def __repr__(self):
        return f"<AISuggestion(id={self.id}, contract_id={self.contract_id}, type='{self.suggestion_type}')>"
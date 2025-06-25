"""
Contract model for storing legal documents
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Contract(Base):
    """Contract model for storing legal documents and their metadata"""
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Contract metadata
    version = Column(String(50), default="1.0", nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, review, approved, signed, archived
    contract_type = Column(String(100), nullable=True)  # NDA, Service Agreement, etc.
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high, urgent
    
    # AI-powered analytics
    risk_score = Column(Float, nullable=True)  # 0.0 to 1.0
    completeness_score = Column(Float, nullable=True)  # 0.0 to 1.0
    word_count = Column(Integer, nullable=True)
    reading_level = Column(String(50), nullable=True)  # Grade level or complexity score
    
    # Legal analysis
    identified_risks = Column(JSON, nullable=True)  # Array of risk objects
    missing_clauses = Column(JSON, nullable=True)  # Array of suggested clauses
    compliance_issues = Column(JSON, nullable=True)  # Array of compliance concerns
    
    # Collaboration metadata
    is_locked = Column(Integer, ForeignKey("users.id"), nullable=True)  # User ID who locked it
    locked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Document properties
    language = Column(String(10), default="en", nullable=False)
    jurisdiction = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="contracts")
    created_by = relationship("User", back_populates="created_contracts")
    comments = relationship("Comment", back_populates="contract", cascade="all, delete-orphan")
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")
    ai_suggestions = relationship("AISuggestion", back_populates="contract", cascade="all, delete-orphan")
    presence_data = relationship("PresenceData", back_populates="contract", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contract(id={self.id}, title='{self.title}', status='{self.status}')>"
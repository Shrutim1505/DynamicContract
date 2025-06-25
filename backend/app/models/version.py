"""
Contract Version model for version control
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class ContractVersion(Base):
    """Contract Version model for tracking document changes"""
    __tablename__ = "contract_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    version_number = Column(String(50), nullable=False)  # e.g., "1.0", "1.1", "2.0"
    
    # Version content
    content = Column(Text, nullable=False)  # Full content snapshot
    changes = Column(JSON, nullable=True)  # Detailed change information
    change_summary = Column(Text, nullable=True)  # Human-readable summary
    
    # Version metadata
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    version_type = Column(String(50), default="minor", nullable=False)  # major, minor, patch, auto
    is_major_version = Column(Boolean, default=False, nullable=False)
    
    # Change tracking
    additions_count = Column(Integer, default=0, nullable=False)
    deletions_count = Column(Integer, default=0, nullable=False)
    modifications_count = Column(Integer, default=0, nullable=False)
    
    # Approval and review
    requires_approval = Column(Boolean, default=False, nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tags and labels
    tags = Column(JSON, nullable=True)  # Array of version tags
    release_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="versions")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    
    def __repr__(self):
        return f"<ContractVersion(id={self.id}, contract_id={self.contract_id}, version='{self.version_number}')>"
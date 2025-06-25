"""
Presence model for real-time collaboration tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class PresenceData(Base):
    """Presence model for tracking real-time user activity"""
    __tablename__ = "presence_data"
    
    id = Column(String(255), primary_key=True)  # Composite key: "user_id:contract_id"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # Presence information
    is_active = Column(Boolean, default=True, nullable=False)
    cursor_position = Column(JSON, nullable=True)  # {"line": int, "character": int}
    selection_range = Column(JSON, nullable=True)  # {"start": int, "end": int}
    
    # Activity tracking
    current_action = Column(String(100), nullable=True)  # typing, selecting, idle, commenting
    last_activity = Column(String(100), nullable=True)  # Last action performed
    
    # Session information
    session_id = Column(String(255), nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    
    # Collaboration context
    editing_section = Column(String(255), nullable=True)  # Which section they're working on
    view_mode = Column(String(50), default="edit", nullable=False)  # edit, review, read-only
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="presence_data")
    contract = relationship("Contract", back_populates="presence_data")
    
    def __repr__(self):
        return f"<PresenceData(user_id={self.user_id}, contract_id={self.contract_id}, is_active={self.is_active})>"
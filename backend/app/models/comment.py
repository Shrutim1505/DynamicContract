"""
Comment model for collaborative discussions
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Comment(Base):
    """Comment model for collaborative discussions on contracts"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # For threading
    
    # Position in document (for inline comments)
    position = Column(JSON, nullable=True)  # {"start": int, "end": int, "text": str}
    
    # Comment metadata
    comment_type = Column(String(50), default="general", nullable=False)  # general, suggestion, issue, question
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Mentions and notifications
    mentioned_users = Column(JSON, nullable=True)  # Array of user IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    contract = relationship("Contract", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    
    def __repr__(self):
        return f"<Comment(id={self.id}, contract_id={self.contract_id}, user_id={self.user_id})>"
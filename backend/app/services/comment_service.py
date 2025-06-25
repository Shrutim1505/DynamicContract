"""
Comment service for collaborative discussions
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.models.comment import Comment
from app.models.contract import Contract
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.schemas.user import UserResponse

class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, comment_data: CommentCreate, user_id: int) -> CommentResponse:
        """Create a new comment"""
        # Verify contract exists and user has access
        contract_result = await self.db.execute(
            select(Contract).where(Contract.id == comment_data.contract_id)
        )
        contract = contract_result.scalar_one_or_none()
        
        if not contract:
            raise ValueError("Contract not found")

        db_comment = Comment(
            content=comment_data.content,
            contract_id=comment_data.contract_id,
            user_id=user_id,
            parent_id=comment_data.parent_id,
            position=comment_data.position.model_dump() if comment_data.position else None,
            comment_type=comment_data.comment_type,
            priority=comment_data.priority,
            mentioned_users=comment_data.mentioned_users
        )
        
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        
        return await self.get_comment_by_id(db_comment.id)

    async def get_comment_by_id(self, comment_id: int) -> Optional[CommentResponse]:
        """Get comment by ID with relationships"""
        result = await self.db.execute(
            select(Comment)
            .options(
                selectinload(Comment.user),
                selectinload(Comment.resolved_by)
            )
            .where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        
        if not comment:
            return None
            
        response = CommentResponse.model_validate(comment)
        
        if comment.user:
            response.user = UserResponse.model_validate(comment.user)
        if comment.resolved_by:
            response.resolved_by = UserResponse.model_validate(comment.resolved_by)
        
        # Get reply count
        reply_count_result = await self.db.execute(
            select(func.count(Comment.id)).where(Comment.parent_id == comment_id)
        )
        response.reply_count = reply_count_result.scalar() or 0
        
        return response

    async def get_comments_by_contract(self, contract_id: int, include_replies: bool = True) -> List[CommentResponse]:
        """Get comments by contract ID"""
        if include_replies:
            # Get all comments for the contract
            result = await self.db.execute(
                select(Comment)
                .options(
                    selectinload(Comment.user),
                    selectinload(Comment.resolved_by)
                )
                .where(Comment.contract_id == contract_id)
                .order_by(Comment.created_at.asc())
            )
        else:
            # Get only top-level comments (no replies)
            result = await self.db.execute(
                select(Comment)
                .options(
                    selectinload(Comment.user),
                    selectinload(Comment.resolved_by)
                )
                .where(Comment.contract_id == contract_id, Comment.parent_id.is_(None))
                .order_by(Comment.created_at.asc())
            )
        
        comments = result.scalars().all()
        
        responses = []
        for comment in comments:
            response = CommentResponse.model_validate(comment)
            if comment.user:
                response.user = UserResponse.model_validate(comment.user)
            if comment.resolved_by:
                response.resolved_by = UserResponse.model_validate(comment.resolved_by)
            responses.append(response)
        
        return responses

    async def get_comment_thread(self, parent_id: int) -> List[CommentResponse]:
        """Get comment thread (parent + all replies)"""
        result = await self.db.execute(
            select(Comment)
            .options(
                selectinload(Comment.user),
                selectinload(Comment.resolved_by)
            )
            .where(
                (Comment.id == parent_id) | (Comment.parent_id == parent_id)
            )
            .order_by(Comment.created_at.asc())
        )
        comments = result.scalars().all()
        
        responses = []
        for comment in comments:
            response = CommentResponse.model_validate(comment)
            if comment.user:
                response.user = UserResponse.model_validate(comment.user)
            if comment.resolved_by:
                response.resolved_by = UserResponse.model_validate(comment.resolved_by)
            responses.append(response)
        
        return responses

    async def update_comment(self, comment_id: int, comment_data: CommentUpdate, user_id: int) -> Optional[CommentResponse]:
        """Update comment (only author can update)"""
        comment = await self.get_comment_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return None

        update_data = comment_data.model_dump(exclude_unset=True)
        if not update_data:
            return comment

        await self.db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(**update_data, updated_at=func.now())
        )
        await self.db.commit()
        
        return await self.get_comment_by_id(comment_id)

    async def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """Delete comment (only author can delete)"""
        comment = await self.get_comment_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return False

        await self.db.execute(delete(Comment).where(Comment.id == comment_id))
        await self.db.commit()
        return True

    async def resolve_comment(self, comment_id: int, user_id: int) -> Optional[CommentResponse]:
        """Mark comment as resolved"""
        await self.db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(
                is_resolved=True,
                resolved_by_id=user_id,
                resolved_at=func.now(),
                updated_at=func.now()
            )
        )
        await self.db.commit()
        
        return await self.get_comment_by_id(comment_id)

    async def unresolve_comment(self, comment_id: int) -> Optional[CommentResponse]:
        """Mark comment as unresolved"""
        await self.db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(
                is_resolved=False,
                resolved_by_id=None,
                resolved_at=None,
                updated_at=func.now()
            )
        )
        await self.db.commit()
        
        return await self.get_comment_by_id(comment_id)
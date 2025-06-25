"""
User service for business logic
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash, generate_api_key

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            timezone=user_data.timezone,
            language=user_data.language,
            email_notifications=user_data.email_notifications,
            push_notifications=user_data.push_notifications,
            api_key=generate_api_key()
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return UserResponse.model_validate(db_user)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user"""
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user_by_id(user_id)

        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data, updated_at=func.now())
        )
        await self.db.commit()
        
        return await self.get_user_by_id(user_id)

    async def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=func.now())
        )
        await self.db.commit()

    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=func.now())
        )
        await self.db.commit()
        return True

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get paginated list of users"""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]
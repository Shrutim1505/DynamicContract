"""
Presence service for real-time collaboration
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.models.presence import PresenceData
from app.models.user import User
from app.schemas.presence import (
    PresenceDataCreate, PresenceDataUpdate, PresenceDataResponse,
    PresenceListResponse, PresenceActivityUpdate
)
from app.schemas.user import UserResponse

class PresenceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_presence(self, presence_data: PresenceDataCreate) -> PresenceDataResponse:
        """Create or update presence data"""
        presence_id = f"{presence_data.user_id}:{presence_data.contract_id}"
        
        # Check if presence already exists
        result = await self.db.execute(
            select(PresenceData).where(PresenceData.id == presence_id)
        )
        existing_presence = result.scalar_one_or_none()
        
        if existing_presence:
            # Update existing presence
            update_data = {
                'is_active': presence_data.is_active,
                'cursor_position': presence_data.cursor_position.model_dump() if presence_data.cursor_position else None,
                'selection_range': presence_data.selection_range.model_dump() if presence_data.selection_range else None,
                'current_action': presence_data.current_action,
                'editing_section': presence_data.editing_section,
                'view_mode': presence_data.view_mode,
                'session_id': presence_data.session_id,
                'user_agent': presence_data.user_agent,
                'ip_address': presence_data.ip_address,
                'last_seen': func.now()
            }
            
            await self.db.execute(
                update(PresenceData)
                .where(PresenceData.id == presence_id)
                .values(**update_data)
            )
        else:
            # Create new presence
            db_presence = PresenceData(
                id=presence_id,
                user_id=presence_data.user_id,
                contract_id=presence_data.contract_id,
                is_active=presence_data.is_active,
                cursor_position=presence_data.cursor_position.model_dump() if presence_data.cursor_position else None,
                selection_range=presence_data.selection_range.model_dump() if presence_data.selection_range else None,
                current_action=presence_data.current_action,
                editing_section=presence_data.editing_section,
                view_mode=presence_data.view_mode,
                session_id=presence_data.session_id,
                user_agent=presence_data.user_agent,
                ip_address=presence_data.ip_address
            )
            
            self.db.add(db_presence)
        
        await self.db.commit()
        return await self.get_presence_by_id(presence_id)

    async def get_presence_by_id(self, presence_id: str) -> Optional[PresenceDataResponse]:
        """Get presence by ID with user information"""
        result = await self.db.execute(
            select(PresenceData)
            .options(selectinload(PresenceData.user))
            .where(PresenceData.id == presence_id)
        )
        presence = result.scalar_one_or_none()
        
        if not presence:
            return None
            
        response = PresenceDataResponse.model_validate(presence)
        
        if presence.user:
            response.user = UserResponse.model_validate(presence.user)
        
        return response

    async def get_presence_by_contract(self, contract_id: int, active_only: bool = True) -> PresenceListResponse:
        """Get all presence data for a contract"""
        query = select(PresenceData).options(selectinload(PresenceData.user)).where(
            PresenceData.contract_id == contract_id
        )
        
        if active_only:
            # Consider presence active if last seen within 5 minutes
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            query = query.where(
                PresenceData.is_active == True,
                PresenceData.last_seen >= cutoff_time
            )
        
        result = await self.db.execute(query.order_by(PresenceData.last_seen.desc()))
        presence_list = result.scalars().all()
        
        responses = []
        active_count = 0
        
        for presence in presence_list:
            response = PresenceDataResponse.model_validate(presence)
            if presence.user:
                response.user = UserResponse.model_validate(presence.user)
            
            responses.append(response)
            
            if presence.is_active:
                active_count += 1
        
        return PresenceListResponse(
            presence_data=responses,
            active_users=active_count,
            total_users=len(responses)
        )

    async def update_presence(self, user_id: int, contract_id: int, presence_data: PresenceDataUpdate) -> Optional[PresenceDataResponse]:
        """Update presence data"""
        presence_id = f"{user_id}:{contract_id}"
        
        update_data = presence_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_presence_by_id(presence_id)

        # Process complex fields
        if 'cursor_position' in update_data and update_data['cursor_position']:
            update_data['cursor_position'] = update_data['cursor_position'].model_dump()
        if 'selection_range' in update_data and update_data['selection_range']:
            update_data['selection_range'] = update_data['selection_range'].model_dump()

        update_data['last_seen'] = func.now()

        await self.db.execute(
            update(PresenceData)
            .where(PresenceData.id == presence_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_presence_by_id(presence_id)

    async def remove_presence(self, user_id: int, contract_id: int) -> bool:
        """Remove user presence from contract"""
        presence_id = f"{user_id}:{contract_id}"
        
        await self.db.execute(
            delete(PresenceData).where(PresenceData.id == presence_id)
        )
        await self.db.commit()
        return True

    async def deactivate_presence(self, user_id: int, contract_id: int) -> Optional[PresenceDataResponse]:
        """Mark presence as inactive"""
        presence_id = f"{user_id}:{contract_id}"
        
        await self.db.execute(
            update(PresenceData)
            .where(PresenceData.id == presence_id)
            .values(
                is_active=False,
                last_activity="disconnected",
                last_seen=func.now()
            )
        )
        await self.db.commit()
        
        return await self.get_presence_by_id(presence_id)

    async def cleanup_inactive_presence(self, inactive_threshold_minutes: int = 30) -> int:
        """Clean up inactive presence records"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=inactive_threshold_minutes)
        
        result = await self.db.execute(
            delete(PresenceData).where(
                PresenceData.last_seen < cutoff_time
            )
        )
        await self.db.commit()
        
        return result.rowcount

    async def get_user_active_contracts(self, user_id: int) -> List[int]:
        """Get list of contract IDs where user is currently active"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        result = await self.db.execute(
            select(PresenceData.contract_id)
            .where(
                PresenceData.user_id == user_id,
                PresenceData.is_active == True,
                PresenceData.last_seen >= cutoff_time
            )
        )
        
        return [row[0] for row in result]

    async def broadcast_activity_update(self, activity: PresenceActivityUpdate) -> Dict[str, Any]:
        """Process and format activity update for broadcasting"""
        # Update presence with activity
        await self.update_presence(
            activity.user_id,
            activity.contract_id,
            PresenceDataUpdate(
                current_action=activity.activity_type,
                last_activity=activity.activity_type
            )
        )
        
        # Format for WebSocket broadcast
        return {
            "type": "presence_update",
            "user_id": activity.user_id,
            "contract_id": activity.contract_id,
            "activity_type": activity.activity_type,
            "data": activity.data,
            "timestamp": activity.timestamp.isoformat()
        }
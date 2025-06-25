"""
AI Suggestion service for managing intelligent recommendations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.models.ai_suggestion import AISuggestion
from app.models.contract import Contract
from app.models.user import User
from app.schemas.ai_suggestion import (
    AISuggestionCreate, AISuggestionUpdate, AISuggestionResponse,
    AISuggestionBatchRequest, AISuggestionFeedback
)
from app.schemas.user import UserResponse
from app.services.ai_service import AIService

class AISuggestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()

    async def create_suggestion(self, suggestion_data: AISuggestionCreate) -> AISuggestionResponse:
        """Create a new AI suggestion"""
        db_suggestion = AISuggestion(
            contract_id=suggestion_data.contract_id,
            title=suggestion_data.title,
            description=suggestion_data.description,
            suggested_text=suggestion_data.suggested_text,
            suggestion_type=suggestion_data.suggestion_type,
            category=suggestion_data.category,
            severity=suggestion_data.severity,
            position=suggestion_data.position.model_dump() if suggestion_data.position else None,
            affected_text=suggestion_data.affected_text,
            confidence_score=suggestion_data.confidence_score,
            ai_model=suggestion_data.ai_model,
            model_version=suggestion_data.model_version,
            legal_basis=suggestion_data.legal_basis,
            references=suggestion_data.references,
            jurisdiction_specific=suggestion_data.jurisdiction_specific
        )
        
        self.db.add(db_suggestion)
        await self.db.commit()
        await self.db.refresh(db_suggestion)
        
        return await self.get_suggestion_by_id(db_suggestion.id)

    async def get_suggestion_by_id(self, suggestion_id: int) -> Optional[AISuggestionResponse]:
        """Get AI suggestion by ID with relationships"""
        result = await self.db.execute(
            select(AISuggestion)
            .options(selectinload(AISuggestion.reviewed_by))
            .where(AISuggestion.id == suggestion_id)
        )
        suggestion = result.scalar_one_or_none()
        
        if not suggestion:
            return None
            
        response = AISuggestionResponse.model_validate(suggestion)
        
        if suggestion.reviewed_by:
            response.reviewed_by = UserResponse.model_validate(suggestion.reviewed_by)
        
        return response

    async def get_suggestions_by_contract(self, contract_id: int, status: Optional[str] = None) -> List[AISuggestionResponse]:
        """Get AI suggestions by contract ID"""
        query = select(AISuggestion).options(selectinload(AISuggestion.reviewed_by)).where(
            AISuggestion.contract_id == contract_id
        )
        
        if status:
            query = query.where(AISuggestion.status == status)
        
        query = query.order_by(AISuggestion.created_at.desc())
        
        result = await self.db.execute(query)
        suggestions = result.scalars().all()
        
        responses = []
        for suggestion in suggestions:
            response = AISuggestionResponse.model_validate(suggestion)
            if suggestion.reviewed_by:
                response.reviewed_by = UserResponse.model_validate(suggestion.reviewed_by)
            responses.append(response)
        
        return responses

    async def update_suggestion(self, suggestion_id: int, suggestion_data: AISuggestionUpdate, user_id: int) -> Optional[AISuggestionResponse]:
        """Update AI suggestion"""
        update_data = suggestion_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_suggestion_by_id(suggestion_id)

        # Add reviewer info if status is being changed
        if 'status' in update_data and update_data['status'] != 'pending':
            update_data['reviewed_by_id'] = user_id
            update_data['reviewed_at'] = func.now()
        
        # Mark as implemented if status is accepted
        if update_data.get('status') == 'implemented':
            update_data['implemented_at'] = func.now()

        await self.db.execute(
            update(AISuggestion)
            .where(AISuggestion.id == suggestion_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_suggestion_by_id(suggestion_id)

    async def delete_suggestion(self, suggestion_id: int) -> bool:
        """Delete AI suggestion"""
        await self.db.execute(delete(AISuggestion).where(AISuggestion.id == suggestion_id))
        await self.db.commit()
        return True

    async def generate_suggestions_for_contract(self, batch_request: AISuggestionBatchRequest) -> List[AISuggestionResponse]:
        """Generate AI suggestions for a contract"""
        # Get contract content
        contract_result = await self.db.execute(
            select(Contract).where(Contract.id == batch_request.contract_id)
        )
        contract = contract_result.scalar_one_or_none()
        
        if not contract:
            raise ValueError("Contract not found")
        
        # Generate suggestions using AI service
        suggestion_types = batch_request.suggestion_types or [
            "clause_addition", "text_improvement", "risk_mitigation", "compliance_check"
        ]
        
        ai_suggestions = await self.ai_service.generate_suggestions(
            contract.content,
            contract.id,
            suggestion_types
        )
        
        # Save suggestions to database
        created_suggestions = []
        for suggestion_data in ai_suggestions:
            db_suggestion = await self.create_suggestion(suggestion_data)
            created_suggestions.append(db_suggestion)
        
        return created_suggestions

    async def submit_feedback(self, feedback: AISuggestionFeedback) -> bool:
        """Submit feedback for an AI suggestion"""
        await self.db.execute(
            update(AISuggestion)
            .where(AISuggestion.id == feedback.suggestion_id)
            .values(
                user_feedback_score=feedback.feedback_score,
                review_notes=feedback.feedback_text
            )
        )
        await self.db.commit()
        return True

    async def get_suggestion_statistics(self, contract_id: Optional[int] = None) -> dict:
        """Get statistics about AI suggestions"""
        base_query = select(func.count(AISuggestion.id))
        
        if contract_id:
            base_query = base_query.where(AISuggestion.contract_id == contract_id)
        
        # Total suggestions
        total_result = await self.db.execute(base_query)
        total = total_result.scalar() or 0
        
        # Suggestions by status
        status_results = await self.db.execute(
            select(AISuggestion.status, func.count(AISuggestion.id))
            .where(AISuggestion.contract_id == contract_id if contract_id else True)
            .group_by(AISuggestion.status)
        )
        
        status_counts = {row[0]: row[1] for row in status_results}
        
        # Average confidence score
        confidence_result = await self.db.execute(
            select(func.avg(AISuggestion.confidence_score))
            .where(AISuggestion.contract_id == contract_id if contract_id else True)
            .where(AISuggestion.confidence_score.is_not(None))
        )
        avg_confidence = confidence_result.scalar() or 0.0
        
        return {
            "total_suggestions": total,
            "by_status": status_counts,
            "average_confidence": round(avg_confidence, 2)
        }
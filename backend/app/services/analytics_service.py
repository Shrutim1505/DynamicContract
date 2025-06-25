"""
Analytics service for contract and platform insights
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.models.contract import Contract
from app.models.project import Project
from app.models.user import User
from app.models.comment import Comment
from app.models.ai_suggestion import AISuggestion
from app.models.version import ContractVersion
from app.models.presence import PresenceData

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_contract_analytics(self, contract_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific contract"""
        # Basic contract info
        contract_result = await self.db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        contract = contract_result.scalar_one_or_none()
        
        if not contract:
            return {}

        # Comment statistics
        comment_stats = await self._get_comment_statistics(contract_id)
        
        # Version statistics
        version_stats = await self._get_version_statistics(contract_id)
        
        # AI suggestion statistics
        ai_stats = await self._get_ai_suggestion_statistics(contract_id)
        
        # Collaboration statistics
        collaboration_stats = await self._get_collaboration_statistics(contract_id)
        
        # Risk analysis
        risk_analysis = await self._analyze_contract_risks(contract)

        return {
            "contract_id": contract_id,
            "basic_info": {
                "title": contract.title,
                "status": contract.status,
                "word_count": contract.word_count,
                "risk_score": contract.risk_score,
                "completeness_score": contract.completeness_score,
                "created_at": contract.created_at,
                "updated_at": contract.updated_at
            },
            "comments": comment_stats,
            "versions": version_stats,
            "ai_suggestions": ai_stats,
            "collaboration": collaboration_stats,
            "risk_analysis": risk_analysis
        }

    async def get_project_analytics(self, project_id: int) -> Dict[str, Any]:
        """Get analytics for a project"""
        # Project basic info
        project_result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            return {}

        # Contract count and status distribution
        contract_stats = await self._get_project_contract_statistics(project_id)
        
        # Activity over time
        activity_stats = await self._get_project_activity_statistics(project_id)
        
        # Top contributors
        contributor_stats = await self._get_project_contributor_statistics(project_id)

        return {
            "project_id": project_id,
            "basic_info": {
                "name": project.name,
                "status": project.project_status,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            },
            "contracts": contract_stats,
            "activity": activity_stats,
            "contributors": contributor_stats
        }

    async def get_platform_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get platform-wide analytics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # User statistics
        user_stats = await self._get_platform_user_statistics(start_date, end_date)
        
        # Contract statistics
        contract_stats = await self._get_platform_contract_statistics(start_date, end_date)
        
        # Activity statistics
        activity_stats = await self._get_platform_activity_statistics(start_date, end_date)
        
        # AI usage statistics
        ai_usage_stats = await self._get_platform_ai_statistics(start_date, end_date)

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "users": user_stats,
            "contracts": contract_stats,
            "activity": activity_stats,
            "ai_usage": ai_usage_stats
        }

    async def _get_comment_statistics(self, contract_id: int) -> Dict[str, Any]:
        """Get comment statistics for a contract"""
        # Total comments
        total_result = await self.db.execute(
            select(func.count(Comment.id)).where(Comment.contract_id == contract_id)
        )
        total_comments = total_result.scalar() or 0

        # Resolved vs unresolved
        resolved_result = await self.db.execute(
            select(func.count(Comment.id)).where(
                Comment.contract_id == contract_id,
                Comment.is_resolved == True
            )
        )
        resolved_comments = resolved_result.scalar() or 0

        # Comments by type
        type_results = await self.db.execute(
            select(Comment.comment_type, func.count(Comment.id))
            .where(Comment.contract_id == contract_id)
            .group_by(Comment.comment_type)
        )
        comments_by_type = {row[0]: row[1] for row in type_results}

        return {
            "total_comments": total_comments,
            "resolved_comments": resolved_comments,
            "unresolved_comments": total_comments - resolved_comments,
            "resolution_rate": resolved_comments / total_comments if total_comments > 0 else 0,
            "by_type": comments_by_type
        }

    async def _get_version_statistics(self, contract_id: int) -> Dict[str, Any]:
        """Get version statistics for a contract"""
        # Total versions
        total_result = await self.db.execute(
            select(func.count(ContractVersion.id)).where(ContractVersion.contract_id == contract_id)
        )
        total_versions = total_result.scalar() or 0

        # Version types
        type_results = await self.db.execute(
            select(ContractVersion.version_type, func.count(ContractVersion.id))
            .where(ContractVersion.contract_id == contract_id)
            .group_by(ContractVersion.version_type)
        )
        versions_by_type = {row[0]: row[1] for row in type_results}

        # Change statistics
        changes_result = await self.db.execute(
            select(
                func.sum(ContractVersion.additions_count),
                func.sum(ContractVersion.deletions_count),
                func.sum(ContractVersion.modifications_count)
            ).where(ContractVersion.contract_id == contract_id)
        )
        changes = changes_result.first()

        return {
            "total_versions": total_versions,
            "by_type": versions_by_type,
            "total_changes": {
                "additions": changes[0] or 0,
                "deletions": changes[1] or 0,
                "modifications": changes[2] or 0
            }
        }

    async def _get_ai_suggestion_statistics(self, contract_id: int) -> Dict[str, Any]:
        """Get AI suggestion statistics for a contract"""
        # Total suggestions
        total_result = await self.db.execute(
            select(func.count(AISuggestion.id)).where(AISuggestion.contract_id == contract_id)
        )
        total_suggestions = total_result.scalar() or 0

        # Suggestions by status
        status_results = await self.db.execute(
            select(AISuggestion.status, func.count(AISuggestion.id))
            .where(AISuggestion.contract_id == contract_id)
            .group_by(AISuggestion.status)
        )
        suggestions_by_status = {row[0]: row[1] for row in status_results}

        # Suggestions by type
        type_results = await self.db.execute(
            select(AISuggestion.suggestion_type, func.count(AISuggestion.id))
            .where(AISuggestion.contract_id == contract_id)
            .group_by(AISuggestion.suggestion_type)
        )
        suggestions_by_type = {row[0]: row[1] for row in type_results}

        # Average confidence score
        confidence_result = await self.db.execute(
            select(func.avg(AISuggestion.confidence_score))
            .where(AISuggestion.contract_id == contract_id)
            .where(AISuggestion.confidence_score.is_not(None))
        )
        avg_confidence = confidence_result.scalar() or 0.0

        return {
            "total_suggestions": total_suggestions,
            "by_status": suggestions_by_status,
            "by_type": suggestions_by_type,
            "average_confidence": round(avg_confidence, 2),
            "acceptance_rate": suggestions_by_status.get('accepted', 0) / total_suggestions if total_suggestions > 0 else 0
        }

    async def _get_collaboration_statistics(self, contract_id: int) -> Dict[str, Any]:
        """Get collaboration statistics for a contract"""
        # Unique collaborators
        collaborators_result = await self.db.execute(
            select(func.count(func.distinct(PresenceData.user_id)))
            .where(PresenceData.contract_id == contract_id)
        )
        unique_collaborators = collaborators_result.scalar() or 0

        # Active sessions in last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)
        active_sessions_result = await self.db.execute(
            select(func.count(PresenceData.id))
            .where(
                PresenceData.contract_id == contract_id,
                PresenceData.last_seen >= yesterday
            )
        )
        active_sessions = active_sessions_result.scalar() or 0

        return {
            "unique_collaborators": unique_collaborators,
            "active_sessions_24h": active_sessions
        }

    async def _analyze_contract_risks(self, contract: Contract) -> Dict[str, Any]:
        """Analyze contract risks"""
        risks = {
            "overall_score": contract.risk_score or 0.0,
            "completeness_score": contract.completeness_score or 0.0,
            "identified_risks": contract.identified_risks or [],
            "missing_clauses": contract.missing_clauses or [],
            "compliance_issues": contract.compliance_issues or []
        }
        
        # Risk level categorization
        risk_score = risks["overall_score"]
        if risk_score < 0.3:
            risks["risk_level"] = "low"
        elif risk_score < 0.7:
            risks["risk_level"] = "medium"
        else:
            risks["risk_level"] = "high"

        return risks

    async def _get_project_contract_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get contract statistics for a project"""
        # Total contracts
        total_result = await self.db.execute(
            select(func.count(Contract.id)).where(Contract.project_id == project_id)
        )
        total_contracts = total_result.scalar() or 0

        # Contracts by status
        status_results = await self.db.execute(
            select(Contract.status, func.count(Contract.id))
            .where(Contract.project_id == project_id)
            .group_by(Contract.status)
        )
        contracts_by_status = {row[0]: row[1] for row in status_results}

        return {
            "total_contracts": total_contracts,
            "by_status": contracts_by_status
        }

    async def _get_project_activity_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get activity statistics for a project"""
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Comments in last 30 days
        comments_result = await self.db.execute(
            select(func.count(Comment.id))
            .select_from(Comment.join(Contract))
            .where(
                Contract.project_id == project_id,
                Comment.created_at >= thirty_days_ago
            )
        )
        recent_comments = comments_result.scalar() or 0

        # Versions in last 30 days
        versions_result = await self.db.execute(
            select(func.count(ContractVersion.id))
            .select_from(ContractVersion.join(Contract))
            .where(
                Contract.project_id == project_id,
                ContractVersion.created_at >= thirty_days_ago
            )
        )
        recent_versions = versions_result.scalar() or 0

        return {
            "recent_comments": recent_comments,
            "recent_versions": recent_versions
        }

    async def _get_project_contributor_statistics(self, project_id: int) -> List[Dict[str, Any]]:
        """Get top contributors for a project"""
        # Top commenters
        commenters_result = await self.db.execute(
            select(User.id, User.full_name, func.count(Comment.id).label('comment_count'))
            .select_from(Comment.join(Contract).join(User))
            .where(Contract.project_id == project_id)
            .group_by(User.id, User.full_name)
            .order_by(desc('comment_count'))
            .limit(5)
        )
        
        top_contributors = []
        for row in commenters_result:
            top_contributors.append({
                "user_id": row[0],
                "name": row[1],
                "comment_count": row[2]
            })

        return top_contributors

    async def _get_platform_user_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get platform user statistics"""
        # Total users
        total_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0

        # New users in period
        new_users_result = await self.db.execute(
            select(func.count(User.id)).where(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        )
        new_users = new_users_result.scalar() or 0

        # Active users in period
        active_users_result = await self.db.execute(
            select(func.count(func.distinct(PresenceData.user_id)))
            .where(
                PresenceData.last_seen >= start_date,
                PresenceData.last_seen <= end_date
            )
        )
        active_users = active_users_result.scalar() or 0

        return {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": active_users
        }

    async def _get_platform_contract_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get platform contract statistics"""
        # Total contracts
        total_result = await self.db.execute(select(func.count(Contract.id)))
        total_contracts = total_result.scalar() or 0

        # New contracts in period
        new_contracts_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                Contract.created_at >= start_date,
                Contract.created_at <= end_date
            )
        )
        new_contracts = new_contracts_result.scalar() or 0

        return {
            "total_contracts": total_contracts,
            "new_contracts": new_contracts
        }

    async def _get_platform_activity_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get platform activity statistics"""
        # Comments in period
        comments_result = await self.db.execute(
            select(func.count(Comment.id)).where(
                Comment.created_at >= start_date,
                Comment.created_at <= end_date
            )
        )
        comments = comments_result.scalar() or 0

        # Versions in period
        versions_result = await self.db.execute(
            select(func.count(ContractVersion.id)).where(
                ContractVersion.created_at >= start_date,
                ContractVersion.created_at <= end_date
            )
        )
        versions = versions_result.scalar() or 0

        return {
            "comments": comments,
            "versions": versions
        }

    async def _get_platform_ai_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get platform AI usage statistics"""
        # AI suggestions in period
        suggestions_result = await self.db.execute(
            select(func.count(AISuggestion.id)).where(
                AISuggestion.created_at >= start_date,
                AISuggestion.created_at <= end_date
            )
        )
        total_suggestions = suggestions_result.scalar() or 0

        # Accepted suggestions
        accepted_result = await self.db.execute(
            select(func.count(AISuggestion.id)).where(
                AISuggestion.created_at >= start_date,
                AISuggestion.created_at <= end_date,
                AISuggestion.status == 'accepted'
            )
        )
        accepted_suggestions = accepted_result.scalar() or 0

        return {
            "total_suggestions": total_suggestions,
            "accepted_suggestions": accepted_suggestions,
            "acceptance_rate": accepted_suggestions / total_suggestions if total_suggestions > 0 else 0
        }
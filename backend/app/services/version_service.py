"""
Version service for contract version control
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime
import difflib

from app.models.version import ContractVersion
from app.models.contract import Contract
from app.models.user import User
from app.schemas.version import (
    ContractVersionCreate, ContractVersionUpdate, ContractVersionResponse,
    ContractVersionDiff, ContractVersionApproval
)
from app.schemas.user import UserResponse

class VersionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_version(self, version_data: ContractVersionCreate, user_id: int) -> ContractVersionResponse:
        """Create a new contract version"""
        # Get current contract to compare changes
        contract_result = await self.db.execute(
            select(Contract).where(Contract.id == version_data.contract_id)
        )
        contract = contract_result.scalar_one_or_none()
        
        if not contract:
            raise ValueError("Contract not found")

        # Calculate changes between versions
        changes = self._calculate_changes(contract.content, version_data.content)
        
        db_version = ContractVersion(
            contract_id=version_data.contract_id,
            version_number=version_data.version_number,
            content=version_data.content,
            changes=version_data.changes or changes,
            change_summary=version_data.change_summary,
            created_by_id=user_id,
            version_type=version_data.version_type,
            is_major_version=version_data.is_major_version,
            requires_approval=version_data.requires_approval,
            tags=version_data.tags,
            release_notes=version_data.release_notes,
            additions_count=changes.get('additions_count', 0),
            deletions_count=changes.get('deletions_count', 0),
            modifications_count=changes.get('modifications_count', 0)
        )
        
        self.db.add(db_version)
        await self.db.commit()
        await self.db.refresh(db_version)
        
        # Update contract with new content and version
        await self.db.execute(
            update(Contract)
            .where(Contract.id == version_data.contract_id)
            .values(
                content=version_data.content,
                version=version_data.version_number,
                updated_at=func.now()
            )
        )
        await self.db.commit()
        
        return await self.get_version_by_id(db_version.id)

    async def get_version_by_id(self, version_id: int) -> Optional[ContractVersionResponse]:
        """Get version by ID with relationships"""
        result = await self.db.execute(
            select(ContractVersion)
            .options(
                selectinload(ContractVersion.created_by),
                selectinload(ContractVersion.approved_by)
            )
            .where(ContractVersion.id == version_id)
        )
        version = result.scalar_one_or_none()
        
        if not version:
            return None
            
        response = ContractVersionResponse.model_validate(version)
        
        if version.created_by:
            response.created_by = UserResponse.model_validate(version.created_by)
        if version.approved_by:
            response.approved_by = UserResponse.model_validate(version.approved_by)
        
        return response

    async def get_versions_by_contract(self, contract_id: int, skip: int = 0, limit: int = 100) -> List[ContractVersionResponse]:
        """Get versions by contract ID"""
        result = await self.db.execute(
            select(ContractVersion)
            .options(
                selectinload(ContractVersion.created_by),
                selectinload(ContractVersion.approved_by)
            )
            .where(ContractVersion.contract_id == contract_id)
            .offset(skip)
            .limit(limit)
            .order_by(ContractVersion.created_at.desc())
        )
        versions = result.scalars().all()
        
        responses = []
        for version in versions:
            response = ContractVersionResponse.model_validate(version)
            if version.created_by:
                response.created_by = UserResponse.model_validate(version.created_by)
            if version.approved_by:
                response.approved_by = UserResponse.model_validate(version.approved_by)
            responses.append(response)
        
        return responses

    async def update_version(self, version_id: int, version_data: ContractVersionUpdate, user_id: int) -> Optional[ContractVersionResponse]:
        """Update version metadata"""
        update_data = version_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_version_by_id(version_id)

        await self.db.execute(
            update(ContractVersion)
            .where(ContractVersion.id == version_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_version_by_id(version_id)

    async def delete_version(self, version_id: int, user_id: int) -> bool:
        """Delete version (only creator can delete)"""
        version = await self.get_version_by_id(version_id)
        if not version or version.created_by_id != user_id:
            return False

        await self.db.execute(delete(ContractVersion).where(ContractVersion.id == version_id))
        await self.db.commit()
        return True

    async def approve_version(self, version_id: int, approval: ContractVersionApproval, user_id: int) -> Optional[ContractVersionResponse]:
        """Approve or reject a version"""
        update_data = {
            'approved_by_id': user_id,
            'approved_at': func.now()
        }
        
        if approval.approval_notes:
            update_data['release_notes'] = approval.approval_notes

        await self.db.execute(
            update(ContractVersion)
            .where(ContractVersion.id == version_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_version_by_id(version_id)

    async def compare_versions(self, base_version_id: int, compare_version_id: int) -> ContractVersionDiff:
        """Compare two versions and return differences"""
        # Get both versions
        base_result = await self.db.execute(
            select(ContractVersion).where(ContractVersion.id == base_version_id)
        )
        base_version = base_result.scalar_one_or_none()
        
        compare_result = await self.db.execute(
            select(ContractVersion).where(ContractVersion.id == compare_version_id)
        )
        compare_version = compare_result.scalar_one_or_none()
        
        if not base_version or not compare_version:
            raise ValueError("One or both versions not found")

        # Calculate differences
        base_lines = base_version.content.splitlines()
        compare_lines = compare_version.content.splitlines()
        
        differ = difflib.unified_diff(
            base_lines,
            compare_lines,
            fromfile=f"Version {base_version.version_number}",
            tofile=f"Version {compare_version.version_number}",
            lineterm=""
        )
        
        additions = []
        deletions = []
        modifications = []
        
        for line in differ:
            if line.startswith('+') and not line.startswith('+++'):
                additions.append({"text": line[1:], "line_number": len(additions) + 1})
            elif line.startswith('-') and not line.startswith('---'):
                deletions.append({"text": line[1:], "line_number": len(deletions) + 1})
            elif line.startswith('@@'):
                modifications.append({"context": line})

        summary = f"Comparing version {base_version.version_number} to {compare_version.version_number}: "
        summary += f"{len(additions)} additions, {len(deletions)} deletions, {len(modifications)} modifications"

        return ContractVersionDiff(
            additions=additions,
            deletions=deletions,
            modifications=modifications,
            summary=summary,
            statistics={
                "additions_count": len(additions),
                "deletions_count": len(deletions),
                "modifications_count": len(modifications),
                "total_changes": len(additions) + len(deletions) + len(modifications)
            }
        )

    def _calculate_changes(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Calculate changes between two content versions"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        differ = difflib.unified_diff(old_lines, new_lines, lineterm="")
        
        additions_count = 0
        deletions_count = 0
        modifications_count = 0
        
        for line in differ:
            if line.startswith('+') and not line.startswith('+++'):
                additions_count += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions_count += 1
            elif line.startswith('@@'):
                modifications_count += 1

        return {
            "additions_count": additions_count,
            "deletions_count": deletions_count,
            "modifications_count": modifications_count,
            "changes": list(difflib.unified_diff(old_lines, new_lines, lineterm=""))[:100]  # Limit for storage
        }
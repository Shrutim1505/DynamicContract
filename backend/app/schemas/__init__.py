"""
Pydantic schemas for request/response models
"""
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserLogin
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.contract import ContractCreate, ContractResponse, ContractUpdate
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.ai_suggestion import AISuggestionCreate, AISuggestionResponse
from app.schemas.version import ContractVersionCreate, ContractVersionResponse
from app.schemas.presence import PresenceDataCreate, PresenceDataResponse

__all__ = [
    "UserCreate", "UserResponse", "UserUpdate", "UserLogin",
    "ProjectCreate", "ProjectResponse", "ProjectUpdate",
    "ContractCreate", "ContractResponse", "ContractUpdate",
    "CommentCreate", "CommentResponse", "CommentUpdate",
    "AISuggestionCreate", "AISuggestionResponse",
    "ContractVersionCreate", "ContractVersionResponse",
    "PresenceDataCreate", "PresenceDataResponse"
]
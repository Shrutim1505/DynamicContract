"""
Security schemas for authentication
"""
from pydantic import BaseModel

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
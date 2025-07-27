"""
Pydantic schemas for ClariFlow API models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4

# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    picture: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = None
    picture: Optional[str] = None

class UserInDB(UserBase):
    """Schema for user data in database."""
    id: UUID4
    created_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """Schema for user response."""
    pass

# Chat History Schemas
class ChatHistoryBase(BaseModel):
    """Base chat history schema."""
    message: str
    response: str
    session_id: Optional[str] = None
    document_id: Optional[str] = None
    source: Optional[str] = None

class ChatHistoryCreate(ChatHistoryBase):
    """Schema for creating new chat history entry."""
    user_id: UUID4

class ChatHistoryUpdate(BaseModel):
    """Schema for updating chat history entry."""
    message: Optional[str] = None
    response: Optional[str] = None
    session_id: Optional[str] = None
    document_id: Optional[str] = None
    source: Optional[str] = None

class ChatHistoryInDB(ChatHistoryBase):
    """Schema for chat history data in database."""
    id: UUID4
    user_id: UUID4
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatHistoryResponse(ChatHistoryInDB):
    """Schema for chat history response."""
    pass

# Chat History with User Info
class ChatHistoryWithUser(ChatHistoryResponse):
    """Schema for chat history with user information."""
    user: UserResponse

# Pagination Schemas
class PaginatedResponse(BaseModel):
    """Base schema for paginated responses."""
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int

class ChatHistoryPaginated(PaginatedResponse):
    """Schema for paginated chat history."""
    items: List[ChatHistoryResponse]

# Google OAuth Schemas
class GoogleUserInfo(BaseModel):
    """Schema for Google OAuth user information."""
    email: str
    name: str
    picture: Optional[str] = None
    sub: str
    email_verified: bool = True

# API Response Schemas
class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None

# Health Check Schema
class HealthCheck(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: datetime
    database: str
    version: str = "2.0.0" 
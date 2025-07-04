from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

# SQLAlchemy Database Models
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    document_id = Column(String, nullable=True)
    source = Column(String, nullable=True)  # "document" or "openai"
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")

# Pydantic Models for API
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    history: Optional[List[str]] = []  # Chat history as list of strings

class ChatResponse(BaseModel):
    response: str
    source: str  # 'document' or 'openai' to indicate the source
    sources: Optional[List[str]] = None  # Document chunks if using document source
    document_id: Optional[str] = None
    timestamp: datetime
    session_id: Optional[str] = None
    # Debug metadata (stretch goal)
    used_context: Optional[bool] = None
    matched_chunks: Optional[List[str]] = None
    relevance_score: Optional[float] = None

class ChatMessageResponse(BaseModel):
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    document_id: Optional[str] = None
    source: Optional[str] = None  # 'document' or 'openai'

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"

class UpdateSessionRequest(BaseModel):
    title: str 
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..models.chat import ChatSession, ChatMessage, ChatSessionResponse, ChatMessageResponse
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ChatMemoryService:
    """Service for managing chat sessions and message history."""
    
    def create_session(self, db: Session, title: str = "New Chat", user_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session with optional user ownership."""
        try:
            session = ChatSession(
                id=str(uuid.uuid4()),
                title=title,
                user_id=user_id
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            logger.info(f"Created new chat session: {session.id} for user {user_id}")
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating chat session: {str(e)}")
            raise
    
    def get_session(self, db: Session, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        try:
            return db.query(ChatSession).filter(ChatSession.id == session_id).first()
        except Exception as e:
            logger.error(f"Error getting chat session {session_id}: {str(e)}")
            raise
    
    def get_all_sessions(self, db: Session, user_id: Optional[str] = None) -> List[ChatSessionResponse]:
        """
        Get all chat sessions with message counts, optionally filtered by user.
        
        Args:
            db: Database session
            user_id: Optional user ID to filter sessions
            
        Returns:
            List of chat sessions with metadata
        """
        try:
            query = db.query(ChatSession).order_by(desc(ChatSession.updated_at))
            
            # Filter by user if provided
            if user_id:
                # Note: This assumes sessions are linked to users via a user_id field
                # You may need to add this field to the ChatSession model
                query = query.filter(ChatSession.user_id == user_id)
            
            sessions = query.all()
            session_responses = []
            
            for session in sessions:
                message_count = len(session.messages)
                session_response = ChatSessionResponse(
                    id=session.id,
                    title=session.title,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    message_count=message_count
                )
                session_responses.append(session_response)
            
            return session_responses
        except Exception as e:
            logger.error(f"Error getting all sessions: {str(e)}")
            raise
    
    def update_session_title(self, db: Session, session_id: str, title: str) -> Optional[ChatSession]:
        """Update the title of a chat session."""
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                session.title = title
                session.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(session)
                logger.info(f"Updated session title: {session_id} -> {title}")
                return session
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating session title: {str(e)}")
            raise
    
    def delete_session(self, db: Session, session_id: str) -> bool:
        """Delete a chat session and all its messages."""
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
                logger.info(f"Deleted chat session: {session_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            raise
    
    def add_message(self, db: Session, session_id: str, role: str, message: str, 
                   document_id: Optional[str] = None, source: Optional[str] = None) -> ChatMessage:
        """Add a message to a chat session."""
        try:
            # Create session if it doesn't exist
            session = self.get_session(db, session_id)
            if not session:
                session = self.create_session(db)
                session_id = session.id
            
            # Add the message
            chat_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                message=message,
                document_id=document_id,
                source=source
            )
            db.add(chat_message)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            
            # Auto-generate title from first user message if it's still "New Chat"
            if session.title == "New Chat" and role == "user":
                # Use first 50 characters of the message as title
                title = message[:50].strip()
                if len(message) > 50:
                    title += "..."
                session.title = title
            
            db.commit()
            db.refresh(chat_message)
            logger.info(f"Added message to session {session_id}: {role}")
            return chat_message
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding message to session {session_id}: {str(e)}")
            raise
    
    def get_session_messages(self, db: Session, session_id: str) -> List[ChatMessageResponse]:
        """Get all messages from a chat session in chronological order."""
        try:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp).all()
            
            message_responses = []
            for message in messages:
                message_response = ChatMessageResponse(
                    id=message.id,
                    role=message.role,
                    content=message.message,
                    timestamp=message.timestamp,
                    document_id=message.document_id,
                    source=message.source
                )
                message_responses.append(message_response)
            
            return message_responses
        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {str(e)}")
            raise
    
    def get_session_history(self, db: Session, session_id: str) -> List[str]:
        """Get chat history as a list of strings for the chat service."""
        try:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp).all()
            
            history = []
            for message in messages:
                history.append(f"{message.role}: {message.message}")
            
            return history
        except Exception as e:
            logger.error(f"Error getting history for session {session_id}: {str(e)}")
            raise 
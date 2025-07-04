from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.chat import (
    ChatRequest, ChatResponse, ChatSessionResponse, ChatMessageResponse,
    CreateSessionRequest, UpdateSessionRequest
)
from ..services.chat_service import ChatService
from ..services.chat_memory import ChatMemoryService
from ..core.database import get_db
from ..core.security import get_current_user, get_current_active_user
from ..middleware.security import rate_limit_per_minute
from ..models.user import User
from ..utils.logger import setup_logger

router = APIRouter()
chat_service = ChatService()
chat_memory_service = ChatMemoryService()
logger = setup_logger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Handle universal chatbot queries with session support.
    
    Args:
        request: ChatRequest with query, optional session_id, and optional history
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ChatResponse with response, source, session_id, and optional metadata
    """
    try:
        logger.info(f"Universal chat request received from user {current_user.email}: query='{request.query[:50]}...', session_id={request.session_id}")
        
        # Validate request
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # Get session history if session_id is provided
        history = request.history
        if request.session_id:
            history = chat_memory_service.get_session_history(db, request.session_id)
        
        # Process universal chat request
        result = await chat_service.chat(query=request.query, history=history)
        
        # Save messages to database
        session_id = request.session_id
        if not session_id:
            # Create new session if none provided
            session = chat_memory_service.create_session(db)
            session_id = session.id
        
        # Save user message
        chat_memory_service.add_message(
            db=db,
            session_id=session_id,
            role="user",
            message=request.query,
            document_id=result.get("document_id"),
            source=result.get("source")
        )
        
        # Save assistant message
        chat_memory_service.add_message(
            db=db,
            session_id=session_id,
            role="assistant",
            message=result["response"],
            document_id=result.get("document_id"),
            source=result.get("source")
        )
        
        # Create response
        response = ChatResponse(
            response=result["response"],
            source=result["source"],
            sources=result["sources"],
            document_id=result["document_id"],
            timestamp=result["timestamp"],
            session_id=session_id,
            used_context=result["used_context"],
            matched_chunks=result["matched_chunks"],
            relevance_score=result["relevance_score"]
        )
        
        # Log the response details
        context_used = "with document context" if result["used_context"] else "as general chat"
        logger.info(f"Universal chat response generated successfully for user {current_user.email}: {context_used}, session_id={session_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in universal chat endpoint for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing chat request"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all chat sessions for the current user.
    
    Returns:
        List of chat sessions with metadata
    """
    try:
        sessions = chat_memory_service.get_all_sessions(db)
        logger.info(f"Retrieved {len(sessions)} chat sessions for user {current_user.email}")
        return sessions
    except Exception as e:
        logger.error(f"Error getting sessions for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting sessions"
        )

@router.get("/sessions/{session_id}", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all messages from a specific chat session.
    
    Args:
        session_id: The ID of the chat session
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of messages in chronological order
    """
    try:
        # Check if session exists
        session = chat_memory_service.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )
        
        messages = chat_memory_service.get_session_messages(db, session_id)
        logger.info(f"Retrieved {len(messages)} messages from session {session_id} for user {current_user.email}")
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session messages for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting session messages"
        )

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    request: CreateSessionRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new chat session.
    
    Args:
        request: CreateSessionRequest with optional title
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created chat session
    """
    try:
        session = chat_memory_service.create_session(db, request.title)
        session_response = ChatSessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0
        )
        logger.info(f"Created new chat session {session.id} for user {current_user.email}")
        return session_response
    except Exception as e:
        logger.error(f"Error creating session for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating session"
        )

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_session(
    session_id: str, 
    request: UpdateSessionRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the title of a chat session.
    
    Args:
        session_id: The ID of the chat session
        request: UpdateSessionRequest with new title
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated chat session
    """
    try:
        session = chat_memory_service.update_session_title(db, session_id, request.title)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )
        
        session_response = ChatSessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=chat_memory_service.get_session_message_count(db, session_id)
        )
        
        logger.info(f"Updated chat session {session_id} for user {current_user.email}")
        return session_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating session"
        )

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a chat session and all its messages.
    
    Args:
        session_id: The ID of the chat session
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Check if session exists
        session = chat_memory_service.get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )
        
        # Delete session and all messages
        chat_memory_service.delete_session(db, session_id)
        
        logger.info(f"Deleted chat session {session_id} for user {current_user.email}")
        return {"message": "Chat session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting session"
        )

@router.get("/documents")
async def get_available_documents(current_user: User = Depends(get_current_active_user)):
    """
    Get list of available documents for chat context.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        List of available documents
    """
    try:
        # This would typically return documents available to the current user
        # For now, returning a placeholder response
        logger.info(f"Document list requested by user {current_user.email}")
        return {
            "documents": [],
            "message": "No documents available"
        }
    except Exception as e:
        logger.error(f"Error getting documents for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting documents"
        ) 
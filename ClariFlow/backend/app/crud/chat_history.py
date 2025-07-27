"""
CRUD operations for ChatHistory model.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..core.database import ChatHistory
from ..schemas import ChatHistoryCreate, ChatHistoryUpdate
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

async def create_chat_history(db: AsyncSession, chat_data: ChatHistoryCreate) -> ChatHistory:
    """
    Create a new chat history entry.
    
    Args:
        db: Async database session
        chat_data: Chat history creation data
        
    Returns:
        Created ChatHistory object
    """
    try:
        db_chat = ChatHistory(
            user_id=chat_data.user_id,
            message=chat_data.message,
            response=chat_data.response,
            session_id=chat_data.session_id,
            document_id=chat_data.document_id,
            source=chat_data.source,
            timestamp=datetime.utcnow()
        )
        db.add(db_chat)
        await db.commit()
        await db.refresh(db_chat)
        
        logger.info(f"Created chat history entry for user {chat_data.user_id}")
        return db_chat
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating chat history for user {chat_data.user_id}: {str(e)}")
        raise

async def get_chat_history_by_user(
    db: AsyncSession, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> List[ChatHistory]:
    """
    Get chat history for a specific user with pagination.
    
    Args:
        db: Async database session
        user_id: User's UUID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatHistory objects
    """
    try:
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting chat history for user {user_id}: {str(e)}")
        raise

async def get_chat_history_by_session(
    db: AsyncSession, 
    session_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[ChatHistory]:
    """
    Get chat history for a specific session with pagination.
    
    Args:
        db: Async database session
        session_id: Session ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatHistory objects
    """
    try:
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.timestamp.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting chat history for session {session_id}: {str(e)}")
        raise

async def get_chat_history_by_id(db: AsyncSession, chat_id: UUID) -> Optional[ChatHistory]:
    """
    Get chat history entry by ID.
    
    Args:
        db: Async database session
        chat_id: Chat history entry UUID
        
    Returns:
        ChatHistory object if found, None otherwise
    """
    try:
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.id == chat_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting chat history by ID {chat_id}: {str(e)}")
        raise

async def update_chat_history(
    db: AsyncSession, 
    chat_id: UUID, 
    chat_data: ChatHistoryUpdate
) -> Optional[ChatHistory]:
    """
    Update a chat history entry.
    
    Args:
        db: Async database session
        chat_id: Chat history entry UUID
        chat_data: Update data
        
    Returns:
        Updated ChatHistory object if found, None otherwise
    """
    try:
        chat_entry = await get_chat_history_by_id(db, chat_id)
        if not chat_entry:
            return None
        
        # Update fields if provided
        if chat_data.message is not None:
            chat_entry.message = chat_data.message
        if chat_data.response is not None:
            chat_entry.response = chat_data.response
        if chat_data.session_id is not None:
            chat_entry.session_id = chat_data.session_id
        if chat_data.document_id is not None:
            chat_entry.document_id = chat_data.document_id
        if chat_data.source is not None:
            chat_entry.source = chat_data.source
        
        await db.commit()
        await db.refresh(chat_entry)
        
        logger.info(f"Updated chat history entry {chat_id}")
        return chat_entry
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating chat history {chat_id}: {str(e)}")
        raise

async def delete_chat_history(db: AsyncSession, chat_id: UUID) -> bool:
    """
    Delete a chat history entry by ID.
    
    Args:
        db: Async database session
        chat_id: Chat history entry UUID
        
    Returns:
        True if entry was deleted, False otherwise
    """
    try:
        chat_entry = await get_chat_history_by_id(db, chat_id)
        if chat_entry:
            await db.delete(chat_entry)
            await db.commit()
            logger.info(f"Deleted chat history entry {chat_id}")
            return True
        return False
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting chat history {chat_id}: {str(e)}")
        raise

async def delete_chat_history_by_user(db: AsyncSession, user_id: UUID) -> int:
    """
    Delete all chat history for a specific user.
    
    Args:
        db: Async database session
        user_id: User's UUID
        
    Returns:
        Number of deleted entries
    """
    try:
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        chat_entries = result.scalars().all()
        
        for entry in chat_entries:
            await db.delete(entry)
        
        await db.commit()
        deleted_count = len(chat_entries)
        logger.info(f"Deleted {deleted_count} chat history entries for user {user_id}")
        return deleted_count
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting chat history for user {user_id}: {str(e)}")
        raise

async def delete_chat_history_by_session(db: AsyncSession, session_id: str) -> int:
    """
    Delete all chat history for a specific session.
    
    Args:
        db: Async database session
        session_id: Session ID
        
    Returns:
        Number of deleted entries
    """
    try:
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.session_id == session_id)
        )
        chat_entries = result.scalars().all()
        
        for entry in chat_entries:
            await db.delete(entry)
        
        await db.commit()
        deleted_count = len(chat_entries)
        logger.info(f"Deleted {deleted_count} chat history entries for session {session_id}")
        return deleted_count
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting chat history for session {session_id}: {str(e)}")
        raise

async def get_chat_history_count_by_user(db: AsyncSession, user_id: UUID) -> int:
    """
    Get the total count of chat history entries for a user.
    
    Args:
        db: Async database session
        user_id: User's UUID
        
    Returns:
        Total count of chat history entries
    """
    try:
        result = await db.execute(
            select(func.count(ChatHistory.id)).where(ChatHistory.user_id == user_id)
        )
        return result.scalar()
    except Exception as e:
        logger.error(f"Error getting chat history count for user {user_id}: {str(e)}")
        raise

async def get_chat_history_with_user(
    db: AsyncSession, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> List[ChatHistory]:
    """
    Get chat history with user information for a specific user.
    
    Args:
        db: Async database session
        user_id: User's UUID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ChatHistory objects with user information
    """
    try:
        result = await db.execute(
            select(ChatHistory)
            .options(selectinload(ChatHistory.user))
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting chat history with user for {user_id}: {str(e)}")
        raise 
"""
CRUD operations for User model.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..core.database import User
from ..schemas import UserCreate
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email address.
    
    Args:
        db: Async database session
        email: User's email address
        
    Returns:
        User object if found, None otherwise
    """
    try:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {str(e)}")
        raise

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Get user by ID.
    
    Args:
        db: Async database session
        user_id: User's UUID
        
    Returns:
        User object if found, None otherwise
    """
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {str(e)}")
        raise

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user.
    
    Args:
        db: Async database session
        user_data: User creation data
        
    Returns:
        Created User object
    """
    try:
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            picture=user_data.picture,
            created_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"Created new user: {db_user.email}")
        return db_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user {user_data.email}: {str(e)}")
        raise

async def update_user_last_seen(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Update user's last seen timestamp.
    
    Args:
        db: Async database session
        user_id: User's UUID
        
    Returns:
        Updated User object if found, None otherwise
    """
    try:
        result = await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_seen=datetime.utcnow())
            .returning(User)
        )
        updated_user = result.scalar_one_or_none()
        
        if updated_user:
            await db.commit()
            logger.debug(f"Updated last_seen for user {user_id}")
        
        return updated_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating last_seen for user {user_id}: {str(e)}")
        raise

async def upsert_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create or update user (upsert operation).
    
    Args:
        db: Async database session
        user_data: User data
        
    Returns:
        User object (created or updated)
    """
    try:
        # Try to get existing user
        existing_user = await get_user_by_email(db, user_data.email)
        
        if existing_user:
            # Update last_seen and other fields if needed
            existing_user.last_seen = datetime.utcnow()
            if user_data.name != existing_user.name:
                existing_user.name = user_data.name
            if user_data.picture != existing_user.picture:
                existing_user.picture = user_data.picture
            
            await db.commit()
            await db.refresh(existing_user)
            
            logger.info(f"Updated existing user: {existing_user.email}")
            return existing_user
        else:
            # Create new user
            return await create_user(db, user_data)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error upserting user {user_data.email}: {str(e)}")
        raise

async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get all users with pagination.
    
    Args:
        db: Async database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of User objects
    """
    try:
        result = await db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise

async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """
    Delete a user by ID.
    
    Args:
        db: Async database session
        user_id: User's UUID
        
    Returns:
        True if user was deleted, False otherwise
    """
    try:
        user = await get_user_by_id(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
            logger.info(f"Deleted user: {user.email}")
            return True
        return False
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise 
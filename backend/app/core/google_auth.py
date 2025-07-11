"""
Google OAuth authentication module for ClariFlow backend.
Handles Google access token verification and user authentication.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..utils.logger import setup_logger
from ..core.database import get_db
from ..core.config import settings
from ..models.user import User

logger = setup_logger(__name__)

class GoogleUserInfo(BaseModel):
    """Google user information from verified token."""
    email: str
    name: str
    picture: Optional[str] = None
    sub: str  # Google user ID
    email_verified: bool = True

class GoogleAuthManager:
    """Manager for Google OAuth authentication."""
    
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not self.google_client_id:
            logger.warning("GOOGLE_CLIENT_ID not set. Google OAuth will not work properly.")
    
    async def verify_google_token(self, token: str) -> GoogleUserInfo:
        """
        Verify Google access token and return user information.
        
        Args:
            token: Google access token from Authorization header
            
        Returns:
            GoogleUserInfo: Verified user information
            
        Raises:
            HTTPException: If token is invalid or verification fails
        """
        try:
            if not self.google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Google OAuth not configured",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.google_client_id
            )
            
            # Extract user information
            user_info = GoogleUserInfo(
                email=idinfo.get('email', ''),
                name=idinfo.get('name', ''),
                picture=idinfo.get('picture'),
                sub=idinfo.get('sub', ''),
                email_verified=idinfo.get('email_verified', False)
            )
            
            logger.info(f"Google token verified successfully for user: {user_info.email}")
            return user_info
            
        except GoogleAuthError as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification error",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Global instance
google_auth_manager = GoogleAuthManager()

async def get_current_user_from_google_token(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract and verify Google access token.
    Also upserts user information to the database.
    
    Args:
        request: FastAPI request object
        db: Async database session
        
    Returns:
        UserResponse: User information from database
        
    Raises:
        HTTPException: If token is missing, invalid, or verification fails
    """
    # Extract Bearer token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if it's a Bearer token
    if not auth_header.lower().startswith("bearer "):
        logger.warning("Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the token
    token = auth_header.split(" ", 1)[1]
    if not token:
        logger.warning("Empty token in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the token and get user info
    google_user_info = await google_auth_manager.verify_google_token(token)
    
    # Get or create user in database
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == google_user_info.email).first()
        
        if not user:
            # Create new user - Google OAuth users don't need a password
            user = User(
                email=google_user_info.email,
                full_name=google_user_info.name,
                hashed_password="",  # Empty password for OAuth users
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New Google OAuth user created: {user.email}")
        else:
            # Update existing user's name if provided and different
            if google_user_info.name and str(user.full_name) != google_user_info.name:
                user.full_name = google_user_info.name
                db.commit()
                db.refresh(user)
            logger.info(f"Existing Google OAuth user authenticated: {user.email}")
        
        return user
        
    except Exception as e:
        logger.error(f"Error processing Google OAuth user {google_user_info.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user authentication",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
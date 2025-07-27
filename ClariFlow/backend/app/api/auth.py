"""
Authentication API endpoints for ClariFlow backend.
Handles user registration, login, token refresh, and user management.
"""

from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..core.database import get_db
from ..core.security import security_manager, get_current_user, get_current_superuser
from ..core.google_auth import get_current_user_from_google_token
from ..services.email_service import email_service
from ..models.user import (
    User, UserCreate, UserResponse, UserUpdate, PasswordChange, EmailVerificationRequest, ResendVerificationRequest
)
from ..utils.logger import setup_logger
from ..middleware.security import rate_limit_per_minute
from ..core.config import settings
import time

# In-memory brute-force protection (for production, use Redis or DB)
FAILED_LOGIN_ATTEMPTS = {}
LOCKED_ACCOUNTS = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 15 * 60  # 15 minutes
LOCKOUT_DURATION_SECONDS = 15 * 60  # 15 minutes

router = APIRouter()
logger = setup_logger(__name__)

class GoogleTokenRequest(BaseModel):
    """Model for Google OAuth token request."""
    access_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@rate_limit_per_minute(5)
async def register_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        # Check if user already exists
        if user_data.email is None:
            raise HTTPException(status_code=400, detail="Email is required")
        existing_user = security_manager.get_user_by_email(db, str(user_data.email))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = security_manager.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Generate verification token
        verification_token = security_manager.generate_verification_token(user)
        # Set email_verification_token using setattr
        setattr(user, 'email_verification_token', verification_token)
        db.commit()
        db.refresh(user)
        
        # Send verification email (optional - will work even if email not configured)
        verification_url = f"{settings.FRONTEND_BASE_URL}/verify-email"
        email_service.send_verification_email(str(user.email), verification_token, verification_url)
        
        logger.info(f"New user registered: {user.email}")
        
        # Fail fast if required fields are missing
        if not hasattr(user, 'id') or user.id is None:
            raise HTTPException(status_code=500, detail="User ID missing after registration")
        if not hasattr(user, 'email') or user.email is None:
            raise HTTPException(status_code=500, detail="User email missing after registration")
        if not hasattr(user, 'created_at') or user.created_at is None:
            raise HTTPException(status_code=500, detail="User created_at missing after registration")
        return {"user": UserResponse.model_validate(user), "message": "Registration successful"}
        
    except HTTPException as exc:
        if exc.status_code == 429:
            logger.warning(f"Rate limit exceeded for registration from {request.client.host if request and request.client else 'unknown'}")
        raise
    except ValueError as e:
        logger.error(f"Validation error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Catch-all for unexpected errors (should be rare)
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=UserResponse)
@rate_limit_per_minute(10)
async def login_user(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return user info with HttpOnly cookies.
    
    Args:
        form_data: OAuth2 password form data
        db: Database session
        response: FastAPI response object for setting cookies
        
    Returns:
        User information with cookies set
        
    Raises:
        HTTPException: If authentication fails
    """
    email = form_data.username.lower()
    now = time.time()
    # Check if account is locked
    lock_info = LOCKED_ACCOUNTS.get(email)
    if lock_info and now < lock_info['until']:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked due to repeated failed logins. Try again in {int((lock_info['until']-now)//60)+1} minutes."
        )
    try:
        # Authenticate user
        user = security_manager.authenticate_user(
            db, email, form_data.password
        )
        if not user:
            # Track failed attempts
            attempts = FAILED_LOGIN_ATTEMPTS.get(email, [])
            # Remove old attempts
            attempts = [t for t in attempts if now - t < LOCKOUT_WINDOW_SECONDS]
            attempts.append(now)
            FAILED_LOGIN_ATTEMPTS[email] = attempts
            if len(attempts) >= MAX_FAILED_ATTEMPTS:
                LOCKED_ACCOUNTS[email] = {'until': now + LOCKOUT_DURATION_SECONDS}
                FAILED_LOGIN_ATTEMPTS[email] = []
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account locked due to repeated failed logins. Try again in {LOCKOUT_DURATION_SECONDS//60} minutes."
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Reset failed attempts on success
        FAILED_LOGIN_ATTEMPTS[email] = []
        if email in LOCKED_ACCOUNTS:
            del LOCKED_ACCOUNTS[email]
        if getattr(user, "is_active", True) is not True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=security_manager.access_token_expire_minutes)
        access_token = security_manager.create_access_token(
            data={"sub": user.email, "user_id": user.id, "is_superuser": user.is_superuser},
            expires_delta=access_token_expires
        )
        
        refresh_token = security_manager.create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Set HttpOnly cookies
        if response:
            security_manager.set_auth_cookies(response, access_token, refresh_token)
        
        logger.info(f"User logged in successfully: {user.email}")
        
        db.refresh(user)
        if not hasattr(user, 'id') or user.id is None:
            raise HTTPException(status_code=500, detail="User ID missing after login")
        if not hasattr(user, 'email') or user.email is None:
            raise HTTPException(status_code=500, detail="User email missing after login")
        if not hasattr(user, 'created_at') or user.created_at is None:
            raise HTTPException(status_code=500, detail="User created_at missing after login")
        return {"user": UserResponse.model_validate(user), "message": "Login successful"}
        
    except HTTPException as exc:
        if exc.status_code == 429:
            logger.warning(f"Rate limit exceeded for login from {request.client.host if request and request.client else 'unknown'}")
        elif exc.status_code == 401:
            logger.warning(f"Failed login for {email} from {request.client.host if request and request.client else 'unknown'}")
        raise
    except ValueError as e:
        logger.error(f"Validation error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Catch-all for unexpected errors (should be rare)
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/logout")
async def logout_user(response: Response):
    """
    Logout user by clearing authentication cookies.
    
    Args:
        response: FastAPI response object for clearing cookies
        
    Returns:
        Success message
    """
    security_manager.clear_auth_cookies(response)
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=UserResponse)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Refresh access token using refresh token from cookies.
    
    Args:
        request: FastAPI request object
        db: Database session
        response: FastAPI response object for setting cookies
        
    Returns:
        User information with new cookies set
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Get refresh token from cookies
        refresh_token = security_manager.get_refresh_token_from_cookies(request)
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify refresh token
        token_data = security_manager.verify_token(refresh_token)
        user = security_manager.get_user_by_email(db, token_data.email)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=security_manager.access_token_expire_minutes)
        access_token = security_manager.create_access_token(
            data={"sub": user.email, "user_id": user.id, "is_superuser": user.is_superuser},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        new_refresh_token = security_manager.create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Set new HttpOnly cookies
        if response:
            security_manager.set_auth_cookies(response, access_token, new_refresh_token)
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=bool(user.is_active),
            is_superuser=bool(user.is_superuser),
            is_email_verified=bool(user.is_email_verified),
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email address using verification token.
    
    Args:
        verification_data: Email verification request
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If verification token is invalid
    """
    try:
        # Verify token
        token_data = security_manager.verify_verification_token(verification_data.token)
        
        # Get user
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        # Verify email
        setattr(user, 'is_email_verified', True)
        setattr(user, 'email_verification_token', None)
        db.commit()
        
        logger.info(f"Email verified for user: {user.email}")
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during email verification"
        )

@router.post("/resend-verification")
async def resend_verification_email(
    verification_data: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend email verification email.
    
    Args:
        verification_data: Resend verification request
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or already verified
    """
    try:
        # Get user
        user = security_manager.get_user_by_email(db, verification_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Generate new verification token
        verification_token = security_manager.generate_verification_token(user)
        setattr(user, 'email_verification_token', verification_token)
        db.commit()
        db.refresh(user)
        
        # Send verification email
        verification_url = f"{settings.FRONTEND_BASE_URL}/verify-email"
        email_service.send_verification_email(str(user.email), verification_token, verification_url)
        
        logger.info(f"Verification email resent to: {user.email}")
        
        return {"message": "Verification email sent"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    
    Args:
        user_data: Updated user data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    try:
        # Update user fields
        if user_data.email is not None:
            # Check if email is already taken by another user
            existing_user = security_manager.get_user_by_email(db, user_data.email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
            current_user.email = user_data.email
        
        if user_data.full_name is not None:
            current_user.full_name = user_data.full_name
        
        if user_data.is_active is not None:
            current_user.is_active = user_data.is_active
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User updated: {current_user.email}")
        
        return UserResponse.model_validate(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user update"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If current password is incorrect
    """
    try:
        # Verify current password
        if not security_manager.verify_password(
            password_data.current_password, current_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = security_manager.get_password_hash(
            password_data.new_password
        )
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password change"
        )

@router.post("/request-password-reset")
async def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        user = security_manager.get_user_by_email(db, data.email)
        if not user:
            logger.warning(f"Password reset requested for non-existent email: {data.email}")
            # Always return success to prevent user enumeration
            return {"message": "If the email exists, a password reset link has been sent."}
        token = security_manager.create_password_reset_token({"sub": user.email, "user_id": user.id})
        reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password"
        email_service.send_password_reset_email(user.email, token, reset_url)
        logger.info(f"Password reset email sent to {user.email}")
        return {"message": "If the email exists, a password reset link has been sent."}
    except Exception as e:
        logger.error(f"Error in password reset request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing password reset request.")

@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    try:
        token_data = security_manager.verify_password_reset_token(data.token)
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
        if not user:
            logger.warning(f"Password reset attempted for invalid user ID: {token_data['user_id']}")
            raise HTTPException(status_code=400, detail="Invalid token or user.")
        # Validate new password (reuse UserCreate validator)
        UserCreate(password=data.new_password, email=user.email)
        user.hashed_password = security_manager.get_password_hash(data.new_password)
        db.commit()
        logger.info(f"Password reset successful for user: {user.email}")
        return {"message": "Password has been reset successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=500, detail="Error resetting password.")

# Admin endpoints (superuser only)
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all users (superuser only).
    
    Args:
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        List of all users
    """
    try:
        users = db.query(User).all()
        return [UserResponse.model_validate(user) for user in users]
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while getting users")

@router.post("/generate-api-key")
async def generate_api_key(current_user: User = Depends(get_current_superuser)):
    """
    Generate a new API key (superuser only).
    
    Args:
        current_user: Current authenticated superuser
        
    Returns:
        Generated API key
    """
    try:
        api_key = security_manager.generate_api_key()
        logger.info(f"API key generated by superuser: {current_user.email}")
        return {"api_key": api_key}
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while generating API key"
        )

@router.post("/google-login", response_model=UserResponse)
async def google_login(
    request: Request,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Authenticate user with Google OAuth token and return user info with HttpOnly cookies.
    
    Args:
        request: FastAPI request object containing Google access token in Authorization header
        db: Database session
        response: FastAPI response object for setting cookies
        
    Returns:
        User information with cookies set
        
    Raises:
        HTTPException: If Google token is invalid or authentication fails
    """
    try:
        # Get user from Google token (this also creates/updates user in DB)
        user = await get_current_user_from_google_token(request, db)
        
        if getattr(user, "is_active", True) is not True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create JWT tokens
        access_token_expires = timedelta(minutes=security_manager.access_token_expire_minutes)
        access_token = security_manager.create_access_token(
            data={"sub": user.email, "user_id": user.id, "is_superuser": user.is_superuser},
            expires_delta=access_token_expires
        )
        
        refresh_token = security_manager.create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Set HttpOnly cookies
        if response:
            security_manager.set_auth_cookies(response, access_token, refresh_token)
        
        logger.info(f"Google OAuth user logged in successfully: {user.email}")
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Google OAuth login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during Google OAuth login"
        ) 
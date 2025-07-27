"""
Security module for ClariFlow backend.
Handles JWT authentication, password hashing, API key validation, and security utilities.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from ..core.config import settings
from ..core.database import get_db
from ..models.user import User, TokenData
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()

class SecurityManager:
    """Central security manager for authentication and authorization."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_verification_token(self, data: dict) -> str:
        """Create email verification token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
        to_encode.update({"exp": expire, "type": "verification"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub", "")
            user_id: int = payload.get("user_id", 0)
            is_superuser: bool = payload.get("is_superuser", False)
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(email=email, user_id=user_id, is_superuser=is_superuser)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def verify_verification_token(self, token: str) -> dict:
        """Verify and decode email verification token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub", "")
            user_id: int = payload.get("user_id", 0)
            
            if not email or user_id == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification token"
                )
            
            return {"email": email, "user_id": user_id}
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def create_user(self, db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Create a new user."""
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def generate_verification_token(self, user: User) -> str:
        """Generate email verification token for user."""
        return self.create_verification_token({
            "sub": user.email,
            "user_id": user.id
        })
    
    def set_auth_cookies(self, response: Response, access_token: str, refresh_token: str):
        """Set HttpOnly cookies for authentication."""
        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE if settings.COOKIE_SAMESITE in ['lax', 'strict', 'none'] else 'lax',
            domain=settings.COOKIE_DOMAIN
        )
        
        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE if settings.COOKIE_SAMESITE in ['lax', 'strict', 'none'] else 'lax',
            domain=settings.COOKIE_DOMAIN
        )
    
    def clear_auth_cookies(self, response: Response):
        """Clear authentication cookies."""
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
    
    def get_token_from_cookies(self, request: Request) -> Optional[str]:
        """Get access token from cookies."""
        return request.cookies.get("access_token")
    
    def get_refresh_token_from_cookies(self, request: Request) -> Optional[str]:
        """Get refresh token from cookies."""
        return request.cookies.get("refresh_token")
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key."""
        return api_key in settings.API_KEYS

    def create_password_reset_token(self, data: dict) -> str:
        """Create password reset token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        to_encode.update({"exp": expire, "type": "password_reset"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_password_reset_token(self, token: str) -> dict:
        """Verify and decode password reset token."""
        if not self.secret_key:
            raise ValueError("SECRET_KEY not configured")
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub", "")
            user_id: int = payload.get("user_id", 0)
            if not email or user_id == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid password reset token"
                )
            return {"email": email, "user_id": user_id}
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token"
            )

# Global security manager instance
security_manager = SecurityManager()

# Dependency functions
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token (cookies or headers)."""
    # Try to get token from cookies first
    token = security_manager.get_token_from_cookies(request)
    
    # Fallback to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = security_manager.verify_token(token)
    
    user = security_manager.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def verify_api_key_header(request: Request) -> bool:
    """Verify API key from request header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    if not security_manager.verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True

async def optional_api_key_auth(request: Request) -> Optional[bool]:
    """Optional API key authentication."""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return security_manager.verify_api_key(api_key)
    return None

# Rate limiting utilities
def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def get_user_identifier(request: Request, user: Optional[User] = None) -> str:
    """Get unique identifier for rate limiting."""
    if user:
        return f"user:{user.id}"
    return f"ip:{get_client_ip(request)}" 
"""
Security middleware for ClariFlow backend.
Handles CORS, rate limiting, security headers, and request validation.
"""

import time
from typing import Dict, List, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from ..core.config import settings
from ..core.security import get_client_ip, get_user_identifier
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if settings.ENABLE_SECURITY_HEADERS:
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            # Content Security Policy
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            response.headers["Content-Security-Policy"] = csp_policy
            
            # HSTS (only in production)
            if settings.ENVIRONMENT == "production":
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate incoming requests."""
    
    def __init__(self, app, max_content_length: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_content_length = max_content_length
        self.allowed_content_types = [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
            "text/plain"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_content_length:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request too large. Maximum size is {self.max_content_length} bytes."
                    )
            except ValueError:
                pass
        
        # Check content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not any(allowed_type in content_type for allowed_type in self.allowed_content_types):
                logger.warning(f"Invalid content type: {content_type} from {get_client_ip(request)}")
        
        # Log suspicious requests
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning(f"Suspicious request: missing or short User-Agent from {get_client_ip(request)}")
        
        response = await call_next(request)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to handle rate limiting."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits: Dict[str, List[float]] = {}
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        # Clean up old rate limit entries
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Get client identifier
        client_id = get_client_ip(request)
        
        # Check rate limits
        if not self._check_rate_limit(client_id, current_time):
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        return response
    
    def _check_rate_limit(self, client_id: str, current_time: float) -> bool:
        """Check if client is within rate limits."""
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = []
        
        # Remove old requests (older than 1 minute)
        self.rate_limits[client_id] = [
            req_time for req_time in self.rate_limits[client_id]
            if current_time - req_time < 60
        ]
        
        # Check if within limit
        if len(self.rate_limits[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        # Add current request
        self.rate_limits[client_id].append(current_time)
        return True
    
    def _cleanup_old_entries(self, current_time: float):
        """Clean up old rate limit entries."""
        cutoff_time = current_time - 3600  # 1 hour
        for client_id in list(self.rate_limits.keys()):
            self.rate_limits[client_id] = [
                req_time for req_time in self.rate_limits[client_id]
                if req_time > cutoff_time
            ]
            if not self.rate_limits[client_id]:
                del self.rate_limits[client_id]

def setup_cors_middleware(app):
    """Setup CORS middleware with proper configuration."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS + ["Authorization", "X-API-Key"],
        expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"],
    )

def setup_security_middleware(app):
    """Setup all security middleware."""
    # Add rate limiter exception handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add security middleware in order
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Setup CORS
    setup_cors_middleware(app)
    
    logger.info("Security middleware configured successfully")

# Rate limiting decorators
def rate_limit_per_minute(limit: int = None):
    """Rate limit decorator for per-minute limits."""
    if limit is None:
        limit = settings.RATE_LIMIT_PER_MINUTE
    return limiter.limit(f"{limit}/minute")

def rate_limit_per_hour(limit: int = None):
    """Rate limit decorator for per-hour limits."""
    if limit is None:
        limit = settings.RATE_LIMIT_PER_HOUR
    return limiter.limit(f"{limit}/hour")

def rate_limit_per_day(limit: int = 10000):
    """Rate limit decorator for per-day limits."""
    return limiter.limit(f"{limit}/day") 
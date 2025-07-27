import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import logging
import requests

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# CORS Settings
BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_DEFAULT_MODEL: str = "deepseek/deepseek-chat-v3-0324"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///clariflow.db"
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".csv", ".xlsx", ".xls", ".md"]
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = "chroma_db"
    
    # Security Configuration - Enforce secure defaults
    SECRET_KEY: Optional[str] = None  # Must be set in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Cookie Configuration for HttpOnly cookies
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Optional[str] = None
    
    # API Key Settings
    API_KEYS: List[str] = []
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS Settings - More secure defaults
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Security Headers
    ENABLE_SECURITY_HEADERS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Email Configuration (for verification)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: Optional[str] = None

    # Frontend URL for email links
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

    # Chat/AI Tuning
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))
    MAX_HISTORY_LENGTH: int = int(os.getenv("MAX_HISTORY_LENGTH", 5))

    # API Settings
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ClariFlow")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Enforce secure configuration in production
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == "dev-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be set in production environment")
            
            if not self.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY must be set in production environment")
            
            # Use secure defaults for production
            self.COOKIE_SECURE = True
            self.DEBUG = False
            # SMTP/Email validation for production
            smtp_placeholders = [
                None, '', 'your-smtp-host', 'your-smtp-username', 'your-smtp-password', 'your-email@example.com', 'your-sendgrid-key', 'your-sendgrid-username', 'your-sendgrid-password', 'your-sendgrid-from-email'
            ]
            missing = []
            if self.SMTP_HOST in smtp_placeholders:
                missing.append('SMTP_HOST')
            if not self.SMTP_PORT:
                missing.append('SMTP_PORT')
            if self.SMTP_USERNAME in smtp_placeholders:
                missing.append('SMTP_USERNAME')
            if self.SMTP_PASSWORD in smtp_placeholders:
                missing.append('SMTP_PASSWORD')
            if self.EMAIL_FROM in smtp_placeholders:
                missing.append('EMAIL_FROM')
            if missing:
                raise ValueError(f"Missing or placeholder SMTP config for production: {', '.join(missing)}. Please set real SendGrid SMTP credentials in .env.")
        else:
            # Warn if placeholders are present in development
            smtp_placeholders = [
                None, '', 'your-smtp-host', 'your-smtp-username', 'your-smtp-password', 'your-email@example.com', 'your-sendgrid-key', 'your-sendgrid-username', 'your-sendgrid-password', 'your-sendgrid-from-email'
            ]
            warn = False
            if self.SMTP_HOST in smtp_placeholders or self.SMTP_USERNAME in smtp_placeholders or self.SMTP_PASSWORD in smtp_placeholders or self.EMAIL_FROM in smtp_placeholders:
                warn = True
            if warn:
                logging.warning("[ClariFlow] SMTP config is missing or uses placeholders. Email verification will not work until real SendGrid credentials are set in .env.")

        # OpenRouter API key validation
        if self.OPENROUTER_API_KEY:
            try:
                resp = requests.get(
                    f"{self.OPENROUTER_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {self.OPENROUTER_API_KEY}"},
                    timeout=8
                )
                if resp.status_code != 200:
                    raise ValueError(f"OPENROUTER_API_KEY is invalid or OpenRouter is unavailable (status {resp.status_code}).")
                logging.info("[ClariFlow] OpenRouter API key validated. Using OpenRouter for AI features.")
            except Exception as e:
                raise ValueError(f"Failed to validate OpenRouter API key: {e}")
        elif self.OPENAI_API_KEY:
            logging.info("[ClariFlow] OpenRouter API key not set. Falling back to OpenAI for AI features.")
        else:
            logging.warning("[ClariFlow] No AI API key set. AI features will not work.")

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

settings = get_settings() 
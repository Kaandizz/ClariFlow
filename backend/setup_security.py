#!/usr/bin/env python3
"""
Security setup script for ClariFlow backend.
Creates initial admin user and generates API keys.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine, Base
from app.core.security import security_manager
from app.models.user import User
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_admin_user():
    """Create initial admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@clariflow.com").first()
        if admin_user:
            logger.info("Admin user already exists")
            return admin_user
        
        # Create admin user
        admin_user = security_manager.create_user(
            db=db,
            email="admin@clariflow.com",
            password="admin123",  # Change this in production!
            full_name="System Administrator"
        )
        
        # Make user a superuser
        admin_user.is_superuser = True
        db.commit()
        
        logger.info("Admin user created successfully")
        logger.info(f"Email: {admin_user.email}")
        logger.info("Password: admin123 (CHANGE THIS IN PRODUCTION!)")
        
        return admin_user
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def generate_api_keys():
    """Generate initial API keys."""
    api_keys = []
    
    # Generate 3 API keys
    for i in range(3):
        api_key = security_manager.generate_api_key()
        api_keys.append(api_key)
        logger.info(f"Generated API Key {i+1}: {api_key}")
    
    logger.info("API Keys generated successfully")
    logger.info("Add these to your .env file as:")
    logger.info("API_KEYS=['key1','key2','key3']")
    
    return api_keys

def setup_database():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def main():
    """Main setup function."""
    logger.info("Starting ClariFlow security setup...")
    
    try:
        # Setup database
        setup_database()
        
        # Create admin user
        admin_user = create_admin_user()
        
        # Generate API keys
        api_keys = generate_api_keys()
        
        logger.info("Security setup completed successfully!")
        logger.info("=" * 50)
        logger.info("NEXT STEPS:")
        logger.info("1. Change the admin password immediately")
        logger.info("2. Add API keys to your .env file")
        logger.info("3. Update CORS settings for production")
        logger.info("4. Change the JWT secret key")
        logger.info("5. Set environment to 'production'")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Security setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
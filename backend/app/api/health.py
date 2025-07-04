from fastapi import APIRouter
from app.utils.logger import setup_logger

# Create router instance
router = APIRouter()

# Setup logger
logger = setup_logger(__name__)

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: A message indicating the API is running
    """
    logger.info("Health check endpoint called")
    return {"status": "success", "message": "ClariFlow backend is running 🚀"} 
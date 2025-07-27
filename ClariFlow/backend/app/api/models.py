from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..utils.model_router import model_router
from ..services.ai_client import ai_client
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/models", tags=["AI Models"])

@router.get("/")
async def get_models_info() -> Dict[str, Any]:
    """
    Get information about supported AI models and their configurations.
    
    Returns:
        Dictionary with model information including:
        - supported_models: List of all supported model names
        - feature_configurations: Model assignments for different features
        - service_status: Status of AI services (OpenRouter, OpenAI)
        - api_configured: Whether OpenRouter API is configured
    """
    try:
        logger.info("Getting AI models information")
        
        # Get model router information
        model_info = model_router.get_model_info()
        
        # Get AI client service status
        service_status = ai_client.get_service_status()
        
        # Combine information
        response = {
            "models": model_info,
            "service_status": service_status,
            "message": "AI models information retrieved successfully"
        }
        
        logger.info(f"Retrieved information for {len(model_info['supported_models'])} supported models")
        return response
        
    except Exception as e:
        logger.error(f"Error getting models information: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving models information: {str(e)}")

@router.get("/status")
async def get_ai_service_status() -> Dict[str, Any]:
    """
    Get the status of AI services and their configuration.
    
    Returns:
        Dictionary with service status information
    """
    try:
        logger.info("Getting AI service status")
        
        status = ai_client.get_service_status()
        
        # Add additional status information
        status.update({
            "message": "AI service status retrieved successfully",
            "timestamp": "2024-01-01T00:00:00Z"  # You can add actual timestamp if needed
        })
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting AI service status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving service status: {str(e)}")

@router.get("/features")
async def get_feature_configurations() -> Dict[str, Any]:
    """
    Get detailed information about model configurations for different features.
    
    Returns:
        Dictionary with feature-specific model configurations
    """
    try:
        logger.info("Getting feature configurations")
        
        feature_configs = model_router.get_supported_models()
        
        response = {
            "feature_configurations": feature_configs,
            "total_features": len(feature_configs),
            "message": "Feature configurations retrieved successfully"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting feature configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving feature configurations: {str(e)}") 
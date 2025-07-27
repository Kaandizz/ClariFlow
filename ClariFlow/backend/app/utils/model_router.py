import os
import httpx
from typing import Dict, List, Any
from enum import Enum
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class FeatureType(Enum):
    """Enum for different AI feature types."""
    CHAT = "chat"
    SEARCH = "search"
    SUMMARIZATION = "summarization"
    INSIGHTS = "insights"
    COMPOSITION = "composition"
    TASK_EXTRACTION = "task_extraction"

class ModelRouter:
    """Dynamic model router for OpenRouter.ai models based on feature type."""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        # Model configurations for different features
        self.model_configs = {
            FeatureType.CHAT: {
                "primary": "deepseek/deepseek-chat-v3-0324:free",
                "fallback": "qwen/qwen3-4b-instruct",
                "description": "Optimized for conversational interactions (DeepSeek Chat v3, free tier)"
            },
            FeatureType.SEARCH: {
                "primary": "deepseek/deepseek-v3-base:free",
                "fallback": "qwen/qwen3-14b-instruct",
                "description": "Optimized for semantic search and Q&A (DeepSeek v3 Base, free tier)"
            },
            FeatureType.SUMMARIZATION: {
                "primary": "deepseek/deepseek-r1:free",
                "fallback": "mistralai/mistral-small-3.1-24b-instruct",
                "description": "Optimized for summarization and analysis (DeepSeek R1, free tier)"
            },
            FeatureType.INSIGHTS: {
                "primary": "deepseek/deepseek-r1:free",
                "fallback": "mistralai/mistral-small-3.1-24b-instruct",
                "description": "Optimized for data analysis and insights (DeepSeek R1, free tier)"
            },
            FeatureType.COMPOSITION: {
                "primary": "qwen/qwen2.5-vl-72b-instruct:free",
                "fallback": "deepseek/deepseek-chat-v3-0324:free",
                "description": "Optimized for content creation and writing (Qwen2.5 VL 72B, free tier)"
            },
            FeatureType.TASK_EXTRACTION: {
                "primary": "deepseek/deepseek-chat-v3-0324:free",
                "fallback": "qwen/qwen3-4b-instruct",
                "description": "Optimized for task extraction and parsing (DeepSeek Chat v3, free tier)"
            }
        }
        
        # Supported models list
        self.supported_models = [
            "deepseek/deepseek-chat-v3-0324:free",
            "deepseek/deepseek-v3-base:free",
            "deepseek/deepseek-r1:free",
            "qwen/qwen2.5-vl-72b-instruct:free",
            "qwen/qwen3-4b-instruct",
            "qwen/qwen3-14b-instruct",
            "mistralai/mistral-small-3.1-24b-instruct"
        ]
    
    def get_model_for_feature(self, feature_type: FeatureType, use_fallback: bool = False) -> str:
        """
        Get the appropriate model for a given feature type.
        
        Args:
            feature_type: The type of AI feature being used
            use_fallback: Whether to use fallback model instead of primary
            
        Returns:
            Model name string
        """
        if feature_type not in self.model_configs:
            logger.warning(f"Unknown feature type: {feature_type}, using default chat model")
            feature_type = FeatureType.CHAT
        
        config = self.model_configs[feature_type]
        model = config["fallback"] if use_fallback else config["primary"]
        
        logger.info(f"Selected model '{model}' for feature '{feature_type.value}' (fallback: {use_fallback})")
        return model
    
    async def make_openrouter_request(
        self, 
        messages: List[Dict[str, str]], 
        feature_type: FeatureType,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        use_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Make a request to OpenRouter.ai with automatic fallback.
        
        Args:
            messages: List of message dictionaries
            feature_type: The type of AI feature being used
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            use_fallback: Whether to use fallback model
            
        Returns:
            Response dictionary with content and metadata
        """
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        model = self.get_model_for_feature(feature_type, use_fallback)
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://clariflow.ai",
            "X-Title": "ClariFlow"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "content": result["choices"][0]["message"]["content"],
                        "model_used": model,
                        "feature_type": feature_type.value,
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                        "success": True
                    }
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    
                    # Try fallback if not already using it
                    if not use_fallback:
                        logger.info(f"Attempting fallback for {feature_type.value}")
                        return await self.make_openrouter_request(
                            messages, feature_type, max_tokens, temperature, use_fallback=True
                        )
                    else:
                        raise Exception(f"OpenRouter API error: {response.status_code}")
                        
        except Exception as e:
            logger.error(f"Error making OpenRouter request: {str(e)}")
            
            # Try fallback if not already using it
            if not use_fallback:
                logger.info(f"Attempting fallback for {feature_type.value} due to error")
                return await self.make_openrouter_request(
                    messages, feature_type, max_tokens, temperature, use_fallback=True
                )
            else:
                raise
    
    def get_supported_models(self) -> List[Dict[str, Any]]:
        """
        Get list of supported models with their configurations.
        
        Returns:
            List of model configurations
        """
        models = []
        
        for feature_type, config in self.model_configs.items():
            models.append({
                "feature_type": feature_type.value,
                "primary_model": config["primary"],
                "fallback_model": config["fallback"],
                "description": config["description"]
            })
        
        return models
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model information for API endpoint.
        
        Returns:
            Dictionary with model information
        """
        return {
            "supported_models": self.supported_models,
            "feature_configurations": self.get_supported_models(),
            "api_base_url": self.openrouter_base_url,
            "api_configured": bool(self.openrouter_api_key)
        }

# Global instance
model_router = ModelRouter() 
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from ..utils.model_router import model_router, FeatureType
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

MODEL_ASSIGNMENTS = {
    'chat': 'deepseek/deepseek-chat-v3-0324:free',
    'search': 'deepseek/deepseek-v3-base:free',
    'insights': 'deepseek/deepseek-r1:free',
    'bi': 'google/gemini-2.0-flash-exp:free',
    'compose': 'qwen/qwen2.5-vl-72b-instruct:free',
}
FALLBACK_MODEL = 'deepseek/deepseek-chat-v3-0324:free'

class AIClient:
    """Unified AI client that supports both OpenAI and OpenRouter models."""
    
    def __init__(self):
        self.openai_client = None
        self.use_openrouter = os.getenv("OPENROUTER_API_KEY") is not None
        
        # Initialize OpenAI client if API key is available
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        logger.info(f"AI Client initialized - OpenRouter: {self.use_openrouter}, OpenAI: {self.openai_client is not None}")
    
    def _get_model_for_task(self, task_type: str) -> str:
        return MODEL_ASSIGNMENTS.get(task_type, FALLBACK_MODEL)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        feature_type: FeatureType,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        use_openai_fallback: bool = False,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response using the appropriate model based on feature type.
        
        Args:
            messages: List of message dictionaries
            feature_type: The type of AI feature being used
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            use_openai_fallback: Whether to use OpenAI as fallback
            
        Returns:
            Response dictionary with content and metadata
        """
        try:
            model = self._get_model_for_task(task_type or feature_type.value)
            # Try OpenRouter first if configured
            if self.use_openrouter and not use_openai_fallback:
                logger.info(f"Using OpenRouter model '{model}' for {feature_type.value} (task_type={task_type})")
                try:
                    response = await model_router.make_openrouter_request(
                        messages, feature_type, max_tokens, temperature, model=model
                    )
                    response['model_used'] = model
                    logger.info(f"Model used: {model}")
                    return response
                except Exception as e:
                    logger.error(f"OpenRouter model '{model}' failed: {e}. Falling back to {FALLBACK_MODEL}.")
                    if model != FALLBACK_MODEL:
                        # Try fallback model
                        response = await model_router.make_openrouter_request(
                            messages, feature_type, max_tokens, temperature, model=FALLBACK_MODEL
                        )
                        response['model_used'] = FALLBACK_MODEL
                        logger.info(f"Fallback model used: {FALLBACK_MODEL}")
                        return response
                    raise
            # Fallback to OpenAI if available
            elif self.openai_client:
                logger.info(f"Using OpenAI for {feature_type.value}")
                response = await self._make_openai_request(messages, max_tokens, temperature)
                response['model_used'] = 'gpt-4'
                return response
            else:
                raise Exception("No AI service configured (OpenRouter or OpenAI)")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Try OpenAI fallback if OpenRouter failed
            if self.use_openrouter and self.openai_client and not use_openai_fallback:
                logger.info("Falling back to OpenAI")
                response = await self.generate_response(
                    messages, feature_type, max_tokens, temperature, use_openai_fallback=True, task_type=task_type
                )
                response['model_used'] = 'gpt-4'
                return response
            else:
                raise
    
    async def _make_openai_request(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Make request to OpenAI API."""
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
                
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,  # type: ignore
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "content": response.choices[0].message.content,
                "model_used": "gpt-4",
                "feature_type": "openai",
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def chat_response(
        self,
        query: str,
        history: Optional[List[str]] = None,
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate chat response."""
        messages = self._build_chat_messages(query, history)
        return await self.generate_response(messages, FeatureType.CHAT, max_tokens, temperature, task_type='chat')
    
    async def search_response(
        self,
        query: str,
        context: str,
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Generate search/Q&A response."""
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful AI assistant. Answer the user's question based on the provided context. If the context doesn't contain enough information, say so clearly.\n\nContext: {context}"
            },
            {"role": "user", "content": query}
        ]
        return await self.generate_response(messages, FeatureType.SEARCH, max_tokens, temperature, task_type='search')
    
    async def summarization_response(
        self,
        content: str,
        max_tokens: int = 800,
        temperature: float = 0.5
    ) -> Dict[str, Any]:
        """Generate summarization response."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert at summarizing content. Provide clear, concise summaries that capture the key points and main ideas."
            },
            {
                "role": "user",
                "content": f"Please summarize the following content:\n\n{content}"
            }
        ]
        return await self.generate_response(messages, FeatureType.SUMMARIZATION, max_tokens, temperature, task_type='bi')
    
    async def insights_response(
        self,
        question: str,
        data_summary: str,
        max_tokens: int = 1200,
        temperature: float = 0.6
    ) -> Dict[str, Any]:
        """Generate insights/analysis response."""
        messages = [
            {
                "role": "system",
                "content": "You are a data analyst and business intelligence expert. Analyze the provided data and answer questions with clear insights and actionable recommendations."
            },
            {
                "role": "user",
                "content": f"Data Summary:\n{data_summary}\n\nQuestion: {question}"
            }
        ]
        return await self.generate_response(messages, FeatureType.INSIGHTS, max_tokens, temperature, task_type='insights')
    
    async def composition_response(
        self,
        prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate composition (email, proposal, etc.) response."""
        messages = [
            {
                "role": "system",
                "content": "You are an expert business communication specialist. Create professional, well-structured content that is clear, persuasive, and appropriate for the intended audience."
            },
            {"role": "user", "content": prompt}
        ]
        return await self.generate_response(messages, FeatureType.COMPOSITION, max_tokens, temperature, task_type='compose')
    
    def _build_chat_messages(self, query: str, history: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """Build chat messages from query and history."""
        messages = [
            {
                "role": "system",
                "content": """You are ClariFlow, a helpful and intelligent AI assistant. 
                You can help with a wide range of topics including:
                - General knowledge questions
                - Problem solving and analysis
                - Creative writing and brainstorming
                - Technical explanations
                - Educational topics
                
                Provide clear, accurate, and helpful responses. Be conversational but professional.
                If you're continuing a conversation, maintain context from the chat history."""
            }
        ]
        
        # Add conversation history
        if history:
            for i, message in enumerate(history):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message})
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of available AI services."""
        return {
            "openrouter_configured": self.use_openrouter,
            "openai_configured": self.openai_client is not None,
            "default_service": "openrouter" if self.use_openrouter else "openai" if self.openai_client else "none",
            "supported_features": [feature.value for feature in FeatureType],
            "model_info": model_router.get_model_info() if self.use_openrouter else None
        }

# Global instance
ai_client = AIClient() 
from typing import Dict, List, Any, Optional
from ..agent_registry import Agent, AgentCapability, AgentMetadata
from ..composition_service import CompositionService
from ...models.composition import EmailComposeRequest, EmailComposeResponse
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class EmailCompositionAgent(Agent):
    """Agent for composing professional emails"""
    
    def __init__(self):
        super().__init__(
            name="email_composition_agent",
            description="Composes professional emails using AI",
            capabilities=[AgentCapability.EMAIL_COMPOSITION, AgentCapability.CONTENT_GENERATION]
        )
        self.composition_service = CompositionService()
    
    async def execute(self, input_data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute email composition.
        
        Args:
            input_data: Must contain email composition parameters
            parameters: Optional additional parameters
            context: Additional context information
            
        Returns:
            EmailComposeResponse with generated email
        """
        try:
            # Validate input
            required_fields = ['subject', 'sender_name', 'sender_email', 'context']
            if not all(field in input_data for field in required_fields):
                raise ValueError(f"Input data must contain fields: {required_fields}")
            
            # Create email compose request
            request = EmailComposeRequest(
                subject=input_data['subject'],
                recipient_name=input_data.get('recipient_name'),
                recipient_email=input_data.get('recipient_email'),
                sender_name=input_data['sender_name'],
                sender_email=input_data['sender_email'],
                email_type=input_data.get('email_type', 'custom'),
                tone=input_data.get('tone', 'professional'),
                context=input_data['context'],
                key_points=input_data.get('key_points', []),
                word_limit=input_data.get('word_limit'),
                call_to_action=input_data.get('call_to_action'),
                include_signature=input_data.get('include_signature', True)
            )
            
            # Compose email using the composition service
            result = await self.composition_service.compose_email(request)
            
            logger.info(f"Email composition completed: {result.word_count} words")
            return result
            
        except Exception as e:
            logger.error(f"Error in email composition agent: {str(e)}")
            raise
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for email composition"""
        required_fields = ['subject', 'sender_name', 'sender_email', 'context']
        return all(field in input_data for field in required_fields)

# Agent metadata for registration
email_composition_metadata = AgentMetadata(
    name="email_composition_agent",
    description="Composes professional emails using AI",
    capabilities=[AgentCapability.EMAIL_COMPOSITION, AgentCapability.CONTENT_GENERATION],
    version="1.0.0",
    author="ClariFlow",
    parameters={
        "recipient_name": "Name of the recipient",
        "recipient_email": "Email of the recipient",
        "email_type": "Type of email (follow_up, introduction, etc.)",
        "tone": "Tone of the email (formal, professional, friendly, etc.)",
        "key_points": "List of key points to include",
        "word_limit": "Target word count",
        "call_to_action": "Call to action text",
        "include_signature": "Whether to include email signature"
    },
    examples=[
        {
            "input": {
                "subject": "Follow-up on our meeting",
                "sender_name": "John Doe",
                "sender_email": "john@company.com",
                "context": "Following up on our meeting from yesterday about the project proposal",
                "recipient_name": "Jane Smith",
                "tone": "professional"
            },
            "output": {
                "subject": "Follow-up on our meeting",
                "body": "Dear Jane,\n\nThank you for taking the time to meet with me yesterday...",
                "word_count": 150
            }
        }
    ]
) 
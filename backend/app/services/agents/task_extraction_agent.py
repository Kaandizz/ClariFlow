from typing import Dict, List, Any, Optional
from ..agent_registry import Agent, AgentCapability, AgentMetadata
from ..task_service import TaskService
from ...models.tasks import TaskParseRequest, TaskParseResponse
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class TaskExtractionAgent(Agent):
    """Agent for extracting tasks from meeting transcripts and conversations"""
    
    def __init__(self):
        super().__init__(
            name="task_extraction_agent",
            description="Extracts actionable tasks from meeting transcripts and conversations using AI",
            capabilities=[AgentCapability.TASK_EXTRACTION, AgentCapability.CONTENT_GENERATION]
        )
        self.task_service = TaskService()
    
    async def execute(self, input_data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute task extraction from transcript.
        
        Args:
            input_data: Must contain 'transcript' field
            parameters: Optional parameters like meeting_date, participants, etc.
            context: Additional context information
            
        Returns:
            TaskParseResponse with extracted tasks
        """
        try:
            # Validate input
            if 'transcript' not in input_data:
                raise ValueError("Input data must contain 'transcript' field")
            
            # Create task parse request
            request = TaskParseRequest(
                transcript=input_data['transcript'],
                meeting_date=parameters.get('meeting_date') if parameters else None,
                participants=parameters.get('participants') if parameters else None,
                auto_assign=parameters.get('auto_assign', True) if parameters else True,
                context=parameters.get('context') if parameters else None
            )
            
            # Extract tasks using the task service
            result = await self.task_service.parse_tasks(request)
            
            logger.info(f"Task extraction completed: {len(result.tasks)} tasks extracted")
            return result
            
        except Exception as e:
            logger.error(f"Error in task extraction agent: {str(e)}")
            raise
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for task extraction"""
        required_fields = ['transcript']
        return all(field in input_data for field in required_fields)

# Agent metadata for registration
task_extraction_metadata = AgentMetadata(
    name="task_extraction_agent",
    description="Extracts actionable tasks from meeting transcripts and conversations using AI",
    capabilities=[AgentCapability.TASK_EXTRACTION, AgentCapability.CONTENT_GENERATION],
    version="1.0.0",
    author="ClariFlow",
    parameters={
        "meeting_date": "Optional meeting date (YYYY-MM-DD)",
        "participants": "Optional list of meeting participants",
        "auto_assign": "Whether to auto-assign tasks (default: True)",
        "context": "Optional meeting context"
    },
    examples=[
        {
            "input": {
                "transcript": "John: We need to follow up with the client by Friday. Sarah: I'll prepare the proposal by next week."
            },
            "output": {
                "tasks": [
                    {
                        "title": "Follow up with client",
                        "assignee": "John",
                        "due_date": "Friday",
                        "priority": "medium"
                    },
                    {
                        "title": "Prepare proposal",
                        "assignee": "Sarah",
                        "due_date": "next week",
                        "priority": "medium"
                    }
                ]
            }
        }
    ]
) 
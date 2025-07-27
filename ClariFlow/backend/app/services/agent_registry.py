import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentCapability(str, Enum):
    """Available agent capabilities"""
    TASK_EXTRACTION = "task_extraction"
    DOCUMENT_ANALYSIS = "document_analysis"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_GENERATION = "content_generation"
    EMAIL_COMPOSITION = "email_composition"
    PROPOSAL_COMPOSITION = "proposal_composition"
    INSIGHT_GENERATION = "insight_generation"
    CHAT_ASSISTANCE = "chat_assistance"
    SEARCH_AND_RETRIEVAL = "search_and_retrieval"
    CRM_INTEGRATION = "crm_integration"

class AgentStatus(str, Enum):
    """Agent status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"

class AgentMetadata(BaseModel):
    """Metadata for registered agents"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    version: str = Field(default="1.0.0", description="Agent version")
    author: str = Field(default="ClariFlow", description="Agent author")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Agent parameters")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")

class AgentRequest(BaseModel):
    """Request model for agent calls"""
    agent_name: str = Field(..., description="Name of the agent to call")
    input_data: Dict[str, Any] = Field(..., description="Input data for the agent")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context information")

class AgentResponse(BaseModel):
    """Response model for agent calls"""
    success: bool = Field(..., description="Whether the agent call was successful")
    result: Any = Field(..., description="Agent result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time: float = Field(..., description="Execution time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")

class AgentRegistry:
    """Central registry for managing and calling agents"""
    
    def __init__(self):
        self.agents: Dict[str, 'Agent'] = {}
        self.metadata: Dict[str, AgentMetadata] = {}
        self._lock = asyncio.Lock()
    
    async def register_agent(self, agent: 'Agent', metadata: AgentMetadata) -> bool:
        """
        Register a new agent in the registry.
        
        Args:
            agent: Agent instance to register
            metadata: Agent metadata
            
        Returns:
            True if registration successful
        """
        async with self._lock:
            try:
                if metadata.name in self.agents:
                    logger.warning(f"Agent {metadata.name} already registered, updating...")
                
                self.agents[metadata.name] = agent
                self.metadata[metadata.name] = metadata
                
                logger.info(f"Successfully registered agent: {metadata.name}")
                return True
                
            except Exception as e:
                logger.error(f"Error registering agent {metadata.name}: {str(e)}")
                return False
    
    async def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_name: Name of the agent to unregister
            
        Returns:
            True if unregistration successful
        """
        async with self._lock:
            try:
                if agent_name in self.agents:
                    del self.agents[agent_name]
                    del self.metadata[agent_name]
                    logger.info(f"Successfully unregistered agent: {agent_name}")
                    return True
                else:
                    logger.warning(f"Agent {agent_name} not found in registry")
                    return False
                    
            except Exception as e:
                logger.error(f"Error unregistering agent {agent_name}: {str(e)}")
                return False
    
    async def get_agent(self, agent_name: str) -> Optional['Agent']:
        """
        Get an agent by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)
    
    async def get_agent_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """
        Get agent metadata by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent metadata or None if not found
        """
        return self.metadata.get(agent_name)
    
    async def list_agents(self, capability: Optional[AgentCapability] = None) -> List[AgentMetadata]:
        """
        List all registered agents, optionally filtered by capability.
        
        Args:
            capability: Optional capability filter
            
        Returns:
            List of agent metadata
        """
        agents = []
        for name, metadata in self.metadata.items():
            if capability is None or capability in metadata.capabilities:
                agents.append(metadata)
        return agents
    
    async def call_agent(self, request: AgentRequest) -> AgentResponse:
        """
        Call an agent with the given request.
        
        Args:
            request: Agent request with input data
            
        Returns:
            Agent response with result
        """
        start_time = datetime.now()
        
        try:
            # Get agent
            agent = await self.get_agent(request.agent_name)
            if not agent:
                return AgentResponse(
                    success=False,
                    result=None,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    error_message=f"Agent '{request.agent_name}' not found"
                )
            
            # Check agent status
            metadata = await self.get_agent_metadata(request.agent_name)
            if metadata and metadata.status != AgentStatus.ACTIVE:
                return AgentResponse(
                    success=False,
                    result=None,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    error_message=f"Agent '{request.agent_name}' is not active (status: {metadata.status})"
                )
            
            # Call agent
            result = await agent.execute(request.input_data, request.parameters, request.context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={"agent_name": request.agent_name}
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error calling agent {request.agent_name}: {str(e)}")
            
            return AgentResponse(
                success=False,
                result=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def call_agent_chain(self, requests: List[AgentRequest]) -> List[AgentResponse]:
        """
        Call multiple agents in sequence, passing results between them.
        
        Args:
            requests: List of agent requests to execute in sequence
            
        Returns:
            List of agent responses
        """
        responses = []
        context = {}
        
        for request in requests:
            # Add previous results to context
            if responses:
                context["previous_results"] = [r.result for r in responses if r.success]
            
            request.context = {**request.context, **context} if request.context else context
            
            response = await self.call_agent(request)
            responses.append(response)
            
            # If this agent failed, stop the chain
            if not response.success:
                break
        
        return responses

class Agent:
    """Base class for all agents"""
    
    def __init__(self, name: str, description: str, capabilities: List[AgentCapability]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.status = AgentStatus.ACTIVE
    
    async def execute(self, input_data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the agent's main functionality.
        
        Args:
            input_data: Primary input data for the agent
            parameters: Additional parameters for the agent
            context: Context information from previous agents
            
        Returns:
            Agent execution result
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for the agent.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if input is valid
        """
        return True
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """
        Get agent capabilities.
        
        Returns:
            List of agent capabilities
        """
        return self.capabilities
    
    async def get_status(self) -> AgentStatus:
        """
        Get agent status.
        
        Returns:
            Agent status
        """
        return self.status
    
    async def set_status(self, status: AgentStatus):
        """
        Set agent status.
        
        Args:
            status: New agent status
        """
        self.status = status

# Global agent registry instance
agent_registry = AgentRegistry() 
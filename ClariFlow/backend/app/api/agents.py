from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..services.agent_registry import (
    agent_registry, AgentRequest, AgentResponse, AgentMetadata, AgentCapability
)
from ..services.agents import (
    TaskExtractionAgent, task_extraction_metadata,
    InsightGenerationAgent, insight_generation_metadata,
    EmailCompositionAgent, email_composition_metadata
)
from ..utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize and register agents
async def initialize_agents():
    """Initialize and register all available agents"""
    try:
        # Register task extraction agent
        task_agent = TaskExtractionAgent()
        await agent_registry.register_agent(task_agent, task_extraction_metadata)
        
        # Register insight generation agent
        insight_agent = InsightGenerationAgent()
        await agent_registry.register_agent(insight_agent, insight_generation_metadata)
        
        # Register email composition agent
        email_agent = EmailCompositionAgent()
        await agent_registry.register_agent(email_agent, email_composition_metadata)
        
        logger.info("All agents registered successfully")
        
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        raise

# Remove router-level startup event - will be called from main.py
# @router.on_event("startup")
# async def startup_event():
#     await initialize_agents()

@router.post("/agents/call", response_model=AgentResponse)
async def call_agent(request: AgentRequest):
    """
    Call a specific agent with input data.
    
    This endpoint allows you to call any registered agent with input data
    and optional parameters.
    """
    try:
        logger.info(f"Calling agent: {request.agent_name}")
        
        response = await agent_registry.call_agent(request)
        
        if response.success:
            logger.info(f"Agent {request.agent_name} executed successfully in {response.execution_time:.2f}s")
        else:
            logger.error(f"Agent {request.agent_name} failed: {response.error_message}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error calling agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to call agent: {str(e)}"
        )

@router.post("/agents/chain", response_model=List[AgentResponse])
async def call_agent_chain(requests: List[AgentRequest]):
    """
    Call multiple agents in sequence, passing results between them.
    
    This endpoint allows you to chain multiple agents together,
    with each agent receiving the results from previous agents.
    """
    try:
        logger.info(f"Calling agent chain with {len(requests)} agents")
        
        responses = await agent_registry.call_agent_chain(requests)
        
        success_count = sum(1 for r in responses if r.success)
        logger.info(f"Agent chain completed: {success_count}/{len(requests)} successful")
        
        return responses
        
    except Exception as e:
        logger.error(f"Error calling agent chain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to call agent chain: {str(e)}"
        )

@router.get("/agents/list", response_model=List[AgentMetadata])
async def list_agents(capability: Optional[AgentCapability] = None):
    """
    List all registered agents, optionally filtered by capability.
    
    Returns metadata for all available agents that can be called.
    """
    try:
        logger.info(f"Listing agents{f' with capability {capability}' if capability else ''}")
        
        agents = await agent_registry.list_agents(capability)
        
        logger.info(f"Found {len(agents)} agents")
        return agents
        
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}"
        )

@router.get("/agents/{agent_name}", response_model=AgentMetadata)
async def get_agent_info(agent_name: str):
    """
    Get detailed information about a specific agent.
    
    Returns metadata including capabilities, parameters, and examples.
    """
    try:
        logger.info(f"Getting info for agent: {agent_name}")
        
        metadata = await agent_registry.get_agent_metadata(agent_name)
        
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found"
            )
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent info: {str(e)}"
        )

@router.get("/agents/capabilities")
async def get_agent_capabilities():
    """
    Get list of all available agent capabilities.
    
    Returns information about what types of agents are available.
    """
    try:
        capabilities = {
            "task_extraction": {
                "name": "Task Extraction",
                "description": "Extract actionable tasks from meeting transcripts and conversations",
                "agents": ["task_extraction_agent"]
            },
            "insight_generation": {
                "name": "Insight Generation", 
                "description": "Generate business insights and analytics from data",
                "agents": ["insight_generation_agent"]
            },
            "email_composition": {
                "name": "Email Composition",
                "description": "Compose professional emails using AI",
                "agents": ["email_composition_agent"]
            },
            "data_analysis": {
                "name": "Data Analysis",
                "description": "Analyze and process data for insights",
                "agents": ["insight_generation_agent"]
            },
            "content_generation": {
                "name": "Content Generation",
                "description": "Generate various types of content",
                "agents": ["task_extraction_agent", "email_composition_agent"]
            }
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent capabilities: {str(e)}"
        )

@router.get("/agents/health")
async def agents_health_check():
    """
    Check the health status of all registered agents.
    
    Returns the status of each agent in the registry.
    """
    try:
        agents = await agent_registry.list_agents()
        
        health_status = {
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a.status == "active"]),
            "agents": [
                {
                    "name": agent.name,
                    "status": agent.status,
                    "capabilities": [c.value for c in agent.capabilities]
                }
                for agent in agents
            ]
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error checking agent health: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check agent health: {str(e)}"
        ) 
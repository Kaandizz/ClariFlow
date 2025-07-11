from typing import Dict, List, Any, Optional
from ..agent_registry import Agent, AgentCapability, AgentMetadata
from ..insight_service import InsightService
from ...models.insights import InsightQuery, InsightResponse
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class InsightGenerationAgent(Agent):
    """Agent for generating business insights from data"""
    
    def __init__(self):
        super().__init__(
            name="insight_generation_agent",
            description="Generates business insights and analytics from data using AI",
            capabilities=[AgentCapability.INSIGHT_GENERATION, AgentCapability.DATA_ANALYSIS]
        )
        self.insight_service = InsightService()
    
    async def execute(self, input_data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute insight generation from data.
        
        Args:
            input_data: Must contain 'question' and 'data_source' fields
            parameters: Optional parameters like visualization_type, analysis_type, etc.
            context: Additional context information
            
        Returns:
            InsightResponse with generated insights
        """
        try:
            # Validate input
            required_fields = ['question', 'data_source']
            if not all(field in input_data for field in required_fields):
                raise ValueError(f"Input data must contain fields: {required_fields}")
            
            # Create insight query
            query = InsightQuery(
                question=input_data['question'],
                data_source=input_data['data_source'],
                data_source_type=input_data.get('data_source_type', 'csv'),
                filters=parameters.get('filters') if parameters else None,
                visualization_type=parameters.get('visualization_type') if parameters else None,
                analysis_type=parameters.get('analysis_type') if parameters else None
            )
            
            # Generate insight using the insight service
            result = await self.insight_service.generate_insight(query)
            
            logger.info(f"Insight generation completed: {result.confidence_score} confidence")
            return result
            
        except Exception as e:
            logger.error(f"Error in insight generation agent: {str(e)}")
            raise
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for insight generation"""
        required_fields = ['question', 'data_source']
        return all(field in input_data for field in required_fields)

# Agent metadata for registration
insight_generation_metadata = AgentMetadata(
    name="insight_generation_agent",
    description="Generates business insights and analytics from data using AI",
    capabilities=[AgentCapability.INSIGHT_GENERATION, AgentCapability.DATA_ANALYSIS],
    version="1.0.0",
    author="ClariFlow",
    parameters={
        "data_source_type": "Type of data source (csv, excel)",
        "filters": "Optional data filters to apply",
        "visualization_type": "Type of visualization to generate",
        "analysis_type": "Type of advanced analysis to perform"
    },
    examples=[
        {
            "input": {
                "question": "What are the sales trends over the last quarter?",
                "data_source": "sales_data.csv"
            },
            "output": {
                "answer": "Sales have increased by 15% over the last quarter...",
                "confidence_score": 0.85,
                "visualization_data": {...}
            }
        }
    ]
) 
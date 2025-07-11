"""
Agent module for ClariFlow.

This module contains all the agent implementations that can be registered
with the agent registry for modular AI functionality.
"""

from .task_extraction_agent import TaskExtractionAgent, task_extraction_metadata
from .insight_generation_agent import InsightGenerationAgent, insight_generation_metadata
from .email_composition_agent import EmailCompositionAgent, email_composition_metadata

__all__ = [
    'TaskExtractionAgent',
    'task_extraction_metadata',
    'InsightGenerationAgent', 
    'insight_generation_metadata',
    'EmailCompositionAgent',
    'email_composition_metadata'
] 
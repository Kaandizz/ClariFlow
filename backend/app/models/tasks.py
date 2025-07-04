from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid
import re

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskCategory(str, Enum):
    MEETING = "meeting"
    FOLLOW_UP = "follow_up"
    RESEARCH = "research"
    PRESENTATION = "presentation"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    OTHER = "other"

class ExtractedTask(BaseModel):
    """Model for a single extracted task"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Task title/description")
    assignee: Optional[str] = Field(default=None, description="Person assigned to the task")
    due_date: Optional[date] = Field(default=None, description="Due date for the task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    category: TaskCategory = Field(default=TaskCategory.OTHER, description="Task category")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    notes: Optional[str] = Field(default=None, description="Additional notes or context")
    source_text: str = Field(..., description="Original text from which the task was extracted")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the extraction")
    extracted_at: datetime = Field(default_factory=datetime.now)

class TaskParseRequest(BaseModel):
    """Request model for task parsing"""
    transcript: str = Field(..., description="Meeting transcript or text to parse for tasks")
    meeting_date: Optional[date] = Field(default=None, description="Date of the meeting")
    participants: Optional[List[str]] = Field(default=None, description="List of meeting participants")
    context: Optional[str] = Field(default=None, description="Additional context about the meeting")
    auto_assign: bool = Field(default=False, description="Whether to automatically assign tasks based on context")

class TaskParseResponse(BaseModel):
    """Response model for task parsing"""
    tasks: List[ExtractedTask]
    total_tasks: int
    parsing_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in the parsing")
    processing_time: float = Field(..., description="Time taken to process the transcript in seconds")
    summary: Optional[str] = Field(default=None, description="Summary of extracted tasks")

class TaskUpdateRequest(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None

class TaskListResponse(BaseModel):
    """Response model for task listing"""
    tasks: List[ExtractedTask]
    total_count: int
    page: int
    per_page: int
    filters: Optional[Dict[str, Any]] = None

class TaskFilter(BaseModel):
    """Filter options for task queries"""
    assignee: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    search_term: Optional[str] = None 
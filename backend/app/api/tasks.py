from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional, List
from datetime import datetime
from ..services.task_service import TaskService
from ..models.tasks import (
    TaskParseRequest, TaskParseResponse, ExtractedTask, TaskUpdateRequest,
    TaskListResponse, TaskFilter, TaskPriority, TaskStatus, TaskCategory
)
from ..utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize service
task_service = TaskService()

@router.post("/tasks/parse", response_model=TaskParseResponse)
async def parse_tasks(request: TaskParseRequest):
    """
    Parse actionable tasks from meeting transcripts or text.
    
    This endpoint uses AI to extract tasks, assignees, due dates, and priorities
    from meeting transcripts or any text content.
    
    Example:
    - Transcript: "John will follow up with the client by Friday. Sarah needs to prepare the presentation."
    - Returns: Structured tasks with assignees, due dates, and priorities
    """
    try:
        logger.info(f"Parsing tasks from transcript of {len(request.transcript)} characters")
        
        if not request.transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcript cannot be empty"
            )
        
        # Parse tasks
        response = await task_service.parse_tasks(request)
        
        logger.info(f"Successfully extracted {response.total_tasks} tasks")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse tasks: {str(e)}"
        )

@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    category: Optional[TaskCategory] = Query(None, description="Filter by category"),
    due_date_from: Optional[str] = Query(None, description="Filter by due date from (YYYY-MM-DD)"),
    due_date_to: Optional[str] = Query(None, description="Filter by due date to (YYYY-MM-DD)"),
    search_term: Optional[str] = Query(None, description="Search in task title and notes")
):
    """
    Get tasks with optional filtering and pagination.
    
    Supports filtering by assignee, status, priority, category, due dates,
    and text search across task titles and notes.
    """
    try:
        logger.info(f"Getting tasks with filters: page={page}, per_page={per_page}")
        
        # Build filter object
        filters = None
        if any([assignee, status, priority, category, due_date_from, due_date_to, search_term]):
            filters = TaskFilter(
                assignee=assignee,
                status=status,
                priority=priority,
                category=category,
                due_date_from=due_date_from,
                due_date_to=due_date_to,
                search_term=search_term
            )
        
        # Get tasks
        response = await task_service.get_tasks(filters, page, per_page)
        
        logger.info(f"Retrieved {len(response.tasks)} tasks out of {response.total_count} total")
        return response
        
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tasks: {str(e)}"
        )

@router.get("/tasks/{task_id}", response_model=ExtractedTask)
async def get_task(task_id: str = Path(..., description="Task ID")):
    """
    Get a specific task by ID.
    
    Returns detailed information about a single task including
    all metadata and extraction details.
    """
    try:
        logger.info(f"Getting task: {task_id}")
        
        # Get task from service
        tasks = await task_service.get_tasks()
        task = None
        
        for t in tasks.tasks:
            if t.id == task_id:
                task = t
                break
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task: {str(e)}"
        )

@router.put("/tasks/{task_id}", response_model=ExtractedTask)
async def update_task(
    task_id: str = Path(..., description="Task ID"),
    update_data: TaskUpdateRequest = None
):
    """
    Update an existing task.
    
    Allows updating task properties like title, assignee, due date,
    priority, category, status, and notes.
    """
    try:
        logger.info(f"Updating task: {task_id}")
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="Update data is required"
            )
        
        # Update task
        updated_task = await task_service.update_task(task_id, update_data)
        
        logger.info(f"Successfully updated task: {task_id}")
        return updated_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update task: {str(e)}"
        )

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str = Path(..., description="Task ID")):
    """
    Delete a task.
    
    Permanently removes a task from the system.
    """
    try:
        logger.info(f"Deleting task: {task_id}")
        
        # Delete task
        success = await task_service.delete_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found"
            )
        
        logger.info(f"Successfully deleted task: {task_id}")
        return {"message": f"Task {task_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete task: {str(e)}"
        )

@router.get("/tasks/statistics")
async def get_task_statistics():
    """
    Get task statistics and analytics.
    
    Returns counts and breakdowns of tasks by status, priority,
    category, and other metrics.
    """
    try:
        logger.info("Getting task statistics")
        
        stats = await task_service.get_task_statistics()
        
        logger.info(f"Retrieved statistics: {stats['total_tasks']} total tasks")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting task statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task statistics: {str(e)}"
        )

@router.get("/tasks/priorities")
async def get_task_priorities():
    """
    Get available task priority levels.
    
    Returns the list of priority levels and their descriptions.
    """
    try:
        priorities = [
            {
                "value": TaskPriority.LOW.value,
                "name": "Low",
                "description": "Low priority tasks that can be addressed when convenient",
                "color": "#6B7280"
            },
            {
                "value": TaskPriority.MEDIUM.value,
                "name": "Medium",
                "description": "Standard priority tasks that should be completed in a reasonable timeframe",
                "color": "#3B82F6"
            },
            {
                "value": TaskPriority.HIGH.value,
                "name": "High",
                "description": "High priority tasks that require immediate attention",
                "color": "#F59E0B"
            },
            {
                "value": TaskPriority.URGENT.value,
                "name": "Urgent",
                "description": "Critical tasks that must be completed immediately",
                "color": "#EF4444"
            }
        ]
        
        return {"priorities": priorities}
        
    except Exception as e:
        logger.error(f"Error getting task priorities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task priorities: {str(e)}"
        )

@router.get("/tasks/categories")
async def get_task_categories():
    """
    Get available task categories.
    
    Returns the list of task categories and their descriptions.
    """
    try:
        categories = [
            {
                "value": TaskCategory.MEETING.value,
                "name": "Meeting",
                "description": "Tasks related to meetings and discussions",
                "icon": "calendar"
            },
            {
                "value": TaskCategory.FOLLOW_UP.value,
                "name": "Follow Up",
                "description": "Follow-up tasks and communications",
                "icon": "mail"
            },
            {
                "value": TaskCategory.RESEARCH.value,
                "name": "Research",
                "description": "Research and analysis tasks",
                "icon": "search"
            },
            {
                "value": TaskCategory.PRESENTATION.value,
                "name": "Presentation",
                "description": "Tasks related to creating or delivering presentations",
                "icon": "presentation"
            },
            {
                "value": TaskCategory.ANALYSIS.value,
                "name": "Analysis",
                "description": "Data analysis and reporting tasks",
                "icon": "chart"
            },
            {
                "value": TaskCategory.COMMUNICATION.value,
                "name": "Communication",
                "description": "Communication and outreach tasks",
                "icon": "message"
            },
            {
                "value": TaskCategory.OTHER.value,
                "name": "Other",
                "description": "Miscellaneous tasks",
                "icon": "more"
            }
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error getting task categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task categories: {str(e)}"
        )

@router.get("/tasks/statuses")
async def get_task_statuses():
    """
    Get available task statuses.
    
    Returns the list of task statuses and their descriptions.
    """
    try:
        statuses = [
            {
                "value": TaskStatus.PENDING.value,
                "name": "Pending",
                "description": "Task is waiting to be started",
                "color": "#6B7280"
            },
            {
                "value": TaskStatus.IN_PROGRESS.value,
                "name": "In Progress",
                "description": "Task is currently being worked on",
                "color": "#3B82F6"
            },
            {
                "value": TaskStatus.COMPLETED.value,
                "name": "Completed",
                "description": "Task has been finished",
                "color": "#10B981"
            },
            {
                "value": TaskStatus.CANCELLED.value,
                "name": "Cancelled",
                "description": "Task has been cancelled or abandoned",
                "color": "#EF4444"
            }
        ]
        
        return {"statuses": statuses}
        
    except Exception as e:
        logger.error(f"Error getting task statuses: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task statuses: {str(e)}"
        )

@router.get("/tasks/health")
async def tasks_health_check():
    """
    Health check endpoint for tasks service.
    
    Verifies that the tasks service is working properly
    and can connect to required dependencies.
    """
    try:
        # Check if OpenAI is accessible
        import openai
        client = openai.OpenAI(api_key=task_service.client.api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        health_status = {
            "status": "healthy",
            "services": {
                "openai": "connected",
                "task_processing": "ready",
                "storage": "available"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Tasks health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Tasks service unhealthy: {str(e)}"
        ) 
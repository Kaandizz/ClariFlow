import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import time
from openai import OpenAI
from ..core.config import settings
from ..utils.logger import setup_logger
from ..models.tasks import (
    TaskParseRequest, TaskParseResponse, ExtractedTask, TaskUpdateRequest,
    TaskListResponse, TaskFilter, TaskPriority, TaskStatus, TaskCategory
)

logger = setup_logger(__name__)

class TaskService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.tasks_storage = {}  # In-memory storage for demo purposes
        
    async def parse_tasks(self, request: TaskParseRequest) -> TaskParseResponse:
        """
        Parse tasks from meeting transcript using OpenAI function calling.
        
        Args:
            request: TaskParseRequest containing transcript and context
            
        Returns:
            TaskParseResponse with extracted tasks
        """
        start_time = time.time()
        
        try:
            logger.info(f"Parsing tasks from transcript of {len(request.transcript)} characters")
            
            # Prepare context for OpenAI
            context = self._prepare_context(request)
            
            # Define function schema for task extraction
            functions = [
                {
                    "type": "function",
                    "function": {
                        "name": "extract_tasks",
                        "description": "Extract actionable tasks from meeting transcript",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "tasks": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "Clear, actionable task description"
                                            },
                                            "assignee": {
                                                "type": "string",
                                                "description": "Person responsible for the task (if mentioned)"
                                            },
                                            "due_date": {
                                                "type": "string",
                                                "description": "Due date in YYYY-MM-DD format (if mentioned)"
                                            },
                                            "priority": {
                                                "type": "string",
                                                "enum": ["low", "medium", "high", "urgent"],
                                                "description": "Task priority level"
                                            },
                                            "category": {
                                                "type": "string",
                                                "enum": ["meeting", "follow_up", "research", "presentation", "analysis", "communication", "other"],
                                                "description": "Task category"
                                            },
                                            "notes": {
                                                "type": "string",
                                                "description": "Additional context or notes about the task"
                                            },
                                            "source_text": {
                                                "type": "string",
                                                "description": "Original text from which this task was extracted"
                                            },
                                            "confidence": {
                                                "type": "number",
                                                "description": "Confidence score (0-1) in the extraction"
                                            }
                                        },
                                        "required": ["title", "source_text", "confidence"]
                                    }
                                },
                                "summary": {
                                    "type": "string",
                                    "description": "Brief summary of all extracted tasks"
                                },
                                "overall_confidence": {
                                    "type": "number",
                                    "description": "Overall confidence in the parsing (0-1)"
                                }
                            },
                            "required": ["tasks", "summary", "overall_confidence"]
                        }
                    }
                }
            ]
            
            # Create prompt for task extraction
            prompt = f"""
            You are an expert at extracting actionable tasks from meeting transcripts and conversations.
            
            Context:
            {context}
            
            Please carefully analyze the transcript and extract all actionable tasks. Focus on:
            1. Clear, specific action items
            2. Who is responsible (if mentioned)
            3. When it's due (if mentioned)
            4. Priority level based on urgency indicators
            5. Task category based on the nature of the work
            
            Be thorough but avoid extracting general discussion points as tasks. Only extract items that require specific action.
            """
            
            # Get response from OpenAI with function calling
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                functions=functions,
                function_call={"name": "extract_tasks"},
                max_tokens=2000,
                temperature=0.2
            )
            
            # Parse function call response
            function_call = response.choices[0].message.function_call
            if function_call and function_call.name == "extract_tasks":
                result = json.loads(function_call.arguments)
                
                # Convert to ExtractedTask objects
                tasks = []
                for task_data in result.get("tasks", []):
                    task = ExtractedTask(
                        title=task_data["title"],
                        assignee=task_data.get("assignee"),
                        due_date=self._parse_date(task_data.get("due_date")),
                        priority=TaskPriority(task_data.get("priority", "medium")),
                        category=TaskCategory(task_data.get("category", "other")),
                        notes=task_data.get("notes"),
                        source_text=task_data["source_text"],
                        confidence_score=task_data["confidence"]
                    )
                    tasks.append(task)
                
                # Store tasks
                for task in tasks:
                    self.tasks_storage[task.id] = task
                
                processing_time = time.time() - start_time
                
                response_obj = TaskParseResponse(
                    tasks=tasks,
                    total_tasks=len(tasks),
                    parsing_confidence=result.get("overall_confidence", 0.8),
                    processing_time=processing_time,
                    summary=result.get("summary")
                )
                
                logger.info(f"Successfully extracted {len(tasks)} tasks in {processing_time:.2f}s")
                return response_obj
            else:
                raise ValueError("Failed to extract tasks from OpenAI response")
                
        except Exception as e:
            logger.error(f"Error parsing tasks: {str(e)}")
            raise
    
    def _prepare_context(self, request: TaskParseRequest) -> str:
        """Prepare context information for task extraction."""
        context_parts = []
        
        if request.meeting_date:
            context_parts.append(f"Meeting Date: {request.meeting_date}")
        
        if request.participants:
            context_parts.append(f"Participants: {', '.join(request.participants)}")
        
        if request.context:
            context_parts.append(f"Meeting Context: {request.context}")
        
        context_parts.append(f"Auto-assign: {request.auto_assign}")
        context_parts.append(f"Transcript:\n{request.transcript}")
        
        return "\n".join(context_parts)
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Try to extract date from natural language
            date_patterns = [
                r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY or DD/MM/YYYY
                r"(\d{4})-(\d{1,2})-(\d{1,2})",  # YYYY-MM-DD
                r"(\d{1,2})-(\d{1,2})-(\d{4})",  # MM-DD-YYYY or DD-MM-YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        return datetime(int(groups[0]), int(groups[1]), int(groups[2])).date()
                    else:  # Assume MM/DD/YYYY
                        return datetime(int(groups[2]), int(groups[0]), int(groups[1])).date()
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {str(e)}")
            return None
    
    async def get_tasks(self, filters: Optional[TaskFilter] = None, page: int = 1, per_page: int = 20) -> TaskListResponse:
        """
        Get tasks with optional filtering and pagination.
        
        Args:
            filters: Optional filters to apply
            page: Page number (1-based)
            per_page: Number of tasks per page
            
        Returns:
            TaskListResponse with filtered and paginated tasks
        """
        try:
            # Get all tasks
            all_tasks = list(self.tasks_storage.values())
            
            # Apply filters
            if filters:
                all_tasks = self._apply_filters(all_tasks, filters)
            
            # Sort by extraction date (newest first)
            all_tasks.sort(key=lambda x: x.extracted_at, reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_tasks = all_tasks[start_idx:end_idx]
            
            return TaskListResponse(
                tasks=paginated_tasks,
                total_count=len(all_tasks),
                page=page,
                per_page=per_page,
                filters=filters.dict() if filters else None
            )
            
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            raise
    
    def _apply_filters(self, tasks: List[ExtractedTask], filters: TaskFilter) -> List[ExtractedTask]:
        """Apply filters to task list."""
        filtered_tasks = tasks
        
        if filters.assignee:
            filtered_tasks = [t for t in filtered_tasks if t.assignee and filters.assignee.lower() in t.assignee.lower()]
        
        if filters.status:
            filtered_tasks = [t for t in filtered_tasks if t.status == filters.status]
        
        if filters.priority:
            filtered_tasks = [t for t in filtered_tasks if t.priority == filters.priority]
        
        if filters.category:
            filtered_tasks = [t for t in filtered_tasks if t.category == filters.category]
        
        if filters.due_date_from:
            filtered_tasks = [t for t in filtered_tasks if t.due_date and t.due_date >= filters.due_date_from]
        
        if filters.due_date_to:
            filtered_tasks = [t for t in filtered_tasks if t.due_date and t.due_date <= filters.due_date_to]
        
        if filters.search_term:
            search_term = filters.search_term.lower()
            filtered_tasks = [
                t for t in filtered_tasks 
                if search_term in t.title.lower() or 
                   (t.notes and search_term in t.notes.lower()) or
                   (t.source_text and search_term in t.source_text.lower())
            ]
        
        return filtered_tasks
    
    async def update_task(self, task_id: str, update_data: TaskUpdateRequest) -> ExtractedTask:
        """
        Update an existing task.
        
        Args:
            task_id: ID of the task to update
            update_data: Data to update
            
        Returns:
            Updated ExtractedTask
        """
        try:
            if task_id not in self.tasks_storage:
                raise ValueError(f"Task with ID {task_id} not found")
            
            task = self.tasks_storage[task_id]
            
            # Update fields if provided
            if update_data.title is not None:
                task.title = update_data.title
            if update_data.assignee is not None:
                task.assignee = update_data.assignee
            if update_data.due_date is not None:
                task.due_date = update_data.due_date
            if update_data.priority is not None:
                task.priority = update_data.priority
            if update_data.category is not None:
                task.category = update_data.category
            if update_data.status is not None:
                task.status = update_data.status
            if update_data.notes is not None:
                task.notes = update_data.notes
            
            logger.info(f"Updated task {task_id}")
            return task
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if task_id not in self.tasks_storage:
                raise ValueError(f"Task with ID {task_id} not found")
            
            del self.tasks_storage[task_id]
            logger.info(f"Deleted task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about tasks.
        
        Returns:
            Dictionary with task statistics
        """
        try:
            tasks = list(self.tasks_storage.values())
            
            if not tasks:
                return {
                    "total_tasks": 0,
                    "by_status": {},
                    "by_priority": {},
                    "by_category": {},
                    "overdue_tasks": 0,
                    "due_soon_tasks": 0
                }
            
            # Count by status
            status_counts = {}
            for task in tasks:
                status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1
            
            # Count by priority
            priority_counts = {}
            for task in tasks:
                priority_counts[task.priority.value] = priority_counts.get(task.priority.value, 0) + 1
            
            # Count by category
            category_counts = {}
            for task in tasks:
                category_counts[task.category.value] = category_counts.get(task.category.value, 0) + 1
            
            # Count overdue and due soon tasks
            today = date.today()
            overdue_tasks = len([t for t in tasks if t.due_date and t.due_date < today and t.status != TaskStatus.COMPLETED])
            due_soon_tasks = len([t for t in tasks if t.due_date and t.due_date <= today + timedelta(days=7) and t.status != TaskStatus.COMPLETED])
            
            return {
                "total_tasks": len(tasks),
                "by_status": status_counts,
                "by_priority": priority_counts,
                "by_category": category_counts,
                "overdue_tasks": overdue_tasks,
                "due_soon_tasks": due_soon_tasks
            }
            
        except Exception as e:
            logger.error(f"Error getting task statistics: {str(e)}")
            raise 
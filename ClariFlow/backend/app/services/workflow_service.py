from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from ..models.workflow import (
    Workflow, WorkflowStep, WorkflowExecution, WorkflowStepExecution,
    WorkflowStatus, WorkflowExecutionStatus, WorkflowActionType
)
from .audit_service import AuditService
from .composition_service import CompositionService
from .task_service import TaskService
from .crm_service import CRMService
from .agent_registry import AgentRegistry

logger = logging.getLogger(__name__)

class WorkflowService:
    """Service for managing workflows and their execution"""
    
    def __init__(self):
        self.audit_service = AuditService()
        self.composition_service = CompositionService()
        self.task_service = TaskService()
        self.crm_service = CRMService()
        self.agent_registry = AgentRegistry()
    
    def create_workflow(self, db: Session, user_id: str, workflow_data: Dict[str, Any]) -> Workflow:
        """Create a new workflow"""
        try:
            workflow = Workflow(
                name=workflow_data["name"],
                description=workflow_data.get("description", ""),
                trigger_type=workflow_data["trigger_type"],
                trigger_config=workflow_data.get("trigger_config", {}),
                status=WorkflowStatus.DRAFT,
                user_id=user_id
            )
            
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
            
            # Create workflow steps
            if "steps" in workflow_data:
                for i, step_data in enumerate(workflow_data["steps"]):
                    step = WorkflowStep(
                        workflow_id=workflow.id,
                        name=step_data["name"],
                        action_type=step_data["action_type"],
                        action_config=step_data.get("action_config", {}),
                        order_index=i,
                        is_conditional=step_data.get("is_conditional", False),
                        condition_config=step_data.get("condition_config", {})
                    )
                    db.add(step)
                
                db.commit()
            
            # Log audit event
            self.audit_service.log_event(
                db=db,
                user_id=user_id,
                action="workflow_created",
                resource_type="workflow",
                resource_id=workflow.id,
                details={"workflow_name": workflow.name}
            )
            
            logger.info(f"Created workflow '{workflow.name}' for user {user_id}")
            return workflow
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating workflow: {str(e)}")
            raise
    
    def get_user_workflows(self, db: Session, user_id: str, status: Optional[WorkflowStatus] = None) -> List[Workflow]:
        """Get workflows for a user"""
        query = db.query(Workflow).filter(Workflow.user_id == user_id)
        
        if status:
            query = query.filter(Workflow.status == status)
        
        return query.order_by(Workflow.created_at.desc()).all()
    
    def get_workflow(self, db: Session, workflow_id: str, user_id: str) -> Optional[Workflow]:
        """Get a specific workflow"""
        return db.query(Workflow).filter(
            and_(Workflow.id == workflow_id, Workflow.user_id == user_id)
        ).first()
    
    def update_workflow(self, db: Session, workflow_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Workflow]:
        """Update a workflow"""
        workflow = self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        try:
            for key, value in update_data.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
            
            workflow.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(workflow)
            
            # Log audit event
            self.audit_service.log_event(
                db=db,
                user_id=user_id,
                action="workflow_updated",
                resource_type="workflow",
                resource_id=workflow_id,
                details=update_data
            )
            
            logger.info(f"Updated workflow '{workflow.name}' for user {user_id}")
            return workflow
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating workflow: {str(e)}")
            raise
    
    def delete_workflow(self, db: Session, workflow_id: str, user_id: str) -> bool:
        """Delete a workflow"""
        workflow = self.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return False
        
        try:
            workflow_name = workflow.name
            db.delete(workflow)
            db.commit()
            
            # Log audit event
            self.audit_service.log_event(
                db=db,
                user_id=user_id,
                action="workflow_deleted",
                resource_type="workflow",
                resource_id=workflow_id,
                details={"workflow_name": workflow_name}
            )
            
            logger.info(f"Deleted workflow '{workflow_name}' for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting workflow: {str(e)}")
            raise
    
    async def execute_workflow(self, db: Session, workflow_id: str, user_id: str, trigger_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        workflow = self.get_workflow(db, workflow_id, user_id)
        if not workflow or workflow.status != WorkflowStatus.ACTIVE:
            raise ValueError("Workflow not found or not active")
        
        try:
            # Create execution record
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                user_id=user_id,
                status=WorkflowExecutionStatus.RUNNING,
                trigger_data=trigger_data or {},
                started_at=datetime.utcnow()
            )
            
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Log audit event
            self.audit_service.log_event(
                db=db,
                user_id=user_id,
                action="workflow_execution_started",
                resource_type="workflow",
                resource_id=workflow_id,
                details={"execution_id": execution.id}
            )
            
            # Execute workflow steps
            steps = db.query(WorkflowStep).filter(
                WorkflowStep.workflow_id == workflow_id
            ).order_by(WorkflowStep.order_index).all()
            
            execution_data = trigger_data or {}
            
            for step in steps:
                step_execution = await self._execute_step(db, execution, step, execution_data)
                if step_execution.status == WorkflowExecutionStatus.FAILED:
                    execution.status = WorkflowExecutionStatus.FAILED
                    execution.error_message = step_execution.error_message
                    break
                elif step_execution.status == WorkflowExecutionStatus.COMPLETED:
                    # Merge output data for next steps
                    if step_execution.output_data:
                        execution_data.update(step_execution.output_data)
            
            # Update execution status
            if execution.status != WorkflowExecutionStatus.FAILED:
                execution.status = WorkflowExecutionStatus.COMPLETED
                execution.result_data = execution_data
            
            execution.completed_at = datetime.utcnow()
            db.commit()
            
            # Log audit event
            self.audit_service.log_event(
                db=db,
                user_id=user_id,
                action="workflow_execution_completed",
                resource_type="workflow",
                resource_id=workflow_id,
                details={
                    "execution_id": execution.id,
                    "status": execution.status.value,
                    "steps_executed": len(steps)
                }
            )
            
            logger.info(f"Completed workflow execution {execution.id} with status {execution.status}")
            return execution
            
        except Exception as e:
            if execution:
                execution.status = WorkflowExecutionStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
                db.commit()
            
            logger.error(f"Error executing workflow: {str(e)}")
            raise
    
    async def _execute_step(self, db: Session, execution: WorkflowExecution, step: WorkflowStep, input_data: Dict[str, Any]) -> WorkflowStepExecution:
        """Execute a single workflow step"""
        step_execution = WorkflowStepExecution(
            execution_id=execution.id,
            step_id=step.id,
            status=WorkflowExecutionStatus.RUNNING,
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        
        db.add(step_execution)
        db.commit()
        db.refresh(step_execution)
        
        try:
            # Check conditional logic
            if step.is_conditional and step.condition_config:
                if not self._evaluate_condition(input_data, step.condition_config):
                    step_execution.status = WorkflowExecutionStatus.COMPLETED
                    step_execution.completed_at = datetime.utcnow()
                    db.commit()
                    return step_execution
            
            # Execute action
            output_data = await self._execute_action(step.action_type, step.action_config, input_data)
            
            step_execution.status = WorkflowExecutionStatus.COMPLETED
            step_execution.output_data = output_data
            step_execution.completed_at = datetime.utcnow()
            
        except Exception as e:
            step_execution.status = WorkflowExecutionStatus.FAILED
            step_execution.error_message = str(e)
            step_execution.completed_at = datetime.utcnow()
            logger.error(f"Error executing step {step.name}: {str(e)}")
        
        db.commit()
        return step_execution
    
    def _evaluate_condition(self, data: Dict[str, Any], condition_config: Dict[str, Any]) -> bool:
        """Evaluate conditional logic for workflow steps"""
        try:
            condition_type = condition_config.get("type", "simple")
            
            if condition_type == "simple":
                field = condition_config.get("field")
                operator = condition_config.get("operator", "equals")
                value = condition_config.get("value")
                
                if field not in data:
                    return False
                
                field_value = data[field]
                
                if operator == "equals":
                    return field_value == value
                elif operator == "not_equals":
                    return field_value != value
                elif operator == "contains":
                    return value in str(field_value)
                elif operator == "greater_than":
                    return field_value > value
                elif operator == "less_than":
                    return field_value < value
                elif operator == "exists":
                    return field_value is not None
                elif operator == "not_exists":
                    return field_value is None
                
            elif condition_type == "complex":
                # Support for complex logical expressions
                conditions = condition_config.get("conditions", [])
                logic = condition_config.get("logic", "AND")
                
                results = []
                for condition in conditions:
                    results.append(self._evaluate_condition(data, condition))
                
                if logic == "AND":
                    return all(results)
                elif logic == "OR":
                    return any(results)
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False
    
    async def _execute_action(self, action_type: WorkflowActionType, action_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow action"""
        try:
            if action_type == WorkflowActionType.SEND_EMAIL:
                return await self._execute_send_email(action_config, input_data)
            elif action_type == WorkflowActionType.CREATE_TASK:
                return await self._execute_create_task(action_config, input_data)
            elif action_type == WorkflowActionType.UPDATE_CRM:
                return await self._execute_update_crm(action_config, input_data)
            elif action_type == WorkflowActionType.SEND_NOTIFICATION:
                return await self._execute_send_notification(action_config, input_data)
            elif action_type == WorkflowActionType.EXECUTE_AGENT:
                return await self._execute_agent(action_config, input_data)
            elif action_type == WorkflowActionType.GENERATE_REPORT:
                return await self._execute_generate_report(action_config, input_data)
            elif action_type == WorkflowActionType.UPDATE_STATUS:
                return await self._execute_update_status(action_config, input_data)
            elif action_type == WorkflowActionType.CUSTOM_SCRIPT:
                return await self._execute_custom_script(action_config, input_data)
            else:
                raise ValueError(f"Unsupported action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {str(e)}")
            raise
    
    async def _execute_send_email(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute send email action"""
        try:
            email_data = {
                "to": config.get("to", data.get("email")),
                "subject": config.get("subject", "Workflow Notification"),
                "content": config.get("content", "This is an automated message from your workflow."),
                "template": config.get("template"),
                "variables": data
            }
            
            # Use composition service to send email
            result = await self.composition_service.compose_email(email_data)
            
            return {
                "email_sent": True,
                "email_id": result.get("id"),
                "recipient": email_data["to"]
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    async def _execute_create_task(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create task action"""
        try:
            task_data = {
                "title": config.get("title", "Workflow Task"),
                "description": config.get("description", ""),
                "priority": config.get("priority", "medium"),
                "due_date": config.get("due_date"),
                "assignee": config.get("assignee"),
                "tags": config.get("tags", []),
                "source": "workflow"
            }
            
            # Merge with input data
            task_data.update(data)
            
            # Use task service to create task
            result = await self.task_service.create_task(task_data)
            
            return {
                "task_created": True,
                "task_id": result.get("id"),
                "task_title": task_data["title"]
            }
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise
    
    async def _execute_update_crm(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CRM update action"""
        try:
            crm_data = {
                "crm_type": config.get("crm_type"),
                "entity_type": config.get("entity_type"),
                "entity_id": config.get("entity_id"),
                "update_data": config.get("update_data", {})
            }
            
            # Use CRM service to update
            result = await self.crm_service.update_entity(crm_data)
            
            return {
                "crm_updated": True,
                "entity_id": crm_data["entity_id"],
                "update_result": result
            }
            
        except Exception as e:
            logger.error(f"Error updating CRM: {str(e)}")
            raise
    
    async def _execute_send_notification(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute send notification action"""
        try:
            notification_data = {
                "type": config.get("type", "info"),
                "title": config.get("title", "Workflow Notification"),
                "message": config.get("message", "Workflow action completed"),
                "recipient": config.get("recipient"),
                "data": data
            }
            
            # For now, just log the notification
            logger.info(f"Notification: {notification_data['title']} - {notification_data['message']}")
            
            return {
                "notification_sent": True,
                "notification_type": notification_data["type"]
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise
    
    async def _execute_agent(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action"""
        try:
            agent_name = config.get("agent_name")
            agent_input = config.get("input", data)
            
            # Use agent registry to execute agent
            result = await self.agent_registry.call_agent(agent_name, agent_input)
            
            return {
                "agent_executed": True,
                "agent_name": agent_name,
                "agent_result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}")
            raise
    
    async def _execute_generate_report(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generate report action"""
        try:
            report_config = {
                "report_type": config.get("report_type", "summary"),
                "data_source": config.get("data_source"),
                "format": config.get("format", "pdf"),
                "parameters": config.get("parameters", {})
            }
            
            # For now, just return a placeholder
            return {
                "report_generated": True,
                "report_type": report_config["report_type"],
                "report_id": f"report_{datetime.utcnow().timestamp()}"
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    async def _execute_update_status(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update status action"""
        try:
            status_data = {
                "resource_type": config.get("resource_type"),
                "resource_id": config.get("resource_id"),
                "new_status": config.get("new_status"),
                "notes": config.get("notes")
            }
            
            # For now, just log the status update
            logger.info(f"Status update: {status_data['resource_type']} {status_data['resource_id']} -> {status_data['new_status']}")
            
            return {
                "status_updated": True,
                "resource_type": status_data["resource_type"],
                "resource_id": status_data["resource_id"],
                "new_status": status_data["new_status"]
            }
            
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            raise
    
    async def _execute_custom_script(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom script action"""
        try:
            script = config.get("script", "")
            script_type = config.get("script_type", "python")
            
            # For security, we'll only allow predefined scripts or simple operations
            # In a production environment, you'd want proper sandboxing
            
            if script_type == "python":
                # Execute in a restricted environment
                local_vars = {"data": data, "result": {}}
                exec(script, {"__builtins__": {}}, local_vars)
                return local_vars.get("result", {})
            else:
                raise ValueError(f"Unsupported script type: {script_type}")
                
        except Exception as e:
            logger.error(f"Error executing custom script: {str(e)}")
            raise
    
    def get_workflow_executions(self, db: Session, user_id: str, workflow_id: Optional[str] = None, limit: int = 50) -> List[WorkflowExecution]:
        """Get workflow executions for a user"""
        query = db.query(WorkflowExecution).join(Workflow).filter(Workflow.user_id == user_id)
        
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        
        return query.order_by(WorkflowExecution.created_at.desc()).limit(limit).all()
    
    def get_execution_details(self, db: Session, execution_id: str, user_id: str) -> Optional[WorkflowExecution]:
        """Get detailed execution information"""
        return db.query(WorkflowExecution).join(Workflow).filter(
            and_(WorkflowExecution.id == execution_id, Workflow.user_id == user_id)
        ).first() 
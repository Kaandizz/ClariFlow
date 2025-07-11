from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.workflow import (
    Workflow, WorkflowStep, WorkflowExecution, WorkflowStatus, WorkflowTriggerType, WorkflowActionType,
    AuditLog, AuditLogLevel, AuditLogCategory
)
from ..services.workflow_service import WorkflowService
from ..services.audit_service import AuditService
from ..schemas import User
from .auth import get_current_user

router = APIRouter(prefix="/api/workflows", tags=["workflows"])
workflow_service = WorkflowService()
audit_service = AuditService()

@router.post("/", response_model=dict)
def create_workflow(
    workflow_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = workflow_service.create_workflow(db, str(current_user.id), workflow_data)
    return {"workflow_id": workflow.id, "status": workflow.status.value}

@router.get("/", response_model=List[dict])
def list_workflows(
    status: Optional[WorkflowStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflows = workflow_service.get_user_workflows(db, str(current_user.id), status)
    return [
        {
            "id": w.id,
            "name": w.name,
            "status": w.status.value,
            "trigger_type": w.trigger_type.value,
            "created_at": w.created_at,
            "updated_at": w.updated_at
        } for w in workflows
    ]

@router.get("/{workflow_id}", response_model=dict)
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = workflow_service.get_workflow(db, workflow_id, str(current_user.id))
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status.value,
        "trigger_type": workflow.trigger_type.value,
        "steps": [
            {
                "id": s.id,
                "name": s.name,
                "action_type": s.action_type.value,
                "order_index": s.order_index
            } for s in workflow.steps
        ],
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at
    }

@router.put("/{workflow_id}", response_model=dict)
def update_workflow(
    workflow_id: str,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = workflow_service.update_workflow(db, workflow_id, str(current_user.id), update_data)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow_id": workflow.id, "status": workflow.status.value}

@router.delete("/{workflow_id}", response_model=dict)
def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = workflow_service.delete_workflow(db, workflow_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"deleted": True}

@router.post("/{workflow_id}/execute", response_model=dict)
async def execute_workflow(
    workflow_id: str,
    trigger_data: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    execution = await workflow_service.execute_workflow(db, workflow_id, str(current_user.id), trigger_data)
    return {"execution_id": execution.id, "status": execution.status.value}

@router.get("/{workflow_id}/executions", response_model=List[dict])
def list_executions(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    executions = workflow_service.get_workflow_executions(db, str(current_user.id), workflow_id)
    return [
        {
            "id": e.id,
            "status": e.status.value,
            "started_at": e.started_at,
            "completed_at": e.completed_at
        } for e in executions
    ]

@router.get("/executions/{execution_id}", response_model=dict)
def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    execution = workflow_service.get_execution_details(db, execution_id, str(current_user.id))
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {
        "id": execution.id,
        "status": execution.status.value,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "result_data": execution.result_data,
        "error_message": execution.error_message
    }

# --- Audit Log Endpoints ---

@router.get("/audit/logs", response_model=List[dict])
def get_user_audit_logs(
    limit: int = 100,
    offset: int = 0,
    category: Optional[AuditLogCategory] = None,
    level: Optional[AuditLogLevel] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = audit_service.get_user_audit_logs(db, str(current_user.id), limit, offset, category, level)
    return [
        {
            "id": log.id,
            "action": log.action,
            "category": log.category.value,
            "level": log.level.value,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "created_at": log.created_at
        } for log in logs
    ]

@router.get("/audit/summary", response_model=dict)
def get_audit_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = audit_service.get_audit_summary(db, str(current_user.id))
    return summary 
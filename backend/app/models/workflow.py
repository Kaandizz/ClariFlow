from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
import uuid
from ..core.database import Base

class WorkflowTriggerType(str, Enum):
    """Types of workflow triggers"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    WEBHOOK = "webhook"
    CONDITION = "condition"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"

class WorkflowExecutionStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowActionType(str, Enum):
    """Types of workflow actions"""
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    UPDATE_CRM = "update_crm"
    SEND_NOTIFICATION = "send_notification"
    EXECUTE_AGENT = "execute_agent"
    GENERATE_REPORT = "generate_report"
    UPDATE_STATUS = "update_status"
    CUSTOM_SCRIPT = "custom_script"

class Workflow(Base):
    """Workflow definition model"""
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    trigger_type = Column(SQLEnum(WorkflowTriggerType), nullable=False)
    trigger_config = Column(JSON)  # Trigger-specific configuration
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")

class WorkflowStep(Base):
    """Individual step in a workflow"""
    __tablename__ = "workflow_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    name = Column(String, nullable=False)
    action_type = Column(SQLEnum(WorkflowActionType), nullable=False)
    action_config = Column(JSON)  # Action-specific configuration
    order_index = Column(Integer, nullable=False)
    is_conditional = Column(Boolean, default=False)
    condition_config = Column(JSON)  # Conditional logic configuration
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    executions = relationship("WorkflowStepExecution", back_populates="step", cascade="all, delete-orphan")

class WorkflowExecution(Base):
    """Workflow execution instance"""
    __tablename__ = "workflow_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(WorkflowExecutionStatus), default=WorkflowExecutionStatus.PENDING)
    trigger_data = Column(JSON)  # Data that triggered the workflow
    result_data = Column(JSON)  # Final result data
    error_message = Column(Text)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User")
    step_executions = relationship("WorkflowStepExecution", back_populates="execution", cascade="all, delete-orphan")

class WorkflowStepExecution(Base):
    """Individual step execution within a workflow"""
    __tablename__ = "workflow_step_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("workflow_executions.id"), nullable=False)
    step_id = Column(String, ForeignKey("workflow_steps.id"), nullable=False)
    status = Column(SQLEnum(WorkflowExecutionStatus), default=WorkflowExecutionStatus.PENDING)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="step_executions")
    step = relationship("WorkflowStep", back_populates="executions")

class AuditLogLevel(str, Enum):
    """Audit log levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditLogCategory(str, Enum):
    """Audit log categories"""
    AUTHENTICATION = "authentication"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    WORKFLOW = "workflow"
    SYSTEM = "system"
    SECURITY = "security"
    USER_ACTION = "user_action"

class AuditLog(Base):
    """Audit log entry"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Null for system events
    category = Column(SQLEnum(AuditLogCategory), nullable=False)
    level = Column(SQLEnum(AuditLogLevel), default=AuditLogLevel.INFO)
    action = Column(String, nullable=False)
    resource_type = Column(String)  # e.g., "user", "lead", "workflow"
    resource_id = Column(String)  # ID of the affected resource
    details = Column(JSON)  # Additional details about the action
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User") 
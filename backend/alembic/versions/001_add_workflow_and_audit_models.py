"""Add workflow and audit models

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workflows table
    op.create_table('workflows',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger_type', sa.Enum('MANUAL', 'SCHEDULED', 'EVENT_BASED', 'WEBHOOK', 'CONDITION', name='workflowtriggertype'), nullable=False),
        sa.Column('trigger_config', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'DRAFT', 'ARCHIVED', name='workflowstatus'), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create workflow_steps table
    op.create_table('workflow_steps',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('action_type', sa.Enum('SEND_EMAIL', 'CREATE_TASK', 'UPDATE_CRM', 'SEND_NOTIFICATION', 'EXECUTE_AGENT', 'GENERATE_REPORT', 'UPDATE_STATUS', 'CUSTOM_SCRIPT', name='workflowactiontype'), nullable=False),
        sa.Column('action_config', sa.JSON(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_conditional', sa.Boolean(), nullable=True),
        sa.Column('condition_config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create workflow_executions table
    op.create_table('workflow_executions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='workflowexecutionstatus'), nullable=True),
        sa.Column('trigger_data', sa.JSON(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create workflow_step_executions table
    op.create_table('workflow_step_executions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('execution_id', sa.String(), nullable=False),
        sa.Column('step_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='workflowexecutionstatus'), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['workflow_executions.id'], ),
        sa.ForeignKeyConstraint(['step_id'], ['workflow_steps.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('category', sa.Enum('AUTHENTICATION', 'DATA_ACCESS', 'DATA_MODIFICATION', 'WORKFLOW', 'SYSTEM', 'SECURITY', 'USER_ACTION', name='auditlogcategory'), nullable=False),
        sa.Column('level', sa.Enum('INFO', 'WARNING', 'ERROR', 'CRITICAL', name='auditloglevel'), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('workflow_step_executions')
    op.drop_table('workflow_executions')
    op.drop_table('workflow_steps')
    op.drop_table('workflows')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS workflowtriggertype')
    op.execute('DROP TYPE IF EXISTS workflowstatus')
    op.execute('DROP TYPE IF EXISTS workflowactiontype')
    op.execute('DROP TYPE IF EXISTS workflowexecutionstatus')
    op.execute('DROP TYPE IF EXISTS auditlogcategory')
    op.execute('DROP TYPE IF EXISTS auditloglevel') 
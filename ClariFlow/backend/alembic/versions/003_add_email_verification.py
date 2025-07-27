"""Add email verification fields

Revision ID: 003
Revises: 002_add_core_models
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_core_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email verification fields to users table
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove email verification fields from users table
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'is_email_verified') 
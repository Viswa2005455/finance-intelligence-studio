"""feedback notes from the in-app button

Revision ID: b7c1e2a4d9f3
Revises: 9d3e5f7a1b20
Create Date: 2026-11-26 19:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b7c1e2a4d9f3'
down_revision: Union[str, Sequence[str], None] = '9d3e5f7a1b20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('feedback',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('page', sa.String(length=200), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('details', sa.Text(), nullable=False),
    sa.Column('user_agent', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_user_id'), 'feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_feedback_created_at'), 'feedback', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feedback_created_at'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_user_id'), table_name='feedback')
    op.drop_table('feedback')

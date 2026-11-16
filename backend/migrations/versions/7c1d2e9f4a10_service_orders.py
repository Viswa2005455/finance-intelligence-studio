"""service orders: one row per paid order from the public services pages

Revision ID: 7c1d2e9f4a10
Revises: 43a2e23540e6
Create Date: 2026-11-16 01:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '7c1d2e9f4a10'
down_revision: Union[str, Sequence[str], None] = '43a2e23540e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('service_orders',
    sa.Column('payment_id', sa.String(length=64), nullable=False),
    sa.Column('payment_link_id', sa.String(length=64), nullable=False),
    sa.Column('service', sa.String(length=160), nullable=False),
    sa.Column('package', sa.String(length=16), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('customer_name', sa.String(length=120), nullable=False),
    sa.Column('customer_email', sa.String(length=254), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('customer_emailed', sa.Boolean(), nullable=False),
    sa.Column('owner_emailed', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('payment_id')
    )
    op.create_index(op.f('ix_service_orders_created_at'), 'service_orders', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_service_orders_created_at'), table_name='service_orders')
    op.drop_table('service_orders')

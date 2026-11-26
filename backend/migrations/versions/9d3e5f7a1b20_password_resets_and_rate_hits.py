"""password resets and durable rate-limit hits

Revision ID: 9d3e5f7a1b20
Revises: 7c1d2e9f4a10
Create Date: 2026-11-26 17:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9d3e5f7a1b20'
down_revision: Union[str, Sequence[str], None] = '7c1d2e9f4a10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('password_resets',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_password_resets_user_id'), 'password_resets', ['user_id'], unique=False)
    op.create_index(op.f('ix_password_resets_expires_at'), 'password_resets', ['expires_at'], unique=False)
    op.create_table('rate_hits',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('key', sa.String(length=200), nullable=False),
    sa.Column('hit_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rate_hits_key'), 'rate_hits', ['key'], unique=False)
    op.create_index(op.f('ix_rate_hits_hit_at'), 'rate_hits', ['hit_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_rate_hits_hit_at'), table_name='rate_hits')
    op.drop_index(op.f('ix_rate_hits_key'), table_name='rate_hits')
    op.drop_table('rate_hits')
    op.drop_index(op.f('ix_password_resets_expires_at'), table_name='password_resets')
    op.drop_index(op.f('ix_password_resets_user_id'), table_name='password_resets')
    op.drop_table('password_resets')

"""create page_visits table

Revision ID: a1b2c3d4e5f6
Revises: 38755cd5500a
Create Date: 2026-05-12 08:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '38755cd5500a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'page_visits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_page_visits_created_at', 'page_visits', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_page_visits_created_at', 'page_visits')
    op.drop_table('page_visits')

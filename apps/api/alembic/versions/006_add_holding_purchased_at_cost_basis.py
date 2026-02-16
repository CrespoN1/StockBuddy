"""add purchased_at and cost_basis to holding

Revision ID: 006
Revises: 005
"""
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("holding", sa.Column("purchased_at", sa.Date(), nullable=True))
    op.add_column("holding", sa.Column("cost_basis", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("holding", "cost_basis")
    op.drop_column("holding", "purchased_at")

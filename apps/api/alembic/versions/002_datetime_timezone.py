"""add timezone to datetime columns

Revision ID: 002
Revises: 001
Create Date: 2026-02-12 02:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All datetime columns that need timezone awareness
COLUMNS = [
    ("portfolio", "created_at"),
    ("portfolio", "updated_at"),
    ("holding", "created_at"),
    ("holding", "updated_at"),
    ("holding", "latest_earnings_call"),
    ("earnings_call", "call_date"),
    ("earnings_call", "created_at"),
    ("portfolio_snapshot", "created_at"),
    ("analysis_job", "created_at"),
    ("analysis_job", "started_at"),
    ("analysis_job", "completed_at"),
]


def upgrade() -> None:
    for table, column in COLUMNS:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(timezone=True),
            existing_type=sa.DateTime(),
            existing_nullable=column not in ("created_at", "updated_at"),
        )


def downgrade() -> None:
    for table, column in COLUMNS:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=column not in ("created_at", "updated_at"),
        )

"""add subscription table

Revision ID: 003
Revises: 002
Create Date: 2026-02-12 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
        sa.Column("plan", sa.String(), nullable=False, server_default="free"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("earnings_analysis_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("portfolio_analysis_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("usage_reset_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_subscription_user_id", "subscription", ["user_id"], unique=True)
    op.create_index("ix_subscription_stripe_customer_id", "subscription", ["stripe_customer_id"])
    op.create_index("ix_subscription_stripe_subscription_id", "subscription", ["stripe_subscription_id"])


def downgrade() -> None:
    op.drop_index("ix_subscription_stripe_subscription_id")
    op.drop_index("ix_subscription_stripe_customer_id")
    op.drop_index("ix_subscription_user_id")
    op.drop_table("subscription")

"""add price_alert table and holding next_earnings_date

Revision ID: 005
Revises: 004
"""
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Feature 6: Price Alerts
    op.create_table(
        "price_alert",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("target_price", sa.Float(), nullable=False),
        sa.Column("direction", sa.String(), nullable=False),  # "above" or "below"
        sa.Column(
            "triggered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("triggered_price", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_price_alert_user_id", "price_alert", ["user_id"])
    op.create_index("ix_price_alert_ticker", "price_alert", ["ticker"])

    # Feature 7: Earnings Calendar — add next_earnings_date to holding
    op.add_column(
        "holding",
        sa.Column("next_earnings_date", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("holding", "next_earnings_date")
    op.drop_index("ix_price_alert_ticker")
    op.drop_index("ix_price_alert_user_id")
    op.drop_table("price_alert")

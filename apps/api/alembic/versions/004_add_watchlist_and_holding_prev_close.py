"""add watchlist table and holding previous_close

Revision ID: 004
Revises: 003
"""
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "watchlist_item",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("last_price", sa.Float(), nullable=True),
        sa.Column("previous_close", sa.Float(), nullable=True),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_watchlist_item_user_id", "watchlist_item", ["user_id"])
    op.create_index("ix_watchlist_item_ticker", "watchlist_item", ["ticker"])
    op.create_unique_constraint(
        "uq_watchlist_user_ticker", "watchlist_item", ["user_id", "ticker"]
    )

    # Add previous_close to holding table for daily % change feature
    op.add_column("holding", sa.Column("previous_close", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("holding", "previous_close")
    op.drop_constraint("uq_watchlist_user_ticker", "watchlist_item")
    op.drop_index("ix_watchlist_item_ticker")
    op.drop_index("ix_watchlist_item_user_id")
    op.drop_table("watchlist_item")

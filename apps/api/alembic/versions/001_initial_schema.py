"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Portfolio ---
    op.create_table(
        "portfolio",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # --- Holding ---
    op.create_table(
        "holding",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column(
            "portfolio_id",
            sa.Integer(),
            sa.ForeignKey("portfolio.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("ticker", sa.String(), nullable=False, index=True),
        sa.Column("shares", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_price", sa.Float(), nullable=True),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column("beta", sa.Float(), nullable=True),
        sa.Column("dividend_yield", sa.Float(), nullable=True),
        sa.Column("latest_earnings_call", sa.DateTime(), nullable=True),
        sa.Column("earnings_call_summary", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # --- EarningsCall ---
    op.create_table(
        "earnings_call",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column(
            "holding_id",
            sa.Integer(),
            sa.ForeignKey("holding.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("ticker", sa.String(), nullable=False, index=True),
        sa.Column("call_date", sa.DateTime(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_metrics", postgresql.JSONB(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("risk_mentions", sa.Integer(), nullable=True),
        sa.Column("growth_mentions", sa.Integer(), nullable=True),
        sa.Column("guidance_outlook", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- PortfolioSnapshot ---
    op.create_table(
        "portfolio_snapshot",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column(
            "portfolio_id",
            sa.Integer(),
            sa.ForeignKey("portfolio.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("total_value", sa.Float(), nullable=True),
        sa.Column("num_positions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recent_earnings_coverage", sa.Float(), nullable=True),
        sa.Column("avg_sentiment_score", sa.Float(), nullable=True),
        sa.Column("risk_exposure_score", sa.Float(), nullable=True),
        sa.Column("health_score", sa.Integer(), nullable=True),
        sa.Column("concentration_risk", sa.Float(), nullable=True),
    )

    # --- AnalysisJob ---
    op.create_table(
        "analysis_job",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("job_type", sa.String(), nullable=False),
        sa.Column(
            "status", sa.String(), nullable=False, server_default="pending", index=True
        ),
        sa.Column("input_data", postgresql.JSONB(), nullable=True),
        sa.Column("result", postgresql.JSONB(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("analysis_job")
    op.drop_table("portfolio_snapshot")
    op.drop_table("earnings_call")
    op.drop_table("holding")
    op.drop_table("portfolio")

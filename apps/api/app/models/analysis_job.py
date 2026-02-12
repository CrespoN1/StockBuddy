import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AnalysisJob(SQLModel, table=True):
    """Tracks async AI analysis jobs (portfolio analysis, earnings analysis, comparison)."""

    __tablename__ = "analysis_job"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    job_type: str  # "portfolio_analysis", "earnings_analysis", "comparison", "technical"
    status: str = Field(default="pending", index=True)  # pending, processing, completed, failed

    input_data: dict | None = Field(default=None, sa_column=Column(JSONB))
    result: dict | None = Field(default=None, sa_column=Column(JSONB))
    error: str | None = Field(default=None, sa_column=Column(Text))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )
    started_at: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))
    completed_at: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))

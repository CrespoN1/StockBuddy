"""
arq worker configuration.

Usage:
    arq worker.WorkerSettings
"""

from arq.connections import RedisSettings

from app.config import settings
from app.workers.tasks import run_earnings_analysis, run_portfolio_analysis, run_comparison


class WorkerSettings:
    """arq worker settings — connects tasks to Redis."""

    functions = [run_earnings_analysis, run_portfolio_analysis, run_comparison]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 10
    job_timeout = 300  # 5 minutes for DeepSeek retries

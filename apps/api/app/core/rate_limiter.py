"""
Per-user rate limiting using slowapi.

Limits are configurable via environment variables (see config.py).
Defaults:
- General endpoints: 100 requests/minute
- AI analysis endpoints: 10 requests/minute (expensive operations)
- Search endpoints: 30 requests/minute
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(key_func=get_remote_address)

GENERAL_LIMIT = settings.general_rate_limit
AI_LIMIT = settings.ai_rate_limit
SEARCH_LIMIT = settings.search_rate_limit

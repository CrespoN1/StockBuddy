"""
Shared FastAPI dependencies: database sessions, authentication, and job queue.
"""

import jwt
import structlog
from arq import ArqRedis
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import get_user_id_from_token
from app.database import get_db

logger = structlog.stdlib.get_logger(__name__)

# HTTPBearer extracts "Bearer <token>" from the Authorization header.
# auto_error=False lets us handle missing tokens ourselves for better error messages.
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """Extract and verify the Clerk user ID from the Authorization header.

    In development mode (when CLERK_JWKS_URL is not set), returns a
    placeholder "dev-user" so endpoints can be tested without Clerk.

    Returns the Clerk user ID string (the JWT 'sub' claim).
    """
    # ── Dev mode: skip auth when Clerk is not configured ──
    if not settings.clerk_jwks_url:
        return "dev-user"

    # ── Production: require and verify JWT ──
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = get_user_id_from_token(credentials.credentials)
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid JWT: %s", exc)
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_arq_pool(request: Request) -> ArqRedis:
    """Retrieve the arq Redis connection pool stored on app state."""
    return request.app.state.arq_pool

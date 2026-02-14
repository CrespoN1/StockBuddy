import uuid
from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from app.api.routers import alerts, analysis, billing, earnings, holdings, portfolios, stocks, watchlist
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.rate_limiter import limiter

# ─── Initialize logging (must be before anything else) ────────────────
setup_logging()
logger = structlog.stdlib.get_logger(__name__)

# ─── Initialize Sentry ────────────────────────────────────────────────
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1 if settings.environment == "production" else 1.0,
        profiles_sample_rate=0.1,
        send_default_pii=False,
    )
    logger.info("Sentry initialized", environment=settings.environment)


# ─── Request context middleware ───────────────────────────────────────
class RequestContextMiddleware(BaseHTTPMiddleware):
    """Bind a unique request_id into structlog context for every request."""

    async def dispatch(
        self, request: StarletteRequest, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


# ─── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — validate production config
    settings.validate_production()

    # Startup — create arq Redis connection pool
    try:
        redis_settings = RedisSettings.from_dsn(settings.redis_url)
        app.state.arq_pool = await create_pool(redis_settings)
        logger.info("arq connection pool created")
    except Exception as exc:
        logger.warning("Could not connect to Redis, arq jobs disabled", error=str(exc))
        app.state.arq_pool = None

    yield

    # Shutdown — close arq pool and DB engine
    if app.state.arq_pool is not None:
        await app.state.arq_pool.close()
        logger.info("arq connection pool closed")

    from app.database import engine

    await engine.dispose()


# ─── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="StockBuddy API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# ─── Exception Handlers ──────────────────────────────────────────────
register_exception_handlers(app)

# ─── Rate Limiting ────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Middleware (order matters: last added = first executed) ──────────
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(portfolios.router, prefix=API_PREFIX)
app.include_router(holdings.router, prefix=API_PREFIX)
app.include_router(stocks.router, prefix=API_PREFIX)
app.include_router(earnings.router, prefix=API_PREFIX)
app.include_router(analysis.router, prefix=API_PREFIX)
app.include_router(billing.router, prefix=API_PREFIX)
app.include_router(watchlist.router, prefix=API_PREFIX)
app.include_router(alerts.router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

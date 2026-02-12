"""
Test fixtures for StockBuddy API.

Uses in-memory SQLite via aiosqlite. Overrides auth (always "test-user"),
database session, and arq pool (AsyncMock). Registers a JSONB → JSON
compiler so PostgreSQL-specific columns work with SQLite.
"""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.api.deps import get_arq_pool, get_current_user
from app.database import get_db

# ─── JSONB → JSON for SQLite ─────────────────────────────────────────
# PostgreSQL JSONB columns need to render as plain JSON in SQLite tests.


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return compiler.visit_JSON(JSON(), **kw)


# ─── Test database (in-memory SQLite) ─────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    # Import models so metadata is populated
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# ─── Override app lifespan to skip Redis ──────────────────────────────

@asynccontextmanager
async def test_lifespan(app_instance):
    """Test lifespan that skips Redis/arq pool creation."""
    app_instance.state.arq_pool = AsyncMock()
    yield


# Import app AFTER the JSONB compiler is registered
from app.main import app  # noqa: E402

# Replace lifespan so tests don't need a running Redis
app.router.lifespan_context = test_lifespan


# ─── Dependency overrides ─────────────────────────────────────────────

async def override_get_db():
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def override_get_current_user():
    return "test-user"


async def override_get_arq_pool():
    mock_pool = AsyncMock()
    mock_pool.enqueue_job = AsyncMock(return_value=MagicMock(job_id="test-job-id"))
    return mock_pool


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_arq_pool] = override_get_arq_pool


# ─── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def db():
    async with TestSession() as session:
        yield session

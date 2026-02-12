import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_subscription_default_free(client: AsyncClient):
    """New users should get a free plan by default."""
    resp = await client.get("/api/v1/billing/subscription")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "free"
    # MVP: limits are None (unlimited) for free tier
    assert data["earnings_analysis_limit"] is None
    assert data["portfolio_analysis_limit"] is None
    assert data["portfolio_limit"] is None
    assert data["holdings_per_portfolio_limit"] is None


@pytest.mark.asyncio
async def test_get_usage_defaults(client: AsyncClient):
    """New free user should have all usage at zero with everything unlocked (MVP)."""
    resp = await client.get("/api/v1/billing/usage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "free"
    assert data["earnings_analysis_used"] == 0
    assert data["portfolio_analysis_used"] == 0
    assert data["can_create_portfolio"] is True
    assert data["can_analyze_earnings"] is True
    assert data["can_analyze_portfolio"] is True
    # MVP: all features unlocked for free users
    assert data["can_compare"] is True
    assert data["can_forecast"] is True
    assert data["can_export_csv"] is True


@pytest.mark.asyncio
async def test_free_user_can_create_multiple_portfolios(client: AsyncClient):
    """MVP: free users can create unlimited portfolios."""
    resp1 = await client.post("/api/v1/portfolios", json={"name": "First"})
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/portfolios", json={"name": "Second"})
    assert resp2.status_code == 201


@pytest.mark.asyncio
async def test_free_user_can_compare(client: AsyncClient):
    """MVP: free users can access comparison (returns 202 for the job)."""
    resp = await client.post(
        "/api/v1/analysis/compare",
        json={"tickers": ["AAPL", "MSFT"]},
    )
    # 202 = job created (not 403)
    assert resp.status_code == 202


@pytest.mark.asyncio
async def test_checkout_returns_503_without_stripe(client: AsyncClient):
    """Checkout should fail gracefully when Stripe is not configured."""
    resp = await client.post("/api/v1/billing/checkout")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_portal_returns_503_without_stripe(client: AsyncClient):
    """Portal should fail gracefully when Stripe is not configured."""
    resp = await client.post("/api/v1/billing/portal")
    assert resp.status_code == 503

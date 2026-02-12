import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_subscription_default_free(client: AsyncClient):
    """New users should get a free plan by default."""
    resp = await client.get("/api/v1/billing/subscription")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "free"
    assert data["earnings_analysis_limit"] == 3
    assert data["portfolio_analysis_limit"] == 1
    assert data["portfolio_limit"] == 1
    assert data["holdings_per_portfolio_limit"] == 10


@pytest.mark.asyncio
async def test_get_usage_defaults(client: AsyncClient):
    """New free user should have all usage at zero."""
    resp = await client.get("/api/v1/billing/usage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "free"
    assert data["earnings_analysis_used"] == 0
    assert data["portfolio_analysis_used"] == 0
    assert data["can_create_portfolio"] is True  # 0 < 1
    assert data["can_analyze_earnings"] is True  # 0 < 3
    assert data["can_analyze_portfolio"] is True  # 0 < 1
    assert data["can_compare"] is False
    assert data["can_forecast"] is False
    assert data["can_export_csv"] is False


@pytest.mark.asyncio
async def test_free_user_portfolio_limit(client: AsyncClient):
    """Free user should be blocked from creating a 2nd portfolio."""
    resp1 = await client.post("/api/v1/portfolios", json={"name": "First"})
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/portfolios", json={"name": "Second"})
    assert resp2.status_code == 403
    assert "Upgrade to Pro" in resp2.json()["detail"]


@pytest.mark.asyncio
async def test_free_user_compare_blocked(client: AsyncClient):
    """Free user should not be able to compare stocks."""
    resp = await client.post(
        "/api/v1/analysis/compare",
        json={"tickers": ["AAPL", "MSFT"]},
    )
    assert resp.status_code == 403
    assert "Pro plan" in resp.json()["detail"]


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

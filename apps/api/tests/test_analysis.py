import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_portfolio_enqueues_job(client: AsyncClient):
    # Create a portfolio first
    portfolio = await client.post("/api/v1/portfolios", json={"name": "Test"})
    pid = portfolio.json()["id"]
    resp = await client.post(f"/api/v1/analysis/portfolios/{pid}/analyze")
    assert resp.status_code == 202
    data = resp.json()
    assert data["job_type"] == "portfolio_analysis"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_compare_enqueues_job(client: AsyncClient):
    resp = await client.post(
        "/api/v1/analysis/compare",
        json={"tickers": ["AAPL", "MSFT"]},
    )
    assert resp.status_code == 202
    data = resp.json()
    assert data["job_type"] == "comparison"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/analysis/jobs/nonexistent-uuid")
    assert resp.status_code == 404

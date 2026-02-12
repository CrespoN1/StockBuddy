import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_earnings_empty(client: AsyncClient):
    resp = await client.get("/api/v1/stocks/AAPL/earnings")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_analyze_earnings_enqueues_job(client: AsyncClient):
    resp = await client.post(
        "/api/v1/stocks/AAPL/earnings/analyze",
        json={"transcript": "This is a test transcript for earnings analysis."},
    )
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "pending"
    assert data["job_type"] == "earnings_analysis"
    assert "id" in data


@pytest.mark.asyncio
async def test_analyze_earnings_no_transcript(client: AsyncClient):
    """Enqueue without transcript — worker will attempt FMP fetch."""
    resp = await client.post(
        "/api/v1/stocks/AAPL/earnings/analyze",
        json={},
    )
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "pending"

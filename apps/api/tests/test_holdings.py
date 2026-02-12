import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient


@pytest.fixture
def mock_market_data():
    with patch("app.services.portfolio.market_data") as mock:
        mock.get_stock_fundamentals = AsyncMock(
            return_value={
                "sector": "Technology",
                "beta": 1.2,
                "dividend_yield": 0.01,
                "price": None,
                "currency": "USD",
                "next_earnings_date": None,
                "market_cap": None,
                "pe_ratio": None,
            }
        )
        mock.get_latest_price = AsyncMock(return_value=150.0)
        yield mock


@pytest.mark.asyncio
async def test_add_holding(client: AsyncClient, mock_market_data):
    portfolio = await client.post("/api/v1/portfolios", json={"name": "P1"})
    pid = portfolio.json()["id"]
    resp = await client.post(
        f"/api/v1/portfolios/{pid}/holdings",
        json={"ticker": "AAPL", "shares": 10},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert data["shares"] == 10.0


@pytest.mark.asyncio
async def test_list_holdings(client: AsyncClient, mock_market_data):
    portfolio = await client.post("/api/v1/portfolios", json={"name": "P1"})
    pid = portfolio.json()["id"]
    await client.post(
        f"/api/v1/portfolios/{pid}/holdings",
        json={"ticker": "AAPL", "shares": 10},
    )
    resp = await client.get(f"/api/v1/portfolios/{pid}/holdings")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_holding(client: AsyncClient, mock_market_data):
    portfolio = await client.post("/api/v1/portfolios", json={"name": "P1"})
    pid = portfolio.json()["id"]
    holding = await client.post(
        f"/api/v1/portfolios/{pid}/holdings",
        json={"ticker": "AAPL", "shares": 10},
    )
    hid = holding.json()["id"]
    resp = await client.delete(f"/api/v1/portfolios/{pid}/holdings/{hid}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_add_holding_portfolio_not_found(client: AsyncClient, mock_market_data):
    resp = await client.post(
        "/api/v1/portfolios/9999/holdings",
        json={"ticker": "AAPL", "shares": 10},
    )
    assert resp.status_code == 404

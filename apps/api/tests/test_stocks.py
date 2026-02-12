import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_stocks(client: AsyncClient):
    with patch("app.api.routers.stocks.search") as mock_search:
        mock_search.search_tickers = AsyncMock(
            return_value=[{"ticker": "AAPL", "name": "Apple Inc.", "type": "CS"}]
        )
        resp = await client.get("/api/v1/stocks/search", params={"q": "AAPL"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_stock_info(client: AsyncClient):
    with patch("app.api.routers.stocks.stock_data") as mock_sd:
        mock_sd.get_stock_info = AsyncMock(
            return_value={
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": "3.00T",
                "summary": "Apple Inc. designs...",
            }
        )
        resp = await client.get("/api/v1/stocks/AAPL")
        assert resp.status_code == 200
        assert resp.json()["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_stock_info_not_found(client: AsyncClient):
    with patch("app.api.routers.stocks.stock_data") as mock_sd:
        mock_sd.get_stock_info = AsyncMock(return_value=None)
        resp = await client.get("/api/v1/stocks/FAKEXYZ")
        assert resp.status_code == 404

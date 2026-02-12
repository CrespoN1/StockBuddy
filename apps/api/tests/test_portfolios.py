import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_portfolio(client: AsyncClient):
    resp = await client.post("/api/v1/portfolios", json={"name": "Test Portfolio"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Portfolio"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_portfolios(client: AsyncClient):
    """Free plan allows 1 portfolio — verify listing works."""
    await client.post("/api/v1/portfolios", json={"name": "A"})
    resp = await client.get("/api/v1/portfolios")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_get_portfolio(client: AsyncClient):
    create = await client.post("/api/v1/portfolios", json={"name": "Detail"})
    pid = create.json()["id"]
    resp = await client.get(f"/api/v1/portfolios/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Detail"


@pytest.mark.asyncio
async def test_get_portfolio_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/portfolios/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_portfolio(client: AsyncClient):
    create = await client.post("/api/v1/portfolios", json={"name": "Old"})
    pid = create.json()["id"]
    resp = await client.put(f"/api/v1/portfolios/{pid}", json={"name": "New"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_portfolio(client: AsyncClient):
    create = await client.post("/api/v1/portfolios", json={"name": "ToDelete"})
    pid = create.json()["id"]
    resp = await client.delete(f"/api/v1/portfolios/{pid}")
    assert resp.status_code == 204
    resp2 = await client.get(f"/api/v1/portfolios/{pid}")
    assert resp2.status_code == 404

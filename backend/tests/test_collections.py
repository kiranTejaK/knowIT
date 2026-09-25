import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_collections_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/api/v1/collections")
    assert response.status_code == 401

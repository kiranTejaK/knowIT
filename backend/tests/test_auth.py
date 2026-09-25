import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"


@pytest.mark.asyncio
async def test_signup_validation(async_client: AsyncClient):
    # Invalid email format validation test
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "not-an-email", "password": "short"}
    )
    assert response.status_code == 422

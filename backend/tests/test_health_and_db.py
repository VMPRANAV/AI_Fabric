import pytest

@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Fabric"
    assert "connected" in data["database"]

@pytest.mark.asyncio
async def test_models_endpoint_auto_seeding(client):
    response = await client.get("/api/v1/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) >= 4
    model_names = [m["name"] for m in models]
    assert "openai/gpt-oss-120b" in model_names
    assert "mock-deterministic-v1" in model_names

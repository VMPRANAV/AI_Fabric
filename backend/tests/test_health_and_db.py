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
    assert "llama-3.3-70b-versatile" in model_names
    assert "llama-3.1-8b-instant" in model_names

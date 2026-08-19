import pytest
from app.services.model_gateway.mock_adapter import MockAdapter
from app.services.model_gateway.groq_adapter import GroqAdapter
from app.services.model_gateway.gateway import model_gateway
from app.core.config import settings

@pytest.mark.asyncio
async def test_mock_adapter_execution():
    adapter = MockAdapter()
    res = await adapter.generate(
        prompt="Analyze slow SQL query on orders table",
        model="mock-deterministic-v1",
        model_profile="balanced"
    )
    assert res.success is True
    assert res.provider == "mock"
    assert res.estimated_cost == 0.0
    assert res.input_tokens > 0
    assert res.output_tokens > 0
    assert res.latency_ms > 0
    assert "SQL Performance" in res.content

@pytest.mark.asyncio
async def test_groq_adapter_unconfigured_auth_error(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "your_groq_api_key_here")
    adapter = GroqAdapter()
    res = await adapter.generate(
        prompt="Test prompt",
        model="llama-3.3-70b-versatile"
    )
    # When API key is placeholder or unconfigured
    assert res.success is False
    assert "AuthenticationError" in res.error_type

@pytest.mark.asyncio
async def test_model_fallback_disabled_by_default(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "your_groq_api_key_here")
    monkeypatch.setattr(settings, "MODEL_FALLBACK_ENABLED", False)
    # Attempting execution with Groq adapter when fallback is disabled
    res = await model_gateway.execute(
        prompt="Test prompt",
        model="llama-3.3-70b-versatile",
        provider="groq"
    )
    assert res.success is False
    assert "AuthenticationError" in res.error_type
    assert "FallbackExecuted" not in (res.error_type or "")

@pytest.mark.asyncio
async def test_models_generate_api_endpoint(client):
    payload = {
        "prompt": "Optimize SELECT * FROM users WHERE status = 'pending'",
        "model": "mock-deterministic-v1",
        "model_profile": "balanced"
    }
    response = await client.post("/api/v1/models/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["provider"] == "mock"
    assert data["estimated_cost"] == 0.0

@pytest.mark.asyncio
async def test_end_to_end_mock_pipeline(client):
    payload = {
        "query": "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement.",
        "routing_strategy": "rule_based",
        "budget": "medium"
    }
    response = await client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert len(data["trace"]) == 6
    assert data["trace"][0]["stage"] == "Prompt Gateway"
    assert data["trace"][1]["stage"] == "Query Analyzer"
    assert data["trace"][2]["stage"] == "Decision Engine"
    assert data["trace"][3]["stage"] == "MCP Gateway"
    assert data["trace"][4]["stage"] == "Model Gateway"
    assert data["trace"][5]["stage"] == "Observability & Feedback"
    assert data["selected_model"] == settings.AI_MODEL_REASONING

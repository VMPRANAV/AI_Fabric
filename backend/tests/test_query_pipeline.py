import pytest

@pytest.mark.asyncio
async def test_execute_query_pipeline(client):
    payload = {
        "query": "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement.",
        "routing_strategy": "rule_based",
        "budget": "medium"
    }
    response = await client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["task_type"] == "sql_analysis_optimization"
    assert data["complexity"] > 0.8
    assert len(data["trace"]) == 6
    assert data["trace"][0]["stage"] == "Prompt Gateway"
    assert data["trace"][1]["stage"] == "Query Analyzer"
    assert data["trace"][2]["stage"] == "Decision Engine"
    assert data["trace"][3]["stage"] == "MCP Gateway"
    assert data["trace"][4]["stage"] == "Model Gateway"
    assert data["trace"][5]["stage"] == "Observability & Feedback"
    assert "CREATE INDEX" in data["response_text"]
    assert data["reward"] > 0

@pytest.mark.asyncio
async def test_metrics_summary(client):
    # Fetch summary
    response = await client.get("/api/v1/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "avg_latency_ms" in data
    assert "routing_distribution" in data

import pytest
from app.services.query_analyzer.service import query_analyzer_service
from app.schemas.analyzer import QueryAnalysisRequest

def test_task_classification_all_categories():
    # 1. SQL Analysis & Optimization
    res_sql = query_analyzer_service.analyze(QueryAnalysisRequest(query="Analyze the slow SELECT query with JOIN and GROUP BY on orders table"))
    assert res_sql.task_type == "sql_analysis_optimization"
    assert res_sql.task_type_idx == 0
    assert res_sql.tool_required is True

    # 2. Repository Architecture
    res_repo = query_analyzer_service.analyze(QueryAnalysisRequest(query="Inspect GitHub repository directory structure and module dependencies"))
    assert res_repo.task_type == "repo_architecture"
    assert res_repo.task_type_idx == 1
    assert res_repo.tool_required is True
    assert res_repo.tool_type == "github_mcp"

    # 3. Code Generation
    res_code = query_analyzer_service.analyze(QueryAnalysisRequest(query="Write a Python script to parse JSON and create an API endpoint"))
    assert res_code.task_type == "code_generation"
    assert res_code.task_type_idx == 2
    assert res_code.tool_required is False
    assert res_code.tool_type == "none"

    # 4. General Reasoning
    res_gen = query_analyzer_service.analyze(QueryAnalysisRequest(query="What are the key benefits of asynchronous I/O in distributed systems?"))
    assert res_gen.task_type == "general_reasoning"
    assert res_gen.task_type_idx == 3
    assert res_gen.tool_required is False
    assert res_gen.tool_type == "none"

def test_complexity_bounds_and_explainable_factors():
    query_text = "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement."
    res = query_analyzer_service.analyze(QueryAnalysisRequest(query=query_text))
    
    # 1. Bound check
    assert 0.0 <= res.complexity <= 1.0
    
    # 2. Explainable factors
    assert "task_base_weight" in res.complexity_factors
    assert "length_factor" in res.complexity_factors
    assert "sql_factor" in res.complexity_factors
    assert "structural_factor" in res.complexity_factors
    assert "reasoning_factor" in res.complexity_factors

def test_exact_6d_state_vector():
    res = query_analyzer_service.analyze(
        QueryAnalysisRequest(
            query="Analyze slow SQL query with index scan",
            budget="high",
            latency_target="fast"
        )
    )
    sv = res.state_vector
    assert len(sv) == 6
    assert sv[0] == float(res.task_type_idx)
    assert sv[1] == float(res.complexity)
    assert sv[2] == float(res.budget_idx)  # high -> 2
    assert sv[3] == float(res.latency_idx) # fast -> 0
    assert sv[4] == float(res.tool_type_idx)
    assert sv[5] == float(res.reasoning_idx)

def test_deterministic_repeatability():
    req = QueryAnalysisRequest(query="Analyze slow SQL query", budget="medium", latency_target="normal")
    res1 = query_analyzer_service.analyze(req)
    res2 = query_analyzer_service.analyze(req)
    
    assert res1.task_type == res2.task_type
    assert res1.complexity == res2.complexity
    assert res1.state_vector == res2.state_vector

@pytest.mark.asyncio
async def test_analyze_api_endpoint(client):
    payload = {
        "query": "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement.",
        "budget": "medium",
        "latency_target": "normal"
    }
    response = await client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "sql_analysis_optimization"
    assert data["task_type_idx"] == 0
    assert 0.0 <= data["complexity"] <= 1.0
    assert data["tool_required"] is True
    assert data["tool_type"] in ["github_mcp", "database_mcp"]
    assert len(data["state_vector"]) == 6

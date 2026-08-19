import pytest
from app.services.decision_engine.rule_based import rule_based_decision_engine
from app.schemas.analyzer import QueryAnalysisResponse

def make_analysis_response(
    complexity: float = 0.5,
    reasoning_req: str = "medium",
    latency_target: str = "normal",
    budget: str = "medium",
    task_type: str = "sql_analysis_optimization"
) -> QueryAnalysisResponse:
    return QueryAnalysisResponse(
        query="Test query",
        normalized_query="test query",
        task_type=task_type,
        task_type_idx=0,
        complexity=complexity,
        complexity_factors={"test": 0.5},
        budget=budget,
        budget_idx=1 if budget == "medium" else (0 if budget == "low" else 2),
        latency_target=latency_target,
        latency_idx=1 if latency_target == "normal" else (0 if latency_target == "fast" else 2),
        tool_required=True,
        tool_type="github_mcp",
        tool_type_idx=1,
        reasoning_required=reasoning_req,
        reasoning_idx=2 if reasoning_req == "high" else (1 if reasoning_req == "medium" else 0),
        state_vector=[0.0, complexity, 1.0, 1.0, 1.0, 1.0]
    )

def test_high_complexity_routes_to_reasoning():
    analysis = make_analysis_response(complexity=0.85)
    decision = rule_based_decision_engine.route(analysis)
    assert decision.model_profile == "reasoning"
    assert decision.decision_source == "rule_based"
    assert any("complexity=0.85 >= 0.70" in r for r in decision.decision_reason)

def test_high_reasoning_req_routes_to_reasoning():
    analysis = make_analysis_response(complexity=0.40, reasoning_req="high")
    decision = rule_based_decision_engine.route(analysis)
    assert decision.model_profile == "reasoning"
    assert any("reasoning_required=high" in r for r in decision.decision_reason)

def test_fast_latency_target_routes_to_fast():
    analysis = make_analysis_response(complexity=0.45, latency_target="fast")
    decision = rule_based_decision_engine.route(analysis)
    assert decision.model_profile == "fast"
    assert any("latency_target=fast" in r for r in decision.decision_reason)

def test_low_budget_routes_to_fast():
    analysis = make_analysis_response(complexity=0.45, budget="low")
    decision = rule_based_decision_engine.route(analysis)
    assert decision.model_profile == "fast"
    assert any("budget=low" in r for r in decision.decision_reason)

def test_default_routes_to_balanced():
    analysis = make_analysis_response(complexity=0.55, budget="medium", latency_target="normal", reasoning_req="medium")
    decision = rule_based_decision_engine.route(analysis)
    assert decision.model_profile == "balanced"

def test_prompt_version_selection_rules():
    # Low complexity -> v1
    d1 = rule_based_decision_engine.route(make_analysis_response(complexity=0.30))
    assert d1.prompt_version == "v1"

    # Moderate complexity -> v2
    d2 = rule_based_decision_engine.route(make_analysis_response(complexity=0.60))
    assert d2.prompt_version == "v2"

    # High complexity -> v3
    d3 = rule_based_decision_engine.route(make_analysis_response(complexity=0.85))
    assert d3.prompt_version == "v3"

def test_preserves_state_vector_and_tool_requirements():
    analysis = make_analysis_response(complexity=0.80)
    decision = rule_based_decision_engine.route(analysis)
    assert decision.tool_required is True
    assert decision.tool_type == "github_mcp"
    assert decision.state_vector == analysis.state_vector

@pytest.mark.asyncio
async def test_route_api_endpoint(client):
    payload = {
        "query": "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement.",
        "budget": "medium",
        "latency_target": "normal"
    }
    response = await client.post("/api/v1/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision_source"] == "rule_based"
    assert data["model_profile"] == "reasoning"
    assert data["prompt_version"] == "v3"
    assert data["tool_required"] is True
    assert len(data["state_vector"]) == 6

from fastapi import APIRouter, HTTPException
from app.schemas.analyzer import QueryAnalysisRequest
from app.schemas.decision import RoutingDecision
from app.services.query_analyzer.service import query_analyzer_service
from app.services.decision_engine.rule_based import rule_based_decision_engine

router = APIRouter(prefix="", tags=["Decision Engine"])

@router.post("/route", response_model=RoutingDecision, summary="Predict Routing Decision (Layer 3)")
async def predict_route(req: QueryAnalysisRequest):
    """
    Executes Layer 3 Decision Engine routing predictions.
    Receives prompt, executes Layer 2 Query Analysis, applies deterministic rule-based
    routing heuristics, and returns an explainable RoutingDecision.
    MUST NOT invoke external LLM providers or MCP tools.
    """
    try:
        analysis = query_analyzer_service.analyze(req)
        decision = rule_based_decision_engine.route(analysis)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision Engine error: {str(e)}")

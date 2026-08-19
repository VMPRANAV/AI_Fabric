from fastapi import APIRouter, HTTPException
from app.schemas.analyzer import QueryAnalysisRequest, QueryAnalysisResponse
from app.services.query_analyzer.service import query_analyzer_service

router = APIRouter(prefix="", tags=["Query Analyzer"])

@router.post("/analyze", response_model=QueryAnalysisResponse, summary="Analyze Request Context (Layer 2)")
async def analyze_query(req: QueryAnalysisRequest):
    """
    Executes Layer 2 Query Analysis on normalized prompt output from Layer 1.
    Performs rule-based task classification, explainable complexity scoring,
    tool requirement detection, reasoning depth estimation, and constructs
    the exact 6-dimensional numerical state vector.
    """
    try:
        return query_analyzer_service.analyze(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query analysis failure: {str(e)}")

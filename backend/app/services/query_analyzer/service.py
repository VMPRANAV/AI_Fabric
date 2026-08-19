from typing import Dict, List
from app.schemas.analyzer import QueryAnalysisRequest, QueryAnalysisResponse
from app.schemas.prompt import PromptProcessRequest
from app.services.prompt_gateway.service import prompt_gateway_service
from app.services.query_analyzer.classifier import classify_task_and_tool
from app.services.query_analyzer.complexity import compute_complexity_and_reasoning

BUDGET_MAP: Dict[str, int] = {"low": 0, "medium": 1, "high": 2}
LATENCY_MAP: Dict[str, int] = {"fast": 0, "normal": 1, "unconstrained": 2}

class QueryAnalyzerService:
    """
    Query Analyzer (Layer 2) Service.
    Consumes output from Prompt Gateway (Layer 1), performs deterministic rule-based
    context analysis, computes explainable complexity factors, and constructs the exact
    6D state vector for the Decision Engine.
    """

    def analyze(self, req: QueryAnalysisRequest) -> QueryAnalysisResponse:
        # Step 1: Pass query through Prompt Gateway (Layer 1) for validation and normalization
        prompt_res = prompt_gateway_service.process(
            PromptProcessRequest(
                query=req.query,
                category=req.category_hint or "general_assistant"
            )
        )
        norm_query = prompt_res.normalized_query

        # Step 2: Task & Tool Classification (Deterministic Heuristics)
        task_type, task_idx, tool_req, tool_type, tool_idx = classify_task_and_tool(
            query_text=norm_query,
            category_hint=req.category_hint
        )

        # Step 3: Complexity & Reasoning Level Analysis
        complexity, complexity_factors, reasoning_level, reasoning_idx = compute_complexity_and_reasoning(
            query_text=norm_query,
            task_type=task_type
        )

        # Step 4: Map Budget & Latency Targets
        budget_str = (req.budget or "medium").lower()
        if budget_str not in BUDGET_MAP:
            budget_str = "medium"
        budget_idx = BUDGET_MAP[budget_str]

        latency_str = (req.latency_target or "normal").lower()
        if latency_str not in LATENCY_MAP:
            latency_str = "normal"
        latency_idx = LATENCY_MAP[latency_str]

        # Step 5: Construct Exact 6D State Vector
        state_vector: List[float] = [
            float(task_idx),
            float(complexity),
            float(budget_idx),
            float(latency_idx),
            float(tool_idx),
            float(reasoning_idx)
        ]

        return QueryAnalysisResponse(
            query=req.query,
            normalized_query=norm_query,
            task_type=task_type,
            task_type_idx=task_idx,
            complexity=complexity,
            complexity_factors=complexity_factors,
            budget=budget_str,
            budget_idx=budget_idx,
            latency_target=latency_str,
            latency_idx=latency_idx,
            tool_required=tool_req,
            tool_type=tool_type,
            tool_type_idx=tool_idx,
            reasoning_required=reasoning_level,
            reasoning_idx=reasoning_idx,
            state_vector=state_vector
        )

query_analyzer_service = QueryAnalyzerService()

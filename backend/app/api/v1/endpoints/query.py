import uuid
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from app.core.database import get_db
from app.schemas.query import QueryRequest, QueryResponse, ExecutionStageTrace
from app.models.request import RequestRecord
from app.models.routing import RoutingDecisionRecord
from app.models.metrics import ExecutionMetricRecord
from app.models.feedback import FeedbackRecord

from app.schemas.prompt import PromptProcessRequest
from app.services.prompt_gateway.service import prompt_gateway_service
from app.schemas.analyzer import QueryAnalysisRequest
from app.services.query_analyzer.service import query_analyzer_service
from app.services.decision_engine.model_selector import get_decision_engine
from app.services.model_gateway.gateway import model_gateway
from app.services.prompt_gateway.renderer import SafeTemplateRenderer
from app.services.observability.service import observability_service

router = APIRouter()

@router.post("/query", response_model=QueryResponse, summary="Execute AI Fabric Query Pipeline")
async def execute_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Core entrypoint for user queries.
    Executes the layered control plane pipeline:
    Prompt Gateway (Layer 1) ➜ Query Analyzer ➜ Decision Engine ➜ Gateways ➜ Observability & Feedback.
    """
    request_id = str(uuid.uuid4())
    await observability_service.start_trace(
        request_id,
        strategy=req.routing_strategy,
        task_type=None,
        prompt_version=None,
    )
    start_time = time.perf_counter()
    traces: list[ExecutionStageTrace] = []

    # 1. Prompt Gateway Stage (First Operational Layer)
    t0 = datetime.utcnow().isoformat() + "Z"
    is_sql_task = "sql" in req.query.lower() or "github" in req.query.lower()
    prompt_category = "sql_analysis" if is_sql_task else "general_assistant"
    prompt_version = "v1"

    prompt_proc = prompt_gateway_service.process(
        PromptProcessRequest(
            query=req.query,
            category=prompt_category,
            version=prompt_version,
            variables={"query": req.query, "context": "Live request context"},
        )
    )

    trace_pg = ExecutionStageTrace(
        stage="Prompt Gateway",
        status="completed" if prompt_proc.safety.is_valid else "failed",
        details={
            "is_valid": prompt_proc.safety.is_valid,
            "is_safe": prompt_proc.safety.is_safe,
            "risk_level": prompt_proc.safety.risk_level,
            "violations": prompt_proc.safety.violations,
            "template_category": prompt_proc.template_category,
            "version": prompt_proc.version,
            "character_count": prompt_proc.safety.character_count,
            "variables_injected": list(prompt_proc.variables_used.keys()),
        },
        timestamp=t0,
    )
    traces.append(trace_pg)
    await observability_service.record_stage(
        request_id,
        "Prompt Gateway",
        {
            "status": trace_pg.status,
            "is_valid": prompt_proc.safety.is_valid,
            "is_safe": prompt_proc.safety.is_safe,
            "risk_level": prompt_proc.safety.risk_level,
            "violations": prompt_proc.safety.violations,
            "template_category": prompt_proc.template_category,
            "version": prompt_proc.version,
            "character_count": prompt_proc.safety.character_count,
            "variables_injected": list(prompt_proc.variables_used.keys()),
        },
        status=trace_pg.status,
    )

    # 2. Query Analyzer Stage
    t1 = datetime.utcnow().isoformat() + "Z"
    analysis_res = query_analyzer_service.analyze(
        QueryAnalysisRequest(
            query=prompt_proc.normalized_query,
            budget=req.budget,
            category_hint=prompt_category,
        )
    )
    task_type = analysis_res.task_type
    complexity = analysis_res.complexity
    tool_required = analysis_res.tool_required
    tool_type = analysis_res.tool_type
    requires_tool = tool_type if tool_required else None

    trace_qa = ExecutionStageTrace(
        stage="Query Analyzer",
        status="completed",
        details={
            "task_type": task_type,
            "task_type_idx": analysis_res.task_type_idx,
            "complexity": complexity,
            "complexity_factors": analysis_res.complexity_factors,
            "budget": analysis_res.budget,
            "latency_target": analysis_res.latency_target,
            "tool_required": tool_required,
            "tool_type": tool_type,
            "reasoning_required": analysis_res.reasoning_required,
            "state_vector": analysis_res.state_vector,
        },
        timestamp=t1,
    )
    traces.append(trace_qa)
    await observability_service.record_stage(
        request_id,
        "Query Analyzer",
        trace_qa.details,
        status=trace_qa.status,
    )

    # 3. Decision Engine Stage
    t2 = datetime.utcnow().isoformat() + "Z"
    decision_engine = get_decision_engine()
    decision = decision_engine.route(analysis_res, request_id=request_id)

    trace_de = ExecutionStageTrace(
        stage="Decision Engine",
        status="completed",
        details={
            "decision_source": decision.decision_source,
            "selected_model": decision.selected_model,
            "model_profile": decision.model_profile,
            "prompt_category": decision.prompt_category,
            "prompt_version": decision.prompt_version,
            "tool_required": decision.tool_required,
            "tool_type": decision.tool_type,
            "decision_reason": decision.decision_reason,
            "state_vector": decision.state_vector,
        },
        timestamp=t2,
    )
    traces.append(trace_de)
    await observability_service.record_stage(
        request_id,
        "Decision Engine",
        trace_de.details,
        status=trace_de.status,
    )

    # 4. Prompt Rendering Stage
    template_text, _ = prompt_gateway_service.get_template(decision.prompt_category, decision.prompt_version)
    final_prompt, _, _ = SafeTemplateRenderer.render(
        template_text=template_text,
        variables={"query": req.query, "context": "Live request execution context"},
        strict=False,
    )

    # 5. MCP Gateway Stage (placeholder)
    t3 = datetime.utcnow().isoformat() + "Z"
    mcp_details = {
        "mcp_server": decision.tool_type,
        "tool_required": decision.tool_required,
        "status": "pending_mcp_milestone" if decision.tool_required else "skipped",
    }
    trace_mcp = ExecutionStageTrace(
        stage="MCP Gateway",
        status="completed",
        details=mcp_details,
        timestamp=t3,
    )
    traces.append(trace_mcp)
    await observability_service.record_stage(
        request_id,
        "MCP Gateway",
        mcp_details,
        status=trace_mcp.status,
    )

    # 6. Model Gateway & Execution
    t4 = datetime.utcnow().isoformat() + "Z"
    exec_res = await model_gateway.execute(
        prompt=final_prompt,
        model=decision.selected_model,
        model_profile=decision.model_profile,
    )

    elapsed_ms = exec_res.latency_ms
    input_tokens = exec_res.input_tokens
    output_tokens = exec_res.output_tokens
    total_tokens = exec_res.total_tokens
    estimated_cost = exec_res.estimated_cost
    response_text = exec_res.content if exec_res.success else f"Error executing model: {exec_res.error_type}"

    trace_mg = ExecutionStageTrace(
        stage="Model Gateway",
        status="completed" if exec_res.success else "failed",
        details={
            "model": exec_res.model,
            "model_profile": exec_res.model_profile,
            "provider": exec_res.provider,
            "latency_ms": exec_res.latency_ms,
            "tokens": exec_res.total_tokens,
            "cost_usd": exec_res.estimated_cost,
            "success": exec_res.success,
        },
        timestamp=t4,
    )
    traces.append(trace_mg)
    await observability_service.record_stage(
        request_id,
        "Model Gateway",
        trace_mg.details,
        status=trace_mg.status,
    )

    # 7. Observability & Feedback Stage
    t5 = datetime.utcnow().isoformat() + "Z"
    quality_score = 0.94
    latency_penalty = 0.08
    cost_penalty = 0.02
    tool_reward = 0.20 if requires_tool else 0.0
    reward = round(0.5 * quality_score + tool_reward - latency_penalty - cost_penalty, 3)

    feedback_details = {
        "quality_score": quality_score,
        "reward": reward,
        "latency_ms": round(elapsed_ms, 2),
        "cost_usd": round(estimated_cost, 6),
    }
    trace_obs = ExecutionStageTrace(
        stage="Observability & Feedback",
        status="completed",
        details=feedback_details,
        timestamp=t5,
    )
    traces.append(trace_obs)
    await observability_service.record_stage(
        request_id,
        "Observability & Feedback",
        feedback_details,
        status=trace_obs.status,
    )

    # Persist to Database
    selected_model = decision.selected_model
    selected_prompt = f"{decision.prompt_category}_{decision.prompt_version}"
    decision_source = decision.decision_source

    try:
        req_record = RequestRecord(
            id=request_id,
            request_text=req.query,
            task_type=task_type,
            complexity=complexity,
            tool_required=requires_tool,
            budget=req.budget or "medium",
        )
        db.add(req_record)
        await db.flush()

        routing_record = RoutingDecisionRecord(
            request_id=request_id,
            selected_model=selected_model,
            prompt_version=selected_prompt,
            selected_tool=requires_tool,
            decision_source=decision_source,
            decision_metadata={"complexity": complexity},
        )
        db.add(routing_record)

        metrics_record = ExecutionMetricRecord(
            request_id=request_id,
            latency_ms=elapsed_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            tool_success=True,
            success=exec_res.success,
        )
        db.add(metrics_record)

        feedback_record = FeedbackRecord(
            request_id=request_id,
            reward=reward,
            quality_score=quality_score,
            latency_penalty=latency_penalty,
            cost_penalty=cost_penalty,
            tool_success_reward=tool_reward,
        )
        db.add(feedback_record)

        await db.commit()
    except Exception as e:
        await observability_service.record_error(request_id, e)
        await db.rollback()
        print(f"DB persist error: {e}")

    await observability_service.finalize_trace(request_id, status="completed", db=db)
    return QueryResponse(
        request_id=request_id,
        query=req.query,
        task_type=task_type,
        complexity=complexity,
        selected_model=selected_model,
        prompt_version=selected_prompt,
        selected_tool=requires_tool,
        response_text=response_text,
        latency_ms=round(elapsed_ms, 2),
        total_tokens=total_tokens,
        estimated_cost=round(estimated_cost, 6),
        reward=reward,
        decision_source=decision_source,
        trace=traces,
    )

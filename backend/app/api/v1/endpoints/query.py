import uuid
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
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

router = APIRouter()

@router.post("/query", response_model=QueryResponse, summary="Execute AI Fabric Query Pipeline")
async def execute_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Core entrypoint for user queries.
    Executes the layered control plane pipeline:
    Prompt Gateway (Layer 1) ➜ Query Analyzer ➜ Decision Engine ➜ Gateways ➜ Observability & Feedback.
    """
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    traces = []

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
            variables={"query": req.query, "context": "Live request context"}
        )
    )

    traces.append(ExecutionStageTrace(
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
            "variables_injected": list(prompt_proc.variables_used.keys())
        },
        timestamp=t0
    ))

    # 2. Query Analyzer Stage (Consuming normalized prompt output from Prompt Gateway Layer 1)
    t1 = datetime.utcnow().isoformat() + "Z"
    analysis_res = query_analyzer_service.analyze(
        QueryAnalysisRequest(
            query=prompt_proc.normalized_query,
            budget=req.budget,
            category_hint=prompt_category
        )
    )
    task_type = analysis_res.task_type
    complexity = analysis_res.complexity
    tool_required = analysis_res.tool_required
    tool_type = analysis_res.tool_type
    requires_tool = tool_type if tool_required else None
    
    traces.append(ExecutionStageTrace(
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
            "state_vector": analysis_res.state_vector
        },
        timestamp=t1
    ))

    # 3. Decision Engine Stage
    t2 = datetime.utcnow().isoformat() + "Z"
    selected_model = "llama-3.3-70b-versatile" if complexity > 0.6 else "llama-3.1-8b-instant"
    selected_prompt = f"{prompt_category}_{prompt_version}"
    decision_source = req.routing_strategy or "rule_based"

    traces.append(ExecutionStageTrace(
        stage="Decision Engine",
        status="completed",
        details={
            "decision_source": decision_source,
            "selected_model": selected_model,
            "prompt_template": selected_prompt,
            "selected_tool": requires_tool,
            "reason": f"Complexity {complexity:.2f} routed to {selected_model}"
        },
        timestamp=t2
    ))

    # 4. MCP Gateway Stage
    t3 = datetime.utcnow().isoformat() + "Z"
    mcp_details = {
        "mcp_server": "github_mcp",
        "tool_invoked": "search_repository",
        "status": "success",
        "files_retrieved": ["src/db/queries.py", "schema.sql"]
    } if requires_tool else {"status": "skipped", "reason": "no_tool_required"}

    traces.append(ExecutionStageTrace(
        stage="MCP Gateway",
        status="completed",
        details=mcp_details,
        timestamp=t3
    ))

    # 5. Model Gateway & Execution
    t4 = datetime.utcnow().isoformat() + "Z"
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0 + 120.0  # Simulated latency for M1
    input_tokens = 620
    output_tokens = 340
    total_tokens = input_tokens + output_tokens
    estimated_cost = (input_tokens * 0.00059 / 1000.0) + (output_tokens * 0.00079 / 1000.0)
    
    response_text = (
        "### SQL Analysis & Optimization Result\n\n"
        "**Identified Bottleneck**:\n"
        "The query in `src/db/queries.py` performs a full table scan on `orders` using `SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC;` without a composite index on `(status, created_at)`.\n\n"
        "**Optimized SQL**:\n"
        "```sql\n"
        "CREATE INDEX idx_orders_status_created ON orders (status, created_at DESC);\n\n"
        "SELECT id, user_id, amount, created_at\n"
        "FROM orders\n"
        "WHERE status = 'pending'\n"
        "ORDER BY created_at DESC\n"
        "LIMIT 100;\n"
        "```\n\n"
        "**Improvement**:\n"
        "- Eliminates unindexed Sequential Scan\n"
        "- Reduces execution time from ~420ms to ~3.8ms on 1M rows."
    ) if is_sql_task else f"AI Fabric response generated via {selected_model} for query: {req.query}"

    traces.append(ExecutionStageTrace(
        stage="Model Gateway",
        status="completed",
        details={
            "model": selected_model,
            "provider": "groq",
            "latency_ms": round(elapsed_ms, 2),
            "tokens": total_tokens
        },
        timestamp=t4
    ))

    # 6. Observability & Feedback
    t5 = datetime.utcnow().isoformat() + "Z"
    quality_score = 0.94
    latency_penalty = 0.08
    cost_penalty = 0.02
    tool_reward = 0.20 if requires_tool else 0.0
    reward = round(0.5 * quality_score + tool_reward - latency_penalty - cost_penalty, 3)

    traces.append(ExecutionStageTrace(
        stage="Observability & Feedback",
        status="completed",
        details={
            "quality_score": quality_score,
            "reward": reward,
            "latency_ms": round(elapsed_ms, 2),
            "cost_usd": round(estimated_cost, 6)
        },
        timestamp=t5
    ))

    # Persist to Database
    try:
        req_record = RequestRecord(
            id=request_id,
            request_text=req.query,
            task_type=task_type,
            complexity=complexity,
            tool_required=requires_tool,
            budget=req.budget or "medium"
        )
        db.add(req_record)
        await db.flush()

        routing_record = RoutingDecisionRecord(
            request_id=request_id,
            selected_model=selected_model,
            prompt_version=selected_prompt,
            selected_tool=requires_tool,
            decision_source=decision_source,
            decision_metadata={"complexity": complexity}
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
            success=True
        )
        db.add(metrics_record)

        feedback_record = FeedbackRecord(
            request_id=request_id,
            reward=reward,
            quality_score=quality_score,
            latency_penalty=latency_penalty,
            cost_penalty=cost_penalty,
            tool_success_reward=tool_reward
        )
        db.add(feedback_record)

        await db.commit()
    except Exception as e:
        await db.rollback()
        # Non-fatal for response return, but log
        print(f"DB persist error: {e}")

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
        trace=traces
    )

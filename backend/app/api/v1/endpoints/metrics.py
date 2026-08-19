from sqlalchemy import Integer
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List
from ....core.database import get_db
from ....models.request import RequestRecord
from....models.metrics import ExecutionMetricRecord
from ....models.routing import RoutingDecisionRecord
from ....models.feedback import FeedbackRecord
from ....schemas.metrics import MetricsSummary, BenchmarkComparison

router = APIRouter()

@router.get("/metrics/summary", response_model=MetricsSummary, summary="Observability Metrics Summary")
async def get_metrics_summary(db: AsyncSession = Depends(get_db)):
    """Computes global observability telemetry metrics."""
    total_req_res = await db.execute(select(func.count(RequestRecord.id)))
    total_requests = total_req_res.scalar() or 0

    if total_requests == 0:
        return MetricsSummary(
            total_requests=0,
            success_rate=100.0,
            avg_latency_ms=0.0,
            avg_cost=0.0,
            avg_tokens=0.0,
            avg_reward=0.0,
            model_distribution={},
            routing_distribution={}
        )

    # Average metrics
    avg_metrics_res = await db.execute(
        select(
            func.avg(ExecutionMetricRecord.latency_ms),
            func.avg(ExecutionMetricRecord.estimated_cost),
            func.avg(ExecutionMetricRecord.total_tokens),
            func.sum(func.cast(ExecutionMetricRecord.success, Integer if hasattr(func, "cast") else int))
        )
    )
    
    # Simple query executions
    metric_rows = (await db.execute(select(ExecutionMetricRecord))).scalars().all()
    feedback_rows = (await db.execute(select(FeedbackRecord))).scalars().all()
    routing_rows = (await db.execute(select(RoutingDecisionRecord))).scalars().all()

    success_count = sum(1 for m in metric_rows if m.success)
    success_rate = (success_count / len(metric_rows) * 100.0) if metric_rows else 100.0
    avg_latency = (sum(m.latency_ms for m in metric_rows) / len(metric_rows)) if metric_rows else 0.0
    avg_cost = (sum(m.estimated_cost for m in metric_rows) / len(metric_rows)) if metric_rows else 0.0
    avg_tokens = (sum(m.total_tokens for m in metric_rows) / len(metric_rows)) if metric_rows else 0.0
    avg_reward = (sum(f.reward for f in feedback_rows) / len(feedback_rows)) if feedback_rows else 0.0

    model_dist: Dict[str, int] = {}
    routing_dist: Dict[str, int] = {}
    for r in routing_rows:
        model_dist[r.selected_model] = model_dist.get(r.selected_model, 0) + 1
        routing_dist[r.decision_source] = routing_dist.get(r.decision_source, 0) + 1

    return MetricsSummary(
        total_requests=total_requests,
        success_rate=round(success_rate, 2),
        avg_latency_ms=round(avg_latency, 2),
        avg_cost=round(avg_cost, 6),
        avg_tokens=round(avg_tokens, 1),
        avg_reward=round(avg_reward, 3),
        model_distribution=model_dist,
        routing_distribution=routing_dist
    )

@router.get("/metrics/benchmarks", response_model=List[BenchmarkComparison], summary="Policy Benchmark Comparison")
async def get_benchmarks(db: AsyncSession = Depends(get_db)):
    """Returns comparative metrics across routing policies: Static, Rule-Based, PPO, Federated."""
    # We query actual recorded runs by decision_source
    routing_rows = (await db.execute(select(RoutingDecisionRecord))).scalars().all()
    
    policies = ["static", "rule_based", "ppo", "federated"]
    benchmarks: List[BenchmarkComparison] = []
    
    for pol in policies:
        matching_req_ids = [r.request_id for r in routing_rows if r.decision_source.lower() == pol.lower()]
        if matching_req_ids:
            metrics = (await db.execute(select(ExecutionMetricRecord).filter(ExecutionMetricRecord.request_id.in_(matching_req_ids)))).scalars().all()
            feedbacks = (await db.execute(select(FeedbackRecord).filter(FeedbackRecord.request_id.in_(matching_req_ids)))).scalars().all()
            
            avg_lat = (sum(m.latency_ms for m in metrics) / len(metrics)) if metrics else 0.0
            avg_c = (sum(m.estimated_cost for m in metrics) / len(metrics)) if metrics else 0.0
            succ_r = (sum(1 for m in metrics if m.success) / len(metrics) * 100.0) if metrics else 100.0
            avg_rew = (sum(f.reward for f in feedbacks) / len(feedbacks)) if feedbacks else 0.0
            avg_qual = (sum(f.quality_score for f in feedbacks) / len(feedbacks)) if feedbacks else 0.85

            benchmarks.append(BenchmarkComparison(
                policy=pol.replace("_", " ").title(),
                avg_latency_ms=round(avg_lat, 2),
                avg_cost=round(avg_c, 5),
                avg_quality=round(avg_qual, 2),
                success_rate=round(succ_r, 1),
                avg_reward=round(avg_rew, 3)
            ))
        else:
            # Default placeholder comparison values for initial dashboard until experiments run
            benchmarks.append(BenchmarkComparison(
                policy=pol.replace("_", " ").title(),
                avg_latency_ms=0.0,
                avg_cost=0.0,
                avg_quality=0.0,
                success_rate=0.0,
                avg_reward=0.0
            ))
            
    return benchmarks

from typing import Optional, List, Dict
from pydantic import BaseModel

class MetricsSummary(BaseModel):
    total_requests: int
    success_rate: float
    avg_latency_ms: float
    avg_cost: float
    avg_tokens: float
    avg_reward: float
    model_distribution: Dict[str, int]
    routing_distribution: Dict[str, int]

class BenchmarkComparison(BaseModel):
    policy: str
    avg_latency_ms: float
    avg_cost: float
    avg_quality: float
    success_rate: float
    avg_reward: float

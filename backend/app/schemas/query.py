from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="User prompt or task description", json_schema_extra={"example": "Analyze my GitHub repository, identify the slow SQL query, optimize it and explain the improvement."})
    routing_strategy: Optional[str] = Field("rule_based", description="'rule_based', 'ppo', 'federated', or 'static'")
    budget: Optional[str] = Field("medium", description="'low', 'medium', 'high'")
    latency_target: Optional[str] = Field("normal", description="'fast', 'normal', 'unconstrained'")
    preferred_provider: Optional[str] = Field(None, description="Optional manual override provider")

class ExecutionStageTrace(BaseModel):
    stage: str
    status: str = "completed"  # 'pending', 'in_progress', 'completed', 'failed'
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str

class QueryResponse(BaseModel):
    request_id: str
    query: str
    task_type: str
    complexity: float
    selected_model: str
    prompt_version: str
    selected_tool: Optional[str] = None
    response_text: str
    latency_ms: float
    total_tokens: int
    estimated_cost: float
    reward: float
    decision_source: str
    trace: List[ExecutionStageTrace] = Field(default_factory=list)

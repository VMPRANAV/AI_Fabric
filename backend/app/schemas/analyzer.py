from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field

class QueryAnalysisRequest(BaseModel):
    query: str = Field(..., description="User prompt text to analyze")
    budget: Optional[str] = Field("medium", description="Budget constraint ('low', 'medium', 'high')")
    latency_target: Optional[str] = Field("normal", description="Latency target ('fast', 'normal', 'unconstrained')")
    category_hint: Optional[str] = Field(None, description="Optional category hint from Prompt Gateway")

class QueryAnalysisResponse(BaseModel):
    query: str = Field(..., description="Original raw query")
    normalized_query: str = Field(..., description="Sanitized and normalized prompt from Prompt Gateway")
    task_type: str = Field(..., description="Task classification label ('sql_analysis_optimization', 'repo_architecture', 'code_generation', 'general_reasoning')")
    task_type_idx: int = Field(..., description="Numerical task index (0=sql, 1=repo, 2=code, 3=general)")
    complexity: float = Field(..., description="Overall complexity score bounded in [0.0, 1.0]")
    complexity_factors: Dict[str, float] = Field(..., description="Explainable breakdown of complexity scoring factors")
    budget: str = Field(..., description="Budget constraint ('low', 'medium', 'high')")
    budget_idx: int = Field(..., description="Numerical budget index (0=low, 1=medium, 2=high)")
    latency_target: str = Field(..., description="Latency target ('fast', 'normal', 'unconstrained')")
    latency_idx: int = Field(..., description="Numerical latency index (0=fast, 1=normal, 2=unconstrained)")
    tool_required: bool = Field(..., description="Whether external tool support is required")
    tool_type: str = Field(..., description="Tool category label ('none', 'github_mcp', 'database_mcp')")
    tool_type_idx: int = Field(..., description="Numerical tool type index (0=none, 1=github_mcp, 2=database_mcp)")
    reasoning_required: str = Field(..., description="Reasoning requirement level ('low', 'medium', 'high')")
    reasoning_idx: int = Field(..., description="Numerical reasoning level index (0=low, 1=medium, 2=high)")
    state_vector: List[float] = Field(..., description="Exact 6D state vector representation: [task_idx, complexity, budget_idx, latency_idx, tool_idx, reasoning_idx]")

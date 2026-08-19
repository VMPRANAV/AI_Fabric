from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class RoutingDecision(BaseModel):
    request_id: Optional[str] = Field(default=None, description="Unique identifier for request trace")
    selected_model: str = Field(..., description="Configured model identifier selected for execution")
    model_profile: Literal["reasoning", "balanced", "fast", "mock"] = Field(..., description="High-level model profile tier")
    prompt_category: str = Field(..., description="Selected prompt template category")
    prompt_version: str = Field(..., description="Selected prompt template version (v1, v2, v3)")
    tool_required: bool = Field(..., description="Preserved tool requirement from Query Analyzer")
    tool_type: str = Field(..., description="Preserved tool type from Query Analyzer")
    decision_source: str = Field(default="rule_based", description="Decision policy source")
    decision_reason: List[str] = Field(..., description="Explainable list of rules that triggered the decision")
    state_vector: List[float] = Field(..., description="Exact 6D state vector from Query Analyzer")

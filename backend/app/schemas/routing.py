from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class RoutingDecisionSchema(BaseModel):
    selected_model: str
    prompt_template: str
    tool: Optional[str] = None
    resource: str = "node-1"
    decision_source: str = "rule_based"
    metadata: Dict[str, Any] = Field(default_factory=dict)

from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

class PromptValidateRequest(BaseModel):
    query: str = Field(..., description="Raw prompt text to validate")
    min_length: int = Field(default=3, description="Minimum acceptable character length", ge=1)
    max_length: int = Field(default=10000, description="Maximum acceptable character length", le=50000)

class PromptValidationResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the prompt meets syntax and length bounds")
    is_safe: bool = Field(..., description="Whether the prompt passed first-stage guardrails")
    risk_level: Literal["low", "medium", "high"] = Field(..., description="Risk assessment rating")
    violations: List[str] = Field(default_factory=list, description="List of detected policy or format violations")
    normalized_query: str = Field(..., description="Sanitized and normalized prompt text")
    character_count: int = Field(..., description="Total character count of normalized prompt")

class PromptProcessRequest(BaseModel):
    query: str = Field(..., description="User prompt text")
    category: Optional[str] = Field(default="general_assistant", description="Template category (e.g., 'sql_analysis', 'repo_analysis', 'general_assistant')")
    version: Optional[str] = Field(default="v1", description="Template version (e.g. 'v1', 'v2', 'v3')")
    variables: Dict[str, str] = Field(default_factory=dict, description="Variables to inject into the template")
    strict_variables: bool = Field(default=False, description="If true, fail if template placeholders are not provided")

class PromptProcessResponse(BaseModel):
    original_query: str
    normalized_query: str
    safety: PromptValidationResponse
    template_category: str
    version: str
    rendered_prompt: str
    variables_used: Dict[str, str]

class TemplateMetadata(BaseModel):
    category: str
    available_versions: List[str]
    placeholders_by_version: Dict[str, List[str]]

class TemplateDetailResponse(BaseModel):
    category: str
    version: str
    raw_template: str
    placeholders: List[str]

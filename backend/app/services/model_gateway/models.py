from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ModelExecutionResult(BaseModel):
    success: bool = Field(..., description="Execution status boolean")
    content: str = Field(default="", description="Generated response content string")
    provider: str = Field(..., description="Provider adapter name ('groq', 'mock')")
    model: str = Field(..., description="Executed model identifier")
    model_profile: str = Field(default="balanced", description="Model profile tier ('fast', 'balanced', 'reasoning', 'mock')")
    latency_ms: float = Field(..., description="Exact wall-clock latency in milliseconds")
    input_tokens: int = Field(default=0, description="Prompt input token count")
    output_tokens: int = Field(default=0, description="Completion output token count")
    total_tokens: int = Field(default=0, description="Total token consumption")
    estimated_cost: float = Field(default=0.0, description="Estimated execution cost in USD")
    error_type: Optional[str] = Field(default=None, description="Error classification string if failed")

class ModelGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Rendered prompt string to execute")
    model: Optional[str] = Field(None, description="Explicit model ID (overrides default profile model if provided)")
    model_profile: Optional[str] = Field("balanced", description="Model profile tier ('fast', 'balanced', 'reasoning', 'mock')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Generation hyperparameters (temperature, max_tokens)")

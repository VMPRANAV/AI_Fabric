# Schema definitions for PPO training and inference

from typing import List, Literal
from pydantic import BaseModel, Field

class PPOTrainRequest(BaseModel):
    timesteps: int = Field(..., gt=0, description="Number of training timesteps")

class PPOTrainResponse(BaseModel):
    status: str = Field(..., description="Result status, e.g., 'started' or 'completed'")
    algorithm: str = Field(default="PPO", description="RL algorithm used")
    timesteps: int
    model_path: str
    metadata_path: str

class PPOPredictRequest(BaseModel):
    state_vector: List[float] = Field(..., min_items=6, max_items=6, description="6‑dimensional state vector from Query Analyzer")

class PPOPredictResponse(BaseModel):
    action: int
    profile: Literal["fast", "balanced", "reasoning"]
    model: str
    policy: Literal["ppo"]

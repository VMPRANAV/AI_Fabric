from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from ....core.database import get_db
from ....models.llm_model import LLMModelRecord

router = APIRouter()

DEFAULT_MODELS = [
    {
        "name": "llama-3.1-8b-instant",
        "provider": "groq",
        "tier": "fast",
        "cost_per_1k_prompt_tokens": 0.00005,
        "cost_per_1k_completion_tokens": 0.00008,
        "max_context_window": 128000,
        "is_active": True
    },
    {
        "name": "llama-3.3-70b-versatile",
        "provider": "groq",
        "tier": "balanced",
        "cost_per_1k_prompt_tokens": 0.00059,
        "cost_per_1k_completion_tokens": 0.00079,
        "max_context_window": 128000,
        "is_active": True
    },
    {
        "name": "deepseek-r1-distill-llama-70b",
        "provider": "groq",
        "tier": "reasoning",
        "cost_per_1k_prompt_tokens": 0.00059,
        "cost_per_1k_completion_tokens": 0.00079,
        "max_context_window": 128000,
        "is_active": True
    },
    {
        "name": "mock-deterministic-v1",
        "provider": "mock",
        "tier": "balanced",
        "cost_per_1k_prompt_tokens": 0.0,
        "cost_per_1k_completion_tokens": 0.0,
        "max_context_window": 128000,
        "is_active": True
    }
]

@router.get("/models", summary="List Available LLM Models")
async def list_models(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Returns available LLM models in AI Fabric action space."""
    # Check if models are populated in DB
    result = await db.execute(select(LLMModelRecord))
    models = result.scalars().all()
    
    if not models:
        # Seed default models
        for m_data in DEFAULT_MODELS:
            model_record = LLMModelRecord(**m_data)
            db.add(model_record)
        await db.commit()
        
        result = await db.execute(select(LLMModelRecord))
        models = result.scalars().all()
        
    return [
        {
            "id": m.id,
            "name": m.name,
            "provider": m.provider,
            "tier": m.tier,
            "cost_per_1k_prompt_tokens": m.cost_per_1k_prompt_tokens,
            "cost_per_1k_completion_tokens": m.cost_per_1k_completion_tokens,
            "max_context_window": m.max_context_window,
            "is_active": m.is_active,
        }
        for m in models
    ]

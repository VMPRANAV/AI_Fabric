import time
from typing import Dict, Any
from app.services.model_gateway.base import BaseModelAdapter
from app.services.model_gateway.models import ModelExecutionResult

class MockAdapter(BaseModelAdapter):
    """
    Deterministic Mock Provider Adapter.
    Requires no API key, makes zero network calls, returns zero-cost execution telemetry.
    """

    async def generate(
        self,
        prompt: str,
        model: str,
        model_profile: str = "balanced",
        parameters: Dict[str, Any] = None
    ) -> ModelExecutionResult:
        start_time = time.perf_counter()
        
        is_sql = "sql" in prompt.lower() or "orders" in prompt.lower()
        
        if is_sql:
            content = (
                "### SQL Performance & Indexing Analysis\n\n"
                "**Identified Bottleneck**:\n"
                "Sequential Scan detected on `orders` table due to missing composite index on `(status, created_at)`.\n\n"
                "**Optimized DDL & Query**:\n"
                "```sql\n"
                "CREATE INDEX idx_orders_status_created ON orders (status, created_at DESC);\n\n"
                "SELECT id, user_id, amount, created_at\n"
                "FROM orders\n"
                "WHERE status = 'pending'\n"
                "ORDER BY created_at DESC\n"
                "LIMIT 100;\n"
                "```\n\n"
                "**Performance Gain**:\n"
                "- Eliminates unindexed table scan\n"
                "- Reduces execution latency from 420ms to 3.8ms"
            )
        else:
            content = f"[Mock LLM Response via {model} ({model_profile})]\nProcessed prompt request successfully."

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0 + 85.0
        
        input_tokens = len(prompt) // 4 + 50
        output_tokens = len(content) // 4 + 20
        total_tokens = input_tokens + output_tokens

        return ModelExecutionResult(
            success=True,
            content=content,
            provider="mock",
            model=model,
            model_profile=model_profile,
            latency_ms=round(elapsed_ms, 2),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=0.0,
            error_type=None
        )

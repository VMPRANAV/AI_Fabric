import time
import httpx
from typing import Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.services.model_gateway.base import BaseModelAdapter
from app.services.model_gateway.models import ModelExecutionResult

# Configurable price lookup table (per 1k tokens)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "llama-3.1-8b-instant": {"prompt": 0.00005, "completion": 0.00008},
    "llama-3.3-70b-versatile": {"prompt": 0.00059, "completion": 0.00079},
    "openai/gpt-oss-120b": {"prompt": 0.00015, "completion": 0.00060},
    "default": {"prompt": 0.00050, "completion": 0.00075}
}

class GroqAdapter(BaseModelAdapter):
    """
    Groq API Provider Adapter executing chat completions asynchronously over HTTP.
    Protects API keys and normalizes token usage, cost, and latency metrics.
    """

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(
        self,
        prompt: str,
        model: str,
        model_profile: str = "balanced",
        parameters: Dict[str, Any] = None
    ) -> ModelExecutionResult:
        api_key = settings.GROQ_API_KEY
        if not api_key or api_key.startswith("your_") or api_key == "mock_groq_key":
            return ModelExecutionResult(
                success=False,
                content="",
                provider="groq",
                model=model,
                model_profile=model_profile,
                latency_ms=0.0,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                estimated_cost=0.0,
                error_type="AuthenticationError: Missing or placeholder GROQ_API_KEY"
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        params = parameters or {}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.2),
            "max_tokens": params.get("max_tokens", 1024)
        }

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.GROQ_API_URL, headers=headers, json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.error(f"Groq API call failed for model {model}: {error_msg}")
                    return ModelExecutionResult(
                        success=False,
                        content="",
                        provider="groq",
                        model=model,
                        model_profile=model_profile,
                        latency_ms=round(elapsed_ms, 2),
                        input_tokens=0,
                        output_tokens=0,
                        total_tokens=0,
                        estimated_cost=0.0,
                        error_type=error_msg
                    )

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

                pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
                estimated_cost = round(
                    (input_tokens * pricing["prompt"] / 1000.0) +
                    (output_tokens * pricing["completion"] / 1000.0),
                    6
                )

                return ModelExecutionResult(
                    success=True,
                    content=content,
                    provider="groq",
                    model=model,
                    model_profile=model_profile,
                    latency_ms=round(elapsed_ms, 2),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=estimated_cost,
                    error_type=None
                )

        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ModelExecutionResult(
                success=False,
                content="",
                provider="groq",
                model=model,
                model_profile=model_profile,
                latency_ms=round(elapsed_ms, 2),
                error_type="TimeoutError: Groq API request timed out"
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ModelExecutionResult(
                success=False,
                content="",
                provider="groq",
                model=model,
                model_profile=model_profile,
                latency_ms=round(elapsed_ms, 2),
                error_type=f"ProviderError: {str(e)}"
            )

from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.services.model_gateway.base import BaseModelAdapter
from app.services.model_gateway.models import ModelExecutionResult
from app.services.model_gateway.groq_adapter import GroqAdapter
from app.services.model_gateway.mock_adapter import MockAdapter

class ModelGateway:
    """
    Model Gateway Service.
    Provider-independent entrypoint managing LLM adapter routing, token tracking,
    latency measurement, and configurable fallback policies.
    """

    def __init__(self):
        self.groq_adapter = GroqAdapter()
        self.mock_adapter = MockAdapter()

    def get_adapter(self, provider_name: Optional[str] = None, model: Optional[str] = None) -> BaseModelAdapter:
        """Resolves target provider adapter based on model ID, explicit parameter, or config."""
        if model and ("mock" in model.lower() or model.startswith("mock-")):
            return self.mock_adapter
        target_provider = (provider_name or settings.MODEL_PROVIDER).lower()
        if target_provider == "groq":
            return self.groq_adapter
        return self.mock_adapter

    async def execute(
        self,
        prompt: str,
        model: str,
        model_profile: str = "balanced",
        provider: Optional[str] = None,
        parameters: Dict[str, Any] = None
    ) -> ModelExecutionResult:
        adapter = self.get_adapter(provider, model=model)
        result = await adapter.generate(prompt, model, model_profile, parameters)

        # Fallback handling (Disabled by default to preserve research telemetry integrity)
        if not result.success and settings.MODEL_FALLBACK_ENABLED and provider != "mock":
            logger.warning(f"Primary provider failed ({result.error_type}). Fallback to MockAdapter enabled.")
            fallback_result = await self.mock_adapter.generate(prompt, model, model_profile, parameters)
            fallback_result.error_type = f"FallbackExecuted (Primary failed: {result.error_type})"
            return fallback_result

        return result

model_gateway = ModelGateway()

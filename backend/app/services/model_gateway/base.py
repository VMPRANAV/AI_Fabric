from abc import ABC, abstractmethod
from typing import Dict, Any
from app.services.model_gateway.models import ModelExecutionResult

class BaseModelAdapter(ABC):
    """
    Provider-independent interface for LLM model execution adapters.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        model_profile: str = "balanced",
        parameters: Dict[str, Any] = None
    ) -> ModelExecutionResult:
        """
        Executes model generation request and returns normalized ModelExecutionResult.
        """
        pass

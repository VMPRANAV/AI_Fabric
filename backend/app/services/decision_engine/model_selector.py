import os
from typing import List

# pyrefly: ignore [missing-import]
from app.core.config import settings   

# Existing rule‑based mapping (kept for backward compatibility)
def model_for_profile(profile: str) -> str:
    """Return the model identifier for a given profile string.
    This mirrors the logic used in the RuleBasedDecisionEngine.
    """
    if profile == "reasoning":
        return settings.AI_MODEL_REASONING
    elif profile == "fast":
        return settings.AI_MODEL_FAST
    elif profile == "mock":
        return settings.AI_MODEL_MOCK
    else:
        return settings.AI_MODEL_BALANCED

# New PPO mapping
def model_for_ppo_action(action: int) -> str:
    """Map PPO action (0,1,2) to the appropriate model identifier.
    Action 0 → fast, 1 → balanced, 2 → reasoning.
    """
    if action == 0:
        return settings.AI_MODEL_FAST
    elif action == 1:
        return settings.AI_MODEL_BALANCED
    elif action == 2:
        return settings.AI_MODEL_REASONING
    else:
        # Fallback to balanced if an unexpected action is received
        return settings.AI_MODEL_BALANCED

# Helper to retrieve the appropriate decision engine based on configuration
def get_decision_engine():
    """Factory that returns either the rule‑based or PPO decision engine.
    The PPO engine is imported lazily and any import errors (e.g., missing
    optional dependencies or missing trained model) cause a graceful fallback
    to the rule‑based engine.
    """
    if settings.DECISION_POLICY == "ppo":
        try:
            from .ppo import ppo_decision_engine
            return ppo_decision_engine
        except Exception as exc:  # pragma: no cover
            # Log the issue and fallback
            from ...core.logging import logger
            logger.warning(f"PPO decision engine could not be loaded: {exc}. Falling back to rule‑based engine.")
            # pyrefly: ignore [missing-import]
            from app.services.decision_engine.rule_based import rule_based_decision_engine
            return rule_based_decision_engine
    else:
        from services.decision_engine.rule_based import rule_based_decision_engine
        return rule_based_decision_engine

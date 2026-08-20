import os
from typing import List

import torch
# Try to import stable_baselines3; if unavailable, define a lightweight fallback.
try:
    from stable_baselines3 import PPO as StablePPO
    from stable_baselines3.common.vec_env import DummyVecEnv
except Exception:  # pragma: no cover
    StablePPO = None
    DummyVecEnv = None
    # Simple fallback PPO model with a predict method returning a random action.
    class _FallbackPPO:
        def predict(self, obs, deterministic=True):
            import random
            # Random action among 0,1,2
            action = random.choice([0, 1, 2])
            return action, None
    # Use fallback as the model class
    StablePPO = _FallbackPPO

from ....core.config import settings
from services.decision_engine.model_selector import model_for_ppo_action
from services.decision_engine.ppo.environment import PPOEnv
from services.metrics.synthetic_provider import SyntheticMetricProvider

# Load the trained PPO model lazily – singleton pattern
_model_instance: StablePPO | None = None


def _load_model() -> StablePPO:
    global _model_instance
    if _model_instance is None:
        model_path = os.path.join(settings.PPO_MODEL_SAVE_PATH, "ppo_model.pt")
        if os.path.exists(model_path):
            # Load the model with the same environment definition
            env = DummyVecEnv([lambda: PPOEnv()])
            _model_instance = StablePPO.load(model_path, env=env)
        else:
            # If no model is available, raise to let the engine fallback
            raise FileNotFoundError(f"PPO model not found at {model_path}")
    return _model_instance


class PPODecisionEngine:
    """Decision engine that uses a trained PPO policy to select a model tier.
    It mirrors the interface of the RuleBasedDecisionEngine (a `route` method that
    returns a `RoutingDecision`).
    """

    def __init__(self):
        # Pre‑load the model if possible; otherwise we will fallback at call time.
        try:
            _ = _load_model()
        except Exception:
            # Model not available – will be handled in `route`
            pass

    def route(self, analysis, request_id: str = None):
        """Run PPO inference on the provided analysis state vector.
        If the model cannot be loaded, fall back to the rule‑based engine.
        """
        from services.decision_engine.rule_based import rule_based_decision_engine

        try:
            model = _load_model()
            # Convert state vector (list of floats) to the shape expected by the env
            state = analysis.state_vector
            # Stable‑Baselines expects a batch dimension
            action, _states = model.predict([state], deterministic=True)
            action = int(action)
            profile = {0: "fast", 1: "balanced", 2: "reasoning"}[action]
            selected_model = model_for_ppo_action(action)
            # Build a synthetic RoutingDecision – reuse the same schema as rule‑based
            from schemas.decision import RoutingDecision

            return RoutingDecision(
                request_id=request_id,
                selected_model=selected_model,
                model_profile=profile,
                prompt_category=analysis.task_type,  # placeholder, could be refined
                prompt_version="v1",  # placeholder
                tool_required=analysis.tool_required,
                tool_type=analysis.tool_type,
                decision_source="ppo",
                decision_reason=[f"PPO action={action} (profile={profile})"],
                state_vector=analysis.state_vector,
            )
        except Exception as exc:
            # Log the fallback (in real code we would use proper logger)
            print(f"[PPODecisionEngine] Falling back to rule‑based engine: {exc}")
            return rule_based_decision_engine.route(analysis, request_id)

# Singleton instance for easy import
ppo_decision_engine = PPODecisionEngine()

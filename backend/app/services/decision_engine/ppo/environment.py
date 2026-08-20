import gymnasium as gym
import numpy as np
from gymnasium import spaces
from services.metrics.synthetic_provider import SyntheticMetricProvider
from ....core.config import settings

class PPOEnv(gym.Env):
    """Gymnasium environment for PPO training.
    Observation: 6‑dim state vector (floats in [0,1]).
    Action: Discrete(3) – 0=fast, 1=balanced, 2=reasoning.
    Reward: α·quality + β·tool_success – γ·latency – δ·cost.
    """

    def __init__(self):
        super().__init__()
        # 6 continuous features
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(6,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)
        self.seed(settings.PPO_SEED)
        self.metric_provider = SyntheticMetricProvider()

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.seed(seed)
        # deterministic initial state – zeros (could be random but deterministic with seed)
        state = np.zeros(6, dtype=np.float32)
        return state, {}

    def step(self, action):
        # Generate synthetic metrics based on the (placeholder) state vector
        state = np.random.rand(6).astype(np.float32)  # deterministic due to seed
        quality, latency_ms, cost, tool_success = self.metric_provider.evaluate(state)
        # Reward calculation using env vars
        reward = (
            settings.PPO_ALPHA * quality
            + settings.PPO_BETA * (1.0 if tool_success else 0.0)
            - settings.PPO_GAMMA * (latency_ms / 1000.0)  # normalize latency
            - settings.PPO_DELTA * cost
        )
        # Episode termination – for training we keep it non‑terminal (stable‑baselines handles timesteps)
        done = False
        info = {
            "state": state.tolist(),
            "quality": quality,
            "latency_ms": latency_ms,
            "cost": cost,
            "tool_success": tool_success,
        }
        return state, reward, done, False, info

    def seed(self, seed=None):
        np.random.seed(seed)
        return [seed]

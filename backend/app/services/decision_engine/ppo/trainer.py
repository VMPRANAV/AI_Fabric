import argparse
import os
from datetime import datetime
import json

import torch
from stable_baselines3 import PPO as StablePPO
from stable_baselines3.common.vec_env import DummyVecEnv

from core.config import settings 
from services.decision_engine.ppo.environment import PPOEnv

def train(timesteps: int):
    """Train the PPO model for the given number of timesteps and persist it.
    The function creates the model directory if it does not exist, saves the
    trained model as `ppo_model.pt` and writes a JSON metadata file.
    """
    # Ensure the save directory exists
    os.makedirs(settings.PPO_MODEL_SAVE_PATH, exist_ok=True)

    env = DummyVecEnv([lambda: PPOEnv()])
    model = StablePPO("MlpPolicy", env, verbose=1, seed=settings.PPO_SEED)
    model.learn(total_timesteps=timesteps)

    # Save model
    model_path = os.path.join(settings.PPO_MODEL_SAVE_PATH, "ppo_model.pt")
    model.save(model_path)

    # Prepare metadata
    metadata = {
        "model_version": "v1",
        "training_timestamp": datetime.utcnow().isoformat() + "Z",
        "timesteps": timesteps,
        "reward_coefficients": {
            "alpha": settings.PPO_ALPHA,
            "beta": settings.PPO_BETA,
            "gamma": settings.PPO_GAMMA,
            "delta": settings.PPO_DELTA,
        },
        "environment_config": {
            "state_dim": 6,
            "seed": settings.PPO_SEED,
        },
    }
    metadata_path = os.path.join(settings.PPO_MODEL_SAVE_PATH, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"PPO training completed. Model saved to {model_path}")
    print(f"Metadata saved to {metadata_path}")
    return model_path, metadata_path

def main():
    parser = argparse.ArgumentParser(description="Train PPO decision engine")
    parser.add_argument("--timesteps", type=int, required=True, help="Number of training timesteps")
    args = parser.parse_args()
    train(args.timesteps)

if __name__ == "__main__":
    main()

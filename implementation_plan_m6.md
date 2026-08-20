# Implementation Plan – Milestone 6: PPO‑Based Adaptive Decision Engine

## Goal Description
Add a Proximal Policy Optimization (PPO) decision engine that co‑exists with the existing rule‑based router. The PPO policy selects one of three model tiers (fast, balanced, reasoning) based on the 6‑dimensional state vector from the Query Analyzer. All other pipeline stages remain unchanged.

## High‑Level Tasks

---
### 1. Configuration
- **File:** `backend/app/core/config.py`
- Add `DECISION_POLICY: str = "rule_based"` (env var `DECISION_POLICY`).
- Add PPO coefficient env vars: `PPO_ALPHA`, `PPO_BETA`, `PPO_GAMMA`, `PPO_DELTA` with defaults `0.40`, `0.20`, `0.20`, `0.20`.
- Add `PPO_SEED: int = 42`.
- Add `PPO_MODEL_SAVE_PATH: str = "backend/models/ppo"`.
- Optional hyper‑parameter env vars (`PPO_LEARNING_RATE`, `PPO_N_STEPS`, `PPO_BATCH_SIZE`).

---
### 2. Schema Additions
- **File:** `backend/app/schemas/ppo.py`
- Define request/response models for training and inference (as supplied by the user).

---
### 3. Model Selector Mapping
- **File:** `backend/app/services/decision_engine/model_selector.py`
- Extend mapping to read from env vars and map PPO actions (0,1,2) → `AI_MODEL_FAST`, `AI_MODEL_BALANCED`, `AI_MODEL_REASONING`.
- Ensure no hard‑coded provider names.

---
### 4. Decision Engine Package
- **File:** `backend/app/services/decision_engine/__init__.py`
  - Export both `RuleBasedDecisionEngine` and new `PPODecisionEngine`.
  - Load `DECISION_POLICY` and route accordingly.

- **New Package:** `backend/app/services/decision_engine/ppo/`
  - `__init__.py` – expose `PPODecisionEngine`.
  - `policy_selector.py` – decides which engine to invoke based on `DECISION_POLICY`.
  - `environment.py` – Gymnasium `Env` implementing the 6‑dim state, deterministic synthetic metrics, reward function using env vars.
  - `trainer.py` – CLI entry point (`python -m app.services.decision_engine.ppo.trainer --timesteps <N>`) and programmatic `train` function.
  - `inference.py` – thin wrapper that loads the saved PPO model and returns action/profile.

---
### 5. Metric Providers
- **New File:** `backend/app/services/metrics/synthetic_provider.py`
  - Deterministic generation of quality, latency, cost, tool_success based on fixed formulas.
- **New File:** `backend/app/services/metrics/db_provider.py`
  - Stub that queries `execution_metrics` table when sufficient historic data exists.

---
### 6. Persistence
- Create directory `backend/models/ppo/`.
- `trainer.py` saves `ppo_model.pt` (Stable‑Baselines3) and `metadata.json` containing:
  - `model_version`
  - `training_timestamp`
  - `timesteps`
  - `reward_coefficients`
  - `environment_config`
  - `seed`

---
### 7. Database Migration (Alembic)
- **File:** `backend/alembic/versions/<timestamp>_add_ppo_columns_to_routing_decisions.py`
  - Add columns to `routing_decisions`:
    - `policy` (String)
    - `action` (Integer)
    - `reward` (Float)
    - `state_vector` (JSON)
    - `quality` (Float)
    - `latency_ms` (Float)
    - `cost` (Float)
    - `tool_success` (Boolean)
  - Use appropriate SQLAlchemy types.

---
### 8. API Endpoints
- **New File:** `backend/app/api/v1/ppo.py`
  - `POST /api/v1/ppo/train` – validates `PPOTrainRequest`, triggers async training task, returns `PPOTrainResponse`.
  - `POST /api/v1/ppo/predict` – validates `PPOPredictRequest`, loads PPO model, returns `PPOPredictResponse` (action, profile, model, policy).
  - Ensure endpoints respect `DECISION_POLICY` and do not interfere with existing `/api/v1/query`.

---
### 9. Frontend Dashboard
- **File:** `frontend/src/components/PpoDashboard.jsx` (or appropriate path in existing research UI).
  - Premium UI (glassmorphism, smooth gradients, Google Font *Inter*).
  - Shows training status, timesteps, current policy, selected action/model, reward breakdown, and comparative table (Static, Rule‑Based, PPO, PPO+FL).
  - No extra authentication needed.

---
### 10. Tests
Create `tests/ppo/` with modules covering:
- Environment state/action spaces and determinism.
- Reward calculation using env vars.
- SyntheticMetricProvider deterministic output.
- Trainer runs without external API keys.
- Model saving/loading correctness.
- Inference endpoint returns correct mapping and fallback behavior.
- Action‑to‑model mapping.
- Policy switching via `DECISION_POLICY`.
- Database persistence of routing decisions.
- End‑to‑end query pipeline with PPO policy.

---
## Open Questions (User Input Required)
> [!WARNING]
> 1. **Metric Provider Plug‑in** – Do you want **only** the `SyntheticMetricProvider` for now, or also create the stub `DBMetricProvider`?
> 2. **CLI Entry Point** – Should the training CLI be exactly `python -m app.services.decision_engine.ppo.trainer --timesteps 10000` (as in the spec) or a separate script under `bin/`?
> 3. **Routing Decisions Migration** – Confirm the column types (String, Integer, Float, JSON, Boolean) as listed.
> 4. **Frontend Layout** – Do you have a preferred design mockup or colour palette, or should we reuse the existing UI theme?

Please answer the above so we can finalize the implementation.

---
## Verification Plan
- Run full existing test suite (`pytest -q`).
- Execute new PPO tests.
- Manual flow: start API, call `/api/v1/ppo/train` (small timesteps), verify model and metadata appear.
- Call `/api/v1/ppo/predict` with sample state, confirm correct action/profile/model.
- Set `DECISION_POLICY=ppo` and hit `/api/v1/query`; ensure only PPO inference runs.
- Open PPO dashboard, verify displayed metrics.

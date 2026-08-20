# PPO Routing Implementation

## Goal Description

Implement a Proximal Policy Optimization (PPO) based routing policy that coexists with the existing rule‑based router. This includes:
- Configurable decision policy (`DECISION_POLICY`) with default `rule_based`.
- Environment‑based model mapping (fast, balanced, reasoning) driven by PPO actions.
- Reward calculation with configurable coefficients via environment variables.
- Persistence of trained PPO models and metadata in `backend/models/ppo/`.
- New metric providers (`SyntheticMetricProvider` and `DBMetricProvider`).
- CLI trainer and programmatic API endpoint.
- Database schema extensions via Alembic migration.
- Front‑end dashboard to display PPO training status and comparisons.
- Comprehensive tests covering the new functionality.

## User Review Required

> [!IMPORTANT]
> Ensure the following decisions are acceptable before we proceed:
> - **Environment variable names** for PPO coefficients: `PPO_ALPHA`, `PPO_BETA`, `PPO_GAMMA`, `PPO_DELTA`.
> - **Model mapping**: PPO action 0 → `AI_MODEL_FAST`, 1 → `AI_MODEL_BALANCED`, 2 → `AI_MODEL_REASONING`. These model identifiers must exist in the existing model configuration (they are currently referenced elsewhere).
> - **Persistence path**: `backend/models/ppo/` will store the model (`ppo_model.pt`) and a JSON metadata file (`metadata.json`).
> - **Metric provider names**: `SyntheticMetricProvider` and `DBMetricProvider` will be registered under the metric provider factory.
> - **Database migration**: New columns will be added to `routing_decisions`. No new table will be created.
> - **API endpoints**: `/api/v1/ppo/train` and `/api/v1/ppo/predict` will be added. Ensure they do not conflict with existing routes.
> - **Frontend dashboard**: The dashboard will be a new page under the existing research UI; no additional authentication is required.

If any of these choices need adjustment, please let me know.

## Open Questions

> [!WARNING]
> - **What should the default PPO model version identifier be?** (e.g., `v1`, timestamp based, or semantic version?)
> - **How should we handle model loading failures in the inference endpoint?** Should we fall back to rule‑based routing or return an error?
> - **Is there a preferred method for seeding the synthetic environment to guarantee reproducibility?** (fixed seed value or configurable via env `PPO_SEED`?)
> - **Do we need to expose any additional configuration for the synthetic metric ranges (quality, latency, cost, tool_success) or are they hard‑coded deterministic values?**
> - **Frontend implementation details:** Do you have a design mockup or color palette for the research dashboard, or should we use the existing UI theme?

## Proposed Changes

---
### Backend Configuration

#### [MODIFY] [`backend/.env`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/.env)
- Add default environment variables for PPO coefficients and decision policy.

---
### Decision Engine

#### [MODIFY] [`app/services/decision_engine/__init__.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/decision_engine/__init__.py)
- Introduce `DecisionPolicy` enum with values `RULE_BASED` and `PPO`.
- Load `DECISION_POLICY` from env, default `rule_based`.
- Route to `PPOPolicySelector` when configured.

#### [NEW] [`app/services/decision_engine/ppo/__init__.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/decision_engine/ppo/__init__.py)
- Expose `PPOPolicySelector` class implementing the PPO inference logic.

#### [NEW] [`app/services/decision_engine/ppo/environment.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/decision_engine/ppo/environment.py)
- Gymnasium environment implementing the state vector, deterministic synthetic metrics, and reward function using env vars.

#### [NEW] [`app/services/decision_engine/ppo/trainer.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/decision_engine/ppo/trainer.py)
- CLI entry point (`python -m app.services.decision_engine.ppo.trainer --timesteps 10000`).
- Programmatic `train` function usable by API.

---
### Metric Providers

#### [NEW] [`app/services/metrics/synthetic_provider.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/metrics/synthetic_provider.py)
- Deterministic metric generation for synthetic training.

#### [NEW] [`app/services/metrics/db_provider.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/metrics/db_provider.py)
- Stub implementation that reads from `execution_metrics` table when data is sufficient.

---
### Model Mapping

#### [MODIFY] [`app/services/decision_engine/model_selector.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/services/decision_engine/model_selector.py)
- Add mapping from PPO actions to model identifiers (`AI_MODEL_FAST`, `AI_MODEL_BALANCED`, `AI_MODEL_REASONING`).
- Ensure no hard‑coded provider names; use existing environment‑based config.

---
### Persistence

#### [NEW] [`backend/models/ppo/metadata.json`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/models/ppo/metadata.json)
- JSON file storing: `model_version`, `training_timestamp`, `timesteps`, `reward_coefficients`, `environment_config`.

---
### Database Migration

#### [NEW] Alembic migration file `versions/<timestamp>_add_ppo_columns_to_routing_decisions.py`
- Add columns: `policy` (String), `action` (Integer), `reward` (Float), `state_vector` (JSON), `quality` (Float), `latency_ms` (Float), `cost` (Float), `tool_success` (Boolean).

---
### API Endpoints

#### [NEW] [`app/api/v1/ppo.py`](file:///Users/pranavvm/Workspace/projects/AI%20Fabric/backend/app/api/v1/ppo.py)
- `POST /api/v1/ppo/train` – triggers training (async background task).
- `POST /api/v1/ppo/predict` – accepts state vector, returns selected action and model.

---
### Frontend Dashboard

#### [NEW] React component `PpoDashboard.jsx` under existing research UI path.
- Displays training status, timesteps, current policy, selected action/model, reward breakdown, and comparison table.
- Uses existing design system and follows premium aesthetics guidelines.

---
### Tests

Create new test modules under `tests/ppo/` covering:
- Environment state/action spaces.
- Reward calculation with env var coefficients.
- Synthetic metric determinism.
- Trainer runs without external API access.
- Model saving/loading.
- Inference endpoint correctness.
- Action‑to‑model mapping.
- Policy switching via `DECISION_POLICY` env.
- Database persistence of decisions.
- End‑to‑end query pipeline with PPO policy.

---
### Verification Plan

### Automated Tests
- Run full test suite (`pytest -q`). Ensure existing Milestone 1‑5 tests still pass.
- Execute new PPO tests.

### Manual Verification
- Start the API server, call `/api/v1/ppo/train` with a small timestep count, verify model file appears in `backend/models/ppo/` and `metadata.json` is populated.
- Call `/api/v1/ppo/predict` with a sample state, confirm a valid action and correct model identifier.
- Set `DECISION_POLICY=ppo` and send a query to `/api/v1/query`; ensure only PPO inference is performed (no training triggered) and the response includes the selected model.
- Open the PPO dashboard in the browser, verify the displayed metrics match the persisted data.

---

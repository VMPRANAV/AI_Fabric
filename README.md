# AI Fabric — Intelligent AI Control Plane

AI Fabric is an intelligent control plane between AI applications and AI resources such as **LLMs, prompt templates, MCP tools, and databases**. It analyzes requests, selects suitable models/tools, executes them, and collects telemetry for adaptive optimization using **PPO** and future **Federated Learning**.

## Architecture

```text
AI Application
      │
      ▼
Prompt Gateway (L1)
      │
      ▼
Query Analyzer (L2)
      │
      ▼
Decision Engine (L3)
      │
      ├──────────────┐
      ▼              ▼
Model Gateway    MCP Gateway
      │              │
    Groq         GitHub MCP
      │              │
      └──────┬───────┘
             ▼
        LLM Response
             │
             ▼
      Unified Observability
             │
             ▼
       PPO / Feedback
             │
             ▼
    Adaptive Optimization
```

## Implemented Milestones

### Milestone 1 — Foundation

* FastAPI backend + React frontend
* Supabase PostgreSQL integration
* Configuration and health APIs
* Initial query pipeline
* Automated testing

### Milestone 2 — Prompt Gateway

* Input validation and normalization
* Unicode NFKC normalization
* First-stage safety guardrails
* Template catalog with `v1`, `v2`, `v3`
* Secure variable injection
* Prompt processing APIs

### Milestone 3 — Query Analyzer

* Task classification
* Complexity scoring `0.0–1.0`
* Budget and latency analysis
* Tool requirement detection
* Reasoning requirement detection
* 6D PPO-ready state vector

```text
[task, complexity, budget, latency, tool, reasoning]
```

### Milestone 4 — Decision Engine + Model Gateway

* Deterministic rule-based routing
* Fast / Balanced / Reasoning model tiers
* Automatic prompt-version selection
* Groq provider integration
* Mock provider for offline testing
* Latency, token and cost tracking
* Configurable fallback

### Milestone 5 — MCP Gateway

* MCP Gateway architecture
* GitHub MCP integration
* Mock GitHub MCP server
* Tool validation and allowlists
* `list_files`, `get_file`, `search_code`, `get_repo_structure`
* Tool execution telemetry
* Context Builder for tool results
* MCP integration into the query pipeline

### Milestone 6 — PPO Adaptive Decision Engine

* PPO-based model routing
* Rule-based routing remains the default baseline
* PPO uses the Query Analyzer's 6D state vector
* Three actions:

```text
0 → Fast
1 → Balanced
2 → Reasoning
```

* Configurable reward:

```text
Reward = α·Quality − β·Latency − γ·Cost + δ·Success
```

* PPO training and inference support
* Model and training metadata persistence
* PPO/rule-based policy switching
* PPO-ready query pipeline

### Milestone 7 — Unified Observability

* Centralized execution tracing
* Existing **Supabase PostgreSQL** used for persistence
* Tracks:

  * Request ID
  * Pipeline stages
  * Selected policy/model
  * Latency
  * Token usage
  * Cost
  * Tool/model success
  * Quality
  * PPO reward
  * Errors
* Stage-level telemetry across:

  * Prompt Gateway
  * Query Analyzer
  * Decision Engine
  * MCP Gateway
  * Model Gateway
* Existing **Research Dashboard** extended with observability metrics
* No separate authentication layer for observability APIs
* PPO reward is reused from the PPO implementation

## Tech Stack

**Backend:** FastAPI, Python, SQLAlchemy, PostgreSQL/Supabase
**Frontend:** React, Vite
**AI:** Groq, PPO, Stable-Baselines3
**Tools:** MCP, GitHub MCP
**Database:** Supabase PostgreSQL
**Testing:** Pytest

## Run the Project

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
pytest -v tests/
```

## Environment

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres

GROQ_API_KEY=<YOUR_GROQ_KEY>
GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>

MCP_PROVIDER=mock
DECISION_POLICY=rule_based
```

Switch to PPO when the trained policy is available:

```env
DECISION_POLICY=ppo
```

## Current Pipeline

```text
User Request
    ↓
Prompt Gateway
    ↓
Query Analyzer
    ↓
Decision Engine
    ↓
┌───────────────┬───────────────┐
│ Model Gateway │  MCP Gateway  │
└───────┬───────┴───────┬───────┘
        ↓               ↓
       LLM          GitHub Tools
        └───────┬───────┘
                ↓
         Final Response
                ↓
         Observability
                ↓
          PPO Feedback
```

**Status:** Milestones **1–7** implemented, with **Unified Observability** as the current layer.

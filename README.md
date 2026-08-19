# AI Fabric — Intelligent AI Control Plane & Orchestration Platform

AI Fabric is an intelligent control plane positioned between AI applications and AI resources (LLMs, Prompt Templates, MCP Tools, and Databases). It uses Reinforcement Learning (PPO) and Federated Learning to adaptively route requests, optimize latency/cost/quality, and learn continuously from closed-loop feedback.

---

## Architecture Overview

```text
                         AI APPLICATION
                               │
                               ▼
                         ┌───────────┐
                         │ AI FABRIC │
                         └─────┬─────┘
                               │
                        ┌──────▼──────┐
                        │Query Analyzer│
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │Decision Engine│
                        └──────┬──────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Prompt Gateway   Model Gateway     MCP Gateway
              │                │                │
              │              Groq          GitHub MCP
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                          LLM RESPONSE
                               │
                               ▼
                         Observability
                               │
                               ▼
                         Feedback Engine
                               │
                               ▼
                              PPO
                               │
                               ▼
                       Improved Policy
                               │
                               ▼
                    Federated Aggregation
```

---

## Milestone 1 Setup & Verification

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Run Backend Server:
```bash
uvicorn app.main:app --port 8000 --reload
```
Interactive Swagger Docs will be available at: `http://localhost:8000/docs`

#### Run Backend Test Suite:
```bash
pytest -v tests/
```

---

### 2. Frontend Setup

```bash
cd frontend
npm install
```

#### Run Frontend Dev Server:
```bash
npm run dev
```
Open `http://localhost:5173` to view the **AI Chat & Live Trace Visualizer** and **Research Dashboard**.

---

### 3. Environment Variables (`backend/.env`)

Configure your secrets in `backend/.env`:

```env
ENVIRONMENT=development
PORT=8000
DEBUG=True

# Supabase PostgreSQL Connection String (Asyncpg)
DATABASE_URL=postgresql+asyncpg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres

# Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# GitHub Token (for live MCP mode)
GITHUB_TOKEN=your_github_token_here
MCP_GITHUB_MODE=mock
```

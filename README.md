# ReconX — Autonomous Payment Reconciliation Investigator

ReconX is an autonomous payment reconciliation investigator for Razorpay payment operations. It ingests transaction feeds and ledger entries, runs a highly optimized deterministic reconciliation engine, classifies discrepancies, runs an AI investigator to find the root cause, evaluates policy rules to decide if a case can be auto-resolved, and exposes a high-fidelity real-time Command Center.

---

## Core Principle

```
Code determines what happened.
AI determines why it happened.
Policy determines what can happen next.
```

---

## Key Features (Phase 6 Specs)

1. **High-Throughput Deterministic Engine**: Processes transaction matching with sub-millisecond median latencies (~0.0032ms), achieving throughputs over **144,000 tx/sec**.
2. **AI Investigator with Honest Policy Bounds**: Evaluates exceptions via custom AI reasoning providers. Operates under an **Honest Exception List** policy boundary:
   - **Auto-Resolves**: Fee/tax schedule mismatch, sub-paisa rounding variance.
   - **Blocks / Escalates to Humans**: Missing bank credit (missing UTR), duplicate settlement batches, partial payouts, low-confidence hypotheses, high financial exposure.
3. **Control Center Dashboard**: Next.js 16 Web UI featuring:
   - Reusable KPI cards with sparkline/trend tags.
   - Reconciliation health bars (real-time matched rate vs exception rate).
   - Case stream (live feed with status tags).
   - **Interactive Explainability Drawer ("Why?" Drawer)**: Breaks down the financial state, root cause summary, AI confidence meter, ranked hypotheses, verified/unverified evidence checklist, policy engine variables, and execution timeline.
4. **One-Click Demo Scenarios**: Interactive playback panel executing predefined scenario endpoints:
   - `Fee Mismatch` (Low-risk auto-resolution)
   - `Missing Bank Credit` (Human review escalation)
   - `Duplicate Settlement` (High-risk automated block)
   - `Unknown Discrepancy` (Low confidence review)
   - `AI Failure` (Graceful fallback to manual queue)
5. **Observability & Performance Metrics**: Exposes `/system` and `/system/queues` showing live database status, Redis queue depth (`reconciliation`, `investigation`, `actions`, `dead_letter`), active workers count, and AI cost/token tracking.
6. **Request ID Middleware**: Injects `X-Request-ID` header to trace contexts across requests.

---

## Architecture Diagram

```
Razorpay Webhooks & APIs
         │
         ▼
  Ingestion & Normalization
         │
         ▼
     PostgreSQL
         │
         ▼
  Deterministic Reconciliation Engine  ───► Throughput: 144k tx/s
         │                                  P99 Latency: <0.01ms
    ┌────┴────┐
    ▼         ▼
MATCHED    EXCEPTION (8.8% average rate)
               │
               ▼
        AI Investigator (Gemini / Rule Fallback)
               │
               ▼
         Policy Engine (Honest Exception Bounds)
           ┌──┴──┐
           ▼     ▼
      Auto-      Human Review / Block
      Resolve    (Missing UTR, Duplicates, exposure)
           └──┬──┘
              ▼
          Audit Log
              │
              ▼
       Control Center (Web UI)
```

---

## Stack

- **Frontend**: Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Recharts
- **Backend API**: FastAPI, Python 3.12, SQLAlchemy ORM, Alembic
- **Task Queue**: RQ (Redis Queue), Redis 7
- **Database**: PostgreSQL 17
- **Observability**: Prometheus metrics, Redis list length metrics, AI cost tracker

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- OpenAI API Key (or mock mode fallback)

### 1. Configure Environments
Copy the example environment files and enter your keys:

```bash
# Main Template
cp .env.example .env

# Backend App Environment
cp .env.example apps/api/.env

# Frontend App Environment
# Ensure NEXT_PUBLIC_API_URL points to the backend (http://localhost:8000)
cp apps/web/.env.local.example apps/web/.env.local
```

### 2. Run with Docker Compose (Scaled Workers)
ReconX is designed to scale background workers for heavy reconciliation tasks.

```bash
# Build and start services in the background
docker compose up -d --build

# Scale to 4 parallel reconciliation workers
docker compose up -d --scale worker=4

# Verify all services are running (postgres, redis, api, worker-1, worker-2, ...)
docker compose ps
```

Services exposed:
- **Control Center Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI backend API**: [http://localhost:8000](http://localhost:8000)
- **API Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Running Locally (Alternative)

#### Backend setup:
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Frontend setup:
```bash
cd apps/web
npm install
npm run dev
```

---

## Benchmarks & Evaluation

To evaluate the AI Investigator's accuracy, a test suite of 100+ synthetic cases is included.

Run evaluation tests:
```bash
cd apps/api
python scripts/evaluate_ai.py
```

### Measured Performance
- **Root Cause Accuracy**: 97.6%
- **False Auto-Resolution Rate**: **0.0%** (strict boundary adherence)
- **P99 Reconciliation latency**: 0.0082ms (sub-millisecond)
- **Throughput**: 144,550.47 tx/sec

View live reports by visiting the **`/benchmark`** and **`/system`** tabs on the web dashboard.
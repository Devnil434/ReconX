# ReconX

### Autonomous Payment Reconciliation Investigator

ReconX investigates payment and settlement exceptions using deterministic financial evidence, AI-assisted root-cause analysis, and an independent policy engine that decides whether an action is safe.

> *AI investigates. Policy authorizes. Verification proves.*

[Architecture](docs/architecture.md) · [Threat Model](docs/threat-model.md) · [Benchmark Report](docs/benchmark.md) · [Demo Script](docs/demo-script.md) · [Known Limitations](docs/limitations.md)

```
┌─────────────────────────────────────────────────────────┐
│                         RECONX                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  100,000 transactions           144,550 tx/s            │
│  97.6% root-cause accuracy      P99 latency < 0.01ms    │
│  98.8% action accuracy          100% human-review recall│
│  0.0% false auto-resolution     100% idempotency rate   │
│                                                         │
│  Deterministic code calculates what happened.           │
│  AI investigates why it happened.                       │
│  Policy engine decides what can happen next.            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## High-Level Architecture

```
                         RAZORPAY TEST MODE
                                │
                                ▼
                         WEBHOOK GATEWAY
                                │
                   ┌────────────┴────────────┐
                   │                         │
              Verify HMAC              Event ID
              (Raw Body)                dedupe
                   │                         │
                   └────────────┬────────────┘
                                │
                                ▼
                         EVENT STORE
                          PostgreSQL
                                │
                                ▼
                          REDIS QUEUE (RQ)
                                │
                                ▼
                         WORKER POOL
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
            RECONCILE      INVESTIGATE       VERIFY
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                          RISK ENGINE
                                │
                          POLICY ENGINE
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
          AUTO-RESOLVE     HUMAN REVIEW         BLOCK
               │                │
               └────────┬───────┘
                        ▼
                  ACTION EXECUTOR
                        │
                        ▼
                   RAZORPAY API
                        │
                        ▼
                  STATE VERIFIER
                        │
                        ▼
                 RECONCILE AGAIN
                        │
                        ▼
                    AUDIT LOG
                        │
                        ▼
                 COMMAND CENTER (Next.js)
```

---

## Key Capabilities

1. **High-Throughput Deterministic Engine**: Processes transaction matching with sub-millisecond median latencies (~0.0032ms), achieving throughputs over **144,000 tx/sec**.
2. **AI Investigator with Honest Policy Bounds**: Evaluates exceptions via AI reasoning providers. Operates under an **Honest Exception List** policy boundary:
   - **Auto-Resolves**: Fee/tax schedule mismatch, sub-paisa rounding variance ($\le ₹1$).
   - **Blocks / Escalates to Humans**: Missing bank credit (missing UTR), duplicate settlement batches, partial payouts, low-confidence hypotheses, high financial exposure.
3. **Control Center Dashboard**: Next.js 16 Web UI featuring:
   - Reusable KPI cards with sparkline/trend tags.
   - Reconciliation health bars (real-time matched rate vs exception rate).
   - Case stream (live feed with status tags).
   - **Interactive Explainability Drawer ("Why?" Drawer)**: Breaks down financial state, root cause summary, AI confidence meter, ranked hypotheses, verified/unverified evidence checklist, policy engine variables, and execution timeline.
4. **One-Click Demo Scenarios**: Interactive playback panel executing predefined scenario endpoints:
   - `Fee Mismatch` (Low-risk auto-resolution)
   - `Missing Bank Credit` (Human review escalation)
   - `Duplicate Settlement` (High-risk automated block)
   - `Unknown Discrepancy` (Low confidence review)
   - `AI Failure` (Graceful fallback to manual queue)
5. **Observability & Performance Metrics**: Exposes `/system` and `/system/queues` showing live database status, Redis queue depth (`reconciliation`, `investigation`, `actions`, `dead_letter`), active workers count, and AI cost/token tracking.
6. **Request ID Middleware**: Injects `X-Request-ID` header to trace contexts across requests.

---

## Stack

- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts
- **Backend API**: FastAPI, Python 3.12, SQLAlchemy ORM, Alembic
- **Task Queue**: RQ (Redis Queue), Redis 7
- **Database**: PostgreSQL 17
- **Observability**: Prometheus metrics, Redis queue metrics, AI cost tracker
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yml`)

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- OpenAI API Key (or mock mode fallback)

### 1. Configure Environments
Copy the example environment files:

```bash
# Main Template
cp .env.example .env

# Backend App Environment
cp .env.example apps/api/.env

# Frontend App Environment
cp apps/web/.env.local.example apps/web/.env.local
```

### 2. Run with Docker Compose (Scaled Workers)
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

## Test & QA Suite

Run the full automated test suite:
```bash
cd apps/api
pytest -v
```

Run frontend lint and build:
```bash
cd apps/web
npm run lint
npm run build
```

---

## Benchmarks & Evaluation

Run evaluation tests against 1,000 labeled test cases:
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
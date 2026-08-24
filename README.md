# ReconX

> Autonomous Payment Reconciliation Investigator

ReconX investigates payment reconciliation exceptions,
identifies root causes, and safely automates low-risk resolutions.

## Architecture

Razorpay
→ Ingestion
→ PostgreSQL
→ Deterministic Reconciliation
→ AI Investigator
→ Policy Engine
→ Autonomous Action
→ Audit Trail

## Stack

- Next.js
- TypeScript
- Tailwind
- shadcn/ui
- FastAPI
- Python
- PostgreSQL
- Redis
- SQLAlchemy
- Razorpay APIs/Webhooks
- LLM

## Development

### Start infrastructure

```bash
docker compose up -d
```

### Start API

```bash
cd apps/api

# Windows
.venv\Scripts\activate

uvicorn app.main:app --reload --port 8000
```

### Start web

```bash
cd apps/web

npm run dev
```

### Services

- **Web:** http://localhost:3000
- **API:** http://localhost:8000
- **API docs:** http://localhost:8000/docs
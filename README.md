# ReconX

> Autonomous Payment Reconciliation Investigator

ReconX investigates payment reconciliation exceptions, identifies root causes, and safely automates low-risk resolutions — powered by deterministic rules, AI reasoning, and a human-approval policy engine.

---

## Core Principle

```
Code determines what happened.
AI determines why it happened.
Policy determines what can happen next.
```

---

## Architecture

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
  Deterministic Reconciliation Engine
         │
    ┌────┴────┐
    ▼         ▼
MATCHED    EXCEPTION
               │
               ▼
        AI Investigator
               │
               ▼
         Policy Engine
           ┌──┴──┐
           ▼     ▼
      Auto-      Human
      Resolve    Review
           └──┬──┘
              ▼
          Audit Log
              │
              ▼
       Control Center (Web UI)
```

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS, shadcn/ui |
| Backend API | FastAPI, Python |
| Database | PostgreSQL 17 (SQLAlchemy + Alembic) |
| Cache / Queue | Redis 7 |
| Payment Gateway | Razorpay APIs & Webhooks |
| AI | OpenAI (GPT) |
| Infrastructure | Docker Compose |

---

## Project Structure

```
ReconX/
├── apps/
│   ├── api/                  # FastAPI backend
│   │   └── app/
│   │       ├── api/routes/   # HTTP endpoints (webhooks, reconciliation, investigations, cases)
│   │       ├── services/     # Business logic (reconciliation, investigator, policy, actions)
│   │       ├── models/       # SQLAlchemy ORM models
│   │       ├── integrations/ # Razorpay client
│   │       ├── ai/           # LLM investigator
│   │       ├── workers/      # Background workers
│   │       └── core/         # Config, DB, dependencies
│   └── web/                  # Next.js frontend (Control Center)
├── docs/                     # Architecture & decision records
├── docker-compose.yml        # PostgreSQL + Redis
└── .env.example              # Environment variable template
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- Razorpay account (test mode keys)
- OpenAI API key

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd ReconX
cp .env.example apps/api/.env
# Fill in your Razorpay and OpenAI keys in apps/api/.env
```

### 2. Start infrastructure

```bash
docker compose up -d
```

This starts:
- **PostgreSQL 17** on port `5432`
- **Redis 7** on port `6379`

### 3. Start the API

```bash
cd apps/api

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --port 8000
```

### 4. Start the Web UI

```bash
cd apps/web
npm install
npm run dev
```

---

## Environment Variables

Copy `.env.example` to `apps/api/.env` and fill in the values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `RAZORPAY_KEY_ID` | Razorpay API key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay API key secret |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay webhook signing secret |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | OpenAI model (e.g. `gpt-4o-mini`) |
| `NEXT_PUBLIC_API_URL` | API base URL used by the frontend |

---

## Services

| Service | URL |
|---|---|
| Web (Control Center) | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (Redoc) | http://localhost:8000/redoc |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/webhooks/razorpay` | Ingest Razorpay webhook events |
| `POST` | `/reconciliation/run` | Trigger reconciliation manually |
| `GET` | `/reconciliation/status` | Get reconciliation summary |
| `GET` | `/investigations` | List all investigations |
| `GET` | `/investigations/{id}` | Get investigation detail |
| `GET` | `/cases` | List exception cases |
| `GET` | `/health` | Health check |

---

## Running Tests

```bash
cd apps/api
pytest
```
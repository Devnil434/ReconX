# Production deployment

This layout uses Vercel for the Next.js app, Render for the FastAPI API and
RQ worker, managed PostgreSQL (Neon or Supabase), and Upstash Redis. Razorpay
must remain in Test Mode until production controls have been reviewed.

## 1. Provision managed services

Create a PostgreSQL database in Neon or Supabase and copy its connection URL.
The API requires the SQLAlchemy psycopg URL form:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Create an Upstash Redis database and copy its TLS Redis URL. It normally begins
with `rediss://`; retain the scheme and any query parameters exactly as issued.

## 2. Deploy the API and worker on Render

Connect this repository in Render and apply [`render.yaml`](../render.yaml).
It creates two services from the same backend image: `reconx-api` and
`reconx-worker`.

Set the following values on **both** services where applicable:

| Variable | API | Worker |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Yes |
| `REDIS_URL` | Yes | Yes |
| `RAZORPAY_MODE` | `test` | `test` |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` | Yes | Yes |
| `RAZORPAY_WEBHOOK_SECRET` | Yes | Yes |
| `GEMINI_API_KEY` | Yes | Yes |
| `CORS_ORIGINS` | Vercel production URL | Not needed |

Before directing traffic at the API, run migrations once from the API service's
shell:

```bash
alembic upgrade head
```

Confirm `https://<api-host>/health` succeeds. Configure the Razorpay Test Mode
webhook URL as `https://<api-host>/webhooks/razorpay` and use the same webhook
secret in Render. Check the exact route in the API docs if your Razorpay event
configuration uses another path.

## 3. Deploy the frontend on Vercel

The frontend is deployed to Vercel at [https://reconx-phi.vercel.app](https://reconx-phi.vercel.app).

When configuring a new deployment:
1. Import the repository into Vercel and set **Root Directory** to `apps/web`.
2. Add this production environment variable:

```text
NEXT_PUBLIC_API_URL=https://<your-render-api-host>
```

3. Add the resulting Vercel URL (`https://reconx-phi.vercel.app`) to the backend API `CORS_ORIGINS` environment variable in Render.

> [!NOTE]
> **Built-in Offline Resilience**: ReconX includes a built-in offline demo fallback layer. If the backend is starting up or temporarily unreachable, the frontend seamlessly serves high-fidelity synthetic demo data (1,284 transactions, 37 exceptions across all policy lanes) so the Command Center is always fully interactive.

## Release checklist

- API `/health` is healthy and database migrations are at `head`.
- API and worker use the identical PostgreSQL and Upstash Redis URLs.
- Razorpay dashboard is explicitly in Test Mode; no live keys are present.
- `CORS_ORIGINS` lists only approved Vercel domains.
- A test webhook reaches the API and its related job is processed by the worker.
- Vercel has `NEXT_PUBLIC_API_URL` set to the public HTTPS API URL.

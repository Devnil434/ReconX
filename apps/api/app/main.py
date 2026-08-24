from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.webhooks import router as webhook_router

app = FastAPI(
    title="ReconX API",
    description="Autonomous Payment Reconciliation Investigator",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(webhook_router)
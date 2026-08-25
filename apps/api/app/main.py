from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.cases import (
    router as cases_router,
)
from app.api.routes.health import (
    router as health_router,
)
from app.api.routes.investigations import (
    router as investigations_router,
)
from app.api.routes.reconciliation import (
    router as reconciliation_router,
)
from app.api.routes.webhooks import (
    router as webhook_router,
)

app = FastAPI(
    title="ReconX API",
    description=(
        "Autonomous Payment "
        "Reconciliation Investigator"
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router
)

app.include_router(
    webhook_router
)

app.include_router(
    reconciliation_router
)

app.include_router(
    investigations_router
)

app.include_router(
    cases_router
)
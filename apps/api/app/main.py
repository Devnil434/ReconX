
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest

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
from app.api.routes.demo import (
    router as demo_router,
)
from app.api.routes.system import (
    router as system_router,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware

configure_logging()

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app = FastAPI(
    title="ReconX API",
    description=(
        "Autonomous Payment "
        "Reconciliation Investigator"
    ),
    version="0.2.0",
)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain",
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

app.include_router(
    system_router
)

app.include_router(
    demo_router
)

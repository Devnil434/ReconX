from fastapi import FastAPI

from app.api.routes.health import (
    router as health_router,
)

from app.api.routes.webhooks import (
    router as webhook_router,
)

from app.api.routes.reconciliation import (
    router as reconciliation_router,
)


app = FastAPI(
    title="RecoverRecon API",
    description=(
        "Autonomous Payment "
        "Reconciliation Investigator"
    ),
    version="0.2.0",
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
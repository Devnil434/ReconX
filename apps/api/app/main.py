# pyrefly: ignore [missing-import]
from fastapi import FastAPI

app = FastAPI(
    title="RecoverRecon API",
    description="Autonomous Payment Reconciliation Investigator",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "recover-recon-api",
        "version": "0.1.0",
    }
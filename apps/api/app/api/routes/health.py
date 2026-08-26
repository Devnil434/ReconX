from fastapi import APIRouter

from app.queue.redis import redis_client

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():
    return {
        "status": "ok",
    }


@router.get("/ready")
def readiness():
    redis_ok = False
    try:
        redis_client.ping()
        redis_ok = True
    except Exception:
        pass

    return {
        "api": True,
        "redis": redis_ok,
    }
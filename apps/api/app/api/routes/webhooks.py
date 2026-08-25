import hashlib
import hmac

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Request,
)

from app.core.config import settings

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


def verify_signature(
    body: bytes,
    signature: str,
    secret: str,
) -> bool:

    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected,
        signature,
    )


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(
        default=None
    ),
    x_razorpay_event_id: str | None = Header(
        default=None
    ),
):

    body = await request.body()

    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing signature",
        )

    if not x_razorpay_event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing event ID",
        )

    if not verify_signature(
        body,
        x_razorpay_signature,
        settings.razorpay_webhook_secret,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature",
        )

    return {
        "received": True,
        "event_id": x_razorpay_event_id,
    }
from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
):
    raw_body = await request.body()

    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay signature",
        )

    if not x_razorpay_event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay event ID",
        )

    # Phase 0:
    # signature verification + idempotency implementation
    # will be added before real webhook processing.

    return {
        "received": True,
        "event_id": x_razorpay_event_id,
    }
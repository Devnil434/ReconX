import hashlib
import hmac

from app.core.config import settings


def verify_webhook_signature(
    body: bytes,
    signature: str,
) -> bool:

    if not settings.razorpay_webhook_secret:
        raise ValueError("RAZORPAY_WEBHOOK_SECRET is not configured.")

    expected = hmac.new(
        settings.razorpay_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected,
        signature,
    )
# apps/api/app/integrations/razorpay/client.py

from typing import Any

import razorpay

from app.core.config import settings


class RazorpayClient:
    def __init__(self):
        self.client = None

        if (
            settings.razorpay_key_id
            and settings.razorpay_key_secret
        ):
            self.client = razorpay.Client(
                auth=(
                    settings.razorpay_key_id,
                    settings.razorpay_key_secret,
                )
            )

    @property
    def is_live(self) -> bool:
        return self.client is not None

    def fetch_payment(
        self,
        payment_id: str,
    ):
        if self.client is None:
            return {
                "id": payment_id,
                "status": "captured",
                "mock": True,
            }

        return self.client.payment.fetch(  # type: ignore[attr-defined]
            payment_id
        )

    def fetch_refund(
        self,
        refund_id: str,
    ):
        if self.client is None:
            return {
                "id": refund_id,
                "status": "processed",
                "mock": True,
            }

        return self.client.refund.fetch(  # type: ignore[attr-defined]
            refund_id
        )

    def create_refund(
        self,
        payment_id: str,
        amount: int,
        idempotency_key: str | None = None,
    ):
        if self.client is None:
            return {
                "id": f"rfnd_mock_{payment_id}",
                "status": "processed",
                "amount": amount,
                "mock": True,
            }

        data: dict[str, Any] = {"amount": amount}
        if idempotency_key:
            data["receipt"] = idempotency_key  # Razorpay uses receipt for idempotency

        return self.client.payment.refund(  # type: ignore[attr-defined]
            payment_id,
            data,
        )
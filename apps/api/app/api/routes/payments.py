"""
payments.py — server-side Razorpay order creation.

POST /api/payments/create-order
  Body  : { amount_paise, currency, name, email, contact }
  Return: { order_id, amount, currency, key_id }

RAZORPAY_KEY_SECRET is used server-side only and is NEVER returned.
Only the public key_id is included in the response for the Checkout.js
client to use.
"""
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.integrations.razorpay.client import RazorpayClient

router = APIRouter(prefix="/api/payments", tags=["Payments"])

# Shared client instance — initialised once at module load
_rzp = RazorpayClient()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class CreateOrderRequest(BaseModel):
    amount_paise: int = Field(
        ...,
        gt=0,
        description="Amount in paise (100 paise = ₹1). Min: 100 (₹1).",
    )
    currency: str = Field(default="INR", max_length=3)
    name: str = Field(default="", max_length=256)
    email: str = Field(default="", max_length=256)
    contact: str = Field(default="", max_length=20)


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int       # paise
    currency: str
    key_id: str       # public key only — secret NEVER returned


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(body: CreateOrderRequest) -> CreateOrderResponse:
    """
    Creates a Razorpay order server-side and returns the order_id +
    public key to the browser.  The key secret never leaves the server.

    The frontend then opens Razorpay Checkout with:
      { order_id, amount, currency, key: key_id }
    """
    receipt = f"rcx_{uuid.uuid4().hex[:12]}"

    try:
        order = _rzp.create_order(
            amount=body.amount_paise,
            currency=body.currency,
            receipt=receipt,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Razorpay order creation failed: {exc}",
        )

    return CreateOrderResponse(
        order_id=order["id"],
        amount=order["amount"],
        currency=order["currency"],
        key_id=settings.razorpay_key_id or "",
    )

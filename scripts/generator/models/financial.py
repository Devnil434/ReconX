from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Payment(BaseModel):
    id: str
    razorpay_payment_id: str
    order_id: str
    amount: int
    currency: str
    status: str
    fee: int
    tax: int
    created_at: datetime
    captured_at: Optional[datetime] = None


class Settlement(BaseModel):
    id: str
    razorpay_settlement_id: str
    payment_id: str
    utr: str
    amount: int
    fee: int
    tax: int
    status: str
    settlement_date: datetime


class BankTransaction(BaseModel):
    id: str
    bank_reference: str
    utr: str
    amount: int
    transaction_type: str
    transaction_date: datetime
    description: str


class Refund(BaseModel):
    id: str
    payment_id: str
    amount: int
    status: str
    created_at: datetime


class GroundTruth(BaseModel):
    case_id: str
    payment_id: str
    exception_type: Optional[str]
    expected_status: str
    expected_difference: int
    expected_root_cause: Optional[str]
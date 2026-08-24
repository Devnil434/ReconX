from pydantic import BaseModel


class ReconciliationResult(BaseModel):
    status: str
    expected_amount: int
    actual_amount: int
    difference: int
    reason_codes: list[str]
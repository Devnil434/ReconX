from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ReconciliationResult(Base):
    __tablename__ = "reconciliation_results"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    payment_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )

    settlement_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )

    bank_transaction_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
    )

    match_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    expected_amount: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    actual_amount: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    difference: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    reason_codes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
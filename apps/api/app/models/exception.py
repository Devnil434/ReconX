from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ReconciliationException(Base):
    __tablename__ = "reconciliation_exceptions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    payment_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )

    exception_type: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    expected_amount: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    actual_amount: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    difference: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="open",
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
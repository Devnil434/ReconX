from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    bank_reference: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    utr: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
    )

    amount: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    transaction_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
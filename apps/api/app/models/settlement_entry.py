from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SettlementEntry(Base):
    __tablename__ = "settlement_entries"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    settlement_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    entity_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    entry_type: Mapped[str] = mapped_column(
        String(32),
    )

    debit: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    credit: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    amount: Mapped[int] = mapped_column(
        BigInteger,
    )

    fee: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    tax: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class InvestigationTrace(Base):
    __tablename__ = "investigation_traces"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    step: Mapped[str] = mapped_column(
        String(64),
    )

    status: Mapped[str] = mapped_column(
        String(32),
    )

    details: Mapped[str | None] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
    )
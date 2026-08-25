from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    actor: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
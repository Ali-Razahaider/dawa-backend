from __future__ import annotations  # to be added to use later declared stuff
from datetime import UTC, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Boolean
from database import Base


class Prescription(Base):
    __tablename__ = "prescription"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_url: Mapped[str] = mapped_column(
        String(500),
    )
    gemini_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # user_id : Mapped[User]

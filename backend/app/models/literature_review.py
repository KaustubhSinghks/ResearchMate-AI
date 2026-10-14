from datetime import datetime

from sqlalchemy import ARRAY, JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewOutline(Base):
    __tablename__ = "review_outlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)

    themes: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {theme: [document_id, ...]}
    trends: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {year: count}
    gaps: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    outline: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # structured outline sections
    suggested_reading: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

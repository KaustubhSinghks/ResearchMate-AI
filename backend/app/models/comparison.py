from datetime import datetime

from sqlalchemy import ARRAY, JSON, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SavedComparison(Base):
    __tablename__ = "saved_comparisons"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    document_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

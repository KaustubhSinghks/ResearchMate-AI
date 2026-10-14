from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NoteType(str, PyEnum):
    NOTE = "note"
    HIGHLIGHT = "highlight"
    TODO = "todo"
    SUMMARY = "summary"


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    type: Mapped[NoteType] = mapped_column(
        Enum(NoteType, name="note_type", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=NoteType.NOTE,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    section_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)  # relevant for todos

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

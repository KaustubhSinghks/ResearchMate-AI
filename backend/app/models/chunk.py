from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.voyage_embedding_dim), nullable=True)

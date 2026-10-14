from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import ARRAY, JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentStatus(str, PyEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    folder_id: Mapped[int | None] = mapped_column(ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(500), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    semantic_scholar_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    datasets: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    models_used: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    algorithms: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    metrics: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    problem_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology: Mapped[str | None] = mapped_column(Text, nullable=True)
    results: Mapped[str | None] = mapped_column(Text, nullable=True)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusions: Mapped[str | None] = mapped_column(Text, nullable=True)
    future_work: Mapped[str | None] = mapped_column(Text, nullable=True)

    short_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    section_summaries: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {section: summary}
    key_contributions: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=DocumentStatus.PROCESSING,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


class DocumentAuthor(Base):
    __tablename__ = "document_authors"

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
    author_order: Mapped[int] = mapped_column(Integer, default=0)

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import ARRAY, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CitationRelationType(str, PyEnum):
    CITES = "cites"  # this document's references
    CITED_BY = "cited_by"  # papers that cite this document
    SIMILAR = "similar"  # in-corpus embedding similarity
    RECOMMENDED = "recommended"  # Semantic Scholar recommendation


class CitationRelation(Base):
    __tablename__ = "citation_relations"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    relation: Mapped[CitationRelationType] = mapped_column(
        Enum(
            CitationRelationType,
            name="citation_relation_type",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )

    # Either points to another in-corpus document, or an external paper (cached fields below)
    related_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    external_paper_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Semantic Scholar paperId
    external_title: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    external_authors: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    external_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    score: Mapped[float | None] = mapped_column(nullable=True)  # similarity score, when applicable

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

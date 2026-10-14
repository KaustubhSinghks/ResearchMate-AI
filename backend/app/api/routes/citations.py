from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Author, Document, DocumentAuthor
from app.models.user import User
from app.schemas.citation_format import CitationFormatResponse
from app.services.citation_formatter import format_all, format_bibtex, format_ris

router = APIRouter(tags=["citations"])


def _authors_for_document(db: Session, document_id: int) -> list[str]:
    rows = (
        db.query(Author.name)
        .join(DocumentAuthor, DocumentAuthor.author_id == Author.id)
        .filter(DocumentAuthor.document_id == document_id)
        .order_by(DocumentAuthor.author_order)
        .all()
    )
    return [r[0] for r in rows]


def _get_owned_document(db: Session, document_id: int, owner_id: int) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/documents/{document_id}/citation", response_model=CitationFormatResponse)
def get_citation(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitationFormatResponse:
    document = _get_owned_document(db, document_id, current_user.id)
    authors = _authors_for_document(db, document_id)
    return CitationFormatResponse(**format_all(document.title, authors, document.year, document.venue))


@router.get("/citations/export", response_class=PlainTextResponse)
def export_citations(
    document_ids: list[int] = Query(...),
    format: str = Query("bibtex", pattern="^(bibtex|ris)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> str:
    documents = (
        db.query(Document).filter(Document.id.in_(document_ids), Document.owner_id == current_user.id).all()
    )
    formatter = format_bibtex if format == "bibtex" else format_ris
    separator = "\n\n"
    entries = [
        formatter(doc.title, _authors_for_document(db, doc.id), doc.year, doc.venue) for doc in documents
    ]
    return separator.join(entries)

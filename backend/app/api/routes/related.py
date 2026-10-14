from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.related import RelatedPaper
from app.services import semantic_scholar
from app.services.recommendation import find_similar_documents

router = APIRouter(tags=["related"])


def _get_owned_document(db: Session, document_id: int, owner_id: int) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/documents/{document_id}/related/similar", response_model=list[RelatedPaper])
def related_similar(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RelatedPaper]:
    """Similar papers already in the user's corpus, via embedding similarity."""
    document = _get_owned_document(db, document_id, current_user.id)
    similar = find_similar_documents(db, document)
    return [
        RelatedPaper(
            relation="similar",
            document_id=doc.id,
            external_paper_id=None,
            title=doc.title,
            authors=None,
            year=doc.year,
            url=None,
            score=score,
        )
        for doc, score in similar
    ]


def _resolve_semantic_scholar_id(document: Document) -> str | None:
    if document.semantic_scholar_id:
        return document.semantic_scholar_id
    return semantic_scholar.find_paper_id_by_title(document.title)


@router.get("/documents/{document_id}/related/references", response_model=list[RelatedPaper])
def related_references(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RelatedPaper]:
    """Papers referenced by this document (its bibliography), via Semantic Scholar."""
    document = _get_owned_document(db, document_id, current_user.id)
    paper_id = _resolve_semantic_scholar_id(document)
    if not paper_id:
        return []
    papers = semantic_scholar.get_references(paper_id)
    return [
        RelatedPaper(
            relation="cites",
            document_id=None,
            external_paper_id=p["paper_id"],
            title=p["title"] or "Untitled",
            authors=p["authors"],
            year=p["year"],
            url=p["url"],
            score=None,
        )
        for p in papers
    ]


@router.get("/documents/{document_id}/related/citing", response_model=list[RelatedPaper])
def related_citing(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RelatedPaper]:
    """Papers that cite this document, via Semantic Scholar."""
    document = _get_owned_document(db, document_id, current_user.id)
    paper_id = _resolve_semantic_scholar_id(document)
    if not paper_id:
        return []
    papers = semantic_scholar.get_citations(paper_id)
    return [
        RelatedPaper(
            relation="cited_by",
            document_id=None,
            external_paper_id=p["paper_id"],
            title=p["title"] or "Untitled",
            authors=p["authors"],
            year=p["year"],
            url=p["url"],
            score=None,
        )
        for p in papers
    ]


@router.get("/documents/{document_id}/related/recommended", response_model=list[RelatedPaper])
def related_recommended(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RelatedPaper]:
    """Semantic Scholar's own recommendation engine for this paper (covers 'recent' and 'seminal' work)."""
    document = _get_owned_document(db, document_id, current_user.id)
    paper_id = _resolve_semantic_scholar_id(document)
    if not paper_id:
        return []
    papers = semantic_scholar.get_recommendations(paper_id)
    return [
        RelatedPaper(
            relation="recommended",
            document_id=None,
            external_paper_id=p["paper_id"],
            title=p["title"] or "Untitled",
            authors=p["authors"],
            year=p["year"],
            url=p["url"],
            score=None,
        )
        for p in papers
    ]

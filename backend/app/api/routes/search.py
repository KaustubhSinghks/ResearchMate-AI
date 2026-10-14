import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.search import SearchResult
from app.services.semantic_search import keyword_search_documents, semantic_search_chunks

router = APIRouter(tags=["search"])
logger = logging.getLogger(__name__)


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SearchResult]:
    results: dict[int, SearchResult] = {}

    for doc in keyword_search_documents(db, q, owner_id=current_user.id):
        results[doc.id] = SearchResult(
            document_id=doc.id,
            title=doc.title,
            year=doc.year,
            venue=doc.venue,
            short_summary=doc.short_summary,
            matched_snippet=doc.abstract[:280] if doc.abstract else None,
            score=1.0,
            match_type="keyword",
        )

    try:
        semantic_matches = semantic_search_chunks(db, q, owner_id=current_user.id, limit=10)
    except Exception:  # noqa: BLE001 - embedding provider issues shouldn't sink keyword results
        logger.exception("Semantic search failed; returning keyword-only results")
        semantic_matches = []

    for match in semantic_matches:
        doc = match.document
        if doc.id in results:
            continue
        results[doc.id] = SearchResult(
            document_id=doc.id,
            title=doc.title,
            year=doc.year,
            venue=doc.venue,
            short_summary=doc.short_summary,
            matched_snippet=match.chunk.text[:280],
            score=match.score,
            match_type="semantic",
        )

    return sorted(results.values(), key=lambda r: r.score, reverse=True)

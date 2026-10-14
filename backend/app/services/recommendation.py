from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embeddings import embed_query


def find_similar_documents(db: Session, document: Document, limit: int = 10) -> list[tuple[Document, float]]:
    """In-corpus recommendations: embed this document's abstract/summary and find the nearest
    chunks belonging to other documents owned by the same user, aggregated to one score per document."""
    query_text = document.abstract or document.short_summary or document.title
    query_embedding = embed_query(query_text)

    distance = Chunk.embedding.cosine_distance(query_embedding)
    rows = (
        db.query(Chunk, Document, distance)
        .join(Document, Chunk.document_id == Document.id)
        .filter(
            Document.owner_id == document.owner_id,
            Document.id != document.id,
            Chunk.embedding.is_not(None),
        )
        .order_by(distance.asc())
        .limit(limit * 5)
        .all()
    )

    best_score_by_doc: dict[int, tuple[Document, float]] = {}
    for _chunk, doc, dist in rows:
        score = 1 - dist
        if doc.id not in best_score_by_doc or score > best_score_by_doc[doc.id][1]:
            best_score_by_doc[doc.id] = (doc, score)

    ranked = sorted(best_score_by_doc.values(), key=lambda pair: pair[1], reverse=True)
    return ranked[:limit]

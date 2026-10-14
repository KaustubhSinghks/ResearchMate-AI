from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embeddings import embed_query


@dataclass
class ChunkMatch:
    document: Document
    chunk: Chunk
    score: float  # cosine similarity, higher is better


def semantic_search_chunks(
    db: Session,
    query: str,
    owner_id: int,
    document_id: int | None = None,
    limit: int = 6,
) -> list[ChunkMatch]:
    query_embedding = embed_query(query)

    distance = Chunk.embedding.cosine_distance(query_embedding)
    q = (
        db.query(Chunk, Document, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .filter(Document.owner_id == owner_id, Chunk.embedding.is_not(None))
    )
    if document_id is not None:
        q = q.filter(Chunk.document_id == document_id)

    rows = q.order_by(distance.asc()).limit(limit).all()
    return [ChunkMatch(document=doc, chunk=chunk, score=1 - dist) for chunk, doc, dist in rows]


def keyword_search_documents(db: Session, query: str, owner_id: int, limit: int = 10) -> list[Document]:
    pattern = f"%{query}%"
    return (
        db.query(Document)
        .filter(
            Document.owner_id == owner_id,
            or_(
                Document.title.ilike(pattern),
                Document.abstract.ilike(pattern),
                Document.venue.ilike(pattern),
            ),
        )
        .limit(limit)
        .all()
    )

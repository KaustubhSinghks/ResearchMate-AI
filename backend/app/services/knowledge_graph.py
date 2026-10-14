from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.citation import CitationRelation, CitationRelationType
from app.models.document import Author, Document, DocumentAuthor
from app.models.folder import DocumentTag, Tag
from app.schemas.graph import GraphEdge, GraphNode, GraphResponse


def build_knowledge_graph(db: Session, owner_id: int) -> GraphResponse:
    documents = db.query(Document).filter(Document.owner_id == owner_id).all()
    doc_ids = [d.id for d in documents]

    nodes: list[GraphNode] = [GraphNode(id=f"doc-{d.id}", label=d.title, type="document") for d in documents]
    edges: list[GraphEdge] = []

    # Authors
    author_rows = (
        db.query(DocumentAuthor, Author)
        .join(Author, DocumentAuthor.author_id == Author.id)
        .filter(DocumentAuthor.document_id.in_(doc_ids))
        .all()
    )
    seen_authors: set[int] = set()
    for doc_author, author in author_rows:
        if author.id not in seen_authors:
            nodes.append(GraphNode(id=f"author-{author.id}", label=author.name, type="author"))
            seen_authors.add(author.id)
        edges.append(GraphEdge(source=f"doc-{doc_author.document_id}", target=f"author-{author.id}", type="authored"))

    # Tags, and shared-tag document-document clustering
    tag_rows = (
        db.query(DocumentTag, Tag)
        .join(Tag, DocumentTag.tag_id == Tag.id)
        .filter(DocumentTag.document_id.in_(doc_ids))
        .all()
    )
    seen_tags: set[int] = set()
    docs_by_tag: dict[int, list[int]] = defaultdict(list)
    for doc_tag, tag in tag_rows:
        if tag.id not in seen_tags:
            nodes.append(GraphNode(id=f"tag-{tag.id}", label=tag.name, type="tag"))
            seen_tags.add(tag.id)
        edges.append(GraphEdge(source=f"doc-{doc_tag.document_id}", target=f"tag-{tag.id}", type="tagged"))
        docs_by_tag[tag.id].append(doc_tag.document_id)

    shared_tag_counts: dict[tuple[int, int], int] = defaultdict(int)
    for tagged_doc_ids in docs_by_tag.values():
        for i, doc_a in enumerate(tagged_doc_ids):
            for doc_b in tagged_doc_ids[i + 1 :]:
                key = (min(doc_a, doc_b), max(doc_a, doc_b))
                shared_tag_counts[key] += 1

    for (doc_a, doc_b), count in shared_tag_counts.items():
        edges.append(GraphEdge(source=f"doc-{doc_a}", target=f"doc-{doc_b}", type="similar", weight=float(count)))

    # Cached citation relations between in-corpus documents
    citation_rows = (
        db.query(CitationRelation)
        .filter(
            CitationRelation.document_id.in_(doc_ids),
            CitationRelation.related_document_id.is_not(None),
            CitationRelation.relation.in_([CitationRelationType.CITES, CitationRelationType.CITED_BY]),
        )
        .all()
    )
    for rel in citation_rows:
        edges.append(GraphEdge(source=f"doc-{rel.document_id}", target=f"doc-{rel.related_document_id}", type="cites"))

    return GraphResponse(nodes=nodes, edges=edges)

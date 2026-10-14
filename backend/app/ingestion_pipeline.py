import logging

from app.db.session import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Author, Document, DocumentAuthor, DocumentStatus
from app.services.chunking import chunk_document
from app.services.embeddings import embed_documents
from app.services.metadata_extraction import extract_metadata
from app.services.pdf_extraction import extract_pdf
from app.services.summarization import summarize_paper

logger = logging.getLogger(__name__)


def _get_or_create_author(db, name: str) -> Author:
    author = db.query(Author).filter(Author.name == name).first()
    if author is None:
        author = Author(name=name)
        db.add(author)
        db.flush()
    return author


def run_ingestion(document_id: int) -> None:
    """Runs the full pipeline for one document: extract -> chunk -> embed -> metadata -> summary."""
    db = SessionLocal()
    try:
        document = db.get(Document, document_id)
        if document is None:
            return

        try:
            extracted = extract_pdf(document.file_path)

            chunks = chunk_document(extracted)
            if chunks:
                embeddings = embed_documents([c.text for c in chunks])
                for chunk, embedding in zip(chunks, embeddings):
                    db.add(
                        Chunk(
                            document_id=document.id,
                            section=chunk.section,
                            page=chunk.page,
                            chunk_index=chunk.chunk_index,
                            text=chunk.text,
                            embedding=embedding,
                        )
                    )

            metadata = extract_metadata(extracted.full_text, extracted.title_guess)
            summary = summarize_paper(extracted.full_text, [s.name for s in extracted.sections])

            document.title = metadata.get("title") or extracted.title_guess or document.original_filename
            document.year = metadata.get("year")
            document.venue = metadata.get("venue")
            document.abstract = metadata.get("abstract")
            document.keywords = metadata.get("keywords") or []
            document.datasets = metadata.get("datasets") or []
            document.models_used = metadata.get("models_used") or []
            document.algorithms = metadata.get("algorithms") or []
            document.metrics = metadata.get("metrics") or []
            document.problem_statement = metadata.get("problem_statement")
            document.conclusions = metadata.get("conclusions")
            document.future_work = metadata.get("future_work")

            document.short_summary = summary.get("short_summary")
            document.key_contributions = summary.get("key_contributions") or []
            document.methodology = summary.get("methodology")
            document.results = summary.get("results")
            document.limitations = summary.get("limitations")
            document.section_summaries = summary.get("section_summaries") or {}

            for order, author_name in enumerate(metadata.get("authors") or []):
                author = _get_or_create_author(db, author_name)
                db.add(DocumentAuthor(document_id=document.id, author_id=author.id, author_order=order))

            document.status = DocumentStatus.READY
            document.error_message = None
            db.commit()
        except Exception as exc:  # noqa: BLE001 - persist failure state for the user to see
            logger.exception("Ingestion failed for document %s", document_id)
            db.rollback()
            document = db.get(Document, document_id)
            if document is not None:
                document.status = DocumentStatus.FAILED
                document.error_message = str(exc)
                db.commit()
    finally:
        db.close()

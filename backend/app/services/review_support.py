from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.folder import DocumentTag, Tag
from app.services.llm import generate_structured

_SCHEMA = {
    "type": "object",
    "properties": {
        "gaps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Under-explored intersections or open problems suggested by this set of papers.",
        },
        "outline": {
            "type": "object",
            "description": "Section name -> bullet points for a literature review outline.",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
        "suggested_reading": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Topics or paper types worth reading next, given gaps found.",
        },
    },
    "required": ["gaps", "outline", "suggested_reading"],
}

SYSTEM_PROMPT = (
    "You are a research assistant helping a student draft a literature review. "
    "Given summaries of several papers, identify gaps in the collective coverage, "
    "propose a literature review outline grouped by theme, and suggest what to read next."
)


def group_by_theme(db: Session, documents: list[Document]) -> dict[str, list[int]]:
    doc_ids = [d.id for d in documents]
    rows = (
        db.query(DocumentTag.document_id, Tag.name)
        .join(Tag, DocumentTag.tag_id == Tag.id)
        .filter(DocumentTag.document_id.in_(doc_ids))
        .all()
    )
    themes: dict[str, list[int]] = defaultdict(list)
    tagged_doc_ids = set()
    for document_id, tag_name in rows:
        themes[tag_name].append(document_id)
        tagged_doc_ids.add(document_id)

    untagged = [d.id for d in documents if d.id not in tagged_doc_ids]
    if untagged:
        themes["untagged"] = untagged

    return dict(themes)


def trends_over_time(documents: list[Document]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for doc in documents:
        year = str(doc.year) if doc.year else "unknown"
        counts[year] += 1
    return dict(sorted(counts.items()))


def _paper_block(document: Document) -> str:
    return (
        f"- {document.title} ({document.year or 'n.d.'}): {document.short_summary or document.abstract or 'no summary available'}\n"
        f"  keywords: {', '.join(document.keywords or []) or 'unknown'}"
    )


def suggest_gaps_and_outline(documents: list[Document]) -> dict[str, Any]:
    papers_text = "\n".join(_paper_block(d) for d in documents)
    user_prompt = f"Papers in this collection:\n{papers_text}"
    return generate_structured(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        tool_description="Record gaps, an outline, and suggested reading for a literature review.",
        input_schema=_SCHEMA,
    )

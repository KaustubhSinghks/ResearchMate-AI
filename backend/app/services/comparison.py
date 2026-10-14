from typing import Any

from app.models.document import Document
from app.services.llm import generate_structured

_ROW_SCHEMA = {
    "type": "object",
    "properties": {
        "document_id": {"type": "integer"},
        "title": {"type": "string"},
        "problem_addressed": {"type": "string"},
        "method_used": {"type": "string"},
        "dataset_or_benchmark": {"type": "string"},
        "performance": {"type": "string"},
        "strengths": {"type": "string"},
        "weaknesses": {"type": "string"},
        "novelty": {"type": "string"},
        "practical_applications": {"type": "string"},
    },
    "required": [
        "document_id",
        "title",
        "problem_addressed",
        "method_used",
        "dataset_or_benchmark",
        "performance",
        "strengths",
        "weaknesses",
        "novelty",
        "practical_applications",
    ],
}

_SCHEMA = {
    "type": "object",
    "properties": {
        "rows": {"type": "array", "items": _ROW_SCHEMA},
        "narrative_summary": {
            "type": "string",
            "description": "2-4 sentence narrative comparing the papers overall.",
        },
    },
    "required": ["rows", "narrative_summary"],
}

SYSTEM_PROMPT = (
    "You are a research assistant comparing academic papers for a literature review. "
    "Use only the provided summaries/metadata for each paper. Use the exact document_id given for each paper."
)


def _paper_block(document: Document) -> str:
    return (
        f"document_id: {document.id}\n"
        f"title: {document.title}\n"
        f"abstract: {document.abstract or 'unknown'}\n"
        f"problem_statement: {document.problem_statement or 'unknown'}\n"
        f"methodology: {document.methodology or 'unknown'}\n"
        f"results: {document.results or 'unknown'}\n"
        f"limitations: {document.limitations or 'unknown'}\n"
        f"datasets: {', '.join(document.datasets or []) or 'unknown'}\n"
        f"metrics: {', '.join(document.metrics or []) or 'unknown'}\n"
        f"key_contributions: {', '.join(document.key_contributions or []) or 'unknown'}\n"
    )


def compare_documents(documents: list[Document]) -> dict[str, Any]:
    papers_text = "\n\n".join(_paper_block(d) for d in documents)
    user_prompt = f"Compare these {len(documents)} papers:\n\n{papers_text}"
    return generate_structured(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        tool_description="Record a structured comparison of multiple research papers.",
        input_schema=_SCHEMA,
    )

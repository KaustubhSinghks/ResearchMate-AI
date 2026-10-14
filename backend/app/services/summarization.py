from typing import Any, TypedDict

from app.services.llm import generate_structured

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "short_summary": {"type": "string", "description": "A 3-5 sentence plain-language summary."},
        "key_contributions": {"type": "array", "items": {"type": "string"}},
        "methodology": {"type": "string"},
        "results": {"type": "string"},
        "limitations": {"type": "string"},
        "section_summaries": {
            "type": "object",
            "description": "Map of section name to a short summary of that section.",
            "additionalProperties": {"type": "string"},
        },
    },
    "required": ["short_summary", "key_contributions", "methodology", "results", "limitations", "section_summaries"],
}


class PaperSummary(TypedDict):
    short_summary: str
    key_contributions: list[str]
    methodology: str
    results: str
    limitations: str
    section_summaries: dict[str, str]


SYSTEM_PROMPT = (
    "You are a research assistant that summarizes academic papers for someone deciding whether "
    "to read the full paper. Be concise, accurate, and only summarize what is present in the text."
)

_MAX_INPUT_CHARS = 60_000


def summarize_paper(full_text: str, section_names: list[str]) -> PaperSummary:
    truncated = full_text[:_MAX_INPUT_CHARS]
    sections_hint = ", ".join(sorted(set(section_names))) or "unknown"
    user_prompt = (
        f"Summarize this paper. Detected sections: {sections_hint}.\n\n"
        f"Produce a section-wise summary only for sections that are actually present.\n\n"
        f"Paper text:\n{truncated}"
    )
    result = generate_structured(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        tool_description="Record a structured summary of a research paper.",
        input_schema=_SCHEMA,
    )
    return result  # type: ignore[return-value]

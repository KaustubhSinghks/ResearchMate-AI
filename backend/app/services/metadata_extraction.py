from typing import Any, TypedDict

from app.services.llm import generate_structured

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "year": {"type": ["integer", "null"]},
        "venue": {"type": ["string", "null"]},
        "abstract": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "datasets": {"type": "array", "items": {"type": "string"}},
        "models_used": {"type": "array", "items": {"type": "string"}},
        "algorithms": {"type": "array", "items": {"type": "string"}},
        "metrics": {"type": "array", "items": {"type": "string"}},
        "problem_statement": {"type": "string"},
        "conclusions": {"type": "string"},
        "future_work": {"type": "string"},
    },
    "required": [
        "title",
        "authors",
        "abstract",
        "keywords",
        "datasets",
        "models_used",
        "algorithms",
        "metrics",
        "problem_statement",
        "conclusions",
        "future_work",
    ],
}


class ExtractedMetadata(TypedDict):
    title: str
    authors: list[str]
    year: int | None
    venue: str | None
    abstract: str
    keywords: list[str]
    datasets: list[str]
    models_used: list[str]
    algorithms: list[str]
    metrics: list[str]
    problem_statement: str
    conclusions: str
    future_work: str


SYSTEM_PROMPT = (
    "You are a research assistant that extracts structured metadata from academic papers. "
    "Only use information present in the provided text. Leave a field as an empty string/array "
    "or null if it is not present rather than guessing."
)

# Gemini's free tier still has a large context window, but we cap input to keep costs/latency down.
_MAX_INPUT_CHARS = 60_000


def extract_metadata(full_text: str, title_guess: str | None) -> ExtractedMetadata:
    truncated = full_text[:_MAX_INPUT_CHARS]
    user_prompt = (
        f"Extract structured metadata from this paper.\n\n"
        f"Guessed title (may be wrong): {title_guess or 'unknown'}\n\n"
        f"Paper text:\n{truncated}"
    )
    result = generate_structured(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        tool_description="Record structured metadata extracted from a research paper.",
        input_schema=_SCHEMA,
    )
    return result  # type: ignore[return-value]

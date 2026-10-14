from pydantic import BaseModel


class SearchResult(BaseModel):
    document_id: int
    title: str
    year: int | None
    venue: str | None
    short_summary: str | None
    matched_snippet: str | None
    score: float
    match_type: str  # "keyword" | "semantic"

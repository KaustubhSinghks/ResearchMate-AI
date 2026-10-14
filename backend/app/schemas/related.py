from pydantic import BaseModel


class RelatedPaper(BaseModel):
    relation: str  # "cites" | "cited_by" | "similar" | "recommended"
    document_id: int | None  # set when the related paper is in-corpus
    external_paper_id: str | None
    title: str
    authors: list[str] | None
    year: int | None
    url: str | None
    score: float | None

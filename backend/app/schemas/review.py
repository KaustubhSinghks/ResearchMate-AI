from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewRequest(BaseModel):
    title: str
    document_ids: list[int]


class ReviewResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    document_ids: list[int]
    themes: dict | None
    trends: dict | None
    gaps: list[str] | None
    outline: dict | None
    suggested_reading: list[str] | None
    created_at: datetime

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class FolderCreate(BaseModel):
    name: str
    parent_id: int | None = None


class FolderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent_id: int | None


class TagCreate(BaseModel):
    name: str


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    year: int | None
    venue: str | None
    status: DocumentStatus
    short_summary: str | None
    created_at: datetime
    folder_id: int | None


class DocumentDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    original_filename: str
    year: int | None
    venue: str | None
    doi: str | None
    abstract: str | None
    keywords: list[str] | None
    datasets: list[str] | None
    models_used: list[str] | None
    algorithms: list[str] | None
    metrics: list[str] | None
    problem_statement: str | None
    methodology: str | None
    results: str | None
    limitations: str | None
    conclusions: str | None
    future_work: str | None
    short_summary: str | None
    section_summaries: dict | None
    key_contributions: list[str] | None
    status: DocumentStatus
    error_message: str | None
    created_at: datetime


class DocumentUpdate(BaseModel):
    title: str | None = None
    folder_id: int | None = None
    tag_names: list[str] | None = None

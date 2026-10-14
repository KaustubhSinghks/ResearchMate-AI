from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompareRequest(BaseModel):
    document_ids: list[int]


class PaperComparisonRow(BaseModel):
    document_id: int
    title: str
    problem_addressed: str
    method_used: str
    dataset_or_benchmark: str
    performance: str
    strengths: str
    weaknesses: str
    novelty: str
    practical_applications: str


class CompareResult(BaseModel):
    rows: list[PaperComparisonRow]
    narrative_summary: str


class SavedComparisonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_ids: list[int]
    result: dict
    created_at: datetime

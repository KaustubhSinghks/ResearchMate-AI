from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    document_id: int | None = None  # None = search across the whole corpus


class CitedChunk(BaseModel):
    document_id: int
    document_title: str
    section: str | None
    page: int | None
    text: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitedChunk]

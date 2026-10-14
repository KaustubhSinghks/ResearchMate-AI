from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.note import NoteType


class NoteCreate(BaseModel):
    document_id: int
    type: NoteType = NoteType.NOTE
    content: str
    section_ref: str | None = None


class NoteUpdate(BaseModel):
    content: str | None = None
    is_done: bool | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    type: NoteType
    content: str
    section_ref: str | None
    is_done: bool
    created_at: datetime

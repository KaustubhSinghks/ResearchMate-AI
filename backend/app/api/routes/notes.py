from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(tags=["notes"])


@router.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    document = db.get(Document, payload.document_id)
    if document is None or document.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    note = Note(
        owner_id=current_user.id,
        document_id=payload.document_id,
        type=payload.type,
        content=payload.content,
        section_ref=payload.section_ref,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/documents/{document_id}/notes", response_model=list[NoteOut])
def list_notes(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Note]:
    return (
        db.query(Note)
        .filter(Note.document_id == document_id, Note.owner_id == current_user.id)
        .order_by(Note.created_at.desc())
        .all()
    )


@router.get("/notes", response_model=list[NoteOut])
def list_all_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Note]:
    return db.query(Note).filter(Note.owner_id == current_user.id).order_by(Note.created_at.desc()).all()


@router.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    note = db.get(Note, note_id)
    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if payload.content is not None:
        note.content = payload.content
    if payload.is_done is not None:
        note.is_done = payload.is_done

    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    note = db.get(Note, note_id)
    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(note)
    db.commit()

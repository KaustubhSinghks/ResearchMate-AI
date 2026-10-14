import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.ingestion_pipeline import run_ingestion
from app.models.document import Document, DocumentStatus
from app.models.folder import DocumentTag, Folder, Tag
from app.models.user import User
from app.schemas.document import (
    DocumentDetail,
    DocumentListItem,
    DocumentUpdate,
    FolderCreate,
    FolderOut,
    TagCreate,
    TagOut,
)

router = APIRouter(tags=["documents"])
settings = get_settings()


@router.post("/documents/upload", response_model=DocumentListItem, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    folder_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported")

    os.makedirs(settings.upload_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.pdf"
    stored_path = os.path.join(settings.upload_dir, stored_name)

    contents = await file.read()
    with open(stored_path, "wb") as f:
        f.write(contents)

    document = Document(
        owner_id=current_user.id,
        folder_id=folder_id,
        title=file.filename,
        original_filename=file.filename,
        file_path=stored_path,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(run_ingestion, document.id)

    return document


@router.get("/documents", response_model=list[DocumentListItem])
def list_documents(
    folder_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    if folder_id is not None:
        query = query.filter(Document.folder_id == folder_id)
    return query.order_by(Document.created_at.desc()).all()


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.patch("/documents/{document_id}", response_model=DocumentDetail)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    document = db.get(Document, document_id)
    if document is None or document.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if payload.title is not None:
        document.title = payload.title
    if payload.folder_id is not None:
        document.folder_id = payload.folder_id

    if payload.tag_names is not None:
        db.query(DocumentTag).filter(DocumentTag.document_id == document.id).delete()
        for name in payload.tag_names:
            tag = db.query(Tag).filter(Tag.owner_id == current_user.id, Tag.name == name).first()
            if tag is None:
                tag = Tag(owner_id=current_user.id, name=name)
                db.add(tag)
                db.flush()
            db.add(DocumentTag(document_id=document.id, tag_id=tag.id))

    db.commit()
    db.refresh(document)
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    document = db.get(Document, document_id)
    if document is None or document.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()


@router.post("/folders", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
def create_folder(
    payload: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Folder:
    folder = Folder(owner_id=current_user.id, name=payload.name, parent_id=payload.parent_id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.get("/folders", response_model=list[FolderOut])
def list_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Folder]:
    return db.query(Folder).filter(Folder.owner_id == current_user.id).all()


@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Tag:
    existing = db.query(Tag).filter(Tag.owner_id == current_user.id, Tag.name == payload.name).first()
    if existing:
        return existing
    tag = Tag(owner_id=current_user.id, name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("/tags", response_model=list[TagOut])
def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Tag]:
    return db.query(Tag).filter(Tag.owner_id == current_user.id).all()

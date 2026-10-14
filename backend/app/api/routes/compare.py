from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.comparison import SavedComparison
from app.models.document import Document
from app.models.user import User
from app.schemas.compare import CompareRequest, CompareResult, SavedComparisonOut
from app.services.comparison import compare_documents

router = APIRouter(tags=["compare"])


@router.post("/compare", response_model=CompareResult)
def compare(
    payload: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompareResult:
    if len(payload.document_ids) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select at least 2 documents to compare")

    documents = (
        db.query(Document)
        .filter(Document.id.in_(payload.document_ids), Document.owner_id == current_user.id)
        .all()
    )
    if len(documents) != len(payload.document_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more documents not found")

    result = compare_documents(documents)

    db.add(SavedComparison(owner_id=current_user.id, document_ids=payload.document_ids, result=result))
    db.commit()

    return CompareResult(**result)


@router.get("/compare/history", response_model=list[SavedComparisonOut])
def compare_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedComparison]:
    return (
        db.query(SavedComparison)
        .filter(SavedComparison.owner_id == current_user.id)
        .order_by(SavedComparison.created_at.desc())
        .all()
    )

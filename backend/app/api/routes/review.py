from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.literature_review import ReviewOutline
from app.models.user import User
from app.schemas.review import ReviewRequest, ReviewResult
from app.services.review_support import group_by_theme, suggest_gaps_and_outline, trends_over_time

router = APIRouter(tags=["review"])


@router.post("/review", response_model=ReviewResult, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewOutline:
    documents = (
        db.query(Document)
        .filter(Document.id.in_(payload.document_ids), Document.owner_id == current_user.id)
        .all()
    )
    if not documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching documents found")

    themes = group_by_theme(db, documents)
    trends = trends_over_time(documents)
    llm_result = suggest_gaps_and_outline(documents)

    review = ReviewOutline(
        owner_id=current_user.id,
        title=payload.title,
        document_ids=payload.document_ids,
        themes=themes,
        trends=trends,
        gaps=llm_result.get("gaps") or [],
        outline=llm_result.get("outline") or {},
        suggested_reading=llm_result.get("suggested_reading") or [],
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/review", response_model=list[ReviewResult])
def list_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReviewOutline]:
    return (
        db.query(ReviewOutline)
        .filter(ReviewOutline.owner_id == current_user.id)
        .order_by(ReviewOutline.created_at.desc())
        .all()
    )


@router.get("/review/{review_id}", response_model=ReviewResult)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewOutline:
    review = db.get(ReviewOutline, review_id)
    if review is None or review.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.graph import GraphResponse
from app.services.knowledge_graph import build_knowledge_graph

router = APIRouter(tags=["graph"])


@router.get("/graph", response_model=GraphResponse)
def get_knowledge_graph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GraphResponse:
    return build_knowledge_graph(db, owner_id=current_user.id)

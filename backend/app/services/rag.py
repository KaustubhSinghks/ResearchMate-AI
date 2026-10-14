from sqlalchemy.orm import Session

from app.schemas.chat import ChatResponse, CitedChunk
from app.services.llm import generate_text
from app.services.semantic_search import semantic_search_chunks

SYSTEM_PROMPT = (
    "You are a research assistant answering questions about uploaded papers. "
    "Answer ONLY using the numbered excerpts provided below. If the excerpts do not contain "
    "the answer, say you don't have enough information from the uploaded papers rather than "
    "guessing. Cite excerpts inline using their number in square brackets, e.g. [1]."
)


def answer_question(db: Session, question: str, owner_id: int, document_id: int | None = None) -> ChatResponse:
    matches = semantic_search_chunks(db, question, owner_id=owner_id, document_id=document_id, limit=6)

    if not matches:
        return ChatResponse(
            answer="I don't have enough information from your uploaded papers to answer that.",
            citations=[],
        )

    excerpts = []
    citations: list[CitedChunk] = []
    for i, match in enumerate(matches, start=1):
        location = f"{match.document.title}"
        if match.chunk.section:
            location += f", section '{match.chunk.section}'"
        if match.chunk.page:
            location += f", page {match.chunk.page}"
        excerpts.append(f"[{i}] ({location}):\n{match.chunk.text}")
        citations.append(
            CitedChunk(
                document_id=match.document.id,
                document_title=match.document.title,
                section=match.chunk.section,
                page=match.chunk.page,
                text=match.chunk.text,
            )
        )

    context = "\n\n".join(excerpts)
    user_prompt = f"Question: {question}\n\nExcerpts:\n{context}"

    answer = generate_text(system=SYSTEM_PROMPT, user=user_prompt)
    return ChatResponse(answer=answer, citations=citations)

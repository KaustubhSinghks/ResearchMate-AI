from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, citations, compare, documents, graph, notes, related, review, search
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="AI-Powered Personal Research Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(related.router)
app.include_router(compare.router)
app.include_router(notes.router)
app.include_router(citations.router)
app.include_router(graph.router)
app.include_router(review.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

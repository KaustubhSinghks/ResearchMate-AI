import voyageai

from app.core.config import get_settings

_client: voyageai.Client | None = None


def _get_client() -> voyageai.Client:
    global _client
    if _client is None:
        _client = voyageai.Client(api_key=get_settings().voyage_api_key)
    return _client


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed chunk/document text for storage and retrieval."""
    if not texts:
        return []
    settings = get_settings()
    result = _get_client().embed(texts, model=settings.voyage_embedding_model, input_type="document")
    return result.embeddings


def embed_query(text: str) -> list[float]:
    """Embed a user query for similarity search against stored chunk embeddings."""
    settings = get_settings()
    result = _get_client().embed([text], model=settings.voyage_embedding_model, input_type="query")
    return result.embeddings[0]

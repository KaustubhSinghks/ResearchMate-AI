from typing import Any

import httpx

from app.core.config import get_settings

_GRAPH_BASE = "https://api.semanticscholar.org/graph/v1"
_RECS_BASE = "https://api.semanticscholar.org/recommendations/v1"

_PAPER_FIELDS = "paperId,title,abstract,year,authors,url,externalIds"


def _headers() -> dict[str, str]:
    api_key = get_settings().semantic_scholar_api_key
    return {"x-api-key": api_key} if api_key else {}


def _paper_from_json(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": data.get("paperId"),
        "title": data.get("title"),
        "authors": [a.get("name") for a in (data.get("authors") or []) if a.get("name")],
        "year": data.get("year"),
        "url": data.get("url"),
    }


def find_paper_id_by_title(title: str) -> str | None:
    """Best-effort match of an in-corpus paper to its Semantic Scholar paperId."""
    try:
        resp = httpx.get(
            f"{_GRAPH_BASE}/paper/search",
            params={"query": title, "limit": 1, "fields": _PAPER_FIELDS},
            headers=_headers(),
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json().get("data") or []
        return data[0]["paperId"] if data else None
    except httpx.HTTPError:
        return None


def get_references(paper_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Papers this paper cites."""
    try:
        resp = httpx.get(
            f"{_GRAPH_BASE}/paper/{paper_id}/references",
            params={"fields": _PAPER_FIELDS, "limit": limit},
            headers=_headers(),
            timeout=10.0,
        )
        resp.raise_for_status()
        return [_paper_from_json(item["citedPaper"]) for item in resp.json().get("data", []) if item.get("citedPaper")]
    except httpx.HTTPError:
        return []


def get_citations(paper_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Papers that cite this paper."""
    try:
        resp = httpx.get(
            f"{_GRAPH_BASE}/paper/{paper_id}/citations",
            params={"fields": _PAPER_FIELDS, "limit": limit},
            headers=_headers(),
            timeout=10.0,
        )
        resp.raise_for_status()
        return [
            _paper_from_json(item["citingPaper"]) for item in resp.json().get("data", []) if item.get("citingPaper")
        ]
    except httpx.HTTPError:
        return []


def get_recommendations(paper_id: str, limit: int = 10) -> list[dict[str, Any]]:
    try:
        resp = httpx.get(
            f"{_RECS_BASE}/papers/forpaper/{paper_id}",
            params={"fields": _PAPER_FIELDS, "limit": limit},
            headers=_headers(),
            timeout=10.0,
        )
        resp.raise_for_status()
        return [_paper_from_json(item) for item in resp.json().get("recommendedPapers", [])]
    except httpx.HTTPError:
        return []

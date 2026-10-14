from dataclasses import dataclass

import tiktoken

from app.services.pdf_extraction import ExtractedPDF

_ENCODING = tiktoken.get_encoding("cl100k_base")

DEFAULT_MAX_TOKENS = 500
DEFAULT_OVERLAP_TOKENS = 50


@dataclass
class DocumentChunk:
    section: str | None
    page: int | None
    chunk_index: int
    text: str


def _split_text_into_token_windows(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    tokens = _ENCODING.encode(text)
    if not tokens:
        return []

    windows: list[str] = []
    start = 0
    step = max(max_tokens - overlap_tokens, 1)

    while start < len(tokens):
        window_tokens = tokens[start : start + max_tokens]
        windows.append(_ENCODING.decode(window_tokens))
        if start + max_tokens >= len(tokens):
            break
        start += step

    return windows


def chunk_document(
    extracted: ExtractedPDF,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    index = 0

    sections = extracted.sections or [
        # Fallback when no section headers were detected: chunk the raw pages.
    ]

    if sections:
        for section in sections:
            for window in _split_text_into_token_windows(section.text, max_tokens, overlap_tokens):
                if not window.strip():
                    continue
                chunks.append(
                    DocumentChunk(section=section.name, page=section.start_page, chunk_index=index, text=window)
                )
                index += 1
    else:
        for page_number, page_text in enumerate(extracted.pages, start=1):
            for window in _split_text_into_token_windows(page_text, max_tokens, overlap_tokens):
                if not window.strip():
                    continue
                chunks.append(DocumentChunk(section=None, page=page_number, chunk_index=index, text=window))
                index += 1

    return chunks

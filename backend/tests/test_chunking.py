from app.services.chunking import chunk_document
from app.services.pdf_extraction import ExtractedPDF, ExtractedSection


def test_chunk_document_splits_long_sections_with_overlap():
    long_text = " ".join(f"word{i}" for i in range(2000))  # far more than max_tokens
    extracted = ExtractedPDF(
        full_text=long_text,
        pages=[long_text],
        sections=[ExtractedSection(name="methodology", start_page=1, text=long_text)],
    )

    chunks = chunk_document(extracted, max_tokens=100, overlap_tokens=20)

    assert len(chunks) > 1
    assert all(c.section == "methodology" for c in chunks)
    assert all(c.page == 1 for c in chunks)
    # chunk_index should be sequential starting at 0
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_chunk_document_falls_back_to_pages_when_no_sections():
    extracted = ExtractedPDF(full_text="hello world", pages=["hello world"], sections=[])

    chunks = chunk_document(extracted, max_tokens=100, overlap_tokens=10)

    assert len(chunks) == 1
    assert chunks[0].section is None
    assert chunks[0].page == 1
    assert "hello world" in chunks[0].text

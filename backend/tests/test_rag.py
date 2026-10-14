from types import SimpleNamespace

from app.services import rag
from app.services.semantic_search import ChunkMatch


def _fake_match(doc_id: int, title: str, text: str, section: str, page: int) -> ChunkMatch:
    document = SimpleNamespace(id=doc_id, title=title)
    chunk = SimpleNamespace(section=section, page=page, text=text)
    return ChunkMatch(document=document, chunk=chunk, score=0.9)


def test_answer_question_returns_placeholder_when_no_matches(mocker):
    mocker.patch("app.services.rag.semantic_search_chunks", return_value=[])
    generate_text_mock = mocker.patch("app.services.rag.generate_text")

    response = rag.answer_question(db=object(), question="What is this about?", owner_id=1)

    assert "don't have enough information" in response.answer
    assert response.citations == []
    generate_text_mock.assert_not_called()


def test_answer_question_builds_context_and_citations(mocker):
    matches = [_fake_match(1, "Paper A", "Some relevant excerpt.", "results", 4)]
    mocker.patch("app.services.rag.semantic_search_chunks", return_value=matches)
    mocker.patch("app.services.rag.generate_text", return_value="The answer is X [1].")

    response = rag.answer_question(db=object(), question="What are the results?", owner_id=1, document_id=1)

    assert response.answer == "The answer is X [1]."
    assert len(response.citations) == 1
    citation = response.citations[0]
    assert citation.document_id == 1
    assert citation.document_title == "Paper A"
    assert citation.section == "results"
    assert citation.page == 4

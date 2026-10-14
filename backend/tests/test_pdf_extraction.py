import fitz

from app.services.pdf_extraction import extract_pdf


def _make_sample_pdf(path: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "A Great Paper Title\n"
        "Jane Doe, John Smith\n\n"
        "Abstract\n"
        "This paper studies an interesting problem and proposes a solution.\n\n"
        "Introduction\n"
        "Prior work has not addressed this problem well.\n\n"
        "Methodology\n"
        "We propose a new method based on X.\n\n"
        "Conclusion\n"
        "Our method works well in practice.\n"
    )
    page.insert_text((50, 72), text, fontsize=11)
    doc.save(path)
    doc.close()


def test_extract_pdf_detects_sections_and_pages(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _make_sample_pdf(str(pdf_path))

    extracted = extract_pdf(str(pdf_path))

    assert extracted.page_count == 1
    assert len(extracted.pages) == 1
    assert "Abstract" not in "".join(s.name for s in extracted.sections)  # names are lowercased

    section_names = [s.name for s in extracted.sections]
    assert "abstract" in section_names
    assert "introduction" in section_names
    assert "method" in section_names  # "methodology" normalizes to the "method" bucket
    assert "conclusion" in section_names

    abstract_section = next(s for s in extracted.sections if s.name == "abstract")
    assert "interesting problem" in abstract_section.text

    assert extracted.title_guess is not None

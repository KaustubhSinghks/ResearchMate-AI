import re
from dataclasses import dataclass, field

import fitz  # PyMuPDF

# Section headers commonly found in academic papers, checked against short standalone lines.
KNOWN_SECTIONS = [
    "abstract",
    "introduction",
    "background",
    "related work",
    "motivation",
    "problem statement",
    "method",
    "methods",
    "methodology",
    "approach",
    "system design",
    "implementation",
    "experiments",
    "experimental setup",
    "evaluation",
    "results",
    "discussion",
    "limitations",
    "conclusion",
    "conclusions",
    "future work",
    "acknowledgments",
    "acknowledgements",
    "references",
    "appendix",
]

_SECTION_LINE_RE = re.compile(
    r"^\s*(?:[0-9]+[.\)]?\s*|[IVXLC]+[.\)]\s*)?([A-Za-z][A-Za-z \-]{2,60})\s*$"
)


@dataclass
class ExtractedSection:
    name: str
    start_page: int
    text: str = ""


@dataclass
class ExtractedPDF:
    full_text: str
    pages: list[str]
    sections: list[ExtractedSection] = field(default_factory=list)
    page_count: int = 0
    title_guess: str | None = None


def _looks_like_section_header(line: str) -> str | None:
    match = _SECTION_LINE_RE.match(line.strip())
    if not match:
        return None
    candidate = match.group(1).strip().lower()
    for known in KNOWN_SECTIONS:
        if candidate == known or candidate.startswith(known):
            return known
    return None


def _guess_title(first_page_text: str) -> str | None:
    for line in first_page_text.splitlines():
        stripped = line.strip()
        if len(stripped) > 10 and not stripped.lower().startswith("abstract"):
            return stripped
    return None


def extract_pdf(file_path: str) -> ExtractedPDF:
    doc = fitz.open(file_path)
    pages: list[str] = []
    sections: list[ExtractedSection] = []
    current_section: ExtractedSection | None = None

    for page_index, page in enumerate(doc):
        page_text = page.get_text()
        pages.append(page_text)

        for line in page_text.splitlines():
            header = _looks_like_section_header(line)
            if header:
                if current_section is not None:
                    sections.append(current_section)
                current_section = ExtractedSection(name=header, start_page=page_index + 1)
                continue
            if current_section is not None:
                current_section.text += line + "\n"
            elif line.strip():
                # Text before the first detected header (title/authors/abstract lead-in).
                if not sections and current_section is None:
                    current_section = ExtractedSection(name="preamble", start_page=page_index + 1)
                    current_section.text += line + "\n"

    if current_section is not None:
        sections.append(current_section)

    page_count = doc.page_count
    doc.close()

    full_text = "\n".join(pages)
    title_guess = _guess_title(pages[0]) if pages else None

    return ExtractedPDF(
        full_text=full_text,
        pages=pages,
        sections=sections,
        page_count=page_count,
        title_guess=title_guess,
    )

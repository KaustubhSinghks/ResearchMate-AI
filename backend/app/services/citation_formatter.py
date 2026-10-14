import re


def _apa_author(name: str) -> str:
    parts = name.strip().split()
    if len(parts) < 2:
        return name
    last = parts[-1]
    initials = " ".join(f"{p[0]}." for p in parts[:-1])
    return f"{last}, {initials}"


def _ieee_author(name: str) -> str:
    parts = name.strip().split()
    if len(parts) < 2:
        return name
    last = parts[-1]
    initials = " ".join(f"{p[0]}." for p in parts[:-1])
    return f"{initials} {last}"


def _bibtex_key(authors: list[str], year: int | None, title: str) -> str:
    first_author_last = authors[0].split()[-1] if authors else "unknown"
    first_word = re.sub(r"[^A-Za-z0-9]", "", title.split()[0]) if title else "paper"
    return f"{first_author_last}{year or ''}{first_word}"


def format_apa(title: str, authors: list[str], year: int | None, venue: str | None) -> str:
    author_str = ", ".join(_apa_author(a) for a in authors) or "Unknown author"
    year_str = f"({year})" if year else "(n.d.)"
    venue_str = f" {venue}." if venue else ""
    return f"{author_str} {year_str}. {title}.{venue_str}"


def format_ieee(title: str, authors: list[str], year: int | None, venue: str | None) -> str:
    author_str = ", ".join(_ieee_author(a) for a in authors) or "Unknown author"
    venue_str = f", {venue}" if venue else ""
    year_str = f", {year}" if year else ""
    return f'{author_str}, "{title},"{venue_str}{year_str}.'


def format_acm(title: str, authors: list[str], year: int | None, venue: str | None) -> str:
    author_str = ", ".join(_apa_author(a) for a in authors) or "Unknown author"
    year_str = f"{year}." if year else "n.d."
    venue_str = f" {venue}." if venue else ""
    return f"{author_str} {year_str} {title}.{venue_str}"


def format_bibtex(title: str, authors: list[str], year: int | None, venue: str | None) -> str:
    key = _bibtex_key(authors, year, title)
    author_field = " and ".join(authors) or "Unknown author"
    lines = [
        f"@article{{{key},",
        f"  author = {{{author_field}}},",
        f"  title = {{{title}}},",
    ]
    if year:
        lines.append(f"  year = {{{year}}},")
    if venue:
        lines.append(f"  journal = {{{venue}}},")
    lines.append("}")
    return "\n".join(lines)


def format_ris(title: str, authors: list[str], year: int | None, venue: str | None) -> str:
    lines = ["TY  - JOUR"]
    for author in authors:
        lines.append(f"AU  - {author}")
    lines.append(f"TI  - {title}")
    if year:
        lines.append(f"PY  - {year}")
    if venue:
        lines.append(f"JO  - {venue}")
    lines.append("ER  - ")
    return "\n".join(lines)


def format_all(title: str, authors: list[str], year: int | None, venue: str | None) -> dict[str, str]:
    return {
        "apa": format_apa(title, authors, year, venue),
        "ieee": format_ieee(title, authors, year, venue),
        "acm": format_acm(title, authors, year, venue),
        "bibtex": format_bibtex(title, authors, year, venue),
        "ris": format_ris(title, authors, year, venue),
    }

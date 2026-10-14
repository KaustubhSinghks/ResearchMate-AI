from app.services.citation_formatter import format_all, format_apa, format_bibtex, format_ieee, format_ris


def test_format_apa_orders_last_name_first():
    apa = format_apa("Attention Is All You Need", ["Ashish Vaswani", "Noam Shazeer"], 2017, "NeurIPS")
    assert apa.startswith("Vaswani, A., Shazeer, N.")
    assert "(2017)" in apa
    assert "Attention Is All You Need" in apa
    assert "NeurIPS" in apa


def test_format_ieee_puts_initials_first():
    ieee = format_ieee("Attention Is All You Need", ["Ashish Vaswani"], 2017, "NeurIPS")
    assert ieee.startswith("A. Vaswani")
    assert '"Attention Is All You Need,"' in ieee


def test_format_bibtex_has_required_fields():
    bibtex = format_bibtex("Attention Is All You Need", ["Ashish Vaswani"], 2017, "NeurIPS")
    assert bibtex.startswith("@article{Vaswani2017Attention,")
    assert "author = {Ashish Vaswani}" in bibtex
    assert "title = {Attention Is All You Need}" in bibtex
    assert "year = {2017}" in bibtex


def test_format_ris_has_required_tags():
    ris = format_ris("Attention Is All You Need", ["Ashish Vaswani"], 2017, "NeurIPS")
    lines = ris.splitlines()
    assert lines[0] == "TY  - JOUR"
    assert "AU  - Ashish Vaswani" in lines
    assert "TI  - Attention Is All You Need" in lines
    assert lines[-1] == "ER  - "


def test_format_all_returns_every_style():
    result = format_all("Title", ["A B"], 2020, "Venue")
    assert set(result.keys()) == {"apa", "ieee", "acm", "bibtex", "ris"}

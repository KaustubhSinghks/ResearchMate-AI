from pydantic import BaseModel


class CitationFormatResponse(BaseModel):
    apa: str
    ieee: str
    acm: str
    bibtex: str
    ris: str

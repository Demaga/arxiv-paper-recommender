from pydantic import BaseModel


class ArxivPaper(BaseModel):
    arxiv_id: str
    doi: str | None
    title: str
    abstract: str
    other: dict = {}
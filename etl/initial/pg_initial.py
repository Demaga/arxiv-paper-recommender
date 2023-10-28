import json
import logging
import os
import psycopg2

from backend.db.schemas import ArxivPaper
from sqlalchemy import JSON, Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert

# log to file
logging.basicConfig(filename="pg_initial.log", level=logging.DEBUG)

Base = declarative_base()


class PaperStage(Base):
    __tablename__ = "papers_stage"

    id = Column(Integer, primary_key=True)
    arxiv_id = Column(String, nullable=True, unique=True)
    doi = Column(String, nullable=True, unique=True)
    title = Column(String)
    abstract = Column(String, nullable=True)
    other = Column(JSON, nullable=True)


if __name__ == "__main__":
    engine = create_engine(
        f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}"
    )
    s = sessionmaker(bind=engine)
    with s() as session:
        Base.metadata.create_all(engine)
        with open("arxiv-metadata-oai-snapshot.json", "r") as f:
            for i, line in enumerate(f):
                paper = json.loads(line)
                logging.info(f"Processing paper {paper}")
                paper = ArxivPaper(
                    arxiv_id=paper.pop("id"),
                    doi=paper.pop("doi"),
                    title=paper.pop("title"),
                    abstract=paper.pop("abstract"),
                    other=paper,
                )
                try:
                    session.execute(
                        insert(PaperStage).values(dict(paper)).on_conflict_do_nothing()
                    )
                except psycopg2.errors.UniqueViolation:
                    logging.info(
                        f"Skipping paper {paper.arxiv_id} because it already exists"
                    )
                if i % 1000 == 0 and i >= 1000:
                    session.commit()
                    logging.info(f"Inserted {i} papers")

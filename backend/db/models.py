import sqlalchemy

from db.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    arxiv_id = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    doi = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    abstract = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    other = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)

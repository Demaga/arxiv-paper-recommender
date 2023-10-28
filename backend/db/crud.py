import sqlalchemy

from db import models, schemas
from db.database import Base


def get_papers(db, offset: int = 0, limit: int = 10):
    return db.query(models.Paper).offset(offset).limit(limit).all()

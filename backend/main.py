from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import schemas
from db.crud import get_papers
from db.database import Base, get_db
from elasticsearch_service import service as elasticsearch_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/doc_count")
async def doc_count():
    return elasticsearch_service.doc_count()


@app.get("/search")
async def search(query: str, offset: int = 0):
    return elasticsearch_service.search(query, offset=offset)


@app.get("/papers", response_model=list[schemas.Paper])
async def papers(db: Session = Depends(get_db)):
    # get last 10 papers from postgres
    return get_papers(db)


@app.get("/")
async def root():
    return {"message": "Hello World"}

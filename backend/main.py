from fastapi import FastAPI

from meilisearch_service import service as meilisearch_service

app = FastAPI()

@app.get("/doc_count")
async def doc_count():
    return meilisearch_service.doc_count()

@app.get("/search")
async def search(query: str, offset: int = 0):
    return meilisearch_service.search(query, offset=offset)

@app.get("/")
async def root():
    return {"message": "Hello World"}

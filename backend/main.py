from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {"message": "Hello World"}

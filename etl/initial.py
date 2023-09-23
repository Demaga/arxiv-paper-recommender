import os
from elasticsearch import Elasticsearch, helpers
import json


def jsonl_generator():
    with open("arxiv-metadata-oai-snapshot.json", "r") as f:
        for line in f:
            doc = json.loads(line)
            action = {
                "_index": "arxiv",
                "_id": doc["id"],
                "_source": doc,
            }
            yield action


if __name__ == "__main__":
    es = Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])

    # create 'arxiv' index if not exists
    if not es.indices.exists(index="arxiv"):
        es.indices.create(index="arxiv")

    i = 0
    for success, info in helpers.parallel_bulk(es, jsonl_generator()):
        i += 1
        if i % 10000 == 0:
            print(f"Inserted {i} documents")
        if not success:
            print("A document failed:", info)

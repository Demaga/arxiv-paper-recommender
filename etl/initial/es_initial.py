import json
import os
from datetime import datetime

from elasticsearch import Elasticsearch, helpers


def jsonl_generator():
    with open("arxiv-metadata-oai-snapshot.json", "r") as f:
        for line in f:
            doc = json.loads(line)
            doc["abstract"] = doc["abstract"].replace("\n", " ").strip()
            action = {
                "_index": f"arxiv",
                "_id": doc["id"],
                "_source": {
                    key: doc[key]
                    for key in ["id", "title", "abstract", "authors", "update_date"]
                },
            }
            yield action


if __name__ == "__main__":
    es = Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])

    i = 0
    for success, info in helpers.parallel_bulk(es, jsonl_generator()):
        i += 1
        if i % 10000 == 0:
            print(f"Inserted {i} documents")
        if not success:
            print("A document failed:", info)

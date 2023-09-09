import json
import os

import meilisearch

import logging

CHUNK_SIZE = 20_000

if __name__ == "__main__":
    # configure log to file
    logging.basicConfig(
        filename="import-meili.log",
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    client = meilisearch.Client(
        os.environ["meilisearch_server"], os.environ["meilisearch_master_key"]
    )

    # create index if not exist
    index = client.index("papers")
    if index is None:
        client.create_index("papers")

    with open("arxiv-metadata-oai-snapshot.json", "r") as f:

        def extract_text_fields(line):
            data = json.loads(line)
            out = {
                "id": data["id"].replace(".", "-"),
                "authors": data["authors"],
                "title": data["title"],
                "abstract": data["abstract"],
            }
            return out
        
        k = 0
        file_read_over = False
        while not file_read_over:
            chunk = []
            for _ in range(CHUNK_SIZE):
                try:
                    chunk.append(extract_text_fields(next(f)))
                except StopIteration:
                    file_read_over = True
                    break
            if len(chunk) > 0:
                client.index("papers").add_documents(chunk)
                logging.info(f"Chunk {k} added")
                k += 1

import os

import meilisearch


class MeilisearchService:
    client = None

    def __init__(self, server, master_key):
        self.client = meilisearch.Client(server, master_key)

    def search(self, query, offset=0, limit=20):
        return self.client.index("papers").search(
            query, {"offset": offset, "limit": limit}
        )

    def doc_count(self):
        stats = dict(self.client.index("papers").get_stats())
        return stats["number_of_documents"]


service = MeilisearchService(
    os.environ["meilisearch_server"], os.environ["meilisearch_master_key"]
)

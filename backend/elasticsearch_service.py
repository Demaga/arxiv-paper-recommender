import os

import elasticsearch


class ElasticsearchService:
    client = None

    def __init__(self, host):
        self.client = elasticsearch.Elasticsearch(hosts=[host])

    def search(self, query, offset=0, limit=20):
        return self.client.search(
            index="arxiv", query={"multi_match": {"query": query, "fields": ["title", "authors", "abstract"]}}, from_=offset, size=limit
        )

    def doc_count(self):
        stats = self.client.indices.stats(index="arxiv")
        return stats["_all"]["primaries"]["docs"]["count"]


service = ElasticsearchService(
    os.environ.get("ELASTICSEARCH_HOST", "http://localhost:9200")
)

import os
import meilisearch


if __name__ == "__main__":
    client = meilisearch.Client(
        os.environ["meilisearch_server"], os.environ["meilisearch_master_key"]
    )

    found = client.index("papers").search("")
    print(found)

    stats = dict(client.index("papers").get_stats())
    print(stats)
    count = stats["number_of_documents"]
    print(count)
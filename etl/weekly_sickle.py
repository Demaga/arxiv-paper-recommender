import os
import time
from elasticsearch import Elasticsearch

from sickle import Sickle

def get_last_record_date() -> str:
    es = Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])
    res = es.search(
        index="arxiv",
        query={"match_all": {}},
        size=1,
        sort=[{"update_date": "desc"}],
    )
    return res["hits"]["hits"][0]["_source"]["update_date"]


def get_sickle_records(start_date: str) -> Sickle.ListRecords:
    s = Sickle("http://export.arxiv.org/oai2")
    records = s.ListRecords(
        metadataPrefix="oai_dc", ignore_deleted=True, **{"from": start_date}
    )
    return records


def transform_records(records: Sickle.ListRecords) -> list[dict]:
    out_records = []

    BATCH_SIZE = 20
    for i, record in enumerate(records):
        record = dict(record)
        identifier = record["identifier"][0].split("/")[-1].replace(".", "-")
        authors = record["creator"]
        for j, author in enumerate(authors):
            author = author.split(",")
            author = " ".join(author[1:]) + " " + author[0]
            author = author.strip()
            authors[j] = author
        authors = ", ".join(authors)
        out = {
            "id": identifier,
            "authors": authors,
            "title": record["title"][0],
            "abstract": record["description"][0].strip().replace("\n", " ")
        }
        out_records.append(out)

        if i >= BATCH_SIZE and i % BATCH_SIZE == 0:
            print(f"Batch {i // BATCH_SIZE} done")
            time.sleep(5) # lazy load, don't overload the server
        if i == 200:
            break

    return out_records

def main():
    date = get_last_record_date()
    print(date)

    records = get_sickle_records(date)
    print(records)

    transformed_records = transform_records(records)
    print(transformed_records)




if __name__ == "__main__":
    main()


# BATCH_SIZE = 20
# for i, record in enumerate(records):
#     record = dict(record)
#     identifier = record["identifier"][0].split("/")[-1].replace(".", "-")
#     authors = record["creator"]
#     for i, author in enumerate(authors):
#         author = author.split(",")
#         author = " ".join(author[1:]) + " " + author[0]
#         author = author.strip()
#         authors[i] = author
#     authors = ", ".join(authors)
#     out = {
#         "id": identifier,
#         "authors": authors,
#         "title": record["title"][0],
#         "abstract": record["description"][0].strip().replace("\n", " ")
#     }
#     print(out)

#     if i >= BATCH_SIZE and i % BATCH_SIZE == 0:
#         print(f"Batch {i // BATCH_SIZE} done")
#         time.sleep(10)
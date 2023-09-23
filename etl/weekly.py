import os
import time

import requests
from elasticsearch import Elasticsearch
from lxml import etree


def get_last_record_date() -> str:
    es = Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])
    res = es.search(
        index="arxiv",
        query={"match_all": {}},
        size=1,
        sort=[{"update_date": "desc"}],
    )
    return res["hits"]["hits"][0]["_source"]["update_date"]


def get_records(start_date: str) -> list[etree._Element]:
    records = []
    url = "http://export.arxiv.org/oai2"
    with requests.session as s:
        while True:
            s = requests.get(url, params={"verb": "ListRecords", "metadataPrefix": "oai_dc", "from": start_date})
            if s.status_code != 200:
                raise Exception(f"Request failed with status code {s.status_code}")
            tree = etree.fromstring(s.content)
            records_batch = tree.find(".//ListRecords", namespaces={None: "http://www.openarchives.org/OAI/2.0/"})
            records.extend(records_batch)
            resumption_token = tree.find(".//resumptionToken", namespaces={None: "http://www.openarchives.org/OAI/2.0/"})
            if resumption_token is None:
                break
            

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

    records = get_records(date)
    print(records)

    transformed_records = transform_records(records)
    print(transformed_records)




if __name__ == "__main__":
    main()

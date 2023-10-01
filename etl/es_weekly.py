import logging
import os
import time
from typing import Generator

import requests
import xmltodict
from elasticsearch import Elasticsearch, helpers
from lxml import etree

logging.basicConfig(level=logging.INFO, filename="weekly.log")


def get_last_record_date() -> str:
    es = Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])
    res = es.search(
        index="arxiv",
        query={"match_all": {}},
        size=1,
        sort=[{"update_date": "desc"}],
    )
    return res["hits"]["hits"][0]["_source"]["update_date"]


def get_records(start_date: str) -> Generator[etree._Element, None, None]:
    url = "http://export.arxiv.org/oai2"
    with requests.session() as s:
        resumption_token = None
        while True:
            if resumption_token is None:
                params = {
                    "verb": "ListRecords",
                    "metadataPrefix": "oai_dc",
                    "from": start_date,
                }
            else:
                params = {
                    "verb": "ListRecords",
                    "resumptionToken": resumption_token.text,
                }
            s = requests.get(
                url,
                params=params,
            )
            if s.status_code != 200:
                raise Exception(f"Request failed with status code {s.status_code}")
            tree = etree.fromstring(s.content)
            records_batch = tree.findall(
                ".//ListRecords/record",
                namespaces={None: "http://www.openarchives.org/OAI/2.0/"},
            )
            for record in records_batch:
                yield record
            resumption_token = tree.find(
                ".//resumptionToken",
                namespaces={None: "http://www.openarchives.org/OAI/2.0/"},
            )
            if resumption_token is None or resumption_token.text is None:
                break
            logging.info(f"Resumption token received: {resumption_token.text}")
            time.sleep(10)


def transform_record(record: etree.Element) -> dict:
    record = xmltodict.parse(etree.tostring(record))["record"]

    identifier = record["header"]["identifier"].split(":")[-1]
    metadata = record["metadata"]["oai_dc:dc"]
    authors = metadata["dc:creator"]
    if type(authors) == str:
        authors = [authors]
    for j, author in enumerate(authors):
        author = author.split(",")
        author = " ".join(author[1:]) + " " + author[0]
        author = author.strip()
        authors[j] = author
    authors = ", ".join(authors)
    out = {
        "id": identifier,
        "authors": authors,
        "title": metadata["dc:title"],
        "abstract": metadata["dc:description"][0].strip().replace("\n", " "),
        "update_date": record["header"]["datestamp"],
    }

    return out


def upload_records(records: list[dict]):
    es = Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])
    actions = [
        {
            "_index": f"arxiv",
            "_id": record["id"],
            "_source": record,
        }
        for record in records
    ]

    i = 0
    for success, info in helpers.parallel_bulk(es, actions):
        i += 1
        if i % 1000 == 0:
            logging.info(f"Inserted {i} documents")
        if not success:
            logging.info("A document failed:", info)


def main():
    date = get_last_record_date()
    logging.info(date)

    to_upload = []
    i = 0
    for record in get_records(start_date=date):
        i += 1
        if i % 1000 == 0:
            upload_records(to_upload)
            to_upload = []
            logging.info(f"Processed {i} records")

        transformed_record = transform_record(record)
        to_upload.append(transformed_record)
    if len(to_upload) > 0:
        upload_records(to_upload)


if __name__ == "__main__":
    main()

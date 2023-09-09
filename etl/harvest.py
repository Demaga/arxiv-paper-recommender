import time

from sickle import Sickle

s = Sickle("http://export.arxiv.org/oai2")

records = s.ListRecords(
    metadataPrefix="oai_dc", ignore_deleted=True, **{"from": "2023-09-06"}
)

BATCH_SIZE = 20
for i, record in enumerate(records):
    record = dict(record)
    identifier = record["identifier"][0].split("/")[-1].replace(".", "-")
    authors = record["creator"]
    for i, author in enumerate(authors):
        author = author.split(",")
        author = " ".join(author[1:]) + " " + author[0]
        author = author.strip()
        authors[i] = author
    authors = ", ".join(authors)
    out = {
        "id": identifier,
        "authors": authors,
        "title": record["title"][0],
        "abstract": record["description"][0].strip().replace("\n", " ")
    }
    print(out)

    if i >= BATCH_SIZE and i % BATCH_SIZE == 0:
        print(f"Batch {i // BATCH_SIZE} done")
        time.sleep(10)
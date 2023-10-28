### Initial
Import initial dataset (OAI archive dump of Arxiv papers) from Kaggle
1. Download dataset from https://www.kaggle.com/datasets/Cornell-University/arxiv?resource=download
2. Unpack 'arxiv-metadata-oai-snapshot.json' into this folder
3. Run `pg_initial.py` and `es_initial.py` scripts to load data into corresponding destinations.
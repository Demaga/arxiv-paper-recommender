
### Initial
Import initial dataset (OAI archive dump of Arxiv papers in JSONL format) from Kaggle
1. Download dataset from https://www.kaggle.com/datasets/Cornell-University/arxiv?resource=download
2. Unpack 'arxiv-metadata-oai-snapshot.json' into this folder
3. Run `python import.py`

### Weekly
Harvest weekly updates from OAI-PMH server (basically an XML feed with a cursor pagination).

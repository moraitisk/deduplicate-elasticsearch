# deduplicate-elasticsearch
A python script to detect duplicate documents in Elasticsearch. 

The script creates a file containing a delete action for each duplicate document that is detected, which looks like this:

- Single index is provided:
```
{"delete": {"_type": "doc", "_id": "1", "_index": "test_index"}}
{"delete": {"_type": "doc", "_id": "2", "_index": "test_index"}}
{"delete": {"_type": "doc", "_id": "3", "_index": "test_index"}}
```

- Index pattern or alias is provided (test_index_*): 
```
{"delete": {"_type": "doc", "_id": "1", "_index": "test_index_a"}}
{"delete": {"_type": "doc", "_id": "2", "_index": "test_index_b"}}
{"delete": {"_type": "doc", "_id": "3", "_index": "test_index_c"}}
```

Once all duplicates are found, you can use the [bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) to perform all of the delete operations in a **single API call** by either providing text file input to curl or attaching the file contents in the request body.

The `curl` command for the first option would be the following:
```
curl -s -H 'Content-Type: application/x-ndjson' -XPOST 'localhost:9200/_bulk' --data-binary "@bulk_deletions_file.txt"
```

## Usage

```
$ python deduplicate-elasticsearch/deduplicate-elaticsearch.py -h


usage: deduplicate-elaticsearch.py [-h] [-es ES_HOST] -i INDEX -k KEYS
                                   [KEYS ...]

optional arguments:
  -h, --help            show this help message and exit
  -es ES_HOST, --es_host ES_HOST
                        Elasticsearch host
  -i INDEX, --index INDEX
                        <Required> Index name or alias to search on
  -k KEYS [KEYS ...], --keys KEYS [KEYS ...]
                        <Required> List of fields that will determine
                        duplicate docs
```
---
For a full description on how this script works including an analysis of the memory requirements, see: https://alexmarquardt.com/2018/07/23/deduplicating-documents-in-elasticsearch/
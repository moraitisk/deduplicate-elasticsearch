#!/usr/local/bin/python3

# A description and analysis of this code can be found at 
# https://alexmarquardt.com/2018/07/23/deduplicating-documents-in-elasticsearch/

import sys
import argparse
import json
import hashlib
from elasticsearch import Elasticsearch, helpers

es_host = 'localhost:9200'

dict_of_duplicate_docs = {}

# The fields that will be used to determine if a document is a duplicate.
keys_to_include_in_hash = []

# The index name or alias in which duplicate documents will be searched.
index_to_search = ''

# Process documents returned by the current search/scroll.
def populate_dict_of_duplicate_docs(hit):
    combined_key = ''
    for mykey in keys_to_include_in_hash:
        combined_key += str(hit['_source'][mykey])

    hashval = hashlib.md5(combined_key.encode('utf-8')).digest()

    # If the hashval is new, then we will create a new key in the dict_of_duplicate_docs,
    # which will be assigned a value of an empty array.
    # We then immediately push a tuple of the doc _index and _id onto the array.
    dict_of_duplicate_docs.setdefault(hashval, []).append((hit['_index'], hit['_id']))

# Loop over all documents in the index, and populate the dict_of_duplicate_docs.
def scroll_over_all_docs():
    es = Elasticsearch([es_host], http_auth=None)
    for hit in helpers.scan(es, index=index_to_search):
        populate_dict_of_duplicate_docs(hit)

def loop_over_hashes_and_remove_duplicates():
    # Search through the dictionary to see if any duplicate hashes have been found.
    bulk_delete_operations = []
    for hashval, duplicates in dict_of_duplicate_docs.items():
        if len(duplicates) <= 1:
            continue

        # Spare the first document so that we keep just one copy of the duplicates,
        # and iterate through the remaining to add delete operations.
        for dup in duplicates[1:]:
            delete_operation = {'delete': {'_index': dup[0], '_type': 'doc', '_id': dup[1]}}
            bulk_delete_operations.append(json.dumps(delete_operation))

    # Create a bulk file, containing all the delete operations, to be applied in a single request.
    with open('bulk_deletions_file.txt', 'w') as bulk_file:
        for op in bulk_delete_operations:
            bulk_file.write(op + '\n')

def main():
    scroll_over_all_docs()
    loop_over_hashes_and_remove_duplicates()

main()

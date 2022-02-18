import logging

from pymongo import errors
from pymongo.mongo_client import MongoClient
from pymongo.read_preferences import ReadPreference

# Default options
__config = {
    'uri': 'mongodb://localhost:27017/feria',
    'fsync': False,
    'write_concern': 0,
    'separate_collections': False,
    'replica_set': None,
    'unique_key': None,
    'buffer': None,
    'stop_on_duplicate': 0
}

dbClient = MongoClient(
            __config['uri'],
            fsync= __config['fsync'],
            read_preference= ReadPreference.PRIMARY)
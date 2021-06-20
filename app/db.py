import logging
import os

from pymongo import MongoClient

DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_collection(collection_name: str):
    """
    Get MongoDB Collection
    """
    client = MongoClient(
        f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE"
    )
    db = client[DB_NAME]
    collection = db[collection_name]
    return collection


def insert_to_database(hash_obj: dict, collection_name: str):
    """
    Insert object to MongoDB Collection
    """
    collection = get_db_collection(collection_name=collection_name)

    inserted_obj = collection.insert_one(hash_obj)
    hash_id = inserted_obj.inserted_id
    logger.info(hash_id)


def update_in_database(obj_id, new_hash: dict, collection_name: str):
    """
    Update object in collection
    """
    collection = get_db_collection(collection_name=collection_name)
    collection.update_one({'_id': obj_id}, {'$set': new_hash})


def find_in_database(hash_obj: dict, collection_name: str):
    """
    Find object by hash value
    """
    collection = get_db_collection(collection_name=collection_name)

    db_obj = collection.find_one(hash_obj)
    return db_obj

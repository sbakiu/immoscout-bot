import logging
import os

from pymongo import MongoClient

DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_collection(collection_name: str):
    client = MongoClient(
        f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE"
    )
    db = client[DB_NAME]
    collection = db[collection_name]
    return collection


def insert_to_database(hash_obj, collection_name):
    collection = get_db_collection(collection_name=collection_name)

    inserted_obj = collection.insert_one(hash_obj)
    hash_id = inserted_obj.inserted_id
    logger.info(hash_id)


def update_in_database(id, hash, collection_name):
    collection = get_db_collection(collection_name=collection_name)
    collection.update_one({'_id': id}, {'$set': hash})

def find_in_database(hash_obj, collection_name):
    collection = get_db_collection(collection_name=collection_name)

    db_obj = collection.find_one(hash_obj)
    return db_obj


def get_all_hashes_in_database(collection_name: str):
    collection = get_db_collection(collection_name=collection_name)

    db_objs = collection.find().sort("_id", -1).limit(25)
    hashes_in_db = []
    for db_obj in db_objs:
        hashes_in_db.append(db_obj["hash"])
    return hashes_in_db

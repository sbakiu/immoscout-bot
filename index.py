import requests
import os
from flask import Flask, Response, __version__
import json
import logging
# from bs4 import BeautifulSoup
from hashlib import sha3_512
from pymongo import MongoClient

NOTIFICATION_URL = 'https://api.pushbullet.com/v2/pushes'
NOTIFICATION_AUTH_KEY = os.environ['NOTIFICATION_AUTH_KEY']

DB_KEY = os.environ["DB_KEY"]
DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]
DB_URL = f"https://{DB_NAME}.restdb.io/rest/{COLLECTION_NAME}"

BAYERNHEIM = "https://bayernheim.de/mieten/"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def add_to_database(hash):
    client = MongoClient("mongodb+srv://%s:%s@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE" % (DB_USERNAME, DB_PASSWORD))
    hash_obj = {"hash": hash}
    db = client[DB_NAME]
    hashes = db[COLLECTION_NAME]
    hash_id = hashes.insert_one(hash_obj).inserted_id
    logger.info(hash_id)

def check_if_exists_in_database(hash):
    client = MongoClient("mongodb+srv://%s:%s@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE" % (DB_USERNAME, DB_PASSWORD))
    hash_obj = {"hash": hash}
    db = client[DB_NAME]
    hashes = db[COLLECTION_NAME]

    db_obj = hashes.find_one(hash_obj)
    return db_obj

@app.route('/checkBayernheim')
def find_new_places():
    logger.debug("Received Request BayernHeim")

    mieten = requests.get(BAYERNHEIM)
    # soup = BeautifulSoup(mieten.text, features="html.parser")
    hash_sha3_512 = sha3_512(mieten.text.encode('utf-8')).hexdigest()
    should_notify = False

    # check if hash exists in db
    db_obj = check_if_exists_in_database(hash_sha3_512)
    if db_obj is None:
        should_notify = True

    if should_notify:
        logger.debug("Sending Notification")

        add_to_database(hash_sha3_512)

        data = {
            'type': 'link',
            'title': f"Changes in BayernHeim",
            'body': f"Changes in BayernHeim",
            'url': BAYERNHEIM
        }
        requests.post(NOTIFICATION_URL, headers={'Access-Token': NOTIFICATION_AUTH_KEY}, json=data)
        return {
            'status' : 'SUCCESS'
        }
    else:
        logger.debug("Not Sending Notification")
        return "There are no changes"
    
    return {
        'status' : 'SUCCESS'
    }

if __name__ == "__main__":
    # pass
    app.run()

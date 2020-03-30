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

default_text = "Im Moment sind wir im Aufbau unseres Wohnungsbestandes. Sobald wir Wohnraum zur Vermietung anbieten können, werden wir an dieser Stelle berichten."

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def add_to_database(hash):
    client = MongoClient("mongodb+srv://%s:%s@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority" % (DB_USERNAME, DB_PASSWORD))
    hash_obj = {"hash": hash}
    db = client.appartmentSearch
    hashes = db.hashcollection
    hash_id = hashes.insert_one(hash_obj).inserted_id
    logger.info(hash_id)

def check_if_exists_in_database(hash):
    client = MongoClient("mongodb+srv://%s:%s@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority" % (DB_USERNAME, DB_PASSWORD))
    hash_obj = {"hash": hash}
    db = client.appartmentSearch
    hashes = db.hashcollection

    db_obj = hashes.find_one(hash_obj)
    print(str(db_obj))

@app.route('/checkBayernheim')
def find_new_places():
    logger.debug("Received Request BayernHeim")

    mieten = requests.get(BAYERNHEIM)
    # soup = BeautifulSoup(mieten.text, features="html.parser")
    hash_sha3_512 = sha3_512(mieten.text.encode('utf-8')).hexdigest()
    should_notify = False
    # check if hash exists in db
    check_if_exists_in_database(hash_sha3_512)
    headers = {'x-apikey': DB_KEY, 'Content-Type': 'application/json'}
    filter_url = f"{DB_URL}?q={{\"hash\":\"{hash_sha3_512}\"}}" 
    request_get = requests.get(filter_url, headers=headers)
    logger.debug("Data Get request return status code: {0} with text: {1}.".format(request_get.status_code, request_get.text))

    req_raw = json.loads(request_get.text)

    if not req_raw:
        should_notify = True
        logging.info("Hash not found for Bayernheim")
    else:
        for obj in req_raw:
            should_notify = False
            logger.debug(obj.get("_id"))

    if should_notify:
        logger.debug("Sending Notification")

        add_to_database(hash_sha3_512)

        # Send DB Request
        headers = {'x-apikey': DB_KEY, 'Content-Type': 'application/json'}
        payload = {"hash": hash_sha3_512}
        
        # POST data to restdb.io
        r = requests.post(DB_URL, headers = headers, data = json.dumps(payload))
        logging.debug(r.status_code, r.text)

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
        # data = {
        #     'type': 'link',
        #     'title': f"No Changes in BayernHeim",
        #     'body': f"No Changes in BayernHeim",
        #     'url': BAYERNHEIM
        # }
        # requests.post(NOTIFICATION_URL, headers={'Access-Token': NOTIFICATION_AUTH_KEY}, json=data)
        return "There are no changes"
    
    return {
        'status' : 'SUCCESS'
    }

if __name__ == "__main__":
    # pass
    app.run()

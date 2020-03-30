import requests
import os
from flask import Flask, Response, __version__
import json
import logging
# from bs4 import BeautifulSoup
from hashlib import md5

NOTIFICATION_URL = 'https://api.pushbullet.com/v2/pushes'
NOTIFICATION_AUTH_KEY = os.environ['NOTIFICATION_AUTH_KEY']

DB_KEY = os.environ["DB_KEY"]
DB_NAME = os.environ["DB_NAME"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]
DB_URL = f"https://{DB_NAME}.restdb.io/rest/{COLLECTION_NAME}"

BAYERNHEIM = "https://bayernheim.de/mieten/"

default_text = "Im Moment sind wir im Aufbau unseres Wohnungsbestandes. Sobald wir Wohnraum zur Vermietung anbieten können, werden wir an dieser Stelle berichten."

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/checkBayernheim')
def find_new_places():
    logger.debug("Received Request BayernHeim")

    mieten = requests.get(BAYERNHEIM)
    # soup = BeautifulSoup(mieten.text, features="html.parser")
    hash_sha3_512 = md5(mieten.text.encode('utf-8')).hexdigest()
    should_notify = False
    # check if hash exists in db
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
            # should_notify = False
            should_notify = True
            logger.debug(obj.get("_id"))

    if should_notify:
        logger.debug("Sending Notification")

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

import requests
import os
from flask import Flask, Response, __version__
import logging
from hashlib import sha3_512
from pymongo import MongoClient
import telegram

DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

BAYERNHEIM = "https://bayernheim.de/mieten/"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = telegram.Bot(token=BOT_TOKEN)

def get_db_collection():
    client = MongoClient(
        "mongodb+srv://%s:%s@cluster0-6gkyq.mongodb.net/test?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE" % (DB_USERNAME, DB_PASSWORD))
    db = client[DB_NAME]
    hashes = db[COLLECTION_NAME]
    return hashes

def add_to_database(hash_obj):
    hashes = get_db_collection()
    
    hash_id = hashes.insert_one(hash_obj).inserted_id
    logger.info(hash_id)

def add_many_to_database(hash_objs):
    hashes = get_db_collection()

    hashes.insert_many(hash_objs)

def check_if_exists_in_database(hash_obj):
    hashes = get_db_collection()

    db_obj = hashes.find_one(hash_obj)
    return db_obj
    
def get_all_hashes_in_database():
    hashes = get_db_collection()

    db_objs = hashes.find().sort("_id", -1).limit(50)
    hashes_in_db = []
    for db_obj in db_objs:
        hashes_in_db.append(db_obj["hash"])
    return hashes_in_db

def get_bayernheim_data():
    return "Changes in BayernHeim"

def get_immoscout_data(apartment):
    text = f"Apartment: {apartment['title']} - Address: {apartment['address']['description']['text']} - Size:{apartment['livingSpace']} m2 - Price (warm): {apartment['calculatedPrice']['value']} EUR -  - [https://www.immobilienscout24.de/expose/{apartment['@id']}](https://www.immobilienscout24.de/expose/{apartment['@id']})"
    return text

def push_notification(text):
    m = bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

@app.route('/findplaces')
def find_new_places():
    search_bayernheim()
    search_immobilienscout()
    return {
        'status' : 'SUCCESS'
    }

@app.route('/checkimmobilienscout')
def search_immobilienscout():
    IMMO_SEARCH_URL = os.environ['IMMO_SEARCH_URL']
    apartments = requests.post(IMMO_SEARCH_URL).json()['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']
    
    unseen_apartments = []
    seen_apartments = get_all_hashes_in_database()
    newly_seen_appartments = []

    public_companies = ["GWG", "GEWOFAG"]

    if not type(apartments) is list:
        apartments = [apartments]

    for apartment in apartments:
        hash_id = sha3_512(apartment['@id'].encode('utf-8')).hexdigest()
        hash_obj = {"hash": hash_id}
        if not hash_id in seen_apartments:
            unseen_apartments.append(apartment)
            seen_apartments.append(hash_obj)
    
    parsed_unseen_apartments = []
    for unseen_apartment in unseen_apartments:
        apartment = unseen_apartment['resultlist.realEstate']
        is_public = False
        
        if 'realtorCompanyName' in apartment:
            company = apartment['realtorCompanyName'].upper()
            for c in public_companies:
                if company.find(c) != -1:
                    is_public = True

        text = get_immoscout_data(apartment)
        # If you are interested only in public companies uncomment the next 2 line.
        # if is_public:
            # push_notification(data)
        
        # If you are interested only in public companies comment out the next line.
        push_notification(text)
        newly_seen_appartments.append(apartment)

    if newly_seen_appartments:
        add_many_to_database(seen_apartments)

    return {
        'status' : 'SUCCESS',
        'unseen_apartments' : parsed_unseen_apartments
    }

@app.route('/checkBayernheim')
def search_bayernheim():
    logger.debug("Received Request BayernHeim")

    mieten = requests.get(BAYERNHEIM)
    # soup = BeautifulSoup(mieten.text, features="html.parser")
    hash_sha3_512 = sha3_512(mieten.text.encode('utf-8')).hexdigest()
    hash_obj = {"hash": hash_sha3_512}
    should_notify = False

    # check if hash exists in db
    db_obj = check_if_exists_in_database(hash_obj)
    if db_obj is None:
        should_notify = True

    if should_notify:
        logger.debug("Sending Notification")
        add_to_database(hash_obj)
        data = get_bayernheim_data()
        push_notification(data)
    else:
        logger.debug("Not Sending Notification")
    
    return {
        'status' : 'SUCCESS'
    }

if __name__ == "__main__":
    # pass
    app.run()

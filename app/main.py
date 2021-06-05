import logging
import os

from fastapi import FastAPI

from pymongo import MongoClient

import app.db as db
import app.utils as utils

import telegram

BH_COLLECTION_NAME = os.environ["BH_COLLECTION_NAME"]
IMMO_COLLECTION_NAME = os.environ["IMMO_COLLECTION_NAME"]

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SECRET = os.environ["SECRET"]

IMMO_SEARCH_URL = os.environ["IMMO_SEARCH_URL"]
BAYERNHEIM = "https://bayernheim.de/mieten/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telegram.Bot(token=BOT_TOKEN)
app = FastAPI()


@app.get("/findplaces")
def find_new_places(q: str = ""):
    if not q:
        return {"status": "FAILED"}
    else:
        search_bayernheim(q)
        search_immobilienscout(q)
        return {"status": "SUCCESS"}


@app.get("/checkBayernheim")
def search_bayernheim(q: str = ""):
    if utils.verify_secret(q, SECRET):
        logger.info("Searching Bayernheim.")

        # Get hash values for the BayernHeim page
        hash_obj = utils.get_bayernheim_hash(BAYERNHEIM)

        # Get hash value stored in database
        db_obj = db.find_in_database(hash_obj, BH_COLLECTION_NAME)

        # Check if notification should be sent
        should_notify = utils.compare_bh_hashes(db_obj, hash_obj)

        if should_notify:
            # Process BayernHeim page update
            utils.process_bayernheim_update(
                bayernheim_link=BAYERNHEIM,
                db_obj=db_obj,
                hash_obj=hash_obj,
                bayernheim_collection=BH_COLLECTION_NAME,
                bot=bot,
                chat_id=CHAT_ID
            )
        else:
            logger.debug("Not Sending Notification")

    return {"status": "SUCCESS"}


@app.get("/checkimmobilienscout")
def search_immobilienscout(q: str = ""):
    if utils.verify_secret(q, SECRET):
        logger.info("Searching Immoscout")

        # Get apartments in Immoscout
        apartments = utils.get_immoscout_apartments(immo_search_url=IMMO_SEARCH_URL)

        # Get already seen apartments from DB
        seen_apartments = db.get_all_hashes_in_database(IMMO_COLLECTION_NAME)

        # Filter unseen apartments
        unseen_apartments = utils.filter_unseen_apartments(apartments, seen_apartments)

        # Process new apartments
        if unseen_apartments:
            utils.process_unseen_apartments(
                unseen_apartments=unseen_apartments,
                bot=bot,
                chat_id=CHAT_ID,
                immo_collection_name=IMMO_COLLECTION_NAME
            )

    return {"status": "SUCCESS"}

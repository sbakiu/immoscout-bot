import logging
import os
import requests

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

        hash_obj = utils.get_bayernheim_hash(BAYERNHEIM)

        db_obj = db.find_in_database(hash_obj, BH_COLLECTION_NAME)

        should_notify = utils.compare_bh_hashes(db_obj, hash_obj)

        if should_notify:
            logger.debug("Sending Notification")
            db.update_in_database(db_obj["_id"], hash_obj, collection_name=BH_COLLECTION_NAME)
            text = utils.get_bayernheim_text(BAYERNHEIM)
            utils.push_notification(bot, CHAT_ID, text)
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

import logging
import os

from fastapi import FastAPI

from pymongo import MongoClient

import app.utils as utils

from app.bayernheim import BayernHeim
from app.immoscout import ImmoScout

SECRET = os.environ["SECRET"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        hash_obj = BayernHeim.get_bayernheim_hash()

        # Get hash value stored in database
        db_obj = BayernHeim.get_stored_hash_from_db()
        # Check if notification should be sent
        should_notify = BayernHeim.compare_bh_hashes(db_obj, hash_obj)

        if should_notify:
            # Process BayernHeim page update
            BayernHeim.process_bayernheim_update(db_obj=db_obj, hash_obj=hash_obj)
        else:
            logger.debug("Not Sending Notification")

    return {"status": "SUCCESS"}


@app.get("/checkimmobilienscout")
def search_immobilienscout(q: str = ""):
    if utils.verify_secret(q, SECRET):
        logger.info("Searching Immoscout")

        # Get announcements in Immoscout
        active_announcements = ImmoScout.get_immoscout_active_announcements()

        # Get already seen apartments from DB
        seen_announcements = ImmoScout.get_already_seen_announcements()

        # Filter unseen apartments
        unseen_announcements = ImmoScout.filter_unseen_announcements(active_announcements, seen_announcements)

        # Process new apartments
        ImmoScout.process_unseen_apartments(
            unseen_announcements=unseen_announcements,
            immo_collection_name=ImmoScout.COLLECTION_NAME
        )

    return {"status": "SUCCESS"}

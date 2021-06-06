import logging
import os

from fastapi import FastAPI

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

    return {"status": "SUCCESS"}


@app.get("/checkimmobilienscout")
def search_immobilienscout(q: str = ""):
    if utils.verify_secret(q, SECRET):
        logger.info("Searching Immoscout")
        immoscout = ImmoScout()

        # Get announcements in Immoscout
        immoscout.get_immoscout_active_announcements()

        # Get already seen announcements from DB
        immoscout.get_already_seen_announcements()

        # Filter unseen announcements
        immoscout.filter_unseen_announcements()

        # Process new announcements
        immoscout.process_unseen_announcements()

    return {"status": "SUCCESS"}

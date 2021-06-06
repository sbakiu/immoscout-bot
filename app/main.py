import logging
import os
import app.utils as utils

from app.bayernheim import BayernHeim
from app.immoscout import ImmoScout
from fastapi import FastAPI

SECRET = os.environ["SECRET"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/checkBayernheim")
def search_bayernheim(q: str = ""):
    if utils.verify_secret(q, SECRET):
        logger.info("Searching BayernHeim.")
        bayernheim = BayernHeim()

        # Check BayernHeim web for changes
        bayernheim.check_for_changes()

    return {"status": "SUCCESS"}


@app.get("/checkimmobilienscout")
def search_immobilienscout(q: str = ""):
    if utils.verify_secret(q, SECRET):
        logger.info("Searching ImmoScout")
        immoscout = ImmoScout()

        # Check ImmoScout for new announcements
        immoscout.check_for_new_announcements()

    return {"status": "SUCCESS"}

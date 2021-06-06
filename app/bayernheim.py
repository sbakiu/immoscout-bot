import logging
import os
import requests

from hashlib import sha3_512

from app.bot import Bot
import app.db as db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BayernHeim(object):

    COLLECTION_NAME = os.environ["BH_COLLECTION_NAME"]
    URL = "https://bayernheim.de/mieten/"

    def __init__(self):
        pass

    @staticmethod
    def get_bayernheim_hash():
        """
        Get BayernHeim page hash
        """
        mieten = requests.get(BayernHeim.URL)
        mieten_text = mieten.text

        hash_sha3_512 = sha3_512(mieten_text.encode("utf-8")).hexdigest()
        hash_obj = {"hash": hash_sha3_512}
        logger.info(f"Calculated hash: {hash_sha3_512}")
        return hash_obj

    @staticmethod
    def get_stored_hash_from_db():
        # Get hash value stored in database
        db_obj = db.find_in_database(None, BayernHeim.COLLECTION_NAME)
        return db_obj

    @staticmethod
    def compare_bh_hashes(db_obj, hash_obj):
        """
        Compare the web page hash with the one stored in database
        """
        if db_obj is None:
            logger.info("DB obj is none")
            return False

        db_hash, web_hash = db_obj["hash"], hash_obj["hash"]

        return db_hash != web_hash

    @staticmethod
    def prepare_bayernheim_text():
        """
        Prepare text for BayernHeim notification
        """
        return f"Changes in BayernHeim: {BayernHeim.URL}"

    @staticmethod
    def process_bayernheim_update(db_obj, hash_obj):
        """
        Update database and send notification for BayernHeim update
        """
        db.update_in_database(db_obj["_id"], hash_obj, collection_name=BayernHeim.COLLECTION_NAME)
        text = BayernHeim.prepare_bayernheim_text()
        bot = Bot()
        bot.push_notification(text=text)

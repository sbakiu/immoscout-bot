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
        """
        Empty method. Might be filled later
        """
        pass

    def check_for_changes(self):
        # Get hash values for the BayernHeim page
        self.get_bayernheim_hash()

        # Get hash value stored in database
        self.get_stored_hash_from_db()

        # Check if notification should be sent
        should_notify = self.compare_bh_hashes()

        if should_notify:
            # Process BayernHeim page update
            self.process_bayernheim_update()

    def get_bayernheim_hash(self):
        """
        Get BayernHeim page hash
        """
        mieten = requests.get(BayernHeim.URL)
        mieten_text = mieten.text

        hash_sha3_512 = sha3_512(mieten_text.encode("utf-8")).hexdigest()
        hash_obj = {"hash": hash_sha3_512}
        logger.info(f"Calculated hash: {hash_sha3_512}")
        self.hash_obj = hash_obj

    def get_stored_hash_from_db(self):
        # Get hash value stored in database
        db_obj = db.find_in_database(None, BayernHeim.COLLECTION_NAME)
        self.db_obj = db_obj

    def compare_bh_hashes(self):
        """
        Compare the web page hash with the one stored in database
        """
        if self.db_obj is None:
            logger.info("DB obj is none")
            return False

        db_hash, web_hash = self.db_obj["hash"], self.hash_obj["hash"]

        return db_hash != web_hash

    @staticmethod
    def prepare_bayernheim_text():
        """
        Prepare text for BayernHeim notification
        """
        return f"Changes in BayernHeim: {BayernHeim.URL}"

    def process_bayernheim_update(self):
        """
        Update database and send notification for BayernHeim update
        """
        db.update_in_database(self.db_obj["_id"], self.hash_obj, collection_name=BayernHeim.COLLECTION_NAME)
        text = BayernHeim.prepare_bayernheim_text()
        bot = Bot()
        bot.push_notification(text=text)

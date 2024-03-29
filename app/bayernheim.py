import logging
import os
import requests

from bs4 import BeautifulSoup

from hashlib import sha3_512

from app.bot import Bot
import app.db as db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BayernHeim(object):

    COLLECTION_NAME = os.environ["BH_COLLECTION_NAME"]
    URL = "https://bayernheim.de"

    def __init__(self):
        """
        Empty method. Might be filled later
        """
        pass

    def check_for_changes(self):
        """
        Check for changes in URL
        """
        # Get hash values for the BayernHeim page
        self.get_bayernheim_hash()

        # Get hash value stored in database
        self.get_hash_from_db()

        # Check if notification should be sent
        if self.should_notify():
            # Process BayernHeim page update
            self.process_bayernheim_update()

    def get_bayernheim_hash(self):
        """
        Get BayernHeim first article hash
        """
        bh = requests.get(BayernHeim.URL)
        bh_content = bh.content

        soup = BeautifulSoup(bh_content, "lxml")
        first_article_text = soup.find_all("article")[0].get_text()

        hash_sha3_512 = sha3_512(first_article_text.encode("utf-8")).hexdigest()
        hash_obj = {"hash": hash_sha3_512}
        self.hash_obj = hash_obj

    def get_hash_from_db(self):
        """
        Get hash value stored in the database
        """
        # Get hash value stored in database
        db_obj = db.find_in_database(None, BayernHeim.COLLECTION_NAME)
        self.db_obj = db_obj

    def should_notify(self):
        """
        Compare the web page hash with the one fetched from the database. If different return True, otherwise False
        """
        if self.db_obj is None:
            logger.info("DB object is none.")
            return False

        db_hash, web_hash = self.db_obj["hash"], self.hash_obj["hash"]

        if db_hash == web_hash:
            logger.info("Hash are equal.")
            return False
        else:
            logger.info("Hash are not equal.")
            return True

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

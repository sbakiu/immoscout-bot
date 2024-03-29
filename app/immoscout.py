import logging
import os
import re
import requests

from typing import List

from app.bot import Bot
import app.db as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImmoScout(object):
    COLLECTION_NAME = os.environ["IMMO_COLLECTION_NAME"]
    URLS = os.environ["IMMO_SEARCH_URL"]
    URL_SPLIT_CHAR = ";"

    def __init__(self):
        """
        Split URLs to be checked
        """
        logger.info("Initializing ImmoScout.")
        self.immo_urls = ImmoScout.URLS.split(ImmoScout.URL_SPLIT_CHAR)
        self.cache = ImmoScout._populate_cache()

    @staticmethod
    def _populate_cache() -> List[str]:
        """
        Initialize ImmoScout cache
        """
        logger.info("Initializing cache.")
        return db.get_hashes_in_database(collection_name=ImmoScout.COLLECTION_NAME)

    def check_for_new_announcements(self):
        """
        Check for new announcements from URL
        """
        # Get active announcements in ImmoScout
        self.get_active_announcements()

        # Filter unseen announcements
        self.filter_unseen_announcements()

        # Process new announcements
        self.process_unseen_announcements()

    def get_active_announcements(self):
        """
        Get announcements online from the urls
        """
        active_announcements_list = self.get_all_active_announcements()

        # Get unique announcements
        active_announcement_dict = {
            active_announcement.get("@id"): active_announcement for active_announcement in active_announcements_list
        }

        self.active_announcements = list(active_announcement_dict.values())

    def get_all_active_announcements(self) -> List[dict]:
        """
        Get all active announcements for all urls
        :return:
        """
        active_announcements_list = []
        # Iterate over all urls
        for url in self.immo_urls:
            try:
                response_text = requests.post(url)
                announcements_json = response_text.json()
                announcements_resultlist = announcements_json["searchResponseModel"]["resultlist.resultlist"]
                url_active_announcements = announcements_resultlist["resultlistEntries"][0]["resultlistEntry"]
            except Exception as e:
                logger.warning("Could not read any listed apartment")
                url_active_announcements = []

            if not type(url_active_announcements) is list:
                url_active_announcements = [url_active_announcements]

            active_announcements_list.extend(url_active_announcements)

        return active_announcements_list

    def filter_unseen_announcements(self):
        """
        Filter announcements not yet seen
        """
        unseen_announcements = []
        collection = db.get_db_collection(collection_name=ImmoScout.COLLECTION_NAME)

        for announcement in self.active_announcements:
            announcement_id = announcement["@id"]

            if self.check_if_announcement_not_seen_yet(announcement_id, collection):
                unseen_announcements.append(announcement)

        self.unseen_announcements = unseen_announcements

    def check_if_announcement_not_seen_yet(self, announcement_id: str, collection) -> bool:
        """
        Check if announcement is in the DB on in the local cache
        :param announcement_id:
        :param collection:
        :return:
        """
        if announcement_id in self.cache:
            logger.info(f"Checking ID: {announcement_id} in the cache.")
            return False

        self.cache.append(announcement_id)

        hash_obj = {"hash": announcement_id}
        if collection.count_documents(hash_obj, limit=1):
            logger.info(f"Checking ID: {announcement_id} in the database.")
            return False
        else:
            return True

    @staticmethod
    def prepare_apartment_notification_text(apartment: dict) -> str:
        """
        Prepare notification text for the apartment
        """
        title_reg_ex = r'[^a-zA-Z0-9.\d\s]+'
        title = re.sub(title_reg_ex, "", apartment["title"])
        address = re.sub(title_reg_ex, "", apartment["address"]["description"]["text"])
        size = apartment["livingSpace"]
        price_warm = ImmoScout.get_price_from_text(apartment=apartment)

        announcement_link = f"https://www.immobilienscout24.de/expose/{apartment['@id']}"
        text_title = f"Apartment: {title} - Address: {address} - Size:{size} m2 - Price (warm): {price_warm} EUR - "
        text_with_link = text_title + f" - [{announcement_link}]({announcement_link})"

        return text_with_link

    @staticmethod
    def get_price_from_text(apartment: dict) -> str:
        """
        Get price value from apartment text
        """
        price_warm = "NONE"
        try:
            price_warm = apartment["calculatedPrice"]["value"]
        except Exception as e:
            try:
                price_warm = apartment["calculatedTotalRent"]["totalRent"]["value"]
            except Exception as e:
                logger.info(f"Error with Apartment: {str(apartment)} ")

        return str(price_warm)

    def process_unseen_announcements(self):
        """
        Process all unseen announcements
        """
        if not self.unseen_announcements:
            return

        # public_companies = ["GWG", "GEWOFAG"]
        for unseen_announcement in self.unseen_announcements:
            apartment = unseen_announcement["resultlist.realEstate"]
            text = ImmoScout.prepare_apartment_notification_text(apartment)

            # If you are interested only in public companies uncomment the next instructions
            # is_public = False
            # if 'realtorCompanyName' in apartment:
            #     company = apartment['realtorCompanyName'].upper()
            #     for c in public_companies:
            #         if company.find(c) != -1:
            #             is_public = True

            # if is_public:

            db.insert_to_database({"hash": apartment["@id"]}, collection_name=ImmoScout.COLLECTION_NAME)
            bot = Bot()
            bot.push_notification(text=text)

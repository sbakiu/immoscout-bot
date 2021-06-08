import logging
import os
import re
import requests

from app.bot import Bot
import app.db as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImmoScout(object):
    COLLECTION_NAME = os.environ["IMMO_COLLECTION_NAME"]
    URL = os.environ["IMMO_SEARCH_URL"]

    def __init__(self):
        """
        Empty method. Might be filled later
        """
        pass

    def check_for_new_announcements(self):
        """
        Check for new announcements from URL
        """
        # Get active announcements in ImmoScout
        self.get_active_announcements()

        # Get already seen announcements from DB
        self.get_already_seen_announcements()

        # Filter unseen announcements
        self.filter_unseen_announcements()

        # Process new announcements
        self.process_unseen_announcements()

    def get_active_announcements(self):
        """
        Get announcements online from the url
        """
        try:
            response_text = requests.post(ImmoScout.URL)
            announcements_json = response_text.json()
            announcements_resultlist = announcements_json["searchResponseModel"]["resultlist.resultlist"]
            active_announcements = announcements_resultlist["resultlistEntries"][0]["resultlistEntry"]
        except Exception as e:
            logger.warn("Could not read any listed apartment")
            active_announcements = []

        if not type(active_announcements) is list:
            active_announcements = [active_announcements]

        self.active_announcements = active_announcements

    def get_already_seen_announcements(self):
        """
        Get announcement Ids stored in the database
        """
        # Get already seen announcements from DB
        seen_announcements = db.get_all_hashes_in_database(ImmoScout.COLLECTION_NAME)
        self.seen_announcements = seen_announcements

    def filter_unseen_announcements(self):
        """
        Filter announcements not yet seen
        """
        unseen_announcements = []

        for announcement in self.active_announcements:
            hash_obj = {"hash": announcement["@id"]}
            if not announcement["@id"] in self.seen_announcements:
                unseen_announcements.append(announcement)
                self.seen_announcements.append(hash_obj)

        self.unseen_announcements = unseen_announcements

    @staticmethod
    def prepare_apartment_notification_text(apartment):
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
    def get_price_from_text(apartment):
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

        return price_warm

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

            # If you are interested only in public companies uncomment the next 2 line.
            # is_public = False

            # If you are interested only in public companies comment out the following lines.
            # if 'realtorCompanyName' in apartment:
            #     company = apartment['realtorCompanyName'].upper()
            #     for c in public_companies:
            #         if company.find(c) != -1:
            #             is_public = True

            # if is_public:

            db.insert_to_database({"hash": apartment["@id"]}, collection_name=ImmoScout.COLLECTION_NAME)
            bot = Bot()
            bot.push_notification(text=text)

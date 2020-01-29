import requests
import os
from flask import Flask, Response, __version__
import json
from bs4 import BeautifulSoup

# DB_BUCKET = os.environ['DB_BUCKET']
# DB_AUTH_KEY = os.environ['DB_AUTH_KEY']
# BOT_TOKEN = os.environ['BOT_TOKEN']
# CHAT_ID = os.environ['CHAT_ID']
NOTIFICATION_URL = 'https://api.pushbullet.com/v2/pushes'
NOTIFICATION_AUTH_KEY = os.environ['NOTIFICATION_AUTH_KEY']

BAYERNHEIM = "https://bayernheim.de/mieten/"
default_text = "Im Moment sind wir im Aufbau unseres Wohnungsbestandes. Sobald wir Wohnraum zur Vermietung anbieten können, werden wir an dieser Stelle berichten."

app = Flask(__name__)

@app.route('/checkBayernheim')
def find_new_places():

    mieten = requests.get(BAYERNHEIM)
    soup = BeautifulSoup(mieten.text)
    should_notify = False
    for div in soup.find_all('div', {"class": "entry-content"}):
        for p in div.find_all('p'):
            text = p.get_text()
            if text == default_text:
                print("No change")
            else:
                should_notify = True

    if should_notify:
        data = {
            'type': 'link',
            'title': f"Changes in BayernHeim",
            'body': f"Changes in BayernHeim",
            'url': BAYERNHEIM
        }
        requests.post(NOTIFICATION_URL, headers={'Access-Token': NOTIFICATION_AUTH_KEY}, json=data)
        return "There are changes"
    else:
        return "There are no changes"
    # TELEGRAM_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    # seen_apartments = requests.get(f'https://kvdb.io/{DB_BUCKET}/{DB_KEY}', auth=(DB_AUTH_KEY, '')).json()
    # apartments = requests.post(IMMO_SEARCH_URL).json()['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']

    # unseen_apartments = []

    # public_companies = ["WBM", "HOWOGE", "GESOBAU", "GEWOBAG", "STADT UND LAND", "WOBEGE"]

    # for apartment in apartments:
    #     if apartment['@id'] not in seen_apartments:
    #         unseen_apartments.append(apartment)
    #         seen_apartments.append(apartment['@id'])
    
    # parsed_unseen_apartments = []

    # for a in unseen_apartments:
    #     apartment = a['resultlist.realEstate']
        
    #     if 'realtorCompanyName' in apartment:
    #         company = apartment['realtorCompanyName'].upper()
    #         for c in public_companies:
    #             if company.find(c) != -1:
    #                 isPublic = True
        
    #     text = f"*New Apartment: {apartment['title']}* - *Address*: {apartment['address']['description']} - *Size*:{apartment['livingSpace']} - *Price (warm)*: {apartment['calculatedPrice']['value']} EUR - [https://www.immobilienscout24.de/expose/{a['@id']}](https://www.immobilienscout24.de/expose/{a['@id']})",
    #     params = {
    #         'chat_id': CHAT_ID,
    #         'text': text,
    #         'parse_mode': 'Markdown'
    #     }
    #     parsed_unseen_apartments.append(text)
    #     # If you are interested only in public companies uncomment the next 2 line.
    #     # if isPublic:
    #         # requests.post(TELEGRAM_URL, params=params)
        
    #     # If you are interested only in public companies comment out the next line.
    #     requests.post(TELEGRAM_URL, params=params)
    # requests.post(f'https://kvdb.io/{DB_BUCKET}/{DB_KEY}', auth=(DB_AUTH_KEY, ''), json=seen_apartments)

    # return {
    #     'status' : 'SUCCESS',
    #     'unseen_apartments' : parsed_unseen_apartments
    # }

if __name__ == "__main__":
    pass
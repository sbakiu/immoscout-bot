import requests
import os
from flask import Flask, Response, __version__
import json
from bs4 import BeautifulSoup

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
        data = {
            'type': 'link',
            'title': f"No Changes in BayernHeim",
            'body': f"No Changes in BayernHeim",
            'url': BAYERNHEIM
        }
        requests.post(NOTIFICATION_URL, headers={'Access-Token': NOTIFICATION_AUTH_KEY}, json=data)
        return "There are no changes"

if __name__ == "__main__":
    pass

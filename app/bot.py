import os

import telegram

class Bot(object):

    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]

    def __init__(self):
        self.bot = telegram.Bot(token=Bot.BOT_TOKEN)

    def push_notification(self, text):
        """
        Push Telegram notification
        """
        self.bot.send_message(chat_id=Bot.CHAT_ID, text=text, parse_mode="Markdown", timeout=15)

import os

import telegram


class Bot(object):

    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]

    def __init__(self):
        self.telegram_bot = telegram.Bot(token=Bot.BOT_TOKEN)

    def push_notification(self, text: str):
        """
        Push Telegram notification
        """
        self.telegram_bot.send_message(chat_id=Bot.CHAT_ID, text=text, parse_mode="Markdown", timeout=15)

import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("CHAT_ID")


async def send_message(chat_id, text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)

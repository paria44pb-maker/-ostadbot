import os
from aiogram import Bot, Dispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

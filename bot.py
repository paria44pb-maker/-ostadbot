from aiogram import Bot, Dispatcher
from config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

async def setup_bot():
    print("Bot started...")

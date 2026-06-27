from aiogram import Bot, Dispatcher
from config import Config

config = Config()

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def setup_bot():
    print(f"Bot @{config.BOT_USERNAME} started...")

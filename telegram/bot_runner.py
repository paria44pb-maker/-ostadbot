from aiogram import Bot, Dispatcher
from security.token_guard import get_safe_token

bot = Bot(token=get_safe_token())
dp = Dispatcher()

async def start_bot():
    print("🤖 Telegram bot starting safely...")

    # جلوگیری از crash کل سیستم
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print("❌ Bot crashed:", e)

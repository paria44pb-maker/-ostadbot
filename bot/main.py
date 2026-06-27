from aiogram import Bot, Dispatcher, types
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def handle(msg: types.Message):
    if msg.text == "/start":
        await msg.answer(
            "🚀 CryptoPulse AI فعال شد\n\n"
            "پلن VIP برای سیگنال‌های حرفه‌ای"
        )

    elif msg.text == "/vip":
        await msg.answer("💰 خرید VIP: 10$")

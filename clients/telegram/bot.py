from aiogram import Bot, Dispatcher, types
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def handler(msg: types.Message):
    if msg.text == "/start":
        await msg.answer("🏢 CryptoPulse ENTERPRISE فعال شد")

    if msg.text == "/vip":
        await msg.answer("💎 VIP Plan: $15/month")

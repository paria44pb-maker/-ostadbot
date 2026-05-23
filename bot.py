import os
import asyncio
import logging
from telegram import Bot
from telegram.ext import Application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@comedyclick"

async def send_test_message():
    """ارسال یک پیام تست به کانال"""
    if not TOKEN or not CHANNEL_ID:
        logger.error("TOKEN یا CHANNEL_ID تنظیم نشده است")
        return
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="✅ ربات تست با موفقیت راه‌اندازی شد!")
        logger.info("پیام تست ارسال شد")
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {e}")

async def main():
    # فقط یک پیام تست بفرست و بعد از ۵ ثانیه ربات را خاموش کن
    await send_test_message()
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

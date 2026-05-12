import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# تنظیمات لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تابع استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام فرهاد! به استاد بات خوش آمدی.\n"
        "هر سوالی داشتی بپرس!"
    )

# تابع پیام‌ها با پاسخ شرطی ساده
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    logger.info(f"Received message: {text}")

    if "سلام" in text:
        reply = "سلام فرهاد! 😄 حالت چطوره؟"
    elif "خوبم" in text:
        reply = "خوشحالم که حالت خوبه 🌟"
    elif "کی هستی" in text:
        reply = "من OstadBot هستم 🤖"
    else:
        reply = "جالبه! بیشتر توضیح بده 👀"

    await update.message.reply_text(reply)

# تابع اصلی
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.err❌ BOT_TOKEN متغیر محیطی یافت نشد!")
        return

   

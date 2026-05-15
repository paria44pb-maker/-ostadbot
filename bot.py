import os
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# ==========================
# ENVIRONMENT VARIABLES
# ==========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")
NOBITEX_API_SECRET = os.getenv("NOBITEX_API_SECRET")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("🔍 Checking environment variables...")
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
print("NOBITEX_API_KEY:", NOBITEX_API_KEY)
print("DEEPSEEK_API_KEY:", DEEPSEEK_API_KEY)
print("GROQ_API_KEY:", GROQ_API_KEY)

# ==========================
# ERROR CHECK
# ==========================

if TELEGRAM_TOKEN is None:
    raise ValueError("❌ ERROR: TELEGRAM_TOKEN is missing in Railway Variables!")

# ==========================
# BOT START
# ==========================

print("🚀 STARTING BOT...")
bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# /start COMMAND
# ==========================

def start(update, context):
    update.message.reply_text("سلام فرهاد! 🤖 ربات با موفقیت روشن شد!")

# ==========================
# /price COMMAND
# ==========================

def price(update, context):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        btc_price = data["bitcoin"]["usd"]
        update.message.reply_text(f"💰 قیمت لحظه‌ای بیت‌کوین: {btc_price} USD")
    except Exception as e:
        update.message.reply_text(f"❌ خطا در دریافت قیمت: {e}")

# ==========================
# TELEGRAM HANDLERS
# ==========================

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("price", price))

# ==========================
# RUN BOT
# ==========================

updater.start_polling()
print("✅ BOT IS RUNNING 24/7")
updater.idle()

import os
import time
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# ==========================
# LOAD ENVIRONMENT VARIABLES
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
# ERROR CHECKS
# ==========================

if not TELEGRAM_TOKEN:
    raise ValueError("❌ ERROR: TELEGRAM_TOKEN is missing in Railway Variables!")

# ==========================
# BOT START
# ==========================

print("🚀 STARTING BOT...")

bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# COMMAND: /start
# ==========================

def start(update, context):
    update.message.reply_text("سلام فرهاد! 🤖 ربات با موفقیت روشن شد!")

# ==========================
# COMMAND: /price (Bitcoin)
# ==========================

def price(update, context):
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = r.json()
        btc_price = data["bitcoin"]["usd"]
        update.message.reply_text(f"💰 قیمت لحظه‌ای بیت‌کوین: {btc_price} USD")
    except:
        update.message.reply_text("❌ خطا در دریافت قیمت")

# ==========================
# TELEGRAM HANDLERS
# ==========================

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("price", price))

# ==========================
# RUN THE BOT
# ==========================

updater.start_polling()
print("✅ BOT IS RUNNING 24/7")
updater.idle()

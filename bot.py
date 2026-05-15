import os
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# ==========================
# ENVIRONMENT VARIABLES
# ==========================

print("🔍 Checking environment variables...")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")
NOBITEX_API_SECRET = os.getenv("NOBITEX_API_SECRET")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
print("NOBITEX_API_KEY:", NOBITEX_API_KEY)
print("NOBITEX_API_SECRET:", NOBITEX_API_SECRET)
print("DEEPSEEK_API_KEY:", DEEPSEEK_API_KEY)
print("GROQ_API_KEY:", GROQ_API_KEY)

# ==========================
# VALIDATE REQUIRED KEYS
# ==========================

if not TELEGRAM_TOKEN:
    raise ValueError("❌ ERROR: TELEGRAM_TOKEN is missing from Railway Variables!")

# ==========================
# START BOT
# ==========================

prin🚀 STARTING BOT...")

bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# COMMAND: /start
# ==========================

def start(update, context):
    update.message.reply_text("سلام فرهاد! 🤖 ربات با موفقیت روشن شد!")
 ==========================
# COMMAND: /price (Bitcoin)
# ==========================

def price(update, context):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        btc_price = data["bitcoin"]["usd"]
        update.message.reply_text(f"💰 قیمت لحظه‌ای بیت‌کوین: {btc_price} USD")
    except Exception as e:
        update.message.reply_text(f"

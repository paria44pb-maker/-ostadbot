import os
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# ==========================
# READ ENVIRONMENT VARIABLES
# ==========================

print("Checking environment variables...")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")
NOBITEX_API_SECRET = os.getenv("NOBITEX_API_SECRET")

print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
print("DEEPSEEK_API_KEY:", DEEPSEEK_API_KEY)
print("GROQ_API_KEY:", GROQ_API_KEY)
print("NOBITEX_API_KEY:", NOBITEX_API_KEY)
print("NOBITEX_API_SECRET:", NOBITEX_API_SECRET)

# ==========================
# VALIDATE TOKEN
# ==========================

if not TELEGRAM_TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN is missing in Railway Variables.")

# ==========================
# START BOT
# ==========================

print("Starting bot...")

bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# COMMAND: /start
# ==========================

def start(update, context):
    update.message.reply_text("سلام فرهاد! ربات با موفقیت روشن شد.")

# ==========================
# COMMAND: /price
# ==========================

def price(update, context):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        btc_price = data["bitcoin"]["usd"]
        update.message.reply_text(f"قیمت لحظه‌ای بیت‌کوین: {btc_price} دلار")
    except Exception as e:
        update.message.reply_text(f"خطا: {e}")

# ==========================
# HANDLERS
# ==========================

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("price", price))

# ==========================
# RUN
# ==========================

print("Bot is running...")
updater.start_polling()
updater.idle()

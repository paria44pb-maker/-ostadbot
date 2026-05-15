import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler

# ==========================
# ENV VARIABLES
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

if not TELEGRAM_TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN not found in Railway Variables.")


# ==========================
# COMMAND: /start
# ==========================

async def start(update, context):
    await update.message.reply_text("سلام فرهاد! ربات با موفقیت روشن شد 🤖")


# ==========================
# COMMAND: /price (bitcoin)
# ==========================

async def price(update, context):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        btc_price = data["bitcoin"]["usd"]
        await update.message.reply_text(f"قیمت بیت‌کوین: {btc_price} دلار")
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")


# ==========================
# RUN BOT
# ==========================

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))

print("Bot is running...")
app.run_polling()

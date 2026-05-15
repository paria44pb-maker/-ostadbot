import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ==========================
# ENV
# ==========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN is missing.")


# ==========================
# COMMAND: /start
# ==========================

async def start(update, context):
    await update.message.reply_text("سلام فرهاد! ربات با موفقیت روشن شد 🤖")


# ==========================
# COMMAND: /price
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
# MESSAGE HANDLER
# ==========================

async def echo(update, context):
    msg = update.message.text
    await update.message.reply_text(f"پیامت رسید فرهاد: {msg}")


# ==========================
# RUN BOT
# ==========================

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("Bot is running...")
app.run_polling()

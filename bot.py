import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


# ==========================
# ENV VARIABLES
# ==========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN not found in Railway Variables")


# ==========================
# COMMAND: /start
# ==========================

async def start(update, context):
    await update.message.reply_text("سلام فرهاد! ربات با موفقیت روشن شد 🤖🔥")


# ==========================
# COMMAND: /price (Bitcoin)
# ==========================

async def price(update, context):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        btc_price = data["bitcoin"]["usd"]
        await update.message.reply_text(f"قیمت بیت‌کوین الان: {btc_price} دلار 💰")
    except Exception as e:
        await update.message.reply_text(f"خطا در دریافت قیمت: {e}")


# ==========================
# TEXT MESSAGE HANDLER
# ==========================

async def message_handler(update, context):
    text = update.message.text.lower()

    # سلام
    if "سلام" in text or "hi" in text:
        await update.message.reply_text("سلام فرهاد! چطوری؟ 😊")

    # قیمت
    elif "قیمت" in text or "price" in text:
        await update.message.reply_text("برای دریافت قیمت بیت‌کوین دستور /price رو بزن 🔥")

    # نوبیتکس
    elif "نوبیتکس" in text:
        await update.message.reply_text("چه کاری با نوبیتکس داری فرهاد؟ 😎")

    # پیام‌های دیگر
    else:
        await update.message.reply_text("دارم گوش میدم فرهاد... دقیق‌تر بگو 👂")


# ==========================
# RUN BOT
# ==========================

def main():
    print("Bot is running...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    # پیام متنی
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()


if __name__ == "__main__":
    main()

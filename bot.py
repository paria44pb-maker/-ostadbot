import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


# ===============================
# ENV VARIABLES
# ===============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN not found")



# ===============================
# GET BITCOIN PRICE
# ===============================
def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        return data["bitcoin"]["usd"]
    except:
        return None



# ===============================
# SMART REPLY (DeepSeek)
# ===============================
def smart_reply(user_msg: str) -> str:
    if not DEEPSEEK_API_KEY:
        return "کلید DeepSeek تنظیم نشده."

    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "پاسخ کوتاه، مودب و دوستانه بده."},
                {"role": "user", "content": user_msg}
            ]
        }

        res = requests.post(url, json=payload, headers=headers, timeout=20)
        data = res.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"خطا: {e}"



# ===============================
# COMMANDS
# ===============================

async def start(update, context):
    await update.message.reply_text("سلام! ربات روشن است.")


async def help_command(update, context):
    await update.message.reply_text("دستورها: /start /help /price")


async def price(update, context):
    price = get_btc_price()
    if price:
        await update.message.reply_text(f"قیمت BTC: {price} دلار")
    else:
        await update.message.reply_text("خطا در دریافت قیمت!")


async def ai_handler(update, context):
    user_text = update.message.text
    response = smart_reply(user_text)
    await update.message.reply_text(response)



# ===============================
# MAIN
# ===============================

def main():
    print("Bot is running...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

    app.run_polling()


if __name__ == "__main__":
    main()

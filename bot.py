import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ===============================
# ENVIRONMENT VARIABLES
# ===============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment!")

# ===============================
# GET BITCOIN PRICE
# ===============================
def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        return requests.get(url).json()["bitcoin"]["usd"]
    except Exception:
        return None

# ===============================
# GROQ SMART REPLY
# ===============================
def smart_reply(user_msg: str) -> str:
    if not GROQ_API_KEY:
        return "GROQ API key is missing."

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a friendly Persian assistant."},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.4
        }

        res = requests.post(url, json=payload, headers=headers, timeout=20)
        data = res.json()

        if "error" in data:
            return f"Groq Error: {data['error']}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Groq request failed: {str(e)}"

# ===============================
# COMMAND HANDLERS
# ===============================
async def start(update, context):
    await update.message.reply_text("سلام! ربات Ultra‑Safe با Groq روشن است.")

async def help_command(update, context):
    await update.message.reply_text("دستورها: /start /help /price")

async def price(update, context):
    p = get_btc_price()
    if p:
        await update.message.reply_text(f"قیمت بیت‌کوین: {p} دلار")
    else:
        await update.message.reply_text("خطا در دریافت قیمت بیت‌کوین.")

async def ai_handler(update, context):
    user_text = update.message.text.strip()

    # جلوگیری از پاسخ مدل به پیام‌های خیلی کوتاه
    if len(user_text) < 2:
        await update.message.reply_text("لطفاً جمله کامل‌تر بنویس ❤️")
        return

    reply = smart_reply(user_text)
    await update.message.reply_text(reply)

# ===============================
# MAIN
# ===============================
def main():
    print("Bot is running... (Ultra‑Safe + Groq)")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

    app.run_polling()

if __name__ == "__main__":
    main()

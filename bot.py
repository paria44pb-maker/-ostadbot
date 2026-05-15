import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing!")


def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        return requests.get(url).json()["bitcoin"]["usd"]
    except Exception:
        return None


# ------------------------
# GROQ SMART REPLY
# ------------------------
def smart_reply(user_msg: str) -> str:
    if not GROQ_API_KEY:
        return "GROQ API key missing."

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a helpful Persian assistant."},
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


# ------------------------
# COMMANDS
# ------------------------
async def start(update, context):
    await update.message.reply_text("سلام! ربات با Groq روشن است.")


async def help_cmd(update, context):
    await update.message.reply_text("دستورات: /start /help /price")


async def price(update, context):
    p = get_btc_price()
    if p:
        await update.message.reply_text(f"قیمت بیت‌کوین: {p} دلار")
    else:
        await update.message.reply_text("خطا در دریافت قیمت.")


async def ai_handler(update, context):
    text = update.message.text.strip()

    if len(text) < 2:
        await update.message.reply_text("لطفاً جمله کامل‌تر بنویس ❤️")
        return

    reply = smart_reply(text)
    await update.message.reply_text(reply)


# ------------------------
# MAIN
# ------------------------
def main():
    print("Bot is running... (Groq Edition)")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

    app.run_polling()


if __name__ == "__main__":
    main()

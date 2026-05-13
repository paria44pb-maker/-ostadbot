import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY تنظیم نشده")


def ask_ai(text: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": text}
        ],
        "temperature": 0.3,
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq error:", repr(e))
        return "خطا در اتصال به هوش مصنوعی."


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام فرهاد! پیام بده تا با هوش مصنوعی جواب بدم.")


async def echo_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    reply = ask_ai(user_text)
    await update.message.reply_text(reply)


def main():
    # هیچ asyncio.run اینجا نداریم، فقط خود کتابخانه loop را مدیریت می‌کند
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_ai))

    # این تابع خودش event loop را ایجاد و مدیریت می‌کند
    app.run_polling()


if __name__ == "__main__":
    main()

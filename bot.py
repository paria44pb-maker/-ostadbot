import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from groq import Groq

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ---------------- GROQ ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "من OstadBot هستم.\n"
        "هر سوالی داری بپرس."
    )

# ---------------- CHAT ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "تو یک دستیار فارسی حرفه‌ای و دوستانه هستی. "
                        "کامل، روان و طبیعی جواب بده. "
                        "هیچوقت اسم کاربر را حدس نزن."
                    )
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        reply = completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq Error: {e}")
        reply = "خطا در اتصال به هوش مصنوعی."

    await update.message.reply_text(reply)

# ---------------- MAIN ----------------
def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        logger.error("BOT_TOKEN not found")
        return

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not found")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    logger.info("Bot started successfully")

    app.run_polling()

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()

import os
import logging

from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================
# تنظیمات
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# =========================================
# اتصال به Groq
# =========================================

client = Groq(api_key=GROQ_API_KEY)

# =========================================
# دستورات ربات
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 ربات هوش مصنوعی فعال شد

✅ آماده پاسخگویی به سوالات شما
✅ پشتیبانی از زبان فارسی
✅ متصل به مدل هوش مصنوعی Groq

دستورها:
/help
/reset
"""

    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
📚 راهنمای ربات

/start
شروع ربات

/help
نمایش راهنما

/reset
پاک کردن حافظه گفتگو

فقط پیام خود را ارسال کنید تا پاسخ دریافت کنید.
"""

    await update.message.reply_text(text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "✅ حافظه گفتگو پاک شد."
    )

# =========================================
# چت اصلی
# =========================================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    await update.message.chat.send_action("typing")

    try:

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
تو یک دستیار هوش مصنوعی حرفه‌ای هستی.

قوانین:
- فارسی روان و حرفه‌ای صحبت کن
- پاسخ‌ها دقیق و کامل باشند
- اگر سوال برنامه‌نویسی بود حرفه‌ای جواب بده
- ساختار پاسخ مرتب باشد
"""
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        answer = completion.choices[0].message.content

        if not answer:
            answer = "❌ پاسخی دریافت نشد."

        await update.message.reply_text(
            answer[:4000]
        )

    except Exception as e:

        logger.error(e)

        await update.message.reply_text(
            "❌ خطا در اتصال به هوش مصنوعی."
        )

# =========================================
# اجرای ربات
# =========================================

def main():

    if not BOT_TOKEN:

        logger.error("BOT_TOKEN پیدا نشد")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    logger.info("ربات اجرا شد ✅")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()

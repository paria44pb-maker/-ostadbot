import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام فرهاد! به OstadBot خوش آمدی.\nهر سوالی داری بپرس."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "سلام" in text:
        reply = "سلام فرهاد! حالت چطوره؟"

    elif "خوبم" in text:
        reply = "خوشحالم که حالت خوبه."

    elif "کی هستی" in text:
        reply = "من OstadBot هستم."

    else:
        reply = "متوجه شدم. بیشتر توضیح بده."

    await update.message.reply_text(reply)


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        logger.error("BOT_TOKEN environment variable not found")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Bot started successfully")

    app.run_polling()


if __name__ == "__main__":
    main()

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram import Update

from config import TELEGRAM_TOKEN
from handlers.start import start
from handlers.chat import chat

from memory.memory import init_db

from services.nobitex import get_wallets   # ✅ اضافه شد

import logging


# --------------------------------------
# LOGGING
# --------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --------------------------------------
# ERROR HANDLER
# --------------------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)

    try:
        if update and hasattr(update, "message"):
            await update.message.reply_text("❌ خطایی در ربات رخ داد.")
    except Exception as e:
        logger.error(e)


# --------------------------------------
# STARTUP
# --------------------------------------
print("🚀 STARTING BOT...")


# --------------------------------------
# DATABASE INIT
# --------------------------------------
init_db()


# --------------------------------------
# TOKEN CHECK
# --------------------------------------
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN یافت نشد!")

print("✅ TOKEN LOADED")


# --------------------------------------
# CREATE APP
# --------------------------------------
app = Application.builder().token(TELEGRAM_TOKEN).build()


# --------------------------------------
# COMMAND: WALLET (NOBITEX)
# --------------------------------------
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_wallets()
    await update.message.reply_text(result)


# --------------------------------------
# HANDLERS
# --------------------------------------
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))   # ✅ اضافه شد
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.add_error_handler(error_handler)


# --------------------------------------
# BOT START
# --------------------------------------
print("🤖 BOT RUNNING...")
app.run_polling(drop_pending_updates=True)

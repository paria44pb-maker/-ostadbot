import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from handlers.start import start
from handlers.chat import chat

from memory.memory import init_db


# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================
# LOAD ENV VARIABLES
# =========================================

TELEGRAM_TOKEN = (
    os.getenv("TELEGRAM_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
)

# =========================================
# ERROR HANDLER
# =========================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):

    logger.exception(
        "Exception while handling update:",
        exc_info=context.error
    )

    try:

        if (
            update
            and hasattr(update, "message")
            and update.message
        ):

            await update.message.reply_text(
                "❌ خطایی در پردازش درخواست رخ داد."
            )

    except Exception as e:

        logger.error(f"Error in error handler: {e}")


# =========================================
# STARTUP
# =========================================

print("🚀 STARTING BOT...")


# =========================================
# TOKEN VALIDATION
# =========================================

if not TELEGRAM_TOKEN:

    logger.error(
        "❌ TELEGRAM_TOKEN not found in environment variables."
    )

    raise ValueError(
        "❌ TELEGRAM_TOKEN یافت نشد! "
        "لطفاً آن را در Railway Variables تنظیم کن."
    )

print("✅ TOKEN LOADED")


# =========================================
# DATABASE INIT
# =========================================

try:

    init_db()
    print("✅ DATABASE INITIALIZED")

except Exception as e:

    logger.exception("Database initialization failed")

    raise RuntimeError(
        f"❌ Database init failed: {e}"
    )


# =========================================
# CREATE APPLICATION
# =========================================

try:

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    print("✅ APPLICATION CREATED")

except Exception as e:

    logger.exception("Application creation failed")

    raise RuntimeError(
        f"❌ Failed to create Telegram application: {e}"
    )


# =========================================
# REGISTER HANDLERS
# =========================================

app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat,
    )
)

app.add_error_handler(error_handler)

print("✅ HANDLERS REGISTERED")


# =========================================
# RUN BOT
# =========================================

prin....

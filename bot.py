from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from config import TELEGRAM_TOKEN

from handlers.start import start
from handlers.chat import chat

from memory.memory import init_db

init_db()

app = Application.builder().token(
    TELEGRAM_TOKEN
).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)

print("BOT RUNNING...")

app.run_polling()

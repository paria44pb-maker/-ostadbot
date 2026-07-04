import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from system.security import Security
from infra.service_registry import ServiceRegistry


class TelegramBot:
    """
    Telegram interface for CryptoPulseAI
    """

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.app = ApplicationBuilder().token(self.token).build()

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user.id

        if not Security.is_admin(user):
            await update.message.reply_text("⛔ Access denied")
            return

        await update.message.reply_text("🚀 CryptoPulseAI is running")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = Security.sanitize(update.message.text)

        await update.message.reply_text(f"📩 Received: {text}")

    def setup(self):
        self.app.add_handler(CommandHandler("start", self.start_cmd))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self):
        self.setup()
        self.app.run_polling()

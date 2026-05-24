import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.settings import TELEGRAM_BOT_TOKEN, OWNER_ID, CHANNEL_ID
from telegram_bot.notifier import TelegramNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.notifier = TelegramNotifier()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(CommandHandler("status", self.status))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if OWNER_ID and update.effective_user.id != OWNER_ID:
            await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
            [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
            [InlineKeyboardButton("📈 تحلیل ۲۵ اندیکاتور", callback_data="technical")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        await update.message.reply_text(
            "🔥 *ربات فوق‌هوشمند کریپتو* 🔥\n\n"
            "✅ ۲۵ اندیکاتور و اسیلاتور\n"
            "✅ معامله خودکار دمو و واقعی\n"
            "✅ تحلیل هوشمند با Groq\n"
            "✅ ارسال خودکار سیگنال به کانال\n\n"
            "از منوی زیر انتخاب کنید:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "✅ ربات فعال است\n"
            f"📢 کانال: {CHANNEL_ID}\n"
            "⚡ سیگنال هر ۵ دقیقه\n"
            "📚 آموزش هر ۲ ساعت\n"
            "📰 اخبار هر ۲ ساعت\n"
            "😨 ترس و طمع هر ۴ ساعت"
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "prices":
            await query.edit_message_text("📊 قیمت لحظه‌ای:\nدر حال توسعه...")
        elif query.data == "signal":
            await query.edit_message_text("🎯 سیگنال فوری:\nدر حال توسعه...")
        elif query.data == "technical":
            await query.edit_message_text("📈 تحلیل ۲۵ اندیکاتور:\nدر حال توسعه...")
        elif query.data == "help":
            await query.edit_message_text("❓ راهنما:\nبرای اطلاعات بیشتر به کانال مراجعه کنید.")

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("Telegram bot started")
        return self.app

import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ------------------ خواندن توکن از Environment ------------------
TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در متغیرهای محیطی یافت نشد!")

# ------------------ دستورات پایه ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 من OstadBot هستم و آماده‌ام 😊")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستورهای موجود:\n/start - شروع\n/help - راهنما")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"پیامت دریافت شد: {text}")

# ------------------ ساخت اپلیکیشن ------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ثبت Handlerها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    print("🚀 Bot is running...")
    app.run_polling()

# ------------------ اجرای برنامه ------------------
if __name__ == "__main__":
    print("TOKEN RAW:", repr(TOKEN))
    print("TOKEN LENGTH:", len(TOKEN))
    main()

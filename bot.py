import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- خواندن توکن از متغیر محیطی ---
TOKEN = os.getenv("BOT_TOKEN")
print(f"RAW TOKEN FROM ENV: {repr(TOKEN)}")  # برای دیباگ در لاگ Railway

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN متغیر محیطی یافت نشد")

TOKEN = TOKEN.strip()
print(f"TOKEN LENGTH: {len(TOKEN)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام فرهاد! ربات فعاله ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"پیامت رو گرفتم: {update.message.text}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🚀 Bot is starting polling...")
    app.run_polling()

if __name__ == "__main__":
    main()

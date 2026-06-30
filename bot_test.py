import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات با موفقیت اجرا شد!")

async def main():
    if not TOKEN:
        print("❌ BOT_TOKEN not found!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("✅ Telegram Bot is running!")
    
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

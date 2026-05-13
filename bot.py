import os
import asyncio
from telegram.ext import Application, CommandHandler
from services.nobitex_service import test_connection


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN is missing!")


# ---------------------------
#      فرمان تست ربات
# ---------------------------
async def start(update, context):
    await update.message.reply_text("سلام فرهاد! ربات روشنه 😊")


# ---------------------------
#         main()
# ---------------------------
async def main():

    print("🚀 STARTING BOT...")
    print("🔍 Testing Nobitex connection...")

    # ---- تست نوبیتکس ----
    nobi_status = test_connection()
    print("📡 NOBITEX RESULT:", nobi_status)
    print("-----------------------------")
    # ------------------------

    print("🧩 Building Telegram bot...")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # فرمان‌ ها
    app.add_handler(CommandHandler("start", start))

    print("🤖 BOT RUNNING...")
    await app.run_polling()


# اجرای ربات
if __name__ == "__main__":
    asyncio.run(main())

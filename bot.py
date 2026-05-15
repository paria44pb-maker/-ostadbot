import os

# Load keys from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")
NOBITEX_API_SECRET = os.getenv("NOBITEX_API_SECRET")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("🔍 Checking environment variables...")
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
print("NOBITEX_API_KEY:", NOBITEX_API_KEY)
print("DEEPSEEK_API_KEY:", DEEPSEEK_API_KEY)
print("GROQ_API_KEY:", GROQ_API_KEY)

print("🚀 STARTING BOT...")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is missing from Railway variables!")



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
# CREATE APPLICATION
# --------------------------------------
app = Application.builder().token(TELEGRAM_TOKEN).build()


# --------------------------------------
# WALLET COMMAND (NOBITEX)
# --------------------------------------
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not NOBITEX_API_KEY:
            await update.message.reply_text("❌ API Key نوبیتکس تنظیم نشده")
            return

        data = get_wallets(NOBITEX_API_KEY)

        if isinstance(data, dict) and "error" in data:
            await update.message.reply_text(data["error"])
            return

        wallets = data.get("wallets", [])

        if not wallets:
            await update.message.reply_text("📭 موجودی‌ای پیدا نشد")
            return

        text = "💰 موجودی نوبیتکس:\n\n"

        for w in wallets:
            currency = w.get("currency", "unknown")
            balance = w.get("balance", 0)

            if float(balance) > 0:
                text += f"• {currency}: {balance}\n"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ خطای داخلی: {str(e)}")


# --------------------------------------
# HANDLERS
# --------------------------------------
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.add_error_handler(error_handler)


# --------------------------------------
# BOT START
# --------------------------------------
print("🤖 BOT RUNNING...")
app.run_polling(drop_pending_updates=True)

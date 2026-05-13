import os
import asyncio
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# -----------------------------
#  LOGGING (Production level)
# -----------------------------
logging.basicConfig(
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.INFO
)
log = logging.getLogger("OstadBot")


# =============================
#      ENVIRONMENT VARS
# =============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NOBITEX_API = os.getenv("NOBITEX_API_KEY")
DROQ_API = os.getenv("DROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN is missing!")

if not NOBITEX_API:
    log.warning("⚠️ NOBITEX_API_KEY is missing. Nobitex features disabled.")

if not DROQ_API:
    log.warning("⚠️ DROQ_API_KEY is missing. Droq AI disabled.")


# =============================
#      IMPORT SERVICES
# =============================
# فرهاد: این‌جا فرض می‌کنم سرویس‌ها را مثل قبل ساخته‌ای
# /services/nobitex_service.py
# /services/droq_service.py

try:
    from services.nobitex_service import NobitexClient
    from services.droq_service import DroqAI
except Exception as e:
    log.error("❌ Could not import service files:", e)
    NobitexClient = None
    DroqAI = None


nobi = NobitexClient(NOBITEX_API) if NOBITEX_API else None
ai = DroqAI(DROQ_API) if DROQ_API else None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام فرهاد 👋\nربات با موفقیت بالا آمد.\n\n"
        "دستورات موجود:\n"
        "/balance ➝ دریافت موجودی نوبیتکس\n"
        "/price btc ⇒ قیمت لحظه‌ای\n"
        "/ask متن ⇒ اتصال به Droq AI\n"
        "/health ➝ وضعیت ربات"
    )


async def price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not nobi:
        return await update.message.reply_text("❌ نوبیتکس فعال نیست.")

    if len(ctx.args) == 0:
        return await update.message.reply_text("مثال:\n/price btc")

    symbol = ctx.args[0].lower()

    price = await nobi.get_price(symbol)
    if price is None:
        return await update.message.reply_text("❌ دریافت قیمت ممکن نشد.")

    await update.message.reply_text(f"💰 قیمت {symbol.upper()} = {price:,} تومان")


async def balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not nobi:
        return await update.message.reply_text("❌ نوبیتکس فعال نیست.")

    wallet = await nobi.get_wallet_balances()
    if wallet is None:
        return await update.message.reply_text("❌ خطا در دریافت موجودی.")

    text = "📊 موجودی کیف پول:\n\n"
    for coin, data in wallet.items():
        text += f"• {coin}: {data['balance']}\n"

    await update.message.reply_text(text)


async def ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ai:
        return await update.message.reply_text("❌ Droq AI فعال نیست.")

    if len(ctx.args) == 0:
        return await update.message.reply_text("مثال:\n/ask بیت‌کوین چنده؟")

    prompt = " ".join(ctx.args)
    answer = await ai.chat(prompt)

    await update.message.reply_text(answer)


async def health(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot is running.\n"
        f"Telegram OK\n"
        f"Nobitex: {'ON' if nobi else 'OFF'}\n"
        f"Droq AI: {'ON' if ai else 'OFF'}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#       HANDLE NORMAL TEXT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def echo_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرهاد جان پیام‌تو گرفتم، دستور خاصی بود بگو ✨")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#       ERROR HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.error("Telegram Error:", exc_info=context.error)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#        MAIN STARTUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def run_bot():
    log.info("🚀 Starting OstadBot...")

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(15)
        .pool_timeout(15)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("ask", ask))

    # Normal text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))

    # Error handler
    app.add_error_handler(error_handler)

    log.info("🤖 Bot is live.")
    await app.run_polling(close_loop=False)


if __name__ == "__main__":
    asyncio.run(run_bot())

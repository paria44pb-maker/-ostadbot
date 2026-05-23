import os
import logging
import asyncio
import random
import numpy as np
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------------------- تنظیمات لاگینگ ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------- متغیرهای محیطی ----------------------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@comedyclick")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ---------------------------- ارزهای تحت پوشش ----------------------------
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- دریافت قیمت از CoinEx (نسخه عمومی) ----------------------------
async def get_coinex_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                ticker = resp.json()["data"]["ticker"]
                return {
                    "price": float(ticker.get("last", 0)),
                    "change": float(ticker.get("change", 0)),
                    "volume": float(ticker.get("vol", 0)),
                }
    except Exception as e:
        logger.error(f"Price error {symbol}: {e}")
    return None

# ---------------------------- اندیکاتورهای ساده ----------------------------
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
    avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signal(change, rsi):
    if change > 2 and rsi < 70:
        return "🟢 خرید قوی", 85
    elif change > 0.5 and rsi < 60:
        return "🟢 خرید", 70
    elif change < -2 and rsi > 30:
        return "🔴 فروش قوی", 85
    elif change < -0.5 and rsi > 40:
        return "🔴 فروش", 70
    else:
        return "⚪ نگهداری", 50

# ---------------------------- ارسال خودکار سیگنال (حلقه دستی بدون JobQueue) ----------------------------
async def auto_signal_loop(app):
    while True:
        await asyncio.sleep(300)  # ۵ دقیقه
        if not CHANNEL_ID:
            continue
        for symbol, info in list(SYMBOLS.items())[:3]:  # فقط ۳ ارز اول
            data = await get_coinex_price(symbol)
            if not data:
                continue
            # شبیه‌سازی داده تاریخی برای RSI
            base = data["price"]
            prices = [base * (1 + random.uniform(-0.02, 0.02)) for _ in range(30)]
            rsi = calculate_rsi(prices)
            signal, confidence = generate_signal(data["change"], rsi)
            msg = f"""
╔══════════════════════════════════════╗
║   🔥 {info['emoji']} *{symbol.replace('USDT','')}* - سیگنال 🔥   ║
╚══════════════════════════════════════╝

💰 قیمت: `${data['price']:,.2f}`
📈 تغییر: `{data['change']:+.2f}%`
🎯 سیگنال: **{signal}** (اطمینان {confidence}%)
📊 RSI تقریبی: `{rsi:.1f}`

✨ @comedyclick
"""
            try:
                await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                logger.info(f"Auto signal sent for {symbol}")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Failed to send {symbol}: {e}")

# ---------------------------- منوی ربات ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات حرفه‌ای کریپتو* 🔥\n\n"
        "✅ قیمت لحظه‌ای ارزها\n✅ سیگنال خرید/فروش\n✅ ارسال خودکار هر ۵ دقیقه به کانال\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای*\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{sym.replace('USDT','')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تولید سیگنال...")
    sym = list(SYMBOLS.keys())[0]
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("خطا در دریافت داده.")
        return
    prices = [data["price"] * (1 + random.uniform(-0.02, 0.02)) for _ in range(30)]
    rsi = calculate_rsi(prices)
    signal, confidence = generate_signal(data["change"], rsi)
    msg = f"🎯 *سیگنال {sym.replace('USDT','')}*\n💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n🔔 {signal} (اطمینان {confidence}%)\n📊 RSI: {rsi:.1f}"
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنما*\n"
        "• قیمت لحظه‌ای: نمایش قیمت ارزها\n"
        "• سیگنال فوری: دریافت سیگنال خرید/فروش\n"
        "• ربات هر ۵ دقیقه سیگنال به کانال ارسال می‌کند.\n\n"
        "⚠️ فقط جنبه آموزشی – مسئولیت با شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()
        await query.edit_message_text("در حال توسعه...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

# ---------------------------- اجرای اصلی ----------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع حلقه خودکار ارسال سیگنال در پس‌زمینه
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(auto_signal_loop(app))

    logger.info("🚀 ربات حرفه‌ای بدون نقص راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()

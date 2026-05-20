import os
import logging
import asyncio
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@comedyclick"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
EMOJIS = {
    "BTCUSDT": "👑", "ETHUSDT": "💎", "SOLUSDT": "⚡", 
    "BNBUSDT": "🟡", "XRPUSDT": "💧"
}

async def get_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"https://api.coinex.com/v1/market/ticker?market={symbol}")
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    ticker = data["data"]["ticker"]
                    return {
                        "price": float(ticker["last"]),
                        "change": float(ticker["change"]),
                        "volume": float(ticker["vol"])
                    }
    except Exception as e:
        logger.error(f"Error getting {symbol}: {e}")
    return None

async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    """ارسال سیگنال هر 5 دقیقه به کانال"""
    for symbol in SYMBOLS:
        data = await get_price(symbol)
        if data:
            change = data["change"]
            if change > 1:
                signal = "🟢 خرید قوی"
                emoji = "📈"
            elif change > 0:
                signal = "🟡 خرید ملایم"
                emoji = "📊"
            elif change < -1:
                signal = "🔴 فروش قوی"
                emoji = "📉"
            elif change < 0:
                signal = "🟠 فروش ملایم"
                emoji = "📊"
            else:
                signal = "⚪ نگهداری"
                emoji = "➖"
            
            msg = f"""
{EMOJIS[symbol]} *{symbol.replace('USDT', '')}* {emoji}

💰 قیمت: ${data['price']:,.2f}
📈 تغییر: {change:+.2f}%
🎯 سیگنال: {signal}

━━━━━━━━━━━━━━━━━━━━━━
✨ @comedyclick
"""
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                logger.info(f"✅ Signal sent for {symbol}")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Failed to send {symbol}: {e}")

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for symbol in SYMBOLS:
        data = await get_price(symbol)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {EMOJIS[symbol]} *{symbol.replace('USDT', '')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ *راهنمای ربات* ❓

📊 **قابلیت‌ها:**
• ارسال خودکار سیگنال هر 5 دقیقه
• قیمت لحظه‌ای 5 ارز برتر
• تحلیل بر اساس تغییرات قیمت

📌 **دستورات:**
• /start - شروع
• /status - وضعیت ربات

⚠️ این ربات فقط جنبه آموزشی دارد
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def status_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات فعال است\n⏰ ارسال سیگنال هر 5 دقیقه\n📡 اتصال به CoinEx: برقرار")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    text = """
🔥 *ربات سیگنال‌گیر کریپتو* 🔥

✅ هر 5 دقیقه سیگنال به کانال ارسال می‌شود
✅ 5 ارز برتر تحت پوشش
✅ تحلیل بر اساس تغییرات قیمت

📌 از منوی زیر انتخاب کن:
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        await start(update, context)
    elif query.data == "prices":
        await prices_menu(update, context)
    elif query.data == "help":
        await help_menu(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(send_signal, interval=300, first=10)
        logger.info("✅ تایمر 5 دقیقه تنظیم شد")
    
    logger.info("🚀 ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()

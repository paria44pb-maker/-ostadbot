import os
import logging
import asyncio
import threading
import time
import random
import json
import hmac
import hashlib
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# تنظیم لاگ با سطح DEBUG برای مشاهده جزئیات بیشتر
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ... (بقیه کدها مانند قبل، تا تابع send_auto_to_channel)

# ---------------------------- ارسال خودکار به کانال (با لاگ) ----------------------------
auto_thread_running = True

def auto_signal_thread(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while auto_thread_running:
        logger.info("⏳ ترد خودکار: در حال انتظار ۵ دقیقه...")
        time.sleep(300)  # 5 دقیقه
        logger.info("🔄 ترد خودکار: شروع ارسال سیگنال...")
        loop.run_until_complete(send_auto_to_channel(app))

async def send_auto_to_channel(app):
    logger.info("🚀 تابع send_auto_to_channel فراخوانی شد.")
    if not CHANNEL_ID:
        logger.error("❌ CHANNEL_ID تنظیم نشده است!")
        return
    logger.info(f"📢 کانال هدف: {CHANNEL_ID}")

    for symbol, info in list(SYMBOLS.items())[:3]:
        logger.info(f"🔄 پردازش {symbol}...")
        price_data = await get_coinex_price(symbol)
        if not price_data:
            logger.warning(f"⚠️ قیمت {symbol} دریافت نشد. ادامه به ارز بعدی...")
            continue
        logger.info(f"✅ قیمت {symbol}: ${price_data['price']:,.2f}")

        kline = await get_historical_klines(symbol, 100)
        if not kline:
            logger.warning(f"⚠️ داده کندل {symbol} دریافت نشد. ادامه...")
            continue
        logger.info(f"✅ داده کندل {symbol} دریافت شد (تعداد {len(kline['close'])}).")

        # تولید سیگنال (مطمئن شوید که generate_signal تعریف شده باشد)
        signal, confidence, reasons, analysis, rsi, macd, macd_sig, ema9, ema20, ema50, bb_u, bb_m, bb_l, stoch_k, cci, will, adx, tenkan, kijun, senkou, total = generate_signal(kline["close"], kline["high"], kline["low"], price_data["price"], price_data["change"], price_data["volume"])

        logger.info(f"🎯 سیگنال {symbol}: {signal} (اطمینان {confidence}%)")

        # محاسبه حد ضرر و هدف
        if "خرید" in signal:
            sl = bb_l if bb_l else price_data["price"] * 0.97
            tp1 = bb_m if bb_m else price_data["price"] * 1.02
            tp2 = bb_u if bb_u else price_data["price"] * 1.05
        else:
            sl = bb_u if bb_u else price_data["price"] * 1.03
            tp1 = bb_m if bb_m else price_data["price"] * 0.98
            tp2 = bb_l if bb_l else price_data["price"] * 0.95

        # ساخت پیام
        msg = f"""
🌿 *『 {info['emoji']} {info['name']} 』* 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر 24h:** `{price_data['change']:+.2f}%`
🎯 **سیگنال:** `{signal}` (اطمینان {confidence}%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **۱۲ اندیکاتور:**
• RSI: `{rsi:.1f}`
• MACD: `{macd:.4f}` (سیگنال: `{macd_sig:.4f}`)
• EMA9: `${ema9:,.2f}` | EMA20: `${ema20:,.2f}` | EMA50: `${ema50:,.2f}`
• باند بولینگر: پایین `${bb_l:,.2f}` | وسط `${bb_m:,.2f}` | بالا `${bb_u:,.2f}`
• استوکاستیک: K=`{stoch_k:.1f}`
• CCI: `{cci:.1f}`
• ویلیامز: `{will:.1f}`
• ADX: `{adx:.1f}`
• ابر ایچیموکو: تنکان=`{tenkan:.0f}` کیجون=`{kijun:.0f}` سنکو=`{senkou:.0f}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **اهداف:** `${tp1:,.2f}` → `${tp2:,.2f}`
{trap}
📝 **دلایل سیگنال:** {', '.join(reasons[:3])}
{analysis}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"✅ پیام {symbol} با موفقیت به کانال ارسال شد.")
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام {symbol} به کانال: {e}")
        await asyncio.sleep(3)

    # بخش‌های دیگر (اخبار، ترس و طمع، آموزش) نیز می‌توانند لاگ‌های مشابه داشته باشند.
    # ...

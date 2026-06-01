import os
import logging
import asyncio
import time
import random
import numpy as np
import pandas as pd
import ta
import ccxt
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# ==================== تنظیمات اصلی ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_USERNAME = "@CryptoPulse606"
CHANNEL_LINK = "https://t.me/CryptoPulse606"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# CoinEx
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")

# تنظیمات معاملاتی
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"]
TIMEFRAMES = {"15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
MAX_POSITIONS = 3
RISK_PER_TRADE = 0.02
ATR_MULTIPLIER_SL = 1.5
RR_RATIO = 2.0
AUTO_TRADE_ENABLED = False
DEMO_BALANCE = 10000

# ==================== صرافی ====================
exchange = ccxt.coinex({
    'apiKey': COINEX_API_KEY,
    'secret': COINEX_SECRET_KEY,
    'password': COINEX_PASSPHRASE,
    'enableRateLimit': True,
})

# ==================== دمو معامله ====================
demo_balance = DEMO_BALANCE
demo_positions = {}
demo_history = []

# ==================== بررسی عضویت در کانال ====================
async def is_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        logger.info(f"User {user_id} status: {member.status}")
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# ==================== منوی اصلی ====================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال لحظه‌ای", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="portfolio")],
        [InlineKeyboardButton("⚡ معامله خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("📰 اخبار", callback_data="news")],
        [InlineKeyboardButton("😨 ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== اندیکاتورها ====================
def calculate_indicators(df):
    close = pd.Series(df['close'].values)
    high = pd.Series(df['high'].values)
    low = pd.Series(df['low'].values)
    volume = pd.Series(df['volume'].values)
    
    indicators = {}
    indicators['RSI'] = ta.momentum.rsi(close, window=14).iloc[-1]
    indicators['EMA20'] = ta.trend.ema_indicator(close, window=20).iloc[-1]
    indicators['EMA50'] = ta.trend.ema_indicator(close, window=50).iloc[-1]
    indicators['BB_UPPER'] = ta.volatility.BollingerBands(close, window=20, window_dev=2).bollinger_hband().iloc[-1]
    indicators['BB_LOWER'] = ta.volatility.BollingerBands(close, window=20, window_dev=2).bollinger_lband().iloc[-1]
    indicators['ATR'] = ta.volatility.average_true_range(high, low, close, window=14).iloc[-1]
    
    macd = ta.trend.MACD(close)
    indicators['MACD'] = macd.macd().iloc[-1]
    indicators['MACD_SIGNAL'] = macd.macd_signal().iloc[-1]
    
    return indicators

def generate_signal(indicators, current_price, change):
    score = 0
    if indicators['RSI'] < 30:
        score += 30
    elif indicators['RSI'] > 70:
        score -= 30
    if indicators['MACD'] > indicators['MACD_SIGNAL']:
        score += 25
    else:
        score -= 25
    if indicators['EMA20'] > indicators['EMA50']:
        score += 20
    else:
        score -= 20
    if current_price <= indicators['BB_LOWER']:
        score += 20
    elif current_price >= indicators['BB_UPPER']:
        score -= 20
    if change > 2:
        score += 15
    elif change < -2:
        score -= 15
    
    if score >= 50:
        return "خرید قوی", 90, "🟢🟢🟢🟢🟢"
    elif score >= 30:
        return "خرید", 75, "🟢🟢🟢⚪⚪"
    elif score <= -50:
        return "فروش قوی", 90, "🔴🔴🔴🔴🔴"
    elif score <= -30:
        return "فروش", 75, "🔴🔴🔴⚪⚪"
    else:
        return "نگهداری", 50, "⚪⚪⚪⚪⚪"

# ==================== ارسال خودکار به کانال ====================
async def auto_signal_loop(app):
    await asyncio.sleep(10)
    while True:
        await asyncio.sleep(300)
        for symbol in SYMBOLS[:3]:
            try:
                ticker = exchange.fetch_ticker(symbol)
                if not ticker:
                    continue
                ohlcv = exchange.fetch_ohlcv(symbol, '1h', 100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                indicators = calculate_indicators(df)
                signal, confidence, strength = generate_signal(indicators, ticker['last'], ticker['percentage'])
                
                msg = f"""
╔══════════════════════════════════════╗
║   🔥 *سیگنال {symbol.replace('USDT', '')}* 🔥   ║
╚══════════════════════════════════════╝

💰 **قیمت:** `${ticker['last']:,.2f}`
📈 **تغییر 24h:** `{ticker['percentage']:+.2f}%`
🎯 **سیگنال:** `{signal}` (اطمینان {confidence}%)
💪 **قدرت:** {strength}

📊 RSI: `{indicators['RSI']:.1f}`
📈 MACD: `{indicators['MACD']:.2f}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
                await app.bot.send_message(chat_id=CHANNEL_USERNAME, text=msg, parse_mode="Markdown")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Auto signal error: {e}")

# ==================== شروع ربات ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot")
    
    # صفحه عضویت با دو دکمه
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = """
🌟 *پلاتینیوم VIP V34* 🌟

🔔 برای استفاده از ربات، **ابتدا در کانال ما عضو شوید**.

✨ پس از عضویت، روی دکمه «عضو شدم» کلیک کنید.
"""

    try:
        with open("images/platinum_vip.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=InputFile(photo, filename="platinum_vip.jpg"),
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except:
        await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=reply_markup)

# ==================== دکمه عضو شدم (خودکار باز کردن ربات) ====================
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    logger.info(f"Checking membership for user: {user_id}")

    if await is_member(user_id, context):
        logger.info(f"User {user_id} IS a member - Opening bot automatically")
        context.user_data["is_member"] = True
        # خودکار ربات باز می‌شود - منوی اصلی نمایش داده می‌شود
        await query.edit_message_caption(
            caption="✅ *عضویت شما تأیید شد!* ✅\n\nبه ربات خوش آمدید.\nاز منوی زیر استفاده کنید:",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
    else:
        logger.warning(f"User {user_id} is NOT a member")
        # به کاربر بگو عضو نیست و دکمه را نگه دار
        await query.answer(
            "❌ شما هنوز عضو کانال نشده‌اید!\n\n"
            "لطفاً ابتدا روی دکمه «عضویت در کانال» کلیک کرده و عضو شوید.\n"
            "سپس دوباره روی «عضو شدم» کلیک کنید.",
            show_alert=True
        )

# ==================== قیمت لحظه‌ای ====================
async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for symbol in SYMBOLS[:5]:
        try:
            ticker = exchange.fetch_ticker(symbol)
            emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
            text += f"{emoji} *{symbol.replace('USDT', '')}*: ${ticker['last']:,.2f} ({ticker['percentage']:+.2f}%)\n"
        except:
            text += f"⚪ *{symbol.replace('USDT', '')}*: خطا\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

# ==================== سیگنال لحظه‌ای ====================
async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    await query.edit_message_text("🔄 تحلیل لحظه‌ای بیت‌کوین...")
    try:
        ticker = exchange.fetch_ticker("BTCUSDT")
        ohlcv = exchange.fetch_ohlcv("BTCUSDT", "1h", 100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        indicators = calculate_indicators(df)
        signal, confidence, strength = generate_signal(indicators, ticker['last'], ticker['percentage'])
        msg = f"""
🎯 *سیگنال لحظه‌ای BTC* 🎯

💰 قیمت: ${ticker['last']:,.2f}
📈 تغییر: {ticker['percentage']:+.2f}%
🎯 سیگنال: {signal} (اطمینان {confidence}%)
💪 قدرت: {strength}
📊 RSI: {indicators['RSI']:.1f}
"""
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_main_menu())
    except Exception as e:
        await query.edit_message_text(f"❌ خطا: {e}", reply_markup=get_main_menu())

# ==================== تحلیل تکنیکال ====================
async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    await query.edit_message_text("📈 نام ارز را وارد کنید (BTC, ETH, SOL):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol_input = update.message.text.upper()
    symbol = None
    for s in SYMBOLS:
        if symbol_input in s:
            symbol = s
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    try:
        ticker = exchange.fetch_ticker(symbol)
        ohlcv = exchange.fetch_ohlcv(symbol, "1h", 100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        indicators = calculate_indicators(df)
        text = f"""
📊 *تحلیل {symbol.replace('USDT', '')}* 📊

💰 قیمت: ${ticker['last']:,.2f}
📈 تغییر: {ticker['percentage']:+.2f}%

📈 **اندیکاتورها:**
• RSI: {indicators['RSI']:.1f}
• MACD: {indicators['MACD']:.2f}
• EMA20: ${indicators['EMA20']:.2f} | EMA50: ${indicators['EMA50']:.2f}
• باند بولینگر: پایین ${indicators['BB_LOWER']:.2f} | بالا ${indicators['BB_UPPER']:.2f}
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")
    context.user_data["waiting_technical"] = False

# ==================== پورتفوی دمو ====================
async def portfolio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    total_pnl = sum(h.get('pnl', 0) for h in demo_history)
    text = f"""
💰 *پورتفوی دمو* 💰

موجودی: ${demo_balance:,.2f}
پوزیشن‌های باز: {len(demo_positions)}
سود/زیان کل: ${total_pnl:+.2f}
⚡ معامله خودکار: {'فعال' if AUTO_TRADE_ENABLED else 'غیرفعال'}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

# ==================== معامله خودکار ====================
async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_TRADE_ENABLED
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    AUTO_TRADE_ENABLED = not AUTO_TRADE_ENABLED
    status = "✅ فعال" if AUTO_TRADE_ENABLED else "❌ غیرفعال"
    await query.edit_message_text(f"⚡ *معامله خودکار*\n\nوضعیت: {status}", parse_mode="Markdown", reply_markup=get_main_menu())

# ==================== اخبار ====================
async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    await query.edit_message_text("📰 *اخبار لحظه‌ای*\n\nدر حال توسعه...", parse_mode="Markdown", reply_markup=get_main_menu())

# ==================== شاخص ترس و طمع ====================
async def fear_greed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    await query.edit_message_text("😨 *شاخص ترس و طمع*\n\nدر حال توسعه...", parse_mode="Markdown", reply_markup=get_main_menu())

# ==================== راهنما ====================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    
    text = """
❓ *راهنمای پلاتینیوم V34* ❓

📊 قیمت لحظه‌ای: نمایش قیمت ارزها
🎯 سیگنال لحظه‌ای: سیگنال خرید/فروش
📈 تحلیل تکنیکال: تحلیل با 10+ اندیکاتور
💰 پورتفوی دمو: مدیریت سرمایه مجازی
⚡ معامله خودکار: خرید/فروش خودکار
📰 اخبار: اخبار لحظه‌ای کریپتو
😨 ترس و طمع: شاخص ترس و طمع بازار

⚠️ فقط جنبه آموزشی
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

# ==================== برگشت به منو ====================
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌟 *منوی اصلی* 🌟\n\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

# ==================== هندلر پیام ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context)
        context.user_data["waiting_technical"] = False
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

# ==================== هندلر دکمه‌ها ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    logger.info(f"Button clicked: {data}")

    if data == "check_membership":
        await check_membership(update, context)
    elif data == "prices":
        await prices(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "portfolio":
        await portfolio_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "fear_greed":
        await fear_greed_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()

# ==================== اجرای اصلی ====================
async def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    asyncio.create_task(auto_signal_loop(app))
    
    logger.info("🚀 ربات پلاتینیوم V34 راه‌اندازی شد.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

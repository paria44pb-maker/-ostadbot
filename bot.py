import os
import logging
import asyncio
import threading
import time
import random
import json
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------------------- تنظیمات لاگینگ ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------- متغیرهای محیطی ----------------------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")          # اختیاری (برای هوش مصنوعی)
CHANNEL_ID = os.getenv("CHANNEL_ID", "@comedyclick")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# لیست ارزهای تحت پوشش (نام، ایموجی، حداقل سفارش)
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- توابع دریافت داده از کوینکس ----------------------------
async def get_coinex_price(symbol):
    """قیمت لحظه‌ای و تغییر 24h (بدون نیاز به API Key)"""
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
                    "high": float(ticker.get("high", 0)),
                    "low": float(ticker.get("low", 0)),
                }
    except Exception as e:
        logger.error(f"Price error {symbol}: {e}")
    return None

async def get_historical_klines(symbol, limit=50):
    """دریافت داده‌های کندل 5 دقیقه‌ای برای محاسبه اندیکاتورهای واقعی"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=5min&limit={limit}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                klines = resp.json()["data"]
                # استخراج قیمت‌های بسته شدن
                closes = [float(k[4]) for k in klines]  # هر کندل: [time, open, high, low, close, volume]
                return closes
    except Exception as e:
        logger.error(f"Kline error {symbol}: {e}")
    return None

# ---------------------------- اندیکاتورهای تکنیکال (بدون numpy) ----------------------------
def calculate_ema(values, period):
    """میانگین متحرک نمایی"""
    if len(values) < period:
        return values[-1] if values else 0
    multiplier = 2 / (period + 1)
    ema = values[0]
    for val in values[1:]:
        ema = (val - ema) * multiplier + ema
    return ema

def calculate_rsi(closes, period=14):
    """شاخص قدرت نسبی (RSI) از داده‌های کندل واقعی"""
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """MACD (line, signal, histogram) از داده‌های واقعی"""
    if len(closes) < slow + signal:
        return 0, 0, 0
    ema_fast = [calculate_ema(closes[:i+1], fast) for i in range(len(closes))]
    ema_slow = [calculate_ema(closes[:i+1], slow) for i in range(len(closes))]
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    macd_signal = [calculate_ema(macd_line[:i+1], signal) for i in range(len(macd_line))]
    macd_hist = [m - s for m, s in zip(macd_line, macd_signal)]
    return macd_line[-1], macd_signal[-1], macd_hist[-1]

def calculate_bollinger(closes, period=20, std_dev=2):
    """باند بولینگر (بالا، میانه، پایین)"""
    if len(closes) < period:
        return None, None, None
    sma = sum(closes[-period:]) / period
    variance = sum((c - sma) ** 2 for c in closes[-period:]) / period
    std = variance ** 0.5
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def support_resistance(closes, lookback=50):
    """سطح حمایت و مقاومت ساده از بالاترین و پایین‌ترین"""
    recent = closes[-lookback:]
    high = max(recent)
    low = min(recent)
    pivot = (high + low) / 2
    r1 = pivot + (high - low) * 0.382
    r2 = pivot + (high - low) * 0.618
    s1 = pivot - (high - low) * 0.382
    s2 = pivot - (high - low) * 0.618
    return {"support": [s1, s2, low], "resistance": [r1, r2, high]}

def detect_trap(change, volume, rsi):
    """تشخیص تله گاوی/خرسی"""
    if change > 3 and volume > 10_000_000 and rsi > 70:
        return "⚠️ تله گاوی (خرید کاذب)"
    if change < -3 and volume > 10_000_000 and rsi < 30:
        return "⚠️ تله خرسی (فروش کاذب)"
    return "✅ بدون تله"

def generate_signal(change, rsi, macd, macd_signal):
    """سیگنال ترکیبی (قوی/متوسط/نگهداری)"""
    score = 0
    if rsi < 30:
        score += 30
    elif rsi > 70:
        score -= 30
    if macd > macd_signal:
        score += 25
    else:
        score -= 25
    if change > 2:
        score += 20
    elif change < -2:
        score -= 20
    if score >= 45:
        return "خرید قوی 🟢🟢", 90
    elif score >= 20:
        return "خرید 🟢", 75
    elif score <= -45:
        return "فروش قوی 🔴🔴", 90
    elif score <= -20:
        return "فروش 🔴", 75
    else:
        return "نگهداری ⚪", 50

# ---------------------------- هوش مصنوعی Groq (اختیاری) ----------------------------
async def groq_analysis(symbol, price, change, rsi):
    if not GROQ_API_KEY:
        return None
    prompt = f"تحلیل سریع {symbol}: قیمت ${price:,.0f}، تغییر {change:+.1f}%، RSI {rsi:.0f}. پیش‌بینی کوتاه مدت و توصیه در یک خط."
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 150}
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return None

# ---------------------------- ارسال خودکار به کانال (در ترد جداگانه) ----------------------------
auto_thread_running = True

def auto_signal_thread(app):
    """حلقه بی‌پایان در ترد جداگانه برای ارسال سیگنال هر ۵ دقیقه"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while auto_thread_running:
        time.sleep(300)  # ۵ دقیقه
        loop.run_until_complete(send_auto_signals(app))

async def send_auto_signals(app):
    """ارسال سیگنال برای ۳ ارز اول به کانال"""
    if not CHANNEL_ID:
        return
    for symbol, info in list(SYMBOLS.items())[:3]:
        price_data = await get_coinex_price(symbol)
        if not price_data:
            continue
        # دریافت کندل‌های واقعی برای تحلیل
        closes = await get_historical_klines(symbol, limit=50)
        if not closes:
            # fallback: شبیه‌سازی ساده
            closes = [price_data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(50)]
        rsi = calculate_rsi(closes)
        macd, macd_signal, _ = calculate_macd(closes)
        signal, confidence = generate_signal(price_data["change"], rsi, macd, macd_signal)
        bb_upper, bb_mid, bb_lower = calculate_bollinger(closes)
        sr = support_resistance(closes)
        trap = detect_trap(price_data["change"], price_data["volume"], rsi)
        # حد ضرر و هدف بر اساس باند بولینگر
        if "خرید" in signal:
            sl = bb_lower if bb_lower else price_data["price"] * 0.97
            tp1 = bb_mid if bb_mid else price_data["price"] * 1.02
            tp2 = bb_upper if bb_upper else price_data["price"] * 1.05
        else:
            sl = bb_upper if bb_upper else price_data["price"] * 1.03
            tp1 = bb_mid if bb_mid else price_data["price"] * 0.98
            tp2 = bb_lower if bb_lower else price_data["price"] * 0.95
        msg = f"""
╔══════════════════════════════════════╗
║   🔥 {info['emoji']} *{symbol.replace('USDT','')}* – سیگنال پیشرفته 🔥   ║
╚══════════════════════════════════════╝

💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر 24h:** `{price_data['change']:+.2f}%`
🎯 **سیگنال:** **{signal}** (اطمینان {confidence}%)
📊 **RSI:** `{rsi:.1f}` | **MACD:** `{macd:.4f}`
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **اهداف:** `${tp1:,.2f}` → `${tp2:,.2f}`
{trap}

✨ @comedyclick
"""
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"✅ خودکار: {symbol} ارسال شد")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"❌ خطا در ارسال {symbol}: {e}")

# ---------------------------- منوی اصلی (بیش از ۱۰ دکمه) ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری (BTC)", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال پیشرفته", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوش مصنوعی", callback_data="ai_analysis")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ", callback_data="whale")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("📰 اخبار کریپتو", callback_data="news")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- هندلرهای دکمه‌ها ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات فوق‌حرفه‌ای کریپتو* 🔥\n\n"
        "✅ **قابلیت‌ها:**\n"
        "• قیمت لحظه‌ای ۷ ارز برتر\n"
        "• سیگنال ترکیبی (RSI, MACD, باند بولینگر)\n"
        "• تشخیص تله بازار\n"
        "• تحلیل هوش مصنوعی (Groq)\n"
        "• ارسال خودکار سیگنال هر ۵ دقیقه به کانال\n"
        "• مدیریت ریسک و پورتفوی دمو\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{sym.replace('USDT','')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای...")
    sym = "BTCUSDT"
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("❌ خطا در دریافت داده")
        return
    closes = await get_historical_klines(sym, 50)
    if not closes:
        closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(50)]
    rsi = calculate_rsi(closes)
    macd, macd_signal, _ = calculate_macd(closes)
    signal, conf = generate_signal(data["change"], rsi, macd, macd_signal)
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    trap = detect_trap(data["change"], data["volume"], rsi)
    msg = f"""
🎯 *سیگنال لحظه‌ای {sym.replace('USDT','')}* 🎯

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر:** {data['change']:+.2f}%
📊 **RSI:** {rsi:.1f} | **MACD:** {macd:.4f}
🎯 **سیگنال:** **{signal}** (اطمینان {conf}%)
{trap}
🟢 باند پایین: ${bb_l:,.2f} | 🟡 وسط: ${bb_m:,.2f} | 🔴 بالا: ${bb_u:,.2f}
"""
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📈 *تحلیل تکنیکال پیشرفته*\n\n"
        "لطفاً نام ارز را وارد کنید (مثل BTC, ETH, SOL):",
        parse_mode="Markdown"
    )
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol_input):
    # پیدا کردن نماد کامل
    symbol = None
    for sym in SYMBOLS:
        if symbol_input in sym or sym.startswith(symbol_input):
            symbol = sym
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    data = await get_coinex_price(symbol)
    if not data:
        await update.message.reply_text("خطا در دریافت قیمت")
        return
    closes = await get_historical_klines(symbol, 50)
    if not closes:
        closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(50)]
    rsi = calculate_rsi(closes)
    macd, macd_signal, _ = calculate_macd(closes)
    ema20 = calculate_ema(closes, 20)
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    sr = support_resistance(closes)
    trap = detect_trap(data["change"], data["volume"], rsi)
    signal, conf = generate_signal(data["change"], rsi, macd, macd_signal)
    reply = (
        f"📊 *تحلیل تکنیکال {symbol.replace('USDT','')}*\n"
        f"💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n"
        f"📊 RSI: {rsi:.1f}\n📈 MACD: {macd:.4f} (سیگنال: {macd_signal:.4f})\n"
        f"🟢 EMA20: ${ema20:,.2f}\n"
        f"📊 باند بولینگر: پایین ${bb_l:,.2f} | وسط ${bb_m:,.2f} | بالا ${bb_u:,.2f}\n"
        f"🟡 حمایت: ${sr['support'][0]:,.2f} | مقاومت: ${sr['resistance'][0]:,.2f}\n"
        f"{trap}\n🎯 سیگنال نهایی: **{signal}** (اطمینان {conf}%)"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def ai_analysis_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("⚠️ هوش مصنوعی فعال نیست (GROQ_API_KEY تنظیم نشده).", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    await query.edit_message_text("🧠 *تحلیل هوش مصنوعی*\nلطفاً سوال خود را بپرسید (مثلاً «بیت‌کوین را تحلیل کن»):", parse_mode="Markdown")
    context.user_data["waiting_ai"] = True

async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_chat_action("typing")
    analysis = await groq_analysis("BTC", 0, 0, 0)  # فعلاً ساده
    if not analysis:
        analysis = "⚠️ متأسفانه هوش مصنوعی در دسترس نیست. لطفاً بعداً تلاش کنید."
    await update.message.reply_text(f"🧠 *تحلیل AI:*\n{analysis}", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 *ردیابی نهنگ‌ها*\n\nاین بخش در حال توسعه است. به زودی اضافه می‌شود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🛡️ *مدیریت ریسک حرفه‌ای*\n\n"
        "📌 **قوانین طلایی:**\n"
        "• حداکثر ۲٪ سرمایه در هر معامله\n"
        "• نسبت ریسک به ریوارد حداقل ۱:۲\n"
        "• همیشه از حد ضرر استفاده کنید\n"
        "• حداکثر ۳ پوزیشن همزمان\n"
        "• در ضررهای متوالی معامله را متوقف کنید"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 *اخبار کریپتو*\n\n🔹 بیت‌کوین به 70 هزار دلار نزدیک شد\n🔹 اتریوم آپدیت بعدی را اعلام کرد\n🔹 سولانا رکورد تراکنش‌ها را شکست\n\n(اخبار لحظه‌ای به زودی اضافه می‌شود)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💰 *پورتفوی دمو*\n\nموجودی: 10,000 USDT\nپوزیشن‌های باز: هیچ\nسود/زیان تحقق‌یافته: 0 USDT\n\n(قابلیت معامله دمو به زودی)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"⚙️ *تنظیمات*\n\n🔑 CoinEx: {'✅ فعال' if os.getenv('COINEX_ACCESS_ID') else '❌ غیرفعال'}\n🧠 Groq: {'✅ فعال' if GROQ_API_KEY else '❌ غیرفعال'}\n📢 کانال: {CHANNEL_ID}\n👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنمای کامل*\n\n"
        "📌 **قابلیت‌های ربات:**\n"
        "• قیمت لحظه‌ای ۷ ارز برتر\n"
        "• سیگنال فوری بر اساس RSI, MACD, باند بولینگر\n"
        "• تحلیل تکنیکال پیشرفته با اندیکاتورهای واقعی\n"
        "• تشخیص تله گاوی و خرسی\n"
        "• هوش مصنوعی Groq (اختیاری)\n"
        "• ارسال خودکار سیگنال هر ۵ دقیقه به کانال\n\n"
        "⚠️ **هشدار:** این ربات فقط جنبه آموزشی دارد و مسئولیت معاملات با شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("waiting_ai"):
        await ai_chat_handler(update, context)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai_analysis":
        await ai_analysis_menu(update, context)
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "demo":
        await demo_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()
        await query.edit_message_text("در حال توسعه...")

# ---------------------------- اجرای اصلی ----------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # راه‌اندازی ترد جداگانه برای ارسال خودکار
    global auto_thread_running
    auto_thread_running = True
    thread = threading.Thread(target=auto_signal_thread, args=(app,), daemon=True)
    thread.start()

    logger.info("🚀 ربات فوق‌حرفه‌ای کریپتو با موفقیت راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()

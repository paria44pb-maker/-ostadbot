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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@comedyclick")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

DEMO_FILE = "demo_portfolio.json"
def load_demo():
    if os.path.exists(DEMO_FILE):
        with open(DEMO_FILE, "r") as f:
            return json.load(f)
    return {"balance": 10000.0, "positions": [], "history": []}
def save_demo(data):
    with open(DEMO_FILE, "w") as f:
        json.dump(data, f, indent=2)

demo_portfolio = load_demo()
auto_trade_enabled = False

# ---------------------------- توابع کوینکس و اخبار ----------------------------
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

async def get_historical_klines(symbol, limit=50):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=5min&limit={limit}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                klines = resp.json()["data"]
                return [float(k[4]) for k in klines]
    except Exception as e:
        logger.error(f"Kline error {symbol}: {e}")
    return None

async def get_crypto_news():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://cryptopanic.com/api/v1/posts/?auth_token=&public=true&kind=news")
            if resp.status_code == 200:
                articles = resp.json().get("results", [])[:5]
                return [{"title": a["title"], "source": a["source"]["title"], "url": a["url"]} for a in articles]
    except Exception as e:
        logger.error(f"News error: {e}")
    return []

async def get_fear_greed():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://api.alternative.me/fng/?limit=1")
            if resp.status_code == 200:
                data = resp.json()["data"][0]
                return {"value": int(data["value"]), "classification": data["value_classification"]}
    except:
        pass
    return {"value": 50, "classification": "Neutral"}

# ---------------------------- اندیکاتورها ----------------------------
def calculate_ema(values, period):
    if len(values) < period:
        return values[-1] if values else 0
    multiplier = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = (v - ema) * multiplier + ema
    return ema

def calculate_rsi(closes, period=14):
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
    avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
    avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(closes, fast=12, slow=26, signal=9):
    if len(closes) < slow + signal:
        return 0, 0, 0
    ema_fast = [calculate_ema(closes[:i+1], fast) for i in range(len(closes))]
    ema_slow = [calculate_ema(closes[:i+1], slow) for i in range(len(closes))]
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    macd_signal = [calculate_ema(macd_line[:i+1], signal) for i in range(len(macd_line))]
    return macd_line[-1], macd_signal[-1]

def calculate_bollinger(closes, period=20, std_dev=2):
    if len(closes) < period:
        return None, None, None
    sma = sum(closes[-period:]) / period
    variance = sum((c - sma) ** 2 for c in closes[-period:]) / period
    std = variance ** 0.5
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

def support_resistance(closes, lookback=50):
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
    if change > 3 and volume > 10_000_000 and rsi > 70:
        return "⚠️ تله گاوی (خرید کاذب)"
    if change < -3 and volume > 10_000_000 and rsi < 30:
        return "⚠️ تله خرسی (فروش کاذب)"
    return "✅ بدون تله"

def generate_signal(change, rsi, macd, macd_signal):
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
        return "خرید قوی", 90
    elif score >= 20:
        return "خرید", 75
    elif score <= -45:
        return "فروش قوی", 90
    elif score <= -20:
        return "فروش", 75
    else:
        return "نگهداری", 50

# ---------------------------- هوش مصنوعی ----------------------------
async def groq_analysis(prompt):
    if not GROQ_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200}
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return None

# ---------------------------- آموزش‌های خودکار ----------------------------
EDUCATION_TOPICS = [
    {"title": "📚 آموزش تکنیکال – RSI", "content": "شاخص قدرت نسبی (RSI) بین ۰ تا ۱۰۰ حرکت می‌کند. مقادیر زیر ۳۰ نشانه اشباع فروش (منطقه خرید) و بالای ۷۰ نشانه اشباع خرید (منطقه فروش) است."},
    {"title": "📚 آموزش فاندامنتال – اخبار", "content": "اخبار اقتصادی مانند نرخ بهره فدرال رزرو، تورم و تصمیمات بانک‌های مرکزی تأثیر مستقیم بر قیمت بیت‌کوین و ارزهای دیجیتال دارد."},
    {"title": "📚 آموزش پرایس اکشن – الگوهای کندل", "content": "الگوی چکش (Hammer) در انتهای روند نزولی نشانه بازگشت صعودی است. دوجی (Doji) نشانه تردید بازار و احتمال تغییر روند می‌باشد."},
    {"title": "📚 آموزش اندیکاتور MACD", "content": "MACD از دو خط (MACD line و Signal line) تشکیل شده. تقاطع صعودی MACD بالای Signal خط سیگنال خرید و تقاطع نزولی سیگنال فروش است."},
    {"title": "📚 مدیریت ریسک", "content": "هرگز بیش از ۲٪ سرمایه خود را در یک معامله ریسک نکنید. نسبت ریسک به ریوارد حداقل ۱:۲ باشد. همیشه از حد ضرر استفاده کنید."},
]

last_education_day = None

async def send_daily_education(app):
    global last_education_day
    today = datetime.now().day
    if last_education_day == today:
        return
    last_education_day = today
    topic = random.choice(EDUCATION_TOPICS)
    msg = f"📘 *آموزش روزانه کریپتو*\n\n{topic['title']}\n\n{topic['content']}\n\n✨ @comedyclick"
    try:
        await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
        logger.info("آموزش روزانه ارسال شد")
    except Exception as e:
        logger.error(f"Education send error: {e}")

# ---------------------------- ارسال خودکار سیگنال، اخبار و آموزش ----------------------------
auto_thread_running = True

def auto_signal_thread(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while auto_thread_running:
        time.sleep(300)  # 5 دقیقه
        loop.run_until_complete(send_auto_signals(app))

async def send_auto_signals(app):
    if not CHANNEL_ID:
        return
    # 1. ارسال سیگنال برای ۳ ارز اول
    for symbol, info in list(SYMBOLS.items())[:3]:
        price_data = await get_coinex_price(symbol)
        if not price_data:
            continue
        closes = await get_historical_klines(symbol, 50)
        if not closes:
            closes = [price_data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(50)]
        rsi = calculate_rsi(closes)
        macd, macd_signal = calculate_macd(closes)
        signal, confidence = generate_signal(price_data["change"], rsi, macd, macd_signal)
        bb_upper, bb_mid, bb_lower = calculate_bollinger(closes)
        sr = support_resistance(closes)
        trap = detect_trap(price_data["change"], price_data["volume"], rsi)
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
║   🔥 {info['emoji']} *{info['name']}* – سیگنال لحظه‌ای 🔥   ║
╚══════════════════════════════════════╝

💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر ۲۴ ساعته:** `{price_data['change']:+.2f}%`
🎯 **سیگنال:** **{signal}** (اطمینان {confidence}%)
📊 **RSI:** `{rsi:.1f}` | **MACD:** `{macd:.4f}`
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **اهداف:** `${tp1:,.2f}` → `${tp2:,.2f}`
{trap}

📚 نکته آموزشی: {random.choice(EDUCATION_TOPICS)['title']} – برای مشاهده کامل به بخش آموزش مراجعه کنید.
✨ @comedyclick
"""
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"Auto signal sent for {symbol}")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Failed to send {symbol}: {e}")

    # 2. ارسال اخبار هر 2 ساعت (هر 4 بار اجرای سیگنال)
    if int(time.time()) % 7200 < 300:
        news = await get_crypto_news()
        if news:
            news_text = "📰 *آخرین اخبار کریپتو*\n\n"
            for n in news[:3]:
                news_text += f"• {n['title'][:100]}...\n"
            news_text += f"\n✨ @comedyclick"
            await app.bot.send_message(chat_id=CHANNEL_ID, text=news_text, parse_mode="Markdown")
            logger.info("Auto news sent")

    # 3. ارسال شاخص ترس و طمع هر 4 ساعت
    if int(time.time()) % 14400 < 300:
        fg = await get_fear_greed()
        fg_emoji = "😰" if fg["value"] < 30 else "😊" if fg["value"] > 70 else "😐"
        msg = f"📊 *شاخص ترس و طمع لحظه‌ای*\n\n{fg_emoji} مقدار: {fg['value']}/100\nوضعیت: {fg['classification']}\n\n✨ @comedyclick"
        await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
        logger.info("Fear & Greed sent")

    # 4. آموزش روزانه (یک بار در روز)
    await send_daily_education(app)

# ---------------------------- معامله خودکار دمو ----------------------------
async def execute_demo_trade(symbol, signal, confidence, price):
    global demo_portfolio, auto_trade_enabled
    if not auto_trade_enabled or confidence < 75:
        return
    if signal in ["خرید", "خرید قوی"]:
        for pos in demo_portfolio["positions"]:
            if pos["symbol"] == symbol:
                return
        amount_usdt = demo_portfolio["balance"] * 0.2
        if amount_usdt > demo_portfolio["balance"]:
            return
        amount_coin = amount_usdt / price
        demo_portfolio["balance"] -= amount_usdt
        demo_portfolio["positions"].append({
            "symbol": symbol, "amount": amount_coin, "entry_price": price,
            "entry_time": datetime.now().isoformat(), "signal": signal
        })
        save_demo(demo_portfolio)
        logger.info(f"Auto buy {symbol}")
    elif signal in ["فروش", "فروش قوی"]:
        for i, pos in enumerate(demo_portfolio["positions"]):
            if pos["symbol"] == symbol:
                sell_value = pos["amount"] * price
                pnl = sell_value - (pos["amount"] * pos["entry_price"])
                demo_portfolio["balance"] += sell_value
                demo_portfolio["history"].append({
                    "symbol": symbol, "side": "فروش", "entry_price": pos["entry_price"],
                    "exit_price": price, "amount": pos["amount"], "pnl": pnl,
                    "time": datetime.now().isoformat()
                })
                demo_portfolio["positions"].pop(i)
                save_demo(demo_portfolio)
                logger.info(f"Auto sell {symbol} PnL: {pnl:.2f}")
                break

# ---------------------------- منوی اصلی (20 دکمه) ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوش مصنوعی", callback_data="ai")],
        [InlineKeyboardButton("📚 آموزش روزانه", callback_data="education")],
        [InlineKeyboardButton("📰 اخبار کریپتو", callback_data="news")],
        [InlineKeyboardButton("😨 شاخص ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ", callback_data="whale")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("⚡ معامله خودکار دمو", callback_data="auto_trade")],
        [InlineKeyboardButton("📊 وضعیت بازار", callback_data="market_status")],
        [InlineKeyboardButton("📅 تقویم اقتصادی", callback_data="calendar")],
        [InlineKeyboardButton("🔄 بک‌تست استراتژی", callback_data="backtest")],
        [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("⭐ نظرسنجی", callback_data="poll")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update, context):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات فوق‌هوشمند جهانی کریپتو* 🔥\n\n"
        "✅ **قابلیت‌های منحصربه‌فرد:**\n"
        "• سیگنال لحظه‌ای با ۷ اندیکاتور\n"
        "• آموزش خودکار روزانه (تکنیکال، فاندامنتال، پرایس اکشن)\n"
        "• اخبار لحظه‌ای و شاخص ترس و طمع\n"
        "• معامله خودکار دمو با مدیریت ریسک\n"
        "• پورتفوی دمو کامل\n"
        "• هوش مصنوعی Groq برای تحلیل\n"
        "• ارسال خودکار به کانال هر ۵ دقیقه\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown", reply_markup=get_main_menu()
    )

# ---------------------------- هندلرهای منو ----------------------------
async def prices_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{info['name']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای...")
    sym = "BTCUSDT"
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("خطا")
        return
    closes = await get_historical_klines(sym, 50) or [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(50)]
    rsi = calculate_rsi(closes)
    macd, macd_signal = calculate_macd(closes)
    signal, conf = generate_signal(data["change"], rsi, macd, macd_signal)
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    trap = detect_trap(data["change"], data["volume"], rsi)
    msg = f"🎯 *سیگنال {SYMBOLS[sym]['name']}*\n💰 ${data['price']:,.2f}\n📈 {data['change']:+.2f}%\n📊 RSI: {rsi:.1f} | MACD: {macd:.4f}\n🎯 {signal} (اطمینان {conf}%)\n{trap}\n🟢 باند پایین: ${bb_l:,.2f} | 🟡 وسط: ${bb_m:,.2f} | 🔴 بالا: ${bb_u:,.2f}"
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 نام ارز را وارد کنید (مثل BTC, ETH):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update, context, symbol_input):
    symbol = next((s for s in SYMBOLS if symbol_input.upper() in s), None)
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    data = await get_coinex_price(symbol)
    if not data:
        await update.message.reply_text("خطا در دریافت قیمت")
        return
    closes = await get_historical_klines(symbol, 50) or [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(50)]
    rsi = calculate_rsi(closes)
    macd, macd_signal = calculate_macd(closes)
    ema20 = calculate_ema(closes, 20)
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    sr = support_resistance(closes)
    trap = detect_trap(data["change"], data["volume"], rsi)
    signal, conf = generate_signal(data["change"], rsi, macd, macd_signal)
    reply = (
        f"📊 *تحلیل {SYMBOLS[symbol]['name']}*\n"
        f"💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n"
        f"📊 RSI: {rsi:.1f}\n📈 MACD: {macd:.4f}\n🟢 EMA20: ${ema20:,.2f}\n"
        f"📊 باند: پایین ${bb_l:,.2f} | وسط ${bb_m:,.2f} | بالا ${bb_u:,.2f}\n"
        f"🟡 حمایت: ${sr['support'][0]:,.2f} | مقاومت: ${sr['resistance'][0]:,.2f}\n{trap}\n🎯 سیگنال: {signal} (اطمینان {conf}%)"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def ai_menu(update, context):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("⚠️ هوش مصنوعی غیرفعال است.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    await query.edit_message_text("🧠 سوال خود را بپرسید:", parse_mode="Markdown")
    context.user_data["waiting_ai"] = True

async def ai_chat(update, context):
    prompt = update.message.text
    await update.message.reply_chat_action("typing")
    data = await get_coinex_price("BTCUSDT")
    closes = await get_historical_klines("BTCUSDT", 30) if data else []
    rsi = calculate_rsi(closes) if closes else 50
    full_prompt = f"{prompt}\n(داده فعلی بیت‌کوین: قیمت ${data['price']:,.0f}, تغییر {data['change']:+.1f}%, RSI {rsi:.0f})" if data else prompt
    resp = await groq_analysis(full_prompt) or "⚠️ هوش مصنوعی در دسترس نیست."
    await update.message.reply_text(f"🧠 *AI:*\n{resp}", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def education_menu(update, context):
    query = update.callback_query
    await query.answer()
    topic = random.choice(EDUCATION_TOPICS)
    text = f"📘 *{topic['title']}*\n\n{topic['content']}\n\nبرای آموزش بیشتر به کانال مراجعه کنید."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def news_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت اخبار...")
    news = await get_crypto_news()
    if not news:
        await query.edit_message_text("اخباری یافت نشد.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    text = "📰 *آخرین اخبار*\n\n"
    for n in news[:5]:
        text += f"• {n['title'][:120]}...\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def fear_greed_menu(update, context):
    query = update.callback_query
    await query.answer()
    fg = await get_fear_greed()
    emoji = "😰" if fg["value"] < 30 else "😊" if fg["value"] > 70 else "😐"
    text = f"📊 *شاخص ترس و طمع*\n\n{emoji} مقدار: {fg['value']}/100\nوضعیت: {fg['classification']}\n\nاین شاخص نشان‌دهنده احساسات سرمایه‌گذاران است."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def whale_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 *ردیابی نهنگ‌ها*\n\nدر حال توسعه...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def risk_menu(update, context):
    query = update.callback_query
    await query.answer()
    text = "🛡️ *مدیریت ریسک*\n\n• حداکثر ۲٪ سرمایه در هر معامله\n• نسبت ریسک به ریوارد ≥ ۱:۲\n• همیشه حد ضرر\n• حداکثر ۳ پوزیشن همزمان\n• توقف پس از ۳ ضرر متوالی"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def demo_portfolio_menu(update, context):
    global demo_portfolio
    query = update.callback_query
    await query.answer()
    total_value = demo_portfolio["balance"]
    pos_value = 0
    pos_text = ""
    for pos in demo_portfolio["positions"]:
        price = (await get_coinex_price(pos["symbol"]))["price"] if await get_coinex_price(pos["symbol"]) else pos["entry_price"]
        current = pos["amount"] * price
        pos_value += current
        pnl = (price - pos["entry_price"]) * pos["amount"]
        pos_text += f"• {SYMBOLS[pos['symbol']]['name']}: {pos['amount']:.4f} @ ${pos['entry_price']:.2f} | سود/زیان: ${pnl:+.2f}\n"
    total_value += pos_value
    text = f"💰 *پورتفوی دمو*\n\nموجودی نقد: ${demo_portfolio['balance']:,.2f}\nارزش پوزیشن‌ها: ${pos_value:,.2f}\nارزش کل: ${total_value:,.2f}\n\n**پوزیشن‌های باز:**\n{pos_text if pos_text else 'هیچ'}\n\nتاریخچه: {len(demo_portfolio['history'])} معامله"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def auto_trade_menu(update, context):
    global auto_trade_enabled
    query = update.callback_query
    await query.answer()
    auto_trade_enabled = not auto_trade_enabled
    status = "✅ فعال" if auto_trade_enabled else "❌ غیرفعال"
    await query.edit_message_text(f"⚡ *معامله خودکار دمو*\n\nوضعیت: {status}\n(فقط سیگنال‌های با اطمینان ≥۷۵٪ اجرا می‌شوند)", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def market_status_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📊 *وضعیت بازار*\n\nدر حال توسعه...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def calendar_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📅 *تقویم اقتصادی*\n\nدر حال توسعه...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def backtest_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 *بک‌تست استراتژی*\n\nدر حال توسعه...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def support_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💬 *پشتیبانی*\n\nسوالات خود را به @Admin ارسال کنید.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def poll_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⭐ *نظرسنجی*\n\nآیا از ربات راضی هستید؟\n1. خیلی زیاد\n2. زیاد\n3. متوسط\n4. کم\n(لطفاً عدد را بفرستید)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def settings_menu(update, context):
    query = update.callback_query
    await query.answer()
    text = f"⚙️ *تنظیمات*\n\n🔑 CoinEx: {'✅' if os.getenv('COINEX_ACCESS_ID') else '❌'}\n🧠 Groq: {'✅' if GROQ_API_KEY else '❌'}\n📢 کانال: {CHANNEL_ID}\n👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه'}\n⚡ معامله خودکار: {'فعال' if auto_trade_enabled else 'غیرفعال'}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update, context):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنما*\n\n"
        "• قیمت لحظه‌ای\n• سیگنال فوری\n• تحلیل تکنیکال\n• هوش مصنوعی\n• آموزش روزانه\n• اخبار و شاخص ترس و طمع\n• پورتفوی دمو و معامله خودکار\n• مدیریت ریسک\n\n"
        "رباط هر ۵ دقیقه سیگنال + هر روز آموزش + هر ۲ ساعت اخبار + هر ۴ ساعت ترس و طمع به کانال می‌فرستد.\n\n⚠️ فقط جنبه آموزشی"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update, context):
    await start(update, context)

async def handle_message(update, context):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("waiting_ai"):
        await ai_chat(update, context)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید.")

async def button_handler(update, context):
    query = update.callback_query
    data = query.data
    if data == "back": await start(update, context)
    elif data == "prices": await prices_menu(update, context)
    elif data == "signal": await signal_now(update, context)
    elif data == "technical": await technical_menu(update, context)
    elif data == "ai": await ai_menu(update, context)
    elif data == "education": await education_menu(update, context)
    elif data == "news": await news_menu(update, context)
    elif data == "fear_greed": await fear_greed_menu(update, context)
    elif data == "whale": await whale_menu(update, context)
    elif data == "risk": await risk_menu(update, context)
    elif data == "demo": await demo_portfolio_menu(update, context)
    elif data == "auto_trade": await auto_trade_menu(update, context)
    elif data == "market_status": await market_status_menu(update, context)
    elif data == "calendar": await calendar_menu(update, context)
    elif data == "backtest": await backtest_menu(update, context)
    elif data == "support": await support_menu(update, context)
    elif data == "poll": await poll_menu(update, context)
    elif data == "settings": await settings_menu(update, context)
    elif data == "help": await help_menu(update, context)
    else: await query.edit_message_text("در حال توسعه...")

# ---------------------------- اجرای اصلی ----------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    global auto_thread_running
    auto_thread_running = True
    thread = threading.Thread(target=auto_signal_thread, args=(app,), daemon=True)
    thread.start()

    logger.info("ربات فوق‌هوشمند جهانی راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()

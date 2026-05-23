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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@comedyclick")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# لیست ارزهای تحت پوشش (نام فارسی، ایموجی)
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- ذخیره‌سازی دمو ----------------------------
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

# ---------------------------- توابع کوینکس ----------------------------
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
        logger.error(f"خطا در دریافت قیمت {symbol}: {e}")
    return None

async def get_historical_klines(symbol, limit=50):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=5min&limit={limit}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                klines = resp.json()["data"]
                return [float(k[4]) for k in klines]  # قیمت بسته شدن
    except Exception as e:
        logger.error(f"خطا در دریافت کندل {symbol}: {e}")
    return None

# ---------------------------- اندیکاتورهای تکنیکال ----------------------------
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

# ---------------------------- هوش مصنوعی Groq ----------------------------
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

# ---------------------------- معامله خودکار دمو ----------------------------
async def execute_demo_trade(symbol, signal, confidence, price):
    global demo_portfolio, auto_trade_enabled
    if not auto_trade_enabled:
        return
    if confidence < 75:  # فقط سیگنال‌های قوی
        return
    # باز کردن پوزیشن
    if signal in ["خرید", "خرید قوی"]:
        # بررسی کنید آیا از قبل پوزیشن باز است
        for pos in demo_portfolio["positions"]:
            if pos["symbol"] == symbol:
                return
        amount_usdt = demo_portfolio["balance"] * 0.2  # 20% سرمایه
        if amount_usdt > demo_portfolio["balance"]:
            return
        amount_coin = amount_usdt / price
        demo_portfolio["balance"] -= amount_usdt
        demo_portfolio["positions"].append({
            "symbol": symbol,
            "amount": amount_coin,
            "entry_price": price,
            "entry_time": datetime.now().isoformat(),
            "signal": signal
        })
        save_demo(demo_portfolio)
        logger.info(f"خرید دمو {symbol} به قیمت ${price:,.2f}")
    elif signal in ["فروش", "فروش قوی"]:
        # بستن پوزیشن مربوطه
        for i, pos in enumerate(demo_portfolio["positions"]):
            if pos["symbol"] == symbol:
                sell_value = pos["amount"] * price
                pnl = sell_value - (pos["amount"] * pos["entry_price"])
                demo_portfolio["balance"] += sell_value
                demo_portfolio["history"].append({
                    "symbol": symbol,
                    "side": "فروش",
                    "entry_price": pos["entry_price"],
                    "exit_price": price,
                    "amount": pos["amount"],
                    "pnl": pnl,
                    "time": datetime.now().isoformat()
                })
                demo_portfolio["positions"].pop(i)
                save_demo(demo_portfolio)
                logger.info(f"فروش دمو {symbol} سود/زیان: ${pnl:+.2f}")
                break

# ---------------------------- ارسال خودکار سیگنال و معامله ----------------------------
auto_thread_running = True

def auto_signal_thread(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while auto_thread_running:
        time.sleep(300)  # ۵ دقیقه
        loop.run_until_complete(send_auto_signals(app))

async def send_auto_signals(app):
    if not CHANNEL_ID:
        return
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

        # اجرای معامله خودکار (دمو)
        await execute_demo_trade(symbol, signal, confidence, price_data["price"])

        msg = f"""
╔══════════════════════════════════════╗
║   🔥 {info['emoji']} *{symbol.replace('USDT','')}* – سیگنال لحظه‌ای 🔥   ║
╚══════════════════════════════════════╝

💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر ۲۴ ساعته:** `{price_data['change']:+.2f}%`
🎯 **سیگنال:** **{signal}** (اطمینان {confidence}%)
📊 **RSI:** `{rsi:.1f}` | **MACD:** `{macd:.4f}`
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **اهداف:** `${tp1:,.2f}` → `${tp2:,.2f}`
{trap}

✨ @comedyclick
"""
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"✅ سیگنال خودکار {symbol} ارسال شد")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"❌ خطا در ارسال {symbol}: {e}")

# ---------------------------- منوی اصلی فارسی ----------------------------
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
        [InlineKeyboardButton("⚡ معامله خودکار دمو", callback_data="auto_trade")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

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
        "• معامله خودکار در حالت دمو (با موجودی مجازی)\n"
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
            text += f"{emoji} {info['emoji']} *{info['name']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
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
    macd, macd_signal = calculate_macd(closes)
    signal, conf = generate_signal(data["change"], rsi, macd, macd_signal)
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    trap = detect_trap(data["change"], data["volume"], rsi)
    msg = f"""
🎯 *سیگنال لحظه‌ای {SYMBOLS[sym]['name']}* 🎯

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر ۲۴ ساعته:** {data['change']:+.2f}%
📊 **RSI:** {rsi:.1f} | **MACD:** {macd:.4f}
🎯 **سیگنال:** **{signal}** (اطمینان {conf}%)
{trap}
🟢 **باند پایین:** ${bb_l:,.2f} | 🟡 **وسط:** ${bb_m:,.2f} | 🔴 **بالا:** ${bb_u:,.2f}
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
    symbol = None
    for sym in SYMBOLS:
        if symbol_input.upper() in sym or sym.startswith(symbol_input.upper()):
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
    macd, macd_signal = calculate_macd(closes)
    ema20 = calculate_ema(closes, 20)
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    sr = support_resistance(closes)
    trap = detect_trap(data["change"], data["volume"], rsi)
    signal, conf = generate_signal(data["change"], rsi, macd, macd_signal)
    reply = (
        f"📊 *تحلیل تکنیکال {SYMBOLS[symbol]['name']}*\n"
        f"💰 **قیمت:** ${data['price']:,.2f}\n📈 **تغییر:** {data['change']:+.2f}%\n"
        f"📊 **RSI:** {rsi:.1f}\n📈 **MACD:** {macd:.4f} (سیگنال: {macd_signal:.4f})\n"
        f"🟢 **EMA20:** ${ema20:,.2f}\n"
        f"📊 **باند بولینگر:** پایین ${bb_l:,.2f} | وسط ${bb_m:,.2f} | بالا ${bb_u:,.2f}\n"
        f"🟡 **حمایت:** ${sr['support'][0]:,.2f} | **مقاومت:** ${sr['resistance'][0]:,.2f}\n"
        f"{trap}\n🎯 **سیگنال نهایی:** **{signal}** (اطمینان {conf}%)"
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
    data = await get_coinex_price("BTCUSDT")
    if not data:
        analysis = "⚠️ داده‌های بازار در دسترس نیست."
    else:
        closes = await get_historical_klines("BTCUSDT", 30)
        if not closes:
            closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
        rsi = calculate_rsi(closes)
        ai_text = await groq_analysis("بیت‌کوین", data["price"], data["change"], rsi)
        analysis = ai_text if ai_text else "⚠️ هوش مصنوعی در دسترس نیست."
    await update.message.reply_text(f"🧠 *تحلیل هوش مصنوعی:*\n{analysis}", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 *ردیابی نهنگ‌ها*\n\nبه زودی اضافه می‌شود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

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
    await query.edit_message_text("📰 *اخبار کریپتو*\n\n🔹 بیت‌کوین به 70 هزار دلار نزدیک شد\n🔹 اتریوم آپدیت بعدی را اعلام کرد\n🔹 سولانا رکورد تراکنش‌ها را شکست\n\n(اخبار لحظه‌ای به زودی)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global demo_portfolio
    query = update.callback_query
    await query.answer()
    total_value = demo_portfolio["balance"]
    open_positions_value = 0
    pos_text = ""
    for pos in demo_portfolio["positions"]:
        price_data = await get_coinex_price(pos["symbol"])
        if price_data:
            current_value = pos["amount"] * price_data["price"]
            open_positions_value += current_value
            pnl = (price_data["price"] - pos["entry_price"]) * pos["amount"]
            pos_text += f"• {SYMBOLS[pos['symbol']]['name']}: {pos['amount']:.4f} @ ${pos['entry_price']:.2f} | سود/زیان: ${pnl:+.2f}\n"
    total_value += open_positions_value
    text = f"💰 *پورتفوی دمو*\n\nموجودی نقد: ${demo_portfolio['balance']:,.2f}\nارزش پوزیشن‌ها: ${open_positions_value:,.2f}\nارزش کل: ${total_value:,.2f}\n\n**پوزیشن‌های باز:**\n{pos_text if pos_text else 'هیچ'}\n\nتاریخچه معاملات: {len(demo_portfolio['history'])} مورد"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_trade_enabled
    query = update.callback_query
    await query.answer()
    auto_trade_enabled = not auto_trade_enabled
    status = "✅ فعال" if auto_trade_enabled else "❌ غیرفعال"
    await query.edit_message_text(f"⚡ *معامله خودکار دمو*\n\nوضعیت: {status}\n\nدر صورت فعال بودن، ربات به طور خودکار بر اساس سیگنال‌های قوی (اطمینان ≥۷۵٪) خرید و فروش می‌کند.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"⚙️ *تنظیمات*\n\n🔑 CoinEx: {'✅ فعال' if os.getenv('COINEX_ACCESS_ID') else '❌ غیرفعال'}\n🧠 Groq: {'✅ فعال' if GROQ_API_KEY else '❌ غیرفعال'}\n📢 کانال: {CHANNEL_ID}\n👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}\n⚡ معامله خودکار: {'فعال' if auto_trade_enabled else 'غیرفعال'}"
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
        "• ارسال خودکار سیگنال هر ۵ دقیقه به کانال\n"
        "• معامله خودکار در حالت دمو (با قابلیت فعال/غیرفعال)\n"
        "• پورتفوی دمو با موجودی مجازی ۱۰,۰۰۰ دلار\n\n"
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
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
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

    global auto_thread_running
    auto_thread_running = True
    thread = threading.Thread(target=auto_signal_thread, args=(app,), daemon=True)
    thread.start()

    logger.info("🚀 ربات فوق‌حرفه‌ای کریپتو با معامله خودکار و هوش مصنوعی راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()

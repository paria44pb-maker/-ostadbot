import os
import logging
import asyncio
import threading
import time
import random
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

SYMBOLS = {
    "BTCUSDT": {"name": "Bitcoin", "emoji": "👑"},
    "ETHUSDT": {"name": "Ethereum", "emoji": "💎"},
    "SOLUSDT": {"name": "Solana", "emoji": "⚡"},
    "BNBUSDT": {"name": "Binance", "emoji": "🟡"},
    "XRPUSDT": {"name": "Ripple", "emoji": "💧"},
    "ADAUSDT": {"name": "Cardano", "emoji": "🌿"},
    "DOGEUSDT": {"name": "Dogecoin", "emoji": "🐕"},
}

# ---------------------------- توابع CoinEx ----------------------------
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
        return "⚠️ Bull Trap (fake buy)"
    if change < -3 and volume > 10_000_000 and rsi < 30:
        return "⚠️ Bear Trap (fake sell)"
    return "✅ No trap"

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
        return "STRONG BUY", 90
    elif score >= 20:
        return "BUY", 75
    elif score <= -45:
        return "STRONG SELL", 90
    elif score <= -20:
        return "SELL", 75
    else:
        return "HOLD", 50

# ---------------------------- هوش مصنوعی (اختیاری) ----------------------------
async def groq_analysis(symbol, price, change, rsi):
    if not GROQ_API_KEY:
        return None
    prompt = f"Quick analysis {symbol}: price ${price:,.0f}, change {change:+.1f}%, RSI {rsi:.0f}. Give short prediction and advice in one line."
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

# ---------------------------- ارسال خودکار (ترد جداگانه) ----------------------------
auto_thread_running = True

def auto_signal_thread(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while auto_thread_running:
        time.sleep(300)  # 5 minutes
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
        if "BUY" in signal:
            sl = bb_lower if bb_lower else price_data["price"] * 0.97
            tp1 = bb_mid if bb_mid else price_data["price"] * 1.02
            tp2 = bb_upper if bb_upper else price_data["price"] * 1.05
        else:
            sl = bb_upper if bb_upper else price_data["price"] * 1.03
            tp1 = bb_mid if bb_mid else price_data["price"] * 0.98
            tp2 = bb_lower if bb_lower else price_data["price"] * 0.95
        msg = f"""
╔══════════════════════════════════════╗
║   🔥 {info['emoji']} *{symbol.replace('USDT','')}* – Signal 🔥   ║
╚══════════════════════════════════════╝

💰 Price: `${price_data['price']:,.2f}`
📈 24h Change: `{price_data['change']:+.2f}%`
🎯 Signal: **{signal}** (confidence {confidence}%)
📊 RSI: `{rsi:.1f}` | MACD: `{macd:.4f}`
🛡️ Stop Loss: `${sl:,.2f}`
🎯 Targets: `${tp1:,.2f}` → `${tp2:,.2f}`
{trap}

✨ @comedyclick
"""
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"Auto signal sent for {symbol}")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Failed to send {symbol}: {e}")

# ---------------------------- منوی اصلی (بدون ایموجی در نام متغیرها) ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Live Prices", callback_data="prices")],
        [InlineKeyboardButton("🎯 Instant Signal (BTC)", callback_data="signal")],
        [InlineKeyboardButton("📈 Advanced Technical", callback_data="technical")],
        [InlineKeyboardButton("🧠 AI Analysis", callback_data="ai_analysis")],
        [InlineKeyboardButton("🐋 Whale Tracking", callback_data="whale")],
        [InlineKeyboardButton("🛡️ Risk Management", callback_data="risk")],
        [InlineKeyboardButton("📰 Crypto News", callback_data="news")],
        [InlineKeyboardButton("💰 Demo Portfolio", callback_data="demo")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Access denied.")
        return
    await update.message.reply_text(
        "🔥 *Ultimate Crypto Bot* 🔥\n\n"
        "✅ **Features:**\n"
        "• Live prices of top 7 coins\n"
        "• Advanced technical analysis (RSI, MACD, Bollinger)\n"
        "• Market trap detection\n"
        "• AI analysis (Groq)\n"
        "• Auto signals every 5 minutes to channel\n"
        "• Risk management & demo portfolio\n\n"
        "Choose from menu:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Fetching prices...")
    text = "💰 *Live Prices* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{sym.replace('USDT','')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Analyzing market...")
    sym = "BTCUSDT"
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("Error fetching data")
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
🎯 *Instant Signal {sym.replace('USDT','')}* 🎯

💰 Price: ${data['price']:,.2f}
📈 Change: {data['change']:+.2f}%
📊 RSI: {rsi:.1f} | MACD: {macd:.4f}
🎯 Signal: **{signal}** (confidence {conf}%)
{trap}
🟢 Lower Band: ${bb_l:,.2f} | 🟡 Middle: ${bb_m:,.2f} | 🔴 Upper: ${bb_u:,.2f}
"""
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📈 *Advanced Technical Analysis*\n\n"
        "Please enter the coin name (e.g., BTC, ETH, SOL):",
        parse_mode="Markdown"
    )
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol_input):
    symbol = None
    for sym in SYMBOLS:
        if symbol_input in sym or sym.startswith(symbol_input):
            symbol = sym
            break
    if not symbol:
        await update.message.reply_text("Invalid coin symbol.")
        return
    data = await get_coinex_price(symbol)
    if not data:
        await update.message.reply_text("Error fetching price.")
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
        f"📊 *Technical Analysis {symbol.replace('USDT','')}*\n"
        f"💰 Price: ${data['price']:,.2f}\n📈 Change: {data['change']:+.2f}%\n"
        f"📊 RSI: {rsi:.1f}\n📈 MACD: {macd:.4f} (Signal: {macd_signal:.4f})\n"
        f"🟢 EMA20: ${ema20:,.2f}\n"
        f"📊 Bollinger Bands: Lower ${bb_l:,.2f} | Middle ${bb_m:,.2f} | Upper ${bb_u:,.2f}\n"
        f"🟡 Support: ${sr['support'][0]:,.2f} | Resistance: ${sr['resistance'][0]:,.2f}\n"
        f"{trap}\n🎯 Final Signal: **{signal}** (confidence {conf}%)"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def ai_analysis_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("⚠️ AI not available (GROQ_API_KEY missing).", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
        return
    await query.edit_message_text("🧠 *AI Analysis*\nPlease ask your question (e.g., 'Analyze Bitcoin'):", parse_mode="Markdown")
    context.user_data["waiting_ai"] = True

async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_chat_action("typing")
    data = await get_coinex_price("BTCUSDT")
    if not data:
        analysis = "⚠️ Market data not available."
    else:
        closes = await get_historical_klines("BTCUSDT", 30)
        if not closes:
            closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
        rsi = calculate_rsi(closes)
        ai_text = await groq_analysis("BTC", data["price"], data["change"], rsi)
        analysis = ai_text if ai_text else "⚠️ AI unavailable."
    await update.message.reply_text(f"🧠 *AI Analysis:*\n{analysis}", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 *Whale Tracking*\n\nComing soon.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🛡️ *Professional Risk Management*\n\n"
        "📌 Golden rules:\n"
        "• Max 2% risk per trade\n"
        "• Risk/reward ratio at least 1:2\n"
        "• Always use stop loss\n"
        "• Max 3 concurrent positions\n"
        "• Stop trading after consecutive losses"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 *Crypto News*\n\n🔹 Bitcoin approaching $70k\n🔹 Ethereum announces next upgrade\n🔹 Solana breaks transaction record\n\n(Real-time news coming soon)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💰 *Demo Portfolio*\n\nBalance: 10,000 USDT\nOpen positions: none\nRealized P&L: 0 USDT\n\n(Trading simulation coming soon)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"⚙️ *Settings*\n\n🔑 CoinEx: {'✅ Enabled' if os.getenv('COINEX_ACCESS_ID') else '❌ Disabled'}\n🧠 Groq: {'✅ Enabled' if GROQ_API_KEY else '❌ Disabled'}\n📢 Channel: {CHANNEL_ID}\n👤 Owner: {OWNER_ID if OWNER_ID != 0 else 'Everyone allowed'}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *Help Guide*\n\n"
        "📌 Features:\n"
        "• Live prices of 7 top coins\n"
        "• Instant signal based on RSI, MACD, Bollinger\n"
        "• Advanced technical analysis with real indicators\n"
        "• Market trap detection\n"
        "• AI analysis (Groq - optional)\n"
        "• Auto signals every 5 minutes to channel\n\n"
        "⚠️ Disclaimer: Educational only – trade at your own risk."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("waiting_ai"):
        await ai_chat_handler(update, context)
    else:
        await update.message.reply_text("Please use the menu buttons or /start.")

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
        await query.edit_message_text("Under development...")

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

    logger.info("Ultimate Crypto Bot started successfully.")
    app.run_polling()

if __name__ == "__main__":
    main()

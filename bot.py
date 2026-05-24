# =========================================================
# 🚀 ULTRA AI CRYPTO BOT - PROFESSIONAL EDITION
# CoinEx + Groq + Multi TimeFrame + Smart Money
# =========================================================

import os
import json
import time
import hmac
import hashlib
import random
import sqlite3
import asyncio
import logging
import numpy as np
import httpx

from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# =========================================================
# ENV
# =========================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")

ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

REAL_TRADE_ENABLED = False

# =========================================================
# SYMBOLS
# =========================================================

SYMBOLS = {
    "BTCUSDT": {"name": "Bitcoin", "emoji": "👑"},
    "ETHUSDT": {"name": "Ethereum", "emoji": "💎"},
    "SOLUSDT": {"name": "Solana", "emoji": "⚡"},
    "XRPUSDT": {"name": "Ripple", "emoji": "💧"},
    "BNBUSDT": {"name": "BNB", "emoji": "🟡"},
    "DOGEUSDT": {"name": "Doge", "emoji": "🐕"},
}

# =========================================================
# TIMEFRAMES
# =========================================================

TIMEFRAMES = {
    "5m": "5min",
    "15m": "15min",
    "1h": "1hour",
    "4h": "4hour",
    "12h": "12hour",
    "1d": "1day",
    "3d": "3day",
    "1w": "1week"
}

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("ultra_ai_bot.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    side TEXT,
    entry REAL,
    exit REAL,
    pnl REAL,
    confidence INTEGER,
    created_at TEXT
)
""")

conn.commit()

# =========================================================
# DEMO PORTFOLIO
# =========================================================

demo_balance = 10000

positions = []

# =========================================================
# COINEX API
# =========================================================

async def get_coinex_price(symbol):

    try:

        async with httpx.AsyncClient(timeout=15) as client:

            url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"

            r = await client.get(url)

            data = r.json()

            if data["code"] == 0:

                ticker = data["data"]["ticker"]

                return {
                    "price": float(ticker["last"]),
                    "change": float(ticker["change"]),
                    "volume": float(ticker["vol"])
                }

    except Exception as e:
        logger.error(e)

    return None

# =========================================================
# KLINES
# =========================================================

async def get_historical_klines(symbol, timeframe="5m", limit=200):

    try:

        tf = TIMEFRAMES.get(timeframe, "5min")

        async with httpx.AsyncClient(timeout=15) as client:

            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type={tf}&limit={limit}"

            r = await client.get(url)

            data = r.json()

            if data["code"] == 0:

                klines = data["data"]

                return {
                    "open": [float(k[1]) for k in klines],
                    "high": [float(k[2]) for k in klines],
                    "low": [float(k[3]) for k in klines],
                    "close": [float(k[4]) for k in klines],
                    "volume": [float(k[5]) for k in klines],
                }

    except Exception as e:
        logger.error(e)

    return None

# =========================================================
# INDICATORS
# =========================================================

def calculate_sma(data, period):

    if len(data) < period:
        return data[-1]

    return sum(data[-period:]) / period

# ---------------------------------------------------------

def ema_series(data, period):

    multiplier = 2 / (period + 1)

    ema = [data[0]]

    for price in data[1:]:

        ema.append(
            (price - ema[-1]) * multiplier + ema[-1]
        )

    return ema

# ---------------------------------------------------------

def calculate_ema(data, period):

    return ema_series(data, period)[-1]

# ---------------------------------------------------------

def calculate_rsi(closes, period=14):

    if len(closes) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, len(closes)):

        diff = closes[i] - closes[i - 1]

        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

# ---------------------------------------------------------

def calculate_macd(closes):

    ema12 = ema_series(closes, 12)

    ema26 = ema_series(closes, 26)

    macd_line = []

    for a, b in zip(ema12, ema26):
        macd_line.append(a - b)

    signal_line = ema_series(macd_line, 9)

    histogram = macd_line[-1] - signal_line[-1]

    return macd_line[-1], signal_line[-1], histogram

# ---------------------------------------------------------

def calculate_bollinger(closes, period=20):

    if len(closes) < period:
        return None, None, None

    sma = calculate_sma(closes, period)

    std = np.std(closes[-period:])

    upper = sma + (std * 2)

    lower = sma - (std * 2)

    return upper, sma, lower

# ---------------------------------------------------------

def calculate_atr(high, low, close, period=14):

    trs = []

    for i in range(1, len(close)):

        tr = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1])
        )

        trs.append(tr)

    return sum(trs[-period:]) / period

# ---------------------------------------------------------

def calculate_obv(closes, volume):

    obv = 0

    for i in range(1, len(closes)):

        if closes[i] > closes[i - 1]:
            obv += volume[i]

        elif closes[i] < closes[i - 1]:
            obv -= volume[i]

    return obv

# ---------------------------------------------------------

def calculate_supertrend(high, low, close):

    atr = calculate_atr(high, low, close)

    hl2 = (high[-1] + low[-1]) / 2

    upperband = hl2 + (3 * atr)

    lowerband = hl2 - (3 * atr)

    if close[-1] > upperband:
        return "BUY"

    if close[-1] < lowerband:
        return "SELL"

    return "HOLD"

# ---------------------------------------------------------

def calculate_vwap(high, low, close, volume):

    typical = []

    for h, l, c in zip(high, low, close):

        typical.append((h + l + c) / 3)

    pv = []

    for tp, v in zip(typical, volume):

        pv.append(tp * v)

    return sum(pv) / sum(volume)

# =========================================================
# SMART MONEY
# =========================================================

def detect_whale(volume):

    avg = np.mean(volume[:-1])

    last = volume[-1]

    if last > avg * 3:
        return True

    return False

# =========================================================
# MARKET REGIME
# =========================================================

def market_regime(adx, atr):

    if adx > 30 and atr > 0:
        return "TRENDING"

    if adx < 20:
        return "RANGING"

    return "VOLATILE"

# =========================================================
# SIGNAL ENGINE
# =========================================================

def generate_signal(klines, current_price, change):

    close = klines["close"]
    high = klines["high"]
    low = klines["low"]
    volume = klines["volume"]

    buy_score = 0
    sell_score = 0

    analysis = []

    # RSI

    rsi = calculate_rsi(close)

    if rsi < 30:
        buy_score += 20
        analysis.append("RSI Oversold")

    elif rsi > 70:
        sell_score += 20
        analysis.append("RSI Overbought")

    # MACD

    macd, signal, hist = calculate_macd(close)

    if macd > signal:
        buy_score += 20
        analysis.append("MACD Bullish")

    else:
        sell_score += 20
        analysis.append("MACD Bearish")

    # EMA

    ema20 = calculate_ema(close, 20)

    ema50 = calculate_ema(close, 50)

    if ema20 > ema50:
        buy_score += 20
        analysis.append("EMA Bullish")

    else:
        sell_score += 20
        analysis.append("EMA Bearish")

    # Bollinger

    upper, middle, lower = calculate_bollinger(close)

    if lower and current_price <= lower:
        buy_score += 15
        analysis.append("Lower Bollinger Touch")

    if upper and current_price >= upper:
        sell_score += 15
        analysis.append("Upper Bollinger Touch")

    # SuperTrend

    st = calculate_supertrend(high, low, close)

    if st == "BUY":
        buy_score += 15
        analysis.append("SuperTrend BUY")

    elif st == "SELL":
        sell_score += 15
        analysis.append("SuperTrend SELL")

    # VWAP

    vwap = calculate_vwap(high, low, close, volume)

    if current_price > vwap:
        buy_score += 10
        analysis.append("Above VWAP")

    else:
        sell_score += 10
        analysis.append("Below VWAP")

    # OBV

    obv = calculate_obv(close, volume)

    if obv > 0:
        buy_score += 10
        analysis.append("OBV Positive")

    else:
        sell_score += 10
        analysis.append("OBV Negative")

    # Whale

    whale = detect_whale(volume)

    if whale:
        buy_score += 15
        analysis.append("Whale Volume Detected")

    # ADX

    atr = calculate_atr(high, low, close)

    regime = market_regime(30, atr)

    total = buy_score - sell_score

    confidence = min(99, 50 + abs(total))

    if total >= 60:
        signal_text = "🟢 ULTRA LONG"

    elif total >= 30:
        signal_text = "🟢 SMART BUY"

    elif total <= -60:
        signal_text = "🔴 WHALE SHORT"

    elif total <= -30:
        signal_text = "🔴 SMART SELL"

    else:
        signal_text = "⚪ HOLD"

    return {
        "signal": signal_text,
        "confidence": confidence,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "analysis": analysis,
        "rsi": rsi,
        "macd": macd,
        "ema20": ema20,
        "ema50": ema50,
        "atr": atr,
        "vwap": vwap,
        "whale": whale,
        "regime": regime
    }

# =========================================================
# MULTI TIMEFRAME ANALYSIS
# =========================================================

async def multi_timeframe_analysis(symbol):

    timeframes = [
        "5m",
        "15m",
        "1h",
        "4h",
        "12h",
        "1d",
        "3d",
        "1w"
    ]

    results = []

    for tf in timeframes:

        klines = await get_historical_klines(symbol, tf)

        if not klines:
            continue

        price_data = await get_coinex_price(symbol)

        if not price_data:
            continue

        signal = generate_signal(
            klines,
            price_data["price"],
            price_data["change"]
        )

        results.append({
            "tf": tf,
            "signal": signal
        })

    return results

# =========================================================
# GROQ AI
# =========================================================

async def ask_groq(prompt):

    if not GROQ_API_KEY:
        return "Groq API Disabled"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional crypto quant trader."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    try:

        async with httpx.AsyncClient(timeout=60) as client:

            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            data = r.json()

            return data["choices"][0]["message"]["content"]

    except Exception as e:

        logger.error(e)

        return "AI Error"

# =========================================================
# MENU
# =========================================================

def main_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "📊 Live Prices",
                callback_data="prices"
            )
        ],

        [
            InlineKeyboardButton(
                "🎯 AI Signal",
                callback_data="signal"
            )
        ],

        [
            InlineKeyboardButton(
                "📈 Multi TF Analysis",
                callback_data="multi"
            )
        ],

        [
            InlineKeyboardButton(
                "🧠 AI Analysis",
                callback_data="ai"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 Demo Portfolio",
                callback_data="portfolio"
            )
        ],

    ]

    return InlineKeyboardMarkup(keyboard)

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if OWNER_ID != 0:

        if update.effective_user.id != OWNER_ID:

            await update.message.reply_text(
                "⛔ Access Denied"
            )

            return

    text = f"""
🟢🟢🟢🟢🟢

🚀 ULTRA AI CRYPTO BOT

━━━━━━━━━━━━━━━━━━

✅ Multi TimeFrame AI
✅ Smart Money Detection
✅ Whale Detection
✅ Groq AI Analysis
✅ Professional Signals
✅ CoinEx Integration
✅ ATR / VWAP / MACD / RSI
✅ SuperTrend AI
✅ Auto Signal Channel

━━━━━━━━━━━━━━━━━━

🌿 Professional Quant Bot Ready
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )

# =========================================================
# PRICES
# =========================================================

async def prices(update, context):

    query = update.callback_query

    await query.answer()

    txt = "💰 LIVE MARKET\n\n"

    for symbol, info in SYMBOLS.items():

        data = await get_coinex_price(symbol)

        if data:

            emoji = "🟢" if data["change"] > 0 else "🔴"

            txt += (
                f"{emoji} "
                f"{info['emoji']} "
                f"{info['name']} "
                f"${data['price']:,.2f} "
                f"({data['change']:+.2f}%)\n"
            )

    await query.edit_message_text(txt)

# =========================================================
# AI SIGNAL
# =========================================================

async def signal_menu(update, context):

    query = update.callback_query

    await query.answer()

    symbol = "BTCUSDT"

    data = await get_coinex_price(symbol)

    klines = await get_historical_klines(symbol, "1h")

    signal = generate_signal(
        klines,
        data["price"],
        data["change"]
    )

    ai_text = await ask_groq(
        f"""
        Analyze BTC market.

        Signal:
        {signal}

        Give professional trading conclusion.
        """
    )

    text = f"""
🟢🟢🟢🟢🟢

🧠 AI SMART SIGNAL

━━━━━━━━━━━━━━━━━━

👑 BTCUSDT

💰 Price: ${data['price']:,.2f}

📈 Change: {data['change']:+.2f}%

🎯 Signal:
{signal['signal']}

🔥 Confidence:
{signal['confidence']}%

📊 RSI:
{signal['rsi']:.2f}

📊 Regime:
{signal['regime']}

🐋 Whale:
{"YES" if signal['whale'] else "NO"}

━━━━━━━━━━━━━━━━━━

📌 ANALYSIS:

"""

    for item in signal["analysis"]:

        text += f"• {item}\n"

    text += f"""

━━━━━━━━━━━━━━━━━━

🧠 AI CONCLUSION:

{ai_text}

━━━━━━━━━━━━━━━━━━
"""

    await query.edit_message_text(text)

# =========================================================
# MULTI TF
# =========================================================

async def multi_tf(update, context):

    query = update.callback_query

    await query.answer()

    symbol = "BTCUSDT"

    results = await multi_timeframe_analysis(symbol)

    text = "📈 MULTI TIMEFRAME ANALYSIS\n\n"

    for item in results:

        text += (
            f"{item['tf']} → "
            f"{item['signal']['signal']} "
            f"({item['signal']['confidence']}%)\n"
        )

    await query.edit_message_text(text)

# =========================================================
# PORTFOLIO
# =========================================================

async def portfolio(update, context):

    query = update.callback_query

    await query.answer()

    text = f"""
💰 DEMO PORTFOLIO

━━━━━━━━━━━━━━━━━━

Balance:
${demo_balance:,.2f}

Open Positions:
{len(positions)}

━━━━━━━━━━━━━━━━━━
"""

    await query.edit_message_text(text)

# =========================================================
# BUTTON HANDLER
# =========================================================

async def button_handler(update, context):

    query = update.callback_query

    data = query.data

    if data == "prices":

        await prices(update, context)

    elif data == "signal":

        await signal_menu(update, context)

    elif data == "multi":

        await multi_tf(update, context)

    elif data == "portfolio":

        await portfolio(update, context)

# =========================================================
# AUTO CHANNEL SIGNALS
# =========================================================

async def auto_channel_signal(app):

    while True:

        try:

            for symbol in SYMBOLS.keys():

                data = await get_coinex_price(symbol)

                klines = await get_historical_klines(symbol, "1h")

                if not data or not klines:
                    continue

                signal = generate_signal(
                    klines,
                    data["price"],
                    data["change"]
                )

                if signal["confidence"] < 70:
                    continue

                msg = f"""
🟢🟢🟢🟢🟢

🚀 AI SMART SIGNAL

━━━━━━━━━━━━━━━━━━

{symbol}

💰 ${data['price']:,.2f}

📈 {data['change']:+.2f}%

🎯 {signal['signal']}

🔥 Confidence:
{signal['confidence']}%

📊 RSI:
{signal['rsi']:.2f}

📊 Regime:
{signal['regime']}

🐋 Whale:
{"YES" if signal['whale'] else "NO"}

━━━━━━━━━━━━━━━━━━

📌 Analysis:

"""

                for a in signal["analysis"]:

                    msg += f"• {a}\n"

                msg += "\n━━━━━━━━━━━━━━━━━━"

                await app.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg
                )

                await asyncio.sleep(3)

        except Exception as e:

            logger.error(e)

        await asyncio.sleep(300)

# =========================================================
# MAIN
# =========================================================

async def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    asyncio.create_task(
        auto_channel_signal(app)
    )

    logger.info("🚀 ULTRA AI BOT STARTED")

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    await asyncio.Event().wait()

# =========================================================

if __name__ == "__main__":

    asyncio.run(main())

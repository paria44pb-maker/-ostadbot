import os
import requests
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BINANCE = "https://api.binance.com/api/v3"


# -------------------------------
# MARKET DATA
# -------------------------------

def get_klines(symbol="BTCUSDT", interval="1h", limit=200):

    url = f"{BINANCE}/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(url, params=params)

    data = r.json()

    candles = []

    for c in data:
        candles.append({
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5])
        })

    return candles


# -------------------------------
# TECHNICAL ANALYSIS
# -------------------------------

def indicators(candles):

    df = pd.DataFrame(candles)

    df["rsi"] = ta.rsi(df["close"], length=14)

    df["ema20"] = ta.ema(df["close"], length=20)

    df["ema50"] = ta.ema(df["close"], length=50)

    macd = ta.macd(df["close"])

    df["macd"] = macd["MACD_12_26_9"]

    bb = ta.bbands(df["close"])

    df["bb_upper"] = bb["BBU_20_2.0"]

    df["bb_lower"] = bb["BBL_20_2.0"]

    return df


# -------------------------------
# PRICE ACTION
# -------------------------------

def market_structure(df):

    last = df.iloc[-1]

    ema20 = last["ema20"]
    ema50 = last["ema50"]

    if ema20 > ema50:
        trend = "bullish"
    else:
        trend = "bearish"

    rsi = last["rsi"]

    if rsi > 70:
        momentum = "overbought"

    elif rsi < 30:
        momentum = "oversold"

    else:
        momentum = "neutral"

    return {
        "trend": trend,
        "momentum": momentum,
        "rsi": round(rsi,2)
    }


# -------------------------------
# SIGNAL ENGINE
# -------------------------------

def generate_signal(data):

    trend = data["trend"]
    momentum = data["momentum"]

    if trend == "bullish" and momentum != "overbought":

        return "BUY"

    if trend == "bearish" and momentum != "oversold":

        return "SELL"

    return "NEUTRAL"


# -------------------------------
# AI ANALYSIS
# -------------------------------

def ai_summary(structure):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Analyze crypto market data.

    Trend: {structure['trend']}
    RSI: {structure['rsi']}
    Momentum: {structure['momentum']}

    Provide short professional analysis.
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, json=payload, headers=headers)

    data = r.json()

    return data["choices"][0]["message"]["content"]


# -------------------------------
# CHART
# -------------------------------

def chart(df):

    plt.figure(figsize=(10,5))

    plt.plot(df["close"], label="Price")

    plt.plot(df["ema20"], label="EMA20")

    plt.plot(df["ema50"], label="EMA50")

    plt.legend()

    file = "chart.png"

    plt.savefig(file)

    plt.close()

    return file


# -------------------------------
# TELEGRAM COMMANDS
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Crypto AI Bot Ready\n\nUse /analyze"
    )


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    candles = get_klines()

    df = indicators(candles)

    structure = market_structure(df)

    signal = generate_signal(structure)

    analysis = ai_summary(structure)

    img = chart(df)

    msg = f"""
BTC Analysis

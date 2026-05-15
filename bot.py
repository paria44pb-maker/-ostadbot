import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ccxt

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# =====================================
# CONFIG
# =====================================

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"

SYMBOL = "BTC/USDT"
TIMEFRAME = "1h"

# =====================================
# EXCHANGE
# =====================================

exchange = ccxt.binance({
    "enableRateLimit": True
})

# =====================================
# LOAD MARKET DATA
# =====================================

def load_market_data():

    candles = exchange.fetch_ohlcv(
        SYMBOL,
        timeframe=TIMEFRAME,
        limit=300
    )

    df = pd.DataFrame(candles, columns=[
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ])

    return df

# =====================================
# RSI
# =====================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# =====================================
# EMA
# =====================================

def calculate_ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()

# =====================================
# MACD
# =====================================

def calculate_macd(series):

    ema12 = calculate_ema(series, 12)

    ema26 = calculate_ema(series, 26)

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    return macd, signal

# =====================================
# APPLY INDICATORS
# =====================================

def apply_indicators(df):

    df["rsi"] = calculate_rsi(df["close"])

    macd, signal = calculate_macd(df["close"])

    df["macd"] = macd

    df["macd_signal"] = signal

    df["ema50"] = calculate_ema(
        df["close"],
        50
    )

    df["ema200"] = calculate_ema(
        df["close"],
        200
    )

    return df

# =====================================
# MARKET STRUCTURE
# =====================================

def analyze_market(df):

    price = df["close"].iloc[-1]

    rsi = round(df["rsi"].iloc[-1], 2)

    macd = df["macd"].iloc[-1]

    macd_signal = df["macd_signal"].iloc[-1]

    ema50 = df["ema50"].iloc[-1]

    ema200 = df["ema200"].iloc[-1]

    trend = "BULLISH"

    if ema50 < ema200:
        trend = "BEARISH"

    signal = "NEUTRAL"

    if (
        trend == "BULLISH"
        and rsi < 40
        and macd > macd_signal
    ):
        signal = "BUY"

    if (
        trend == "BEARISH"
        and rsi > 60
        and macd < macd_signal
    ):
        signal = "SELL"

    return {
        "price": round(price, 2),
        "trend": trend,
        "signal": signal,
        "rsi": rsi
    }

# =====================================
# AI ANALYSIS
# =====================================

def ai_analysis(data):

    text = f"""
AI MARKET ANALYSIS

Pair: {SYMBOL}

Trend: {data['trend']}

Signal: {data['signal']}

RSI: {data['rsi']}

Current Price: {data['price']}

Interpretation:
The AI engine analyzed momentum,
trend direction and market strength.

Use proper risk management before trading.
"""

    return text

# =====================================
# CHART
# =====================================

def generate_chart(df):

    if not os.path.exists("charts"):
        os.makedirs("charts")

    path = "charts/chart.png"

    plt.figure(figsize=(12, 6))

    plt.plot(df["close"])

    plt.title(f"{SYMBOL} Price Chart")

    plt.xlabel("Candles")

    plt.ylabel("Price")

    plt.grid(True)

    plt.savefig(path)

    plt.close()

    return path

# =====================================
# START COMMAND
# =====================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "AI Trading Bot Activated ✅"
    )

# =====================================
# ANALYZE COMMAND
# =====================================

async def analyze(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        await update.message.reply_text(
            "Analyzing Market..."
        )

        df = load_market_data()

        df = apply_indicators(df)

        result = analyze_market(df)

        analysis = ai_analysis(result)

        chart = generate_chart(df)

        await update.message.reply_photo(
            photo=open(chart, "rb"),
            caption=analysis
        )

    except Exception as e:

        await update.message.reply_text(
            f"Error:\n{str(e)}"
        )

# =====================================
# HELP COMMAND
# =====================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    msg = """
AVAILABLE COMMANDS

/start
Start bot

/analyze
Analyze BTC market

/help
Show commands
"""

    await update.message.reply_text(msg)

# =====================================
# MAIN
# =====================================

def main():

    app = ApplicationBuilder()\
        .token(TELEGRAM_TOKEN)\
        .build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "analyze",
            analyze
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    print("AI BOT RUNNING...")

    app.run_polling()

# =====================================
# RUN
# =====================================

if __name__ == "__main__":

    main()

import pandas as pd
import matplotlib.pyplot as plt

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from config import *
from exchange import get_ohlcv
from indicators import apply_indicators
from smart_money import detect_structure
from ai_engine import generate_ai_text
from risk_manager import calculate_risk

# --------------------
# LOAD DATA
# --------------------

def load_dataframe():

    data = get_ohlcv(SYMBOL, TIMEFRAME)

    df = pd.DataFrame(data, columns=[
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ])

    return df

# --------------------
# GENERATE SIGNAL
# --------------------

def generate_signal(df):

    rsi = df["rsi"].iloc[-1]

    macd = df["macd"].iloc[-1]

    macd_signal = df["macd_signal"].iloc[-1]

    ema50 = df["ema50"].iloc[-1]

    ema200 = df["ema200"].iloc[-1]

    price = df["close"].iloc[-1]

    if (
        rsi < 35 and
        macd > macd_signal and
        ema50 > ema200
    ):
        return "BUY"

    if (
        rsi > 65 and
        macd < macd_signal and
        ema50 < ema200
    ):
        return "SELL"

    return "NEUTRAL"

# --------------------
# CHART
# --------------------

def create_chart(df):

    path = "charts/chart.png"

    plt.figure(figsize=(12,6))

    plt.plot(df["close"])

    plt.title("AI Trading Chart")

    plt.grid(True)

    plt.savefig(path)

    plt.close()

    return path

# --------------------
# COMMANDS
# --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "AI Trading Bot Activated ✅"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    df = load_dataframe()

    df = apply_indicators(df)

    signal = generate_signal(df)

    structure = detect_structure(df)

    rsi = round(df["rsi"].iloc[-1],2)

    entry = round(df["close"].iloc[-1],2)

    stop = round(entry * 0.98,2)

    risk = calculate_risk(entry, stop)

    ai_text = generate_ai_text(
        signal,
        structure,
        rsi
    )

    chart = create_chart(df)

    msg = f"""
PAIR: {SYMBOL}

SIGNAL: {signal}

STRUCTURE: {structure}

RSI: {rsi}

ENTRY: {entry}

STOP LOSS: {stop}

TP1: {risk['tp1']}

TP2: {risk['tp2']}

AI ANALYSIS:
{ai_text}
"""

    await update.message.reply_photo(
        open(chart, "rb"),
        caption=msg
    )

# --------------------
# MAIN
# --------------------

def main():

    app = ApplicationBuilder()\
        .token(TELEGRAM_TOKEN)\
        .build()

    app.add_handler(CommandHandler(
        "start",
        start
    ))

    app.add_handler(CommandHandler(
        "analyze",
        analyze
    ))

    print("AI BOT RUNNING...")

    app.run_polling()

if __name__ == "__main__":

    main()

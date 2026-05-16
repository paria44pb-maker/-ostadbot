import requests
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"


# ------------------------------
# دریافت دیتا از Binance
# ------------------------------
def get_data(symbol="BTCUSDT", interval="1h", limit=150):
    url = (
        f"https://api.binance.com/api/v3/klines?"
        f"symbol={symbol}&interval={interval}&limit={limit}"
    )

    data = requests.get(url).json()

    df = pd.DataFrame(
        data,
        columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "num_trades",
            "taker_base_vol", "taker_quote_vol", "ignore"
        ]
    )

    df["close"] = df["close"].astype(float)

    return df


# ------------------------------
# اندیکاتورها (نسخه‌ی دستی)
# ------------------------------
def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()


def RSI(series, period=14):
    delta = series.diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain = pd.Series(gain).rolling(period).mean()
    loss = pd.Series(loss).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


def MACD(series):
    ema12 = EMA(series, 12)
    ema26 = EMA(series, 26)
    macd = ema12 - ema26
    signal = EMA(macd, 9)
    return macd, signal


def BBANDS(series, period=20):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return upper, lower


# ------------------------------
# تحلیل تکنیکال
# ------------------------------
def analyze(symbol):
    df = get_data(symbol)
    close = df["close"]

    ema20 = EMA(close, 20)
    ema50 = EMA(close, 50)
    rsi = RSI(close)
    macd, signal = MACD(close)
    upper, lower = BBANDS(close)

    price = close.iloc[-1]

    if ema20.iloc[-1] > ema50.iloc[-1]:
        trend = "Bullish"
    elif ema20.iloc[-1] < ema50.iloc[-1]:
        trend = "Bearish"
    else:
        trend = "Sideways"

    return {
        "price": price,
        "trend": trend,
        "rsi": rsi.iloc[-1],
        "macd": macd.iloc[-1],
    }


# ------------------------------
# دستورات تلگرام
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام فرهاد! ربات تحلیل تکنیکال آماده‌ست.\n\n"
        "دستورات:\n"
        "/btc\n"
        "/eth"
    )


async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = analyze("BTCUSDT")
    await update.message.reply_text(
        f"BTC/USDT تحلیل:\n\n"
        f"قیمت: {data['price']:.2f}\n"
        f"Trend: {data['trend']}\n"
        f"RSI: {data['rsi']:.2f}\n"
        f"MACD: {data['macd']:.4f}"
    )


async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = analyze("ETHUSDT")
    await update.message.reply_text(
        f"ETH/USDT تحلیل:\n\n"

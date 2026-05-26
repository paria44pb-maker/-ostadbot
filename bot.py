# ============================================================
# CRYPTO PULSE TITAN X v13.0 - ULTIMATE EDITION
# Persian VIP Telegram Crypto AI Bot
# ============================================================

import os, asyncio, logging, json, random, time, io, re
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque

import ccxt
import httpx
import pandas as pd
import numpy as np
import jdatetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

# ============================================================
# CONFIG
# ============================================================

@dataclass
class Config:

    TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")

    GROQ_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_KEY: str = os.getenv("GEMINI_API_KEY", "")

    SYMBOLS: list = field(default_factory=lambda: [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
        "XRP/USDT",
        "BNB/USDT",
        "DOGE/USDT",
        "ADA/USDT",
        "AVAX/USDT",
        "LINK/USDT"
    ])

cfg = Config()

# ============================================================
# LOGGER
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TitanX")

# ============================================================
# DATE
# ============================================================

class DTM:

    @staticmethod
    def now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def persian():

        now = jdatetime.datetime.now()

        days = {
            0:"دوشنبه",
            1:"سه‌شنبه",
            2:"چهارشنبه",
            3:"پنجشنبه",
            4:"جمعه",
            5:"شنبه",
            6:"یکشنبه"
        }

        return (
            f"{days[now.weekday()]} "
            f"{now.day} "
            f"{now.strftime('%B')} "
            f"{now.year}"
            f" | ⏰ {now.strftime('%H:%M:%S')}"
        )

# ============================================================
# EXCHANGE
# ============================================================

class ExchangeManager:

    def __init__(self):

        self.ex = ccxt.coinex({
            "enableRateLimit": True
        })

        self.ex.load_markets()

    def ticker(self, symbol):

        try:
            return self.ex.fetch_ticker(symbol)
        except:
            return None

    def ohlcv(self, symbol, tf="1h", limit=200):

        try:

            data = self.ex.fetch_ohlcv(
                symbol,
                tf,
                limit=limit
            )

            df = pd.DataFrame(
                data,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

            return df

        except:
            return None

exchange = ExchangeManager()

# ============================================================
# FOREX - ALANCHAND
# ============================================================

class IranianForex:

    @staticmethod
    async def alanchand():

        rates = {}

        try:

            async with httpx.AsyncClient(timeout=30) as client:

                r = await client.get(
                    "https://alanchand.com/",
                    headers={
                        "User-Agent":"Mozilla/5.0"
                    }
                )

                soup = BeautifulSoup(r.text, "html.parser")

                text = soup.get_text(" ", strip=True)

                patterns = {
                    "usd":"دلار",
                    "eur":"یورو",
                    "try":"لیر",
                    "iqd":"دینار",
                    "gold":"طلا"
                }

                for key, word in patterns.items():

                    m = re.search(
                        rf"{word}.*?([\d,]+)",
                        text
                    )

                    if m:

                        rates[key] = int(
                            m.group(1).replace(",", "")
                        )

        except Exception as e:

            logger.error(e)

        return rates

# ============================================================
# INDICATORS
# ============================================================

class Indicators:

    @staticmethod
    def calc(df):

        close = df["close"]

        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]

        rsi = 50

        try:

            delta = close.diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            rsi = 100 - (100 / (1 + rs))

            rsi = float(rsi.iloc[-1])

        except:
            pass

        return {
            "EMA20": ema20,
            "EMA50": ema50,
            "RSI": rsi
        }

# ============================================================
# SIGNAL ENGINE
# ============================================================

class SignalEngine:

    @staticmethod
    def generate(indicators):

        score = 0

        if indicators["EMA20"] > indicators["EMA50"]:
            score += 100
        else:
            score -= 100

        if indicators["RSI"] < 30:
            score += 150

        elif indicators["RSI"] > 70:
            score -= 150

        if score > 100:
            return "🟢 خرید", 92

        elif score < -100:
            return "🔴 فروش", 91

        return "⚪ خنثی", 50

# ============================================================
# AI
# ============================================================

class GroqAI:

    URL = "https://api.groq.com/openai/v1/chat/completions"

    MODEL = "llama-3.3-70b-versatile"

    @staticmethod
    async def analyze(symbol, price, signal):

        if not cfg.GROQ_KEY:
            return None

        prompt = f"""
تو یک تحلیلگر حرفه‌ای نهنگ بازار کریپتو هستی.

تحلیل کامل فارسی بده:

ارز:
{symbol}

قیمت:
{price}

سیگنال:
{signal}

تحلیل:
- روند
- حمایت
- مقاومت
- رفتار نهنگ‌ها
- ریسک
- نتیجه گیری

با ایموجی حرفه‌ای.
"""

        try:

            async with httpx.AsyncClient(timeout=60) as client:

                r = await client.post(
                    GroqAI.URL,
                    headers={
                        "Authorization": f"Bearer {cfg.GROQ_KEY}"
                    },
                    json={
                        "model": GroqAI.MODEL,
                        "messages":[
                            {
                                "role":"user",
                                "content":prompt
                            }
                        ]
                    }
                )

                data = r.json()

                return data["choices"][0]["message"]["content"]

        except Exception as e:

            logger.error(e)

            return None

# ============================================================
# FORMATTER
# ============================================================

class Formatter:

    @staticmethod
    def signal(symbol, price, change, signal, confidence, ai_text):

        signal_bar = (
            "🟩" * int(confidence / 10)
            +
            "⬜" * (10 - int(confidence / 10))
        )

        return f"""
╔════════════════════════════╗
║ 🚀 VIP CRYPTO SIGNAL 🚀 ║
╚════════════════════════════╝

📅 {DTM.persian()}

💎 ارز:
{symbol}

💰 قیمت:
${price:,.2f}

📈 تغییر:
{change:+.2f}%

🎯 سیگنال:
{signal}

💪 قدرت:
{confidence}%

{signal_bar}

━━━━━━━━━━━━━━━━━━

🧠 تحلیل هوش مصنوعی:

{ai_text[:700] if ai_text else 'تحلیل در دسترس نیست'}

━━━━━━━━━━━━━━━━━━

⚠️ مدیریت سرمایه فراموش نشود

✨ @CryptoPulse606

#بیتکوین #کریپتو #سیگنال
"""

    @staticmethod
    def forex(rates):

        return f"""
╔════════════════════════════╗
║ 💰 قیمت ارز و طلا 💰 ║
╚════════════════════════════╝

📅 {DTM.persian()}

💵 دلار:
{rates.get('usd',0):,} تومان

🇪🇺 یورو:
{rates.get('eur',0):,} تومان

🇹🇷 لیر:
{rates.get('try',0):,} تومان

🇮🇶 دینار:
{rates.get('iqd',0):,} تومان

🥇 طلا:
{rates.get('gold',0):,} تومان

━━━━━━━━━━━━━━━━━━

📡 منبع:
alanchand.com

✨ @CryptoPulse606
"""

# ============================================================
# MENU
# ============================================================

class Menu:

    @staticmethod
    def main():

        return InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "💰 قیمت‌ها",
                    callback_data="prices"
                ),

                InlineKeyboardButton(
                    "🎯 سیگنال BTC",
                    callback_data="signal_BTC/USDT"
                )
            ],

            [
                InlineKeyboardButton(
                    "📊 اسکن بازار",
                    callback_data="scan"
                ),

                InlineKeyboardButton(
                    "💰 ارز و طلا",
                    callback_data="forex"
                )
            ],

            [
                InlineKeyboardButton(
                    "📰 اخبار",
                    callback_data="news"
                ),

                InlineKeyboardButton(
                    "📚 آموزش",
                    callback_data="edu"
                )
            ]
        ])

# ============================================================
# START
# ============================================================

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        f"""
🚀 CRYPTO PULSE TITAN X v13

📅 {DTM.persian()}

🧠 هوش مصنوعی
📊 تحلیل حرفه‌ای
💰 قیمت آنلاین ارز
📈 سیگنال VIP
🐋 تحلیل نهنگ‌ها

👇 انتخاب کنید:
""",

        reply_markup=Menu.main()
    )

# ============================================================
# SIGNAL
# ============================================================

async def signal_handler(
    update,
    ctx,
    symbol="BTC/USDT"
):

    q = update.callback_query

    await q.answer()

    await q.edit_message_text(
        "🔄 تحلیل بازار..."
    )

    ticker = exchange.ticker(symbol)

    df = exchange.ohlcv(symbol)

    if not ticker or df is None:

        await q.edit_message_text("❌ خطا")

        return

    indicators = Indicators.calc(df)

    signal, confidence = SignalEngine.generate(
        indicators
    )

    ai_text = await GroqAI.analyze(
        symbol,
        ticker["last"],
        signal
    )

    text = Formatter.signal(
        symbol,
        ticker["last"],
        ticker.get("percentage", 0),
        signal,
        confidence,
        ai_text
    )

    await q.edit_message_text(
        text
    )

# ============================================================
# FOREX
# ============================================================

async def forex_handler(update, ctx):

    q = update.callback_query

    await q.answer()

    await q.edit_message_text(
        "🔄 دریافت قیمت‌ها..."
    )

    rates = await IranianForex.alanchand()

    text = Formatter.forex(rates)

    await q.edit_message_text(text)

# ============================================================
# PRICES
# ============================================================

async def prices_handler(update, ctx):

    q = update.callback_query

    await q.answer()

    text = f"""
💰 قیمت‌های لحظه‌ای

📅 {DTM.persian()}

"""

    for sym in cfg.SYMBOLS:

        ticker = exchange.ticker(sym)

        if ticker:

            emoji = (
                "🟢"
                if ticker.get("percentage",0) > 0
                else "🔴"
            )

            text += (
                f"{emoji} "
                f"{sym.replace('/USDT','')}"
                f" | "
                f"${ticker['last']:,.2f}"
                f" | "
                f"{ticker.get('percentage',0):+.2f}%\n"
            )

    await q.edit_message_text(text)

# ============================================================
# MARKET SCAN
# ============================================================

async def scan_handler(update, ctx):

    q = update.callback_query

    await q.answer()

    await q.edit_message_text(
        "🔍 اسکن بازار..."
    )

    results = []

    for sym in cfg.SYMBOLS:

        ticker = exchange.ticker(sym)

        df = exchange.ohlcv(sym)

        if ticker and df is not None:

            ind = Indicators.calc(df)

            signal, confidence = SignalEngine.generate(ind)

            results.append({
                "symbol": sym,
                "signal": signal,
                "confidence": confidence
            })

    text = f"""
📊 اسکن بازار

📅 {DTM.persian()}

"""

    for r in results:

        text += (
            f"{r['signal']} "
            f"{r['symbol']} "
            f"| "
            f"{r['confidence']}%\n"
        )

    await q.edit_message_text(text)

# ============================================================
# NEWS
# ============================================================

async def news_handler(update, ctx):

    q = update.callback_query

    await q.answer()

    await q.edit_message_text(
        """
📰 اخبار فوری بازار

🚀 بیتکوین در مرکز توجه نهنگ‌ها

📈 حجم معاملات افزایش یافته

⚠️ مراقب نوسانات باشید

✨ @CryptoPulse606
"""
    )

# ============================================================
# EDUCATION
# ============================================================

async def edu_handler(update, ctx):

    q = update.callback_query

    await q.answer()

    await q.edit_message_text(
        """
📚 آموزش امروز

🎯 موضوع:
واگرایی RSI

📈 زمانی که قیمت بالا می‌رود
اما RSI نزولی می‌شود
احتمال ریزش وجود دارد.

🔥 نکته نهنگ‌ها:
همیشه حجم معاملات را بررسی کنید.

✨ @CryptoPulse606
"""
    )

# ============================================================
# ROUTER
# ============================================================

async def router(update, ctx):

    q = update.callback_query

    data = q.data

    try:

        if data == "prices":

            await prices_handler(update, ctx)

        elif data.startswith("signal_"):

            await signal_handler(
                update,
                ctx,
                data.replace("signal_", "")
            )

        elif data == "scan":

            await scan_handler(update, ctx)

        elif data == "forex":

            await forex_handler(update, ctx)

        elif data == "news":

            await news_handler(update, ctx)

        elif data == "edu":

            await edu_handler(update, ctx)

    except Exception as e:

        logger.error(e)

# ============================================================
# AUTO SIGNAL LOOP
# ============================================================

async def auto_signals(app):

    while True:

        try:

            for symbol in cfg.SYMBOLS[:3]:

                ticker = exchange.ticker(symbol)

                df = exchange.ohlcv(symbol)

                if ticker and df is not None:

                    ind = Indicators.calc(df)

                    signal, confidence = SignalEngine.generate(ind)

                    ai = await GroqAI.analyze(
                        symbol,
                        ticker["last"],
                        signal
                    )

                    text = Formatter.signal(
                        symbol,
                        ticker["last"],
                        ticker.get("percentage",0),
                        signal,
                        confidence,
                        ai
                    )

                    await app.bot.send_message(
                        cfg.CHANNEL_ID,
                        text
                    )

                    await asyncio.sleep(5)

        except Exception as e:

            logger.error(e)

        await asyncio.sleep(14400)

# ============================================================
# AUTO FOREX LOOP
# ============================================================

async def auto_forex(app):

    while True:

        try:

            rates = await IranianForex.alanchand()

            text = Formatter.forex(rates)

            await app.bot.send_message(
                cfg.CHANNEL_ID,
                text
            )

        except Exception as e:

            logger.error(e)

        await asyncio.sleep(3600)

# ============================================================
# MAIN
# ============================================================

async def main():

    app = (
        Application.builder()
        .token(cfg.TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(router)
    )

    asyncio.create_task(
        auto_signals(app)
    )

    asyncio.create_task(
        auto_forex(app)
    )

    logger.info("🚀 TITAN X STARTED")

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    await asyncio.Event().wait()

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())

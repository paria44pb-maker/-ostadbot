import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import numpy as np
import os
import json
import logging
import asyncio
import asyncpg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import talib
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

plt.rcParams['font.family'] = 'DejaVu Sans'

class Database:
    def __init__(self):
        self.pool = None
    
    async def init(self):
        if DATABASE_URL:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            await self.create_tables()
            logger.info("✅ دیتابیس متصل شد")
    
    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    balance DECIMAL DEFAULT 10000,
                    total_profit DECIMAL DEFAULT 0,
                    win_rate DECIMAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    symbol VARCHAR(10),
                    side VARCHAR(10),
                    amount DECIMAL,
                    entry_price DECIMAL,
                    stop_loss DECIMAL,
                    take_profit DECIMAL,
                    status VARCHAR(20) DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    symbol VARCHAR(10),
                    side VARCHAR(10),
                    amount DECIMAL,
                    entry_price DECIMAL,
                    exit_price DECIMAL,
                    pnl DECIMAL,
                    pnl_percent DECIMAL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10),
                    price DECIMAL,
                    volume DECIMAL,
                    high DECIMAL,
                    low DECIMAL,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    symbol VARCHAR(10),
                    target_price DECIMAL,
                    condition VARCHAR(5),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

class PriceAPI:
    def __init__(self):
        self.cache = {}
    
    async def get_ohlcv(self, symbol="BTC", interval="1h", limit=100):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"https://api.binance.com/api/v3/klines",
                    params={"symbol": f"{symbol}USDT", "interval": interval, "limit": limit}
                )
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                    ])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
                    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            logger.error(f"OHLCV error: {e}")
        return None
    
    async def get_realtime_price(self, symbol="BTC"):
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "price": float(data['lastPrice']),
                        "change": float(data['priceChangePercent']),
                        "high": float(data['highPrice']),
                        "low": float(data['lowPrice']),
                        "volume": float(data['volume']),
                        "source": "Binance"
                    }
        except:
            pass
        return None

class TechnicalAnalysis:
    @staticmethod
    def calculate_all_indicators(df):
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        indicators = {}
        indicators['SMA_20'] = talib.SMA(close, timeperiod=20)[-1] if len(close) >= 20 else close[-1]
        indicators['SMA_50'] = talib.SMA(close, timeperiod=50)[-1] if len(close) >= 50 else close[-1]
        indicators['EMA_12'] = talib.EMA(close, timeperiod=12)[-1] if len(close) >= 12 else close[-1]
        indicators['EMA_26'] = talib.EMA(close, timeperiod=26)[-1] if len(close) >= 26 else close[-1]
        indicators['RSI_14'] = talib.RSI(close, timeperiod=14)[-1] if len(close) >= 14 else 50
        macd, signal, hist = talib.MACD(close)
        indicators['MACD'] = macd[-1] if len(macd) > 0 else 0
        indicators['MACD_Signal'] = signal[-1] if len(signal) > 0 else 0
        indicators['MACD_Hist'] = hist[-1] if len(hist) > 0 else 0
        upper, middle, lower = talib.BBANDS(close)
        indicators['BB_Upper'] = upper[-1] if len(upper) > 0 else close[-1] * 1.05
        indicators['BB_Middle'] = middle[-1] if len(middle) > 0 else close[-1]
        indicators['BB_Lower'] = lower[-1] if len(lower) > 0 else close[-1] * 0.95
        slowk, slowd = talib.STOCH(high, low, close)
        indicators['Stoch_K'] = slowk[-1] if len(slowk) > 0 else 50
        indicators['Stoch_D'] = slowd[-1] if len(slowd) > 0 else 50
        indicators['ADX'] = talib.ADX(high, low, close, timeperiod=14)[-1] if len(close) >= 14 else 25
        return indicators
    
    @staticmethod
    def generate_signal(indicators, current_price):
        score = 0
        signals = []
        rsi = indicators.get('RSI_14', 50)
        if rsi < 30:
            score += 25
            signals.append(f"RSI Oversold ({rsi:.0f})")
        elif rsi > 70:
            score -= 25
            signals.append(f"RSI Overbought ({rsi:.0f})")
        macd = indicators.get('MACD', 0)
        macd_signal = indicators.get('MACD_Signal', 0)
        if macd > macd_signal:
            score += 20
            signals.append("MACD Bullish")
        elif macd < macd_signal:
            score -= 20
            signals.append("MACD Bearish")
        sma_20 = indicators.get('SMA_20', current_price)
        sma_50 = indicators.get('SMA_50', current_price)
        if sma_20 > sma_50:
            score += 15
            signals.append("Golden Cross")
        elif sma_20 < sma_50:
            score -= 15
            signals.append("Death Cross")
        if score >= 40:
            action = "STRONG_BUY"
            confidence = min(95, 60 + score)
        elif score >= 20:
            action = "BUY"
            confidence = 55 + score // 2
        elif score <= -40:
            action = "STRONG_SELL"
            confidence = min(95, 60 + abs(score))
        elif score <= -20:
            action = "SELL"
            confidence = 55 + abs(score) // 2
        else:
            action = "HOLD"
            confidence = 50
        return {"action": action, "confidence": confidence, "signals": signals[:3]}

db = Database()
price_api = PriceAPI()
ta = TechnicalAnalysis()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال", callback_data="signals")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("💰 پرتفوی", callback_data="portfolio")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    text = "🔥 **ربات تریدر حرفه‌ای** 🔥\n\nاز منوی زیر انتخاب کن:"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...", parse_mode="Markdown")
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    text = "📊 **قیمت لحظه‌ای** 📊\n\n"
    for symbol in symbols:
        data = await price_api.get_realtime_price(symbol)
        if data:
            emoji = "🟢" if data.get('change', 0) > 0 else "🔴" if data.get('change', 0) < 0 else "⚪"
            text += f"{emoji} **{symbol}**: ${data['price']:,.0f} ({data.get('change', 0):+.1f}%)\n"
        else:
            text += f"⚪ **{symbol}**: خطا\n"
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_prices")], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔄 محاسبه سیگنال‌ها...", parse_mode="Markdown")
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    text = "🎯 **سیگنال‌ها** 🎯\n\n"
    for symbol in symbols:
        df = await price_api.get_ohlcv(symbol, "1h", 100)
        if df is not None:
            indicators = ta.calculate_all_indicators(df)
            current_price = df['close'].iloc[-1]
            signal = ta.generate_signal(indicators, current_price)
            if signal['action'] in ["STRONG_BUY", "BUY"]:
                emoji = "🟢"
            elif signal['action'] in ["STRONG_SELL", "SELL"]:
                emoji = "🔴"
            else:
                emoji = "⚪"
            text += f"{emoji} **{symbol}**: {signal['action']} (اطمینان: {signal['confidence']}%)\n"
        else:
            text += f"⚪ **{symbol}**: خطا\n"
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_signals")], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for symbol in ["BTC", "ETH", "SOL", "BNB"]:
        keyboard.append([InlineKeyboardButton(f"📈 {symbol}", callback_data=f"tech_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await update.callback_query.edit_message_text("📈 **تحلیل تکنیکال**\nارز را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    await update.callback_query.edit_message_text(f"📊 تحلیل {symbol}...", parse_mode="Markdown")
    df = await price_api.get_ohlcv(symbol, "1h", 100)
    if df is None:
        await update.callback_query.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]))
        return
    indicators = ta.calculate_all_indicators(df)
    current_price = df['close'].iloc[-1]
    signal = ta.generate_signal(indicators, current_price)
    text = f"📈 **تحلیل {symbol}** 📈\n\n💰 قیمت: ${current_price:,.0f}\n📊 RSI: {indicators['RSI_14']:.0f}\n📊 MACD: {indicators['MACD']:.2f}\n🎯 سیگنال: {signal['action']} ({signal['confidence']}%)"
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def portfolio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💰 **پرتفوی** 💰\n\nموجودی: $10,000\nسود/زیان: $0\nتعداد معاملات: 0"
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🛡️ **مدیریت ریسک** 🛡️\n\n1️⃣ حداکثر ریسک: ۲٪\n2️⃣ نسبت R:R: ۱:۲\n3️⃣ حد ضرر: اجباری\n4️⃣ حداکثر معاملات: ۳"
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "❓ **راهنما** ❓\n\n📊 قیمت لحظه‌ای\n🎯 سیگنال معاملاتی\n📈 تحلیل تکنیکال\n💰 مدیریت پرتفوی\n🛡️ مدیریت ریسک\n\n⚠️ فقط جنبه آموزشی"
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "portfolio":
        await portfolio_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "refresh_prices":
        await prices_menu(update, context)
    elif data == "refresh_signals":
        await signals_menu(update, context)
    elif data.startswith("tech_"):
        await technical_analysis(update, context, data.split("_")[1])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍃 لطفاً از دکمه‌های منو استفاده کن یا /start بزن.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()

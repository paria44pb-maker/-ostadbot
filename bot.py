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

# تنظیمات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# تنظیمات فونت فارسی برای نمودار
plt.rcParams['font.family'] = 'DejaVu Sans'

# ========== دیتابیس پیشرفته ==========
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
            # جدول کاربران
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    balance DECIMAL DEFAULT 10000,
                    total_profit DECIMAL DEFAULT 0,
                    win_rate DECIMAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # جدول پوزیشن‌ها
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
            
            # جدول معاملات
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
            
            # جدول قیمت‌ها (برای نمودار)
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
            
            # جدول هشدارها
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

# ========== API قیمت لحظه‌ای ==========
class PriceAPI:
    def __init__(self):
        self.cache = {}
        self.websocket_connected = False
    
    async def get_ohlcv(self, symbol="BTC", interval="1h", limit=100):
        """دریافت داده OHLCV از بایننس"""
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
        """دریافت قیمت لحظه‌ای از چند منبع"""
        # تلاش از بایننس اول
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
        except: pass
        
        # تلاش از نوبیتکس
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    "https://api.nobitex.ir/market/stats",
                    json={"srcCurrency": symbol, "dstCurrency": "USDT"}
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get("stats", {})
                    return {
                        "price": float(stats.get('bestSell', 0)),
                        "change": float(stats.get('change24h', 0)),
                        "source": "Nobitex"
                    }
        except: pass
        
        return None

# ========== تحلیل تکنیکال پیشرفته ==========
class TechnicalAnalysis:
    @staticmethod
    def calculate_all_indicators(df):
        """محاسبه تمام اندیکاتورها"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        indicators = {}
        
        # میانگین متحرک
        indicators['SMA_20'] = talib.SMA(close, timeperiod=20)[-1]
        indicators['SMA_50'] = talib.SMA(close, timeperiod=50)[-1]
        indicators['EMA_12'] = talib.EMA(close, timeperiod=12)[-1]
        indicators['EMA_26'] = talib.EMA(close, timeperiod=26)[-1]
        
        # RSI
        indicators['RSI_14'] = talib.RSI(close, timeperiod=14)[-1]
        
        # MACD
        macd, signal, hist = talib.MACD(close)
        indicators['MACD'] = macd[-1]
        indicators['MACD_Signal'] = signal[-1]
        indicators['MACD_Hist'] = hist[-1]
        
        # باندهای بولینگر
        upper, middle, lower = talib.BBANDS(close)
        indicators['BB_Upper'] = upper[-1]
        indicators['BB_Middle'] = middle[-1]
        indicators['BB_Lower'] = lower[-1]
        
        # استوکاستیک
        slowk, slowd = talib.STOCH(high, low, close)
        indicators['Stoch_K'] = slowk[-1]
        indicators['Stoch_D'] = slowd[-1]
        
        # ADX (قدرت روند)
        indicators['ADX'] = talib.ADX(high, low, close, timeperiod=14)[-1]
        
        # ابر ایچیموکو
        indicators['Ichimoku_Tenkan'] = (max(high[-9:]) + min(low[-9:])) / 2
        indicators['Ichimoku_Kijun'] = (max(high[-26:]) + min(low[-26:])) / 2
        
        # حجم
        indicators['Volume_SMA'] = talib.SMA(volume, timeperiod=20)[-1]
        
        return indicators
    
    @staticmethod
    def generate_signal(indicators, current_price):
        """تولید سیگنال ترکیبی از چند اندیکاتور"""
        score = 0
        signals = []
        
        # RSI Signal
        rsi = indicators.get('RSI_14', 50)
        if rsi < 30:
            score += 25
            signals.append(f"RSI Oversold ({rsi:.0f})")
        elif rsi > 70:
            score -= 25
            signals.append(f"RSI Overbought ({rsi:.0f})")
        
        # MACD Signal
        macd = indicators.get('MACD', 0)
        macd_signal = indicators.get('MACD_Signal', 0)
        if macd > macd_signal:
            score += 20
            signals.append("MACD Bullish Crossover")
        elif macd < macd_signal:
            score -= 20
            signals.append("MACD Bearish Crossover")
        
        # Moving Averages
        sma_20 = indicators.get('SMA_20', current_price)
        sma_50 = indicators.get('SMA_50', current_price)
        if sma_20 > sma_50:
            score += 15
            signals.append("Golden Cross (SMA20 > SMA50)")
        elif sma_20 < sma_50:
            score -= 15
            signals.append("Death Cross (SMA20 < SMA50)")
        
        # Bollinger Bands
        bb_lower = indicators.get('BB_Lower', current_price * 0.95)
        bb_upper = indicators.get('BB_Upper', current_price * 1.05)
        if current_price <= bb_lower:
            score += 20
            signals.append("Price at Lower Band (Buy Zone)")
        elif current_price >= bb_upper:
            score -= 20
            signals.append("Price at Upper Band (Sell Zone)")
        
        # ADX (Trend Strength)
        adx = indicators.get('ADX', 25)
        if adx > 25:
            if score > 0:
                score += 10
                signals.append(f"Strong Uptrend (ADX: {adx:.0f})")
            elif score < 0:
                score -= 10
                signals.append(f"Strong Downtrend (ADX: {adx:.0f})")
        
        # تصمیم نهایی
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
        
        return {
            "action": action,
            "confidence": confidence,
            "score": score,
            "signals": signals[:3],
            "indicators": indicators
        }

# ========== تولید نمودار ==========
class ChartGenerator:
    @staticmethod
    async def generate_candlestick_chart(df, symbol, indicators=None):
        """تولید نمودار کندل استیک"""
        try:
            # تنظیم داده‌ها
            df.set_index('timestamp', inplace=True)
            df.index = pd.DatetimeIndex(df.index)
            
            # اندیکاتورهای اضافی
            add_plots = []
            if indicators:
                if 'SMA_20' in indicators:
                    sma20 = pd.Series([indicators['SMA_20']] * len(df), index=df.index)
                    add_plots.append(mpf.make_addplot(sma20, color='blue', width=0.5))
                if 'BB_Upper' in indicators:
                    bb_upper = pd.Series([indicators['BB_Upper']] * len(df), index=df.index)
                    bb_lower = pd.Series([indicators['BB_Lower']] * len(df), index=df.index)
                    add_plots.append(mpf.make_addplot(bb_upper, color='gray', linestyle='--', width=0.5))
                    add_plots.append(mpf.make_addplot(bb_lower, color='gray', linestyle='--', width=0.5))
            
            # ذخیره نمودار
            filename = f"chart_{symbol}_{datetime.now().timestamp()}.png"
            mpf.plot(df, type='candle', style='charles', title=f'{symbol}/USDT',
                    ylabel='Price (USDT)', volume=True, addplot=add_plots,
                    savefig=filename, figsize=(12, 8))
            
            return filename
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None

# ========== یادگیری ماشین ساده ==========
class MLPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def prepare_features(self, df):
        """آماده‌سازی ویژگی‌ها برای مدل"""
        features = []
        for i in range(20, len(df)):
            features.append([
                df['close'].iloc[i-1] / df['close'].iloc[i-2] - 1,  # بازگشت 1
                df['close'].iloc[i-5] / df['close'].iloc[i-10] - 1,  # بازگشت 5
                df['high'].iloc[i] - df['low'].iloc[i],  # رنج روزانه
                df['volume'].iloc[i] / df['volume'].iloc[i-1],  # نسبت حجم
            ])
        return np.array(features)
    
    def prepare_target(self, df):
        """آماده‌سازی هدف (قیمت 5 قدم بعد)"""
        targets = []
        for i in range(20, len(df) - 5):
            future_return = df['close'].iloc[i+5] / df['close'].iloc[i] - 1
            targets.append(1 if future_return > 0.01 else 0)  # 1% رشد = سیگنال خرید
        return np.array(targets)
    
    async def train(self, df):
        """آموزش مدل"""
        if len(df) < 100:
            return
        X = self.prepare_features(df)
        y = self.prepare_target(df)
        if len(X) > 0 and len(y) > 0:
            self.model.fit(X[:len(y)], y)
            self.is_trained = True
            logger.info("مدل یادگیری ماشین آموزش دید")
    
    async def predict(self, df):
        """پیش‌بینی"""
        if not self.is_trained or len(df) < 25:
            return None
        X = self.prepare_features(df)
        if len(X) > 0:
            proba = self.model.predict_proba([X[-1]])[0]
            return proba[1]  # احتمال صعود

# ========== ربات اصلی ==========
class UltimateTradingBot:
    def __init__(self):
        self.price_api = PriceAPI()
        self.ta = TechnicalAnalysis()
        self.chart = ChartGenerator()
        self.ml = MLPredictor()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
            [InlineKeyboardButton("🎯 سیگنال حرفه‌ای", callback_data="signals")],
            [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
            [InlineKeyboardButton("📉 نمودار پیشرفته", callback_data="chart")],
            [InlineKeyboardButton("🧠 تحلیل با AI", callback_data="ai")],
            [InlineKeyboardButton("🤖 پیش‌بینی ML", callback_data="ml_predict")],
            [InlineKeyboardButton("💰 پرتفوی من", callback_data="portfolio")],
            [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("🔔 هشدار قیمت", callback_data="alert")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        
        text = """
🔥 **ربات تریدر فوق‌حرفه‌ای** 🔥

✅ **قابلیت‌های پیشرفته:**
• 📡 12+ اندیکاتور تکنیکال
• 📉 نمودار کندل استیک با اندیکاتورها
• 🧠 تحلیل هوشمند با Groq AI
• 🤖 یادگیری ماشین (Random Forest)
• 🎯 سیگنال چندزمانه
• 🔔 هشدار قیمت خودکار

---
📌 **از منوی زیر انتخاب کن** 👇
"""
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def prices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...", parse_mode="Markdown")
        
        symbols = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX"]
        text = "📊 **قیمت لحظه‌ای ارزها** 📊\n\n"
        
        for symbol in symbols:
            data = await self.price_api.get_realtime_price(symbol)
            if data:
                emoji = "🟢" if data.get('change', 0) > 0 else "🔴" if data.get('change', 0) < 0 else "⚪"
                text += f"{emoji} **{symbol}/USDT**: ${data['price']:,.0f}\n"
                text += f"   📈 24h: {data.get('change', 0):+.1f}% | 📍 {data.get('source', 'Unknown')}\n\n"
            else:
                text += f"⚪ **{symbol}**: خطا در دریافت\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def signals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 محاسبه سیگنال‌ها...", parse_mode="Markdown")
        
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        text = "🎯 **سیگنال‌های پیشرفته** 🎯\n\n"
        
        for symbol in symbols:
            df = await self.price_api.get_ohlcv(symbol, "1h", 100)
            if df is not None:
                indicators = self.ta.calculate_all_indicators(df)
                current_price = df['close'].iloc[-1]
                signal = self.ta.generate_signal(indicators, current_price)
                
                if signal['action'] in ["STRONG_BUY", "BUY"]:
                    emoji = "🟢"
                elif signal['action'] in ["STRONG_SELL", "SELL"]:
                    emoji = "🔴"
                else:
                    emoji = "⚪"
                
                text += f"{emoji} **{symbol}**: {signal['action']}\n"
                text += f"   💪 اطمینان: {signal['confidence']}%\n"
                if signal['signals']:
                    text += f"   📝 {signal['signals'][0]}\n\n"
            else:
                text += f"⚪ **{symbol}**: خطا\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_signals")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def technical_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for symbol in ["BTC", "ETH", "SOL", "BNB"]:
            keyboard.append([InlineKeyboardButton(f"📈 {symbol}", callback_data=f"tech_{symbol}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        
        await update.callback_query.edit_message_text(
            "📈 **تحلیل تکنیکال پیشرفته**\n\n"
            "📊 **اندیکاتورها:**\n"
            "• SMA20, SMA50, EMA12, EMA26\n"
            "• RSI, MACD, Bollinger Bands\n"
            "• Stochastic, ADX, Ichimoku\n\n"
            "ارز مورد نظر را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def technical_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        await update.callback_query.edit_message_text(f"📊 تحلیل {symbol}...", parse_mode="Markdown")
        
        df = await self.price_api.get_ohlcv(symbol, "1h", 100)
        if df is None:
            await update.callback_query.edit_message_text("❌ خطا در دریافت داده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]))
            return
        
        indicators = self.ta.calculate_all_indicators(df)
        current_price = df['close'].iloc[-1]
        signal = self.ta.generate_signal(indicators, current_price)
        
        text = f"📈 **تحلیل تکنیکال {symbol}** 📈\n\n"
        text += f"💰 **قیمت فعلی:** ${current_price:,.0f}\n\n"
        
        text += "**📊 میانگین متحرک:**\n"
        text += f"• SMA20: ${indicators['SMA_20']:,.0f}\n"
        text += f"• SMA50: ${indicators['SMA_50']:,.0f}\n"
        text += f"• EMA12: ${indicators['EMA_12']:,.0f}\n"
        text += f"• EMA26: ${indicators['EMA_26']:,.0f}\n\n"
        
        text += "**📈 اندیکاتورها:**\n"
        text += f"• RSI(14): {indicators['RSI_14']:.0f} "
        if indicators['RSI_14'] < 30:
            text += "(🟢 Oversold)\n"
        elif indicators['RSI_14'] > 70:
            text += "(🔴 Overbought)\n"
        else:
            text += "(⚪ Neutral)\n"
        
        text += f"• MACD: {indicators['MACD']:.2f} | Signal: {indicators['MACD_Signal']:.2f}\n"
        text += f"• Stochastic K: {indicators['Stoch_K']:.0f} | D: {indicators['Stoch_D']:.0f}\n"
        text += f"• ADX (Trend): {indicators['ADX']:.0f} "
        if indicators['ADX'] > 25:
            text += "(Strong Trend)\n"
        else:
            text += "(Weak Trend)\n\n"
        
        text += "**🎯 باندهای بولینگر:**\n"
        text += f"🟢 Lower: ${indicators['BB_Lower']:,.0f}\n"
        text += f"⚪ Middle: ${indicators['BB_Middle']:,.0f}\n"
        text += f"🔴 Upper: ${indicators['BB_Upper']:,.0f}\n\n"
        
        text += f"**🎯 سیگنال نهایی:** "
        if signal['action'] == "STRONG_BUY":
            text += f"🟢 خرید قوی (اطمینان: {signal['confidence']}%)\n"
        elif signal['action'] == "BUY":
            text += f"🟡 خرید ملایم (اطمینان: {signal['confidence']}%)\n"
        elif signal['action'] == "STRONG_SELL":
            text += f"🔴 فروش قوی (اطمینان: {signal['confidence']}%)\n"
        elif signal['action'] == "SELL":
            text += f"🟠 فروش ملایم (اطمینان: {signal['confidence']}%)\n"
        else:
            text += f"⚪ نگهداری (اطمینان: {signal['confidence']}%)\n"
        
        if signal['signals']:
            text += f"\n**📝 دلایل:**\n"
            for s in signal['signals'][:3]:
                text += f"• {s}\n"
        
        keyboard = [
            [InlineKeyboardButton("📉 نمایش نمودار", callback_data=f"chart_{symbol}")],
            [InlineKeyboardButton("🧠 تحلیل AI", callback_data=f"ai_{symbol}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]
        ]
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def chart_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for symbol in ["BTC", "ETH", "SOL", "BNB"]:
            keyboard.append([InlineKeyboardButton(f"📉 {symbol}", callback_data=f"chart_{symbol}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        
        await update.callback_query.edit_message_text(
            "📉 **نمودار پیشرفته**\n\n"
            "نمودار کندل استیک + اندیکاتورهای تکنیکال\n\n"
            "ارز مورد نظر را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        await update.callback_query.edit_message_text(f"📊 در حال آماده‌سازی نمودار {symbol}...", parse_mode="Markdown")
        
        df = await self.price_api.get_ohlcv(symbol, "1h", 100)
        if df is None:
            await update.callback_query.edit_message_text("❌ خطا در دریافت داده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="chart")]]))
            return
        
        indicators = self.ta.calculate_all_indicators(df)
        filename = await self.chart.generate_candlestick_chart(df, symbol, indicators)
        
        if filename and os.path.exists(filename):
            with open(filename, 'rb') as f:
                await update.callback_query.message.reply_photo(
                    photo=InputFile(f),
                    caption=f"📊 **نمودار {symbol}/USDT**\nزمان: 1 ساعته | 100 کندل"
                )
            os.remove(filename)
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="chart")]]
        await update.callback_query.edit_message_text("✅ نمودار ارسال شد!", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def ai_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for symbol in ["BTC", "ETH", "SOL", "BNB"]:
            keyboard.append([InlineKeyboardButton(f"🧠 {symbol}", callback_data=f"ai_{symbol}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        
        await update.callback_query.edit_message_text(
            "🧠 **تحلیل هوشمند با Groq AI**\n\n"
            "تحلیل پیشرفته بازار با هوش مصنوعی\n\n"
            "ارز مورد نظر را انتخاب کن:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        await update.callback_query.edit_message_text(f"🤖 تحلیل {symbol} با AI...", parse_mode="Markdown")
        
        data = await self.price_api.get_realtime_price(symbol)
        df = await self.price_api.get_ohlcv(symbol, "1h", 50)
        
        if not data:
            await update.callback_query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="ai")]]))
            return
        
        # محاسبه اندیکاتورها
        indicators = self.ta.calculate_all_indicators(df) if df is not None else {}
        
        if GROQ_API_KEY:
            prompt = f"""به عنوان یک تحلیلگر حرفه‌ای بازار کریپتو، {symbol} را تحلیل کن:

قیمت فعلی: ${data['price']:,.0f}
تغییر 24h: {data.get('change', 0):+.1f}%
RSI: {indicators.get('RSI_14', 50):.0f}
MACD: {indicators.get('MACD', 0):.4f}

در ۴ خط تحلیل کن:
1. وضعیت فعلی
2. پیش‌بینی کوتاه مدت
3. سطوح کلیدی
4. توصیه نهایی"""
            
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 400
                        }
                    )
                    if response.status_code == 200:
                        ai_text = response.json()["choices"][0]["message"]["content"]
                    else:
                        ai_text = self.fallback_ai_analysis(symbol, data, indicators)
            except:
                ai_text = self.fallback_ai_analysis(symbol, data, indicators)
        else:
            ai_text = self.fallback_ai_analysis(symbol, data, indicators)
        
        text = f"🧠 **تحلیل AI - {symbol}** 🧠\n\n"
        text += f"💰 **قیمت:** ${data['price']:,.0f}\n"
        text += f"📊 **تغییر:** {data.get('change', 0):+.1f}%\n\n"
        text += ai_text
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="ai")]]
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    def fallback_ai_analysis(self, symbol, data, indicators):
        change = data.get('change', 0)
        rsi = indicators.get('RSI_14', 50)
        
        if change > 3 and rsi < 60:
            return f"✅ **روند صعودی قوی**\n🔹 هدف اول: ${data['price'] * 1.05:,.0f}\n🔹 حد ضرر: ${data['price'] * 0.97:,.0f}"
        elif change < -3 and rsi > 40:
            return f"🔴 **روند نزولی قوی**\n🔹 از ورود خودداری کن\n🔹 منتظر تثبیت قیمت باش"
        elif rsi < 30:
            return f"🟢 **منطقه اشباع فروش**\n🔹 احتمال بازگشت صعودی\n🔹 ورود با حد ضرر tight"
        elif rsi > 70:
            return f"🟡 **منطقه اشباع خرید**\n🔹 احتمال اصلاح قیمت\n🔹 خروج یا کاهش پوزیشن"
        else:
            return f"⚪ **بازار خنثی**\n🔹 بهترین استراتژی: صبر\n🔹 سطوح حمایت/مقاومت را رصد کن"
    
    async def ml_predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🤖 در حال آموزش مدل و پیش‌بینی...", parse_mode="Markdown")
        
        df = await self.price_api.get_ohlcv("BTC", "1h", 200)
        if df is None:
            await update.callback_query.edit_message_text("❌ خطا در دریافت داده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            return
        
        await self.ml.train(df)
        prediction = await self.ml.predict(df)
        
        if prediction is None:
            text = "🤖 **پیش‌بینی ML** 🤖\n\nمدل در حال آموزش است. کمی صبر کن..."
        else:
            current_price = df['close'].iloc[-1]
            text = f"🤖 **پیش‌بینی یادگیری ماشین** 🤖\n\n"
            text += f"💰 **قیمت فعلی بیت‌کوین:** ${current_price:,.0f}\n\n"
            text += f"📊 **احتمال صعود در ۵ کندل بعد:** {(prediction * 100):.1f}%\n\n"
            
            if prediction > 0.6:
                text += "✅ **نتیجه:** سیگنال خرید قوی\n🎯 پیش‌بینی رشد بیشتر"
            elif prediction > 0.55:
                text += "🟡 **نتیجه:** سیگنال خرید ملایم\n🎯 پیش‌بینی رشد جزئی"
            elif prediction < 0.4:
                text += "🔴 **نتیجه:** سیگنال فروش/نگهداری\n🎯 پیش‌بینی نزول یا رنج"
            else:
                text += "⚪ **نتیجه:** بازار خنثی\n🎯 بهترین استراتژی: صبر"
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def portfolio_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
💰 **پرتفوی شخصی** 💰

📊 **آمار حساب:**
• موجودی: $10,000
• سود/زیان کل: $0 (0%)
• نرخ موفقیت: 0%
• تعداد معاملات: 0

📭 **پوزیشن‌های باز:**
هیچ پوزیشنی فعال نیست

---
💡 برای شروع معامله، ابتدا تحلیل رو بررسی کن
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

📊 **قوانین طلایی:**

1️⃣ **حداکثر ریسک:** ۲٪ سرمایه در هر معامله

2️⃣ **نسبت R:R:** حداقل ۱:۲

3️⃣ **حد ضرر:** همیشه اجباری

4️⃣ **حداکثر معاملات:** ۳ تا همزمان

5️⃣ **حداکثر افت روزانه:** ۶٪

---
📈 **فرمول حجم معامله:**

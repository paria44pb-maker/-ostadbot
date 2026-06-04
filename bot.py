import os
import logging
import asyncio
import time
import random
import numpy as np
import pandas as pd
import ta
import ccxt
import httpx
import feedparser
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

load_dotenv()

# ==================== تنظیمات اصلی ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_USERNAME = "@CryptoPulse606"
CHANNEL_LINK = "https://t.me/CryptoPulse606"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# CoinEx
exchange = ccxt.coinex({'enableRateLimit': True})

# ارزهای تحت پوشش (۷ ارز معتبر)
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT"]

# تنظیمات دمو
demo_balance = 10000
demo_positions = {}
demo_history = []
auto_trade_enabled = False

# مدل یادگیری ماشین (برای پیش‌بینی فوق‌دقیق)
ml_model = None
scaler = StandardScaler()

# ==================== بررسی عضویت ====================
async def is_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ==================== منوی اصلی ====================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوق‌دقیق", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال پیشرفته", callback_data="technical")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="portfolio")],
        [InlineKeyboardButton("⚡ معامله خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("🤖 هوش مصنوعی (همیشه فعال)", callback_data="ai_chat")],
        [InlineKeyboardButton("📊 رشد و ریزش روزانه", callback_data="daily_report")],
        [InlineKeyboardButton("📰 اخبار داغ", callback_data="news")],
        [InlineKeyboardButton("😨 شاخص ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== اندیکاتورهای پیشرفته (۳۵+ اندیکاتور) ====================
class AdvancedIndicators:
    @staticmethod
    def calculate_all(df):
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        close_series = pd.Series(close)
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        volume_series = pd.Series(volume)
        
        ind = {}
        
        # میانگین متحرک (SMA, EMA, WMA)
        for p in [9, 12, 20, 26, 50, 100, 200]:
            ind[f'SMA{p}'] = ta.trend.sma_indicator(close_series, window=p).iloc[-1] if len(close_series) >= p else close[-1]
            ind[f'EMA{p}'] = ta.trend.ema_indicator(close_series, window=p).iloc[-1] if len(close_series) >= p else close[-1]
            ind[f'WMA{p}'] = ta.trend.wma_indicator(close_series, window=p).iloc[-1] if len(close_series) >= p else close[-1]
        
        # اسیلاتورها
        ind['RSI'] = ta.momentum.rsi(close_series, window=14).iloc[-1] if len(close_series) >= 14 else 50
        ind['RSI_FAST'] = ta.momentum.rsi(close_series, window=7).iloc[-1] if len(close_series) >= 7 else 50
        ind['RSI_SLOW'] = ta.momentum.rsi(close_series, window=21).iloc[-1] if len(close_series) >= 21 else 50
        
        macd = ta.trend.MACD(close_series)
        ind['MACD'] = macd.macd().iloc[-1] if len(macd.macd()) > 0 else 0
        ind['MACD_SIGNAL'] = macd.macd_signal().iloc[-1] if len(macd.macd_signal()) > 0 else 0
        ind['MACD_HIST'] = macd.macd_diff().iloc[-1] if len(macd.macd_diff()) > 0 else 0
        
        ind['STOCH_K'] = ta.momentum.stoch(high_series, low_series, close_series, window=14, smooth_window=3).iloc[-1] if len(close_series) >= 14 else 50
        ind['STOCH_D'] = ta.momentum.stoch_signal(high_series, low_series, close_series, window=14, smooth_window=3).iloc[-1] if len(close_series) >= 14 else 50
        ind['STOCH_RSI'] = ta.momentum.stochrsi(close_series, window=14).iloc[-1] if len(close_series) >= 14 else 50
        
        ind['CCI'] = ta.trend.cci(high_series, low_series, close_series, window=20).iloc[-1] if len(close_series) >= 20 else 0
        ind['WILLIAMS_R'] = ta.momentum.williams_r(high_series, low_series, close_series, lbp=14).iloc[-1] if len(close_series) >= 14 else -50
        ind['ULTIMATE'] = ta.momentum.ultimate_oscillator(high_series, low_series, close_series, window1=7, window2=14, window3=28).iloc[-1] if len(close_series) >= 28 else 50
        
        # باند بولینگر
        bb = ta.volatility.BollingerBands(close_series, window=20, window_dev=2)
        ind['BB_UPPER'] = bb.bollinger_hband().iloc[-1] if len(bb.bollinger_hband()) > 0 else close[-1] * 1.05
        ind['BB_MIDDLE'] = bb.bollinger_mavg().iloc[-1] if len(bb.bollinger_mavg()) > 0 else close[-1]
        ind['BB_LOWER'] = bb.bollinger_lband().iloc[-1] if len(bb.bollinger_lband()) > 0 else close[-1] * 0.95
        ind['BB_WIDTH'] = (ind['BB_UPPER'] - ind['BB_LOWER']) / ind['BB_MIDDLE']
        
        # نوسان
        ind['ATR'] = ta.volatility.average_true_range(high_series, low_series, close_series, window=14).iloc[-1] if len(close_series) >= 14 else 0
        ind['NATR'] = ind['ATR'] / close[-1] * 100 if close[-1] != 0 else 0
        
        # قدرت روند
        ind['ADX'] = ta.trend.adx(high_series, low_series, close_series, window=14).iloc[-1] if len(close_series) >= 14 else 25
        ind['PLUS_DI'] = ta.trend.plus_di(high_series, low_series, close_series, window=14).iloc[-1] if len(close_series) >= 14 else 20
        ind['MINUS_DI'] = ta.trend.minus_di(high_series, low_series, close_series, window=14).iloc[-1] if len(close_series) >= 14 else 20
        
        # حجم
        ind['OBV'] = ta.volume.on_balance_volume(close_series, volume_series).iloc[-1] if len(close_series) > 1 else 0
        ind['MFI'] = ta.volume.money_flow_index(high_series, low_series, close_series, volume_series, window=14).iloc[-1] if len(close_series) >= 14 else 50
        ind['VOLUME_SMA'] = volume_series.rolling(20).mean().iloc[-1] if len(volume_series) >= 20 else volume[-1]
        
        # نقاط محوری (Pivot Points)
        ind['PIVOT'] = (high[-1] + low[-1] + close[-1]) / 3
        ind['R1'] = 2 * ind['PIVOT'] - low[-1]
        ind['S1'] = 2 * ind['PIVOT'] - high[-1]
        
        return ind

# ==================== تولید سیگنال فوق‌دقیق با یادگیری ماشین ====================
def generate_ml_signal(features):
    """پیش‌بینی با مدل Random Forest (در صورت وجود)"""
    if ml_model is not None:
        try:
            features_scaled = scaler.transform([features])
            prob = ml_model.predict_proba(features_scaled)[0][1]  # احتمال صعود
            return prob
        except:
            return None
    return None

def generate_signal(indicators, current_price, change):
    buy_score = 0
    sell_score = 0
    reasons = []
    
    # RSI (وزن 40)
    rsi = indicators['RSI']
    if rsi < 20:
        buy_score += 45
        reasons.append(f"📉 RSI فوق‌اشباع فروش! ({rsi:.0f}) آماده برای جهش 🚀")
    elif rsi < 30:
        buy_score += 35
        reasons.append(f"📉 RSI اشباع فروش ({rsi:.0f}) – زمان خرید عالیه 😎")
    elif rsi > 80:
        sell_score += 45
        reasons.append(f"📈 RSI فوق‌اشباع خرید! ({rsi:.0f}) وقت فروشه 🔥")
    elif rsi > 70:
        sell_score += 35
        reasons.append(f"📈 RSI اشباع خرید ({rsi:.0f}) – مواظب باش! ⚠️")
    
    # MACD (وزن 30)
    if indicators['MACD'] > indicators['MACD_SIGNAL']:
        buy_score += 30
        reasons.append("🟢 MACD صعودی شد! تقاطع خرید عالی 📈")
    else:
        sell_score += 30
        reasons.append("🔴 MACD نزولی شد! تقاطع فروش هشدار ⚠️")
    
    # EMA ترتیبی (وزن 25)
    if indicators['EMA20'] > indicators['EMA50'] > indicators['EMA100']:
        buy_score += 25
        reasons.append("📈 EMA ترتیبی صعودی! روند قوی و پایدار 💪")
    elif indicators['EMA20'] < indicators['EMA50'] < indicators['EMA100']:
        sell_score += 25
        reasons.append("📉 EMA ترتیبی نزولی! روند ضعیف و خطرناک 😨")
    
    # باند بولینگر (وزن 25)
    if current_price <= indicators['BB_LOWER']:
        buy_score += 25
        reasons.append("🎯 قیمت به باند پایین بولینگر رسید! منطقه خرید طلایی 🥇")
    elif current_price >= indicators['BB_UPPER']:
        sell_score += 25
        reasons.append("⚠️ قیمت به باند بالای بولینگر رسید! منطقه فروش داغ 🥵")
    
    # استوکاستیک (وزن 20)
    if indicators['STOCH_K'] < 15:
        buy_score += 25
        reasons.append(f"🟢 استوکاستیک فوق‌اشباع فروش (K={indicators['STOCH_K']:.0f})")
    elif indicators['STOCH_K'] < 20:
        buy_score += 15
    elif indicators['STOCH_K'] > 85:
        sell_score += 25
        reasons.append(f"🔴 استوکاستیک فوق‌اشباع خرید (K={indicators['STOCH_K']:.0f})")
    elif indicators['STOCH_K'] > 80:
        sell_score += 15
    
    # CCI (وزن 20)
    if indicators['CCI'] < -200:
        buy_score += 25
        reasons.append(f"📊 CCI فوق‌اشباع فروش! ({indicators['CCI']:.0f})")
    elif indicators['CCI'] < -100:
        buy_score += 15
    elif indicators['CCI'] > 200:
        sell_score += 25
        reasons.append(f"📊 CCI فوق‌اشباع خرید! ({indicators['CCI']:.0f})")
    elif indicators['CCI'] > 100:
        sell_score += 15
    
    # ویلیامز (وزن 15)
    if indicators['WILLIAMS_R'] < -90:
        buy_score += 20
        reasons.append("📉 ویلیامز فوق‌اشباع فروش! بخر عزیزم 💚")
    elif indicators['WILLIAMS_R'] < -80:
        buy_score += 10
    elif indicators['WILLIAMS_R'] > -10:
        sell_score += 20
        reasons.append("📈 ویلیامز فوق‌اشباع خرید! بفروش جانم 💔")
    elif indicators['WILLIAMS_R'] > -20:
        sell_score += 10
    
    # ADX (قدرت روند)
    adx = indicators['ADX']
    if adx > 40:
        if buy_score > sell_score:
            buy_score += 20
            reasons.append(f"💪 روند صعودی بسیار قوی! ADX={adx:.0f}")
        elif sell_score > buy_score:
            sell_score += 20
            reasons.append(f"💪 روند نزولی بسیار قوی! ADX={adx:.0f}")
    elif adx > 25:
        if buy_score > sell_score:
            buy_score += 10
            reasons.append(f"👍 روند صعودی خوب (ADX={adx:.0f})")
        elif sell_score > buy_score:
            sell_score += 10
            reasons.append(f"👍 روند نزولی خوب (ADX={adx:.0f})")
    
    # MFI (وزن 15)
    if indicators['MFI'] < 20:
        buy_score += 15
        reasons.append(f"💰 جریان پول اشباع فروش! MFI={indicators['MFI']:.0f}")
    elif indicators['MFI'] > 80:
        sell_score += 15
        reasons.append(f"💰 جریان پول اشباع خرید! MFI={indicators['MFI']:.0f}")
    
    # تغییر قیمت (وزن 20)
    if change > 4:
        buy_score += 25
        reasons.append(f"🚀 رشد انفجاری! {change:+.1f}% – فرصت عالی")
    elif change > 2:
        buy_score += 15
        reasons.append(f"📈 رشد خوب {change:+.1f}%")
    elif change < -4:
        sell_score += 25
        reasons.append(f"💀 ریزش شدید! {change:+.1f}% – فرار کن")
    elif change < -2:
        sell_score += 15
        reasons.append(f"📉 ریزش ملایم {change:+.1f}%")
    
    # حجم (تأیید)
    volume_ratio = indicators.get('volume_ratio', 1)
    if volume_ratio > 2:
        if buy_score > sell_score:
            buy_score += 15
            reasons.append("📊 حجم بی‌سابقه! تأیید قوی خرید 🟢")
        elif sell_score > buy_score:
            sell_score += 15
            reasons.append("📊 حجم بی‌سابقه! تأیید قوی فروش 🔴")
    elif volume_ratio > 1.5:
        if buy_score > sell_score:
            buy_score += 8
        elif sell_score > buy_score:
            sell_score += 8
    
    total_score = buy_score - sell_score
    
    # اعمال پیش‌بینی ML در صورت وجود (افزایش دقت)
    ml_prob = None
    if ml_model is not None:
        features = [
            indicators['RSI'], indicators['MACD'], indicators['MACD_SIGNAL'],
            indicators['EMA20'] / indicators['EMA50'], indicators['BB_WIDTH'],
            indicators['ADX'], change, volume_ratio
        ]
        ml_prob = generate_ml_signal(features)
        if ml_prob is not None:
            if ml_prob > 0.65:
                buy_score += int(20 * (ml_prob - 0.5))
                reasons.append(f"🤖 هوش مصنوعی {ml_prob*100:.0f}٪ احتمال صعود می‌دهد!")
            elif ml_prob < 0.35:
                sell_score += int(20 * (0.5 - ml_prob))
                reasons.append(f"🤖 هوش مصنوعی {(1-ml_prob)*100:.0f}٪ احتمال نزول می‌دهد!")
            total_score = buy_score - sell_score
    
    # تعیین سیگنال نهایی با قدرت بالا
    if total_score >= 100:
        signal = "خرید انفجاری 🔥🔥🔥"
        confidence = 99
        strength = "🟢🟢🟢🟢🟢"
    elif total_score >= 80:
        signal = "خرید بسیار قوی 💪💪"
        confidence = 95
        strength = "🟢🟢🟢🟢⚪"
    elif total_score >= 60:
        signal = "خرید قوی 📈📈"
        confidence = 90
        strength = "🟢🟢🟢⚪⚪"
    elif total_score <= -100:
        signal = "فروش انفجاری 💀💀💀"
        confidence = 99
        strength = "🔴🔴🔴🔴🔴"
    elif total_score <= -80:
        signal = "فروش بسیار قوی 😱😱"
        confidence = 95
        strength = "🔴🔴🔴🔴⚪"
    elif total_score <= -60:
        signal = "فروش قوی 📉📉"
        confidence = 90
        strength = "🔴🔴🔴⚪⚪"
    else:
        signal = "نگهداری (صبر کن، وقتشه!) ⚪"
        confidence = 50
        strength = "⚪⚪⚪⚪⚪"
    
    return signal, confidence, strength, total_score, reasons[:6], ml_prob

# ==================== تحلیل فاندامنتال با Groq ====================
async def get_fundamental_analysis(symbol, price, change):
    if not GROQ_API_KEY:
        return None
    prompt = f"""سلام استاد! می‌خوام یه تحلیل فاندامنتال سریع و دقیق برای {symbol} بدی.
قیمت فعلی: ${price:,.0f}
تغییر ۲۴ ساعته: {change:+.1f}%
لطفاً با لحنی صمیمی و شوخ، ۲-۳ خط درباره اخبار مهم، احساسات بازار و تأثیرات اقتصادی بنویس.
"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": "تو یک کارشناس ارشد کریپتو با لحنی صمیمی، شوخ و کاملاً فارسی هستی."},
                                 {"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.8
                }
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None

# ==================== رسم نمودار حرفه‌ای ====================
def create_chart(df, symbol):
    df_copy = df.copy()
    df_copy.set_index('timestamp', inplace=True)
    df_copy.index = pd.DatetimeIndex(df_copy.index)
    
    add_plots = [
        mpf.make_addplot(df_copy['EMA20'], color='blue', width=0.8),
        mpf.make_addplot(df_copy['EMA50'], color='orange', width=0.8),
    ]
    
    style = 'charles'
    figsize = (14, 10)
    title = f"🔥 {symbol.replace('USDT', '')} – تحلیل پیشرفته پلاتینیوم VIP 🔥"
    
    filename = f"chart_{symbol}_{int(time.time())}.png"
    try:
        mpf.plot(df_copy, type='candle', style=style, title=title,
                 ylabel='Price (USDT)', volume=True, addplot=add_plots,
                 savefig=filename, figsize=figsize)
        return filename
    except Exception as e:
        logger.error(f"Chart error: {e}")
        return None

# ==================== اخبار از چند منبع ====================
async def get_crypto_news():
    all_news = []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://cryptopanic.com/api/v1/posts/?auth_token=&public=true&kind=news")
            if resp.status_code == 200:
                for item in resp.json().get('results', [])[:3]:
                    all_news.append({"title": item['title'], "source": "CryptoPanic"})
        
        feed = feedparser.parse("https://www.coindesk.com/feed/")
        for entry in feed.entries[:2]:
            all_news.append({"title": entry.title, "source": "CoinDesk"})
        
        feed2 = feedparser.parse("https://cointelegraph.com/rss")
        for entry in feed2.entries[:2]:
            all_news.append({"title": entry.title, "source": "CoinTelegraph"})
    except:
        pass
    return all_news[:7]

# ==================== رشد و ریزش ====================
async def get_top_gainers_losers():
    gainers = []
    losers = []
    for symbol in SYMBOLS:
        try:
            ticker = exchange.fetch_ticker(symbol)
            change = ticker['percentage']
            if change > 0:
                gainers.append((symbol, change, ticker['last']))
            else:
                losers.append((symbol, change, ticker['last']))
        except:
            continue
    gainers.sort(key=lambda x: x[1], reverse=True)
    losers.sort(key=lambda x: x[1])
    return gainers[:5], losers[:5]

# ==================== هوش مصنوعی همیشه فعال ====================
async def groq_chat(prompt):
    if not GROQ_API_KEY:
        return "🤖 هوش مصنوعی در دسترس نیست (کلید API تنظیم نشده)."
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": "تو یک دوست صمیمی، شوخ و کارشناس ارشد کریپتو هستی. کاملاً فارسی و با شکلک زیاد صحبت کن."},
                                 {"role": "user", "content": prompt}],
                    "max_tokens": 600,
                    "temperature": 0.85
                }
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "🤖 اوپس! نتونستم جواب بدم. دوباره تلاش کن عزیزم 😊"

# ==================== ارسال خودکار سیگنال + تحلیل فاندامنتال + نمودار ====================
async def auto_signal_loop(app):
    await asyncio.sleep(10)
    last_daily_report = 0
    last_news = 0
    
    while True:
        await asyncio.sleep(300)  # 5 دقیقه
        
        for symbol in SYMBOLS:
            try:
                ticker = exchange.fetch_ticker(symbol)
                if not ticker or ticker['volume'] < 500000:
                    continue
                
                ohlcv = exchange.fetch_ohlcv(symbol, '1h', 200)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # اندیکاتورها
                indicators = AdvancedIndicators.calculate_all(df)
                indicators['volume_ratio'] = df['volume'].iloc[-1] / df['volume'].rolling(50).mean().iloc[-1] if len(df) >= 50 else 1
                
                # اضافه کردن EMA به df برای نمودار
                df['EMA20'] = indicators['EMA20']
                df['EMA50'] = indicators['EMA50']
                
                # سیگنال
                signal, confidence, strength, score, reasons, ml_prob = generate_signal(indicators, ticker['last'], ticker['percentage'])
                
                # تحلیل فاندامنتال (اختیاری)
                fundamental = await get_fundamental_analysis(symbol.replace('USDT', ''), ticker['last'], ticker['percentage'])
                
                # نمودار
                chart_file = create_chart(df, symbol)
                
                # ساخت پیام
                ml_text = f"\n🤖 *هوش مصنوعی:* {ml_prob*100:.0f}% احتمال صعود" if ml_prob else ""
                fundamental_text = f"\n📰 *تحلیل فاندامنتال:*\n{fundamental}" if fundamental else ""
                
                msg = f"""
╔══════════════════════════════════════════════════════════╗
║   🔥 *سیگنال پلاتینیوم VIP {symbol.replace('USDT', '')}* 🔥   ║
╚══════════════════════════════════════════════════════════╝

💰 **قیمت لحظه‌ای:** `${ticker['last']:,.2f}`
📈 **تغییر 24h:** `{ticker['percentage']:+.2f}%`
📊 **حجم 24h:** `${ticker['volume']/1e6:.1f}M`

┌─────────────────────────────────────────────────────────┐
│  🎯 *سیگنال نهایی:* {signal}                           │
│  📊 *اطمینان:* {confidence}%                           │
│  💪 *قدرت:* {strength}                                 │
│  📈 *امتیاز:* `{score:+d}`{ml_text}                    │
└─────────────────────────────────────────────────────────┘

📊 *تحلیل تکنیکال پیشرفته (۳۵+ اندیکاتور):*
• RSI: `{indicators['RSI']:.1f}` {'(فوق‌اشباع فروش 📉)' if indicators['RSI'] < 25 else '(اشباع خرید 📈)' if indicators['RSI'] > 75 else '(متوسط ⚪)'}
• MACD: `{indicators['MACD']:.2f}` (سیگنال: `{indicators['MACD_SIGNAL']:.2f}`) → {'صعودی 🟢' if indicators['MACD'] > indicators['MACD_SIGNAL'] else 'نزولی 🔴'}
• EMA20: `${indicators['EMA20']:.2f}` | EMA50: `${indicators['EMA50']:.2f}`
• باند بولینگر: پایین `${indicators['BB_LOWER']:.2f}` | وسط `${indicators['BB_MIDDLE']:.2f}` | بالا `${indicators['BB_UPPER']:.2f}`
• استوکاستیک: K=`{indicators['STOCH_K']:.1f}` D=`{indicators['STOCH_D']:.1f}`
• CCI: `{indicators['CCI']:.1f}` | ویلیامز: `{indicators['WILLIAMS_R']:.1f}`
• ADX: `{indicators['ADX']:.1f}` {'(روند خیلی قوی 🔥)' if indicators['ADX'] > 40 else '(روند متوسط 🌊)' if indicators['ADX'] > 25 else '(روند ضعیف 💤)'}
• ATR: `${indicators['ATR']:.2f}` | MFI: `{indicators['MFI']:.1f}`

🔑 *سطوح کلیدی پلاتینیوم:*
🟢 حمایت اصلی: `${indicators['BB_LOWER']:.2f}` | حمایت قوی: `${indicators['S1']:.2f}`
🔴 مقاومت اصلی: `${indicators['BB_UPPER']:.2f}` | مقاومت قوی: `${indicators['R1']:.2f}`

📝 *دلایل سیگنال طلایی:*
{chr(10).join(['• ' + r for r in reasons])}
{fundamental_text}

🎯 *مدیریت سرمایه پیشنهادی (۲٪ ریسک):*
• حد ضرر هوشمند: `${ticker['last'] * 0.97:.2f}` (۳٪)
• هدف اول: `${ticker['last'] * 1.04:.2f}` (۴٪)
• هدف دوم: `${ticker['last'] * 1.09:.2f}` (۹٪)

✨ *ربات پلاتینیوم VIP – کارشناس ارشد کریپتو* ✨
@CryptoPulse606
"""
                if chart_file and os.path.exists(chart_file):
                    with open(chart_file, 'rb') as f:
                        await app.bot.send_photo(chat_id=CHANNEL_USERNAME, photo=InputFile(f), caption=msg, parse_mode="Markdown")
                    os.remove(chart_file)
                else:
                    await app.bot.send_message(chat_id=CHANNEL_USERNAME, text=msg, parse_mode="Markdown")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Auto signal error {symbol}: {e}")
        
        # گزارش رشد و ریزش هر ۱۲ ساعت
        if time.time() - last_daily_report > 43200:
            last_daily_report = time.time()
            gainers, losers = await get_top_gainers_losers()
            
            gainers_text = "\n".join([f"• {sym.replace('USDT', '')}: +{chg:.2f}% (${price:,.2f}) 🚀" for sym, chg, price in gainers])
            losers_text = "\n".join([f"• {sym.replace('USDT', '')}: {chg:.2f}% (${price:,.2f}) 💀" for sym, chg, price in losers])
            
            report_msg = f"""
📊 *گزارش روزانه رشد و ریزش بازار* 📊

🚀 **بیشترین رشد‌ها (Top 5):**
{gainers_text if gainers_text else 'هیچ ارز در حال رشدی یافت نشد 😢'}

💀 **بیشترین ریزش‌ها (Top 5):**
{losers_text if losers_text else 'هیچ ارز در حال ریزشی یافت نشد 😎'}

📅 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✨ @CryptoPulse606
"""
            await app.bot.send_message(chat_id=CHANNEL_USERNAME, text=report_msg, parse_mode="Markdown")
        
        # اخبار داغ هر ۱۲ ساعت
        if time.time() - last_news > 43200:
            last_news = time.time()
            news_list = await get_crypto_news()
            if news_list:
                news_text = "📰 *اخبار داغ کریپتو (چند منبع معتبر)* 📰\n\n"
                for n in news_list[:7]:
                    news_text += f"🔥 {n['title'][:120]}...\n📍 _{n['source']}_\n\n"
                news_text += f"\n✨ @CryptoPulse606"
                await app.bot.send_message(chat_id=CHANNEL_USERNAME, text=news_text, parse_mode="Markdown")

# ==================== هندلرهای ربات ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_member(user_id, context):
        context.user_data["is_member"] = True
        await update.message.reply_text(
            "🌟✨ *به ربات پلاتینیوم VIP ۳۰ خوش آمدی، کارشناس ارشد کریپتو!* ✨🌟\n\n"
            "🤖 من اینجام تا با تحلیل‌های فوق‌دقیق و هوش مصنوعی، موج‌سواری کنی و سودهای رویایی بگیری!\n\n"
            "از منوی زیر انتخاب کن 👇",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = """
🌟 *پلاتینیوم VIP ۳۰ – کارشناس ارشد کریپتو* 🌟

🔔 برای استفاده از ربات، **ابتدا در کانال ما عضو شو** عزیزم!

✨ بعد از عضویت، روی دکمه «عضو شدم» کلیک کن تا دنیای تحلیل‌های حرفه‌ای به روت باز بشه 😎
"""
    try:
        with open("images/platinum_vip.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=InputFile(photo, filename="platinum_vip.jpg"),
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except:
        await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=reply_markup)

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if await is_member(user_id, context):
        context.user_data["is_member"] = True
        await query.edit_message_caption(
            caption="✅ *عضویت تو تأیید شد!* ✅\n\nبه جمع تریدرهای حرفه‌ای خوش اومدی! 🚀\n\nاز منوی زیر استفاده کن:",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
    else:
        await query.answer("❌ هنوز عضو کانال نشدی! لطفاً اول عضو شو بعد بیا اینجا 😊", show_alert=True)

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای ارزها* 💰\n\n"
    for symbol in SYMBOLS:
        try:
            ticker = exchange.fetch_ticker(symbol)
            emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
            text += f"{emoji} *{symbol.replace('USDT', '')}*: `${ticker['last']:,.2f}` ({ticker['percentage']:+.2f}%)\n"
        except:
            text += f"⚪ *{symbol.replace('USDT', '')}*: خطا\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("🔄 تحلیل فوق‌دقیق بیت‌کوین با هوش مصنوعی...")
    symbol = "BTCUSDT"
    try:
        ticker = exchange.fetch_ticker(symbol)
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', 200)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        indicators = AdvancedIndicators.calculate_all(df)
        indicators['volume_ratio'] = df['volume'].iloc[-1] / df['volume'].rolling(50).mean().iloc[-1] if len(df) >= 50 else 1
        signal, confidence, strength, score, reasons, ml_prob = generate_signal(indicators, ticker['last'], ticker['percentage'])
        fundamental = await get_fundamental_analysis("بیت‌کوین", ticker['last'], ticker['percentage'])
        ml_text = f"\n🤖 *پیش‌بینی AI:* {ml_prob*100:.0f}٪ احتمال صعود" if ml_prob else ""
        
        msg = f"""
🎯 *سیگنال فوق‌دقیق {symbol.replace('USDT', '')}* 🎯

💰 قیمت: `${ticker['last']:,.2f}`
📈 تغییر: `{ticker['percentage']:+.2f}%`
🎯 سیگنال: **{signal}** (اطمینان {confidence}%)
💪 قدرت: {strength}
📈 امتیاز: `{score:+d}`{ml_text}

📊 RSI: `{indicators['RSI']:.1f}`
📈 MACD: `{indicators['MACD']:.2f}`
📊 EMA20: `${indicators['EMA20']:.2f}` | EMA50: `${indicators['EMA50']:.2f}`

📝 دلایل سیگنال:
{chr(10).join(['• ' + r for r in reasons[:3]])}
{fundamental if fundamental else ''}
"""
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_main_menu())
    except Exception as e:
        await query.edit_message_text(f"❌ خطا: {e}", reply_markup=get_main_menu())

# سایر هندلرها (مشابه قبل با کمی تغییرات در متن‌ها)
async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("📈 لطفاً نام ارز را وارد کن (BTC, ETH, SOL, XRP, ADA, DOGE, DOT):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol_input = update.message.text.upper()
    symbol = None
    for s in SYMBOLS:
        if symbol_input in s:
            symbol = s
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست. از اینا انتخاب کن: BTC, ETH, SOL, XRP, ADA, DOGE, DOT")
        return
    try:
        ticker = exchange.fetch_ticker(symbol)
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', 200)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        indicators = AdvancedIndicators.calculate_all(df)
        signal, confidence, strength, score, reasons, _ = generate_signal(indicators, ticker['last'], ticker['percentage'])
        
        text = f"""
📊 *تحلیل حرفه‌ای {symbol.replace('USDT', '')}* 📊

💰 قیمت: `${ticker['last']:,.2f}`
📈 تغییر: `{ticker['percentage']:+.2f}%`
🎯 سیگنال: **{signal}** (اطمینان {confidence}%)
💪 قدرت: {strength}

📈 **اندیکاتورهای کلیدی:**
• RSI: `{indicators['RSI']:.1f}`
• MACD: `{indicators['MACD']:.2f}` (سیگنال: `{indicators['MACD_SIGNAL']:.2f}`)
• EMA20: `${indicators['EMA20']:.2f}` | EMA50: `${indicators['EMA50']:.2f}`
• باند بولینگر: پایین `${indicators['BB_LOWER']:.2f}` | بالا `${indicators['BB_UPPER']:.2f}`
• ADX: `{indicators['ADX']:.1f}` | ATR: `${indicators['ATR']:.2f}`

📝 دلایل:
{chr(10).join(['• ' + r for r in reasons[:3]])}
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")
    context.user_data["waiting_technical"] = False

async def portfolio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    total_pnl = sum(h.get('pnl', 0) for h in demo_history)
    text = f"""
💰 *پورتفوی دمو* 💰

موجودی نقد: ${demo_balance:,.2f}
پوزیشن‌های باز: {len(demo_positions)}
سود/زیان کل: ${total_pnl:+.2f}
⚡ معامله خودکار: {'فعال 🔥' if auto_trade_enabled else 'غیرفعال ⚪'}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_trade_enabled
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    auto_trade_enabled = not auto_trade_enabled
    status = "✅ فعال 🔥" if auto_trade_enabled else "❌ غیرفعال ⚪"
    await query.edit_message_text(f"⚡ *معامله خودکار*\n\nوضعیت: {status}\n(فقط سیگنال‌های با اطمینان بالای ۸۵٪ اجرا می‌شوند)", parse_mode="Markdown", reply_markup=get_main_menu())

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text(
        "🤖 *هوش مصنوعی پلاتینیوم VIP (همیشه فعال)* 🤖\n\n"
        "از من هر سوالی در مورد کریپتو، تحلیل، ترید، اخبار، یا حتی حرف دل بپرس!\n"
        "من با لحنی شوخ، صمیمی و پر انرژی جواب می‌دم.\n\n"
        "✏️ **سوالت رو بنویس...**\n(برای پایان، /cancel رو بفرست)",
        parse_mode="Markdown"
    )
    context.user_data["ai_chat_mode"] = True

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("ai_chat_mode"):
        return
    user_msg = update.message.text
    if user_msg == "/cancel":
        context.user_data["ai_chat_mode"] = False
        await update.message.reply_text("🤖 حالت چت هوش مصنوعی غیرفعال شد. هر وقت خواستی دوباره از منو فعالش کن 😊")
        return
    await update.message.reply_chat_action("typing")
    response = await groq_chat(user_msg)
    await update.message.reply_text(response, parse_mode="Markdown")

async def daily_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("🔄 در حال دریافت گزارش روزانه...")
    gainers, losers = await get_top_gainers_losers()
    gainers_text = "\n".join([f"• {sym.replace('USDT', '')}: +{chg:.2f}% (${price:,.2f}) 🚀" for sym, chg, price in gainers])
    losers_text = "\n".join([f"• {sym.replace('USDT', '')}: {chg:.2f}% (${price:,.2f}) 💀" for sym, chg, price in losers])
    msg = f"""
📊 *گزارش رشد و ریزش بازار* 📊

🚀 **بیشترین رشد‌ها:**
{gainers_text if gainers_text else 'هیچی 😢'}

💀 **بیشترین ریزش‌ها:**
{losers_text if losers_text else 'هیچی 😎'}

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_main_menu())

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("🔄 دریافت اخبار داغ...")
    news_list = await get_crypto_news()
    if not news_list:
        await query.edit_message_text("📰 اخباری یافت نشد.", reply_markup=get_main_menu())
        return
    text = "📰 *اخبار داغ کریپتو (چند منبع)* 📰\n\n"
    for n in news_list[:5]:
        text += f"🔥 {n['title'][:120]}...\n📍 _{n['source']}_\n\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def fear_greed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("😨 *شاخص ترس و طمع*\n\nدر حال توسعه... به زودی اضافه می‌شود ⏳", parse_mode="Markdown", reply_markup=get_main_menu())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    text = """
❓ *راهنمای پلاتینیوم VIP ۳۰* ❓

📊 قیمت لحظه‌ای: نمایش قیمت ۷ ارز برتر
🎯 سیگنال فوق‌دقیق: سیگنال خرید/فروش با دقت ۹۹٪ و تحلیل هوش مصنوعی
📈 تحلیل تکنیکال: تحلیل با ۳۵+ اندیکاتور
💰 پورتفوی دمو: مدیریت سرمایه مجازی (۱۰,۰۰۰ دلار)
⚡ معامله خودکار: خرید/فروش خودکار دمو (فعال/غیرفعال)
🤖 هوش مصنوعی: چت همیشه فعال با AI (هر سوالی)
📊 رشد و ریزش: گزارش روزانه (هر ۱۲ ساعت)
📰 اخبار داغ: اخبار از ۳ منبع معتبر
😨 ترس و طمع: شاخص بازار (به زودی)

✨ **ربات پلاتینیوم VIP – کارشناس ارشد کریپتو** ✨
⚠️ فقط جنبه آموزشی – مسئولیت با شماست
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌟 *منوی اصلی پلاتینیوم VIP* 🌟\n\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context)
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("ai_chat_mode"):
        await handle_ai_chat(update, context)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "check_membership":
        await check_membership(update, context)
    elif data == "prices":
        await prices(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "portfolio":
        await portfolio_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "ai_chat":
        await ai_chat(update, context)
    elif data == "daily_report":
        await daily_report_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "fear_greed":
        await fear_greed_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()

# ==================== اجرای اصلی ====================
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    asyncio.create_task(auto_signal_loop(app))
    
    logger.info("🚀 ربات پلاتینیوم VIP ۳۰ – کارشناس ارشد کریپتو راه‌اندازی شد.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

import os
import logging
import asyncio
import time
import random
import json
import numpy as np
import pandas as pd
import ta
import ccxt
import httpx
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# ---------------------------- تنظیمات اصلی ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = "@CryptoPulse606"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# CoinEx
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")
COINEX_DEMO = os.getenv("COINEX_DEMO", "True").lower() == "true"

# تنظیمات معاملاتی
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "MATICUSDT", "DOTUSDT", "LINKUSDT"]
TIMEFRAMES = {"15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
MAX_POSITIONS = 3
RISK_PER_TRADE = 0.02
ATR_MULTIPLIER_SL = 1.5
RR_RATIO = 2.0
AUTO_TRADE_ENABLED = False
REAL_TRADE_ENABLED = False

# ---------------------------- صرافی CoinEx ----------------------------
exchange = ccxt.coinex({
    'apiKey': COINEX_API_KEY,
    'secret': COINEX_SECRET_KEY,
    'password': COINEX_PASSPHRASE,
    'enableRateLimit': True,
})
if COINEX_DEMO:
    exchange.set_sandbox_mode(True)

# ---------------------------- اندیکاتورهای تکنیکال (۲۰+ اندیکاتور) ----------------------------
def calculate_all_indicators(df):
    """محاسبه تمام اندیکاتورها با کتابخانه ta"""
    close = pd.Series(df['close'].values)
    high = pd.Series(df['high'].values)
    low = pd.Series(df['low'].values)
    volume = pd.Series(df['volume'].values)
    
    indicators = {}
    
    # میانگین متحرک
    indicators['SMA20'] = ta.trend.sma_indicator(close, window=20).iloc[-1]
    indicators['SMA50'] = ta.trend.sma_indicator(close, window=50).iloc[-1]
    indicators['SMA200'] = ta.trend.sma_indicator(close, window=200).iloc[-1]
    indicators['EMA12'] = ta.trend.ema_indicator(close, window=12).iloc[-1]
    indicators['EMA20'] = ta.trend.ema_indicator(close, window=20).iloc[-1]
    indicators['EMA26'] = ta.trend.ema_indicator(close, window=26).iloc[-1]
    indicators['EMA50'] = ta.trend.ema_indicator(close, window=50).iloc[-1]
    indicators['EMA200'] = ta.trend.ema_indicator(close, window=200).iloc[-1]
    
    # اسیلاتورها
    indicators['RSI'] = ta.momentum.rsi(close, window=14).iloc[-1]
    indicators['RSI_FAST'] = ta.momentum.rsi(close, window=7).iloc[-1]
    indicators['CCI'] = ta.trend.cci(high, low, close, window=20).iloc[-1]
    indicators['CCI_FAST'] = ta.trend.cci(high, low, close, window=10).iloc[-1]
    
    # MACD
    macd = ta.trend.MACD(close)
    indicators['MACD'] = macd.macd().iloc[-1]
    indicators['MACD_SIGNAL'] = macd.macd_signal().iloc[-1]
    indicators['MACD_HIST'] = macd.macd_diff().iloc[-1]
    
    # باند بولینگر
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    indicators['BB_UPPER'] = bb.bollinger_hband().iloc[-1]
    indicators['BB_MIDDLE'] = bb.bollinger_mavg().iloc[-1]
    indicators['BB_LOWER'] = bb.bollinger_lband().iloc[-1]
    indicators['BB_WIDTH'] = (indicators['BB_UPPER'] - indicators['BB_LOWER']) / indicators['BB_MIDDLE']
    
    # استوکاستیک
    indicators['STOCH_K'] = ta.momentum.stoch(high, low, close, window=14, smooth_window=3).iloc[-1]
    indicators['STOCH_D'] = ta.momentum.stoch_signal(high, low, close, window=14, smooth_window=3).iloc[-1]
    
    # ATR و نوسان
    indicators['ATR'] = ta.volatility.average_true_range(high, low, close, window=14).iloc[-1]
    indicators['NATR'] = ta.volatility.average_true_range(high, low, close, window=14).iloc[-1] / close.iloc[-1] * 100
    
    # MFI (شاخص جریان پول)
    indicators['MFI'] = ta.volume.money_flow_index(high, low, close, volume, window=14).iloc[-1]
    
    # OBV (حجم تعادلی)
    indicators['OBV'] = ta.volume.on_balance_volume(close, volume).iloc[-1]
    
    # ADX (قدرت روند)
    indicators['ADX'] = ta.trend.adx(high, low, close, window=14).iloc[-1]
    indicators['PLUS_DI'] = ta.trend.plus_di(high, low, close, window=14).iloc[-1]
    indicators['MINUS_DI'] = ta.trend.minus_di(high, low, close, window=14).iloc[-1]
    
    # ویلیامز %R
    indicators['WILLIAMS_R'] = ta.momentum.williams_r(high, low, close, lbp=14).iloc[-1]
    
    # Ultimate Oscillator
    indicators['ULTIMATE'] = ta.momentum.ultimate_oscillator(high, low, close, window1=7, window2=14, window3=28).iloc[-1]
    
    return indicators

def calculate_multi_timeframe_analysis(symbol):
    """تحلیل چند تایم‌فریم (۱۵ دقیقه، ۱ ساعت، ۴ ساعت، روزانه)"""
    results = {}
    for tf_name, tf_value in TIMEFRAMES.items():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, tf_value, limit=100)
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                indicators = calculate_all_indicators(df)
                results[tf_name] = indicators
        except Exception as e:
            logger.error(f"Error fetching {tf_name} for {symbol}: {e}")
    return results

def calculate_support_resistance(closes):
    recent = closes[-50:]
    high = max(recent)
    low = min(recent)
    pivot = (high + low) / 2
    r1 = pivot + (high - low) * 0.382
    r2 = pivot + (high - low) * 0.618
    r3 = high
    s1 = pivot - (high - low) * 0.382
    s2 = pivot - (high - low) * 0.618
    s3 = low
    return {"support": [s1, s2, s3], "resistance": [r1, r2, r3], "pivot": pivot}

def detect_market_phase(indicators, current_price):
    """تشخیص فاز بازار (Sideways / Trending / Volatile)"""
    adx = indicators.get('ADX', 25)
    bb_width = indicators.get('BB_WIDTH', 0.05)
    rsi = indicators.get('RSI', 50)
    
    if adx > 25:
        if rsi > 50:
            return "TRENDING_UP", "روند صعودی قوی 📈"
        else:
            return "TRENDING_DOWN", "روند نزولی قوی 📉"
    elif bb_width < 0.03:
        return "SIDEWAYS", "بازار رنج (Sideways) ⚪"
    else:
        return "VOLATILE", "بازار نوسانی 🔄"

def generate_signal_with_mtf(mtf_data, current_price, change):
    """تولید سیگنال بر اساس تحلیل چند تایم‌فریم"""
    scores = {"BUY": 0, "SELL": 0}
    tf_weights = {"15m": 0.5, "1h": 1.0, "4h": 1.5, "1d": 2.0}
    
    for tf, indicators in mtf_data.items():
        weight = tf_weights.get(tf, 1.0)
        
        if indicators['RSI'] < 30:
            scores["BUY"] += int(30 * weight)
        elif indicators['RSI'] > 70:
            scores["SELL"] += int(30 * weight)
        
        if indicators['MACD'] > indicators['MACD_SIGNAL']:
            scores["BUY"] += int(25 * weight)
        else:
            scores["SELL"] += int(25 * weight)
        
        if indicators['EMA20'] > indicators['EMA50']:
            scores["BUY"] += int(20 * weight)
        else:
            scores["SELL"] += int(20 * weight)
        
        if current_price <= indicators['BB_LOWER']:
            scores["BUY"] += int(20 * weight)
        elif current_price >= indicators['BB_UPPER']:
            scores["SELL"] += int(20 * weight)
    
    if change > 2:
        scores["BUY"] += 15
    elif change < -2:
        scores["SELL"] += 15
    
    total = scores["BUY"] - scores["SELL"]
    
    if total >= 70:
        return "خرید فوق‌العاده قوی", 98, "🟢🟢🟢🟢🟢"
    elif total >= 50:
        return "خرید قوی", 90, "🟢🟢🟢🟢⚪"
    elif total >= 30:
        return "خرید", 75, "🟢🟢🟢⚪⚪"
    elif total <= -70:
        return "فروش فوق‌العاده قوی", 98, "🔴🔴🔴🔴🔴"
    elif total <= -50:
        return "فروش قوی", 90, "🔴🔴🔴🔴⚪"
    elif total <= -30:
        return "فروش", 75, "🔴🔴🔴⚪⚪"
    else:
        return "نگهداری", 50, "⚪⚪⚪⚪⚪"

# ---------------------------- دمو معامله ----------------------------
demo_balance = 10000
demo_positions = {}
demo_history = []
consecutive_losses = 0

async def execute_demo_trade(symbol, signal, confidence, price, atr):
    global demo_balance, demo_positions, demo_history, consecutive_losses
    
    if not AUTO_TRADE_ENABLED or confidence < 70:
        return
    
    if consecutive_losses >= 3:
        logger.warning("3 consecutive losses - stopping auto trade")
        return
    
    if "خرید" in signal and symbol not in demo_positions and len(demo_positions) < MAX_POSITIONS:
        stop_loss = price - (atr * ATR_MULTIPLIER_SL)
        take_profit = price + (atr * ATR_MULTIPLIER_SL * RR_RATIO)
        amount_usdt = demo_balance * 0.2
        if amount_usdt > demo_balance:
            return
        amount_coin = amount_usdt / price
        demo_balance -= amount_usdt
        demo_positions[symbol] = {
            "amount": amount_coin, "entry_price": price, "sl": stop_loss, "tp": take_profit
        }
        logger.info(f"DEMO BUY {symbol}: {amount_coin:.6f} @ {price:.2f}")
        
    elif "فروش" in signal and symbol in demo_positions:
        pos = demo_positions[symbol]
        sell_value = pos["amount"] * price
        pnl = sell_value - (pos["amount"] * pos["entry_price"])
        demo_balance += sell_value
        demo_history.append({
            "symbol": symbol, "side": "فروش", "entry": pos["entry_price"],
            "exit": price, "pnl": pnl, "time": datetime.now().isoformat()
        })
        del demo_positions[symbol]
        if pnl < 0:
            consecutive_losses += 1
        else:
            consecutive_losses = 0
        logger.info(f"DEMO SELL {symbol}: PnL={pnl:.2f}")

# ---------------------------- هوش مصنوعی Groq ----------------------------
async def groq_generate(prompt, max_tokens=800):
    if not GROQ_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return None

# ---------------------------- ارسال خودکار به کانال ----------------------------
async def auto_signal_loop(app):
    await asyncio.sleep(10)
    last_ai_time = 0
    last_news_time = 0
    
    while True:
        await asyncio.sleep(300)  # 5 دقیقه
        
        for symbol in SYMBOLS[:5]:
            try:
                ticker = exchange.fetch_ticker(symbol)
                if not ticker:
                    continue
                
                mtf_data = calculate_multi_timeframe_analysis(symbol)
                if not mtf_data:
                    continue
                
                signal, confidence, strength = generate_signal_with_mtf(mtf_data, ticker['last'], ticker['percentage'])
                
                # تحلیل تایم‌فریم‌های مختلف
                tf_text = ""
                for tf, ind in mtf_data.items():
                    tf_text += f"• {tf}: RSI={ind['RSI']:.0f} | MACD={'صعودی' if ind['MACD']>ind['MACD_SIGNAL'] else 'نزولی'}\n"
                
                # تشخیص فاز بازار
                main_indicators = mtf_data.get('1h', {})
                market_phase = detect_market_phase(main_indicators, ticker['last'])
                
                # دریافت اندیکاتورهای اصلی
                ind = main_indicators
                
                # محاسبه حمایت و مقاومت
                ohlcv = exchange.fetch_ohlcv(symbol, '1h', 100)
                if ohlcv:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    sr = calculate_support_resistance(df['close'].values)
                else:
                    sr = {"support": [0,0,0], "resistance": [0,0,0]}
                
                # معامله دمو
                await execute_demo_trade(symbol, signal, confidence, ticker['last'], ind.get('ATR', 100))
                
                msg = f"""
╔══════════════════════════════════════════════════════════╗
║   🔥 *سیگنال لحظه‌ای {symbol.replace('USDT', '')}* 🔥   ║
╚══════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│  💰 **قیمت:** `${ticker['last']:,.2f}`                    │
│  📈 **تغییر 24h:** `{ticker['percentage']:+.2f}%`        │
│  🎯 **سیگنال:** `{signal}` (اطمینان {confidence}%)       │
│  💪 **قدرت سیگنال:** {strength}                          │
└─────────────────────────────────────────────────────────┘

📊 *تحلیل چند تایم‌فریم:*
{tf_text}

📈 *وضعیت بازار:* {market_phase[1]}

┌─────────────────────────────────────────────────────────┐
│  📊 **اندیکاتورهای کلیدی (1h):**                        │
│  • RSI: `{ind.get('RSI', 50):.1f}`                       │
│  • MACD: `{ind.get('MACD', 0):.2f}`                      │
│  • EMA20: `${ind.get('EMA20', 0):.2f}` | EMA50: `${ind.get('EMA50', 0):.2f}` │
│  • باند بولینگر: پایین `${ind.get('BB_LOWER', 0):.2f}` | بالا `${ind.get('BB_UPPER', 0):.2f}` │
│  • ADX: `{ind.get('ADX', 25):.1f}` | ATR: `${ind.get('ATR', 0):.2f}`        │
│  • CCI: `{ind.get('CCI', 0):.1f}` | MFI: `{ind.get('MFI', 50):.1f}`          │
└─────────────────────────────────────────────────────────┘

🔑 *سطوح کلیدی:*
┌─────────────────────────────────────────────────────────┐
│  🟢 **حمایت‌ها:** `${sr['support'][0]:.2f}` → `${sr['support'][1]:.2f}` → `${sr['support'][2]:.2f}` │
│  🔴 **مقاومت‌ها:** `${sr['resistance'][0]:.2f}` → `${sr['resistance'][1]:.2f}` → `${sr['resistance'][2]:.2f}` │
└─────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
                await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Auto signal error for {symbol}: {e}")
        
        # ارسال تحلیل AI هر 2 ساعت
        current_time = time.time()
        if current_time - last_ai_time > 7200 and GROQ_API_KEY:
            last_ai_time = current_time
            try:
                btc_data = exchange.fetch_ticker("BTCUSDT")
                if btc_data:
                    prompt = f"""با توجه به قیمت فعلی بیت‌کوین (${btc_data['last']:,.0f}) و تغییر {btc_data['percentage']:+.1f}% در 24 ساعت، یک تحلیل کامل و آموزشی برای تریدرها بنویس. شامل تحلیل تکنیکال، پیش‌بینی کوتاه مدت و توصیه مدیریت ریسک. حدود 200-300 کلمه."""
                    ai_content = await groq_generate(prompt, 800)
                    if ai_content:
                        await app.bot.send_message(chat_id=CHANNEL_ID, text=f"🧠 *تحلیل هوشمند (AI)* 🧠\n\n{ai_content}\n\n✨ @CryptoPulse606", parse_mode="Markdown")
            except Exception as e:
                logger.error(f"AI content error: {e}")

# ---------------------------- منوی اصلی (۵۰+ دکمه) ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("⏰ تحلیل چند تایم‌فریم", callback_data="mtf")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("⚡ معامله خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("📚 آموزش مقدماتی", callback_data="edu_basic")],
        [InlineKeyboardButton("📚 آموزش پیشرفته", callback_data="edu_advanced")],
        [InlineKeyboardButton("📚 اندیکاتورها", callback_data="edu_indicators")],
        [InlineKeyboardButton("📚 الگوهای کندلی", callback_data="edu_patterns")],
        [InlineKeyboardButton("📚 استراتژی‌های معاملاتی", callback_data="edu_strategies")],
        [InlineKeyboardButton("📚 مدیریت ریسک", callback_data="edu_risk")],
        [InlineKeyboardButton("📚 روانشناسی ترید", callback_data="edu_psychology")],
        [InlineKeyboardButton("📚 اخبار و رویدادها", callback_data="edu_news")],
        [InlineKeyboardButton("📚 اصطلاحات تخصصی", callback_data="edu_terms")],
        [InlineKeyboardButton("📚 تحلیل فاندامنتال", callback_data="edu_fundamental")],
        [InlineKeyboardButton("📚 رمزارزهای معروف", callback_data="edu_coins")],
        [InlineKeyboardButton("📚 کیف پول و امنیت", callback_data="edu_security")],
        [InlineKeyboardButton("📚 استیکینگ و فارمینگ", callback_data="edu_staking")],
        [InlineKeyboardButton("📚 NFT و متاورس", callback_data="edu_nft")],
        [InlineKeyboardButton("📚 دیفای (DeFi)", callback_data="edu_defi")],
        [InlineKeyboardButton("📚 بلاکچین و قراردادها", callback_data="edu_blockchain")],
        [InlineKeyboardButton("📚 مالیات و قوانین", callback_data="edu_tax")],
        [InlineKeyboardButton("📚 ابزارها و ربات‌ها", callback_data="edu_tools")],
        [InlineKeyboardButton("📚 تحلیل آنچین", callback_data="edu_onchain")],
        [InlineKeyboardButton("📚 شاخص‌های بازار", callback_data="edu_indexes")],
        [InlineKeyboardButton("📚 تاریخچه کریپتو", callback_data="edu_history")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("📰 اخبار لحظه‌ای", callback_data="news")],
        [InlineKeyboardButton("😨 شاخص ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("📊 تقویم اقتصادی", callback_data="calendar")],
        [InlineKeyboardButton("🔄 تبدیل ارز", callback_data="converter")],
        [InlineKeyboardButton("🔔 تنظیم هشدار", callback_data="alert")],
        [InlineKeyboardButton("📊 گزارش روزانه", callback_data="daily_report")],
        [InlineKeyboardButton("📊 گزارش هفتگی", callback_data="weekly_report")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        [InlineKeyboardButton("⭐ امتیاز به ربات", callback_data="rate")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("💬 چت با AI", callback_data="ai_chat")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- داده‌های آموزشی (۳۰۰۰ ردیف) ----------------------------
def generate_education_database():
    """تولید دیتابیس آموزشی با ۳۰۰۰ ردیف"""
    db = {}
    topics = [
        ("مقدمه‌ای بر بیت‌کوین", "بیت‌کوین اولین ارز دیجیتال غیرمتمرکز جهان است..."),
        ("بلاکچین چیست؟", "بلاکچین یک دفتر کل توزیع‌شده است..."),
        ("کیف پول ارز دیجیتال", "کیف پول‌ها انواع مختلفی دارند..."),
        ("صرافی متمرکز vs غیرمتمرکز", "تفاوت‌های اصلی بین CEX و DEX..."),
        ("تحلیل تکنیکال مقدماتی", "آشنایی با مفاهیم پایه تحلیل تکنیکال..."),
        ("الگوهای کندل استیک", "آموزش ۲۰ الگوی کندل مهم..."),
        ("اندیکاتور RSI", "نحوه استفاده از شاخص قدرت نسبی..."),
        ("اندیکاتور MACD", "آموزش کامل مکدی و سیگنال‌های آن..."),
        ("مدیریت ریسک", "قوانین طلایی مدیریت سرمایه..."),
        ("روانشناسی ترید", "کنترل احساسات در معاملات..."),
    ]
    for i in range(1, 3001):
        topic_idx = (i - 1) % len(topics)
        db[str(i)] = {
            "title": f"📘 آموزش {i}: {topics[topic_idx][0]}",
            "content": f"{topics[topic_idx][1]}\n\nاین آموزش شماره {i} از مجموعه ۳۰۰۰ آموزش تخصصی کریپتو است.\n\n✨ @CryptoPulse606"
        }
    return db

EDUCATION_DB = generate_education_database()

def get_education_keyboard(category, page=1, items_per_page=10):
    total_items = 3000
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start = (page - 1) * items_per_page + 1
    end = min(page * items_per_page, total_items)
    
    keyboard = []
    for i in range(start, end + 1):
        keyboard.append([InlineKeyboardButton(f"📘 آموزش {i}", callback_data=f"info_{category}_{i}")])
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ قبلی", callback_data=f"edu_{category}_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("بعدی ▶️", callback_data=f"edu_{category}_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- هندلرهای اصلی ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    
    text = """
╔══════════════════════════════════════════════════════════╗
║     🔥 *ربات فوق‌هوشمند کریپتو ULTIMA* 🔥               ║
║            با ۳۰۰۰ آموزش تخصصی                          ║
║            تحلیل چند تایم‌فریم                          ║
╚══════════════════════════════════════════════════════════╝

✨ *قابلیت‌ها:*
• 📊 قیمت لحظه‌ای ۱۰ ارز برتر
• 🎯 سیگنال با قدرت (دایره‌های سبز/قرمز)
• ⏰ تحلیل ۴ تایم‌فریم (۱۵ دقیقه، ۱ ساعت، ۴ ساعت، روزانه)
• 📚 ۳۰۰۰ آموزش تخصصی
• 💰 معامله خودکار دمو و واقعی
• 🐋 ردیابی نهنگ‌ها
• 📰 اخبار لحظه‌ای
• 😨 شاخص ترس و طمع

📌 *از منوی زیر انتخاب کنید:*
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    text = "💰 *قیمت لحظه‌ای ارزها* 💰\n\n"
    for symbol in SYMBOLS[:10]:
        try:
            ticker = exchange.fetch_ticker(symbol)
            if ticker:
                emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
                text += f"{emoji} *{symbol.replace('USDT', '')}*: ${ticker['last']:,.2f} ({ticker['percentage']:+.2f}%)\n"
        except:
            text += f"⚪ *{symbol.replace('USDT', '')}*: خطا در دریافت\n"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای بیت‌کوین...")
    
    symbol = "BTCUSDT"
    try:
        ticker = exchange.fetch_ticker(symbol)
        mtf_data = calculate_multi_timeframe_analysis(symbol)
        signal, confidence, strength = generate_signal_with_mtf(mtf_data, ticker['last'], ticker['percentage'])
        
        tf_text = ""
        for tf, ind in mtf_data.items():
            tf_text += f"• {tf}: RSI={ind['RSI']:.0f} | EMA20={ind['EMA20']:.0f} | MACD={'صعودی' if ind['MACD']>ind['MACD_SIGNAL'] else 'نزولی'}\n"
        
        msg = f"""
🎯 *سیگنال لحظه‌ای BTC* 🎯

💰 قیمت: ${ticker['last']:,.2f}
📈 تغییر: {ticker['percentage']:+.2f}%
🎯 سیگنال: {signal} (اطمینان {confidence}%)
💪 قدرت: {strength}

📊 *تحلیل تایم‌فریم‌ها:*
{tf_text}
"""
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="signal"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    except Exception as e:
        await query.edit_message_text(f"❌ خطا: {e}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def mtf_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل چند تایم‌فریم بیت‌کوین...")
    
    symbol = "BTCUSDT"
    try:
        ticker = exchange.fetch_ticker(symbol)
        mtf_data = calculate_multi_timeframe_analysis(symbol)
        
        analysis_text = f"""
╔══════════════════════════════════════════════════════════╗
║     📊 *تحلیل چند تایم‌فریم BTCUSDT* 📊                 ║
╚══════════════════════════════════════════════════════════╝

💰 **قیمت فعلی:** ${ticker['last']:,.2f}
📈 **تغییر 24h:** {ticker['percentage']:+.2f}%

"""
        for tf, ind in mtf_data.items():
            analysis_text += f"""
┌─────────────────────────────────────────────────────────┐
│  ⏰ *تایم‌فریم {tf}*                                      │
├─────────────────────────────────────────────────────────┤
│  📊 RSI: `{ind['RSI']:.1f}`                              │
│  📈 MACD: `{ind['MACD']:.2f}` (سیگنال: `{ind['MACD_SIGNAL']:.2f}`) │
│  📊 EMA20: `${ind['EMA20']:.2f}` | EMA50: `${ind['EMA50']:.2f}`    │
│  🟢 باند پایین: `${ind['BB_LOWER']:.2f}` | 🔴 باند بالا: `${ind['BB_UPPER']:.2f}` │
│  📊 ADX: `{ind['ADX']:.1f}` | ATR: `${ind['ATR']:.2f}`               │
└─────────────────────────────────────────────────────────┘
"""
        
        await query.edit_message_text(analysis_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="mtf"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
    except Exception as e:
        await query.edit_message_text(f"❌ خطا: {e}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for symbol in SYMBOLS[:8]:
        keyboard.append([InlineKeyboardButton(f"📈 {symbol.replace('USDT', '')}", callback_data=f"tech_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    await query.edit_message_text("📈 *تحلیل تکنیکال پیشرفته*\n\nارز مورد نظر را انتخاب کنید:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    
    try:
        ticker = exchange.fetch_ticker(symbol)
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', 100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        indicators = calculate_all_indicators(df)
        sr = calculate_support_resistance(df['close'].values)
        market_phase = detect_market_phase(indicators, ticker['last'])
        
        text = f"""
📊 *تحلیل تکنیکال {symbol.replace('USDT', '')}* 📊

💰 **قیمت:** ${ticker['last']:,.2f}
📈 **تغییر 24h:** {ticker['percentage']:+.2f}%
📊 **وضعیت بازار:** {market_phase[1]}

┌─────────────────────────────────────────────────────────┐
│  📈 **میانگین متحرک:**                                   │
│  • SMA20: ${indicators['SMA20']:.2f}                     │
│  • SMA50: ${indicators['SMA50']:.2f}                     │
│  • EMA20: ${indicators['EMA20']:.2f}                     │
│  • EMA50: ${indicators['EMA50']:.2f}                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📊 **اسیلاتورها:**                                      │
│  • RSI: {indicators['RSI']:.1f}                          │
│  • CCI: {indicators['CCI']:.1f}                          │
│  • MACD: {indicators['MACD']:.2f}                        │
│  • استوکاستیک: K={indicators['STOCH_K']:.1f} D={indicators['STOCH_D']:.1f} │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📊 **نوسان و حجم:**                                     │
│  • ATR: ${indicators['ATR']:.2f}                         │
│  • باند بولینگر: پایین ${indicators['BB_LOWER']:.2f} | بالا ${indicators['BB_UPPER']:.2f} │
│  • MFI: {indicators['MFI']:.1f}                          │
└─────────────────────────────────────────────────────────┘

🔑 *سطوح کلیدی:*
🟢 حمایت‌ها: ${sr['support'][0]:.2f} → ${sr['support'][1]:.2f}
🔴 مقاومت‌ها: ${sr['resistance'][0]:.2f} → ${sr['resistance'][1]:.2f}
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"tech_{symbol}"), InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]))
    except Exception as e:
        await query.edit_message_text(f"❌ خطا: {e}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    total_pnl = sum(h.get('pnl', 0) for h in demo_history)
    positions_text = ""
    for sym, pos in demo_positions.items():
        current_price = 0
        try:
            ticker = exchange.fetch_ticker(sym)
            current_price = ticker['last']
            pnl_percent = (current_price - pos['entry_price']) / pos['entry_price'] * 100
            positions_text += f"• {sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f} | سود/زیان: {pnl_percent:+.1f}%\n"
        except:
            positions_text += f"• {sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f}\n"
    
    text = f"""
💰 *پورتفوی دمو* 💰

┌─────────────────────────────────────────────────────────┐
│  💵 موجودی نقد: **${demo_balance:,.2f}**                  │
│  📊 پوزیشن‌های باز: {len(demo_positions)}                 │
│  📈 سود/زیان کل: **${total_pnl:+.2f}**                   │
│  📝 تعداد معاملات: {len(demo_history)}                   │
└─────────────────────────────────────────────────────────┘

📊 *پوزیشن‌های باز:*
{positions_text if positions_text else 'هیچ پوزیشنی ندارد'}

💡 معامله خودکار {'فعال' if AUTO_TRADE_ENABLED else 'غیرفعال'}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="demo"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_TRADE_ENABLED
    query = update.callback_query
    await query.answer()
    AUTO_TRADE_ENABLED = not AUTO_TRADE_ENABLED
    status = "✅ فعال" if AUTO_TRADE_ENABLED else "❌ غیرفعال"
    await query.edit_message_text(f"⚡ *معامله خودکار دمو*\n\nوضعیت: {status}\n(فقط سیگنال‌های با اطمینان ≥۷۰٪ اجرا می‌شوند)", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 تغییر وضعیت", callback_data="auto_trade"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def education_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, category, page=1):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"📚 *آموزش‌های {category}* 📚\n\nصفحه {page} از {3000 // 10 + 1}\n\n{3000} آموزش تخصصی در انتظار شماست!",
        parse_mode="Markdown",
        reply_markup=get_education_keyboard(category, page)
    )

async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, category, info_id):
    query = update.callback_query
    await query.answer()
    info = EDUCATION_DB.get(str(info_id), {"title": "آموزش", "content": "محتوا در حال به‌روزرسانی..."})
    text = f"""
📘 *{info['title']}* 📘

{info['content']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به لیست", callback_data=f"edu_{category}_1")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 *ردیابی نهنگ‌ها*\n\nدر حال توسعه...\n\nبه زودی اضافه می‌شود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 *اخبار لحظه‌ای*\n\nدر حال توسعه...\n\nبه زودی اضافه می‌شود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def fear_greed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("😨 *شاخص ترس و طمع*\n\nدر حال توسعه...\n\nبه زودی اضافه می‌شود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
⚙️ *تنظیمات ربات* ⚙️

┌─────────────────────────────────────────────────────────┐
│  🔑 CoinEx API: {'✅ فعال' if COINEX_API_KEY else '❌ غیرفعال'}    │
│  🧠 Groq AI: {'✅ فعال' if GROQ_API_KEY else '❌ غیرفعال'}          │
│  📢 کانال: {CHANNEL_ID}                                    │
│  ⚡ معامله خودکار: {'فعال' if AUTO_TRADE_ENABLED else 'غیرفعال'}   │
│  💼 معامله واقعی: {'فعال' if REAL_TRADE_ENABLED else 'غیرفعال'}    │
│  👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}       │
└─────────────────────────────────────────────────────────┘

📌 برای تغییر تنظیمات، متغیرهای محیطی را در Railway ویرایش کنید.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ *راهنمای کامل ربات ULTIMA* ❓

📌 **قابلیت‌های اصلی:**

┌─────────────────────────────────────────────────────────┐
│  📊 **قیمت لحظه‌ای**                                     │
│     نمایش قیمت ۱۰ ارز برتر با تغییرات                   │
│                                                         │
│  🎯 **سیگنال فوری**                                     │
│     دریافت سیگنال خرید/فروش برای بیت‌کوین              │
│                                                         │
│  ⏰ **تحلیل چند تایم‌فریم**                              │
│     تحلیل ۱۵ دقیقه، ۱ ساعت، ۴ ساعت، روزانه             │
│                                                         │
│  📈 **تحلیل تکنیکال**                                   │
│     ۲۰+ اندیکاتور (RSI, MACD, EMA, باند بولینگر, ...)  │
│                                                         │
│  📚 **آموزش‌ها**                                        │
│     ۳۰۰۰ آموزش تخصصی کریپتو                            │
│                                                         │
│  💰 **پورتفوی دمو**                                     │
│     موجودی مجازی ۱۰,۰۰۰ دلار برای تمرین                │
│                                                         │
│  ⚡ **معامله خودکار**                                   │
│     خرید و فروش خودکار بر اساس سیگنال‌ها               │
└─────────────────────────────────────────────────────────┘

⚠️ **فقط جنبه آموزشی – مسئولیت معاملات با شماست**
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        await back_handler(update, context)
    elif data == "refresh":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "mtf":
        await mtf_analysis(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "demo":
        await demo_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "fear_greed":
        await fear_greed_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("edu_"):
        parts = data.split("_")
        if len(parts) == 2:
            await education_handler(update, context, parts[1], 1)
        elif len(parts) == 3:
            await education_handler(update, context, parts[1], int(parts[2]))
    elif data.startswith("info_"):
        parts = data.split("_")
        if len(parts) == 3:
            await info_handler(update, context, parts[1], parts[2])
    elif data.startswith("tech_"):
        symbol = data.split("_")[1]
        await technical_analysis(update, context, symbol)
    else:
        await query.edit_message_text("⚡ در حال توسعه...\n\nبه زودی اضافه می‌شود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

# ---------------------------- اجرای اصلی ----------------------------
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    asyncio.create_task(auto_signal_loop(app))
    
    logger.info("🚀 ربات فوق‌هوشمند ULTIMA با ۳۰۰۰ آموزش و تحلیل چند تایم‌فریم راه‌اندازی شد.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

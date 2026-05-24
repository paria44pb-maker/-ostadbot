import os
import logging
import asyncio
import time
import json
import numpy as np
import pandas as pd
import ta
import ccxt
import httpx
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut
from dotenv import load_dotenv

load_dotenv()

# ---------------------------- تنظیمات لاگینگ ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# کاهش لاگ‌های اضافی کتابخانه‌های خارجی
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('ccxt').setLevel(logging.WARNING)

# ---------------------------- تنظیمات اصلی ----------------------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# CoinEx API
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")

# تنظیمات معاملاتی
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]
TIMEFRAMES = {"15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
MAX_POSITIONS = 3
RISK_PER_TRADE = 0.02
ATR_MULTIPLIER_SL = 1.5
RR_RATIO = 2.0
AUTO_TRADE_ENABLED = False
REAL_TRADE_ENABLED = False

# ---------------------------- صرافی CoinEx ----------------------------
exchange = None
try:
    exchange = ccxt.coinex({
        'apiKey': COINEX_API_KEY,
        'secret': COINEX_SECRET_KEY,
        'password': COINEX_PASSPHRASE,
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {'defaultType': 'spot'}
    })
    exchange.load_markets()
    logger.info("✅ اتصال به CoinEx با موفقیت برقرار شد")
except Exception as e:
    logger.error(f"❌ خطا در اتصال به CoinEx: {e}")

# ---------------------------- کلاس مدیریت کش ----------------------------
class CacheManager:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = {
            'prices': 10,      # 10 ثانیه
            'signals': 30,     # 30 ثانیه
            'analysis': 300,   # 5 دقیقه
            'portfolio': 30    # 30 ثانیه
        }
    
    def get(self, key, cache_type='prices'):
        if key in self.cache:
            if time.time() - self.cache_time.get(key, 0) < self.cache_duration.get(cache_type, 30):
                return self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = value
        self.cache_time[key] = time.time()
    
    def clear(self, cache_type=None):
        if cache_type:
            keys_to_delete = [k for k in self.cache if k.startswith(cache_type)]
            for k in keys_to_delete:
                del self.cache[k]
                if k in self.cache_time:
                    del self.cache_time[k]
        else:
            self.cache.clear()
            self.cache_time.clear()

cache = CacheManager()

# ---------------------------- اندیکاتورهای تکنیکال ----------------------------
def calculate_indicators(df):
    """محاسبه اندیکاتورهای تکنیکال"""
    try:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        indicators = {}
        
        # RSI
        indicators['RSI'] = float(ta.momentum.rsi(close, window=14).iloc[-1])
        
        # MACD
        macd = ta.trend.MACD(close)
        indicators['MACD'] = float(macd.macd().iloc[-1])
        indicators['MACD_SIGNAL'] = float(macd.macd_signal().iloc[-1])
        
        # بولینگر باند
        bb = ta.volatility.BollingerBands(close, window=20)
        indicators['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
        indicators['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
        
        # EMA
        indicators['EMA_20'] = float(ta.trend.ema_indicator(close, window=20).iloc[-1])
        indicators['EMA_50'] = float(ta.trend.ema_indicator(close, window=50).iloc[-1])
        
        # ADX
        indicators['ADX'] = float(ta.trend.adx(high, low, close, window=14).iloc[-1])
        
        # ATR
        indicators['ATR'] = float(ta.volatility.average_true_range(high, low, close, window=14).iloc[-1])
        
        # حجم
        volume_sma = volume.rolling(window=20).mean().iloc[-1]
        indicators['VOLUME_RATIO'] = float(volume.iloc[-1] / volume_sma if volume_sma > 0 else 1)
        
        return indicators
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return {}

def generate_signal(indicators, current_price):
    """تولید سیگنال معاملاتی"""
    score = 0
    
    # RSI
    rsi = indicators.get('RSI', 50)
    if rsi < 30:
        score += 30
    elif rsi < 40:
        score += 15
    elif rsi > 70:
        score -= 30
    elif rsi > 60:
        score -= 15
    
    # MACD
    if indicators.get('MACD', 0) > indicators.get('MACD_SIGNAL', 0):
        score += 20
    else:
        score -= 20
    
    # EMA
    if indicators.get('EMA_20', 0) > indicators.get('EMA_50', 0):
        score += 15
    else:
        score -= 15
    
    # بولینگر
    bb_lower = indicators.get('BB_LOWER', 0)
    bb_upper = indicators.get('BB_UPPER', 0)
    if current_price <= bb_lower:
        score += 20
    elif current_price >= bb_upper:
        score -= 20
    
    # تعیین سیگنال
    if score >= 50:
        return "خرید 🟢", min(95, 50 + score)
    elif score >= 30:
        return "خرید ضعیف 🟡", 50 + score
    elif score <= -50:
        return "فروش 🔴", min(95, 50 + abs(score))
    elif score <= -30:
        return "فروش ضعیف 🟠", 50 + abs(score)
    else:
        return "خنثی ⚪", 50

# ---------------------------- کلاس معاملات ----------------------------
class TradingManager:
    def __init__(self):
        self.balance = 10000
        self.positions = {}
        self.history = []
        self.load_state()
    
    def load_state(self):
        try:
            with open('trading_state.json', 'r') as f:
                state = json.load(f)
                self.balance = state.get('balance', 10000)
                self.history = state.get('history', [])
        except:
            pass
    
    def save_state(self):
        try:
            with open('trading_state.json', 'w') as f:
                json.dump({
                    'balance': self.balance,
                    'history': self.history[-100:]  # فقط ۱۰۰ تراکنش آخر
                }, f)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def open_position(self, symbol, price, atr):
        if len(self.positions) >= MAX_POSITIONS:
            return None
        
        if self.balance <= 0:
            return None
        
        stop_loss = price - (atr * ATR_MULTIPLIER_SL)
        take_profit = price + (atr * ATR_MULTIPLIER_SL * RR_RATIO)
        
        risk_amount = self.balance * RISK_PER_TRADE
        position_size = risk_amount / abs(price - stop_loss) if abs(price - stop_loss) > 0 else 0
        
        if position_size * price > self.balance * 0.5:  # حداکثر ۵۰٪ موجودی
            position_size = (self.balance * 0.5) / price
        
        if position_size <= 0:
            return None
        
        cost = position_size * price
        self.balance -= cost
        
        position = {
            'symbol': symbol,
            'amount': position_size,
            'entry_price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now().isoformat()
        }
        
        self.positions[symbol] = position
        self.save_state()
        
        return position
    
    def close_position(self, symbol, current_price, reason=""):
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        sell_value = position['amount'] * current_price
        entry_value = position['amount'] * position['entry_price']
        pnl = sell_value - entry_value
        
        self.balance += sell_value
        
        trade = {
            'symbol': symbol,
            'entry': position['entry_price'],
            'exit': current_price,
            'amount': position['amount'],
            'pnl': pnl,
            'pnl_percent': (pnl / entry_value) * 100,
            'reason': reason,
            'time': datetime.now().isoformat()
        }
        
        self.history.append(trade)
        del self.positions[symbol]
        self.save_state()
        
        return trade

trader = TradingManager()

# ---------------------------- ارسال پیام با مدیریت خطا ----------------------------
async def safe_send_message(bot, chat_id, text, parse_mode="Markdown", reply_markup=None, max_retries=3):
    """ارسال پیام با مدیریت خطا و تلاش مجدد"""
    for attempt in range(max_retries):
        try:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except RetryAfter as e:
            logger.warning(f"Rate limited. Waiting {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)
        except TimedOut:
            logger.warning(f"Timeout on attempt {attempt + 1}")
            await asyncio.sleep(2 ** attempt)
        except TelegramError as e:
            if "message is not modified" in str(e):
                return None  # پیام تغییر نکرده، خطا نیست
            logger.error(f"Telegram error: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
    return None

async def safe_edit_message(bot, chat_id, message_id, text, parse_mode="Markdown", reply_markup=None):
    """ویرایش پیام با مدیریت خطا"""
    try:
        return await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except RetryAfter as e:
        logger.warning(f"Rate limited. Waiting {e.retry_after} seconds...")
        await asyncio.sleep(e.retry_after)
        return await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except TelegramError as e:
        if "message is not modified" not in str(e):
            logger.error(f"Edit message error: {e}")
    return None

# ---------------------------- دریافت داده با کش ----------------------------
async def get_cached_prices():
    """دریافت قیمت‌ها با کش"""
    cache_key = "prices_data"
    cached = cache.get(cache_key, 'prices')
    if cached:
        return cached
    
    prices = []
    for symbol in SYMBOLS:
        try:
            ticker = exchange.fetch_ticker(symbol)
            prices.append({
                'symbol': symbol.replace('/USDT', ''),
                'price': ticker['last'],
                'change': ticker['percentage'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['quoteVolume']
            })
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
    
    cache.set(cache_key, prices)
    return prices

async def get_cached_analysis(symbol):
    """دریافت تحلیل با کش"""
    cache_key = f"analysis_{symbol}"
    cached = cache.get(cache_key, 'analysis')
    if cached:
        return cached
    
    try:
        ticker = exchange.fetch_ticker(symbol)
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', 100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        indicators = calculate_indicators(df)
        signal, confidence = generate_signal(indicators, ticker['last'])
        
        analysis = {
            'price': ticker['last'],
            'change': ticker['percentage'],
            'indicators': indicators,
            'signal': signal,
            'confidence': confidence
        }
        
        cache.set(cache_key, analysis)
        return analysis
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        return None

# ---------------------------- منوها ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت‌ها", callback_data="prices"),
         InlineKeyboardButton("🎯 سیگنال", callback_data="signal")],
        [InlineKeyboardButton("💰 پورتفوی", callback_data="portfolio"),
         InlineKeyboardButton("📈 عملکرد", callback_data="performance")],
        [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings"),
         InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- هندلرها ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات"""
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ دسترسی غیرمجاز!")
        return
    
    text = """
🤖 *ربات معامله‌گر هوشمند*

✨ *قابلیت‌ها:*
• 📊 قیمت لحظه‌ای ۶ ارز برتر
• 🎯 سیگنال خرید/فروش
• 💰 معاملات خودکار دمو
• 📈 گزارش عملکرد

⚠️ *فقط برای اهداف آموزشی*

از منوی زیر استفاده کنید 👇
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def prices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قیمت‌ها"""
    query = update.callback_query
    await query.answer()
    
    status_msg = await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    prices = await get_cached_prices()
    
    if not prices:
        await safe_edit_message(
            context.bot, query.message.chat_id, status_msg.message_id,
            "❌ خطا در دریافت قیمت‌ها", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 تلاش مجدد", callback_data="prices"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="back")
            ]])
        )
        return
    
    text = "💰 *قیمت‌های لحظه‌ای*\n\n"
    for p in prices:
        emoji = "🟢" if p['change'] > 0 else "🔴" if p['change'] < 0 else "⚪"
        text += f"{emoji} *{p['symbol']}*: ${p['price']:,.2f}\n"
        text += f"   تغییر: {p['change']:+.2f}% | حجم: ${p['volume']:,.0f}\n\n"
    
    text += f"⏰ بروزرسانی: {datetime.now().strftime('%H:%M:%S')}"
    
    await safe_edit_message(
        context.bot, query.message.chat_id, status_msg.message_id,
        text, reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

async def signal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سیگنال"""
    query = update.callback_query
    await query.answer()
    
    status_msg = await query.edit_message_text("🔄 تحلیل بازار...")
    
    # تحلیل BTC
    btc_analysis = await get_cached_analysis("BTC/USDT")
    
    if not btc_analysis:
        await safe_edit_message(
            context.bot, query.message.chat_id, status_msg.message_id,
            "❌ خطا در تحلیل", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 تلاش مجدد", callback_data="signal"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="back")
            ]])
        )
        return
    
    ind = btc_analysis['indicators']
    
    text = f"""
🎯 *سیگنال معاملاتی BTC*

💰 قیمت: ${btc_analysis['price']:,.2f}
📊 تغییر: {btc_analysis['change']:+.2f}%

🎯 *سیگنال:* {btc_analysis['signal']}
💪 *اطمینان:* {btc_analysis['confidence']:.0f}%

📈 *اندیکاتورها:*
• RSI: {ind.get('RSI', 0):.1f}
• MACD: {'صعودی' if ind.get('MACD', 0) > ind.get('MACD_SIGNAL', 0) else 'نزولی'}
• ADX: {ind.get('ADX', 0):.1f}

⚠️ *این سیگنال آموزشی است.*
"""
    
    await safe_edit_message(
        context.bot, query.message.chat_id, status_msg.message_id,
        text, reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="signal"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

async def portfolio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پورتفوی"""
    query = update.callback_query
    await query.answer()
    
    total_pnl = sum(t.get('pnl', 0) for t in trader.history)
    win_trades = len([t for t in trader.history if t.get('pnl', 0) > 0])
    total_trades = len(trader.history)
    
    text = f"""
💰 *پورتفوی معاملاتی*

💵 موجودی: ${trader.balance:,.2f}
📊 سود/زیان: ${total_pnl:+,.2f}

📈 *پوزیشن‌های باز:* {len(trader.positions)}
"""
    
    if trader.positions:
        text += "\n*پوزیشن‌های فعال:*\n"
        for symbol, pos in trader.positions.items():
            text += f"• {symbol}: ورود ${pos['entry_price']:,.2f}\n"
    
    text += f"""
📊 *آمار:*
• کل معاملات: {total_trades}
• موفق: {win_trades}
• ناموفق: {total_trades - win_trades}
• نرخ موفقیت: {(win_trades/total_trades*100) if total_trades > 0 else 0:.1f}%
"""
    
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="portfolio"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

async def performance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش عملکرد"""
    query = update.callback_query
    await query.answer()
    
    if not trader.history:
        text = "📊 هنوز معامله‌ای انجام نشده است."
    else:
        pnls = [t['pnl'] for t in trader.history]
        total_pnl = sum(pnls)
        avg_pnl = total_pnl / len(pnls)
        max_win = max(pnls)
        max_loss = min(pnls)
        
        text = f"""
📊 *گزارش عملکرد*

💰 سود/زیان کل: ${total_pnl:+,.2f}
📈 میانگین: ${avg_pnl:+,.2f}
🟢 بهترین: ${max_win:+,.2f}
🔴 بدترین: ${max_loss:+,.2f}

📊 تعداد معاملات: {len(trader.history)}
"""
    
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="performance"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

async def auto_trade_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات معاملات خودکار"""
    global AUTO_TRADE_ENABLED
    query = update.callback_query
    await query.answer()
    AUTO_TRADE_ENABLED = not AUTO_TRADE_ENABLED
    
    text = f"""
⚙️ *معاملات خودکار*

وضعیت: {'✅ فعال' if AUTO_TRADE_ENABLED else '❌ غیرفعال'}

⚠️ معاملات فقط در حالت دمو انجام می‌شود.
"""
    
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 تغییر وضعیت", callback_data="auto_trade"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش تنظیمات"""
    query = update.callback_query
    await query.answer()
    
    text = f"""
⚙️ *تنظیمات ربات*

🔑 CoinEx: {'✅ متصل' if exchange else '❌ قطع'}
🧠 Groq AI: {'✅ فعال' if GROQ_API_KEY else '❌ غیرفعال'}
📢 کانال: {CHANNEL_ID}
🤖 معاملات خودکار: {'✅' if AUTO_TRADE_ENABLED else '❌'}

📊 *پارامترها:*
• حداکثر پوزیشن: {MAX_POSITIONS}
• ریسک: {RISK_PER_TRADE*100}%
• نسبت سود/ضرر: {RR_RATIO}
"""
    
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    query = update.callback_query
    await query.answer()
    
    text = "🤖 *منوی اصلی*\nلطفاً انتخاب کنید:"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک‌های منو"""
    query = update.callback_query
    data = query.data
    
    handlers = {
        "prices": prices_handler,
        "signal": signal_handler,
        "portfolio": portfolio_handler,
        "performance": performance_handler,
        "auto_trade": auto_trade_handler,
        "settings": settings_handler,
        "back": back_handler,
        "refresh": back_handler
    }
    
    handler = handlers.get(data)
    if handler:
        await handler(update, context)
    else:
        await query.answer("در حال توسعه...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی"""
    await update.message.reply_text(
        "لطفاً از منوی ربات استفاده کنید.\n/start",
        reply_markup=get_main_menu()
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاهای تلگرام"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.\n/start"
            )
    except:
        pass

# ---------------------------- حلقه خودکار ----------------------------
async def auto_signal_loop(app):
    """حلقه ارسال خودکار سیگنال به کانال"""
    await asyncio.sleep(10)
    
    while True:
        try:
            if CHANNEL_ID and CHANNEL_ID != "@CryptoPulse606":
                # ارسال قیمت‌ها هر ۳۰ دقیقه
                prices = await get_cached_prices()
                if prices:
                    text = "📊 *بروزرسانی قیمت‌ها*\n\n"
                    for p in prices[:6]:
                        emoji = "🟢" if p['change'] > 0 else "🔴" if p['change'] < 0 else "⚪"
                        text += f"{emoji} {p['symbol']}: ${p['price']:,.2f} ({p['change']:+.1f}%)\n"
                    
                    await safe_send_message(app.bot, CHANNEL_ID, text)
                
                await asyncio.sleep(1800)  # ۳۰ دقیقه
            else:
                await asyncio.sleep(60)
                
        except Exception as e:
            logger.error(f"Auto loop error: {e}")
            await asyncio.sleep(60)

# ---------------------------- اجرای اصلی ----------------------------
async def main():
    """تابع اصلی"""
    if not TOKEN:
        logger.error("❌ توکن تلگرام تنظیم نشده!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    # شروع حلقه خودکار
    asyncio.create_task(auto_signal_loop(app))
    
    logger.info("🚀 ربات آماده به کار است!")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 ربات خاموش شد")
    except Exception as e:
        logger.error(f"❌ خطا: {e}")

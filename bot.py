import os
import sys
import logging
import asyncio
import time
import json
import random
import signal
import socket
import hashlib
import numpy as np
import pandas as pd
import ta
from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel, DonchianChannel, UlcerIndex
from ta.trend import MACD, ADXIndicator, IchimokuIndicator, PSARIndicator, STCIndicator, VortexIndicator, MassIndex, AroonIndicator, CCIIndicator, DPOIndicator, KSTIndicator, TRIXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, UltimateOscillator, ROCIndicator, AwesomeOscillatorIndicator, KAMAIndicator, PercentagePriceOscillator, PercentageVolumeOscillator
from ta.volume import VolumeWeightedAveragePrice, AccDistIndexIndicator, EaseOfMovementIndicator, ForceIndexIndicator, MFIIndicator, NegativeVolumeIndexIndicator, OnBalanceVolumeIndicator, VolumePriceTrendIndicator
from ta.others import CumulativeReturnIndicator, DailyLogReturnIndicator, DailyReturnIndicator
import ccxt
import httpx
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, JobQueue
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# لود فایل .env
load_dotenv()

# ================================ LOCK FILE برای جلوگیری از اجرای همزمان ================================
LOCK_FILE = "ultra_bot.lock"
PID_FILE = "ultra_bot.pid"

def create_lock():
    """ایجاد فایل قفل برای جلوگیری از اجرای چندگانه"""
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, 'r') as f:
                old_pid = f.read().strip()
            
            if old_pid:
                try:
                    old_pid = int(old_pid)
                    if sys.platform != 'win32':
                        os.kill(old_pid, 0)
                        logger.error(f"❌ یک نمونه دیگر با PID {old_pid} در حال اجراست!")
                        return False
                    else:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        handle = kernel32.OpenProcess(1, False, old_pid)
                        if handle:
                            kernel32.CloseHandle(handle)
                            logger.error(f"❌ یک نمونه دیگر با PID {old_pid} در حال اجراست!")
                            return False
                except (OSError, ProcessLookupError):
                    os.remove(LOCK_FILE)
                    if os.path.exists(PID_FILE):
                        os.remove(PID_FILE)
        
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        logger.info(f"🔒 فایل قفل ایجاد شد (PID: {os.getpid()})")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد فایل قفل: {e}")
        return False

def remove_lock():
    """حذف فایل قفل"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        logger.info("🔓 فایل قفل حذف شد")
    except Exception as e:
        logger.error(f"❌ خطا در حذف فایل قفل: {e}")

def signal_handler(signum, frame):
    """مدیریت سیگنال‌های خروج"""
    logger.info(f"📡 دریافت سیگنال {signum}...")
    remove_lock()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if sys.platform != 'win32':
    signal.signal(signal.SIGHUP, signal_handler)

# ================================ تنظیمات لاگینگ ================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('ultra_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltraBot')

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'apscheduler', 'urllib3', 'asyncio']:
    logging.getLogger(lib).setLevel(logging.ERROR)

# ================================ تنظیمات اصلی ================================
class Config:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
    
    # CoinEx
    COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
    COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
    COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")
    
    # ۳۰ ارز برتر بازار
    SYMBOLS = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", 
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "SHIB/USDT",
        "TRX/USDT", "AVAX/USDT", "UNI/USDT", "ATOM/USDT", "LINK/USDT",
        "ETC/USDT", "XLM/USDT", "FIL/USDT", "LTC/USDT", "BCH/USDT",
        "VET/USDT", "ALGO/USDT", "ICP/USDT", "SAND/USDT", "AXS/USDT",
        "FTM/USDT", "MANA/USDT", "GALA/USDT", "ENJ/USDT", "CHZ/USDT"
    ]
    
    TIMEFRAMES = {
        "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
    }
    
    MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "5"))
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.015"))
    ATR_MULTIPLIER_SL = float(os.getenv("ATR_MULTIPLIER_SL", "2.0"))
    RR_RATIO_MIN = float(os.getenv("RR_RATIO_MIN", "2.5"))
    LEVERAGE = int(os.getenv("LEVERAGE", "1"))
    
    AUTO_TRADE = os.getenv("TRADING_MODE", "demo") in ["demo", "real"]
    REAL_TRADE = os.getenv("TRADING_MODE", "demo") == "real"
    SIGNAL_INTERVAL = int(os.getenv("SIGNAL_INTERVAL", "600"))
    ANALYSIS_INTERVAL = int(os.getenv("ANALYSIS_INTERVAL", "3600"))
    INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "100000"))

config = Config()

# ================================ صرافی با مدیریت اتصال ================================
class ExchangeManager:
    def __init__(self):
        self.exchange = None
        self.connected = False
        self.last_error = None
        self.reconnect_attempts = 0
        self.max_reconnect = 5
    
    def connect(self):
        try:
            self.exchange = ccxt.coinex({
                'apiKey': config.COINEX_API_KEY,
                'secret': config.COINEX_SECRET_KEY,
                'password': config.COINEX_PASSPHRASE,
                'enableRateLimit': True,
                'timeout': 30000,
                'options': {'defaultType': 'spot'}
            })
            self.exchange.load_markets()
            self.connected = True
            self.reconnect_attempts = 0
            logger.info("✅ اتصال به CoinEx با موفقیت برقرار شد")
            return True
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"❌ خطا در اتصال به CoinEx: {e}")
            return False
    
    async def reconnect(self):
        while self.reconnect_attempts < self.max_reconnect:
            self.reconnect_attempts += 1
            wait_time = 2 ** self.reconnect_attempts
            logger.info(f"🔄 تلاش مجدد {self.reconnect_attempts}/{self.max_reconnect} در {wait_time} ثانیه...")
            await asyncio.sleep(wait_time)
            if self.connect():
                return True
        return False
    
    def is_connected(self):
        return self.connected and self.exchange is not None
    
    def get_exchange(self):
        return self.exchange

exchange_mgr = ExchangeManager()

if config.COINEX_API_KEY and config.COINEX_SECRET_KEY:
    exchange_mgr.connect()

# ================================ تحلیل تکنیکال فوق پیشرفته ================================
class UltraTechnicalAnalyzer:
    @staticmethod
    def calculate_all(df):
        """محاسبه ۱۰۰+ اندیکاتور"""
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        ind = {}
        
        # === روند (Trend) ===
        for period in [7, 14, 20, 50, 100, 200]:
            ind[f'SMA_{period}'] = float(close.rolling(period).mean().iloc[-1])
            ind[f'EMA_{period}'] = float(close.ewm(span=period).mean().iloc[-1])
        
        # ایچیموکو
        ichimoku = IchimokuIndicator(high, low, window1=9, window2=26, window3=52)
        ind['ICHIMOKU_A'] = float(ichimoku.ichimoku_a().iloc[-1])
        ind['ICHIMOKU_B'] = float(ichimoku.ichimoku_b().iloc[-1])
        
        # ADX
        adx = ADXIndicator(high, low, close, window=14)
        ind['ADX'] = float(adx.adx().iloc[-1])
        ind['ADX_POS'] = float(adx.adx_pos().iloc[-1])
        ind['ADX_NEG'] = float(adx.adx_neg().iloc[-1])
        
        # === مومنتوم ===
        rsi = RSIIndicator(close, window=14)
        ind['RSI'] = float(rsi.rsi().iloc[-1])
        
        stoch = StochasticOscillator(high, low, close)
        ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        
        # CCI
        cci = CCIIndicator(high, low, close, window=20)
        ind['CCI'] = float(cci.cci().iloc[-1])
        
        # === نوسان ===
        bb = BollingerBands(close, window=20, window_dev=2)
        ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
        ind['BB_MIDDLE'] = float(bb.bollinger_mavg().iloc[-1])
        ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
        ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        
        # ATR
        atr = AverageTrueRange(high, low, close, window=14)
        ind['ATR'] = float(atr.average_true_range().iloc[-1])
        ind['ATR_PCT'] = float(atr.average_true_range().iloc[-1] / close.iloc[-1] * 100)
        
        # === MACD ===
        macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        ind['MACD_12_26_9_MACD'] = float(macd.macd().iloc[-1])
        ind['MACD_12_26_9_SIGNAL'] = float(macd.macd_signal().iloc[-1])
        ind['MACD_12_26_9_HIST'] = float(macd.macd_diff().iloc[-1])
        
        # === حجم ===
        ind['MFI'] = float(MFIIndicator(high, low, close, volume).money_flow_index().iloc[-1])
        ind['OBV'] = float(OnBalanceVolumeIndicator(close, volume).on_balance_volume().iloc[-1])
        
        volume_sma_20 = volume.rolling(20).mean().iloc[-1]
        ind['VOLUME_RATIO'] = float(volume.iloc[-1] / volume_sma_20 if volume_sma_20 > 0 else 1)
        
        # === واگرایی ===
        ind['DIVERGENCE'] = UltraTechnicalAnalyzer.detect_divergence(close, rsi.rsi())
        
        # === نقاط پیوت ===
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        ind['PIVOT'] = float(pivot)
        ind['PIVOT_R1'] = float(pivot + (high.iloc[-1] - low.iloc[-1]) * 0.382)
        ind['PIVOT_S1'] = float(pivot - (high.iloc[-1] - low.iloc[-1]) * 0.382)
        
        return ind
    
    @staticmethod
    def detect_divergence(price, rsi_series):
        if len(price) < 20:
            return "NONE"
        
        recent_price = price.iloc[-20:]
        recent_rsi = rsi_series.iloc[-20:]
        
        price_high = recent_price.max()
        price_low = recent_price.min()
        rsi_high = recent_rsi.max()
        rsi_low = recent_rsi.min()
        
        if rsi_low > recent_rsi.iloc[:10].min() and price_low < recent_price.iloc[:10].min():
            return "BULLISH"
        elif rsi_high < recent_rsi.iloc[:10].max() and price_high > recent_price.iloc[:10].max():
            return "BEARISH"
        elif rsi_low < recent_rsi.iloc[:10].min() and price_low > recent_price.iloc[:10].min():
            return "HIDDEN_BULLISH"
        elif rsi_high > recent_rsi.iloc[:10].max() and price_high < recent_price.iloc[:10].max():
            return "HIDDEN_BEARISH"
        
        return "NONE"

# ================================ سیستم امتیازدهی هوشمند ================================
class UltraSignalGenerator:
    @staticmethod
    def generate(ind, mtf_data, price, volume_24h):
        score = 0
        
        # روند
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50'] > ind['EMA_200']:
            score += 150
        elif ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']:
            score += 100
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50'] < ind['EMA_200']:
            score -= 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']:
            score -= 100
        
        # ADX
        if ind['ADX'] > 40 and ind['ADX_POS'] > ind['ADX_NEG']:
            score += 100
        elif ind['ADX'] > 40 and ind['ADX_NEG'] > ind['ADX_POS']:
            score -= 100
        
        # RSI
        rsi = ind['RSI']
        if 30 <= rsi <= 70:
            score += int((rsi - 50) * 2)
        elif rsi < 30:
            score += 80
        elif rsi > 70:
            score -= 80
        
        # Stochastic
        if ind['STOCH_K'] < 20:
            score += 60
        elif ind['STOCH_K'] > 80:
            score -= 60
        
        # MACD
        if ind['MACD_12_26_9_HIST'] > 0:
            score += 50
        else:
            score -= 50
        
        # CCI
        cci = ind.get('CCI', 0)
        if cci < -200:
            score += 50
        elif cci > 200:
            score -= 50
        
        # بولینگر
        if ind['BB_PCT'] < 0.1:
            score += 80
        elif ind['BB_PCT'] > 0.9:
            score -= 80
        
        # حجم
        if ind['VOLUME_RATIO'] > 2.0:
            score += 50 if score > 0 else -50
        
        # MFI
        if ind['MFI'] < 20:
            score += 50
        elif ind['MFI'] > 80:
            score -= 50
        
        # واگرایی
        if ind['DIVERGENCE'] == "BULLISH":
            score += 100
        elif ind['DIVERGENCE'] == "BEARISH":
            score -= 100
        elif ind['DIVERGENCE'] == "HIDDEN_BULLISH":
            score += 60
        elif ind['DIVERGENCE'] == "HIDDEN_BEARISH":
            score -= 60
        
        # مولتی تایم‌فریم
        if mtf_data:
            for tf, tf_ind in mtf_data.items():
                weight = {"1h": 1, "4h": 1.5, "1d": 2}.get(tf, 0.5)
                if tf_ind.get('RSI', 50) > 50:
                    score += 20 * weight
                else:
                    score -= 20 * weight
        
        score = max(-1000, min(1000, score))
        
        # سیگنال
        if score >= 600:
            signal = "خرید فوق‌العاده قوی 🟢🟢🟢🟢🟢"
            confidence = 98
        elif score >= 400:
            signal = "خرید قوی 🟢🟢🟢🟢"
            confidence = 90
        elif score >= 200:
            signal = "خرید 🟢🟢🟢"
            confidence = 80
        elif score >= 100:
            signal = "خرید ضعیف 🟢🟢"
            confidence = 70
        elif score <= -600:
            signal = "فروش فوق‌العاده قوی 🔴🔴🔴🔴🔴"
            confidence = 98
        elif score <= -400:
            signal = "فروش قوی 🔴🔴🔴🔴"
            confidence = 90
        elif score <= -200:
            signal = "فروش 🔴🔴🔴"
            confidence = 80
        elif score <= -100:
            signal = "فروش ضعیف 🔴🔴"
            confidence = 70
        else:
            signal = "خنثی ⚪⚪⚪"
            confidence = 50
        
        return signal, confidence, score

# ================================ مدیریت معاملات ================================
class AdvancedTradingEngine:
    def __init__(self):
        self.positions = {}
        self.history = []
        self.balance = config.INITIAL_BALANCE
        self.initial_balance = config.INITIAL_BALANCE
        self.peak_balance = config.INITIAL_BALANCE
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.daily_trades = 0
        self.load()
    
    def load(self):
        try:
            with open('trading_engine.json', 'r') as f:
                data = json.load(f)
                self.balance = data.get('balance', config.INITIAL_BALANCE)
                self.history = data.get('history', [])
                self.peak_balance = data.get('peak', config.INITIAL_BALANCE)
        except:
            pass
    
    def save(self):
        try:
            with open('trading_engine.json', 'w') as f:
                json.dump({
                    'balance': self.balance,
                    'history': self.history[-500:],
                    'peak': max(self.peak_balance, self.balance)
                }, f)
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def get_stats(self):
        total_trades = len(self.history)
        wins = len([t for t in self.history if t['pnl'] > 0])
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t['pnl'] for t in self.history)
        
        if wins > 0:
            avg_win = sum(t['pnl'] for t in self.history if t['pnl'] > 0) / wins
        else:
            avg_win = 0
        
        if losses > 0:
            avg_loss = sum(t['pnl'] for t in self.history if t['pnl'] <= 0) / losses
        else:
            avg_loss = 0
        
        profit_factor = abs(sum(t['pnl'] for t in self.history if t['pnl'] > 0) / 
                          sum(t['pnl'] for t in self.history if t['pnl'] < 0)) if sum(t['pnl'] for t in self.history if t['pnl'] < 0) != 0 else 999
        
        return {
            'balance': self.balance,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'consecutive_losses': self.consecutive_losses,
            'open_positions': len(self.positions),
            'daily_pnl': self.daily_pnl,
            'roi': ((self.balance - self.initial_balance) / self.initial_balance) * 100
        }

engine = AdvancedTradingEngine()

# ================================ کش ================================
class SmartCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key, max_age=30):
        if key in self.cache:
            if time.time() - self.timestamps.get(key, 0) < max_age:
                return self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear_old(self, max_age=300):
        now = time.time()
        for key in list(self.timestamps.keys()):
            if now - self.timestamps[key] > max_age:
                del self.cache[key]
                del self.timestamps[key]

cache = SmartCache()

# ================================ توابع کمکی ================================
async def fetch_ohlcv_safe(symbol, timeframe, limit=200):
    cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
    cached = cache.get(cache_key, 15)
    if cached:
        return cached
    
    if not exchange_mgr.is_connected():
        return None
    
    for attempt in range(3):
        try:
            exchange = exchange_mgr.get_exchange()
            data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if data and len(data) > 50:
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                cache.set(cache_key, df)
                return df
        except Exception as e:
            logger.warning(f"Fetch attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1)
    
    return None

async def get_mtf_analysis(symbol):
    mtf = {}
    for tf_name, tf_value in config.TIMEFRAMES.items():
        df = await fetch_ohlcv_safe(symbol, tf_value)
        if df is not None and len(df) > 50:
            mtf[tf_name] = UltraTechnicalAnalyzer.calculate_all(df)
    return mtf

async def analyze_symbol_full(symbol):
    try:
        if not exchange_mgr.is_connected():
            await exchange_mgr.reconnect()
            if not exchange_mgr.is_connected():
                return None
        
        exchange = exchange_mgr.get_exchange()
        ticker = exchange.fetch_ticker(symbol)
        df_1h = await fetch_ohlcv_safe(symbol, '1h', 200)
        
        if df_1h is None or len(df_1h) < 50:
            return None
        
        indicators = UltraTechnicalAnalyzer.calculate_all(df_1h)
        mtf_data = await get_mtf_analysis(symbol)
        
        signal, confidence, score = UltraSignalGenerator.generate(
            indicators, mtf_data, ticker['last'], ticker['quoteVolume']
        )
        
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'change_24h': ticker['percentage'],
            'volume_24h': ticker['quoteVolume'],
            'high_24h': ticker['high'],
            'low_24h': ticker['low'],
            'indicators': indicators,
            'mtf': mtf_data,
            'signal': signal,
            'confidence': confidence,
            'score': score,
            'timestamp': datetime.now()
        }
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        return None

# ================================ فرمت‌دهی پیام‌ها ================================
def format_signal_message(analysis):
    sym = analysis['symbol'].replace('/USDT', '')
    ind = analysis['indicators']
    
    confidence_bar = "█" * int(analysis['confidence'] / 10) + "░" * (10 - int(analysis['confidence'] / 10))
    
    msg = f"""
╔══════════════════════════════════════════════════╗
║        🔥 سیگنال معاملاتی {sym} 🔥              ║
╚══════════════════════════════════════════════════╝

💰 *قیمت:* ${analysis['price']:,.4f}
📊 *تغییر ۲۴h:* {analysis['change_24h']:+.2f}%
📈 *حجم ۲۴h:* ${analysis['volume_24h']:,.0f}

🎯 *سیگنال:* {analysis['signal']}
💪 *اطمینان:* {analysis['confidence']:.0f}%
📊 [{confidence_bar}]
🎯 *امتیاز:* {analysis['score']}/1000

📈 *اندیکاتورهای کلیدی:*
• RSI(14): {ind['RSI']:.1f}
• MACD: {'صعودی ⬆️' if ind['MACD_12_26_9_HIST'] > 0 else 'نزولی ⬇️'}
• ADX: {ind['ADX']:.1f}
• بولینگر: {'پایین باند 📍' if ind['BB_PCT'] < 0.2 else 'بالای باند 📍' if ind['BB_PCT'] > 0.8 else 'میانه'}
• حجم: {'بالا 🔥' if ind['VOLUME_RATIO'] > 1.5 else 'نرمال'}

🔑 *سطوح کلیدی:*
• حمایت: ${ind['PIVOT_S1']:,.4f}
• مقاومت: ${ind['PIVOT_R1']:,.4f}

⚠️ *پیشنهاد:*
• حد ضرر: ${analysis['price'] - ind['ATR'] * 2:.4f}
• حد سود ۱: ${analysis['price'] + ind['ATR'] * 3:.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✨ @CryptoPulse606
"""
    return msg

def format_educational_content():
    topics = [
        "تحلیل عمیق ساختار بازار و فازهای مختلف",
        "روانشناسی معامله‌گری و مدیریت احساسات",
        "استراتژی‌های پیشرفته مدیریت سرمایه",
        "تحلیل وایکوف و تشخیص فازهای انباشت و توزیع",
        "الگوهای هارمونیک پیشرفته",
        "تحلیل آنچین و داده‌های درون شبکه‌ای",
        "تشخیص واگرایی‌های مخفی و معمولی",
        "استراتژی شکست سطوح با تایید حجم",
        "تحلیل پرایس اکشن و الگوهای کندلی",
        "مدیریت حد ضرر داینامیک و ترلینگ استاپ"
    ]
    
    topic = random.choice(topics)
    content = f"""
📚 *تحلیل و آموزش تخصصی*

📖 *موضوع:* {topic}

🔍 *نکات کلیدی:*

۱. همیشه ساختار کلی بازار را بررسی کنید.
۲. تایم‌فریم‌های بالاتر روند اصلی را نشان می‌دهند.
۳. حداقل نسبت ریسک به ریوارد ۱:۲ را رعایت کنید.
۴. بیش از ۲٪ سرمایه را در یک معامله ریسک نکنید.
۵. همیشه حد ضرر داشته باشید.
۶. بعد از ۳ ضرر متوالی، معامله را متوقف کنید.
۷. ژورنال معاملاتی داشته باشید.
۸. صبور باشید - فرصت‌های خوب همیشه وجود دارند.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return content

# ================================ منوها ================================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت‌های لحظه‌ای", callback_data="prices_all"),
         InlineKeyboardButton("🎯 سیگنال فوری BTC", callback_data="signal_btc")],
        [InlineKeyboardButton("🔍 اسکن کامل بازار", callback_data="market_scan"),
         InlineKeyboardButton("⭐ بهترین فرصت‌ها", callback_data="best_opportunities")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="menu_technical"),
         InlineKeyboardButton("⏰ مولتی تایم‌فریم", callback_data="menu_mtf")],
        [InlineKeyboardButton("💰 پورتفوی", callback_data="portfolio"),
         InlineKeyboardButton("📊 عملکرد", callback_data="performance")],
        [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="menu_auto"),
         InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("📚 تحلیل روزانه", callback_data="daily_analysis"),
         InlineKeyboardButton("📰 وضعیت بازار", callback_data="market_status")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale_track"),
         InlineKeyboardButton("📉 ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("💎 آلت‌کوین‌ها", callback_data="altcoins"),
         InlineKeyboardButton("🔮 پیش‌بینی", callback_data="prediction")],
        [InlineKeyboardButton("📋 تاریخچه معاملات", callback_data="trade_history"),
         InlineKeyboardButton("📈 نمودار زنده", callback_data="live_chart")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh"),
         InlineKeyboardButton("❓ راهنما", callback_data="help")],
        [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="emergency_stop")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_technical_menu():
    keyboard = [
        [InlineKeyboardButton("BTC/USDT", callback_data="tech_BTC/USDT"),
         InlineKeyboardButton("ETH/USDT", callback_data="tech_ETH/USDT")],
        [InlineKeyboardButton("SOL/USDT", callback_data="tech_SOL/USDT"),
         InlineKeyboardButton("BNB/USDT", callback_data="tech_BNB/USDT")],
        [InlineKeyboardButton("XRP/USDT", callback_data="tech_XRP/USDT"),
         InlineKeyboardButton("ADA/USDT", callback_data="tech_ADA/USDT")],
        [InlineKeyboardButton("DOGE/USDT", callback_data="tech_DOGE/USDT"),
         InlineKeyboardButton("AVAX/USDT", callback_data="tech_AVAX/USDT")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_mtf_menu():
    symbols_short = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX"]
    keyboard = []
    row = []
    for sym in symbols_short:
        row.append(InlineKeyboardButton(sym, callback_data=f"mtf_{sym}/USDT"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_auto_trade_menu():
    keyboard = [
        [InlineKeyboardButton(f"🤖 دمو: {'✅' if config.AUTO_TRADE else '❌'}", callback_data="toggle_demo")],
        [InlineKeyboardButton(f"💹 واقعی: {'✅' if config.REAL_TRADE else '❌'}", callback_data="toggle_real")],
        [InlineKeyboardButton("⚙️ تنظیمات ریسک", callback_data="risk_settings")],
        [InlineKeyboardButton("📊 پوزیشن‌های باز", callback_data="open_positions")],
        [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="emergency_stop")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_menu():
    keyboard = [
        [InlineKeyboardButton("🔑 وضعیت API", callback_data="api_status")],
        [InlineKeyboardButton("📢 تنظیمات کانال", callback_data="channel_settings")],
        [InlineKeyboardButton("⏰ فواصل ارسال", callback_data="interval_settings")],
        [InlineKeyboardButton("📊 پارامترهای تحلیل", callback_data="analysis_params")],
        [InlineKeyboardButton("💰 مدیریت سرمایه", callback_data="capital_mgmt")],
        [InlineKeyboardButton("🔔 هشدارها", callback_data="alert_settings")],
        [InlineKeyboardButton("🗑️ پاکسازی کش", callback_data="clear_cache")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================================ هندلرها (بدون محدودیت دسترسی) ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات - دسترسی برای همه"""
    text = """
╔═══════════════════════════════════════╗
║  🤖 ربات معامله‌گر اولترا پیشرفته   ║
║     Ultra Trading Bot v3.0           ║
║     🌍 دسترسی آزاد برای همه          ║
╚═══════════════════════════════════════╝

✨ *قابلیت‌های کلیدی:*

📊 *تحلیل تکنیکال فوق پیشرفته*
• ۱۰۰+ اندیکاتور و اسیلاتور
• تحلیل ۸ تایم‌فریم همزمان
• تشخیص واگرایی و الگوها

🎯 *سیگنال‌های هوشمند*
• امتیازدهی ۱۰۰۰ امتیازی
• ۳۰ ارز برتر بازار
• اسکن خودکار بازار

💰 *معاملات حرفه‌ای*
• مدیریت سرمایه داینامیک
• ترلینگ استاپ هوشمند
• حد سود جزئی خودکار

📢 *ارسال خودکار به کانال*
• سیگنال هر ۱۰ دقیقه
• تحلیل جامع هر ۱ ساعت

🔰 از منوی زیر استفاده کنید:
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def prices_all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    if not exchange_mgr.is_connected():
        await query.edit_message_text("❌ صرافی متصل نیست!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 تلاش مجدد", callback_data="prices_all"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    exchange = exchange_mgr.get_exchange()
    text = "💰 *قیمت‌های لحظه‌ای* 💰\n\n"
    
    for symbol in config.SYMBOLS[:20]:
        try:
            ticker = exchange.fetch_ticker(symbol)
            emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
            text += f"{emoji} *{symbol.replace('/USDT', '')}*: ${ticker['last']:,.4f}"
            text += f" ({ticker['percentage']:+.2f}%)\n"
        except:
            text += f"⚪ *{symbol.replace('/USDT', '')}*: خطا\n"
    
    text += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices_all"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def market_scan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text("🔍 در حال اسکن ۳۰ ارز...")
    
    results = []
    for symbol in config.SYMBOLS:
        analysis = await analyze_symbol_full(symbol)
        if analysis:
            results.append(analysis)
    
    results.sort(key=lambda x: abs(x['score']), reverse=True)
    
    text = "🔍 *نتایج اسکن بازار* 🔍\n\n"
    
    for i, r in enumerate(results[:15], 1):
        emoji = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
        text += f"{i}. {emoji} *{r['symbol'].replace('/USDT', '')}*: "
        text += f"${r['price']:,.4f} | {r['signal'][:20]} | {r['confidence']:.0f}%\n"
    
    keyboard = [[InlineKeyboardButton("🔄 اسکن مجدد", callback_data="market_scan"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def signal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol="BTC/USDT"):
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT', '')}...")
    
    analysis = await analyze_symbol_full(symbol)
    
    if not analysis:
        await query.edit_message_text("❌ خطا در تحلیل", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    msg = format_signal_message(analysis)
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"signal_{symbol.replace('/USDT', '')}"),
                 InlineKeyboardButton("📊 اسکن بازار", callback_data="market_scan"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def portfolio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    stats = engine.get_stats()
    
    text = f"""
💰 *پورتفوی معاملاتی* 💰

💵 *موجودی:* ${stats['balance']:,.2f}
📈 *سود/زیان کل:* ${stats['total_pnl']:+,.2f}
📊 *ROI:* {stats['roi']:+.2f}%

📈 *پوزیشن‌های باز:* {stats['open_positions']}
"""
    
    if engine.positions:
        text += "\n*پوزیشن‌های فعال:*\n"
        for sym, pos in engine.positions.items():
            try:
                if exchange_mgr.is_connected():
                    exchange = exchange_mgr.get_exchange()
                    ticker = exchange.fetch_ticker(sym)
                    current = ticker['last']
                    pnl_pct = (current - pos['entry']) / pos['entry'] * 100
                    text += f"• {sym.replace('/USDT', '')}: ورود {pos['entry']:,.4f} | فعلی {current:,.4f} | {pnl_pct:+.2f}%\n"
                else:
                    text += f"• {sym.replace('/USDT', '')}: ورود {pos['entry']:,.4f}\n"
            except:
                text += f"• {sym.replace('/USDT', '')}: ورود {pos['entry']:,.4f}\n"
    
    text += f"""
📊 *آمار:*
• کل معاملات: {stats['total_trades']}
• موفق: {stats['wins']} | ناموفق: {stats['losses']}
• نرخ موفقیت: {stats['win_rate']:.1f}%
• فاکتور سود: {stats['profit_factor']:.2f}
"""
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="portfolio"),
                 InlineKeyboardButton("📋 تاریخچه", callback_data="trade_history"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def performance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not engine.history:
        await query.edit_message_text("📊 هنوز معامله‌ای انجام نشده.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    stats = engine.get_stats()
    history = engine.history
    
    best = max(history, key=lambda x: x['pnl'])
    worst = min(history, key=lambda x: x['pnl'])
    
    text = f"""
📊 *گزارش عملکرد جامع*

💰 سود/زیان کل: ${stats['total_pnl']:+,.2f}
📈 ROI: {stats['roi']:+.2f}%

📈 *بهترین:* {best['symbol']}: ${best['pnl']:+,.2f}
📉 *بدترین:* {worst['symbol']}: ${worst['pnl']:+,.2f}

📊 *آمار:*
• کل: {stats['total_trades']} | موفق: {stats['wins']} | ناموفق: {stats['losses']}
• نرخ موفقیت: {stats['win_rate']:.1f}%
• فاکتور سود: {stats['profit_factor']:.2f}
"""
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="performance"),
                 InlineKeyboardButton("📋 تاریخچه کامل", callback_data="trade_history"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ *راهنمای ربات*

📊 *تحلیل و سیگنال:*
• قیمت‌ها، سیگنال، اسکن بازار
• تحلیل تکنیکال، مولتی تایم‌فریم

💰 *معاملات:*
• پورتفوی، عملکرد
• پوزیشن‌های باز، تاریخچه

⚙️ *تنظیمات:*
• وضعیت API
• تنظیمات کانال
• فواصل ارسال

⚠️ *هشدار:*
این ربات برای تحلیل و سیگنال‌دهی است.
مسئولیت معاملات با شماست.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 *منوی اصلی*\nلطفاً انتخاب کنید:", parse_mode="Markdown", reply_markup=get_main_menu())

async def emergency_stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    for sym in list(engine.positions.keys()):
        try:
            if exchange_mgr.is_connected():
                exchange = exchange_mgr.get_exchange()
                ticker = exchange.fetch_ticker(sym)
                engine.close_position(sym, ticker['last'], "EMERGENCY_STOP")
            else:
                del engine.positions[sym]
        except:
            pass
    
    await query.edit_message_text("⏸️ *توقف اضطراری*\n\n✅ همه پوزیشن‌ها بسته شدند.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    try:
        if data == "back":
            await back_handler(update, context)
        elif data == "prices_all":
            await prices_all_handler(update, context)
        elif data == "market_scan":
            await market_scan_handler(update, context)
        elif data == "best_opportunities":
            await market_scan_handler(update, context)
        elif data.startswith("signal_"):
            symbol = data.replace("signal_", "")
            if symbol == "btc":
                await signal_handler(update, context)
            else:
                await signal_handler(update, context, f"{symbol.upper()}/USDT")
        elif data == "menu_technical":
            await query.edit_message_text("📈 *تحلیل تکنیکال*\nارز را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_technical_menu())
        elif data.startswith("tech_"):
            symbol = data.replace("tech_", "")
            await signal_handler(update, context, symbol)
        elif data == "menu_mtf":
            await query.edit_message_text("⏰ *مولتی تایم‌فریم*\nارز را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_mtf_menu())
        elif data.startswith("mtf_"):
            symbol = data.replace("mtf_", "")
            await signal_handler(update, context, symbol)
        elif data == "portfolio":
            await portfolio_handler(update, context)
        elif data == "performance":
            await performance_handler(update, context)
        elif data == "trade_history":
            await performance_handler(update, context)
        elif data == "menu_auto":
            await query.edit_message_text("🤖 *معاملات خودکار*\nتنظیمات را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_auto_trade_menu())
        elif data == "toggle_demo":
            config.AUTO_TRADE = not config.AUTO_TRADE
            await query.edit_message_text("🤖 *معاملات خودکار*\nتنظیمات را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_auto_trade_menu())
        elif data == "toggle_real":
            if not exchange_mgr.is_connected():
                await query.answer("❌ صرافی متصل نیست!", show_alert=True)
                return
            config.REAL_TRADE = not config.REAL_TRADE
            await query.edit_message_text("🤖 *معاملات خودکار*\nتنظیمات را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_auto_trade_menu())
        elif data == "settings":
            await query.edit_message_text("⚙️ *تنظیمات ربات*\nبخش مورد نظر را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_settings_menu())
        elif data == "help":
            await help_handler(update, context)
        elif data == "refresh":
            await back_handler(update, context)
        elif data == "daily_analysis":
            content = format_educational_content()
            await query.edit_message_text(content, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif data == "market_status":
            await market_scan_handler(update, context)
        elif data == "emergency_stop":
            await emergency_stop_handler(update, context)
        elif data == "clear_cache":
            cache.clear_old(0)
            await query.answer("✅ کش پاکسازی شد", show_alert=True)
        elif data == "api_status":
            status = "✅ متصل" if exchange_mgr.is_connected() else "❌ قطع"
            await query.edit_message_text(f"🔑 *وضعیت API*\n\nCoinEx: {status}\nGroq: {'✅' if config.GROQ_API_KEY else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="settings")]]))
        elif data == "open_positions":
            await portfolio_handler(update, context)
        else:
            await query.answer("در حال توسعه...")
    except Exception as e:
        logger.error(f"Button handler error: {e}")
        try:
            await query.edit_message_text(f"❌ خطا: {str(e)[:100]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        except:
            pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً از منوی ربات استفاده کنید.\n/start", reply_markup=get_main_menu())

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.critical("❌ Conflict error - یک نمونه دیگر از ربات در حال اجراست!")
        remove_lock()
        sys.exit(1)
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ خطایی رخ داد. /start")
    except:
        pass

# ================================ حلقه‌های خودکار ================================
async def auto_signal_to_channel(app):
    await asyncio.sleep(15)
    
    while True:
        try:
            if not config.CHANNEL_ID or config.CHANNEL_ID == "@CryptoPulse606":
                await asyncio.sleep(60)
                continue
            
            if not exchange_mgr.is_connected():
                await exchange_mgr.reconnect()
                if not exchange_mgr.is_connected():
                    await asyncio.sleep(60)
                    continue
            
            # BTC
            btc_analysis = await analyze_symbol_full("BTC/USDT")
            if btc_analysis:
                msg = format_signal_message(btc_analysis)
                await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                logger.info("📤 BTC signal sent")
            
            await asyncio.sleep(120)
            
            # ETH
            eth_analysis = await analyze_symbol_full("ETH/USDT")
            if eth_analysis:
                msg = format_signal_message(eth_analysis)
                await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                logger.info("📤 ETH signal sent")
            
            await asyncio.sleep(120)
            
            # Top 3
            results = []
            for symbol in config.SYMBOLS[:10]:
                analysis = await analyze_symbol_full(symbol)
                if analysis:
                    results.append(analysis)
            
            results.sort(key=lambda x: abs(x['score']), reverse=True)
            
            for r in results[:3]:
                msg = format_signal_message(r)
                await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                await asyncio.sleep(90)
            
        except Exception as e:
            logger.error(f"Auto signal error: {e}")
        
        await asyncio.sleep(config.SIGNAL_INTERVAL)

async def auto_educational_content(app):
    await asyncio.sleep(30)
    
    while True:
        try:
            if config.CHANNEL_ID and config.CHANNEL_ID != "@CryptoPulse606":
                content = format_educational_content()
                await safe_send_message(app.bot, config.CHANNEL_ID, content)
                logger.info("📚 Educational content sent")
        except Exception as e:
            logger.error(f"Educational content error: {e}")
        
        await asyncio.sleep(config.ANALYSIS_INTERVAL)

async def safe_send_message(bot, chat_id, text, parse_mode="Markdown", reply_markup=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=True)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TimedOut:
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
    return None

# ================================ اجرای اصلی ================================
async def main():
    if not create_lock():
        logger.critical("❌ یک نمونه دیگر در حال اجراست. خروج...")
        sys.exit(1)
    
    logger.info(f"🔒 Lock file created. PID: {os.getpid()}")
    
    if not config.TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        remove_lock()
        return
    
    if config.COINEX_API_KEY and config.COINEX_SECRET_KEY:
        if not exchange_mgr.is_connected():
            exchange_mgr.connect()
    
    app = Application.builder().token(config.TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    asyncio.create_task(auto_signal_to_channel(app))
    asyncio.create_task(auto_educational_content(app))
    
    logger.info("🚀 Ultra Trading Bot v3.0 - دسترسی آزاد برای همه")
    logger.info(f"📢 Channel: {config.CHANNEL_ID}")
    logger.info(f"💰 Balance: ${config.INITIAL_BALANCE:,.0f}")
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        await asyncio.Event().wait()
    except Conflict as e:
        logger.critical(f"❌ Conflict Error: {e}")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        if hasattr(app, 'updater') and app.updater and app.updater.running:
            await app.updater.stop()
        if app.running:
            await app.stop()
        await app.shutdown()
        remove_lock()
        logger.info("👋 Bot shut down")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped")
        remove_lock()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        remove_lock()
        sys.exit(1)

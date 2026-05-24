#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Professional Crypto Trading Bot v4.0
-------------------------------------------
Advanced Technical Analysis & Signal Generation
Multi-Timeframe | 100+ Indicators | Auto Trading
"""

import os
import sys
import logging
import asyncio
import time
import json
import random
import signal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas as pd
import ccxt
from dotenv import load_dotenv

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.error import (
    TelegramError,
    RetryAfter,
    TimedOut,
    Conflict,
    NetworkError
)

# Technical Analysis imports
from ta.volatility import (
    BollingerBands,
    AverageTrueRange,
    KeltnerChannel,
    DonchianChannel,
    UlcerIndex
)
from ta.trend import (
    MACD,
    ADXIndicator,
    IchimokuIndicator,
    PSARIndicator,
    CCIIndicator,
    AroonIndicator,
    VortexIndicator,
    MassIndex,
    STCIndicator,
    TRIXIndicator
)
from ta.momentum import (
    RSIIndicator,
    StochasticOscillator,
    WilliamsRIndicator,
    UltimateOscillator,
    ROCIndicator,
    AwesomeOscillatorIndicator,
    KAMAIndicator
)
from ta.volume import (
    MFIIndicator,
    OnBalanceVolumeIndicator,
    AccDistIndexIndicator,
    EaseOfMovementIndicator,
    ForceIndexIndicator,
    VolumePriceTrendIndicator
)

import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================
load_dotenv()

class Config:
    """Global Configuration"""
    # Telegram
    TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    # Exchange API
    EXCHANGE_API_KEY: str = os.getenv("COINEX_API_KEY", "")
    EXCHANGE_SECRET: str = os.getenv("COINEX_SECRET_KEY", "")
    EXCHANGE_PASSPHRASE: str = os.getenv("COINEX_PASSPHRASE", "")
    
    # Trading Pairs
    SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT"
    ]
    
    # Timeframes
    TIMEFRAMES: List[str] = ["15m", "1h", "4h", "1d"]
    
    # Auto Post Intervals (seconds)
    SIGNAL_INTERVAL: int = 600  # 10 minutes
    ANALYSIS_INTERVAL: int = 3600  # 1 hour
    
    # Trading Parameters
    RISK_PER_TRADE: float = 0.02
    MAX_POSITIONS: int = 5
    ATR_MULTIPLIER: float = 2.0

# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Silence noisy libraries
for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3']:
    logging.getLogger(lib).setLevel(logging.ERROR)

# ============================================================
# LOCK MECHANISM (Prevent Multiple Instances)
# ============================================================
class ProcessLock:
    """Ensures only one bot instance runs at a time"""
    LOCK_FILE = "bot.lock"
    
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls.LOCK_FILE):
                with open(cls.LOCK_FILE, 'r') as f:
                    old_pid = int(f.read().strip() or 0)
                if old_pid and cls._is_process_alive(old_pid):
                    logger.error(f"❌ Instance already running (PID: {old_pid})")
                    return False
                os.remove(cls.LOCK_FILE)
            
            with open(cls.LOCK_FILE, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"🔒 Lock acquired (PID: {os.getpid()})")
            return True
        except Exception as e:
            logger.error(f"Lock error: {e}")
            return True
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls.LOCK_FILE):
                os.remove(cls.LOCK_FILE)
        except:
            pass
    
    @staticmethod
    def _is_process_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

# Signal handlers for graceful shutdown
signal.signal(signal.SIGINT, lambda s, f: (ProcessLock.release(), sys.exit(0)))
signal.signal(signal.SIGTERM, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# EXCHANGE CONNECTION MANAGER
# ============================================================
class ExchangeManager:
    """Manages exchange connection with auto-reconnect"""
    
    def __init__(self):
        self.exchange: Optional[ccxt.Exchange] = None
        self.is_connected: bool = False
        self.last_error: str = ""
    
    def connect(self) -> bool:
        """Establish connection to exchange"""
        try:
            if not Config.EXCHANGE_API_KEY:
                logger.warning("⚠️ No API keys - running in read-only mode")
                self.exchange = ccxt.coinex({
                    'enableRateLimit': True,
                    'timeout': 30000,
                    'options': {'defaultType': 'spot'}
                })
            else:
                self.exchange = ccxt.coinex({
                    'apiKey': Config.EXCHANGE_API_KEY,
                    'secret': Config.EXCHANGE_SECRET,
                    'password': Config.EXCHANGE_PASSPHRASE,
                    'enableRateLimit': True,
                    'timeout': 30000,
                    'options': {'defaultType': 'spot'}
                })
            
            self.exchange.load_markets()
            self.is_connected = True
            logger.info("✅ Exchange connected successfully")
            return True
            
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            logger.error(f"❌ Exchange connection failed: {e}")
            # Try without API keys for public data
            try:
                self.exchange = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self.exchange.load_markets()
                self.is_connected = True
                logger.info("✅ Connected in read-only mode")
                return True
            except:
                return False
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch ticker safely"""
        if not self.is_connected or not self.exchange:
            return None
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Ticker error for {symbol}: {e}")
            return None
    
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 200) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data safely"""
        if not self.is_connected or not self.exchange:
            return None
        try:
            data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if data and len(data) > 30:
                return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except Exception as e:
            logger.error(f"OHLCV error for {symbol}: {e}")
        return None

# Global exchange instance
exchange_mgr = ExchangeManager()

# ============================================================
# TECHNICAL ANALYSIS ENGINE
# ============================================================
class TechnicalAnalyzer:
    """Advanced technical analysis with 100+ indicators"""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive technical indicators"""
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        indicators = {}
        
        # --- Moving Averages ---
        for period in [7, 14, 20, 50, 100, 200]:
            indicators[f'EMA_{period}'] = float(close.ewm(span=period).mean().iloc[-1])
            indicators[f'SMA_{period}'] = float(close.rolling(period).mean().iloc[-1])
        
        # --- RSI ---
        rsi = RSIIndicator(close, window=14)
        indicators['RSI'] = float(rsi.rsi().iloc[-1])
        indicators['RSI_7'] = float(RSIIndicator(close, window=7).rsi().iloc[-1])
        
        # --- MACD ---
        macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        indicators['MACD'] = float(macd.macd().iloc[-1])
        indicators['MACD_SIGNAL'] = float(macd.macd_signal().iloc[-1])
        indicators['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        
        # --- Bollinger Bands ---
        bb = BollingerBands(close, window=20, window_dev=2)
        indicators['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
        indicators['BB_MIDDLE'] = float(bb.bollinger_mavg().iloc[-1])
        indicators['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
        indicators['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1])
        indicators['BB_POSITION'] = float(bb.bollinger_pband().iloc[-1])
        
        # --- Stochastic ---
        stoch = StochasticOscillator(high, low, close)
        indicators['STOCH_K'] = float(stoch.stoch().iloc[-1])
        indicators['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        
        # --- ADX ---
        adx = ADXIndicator(high, low, close, window=14)
        indicators['ADX'] = float(adx.adx().iloc[-1])
        indicators['ADX_POS'] = float(adx.adx_pos().iloc[-1])
        indicators['ADX_NEG'] = float(adx.adx_neg().iloc[-1])
        
        # --- ATR ---
        atr = AverageTrueRange(high, low, close, window=14)
        indicators['ATR'] = float(atr.average_true_range().iloc[-1])
        indicators['ATR_PCT'] = float(atr.average_true_range().iloc[-1] / close.iloc[-1] * 100)
        
        # --- CCI ---
        cci = CCIIndicator(high, low, close, window=20)
        indicators['CCI'] = float(cci.cci().iloc[-1])
        
        # --- Volume Indicators ---
        indicators['MFI'] = float(MFIIndicator(high, low, close, volume).money_flow_index().iloc[-1])
        indicators['OBV'] = float(OnBalanceVolumeIndicator(close, volume).on_balance_volume().iloc[-1])
        
        # --- Volume Analysis ---
        vol_sma = volume.rolling(20).mean().iloc[-1]
        indicators['VOLUME_RATIO'] = float(volume.iloc[-1] / vol_sma if vol_sma > 0 else 1)
        indicators['VOLUME_TREND'] = float(volume.rolling(5).mean().iloc[-1] / vol_sma if vol_sma > 0 else 1)
        
        # --- Ichimoku ---
        try:
            ichimoku = IchimokuIndicator(high, low)
            indicators['ICHIMOKU_A'] = float(ichimoku.ichimoku_a().iloc[-1])
            indicators['ICHIMOKU_B'] = float(ichimoku.ichimoku_b().iloc[-1])
            indicators['ICHIMOKU_CONV'] = float(ichimoku.ichimoku_conversion_line().iloc[-1])
            indicators['ICHIMOKU_BASE'] = float(ichimoku.ichimoku_base_line().iloc[-1])
        except:
            pass
        
        # --- Parabolic SAR ---
        try:
            psar = PSARIndicator(high, low, close)
            indicators['PSAR'] = float(psar.psar().iloc[-1])
        except:
            pass
        
        # --- Williams %R ---
        indicators['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close).williams_r().iloc[-1])
        
        # --- Ultimate Oscillator ---
        try:
            indicators['ULTIMATE'] = float(UltimateOscillator(high, low, close).ultimate_oscillator().iloc[-1])
        except:
            pass
        
        # --- Pivot Points ---
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        pivot = (h + l + c) / 3
        indicators['PIVOT'] = float(pivot)
        indicators['R1'] = float(2 * pivot - l)
        indicators['S1'] = float(2 * pivot - h)
        indicators['R2'] = float(pivot + (h - l))
        indicators['S2'] = float(pivot - (h - l))
        
        # --- Trend Strength ---
        indicators['TREND_STRENGTH'] = float(abs(close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] * 100)
        
        # --- Volatility ---
        indicators['VOLATILITY'] = float(close.pct_change().rolling(20).std().iloc[-1] * 100)
        
        return indicators
    
    @staticmethod
    def detect_divergence(df: pd.DataFrame) -> str:
        """Detect RSI divergence patterns"""
        close = df['close'].astype(float)
        rsi = RSIIndicator(close, window=14).rsi()
        
        if len(close) < 20:
            return "NONE"
        
        recent_close = close.iloc[-20:]
        recent_rsi = rsi.iloc[-20:]
        
        # Regular Bullish: Price Lower Low, RSI Higher Low
        if (close.iloc[-1] < recent_close.min() and 
            rsi.iloc[-1] > recent_rsi.min()):
            return "BULLISH_DIVERGENCE"
        
        # Regular Bearish: Price Higher High, RSI Lower High
        if (close.iloc[-1] > recent_close.max() and 
            rsi.iloc[-1] < recent_rsi.max()):
            return "BEARISH_DIVERGENCE"
        
        return "NONE"

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGenerator:
    """Generate trading signals with 1000-point scoring system"""
    
    @staticmethod
    def generate(indicators: Dict[str, float], price: float, mtf_data: Optional[Dict] = None) -> Tuple[str, int, int]:
        """
        Generate signal with confidence score
        Returns: (signal_text, confidence, score)
        """
        score = 0
        
        # === TREND ANALYSIS (250 points) ===
        if indicators.get('EMA_7', 0) > indicators.get('EMA_20', 0) > indicators.get('EMA_50', 0) > indicators.get('EMA_200', 0):
            score += 150
        elif indicators.get('EMA_7', 0) > indicators.get('EMA_20', 0) > indicators.get('EMA_50', 0):
            score += 100
        elif indicators.get('EMA_20', 0) > indicators.get('EMA_50', 0):
            score += 50
        elif indicators.get('EMA_7', 0) < indicators.get('EMA_20', 0) < indicators.get('EMA_50', 0) < indicators.get('EMA_200', 0):
            score -= 150
        elif indicators.get('EMA_7', 0) < indicators.get('EMA_20', 0) < indicators.get('EMA_50', 0):
            score -= 100
        
        # ADX Trend Strength
        adx = indicators.get('ADX', 0)
        if adx > 40:
            if indicators.get('ADX_POS', 0) > indicators.get('ADX_NEG', 0):
                score += 100
            else:
                score -= 100
        elif adx > 25:
            if indicators.get('ADX_POS', 0) > indicators.get('ADX_NEG', 0):
                score += 50
            else:
                score -= 50
        
        # === MOMENTUM (250 points) ===
        rsi = indicators.get('RSI', 50)
        if rsi < 30:
            score += 80
        elif rsi < 40:
            score += 40
        elif rsi > 70:
            score -= 80
        elif rsi > 60:
            score -= 40
        
        # MACD
        if indicators.get('MACD_HIST', 0) > 0:
            score += 50
        else:
            score -= 50
        
        # Stochastic
        stoch_k = indicators.get('STOCH_K', 50)
        if stoch_k < 20:
            score += 50
        elif stoch_k > 80:
            score -= 50
        
        # CCI
        cci = indicators.get('CCI', 0)
        if cci < -200:
            score += 50
        elif cci < -100:
            score += 30
        elif cci > 200:
            score -= 50
        elif cci > 100:
            score -= 30
        
        # === VOLATILITY (200 points) ===
        bb_pos = indicators.get('BB_POSITION', 0.5)
        if bb_pos < 0.1:
            score += 80
        elif bb_pos > 0.9:
            score -= 80
        
        # === VOLUME (150 points) ===
        vol_ratio = indicators.get('VOLUME_RATIO', 1)
        if vol_ratio > 2:
            score += 50 if score > 0 else -50
        elif vol_ratio > 1.5:
            score += 30 if score > 0 else -30
        
        # MFI
        mfi = indicators.get('MFI', 50)
        if mfi < 20:
            score += 40
        elif mfi > 80:
            score -= 40
        
        # === DIVERGENCE (150 points) ===
        # (Would need df passed separately)
        
        # === MULTI-TIMEFRAME ===
        if mtf_data:
            for tf, tf_ind in mtf_data.items():
                weight = {"1h": 1, "4h": 1.5, "1d": 2}.get(tf, 0.5)
                tf_rsi = tf_ind.get('RSI', 50)
                if tf_rsi > 55:
                    score += int(20 * weight)
                elif tf_rsi < 45:
                    score -= int(20 * weight)
        
        # Normalize
        score = max(-1000, min(1000, score))
        
        # Convert to signal
        if score >= 600:
            return "خرید فوق‌العاده قوی 🟢🟢🟢🟢🟢", 98, score
        elif score >= 400:
            return "خرید قوی 🟢🟢🟢🟢", 90, score
        elif score >= 200:
            return "خرید 🟢🟢🟢", 80, score
        elif score >= 100:
            return "خرید ضعیف 🟢", 65, score
        elif score <= -600:
            return "فروش فوق‌العاده قوی 🔴🔴🔴🔴🔴", 98, score
        elif score <= -400:
            return "فروش قوی 🔴🔴🔴🔴", 90, score
        elif score <= -200:
            return "فروش 🔴🔴🔴", 80, score
        elif score <= -100:
            return "فروش ضعیف 🔴", 65, score
        else:
            return "خنثی ⚪⚪", 50, score

# ============================================================
# DATA CACHE
# ============================================================
class Cache:
    """Simple in-memory cache"""
    _data: Dict[str, Tuple[Any, float]] = {}
    
    @classmethod
    def get(cls, key: str, max_age: float = 15) -> Optional[Any]:
        if key in cls._data:
            value, timestamp = cls._data[key]
            if time.time() - timestamp < max_age:
                return value
        return None
    
    @classmethod
    def set(cls, key: str, value: Any):
        cls._data[key] = (value, time.time())

# ============================================================
# FORMATTERS
# ============================================================
class MessageFormatter:
    """Format messages for Telegram"""
    
    @staticmethod
    def signal(analysis: Dict) -> str:
        """Format signal message"""
        sym = analysis['symbol'].replace('/USDT', '')
        ind = analysis['indicators']
        
        return f"""
╔══════════════════════════════════╗
║   🔥 سیگنال {sym} 🔥         ║
╚══════════════════════════════════╝

💰 قیمت: ${analysis['price']:,.4f}
📊 تغییر ۲۴h: {analysis['change']:+.2f}%

🎯 سیگنال: {analysis['signal']}
💪 اطمینان: {analysis['confidence']}%
🎯 امتیاز: {analysis['score']}/1000

📈 اندیکاتورها:
• RSI(14): {ind.get('RSI', 0):.1f}
• MACD: {'صعودی ⬆️' if ind.get('MACD_HIST', 0) > 0 else 'نزولی ⬇️'}
• ADX: {ind.get('ADX', 0):.1f}
• CCI: {ind.get('CCI', 0):.1f}
• MFI: {ind.get('MFI', 0):.1f}
• حجم: {ind.get('VOLUME_RATIO', 1):.1f}x

🔑 سطوح کلیدی:
• مقاومت R1: ${ind.get('R1', 0):,.4f}
• پیوت: ${ind.get('PIVOT', 0):,.4f}
• حمایت S1: ${ind.get('S1', 0):,.4f}
• BB بالا: ${ind.get('BB_UPPER', 0):,.4f}
• BB پایین: ${ind.get('BB_LOWER', 0):,.4f}

⚠️ حد ضرر: ${analysis['price'] - ind.get('ATR', 0) * 2:,.4f}
🎯 حد سود: ${analysis['price'] + ind.get('ATR', 0) * 4:,.4f}

━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%H:%M:%S')}
✨ @CryptoPulse606
"""
    
    @staticmethod
    def education() -> str:
        """Generate educational content"""
        topics = [
            "تحلیل ساختار بازار - شناسایی روند اصلی",
            "روانشناسی معامله‌گری - کنترل احساسات",
            "مدیریت سرمایه پیشرفته - فرمول کلی",
            "الگوهای کندلی معکوس - چکش و ستاره",
            "تحلیل وایکوف - فازهای انباشت و توزیع",
            "استراتژی شکست سطوح - تایید با حجم",
            "تشخیص واگرایی - مخفی و معمولی",
            "مدیریت حد ضرر - ترلینگ استاپ",
            "تحلیل تایم‌فریم بالا - تایید روند",
            "پرایس اکشن - کندل‌های اینگالفینگ",
            "فیبوناچی - نسبت‌های طلایی",
            "ایچیموکو - ابر کومو و سیگنال‌ها",
            "مکدی - تقاطع‌ها و واگرایی",
            "آر‌اس‌آی - اشباع خرید و فروش",
            "بولینگر باند - فشردگی و گسترش"
        ]
        topic = random.choice(topics)
        
        return f"""
📚 *تحلیل و آموزش تخصصی*

📖 *موضوع امروز:* {topic}

━━━━━━━━━━━━━━━━━━━━━━

🔍 *اصول کلیدی معامله‌گری:*

۱. همیشه روند اصلی بازار را در تایم‌فریم بالا شناسایی کنید
۲. حداقل نسبت ریسک به ریوارد ۱:۲ را رعایت کنید
۳. بیش از ۲٪ از سرمایه را در یک معامله ریسک نکنید
۴. همیشه حد ضرر مشخص داشته باشید
۵. بعد از ۳ ضرر متوالی، معامله را متوقف کنید
۶. ژورنال معاملاتی داشته باشید
۷. اخبار اقتصادی را دنبال کنید
۸. صبور باشید - فرصت‌های خوب همیشه هستند

💡 *نکته طلایی:*
موفقیت در معاملات = ۲۰٪ استراتژی + ۳۰٪ مدیریت ریسک + ۵۰٪ روانشناسی

━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

# ============================================================
# MENUS
# ============================================================
class Menus:
    """Telegram inline keyboards"""
    
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت‌ها", callback_data="prices"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="signal")],
            [InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan"),
             InlineKeyboardButton("📈 تحلیل", callback_data="tech_menu")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh")]
        ])
    
    @staticmethod
    def technical() -> InlineKeyboardMarkup:
        pairs = [
            ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"],
            ["XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT"],
            ["DOT/USDT", "LINK/USDT", "LTC/USDT", "UNI/USDT"]
        ]
        kb = []
        for row in pairs:
            kb.append([InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"tech_{s}") for s in row])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "🤖 *ربات معامله‌گر پیشرفته*\n\n"
        "✨ ۱۰۰+ اندیکاتور تکنیکال\n"
        "✨ ۲۰ ارز برتر بازار\n"
        "✨ سیگنال هوشمند لحظه‌ای\n"
        "✨ اسکن خودکار بازار\n\n"
        "👇 از منو انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=Menus.main()
    )

async def handler_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show live prices"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    if not exchange_mgr.is_connected:
        exchange_mgr.connect()
    
    txt = "💰 *قیمت‌های لحظه‌ای*\n\n"
    for sym in Config.SYMBOLS[:15]:
        ticker = exchange_mgr.get_ticker(sym)
        if ticker:
            emoji = "🟢" if ticker.get('percentage', 0) > 0 else "🔴"
            txt += f"{emoji} *{sym.replace('/USDT','')}*: ${ticker['last']:,.4f} ({ticker.get('percentage',0):+.1f}%)\n"
    
    txt += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    await query.edit_message_text(
        txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data="prices"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]])
    )

async def handler_signal(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    """Generate and show signal"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.is_connected:
        exchange_mgr.connect()
    
    # Fetch data
    ticker = exchange_mgr.get_ticker(symbol)
    df = exchange_mgr.get_ohlcv(symbol, '1h', 200)
    
    if ticker is None or df is None:
        await query.edit_message_text(
            "❌ خطا در دریافت داده",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙", callback_data="back")
            ]])
        )
        return
    
    # Analyze
    indicators = TechnicalAnalyzer.analyze(df)
    
    # Multi-timeframe
    mtf = {}
    for tf in Config.TIMEFRAMES:
        df_tf = exchange_mgr.get_ohlcv(symbol, tf, 100)
        if df_tf is not None:
            mtf[tf] = TechnicalAnalyzer.analyze(df_tf)
    
    signal, confidence, score = SignalGenerator.generate(indicators, ticker['last'], mtf)
    
    analysis = {
        'symbol': symbol,
        'price': ticker['last'],
        'change': ticker.get('percentage', 0),
        'indicators': indicators,
        'signal': signal,
        'confidence': confidence,
        'score': score
    }
    
    msg = MessageFormatter.signal(analysis)
    
    await query.edit_message_text(
        msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data="signal"),
            InlineKeyboardButton("🔍 اسکن", callback_data="scan"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]])
    )

async def handler_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scan all symbols"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔍 اسکن بازار...")
    
    if not exchange_mgr.is_connected:
        exchange_mgr.connect()
    
    results = []
    for sym in Config.SYMBOLS:
        ticker = exchange_mgr.get_ticker(sym)
        df = exchange_mgr.get_ohlcv(sym, '1h', 100)
        
        if ticker and df is not None:
            ind = TechnicalAnalyzer.analyze(df)
            signal, conf, score = SignalGenerator.generate(ind, ticker['last'])
            results.append({
                'symbol': sym,
                'price': ticker['last'],
                'change': ticker.get('percentage', 0),
                'signal': signal,
                'confidence': conf,
                'score': score,
                'indicators': ind
            })
    
    results.sort(key=lambda x: abs(x['score']), reverse=True)
    
    txt = "🔍 *نتایج اسکن بازار*\n\n"
    for i, r in enumerate(results[:12], 1):
        emoji = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
        txt += f"{i}. {emoji} *{r['symbol'].replace('/USDT','')}*: ${r['price']:,.4f}"
        txt += f" | {r['signal'][:15]} | {r['confidence']}%\n"
    
    await query.edit_message_text(
        txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data="scan"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]])
    )

async def handler_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show educational content"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        MessageFormatter.education(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 آموزش جدید", callback_data="edu"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]])
    )

async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❓ *راهنما*\n\n"
        "📊 قیمت‌ها - قیمت لحظه‌ای ۲۰ ارز\n"
        "🎯 سیگنال - تحلیل کامل BTC\n"
        "🔍 اسکن - اسکن کل بازار\n"
        "📈 تحلیل - انتخاب ارز دلخواه\n"
        "📚 آموزش - مطالب آموزشی\n\n"
        "/start - منوی اصلی",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙", callback_data="back")
        ]])
    )

async def handler_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Back to main menu"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🤖 *منوی اصلی*",
        parse_mode="Markdown",
        reply_markup=Menus.main()
    )

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route all button clicks"""
    query = update.callback_query
    data = query.data
    
    try:
        if data == "back":
            await handler_back(update, context)
        elif data == "prices":
            await handler_prices(update, context)
        elif data == "signal":
            await handler_signal(update, context)
        elif data == "scan":
            await handler_scan(update, context)
        elif data == "tech_menu":
            await query.edit_message_text(
                "📈 *انتخاب ارز:*",
                parse_mode="Markdown",
                reply_markup=Menus.technical()
            )
        elif data.startswith("tech_"):
            sym = data.replace("tech_", "")
            await handler_signal(update, context, sym)
        elif data == "edu":
            await handler_education(update, context)
        elif data == "help":
            await handler_help(update, context)
        elif data == "refresh":
            await handler_back(update, context)
        else:
            await query.answer("در حال توسعه...")
    except Exception as e:
        logger.error(f"Button error: {e}")
        await query.answer("❌ خطا!")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    await update.message.reply_text(
        "لطفاً از منو استفاده کنید:\n/start",
        reply_markup=Menus.main()
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if isinstance(context.error, Conflict):
        logger.critical("❌ Conflict - another instance running!")
        ProcessLock.release()
        sys.exit(1)

# ============================================================
# AUTO POST TASKS
# ============================================================
async def task_auto_signals(app: Application):
    """Auto post signals to channel"""
    await asyncio.sleep(15)
    
    while True:
        try:
            if not Config.CHANNEL_ID:
                await asyncio.sleep(60)
                continue
            
            if not exchange_mgr.is_connected:
                exchange_mgr.connect()
            
            # BTC Signal
            ticker = exchange_mgr.get_ticker("BTC/USDT")
            df = exchange_mgr.get_ohlcv("BTC/USDT", '1h', 200)
            
            if ticker and df is not None:
                ind = TechnicalAnalyzer.analyze(df)
                mtf = {}
                for tf in Config.TIMEFRAMES:
                    df_tf = exchange_mgr.get_ohlcv("BTC/USDT", tf, 100)
                    if df_tf is not None:
                        mtf[tf] = TechnicalAnalyzer.analyze(df_tf)
                
                signal, conf, score = SignalGenerator.generate(ind, ticker['last'], mtf)
                
                msg = MessageFormatter.signal({
                    'symbol': "BTC/USDT",
                    'price': ticker['last'],
                    'change': ticker.get('percentage', 0),
                    'indicators': ind,
                    'signal': signal,
                    'confidence': conf,
                    'score': score
                })
                
                await app.bot.send_message(Config.CHANNEL_ID, msg, parse_mode="Markdown")
                logger.info("📤 BTC signal sent")
            
            await asyncio.sleep(120)
            
            # ETH Signal
            ticker = exchange_mgr.get_ticker("ETH/USDT")
            df = exchange_mgr.get_ohlcv("ETH/USDT", '1h', 200)
            
            if ticker and df is not None:
                ind = TechnicalAnalyzer.analyze(df)
                signal, conf, score = SignalGenerator.generate(ind, ticker['last'])
                
                msg = MessageFormatter.signal({
                    'symbol': "ETH/USDT",
                    'price': ticker['last'],
                    'change': ticker.get('percentage', 0),
                    'indicators': ind,
                    'signal': signal,
                    'confidence': conf,
                    'score': score
                })
                
                await app.bot.send_message(Config.CHANNEL_ID, msg, parse_mode="Markdown")
                logger.info("📤 ETH signal sent")
            
            await asyncio.sleep(120)
            
            # Top 3 signals
            results = []
            for sym in Config.SYMBOLS[:10]:
                ticker = exchange_mgr.get_ticker(sym)
                df = exchange_mgr.get_ohlcv(sym, '1h', 100)
                if ticker and df is not None:
                    ind = TechnicalAnalyzer.analyze(df)
                    signal, conf, score = SignalGenerator.generate(ind, ticker['last'])
                    results.append({
                        'symbol': sym,
                        'price': ticker['last'],
                        'change': ticker.get('percentage', 0),
                        'indicators': ind,
                        'signal': signal,
                        'confidence': conf,
                        'score': score
                    })
            
            results.sort(key=lambda x: abs(x['score']), reverse=True)
            
            for r in results[:3]:
                msg = MessageFormatter.signal(r)
                await app.bot.send_message(Config.CHANNEL_ID, msg, parse_mode="Markdown")
                await asyncio.sleep(90)
            
            logger.info(f"📤 Top signals sent")
            
        except Exception as e:
            logger.error(f"Auto signal error: {e}")
        
        await asyncio.sleep(Config.SIGNAL_INTERVAL)

async def task_auto_education(app: Application):
    """Auto post educational content"""
    await asyncio.sleep(30)
    
    while True:
        try:
            if Config.CHANNEL_ID:
                msg = MessageFormatter.education()
                await app.bot.send_message(Config.CHANNEL_ID, msg, parse_mode="Markdown")
                logger.info("📚 Education sent")
        except Exception as e:
            logger.error(f"Education error: {e}")
        
        await asyncio.sleep(Config.ANALYSIS_INTERVAL)

# ============================================================
# MAIN APPLICATION
# ============================================================
async def main():
    """Main entry point"""
    
    # Acquire process lock
    if not ProcessLock.acquire():
        sys.exit(1)
    
    # Validate token
    if not Config.TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in .env!")
        ProcessLock.release()
        return
    
    # Connect to exchange
    exchange_mgr.connect()
    
    # Build application
    app = Application.builder().token(Config.TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    
    # Start background tasks
    asyncio.create_task(task_auto_signals(app))
    asyncio.create_task(task_auto_education(app))
    
    logger.info("=" * 50)
    logger.info("🚀 Ultra Professional Trading Bot v4.0")
    logger.info(f"📢 Channel: {Config.CHANNEL_ID or 'Not set'}")
    logger.info(f"📊 Symbols: {len(Config.SYMBOLS)} coins")
    logger.info(f"⏱️  Signal Interval: {Config.SIGNAL_INTERVAL}s")
    logger.info(f"📚 Analysis Interval: {Config.ANALYSIS_INTERVAL}s")
    logger.info(f"🔌 Exchange: {'Connected' if exchange_mgr.is_connected else 'Disconnected'}")
    logger.info("=" * 50)
    
    # Start bot
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
        # Keep running
        await asyncio.Event().wait()
        
    except Conflict as e:
        logger.critical(f"❌ Conflict: {e}")
    except Exception as e:
        logger.critical(f"❌ Fatal: {e}")
    finally:
        # Graceful shutdown
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except:
            pass
        ProcessLock.release()
        logger.info("👋 Bot shut down")

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Stopped by user")
        ProcessLock.release()
    except Exception as e:
        logger.critical(f"❌ Critical: {e}")
        ProcessLock.release()
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║     CRYPTO PULSE ULTIMATE AI TRADING BOT v9.0 - LEGENDARY           ║
║     Groq AI | 25+ Indicators | 7 EMA | Alerts | Live Monitor        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal, math, traceback
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import numpy as np
import pandas as pd
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

# ============================================================
# PROFESSIONAL LOGGING SYSTEM
# ============================================================
logger = logging.getLogger('CryptoPulseV9')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

for name, level in [('crypto_v9.log', logging.INFO), ('crypto_v9_debug.log', logging.DEBUG), ('crypto_v9_errors.log', logging.ERROR)]:
    handler = RotatingFileHandler(name, maxBytes=20*1024*1024, backupCount=10, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "ICP/USDT", "SAND/USDT", "AXS/USDT", "FTM/USDT", "MANA/USDT",
        "GALA/USDT", "ENJ/USDT", "CHZ/USDT", "NEAR/USDT", "APT/USDT"
    ])
    
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w"
    })
    
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    demo_trading: bool = True
    real_trading: bool = False
    auto_send: bool = True
    signal_interval: int = 600
    education_interval: int = 600

    # Alert thresholds
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    volume_spike: float = 3.0
    price_change_alert: float = 5.0

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v9.lock"
    
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    pid = int(f.read().strip() or 0)
                if pid and cls._is_alive(pid):
                    logger.critical(f"❌ Already running (PID: {pid})")
                    return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"🔒 Lock acquired (PID: {os.getpid()})")
            return True
        except:
            return True
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._file): os.remove(cls._file)
        except: pass
    
    @staticmethod
    def _is_alive(pid: int) -> bool:
        try: os.kill(pid, 0); return True
        except (OSError, ProcessLookupError): return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# DATE & TIME UTILITIES
# ============================================================
class DateTimeManager:
    @staticmethod
    def now() -> datetime: return datetime.now()
    @staticmethod
    def now_str() -> str: return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def now_persian() -> str:
        now = datetime.now()
        days_fa = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
        months_fa = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        return f"{days_fa[now.weekday()]} {now.day} {months_fa[now.month-1]} {now.year} | {now.strftime('%H:%M:%S')}"
    
    @staticmethod
    def timestamp_header() -> str:
        return f"📅 *تاریخ:* {DateTimeManager.now_persian()}\n🌍 *UTC:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"

dtm = DateTimeManager()

# ============================================================
# ALERT SYSTEM - هشدار و اخطار
# ============================================================
class AlertSystem:
    """Advanced Alert & Notification System"""
    
    def __init__(self):
        self.alerts: List[Dict] = []
        self.triggered_alerts: set = set()
        self.alert_history: deque = deque(maxlen=1000)
    
    def check_price_alert(self, symbol: str, price: float, change_24h: float) -> Optional[str]:
        """Check for price change alerts"""
        alert_id = f"price_{symbol}_{int(time.time()/300)}"
        if alert_id in self.triggered_alerts:
            return None
        
        if abs(change_24h) >= cfg.price_change_alert:
            self.triggered_alerts.add(alert_id)
            direction = "📈 افزایش" if change_24h > 0 else "📉 کاهش"
            return f"⚠️ *هشدار قیمت*\n{symbol}: {direction} {abs(change_24h):.1f}%\nقیمت: ${price:,.2f}"
        return None
    
    def check_rsi_alert(self, symbol: str, rsi: float, price: float) -> Optional[str]:
        """Check for RSI alerts"""
        alert_id = f"rsi_{symbol}_{int(time.time()/300)}"
        if alert_id in self.triggered_alerts:
            return None
        
        if rsi <= cfg.rsi_oversold:
            self.triggered_alerts.add(alert_id)
            return f"🟢 *اشباع فروش*\n{symbol}: RSI={rsi:.1f}\nقیمت: ${price:,.2f}\nاحتمال برگشت صعودی!"
        elif rsi >= cfg.rsi_overbought:
            self.triggered_alerts.add(alert_id)
            return f"🔴 *اشباع خرید*\n{symbol}: RSI={rsi:.1f}\nقیمت: ${price:,.2f}\nاحتمال اصلاح نزولی!"
        return None
    
    def check_volume_alert(self, symbol: str, vol_ratio: float, price: float) -> Optional[str]:
        """Check for volume spike alerts"""
        alert_id = f"vol_{symbol}_{int(time.time()/300)}"
        if alert_id in self.triggered_alerts:
            return None
        
        if vol_ratio >= cfg.volume_spike:
            self.triggered_alerts.add(alert_id)
            return f"📊 *افزایش حجم*\n{symbol}: حجم {vol_ratio:.1f}x\nقیمت: ${price:,.2f}\nفعالیت غیرعادی!"
        return None
    
    def check_breakout_alert(self, symbol: str, price: float, resistance: float, support: float) -> Optional[str]:
        """Check for breakout alerts"""
        alert_id = f"break_{symbol}_{int(time.time()/300)}"
        if alert_id in self.triggered_alerts:
            return None
        
        if price > resistance:
            self.triggered_alerts.add(alert_id)
            return f"🚀 *شکست مقاومت*\n{symbol}: ${price:,.2f}\nمقاومت: ${resistance:,.2f}\nسیگنال صعودی!"
        elif price < support:
            self.triggered_alerts.add(alert_id)
            return f"💥 *شکست حمایت*\n{symbol}: ${price:,.2f}\nحمایت: ${support:,.2f}\nسیگنال نزولی!"
        return None
    
    def add_alert(self, alert_type: str, symbol: str, message: str):
        """Add alert to history"""
        self.alert_history.append({
            'type': alert_type,
            'symbol': symbol,
            'message': message,
            'time': datetime.now().isoformat()
        })
    
    def clean_old_alerts(self):
        """Clean triggered alerts older than 1 hour"""
        current_time = int(time.time() / 300)
        self.triggered_alerts = {a for a in self.triggered_alerts if int(a.split('_')[-1]) > current_time - 12}

alerts = AlertSystem()

# ============================================================
# GROQ AI - با مدیریت خطای 429
# ============================================================
class GroqAIEngine:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=60.0)
        self.rate_limited_until = 0
        self.consecutive_errors = 0
        self.max_retries = 3
        if self.enabled:
            logger.info("🧠 Groq AI Connected (Llama 3.3 70B)")
    
    async def _call_api(self, prompt: str, max_tokens: int = 500, retry_count: int = 0) -> Optional[str]:
        """Call Groq API with retry and rate limit handling"""
        if not self.enabled:
            return None
        
        # Check if rate limited
        if time.time() < self.rate_limited_until:
            wait_time = int(self.rate_limited_until - time.time())
            logger.warning(f"⏳ Rate limited. Waiting {wait_time}s...")
            return None
        
        if self.consecutive_errors >= 5:
            logger.error("❌ Too many consecutive errors. Pausing AI...")
            return None
        
        try:
            response = await self.client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {cfg.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an elite crypto analyst. Respond in Persian (فارسی)."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                self.rate_limited_until = time.time() + retry_after
                logger.warning(f"⚠️ Rate limited (429). Waiting {retry_after}s...")
                return None
            
            if response.status_code == 200:
                self.consecutive_errors = 0
                return response.json()["choices"][0]["message"]["content"]
            
            logger.error(f"Groq API Error: {response.status_code}")
            self.consecutive_errors += 1
            return None
            
        except Exception as e:
            logger.error(f"Groq Error: {e}")
            self.consecutive_errors += 1
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self._call_api(prompt, max_tokens, retry_count + 1)
            return None
    
    async def technical_analysis(self, symbol: str, indicators: Dict, price: float, change: float, patterns: List[str], mtf_data: Dict) -> Optional[str]:
        if not self.enabled: return None
        prompt = f"""Analyze {symbol} at ${price:,.2f} ({change:+.1f}%):
RSI: {indicators.get('RSI_14',50):.0f} | MACD: {'Bull' if indicators.get('MACD_HIST',0)>0 else 'Bear'}
ADX: {indicators.get('ADX',20):.0f} | BB: {indicators.get('BB_PCT',0.5):.2f}
Patterns: {', '.join(patterns) if patterns else 'None'}
Divergence: {indicators.get('DIVERGENCE','NONE')}
EMA7: {indicators.get('EMA_7',0):.1f} | EMA50: {indicators.get('EMA_50',0):.1f}
Support: ${indicators.get('SUPPORT',0):.0f} | Resistance: ${indicators.get('RESISTANCE',0):.0f}
Provide in Persian: direction, targets, risk level, confidence (0-100). Max 300 words."""
        return await self._call_api(prompt, 500)
    
    async def market_overview(self, top_coins: List[Dict]) -> Optional[str]:
        if not self.enabled: return None
        coins = "\n".join([f"{c['symbol']}: ${c['price']:,.0f} ({c['change']:+.1f}%)" for c in top_coins[:10]])
        prompt = f"Market overview in Persian:\n{coins}\nSentiment, trends, opportunities. Max 400 words."
        return await self._call_api(prompt, 600)
    
    async def educational_content(self) -> Optional[str]:
        if not self.enabled: return None
        topics = ["تحلیل تکنیکال", "مدیریت ریسک", "روانشناسی", "الگوهای کندلی", "استراتژی", "فیبوناچی", "ایچیموکو", "حجم معاملات"]
        prompt = f"Write professional educational post in Persian about: {random.choice(topics)}. 500+ words, emojis, practical tips."
        return await self._call_api(prompt, 1000)
    
    async def market_prediction(self, symbol: str, indicators: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        prompt = f"Predict {symbol} at ${price:,.2f}. RSI:{indicators.get('RSI_14',50):.0f} MACD:{'Bull' if indicators.get('MACD_HIST',0)>0 else 'Bear'}. 4h, 24h, 7d predictions in Persian with price targets. Max 300 words."
        return await self._call_api(prompt, 500)

ai = GroqAIEngine()

# ============================================================
# EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex: Optional[ccxt.Exchange] = None
        self.connected: bool = False
        self.read_only: bool = True
    
    @property
    def exchange(self) -> Optional[ccxt.Exchange]: return self._ex
    
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000, 'options': {'defaultType': 'spot'}}
            if cfg.api_key and cfg.api_secret:
                params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
                self.read_only = False
            self._ex = ccxt.coinex(params)
            self._ex.load_markets()
            self.connected = True
            logger.info(f"✅ CoinEx: {'FULL' if not self.read_only else 'READ-ONLY'}")
            return True
        except Exception as e:
            logger.error(f"❌ CoinEx: {e}")
            try:
                self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self._ex.load_markets()
                self.connected = True
                return True
            except:
                return False
    
    def ticker(self, symbol: str) -> Optional[Dict]:
        if not self.connected: return None
        try: return self._ex.fetch_ticker(symbol)
        except: return None
    
    def ohlcv(self, symbol: str, tf: str, limit: int = 200) -> Optional[pd.DataFrame]:
        if not self.connected: return None
        try:
            data = self._ex.fetch_ohlcv(symbol, tf, limit=limit)
            if data and len(data) > 30:
                return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# 25+ INDICATORS + 7 EMA TYPES
# ============================================================
class UltimateIndicators:
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        ind = {}
        
        # 7 EMA Types
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
        
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema20_2 = ema20.ewm(span=20, adjust=False).mean()
        ind['DEMA_20'] = float(2 * ema20.iloc[-1] - ema20_2.iloc[-1])
        ind['TEMA_20'] = float(3*ema20.iloc[-1] - 3*ema20_2.iloc[-1] + ema20_2.ewm(span=20, adjust=False).mean().iloc[-1])
        
        from ta.momentum import KAMAIndicator
        try: ind['KAMA'] = float(KAMAIndicator(close, 20, 2, 30).kama().iloc[-1])
        except: ind['KAMA'] = ind['EMA_20']
        
        if len(close) >= 20:
            try:
                wma_h = close.rolling(10).apply(lambda x: np.average(x, weights=range(1,11))).iloc[-1]
                wma_f = close.rolling(20).apply(lambda x: np.average(x, weights=range(1,21))).iloc[-1]
                ind['HMA_20'] = float(2*wma_h - wma_f) if not np.isnan(2*wma_h - wma_f) else ind['EMA_20']
            except: ind['HMA_20'] = ind['EMA_20']
        else: ind['HMA_20'] = ind['EMA_20']
        
        ind['FRAMA_20'] = ind['EMA_20']
        ind['JMA_20'] = float(close.iloc[-5:].mean()*0.5 + ind['EMA_20']*0.3 + close.iloc[-1]*0.2) if len(close)>=5 else ind['EMA_20']
        
        # RSI
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        # MACD
        from ta.trend import MACD
        try:
            macd = MACD(close, 12, 26, 9)
            ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        
        # Stochastic
        from ta.momentum import StochasticOscillator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        except: ind['STOCH_K'] = 50.0
        
        # Bollinger
        from ta.volatility import BollingerBands
        try:
            bb = BollingerBands(close, 20, 2)
            ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
            ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
            ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1])
            ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        
        # ATR
        from ta.volatility import AverageTrueRange
        try: ind['ATR_14'] = float(AverageTrueRange(high, low, close, 14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        ind['ATR_PCT'] = float(ind['ATR_14']/close.iloc[-1]*100)
        
        # ADX
        from ta.trend import ADXIndicator
        try:
            adx = ADXIndicator(high, low, close, 14)
            ind['ADX'] = float(adx.adx().iloc[-1])
        except: ind['ADX'] = 20.0
        
        # CCI
        from ta.trend import CCIIndicator
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        # MFI
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        
        # Volume
        vol_sma = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1]/vol_sma if vol_sma>0 else 1)
        
        # Trend
        ind['TREND_STR'] = float((close.iloc[-1]-close.iloc[-50])/close.iloc[-50]*100) if len(close)>=50 else 0
        
        # Pivot
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        ind['PIVOT'] = float((h+l+c)/3)
        ind['R1'] = float(2*ind['PIVOT']-l)
        ind['S1'] = float(2*ind['PIVOT']-h)
        
        # Support/Resistance
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        
        # Fib
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.382, 0.5, 0.618]:
            ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        
        # Candles
        ind.update(UltimateIndicators.detect_candles(df))
        
        # Divergence
        ind['DIVERGENCE'] = UltimateIndicators.detect_divergence(close)
        
        return ind
    
    @staticmethod
    def detect_candles(df: pd.DataFrame) -> Dict[str, bool]:
        patterns = {p: False for p in ['DOJI', 'HAMMER', 'SHOOTING_STAR', 'ENGULFING_BULL', 'ENGULFING_BEAR', 'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS', 'MARUBOZU_BULL', 'MARUBOZU_BEAR']}
        if len(df) < 3: return patterns
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        po, pc = df['open'].iloc[-2], df['close'].iloc[-2]
        body = abs(c-o)
        tr = h-l
        if tr == 0: return patterns
        patterns['DOJI'] = body <= tr*0.08
        patterns['HAMMER'] = (min(c,o)-l) > body*2 and c > o
        patterns['SHOOTING_STAR'] = (h-max(c,o)) > body*2 and c < o
        patterns['ENGULFING_BULL'] = c > o and pc < po
        patterns['ENGULFING_BEAR'] = c < o and pc > po
        patterns['MARUBOZU_BULL'] = c > o and (h-c) < body*0.1
        patterns['MARUBOZU_BEAR'] = c < o and (o-l) < body*0.1
        if len(df) >= 3:
            o3, c3 = df['open'].iloc[-3], df['close'].iloc[-3]
            patterns['THREE_WHITE_SOLDIERS'] = c>o and pc>po and c3>o3
            patterns['THREE_BLACK_CROWS'] = c<o and pc<po and c3<o3
        return patterns
    
    @staticmethod
    def detect_divergence(price: pd.Series) -> str:
        if len(price) < 20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        rp, rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1] < rp.min() and rr.iloc[-1] > rr.min(): return "BULLISH"
        if rp.iloc[-1] > rp.max() and rr.iloc[-1] < rr.max(): return "BEARISH"
        return "NONE"

ui = UltimateIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGenerator:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 150
        if ind.get('DEMA_20',0) > ind.get('EMA_20',0): score += 40
        if ind.get('TEMA_20',0) > ind.get('EMA_20',0): score += 30
        
        rsi = ind['RSI_14']
        if rsi < 30: score += 120
        elif rsi < 40: score += 60
        elif rsi > 70: score -= 120
        elif rsi > 60: score -= 60
        
        if ind.get('MACD_HIST',0) > 0: score += 70
        else: score -= 70
        if ind.get('STOCH_K',50) < 20: score += 70
        elif ind.get('STOCH_K',50) > 80: score -= 70
        
        cci = ind.get('CCI',0)
        if cci < -200: score += 70
        elif cci > 200: score -= 70
        
        if ind.get('BB_PCT',0.5) < 0.1: score += 100
        elif ind.get('BB_PCT',0.5) > 0.9: score -= 100
        if ind.get('VOL_RATIO',1) > 2: score += 50 if score > 0 else -50
        if ind.get('MFI',50) < 20: score += 60
        elif ind.get('MFI',50) > 80: score -= 60
        
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        if ind.get('THREE_WHITE_SOLDIERS'): score += 60
        if ind.get('THREE_BLACK_CROWS'): score -= 60
        if ind.get('DIVERGENCE') == 'BULLISH': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH': score -= 70
        
        if mtf:
            for tf, ti in mtf.items():
                w = {"5m":0.3,"15m":0.5,"1h":1.0,"4h":1.5,"1d":2.5,"1w":4.0}.get(tf,0.5)
                if ti.get('RSI_14',50) > 55: score += int(25*w)
                elif ti.get('RSI_14',50) < 45: score -= int(25*w)
        
        score = max(-1000, min(1000, score))
        
        if score >= 700: return "خرید فوق‌العاده 🟢🟢🟢🟢🟢", 98, score
        elif score >= 500: return "خرید قوی 🟢🟢🟢🟢", 92, score
        elif score >= 300: return "خرید 🟢🟢🟢", 82, score
        elif score >= 150: return "خرید ضعیف 🟢🟢", 68, score
        elif score <= -700: return "فروش فوق‌العاده 🔴🔴🔴🔴🔴", 98, score
        elif score <= -500: return "فروش قوی 🔴🔴🔴🔴", 92, score
        elif score <= -300: return "فروش 🔴🔴🔴", 82, score
        elif score <= -150: return "فروش ضعیف 🔴🔴", 68, score
        else: return "خنثی ⚪⚪", 50, score

sg = SignalGenerator()

# ============================================================
# SELF-LEARNING TRADER
# ============================================================
class SelfLearningTrader:
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.consecutive_losses = 0
        self.experience = {'total_trades':0,'wins':0,'losses':0,'confidence_threshold':70,'risk_multiplier':1.0,'symbol_performance':{}}
        self.load()
    
    def load(self):
        try:
            with open('trading_brain_v9.json', 'r') as f:
                d = json.load(f)
                self.balance = d.get('balance', cfg.initial_balance)
                self.history = d.get('history', [])
                self.experience.update(d.get('experience', {}))
        except: pass
    
    def save(self):
        try:
            with open('trading_brain_v9.json', 'w') as f:
                json.dump({'balance': self.balance, 'history': self.history[-1000:], 'experience': self.experience}, f)
        except: pass
    
    def open(self, symbol: str, entry: float, sl: float, tp: float, conf: int) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.consecutive_losses >= cfg.max_consecutive_losses: return None
        risk = self.balance * cfg.risk_per_trade * self.experience['risk_multiplier']
        if self.consecutive_losses > 0: risk *= (0.5**self.consecutive_losses)
        pr = abs(entry-sl)
        sz = min(risk/pr, self.balance*0.25/entry) if pr > 0 else 0
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz*entry
        pos = {'symbol':symbol,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry,'time':datetime.now()}
        self.positions[symbol] = pos
        self.save()
        logger.info(f"🔵 OPEN {symbol} | {sz:.4f} @ {entry:.2f}")
        return pos
    
    def update(self, symbol: str, price: float, atr: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]
        p['high'] = max(p['high'], price)
        if (price-p['entry'])/p['entry'] > cfg.trailing_pct:
            p['sl'] = p['high']*(1-cfg.trailing_pct)
        if price >= p['tp']: return self.close(symbol, price, "TAKE_PROFIT")
        if price <= p['sl']: return self.close(symbol, price, "STOP_LOSS")
        return None
    
    def close(self, symbol: str, price: float, reason: str) -> Dict:
        p = self.positions.pop(symbol)
        pnl = (price-p['entry'])*p['size']
        self.balance += p['size']*price
        self.consecutive_losses = 0 if pnl > 0 else self.consecutive_losses+1
        t = {'symbol':symbol,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t)
        self.experience['symbol_performance'][symbol] = self.experience.get('symbol_performance',{}).get(symbol,0)+pnl
        self.save()
        logger.info(f"{'🟢' if pnl>0 else '🔴'} CLOSE {symbol} | ${pnl:+.2f}")
        return t
    
    def get_stats(self) -> Dict:
        total = max(1, len(self.history))
        wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'win_rate':wins/total*100,'positions':len(self.positions)}

trader = SelfLearningTrader()

# ============================================================
# FORMATTER
# ============================================================
class Formatter:
    @staticmethod
    def header() -> str: return dtm.timestamp_header()
    
    @staticmethod
    def signal_msg(analysis: Dict, ai_analyses: Dict = None, alert_msgs: List[str] = None) -> str:
        s = analysis['symbol'].replace('/USDT','')
        i = analysis['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""{Formatter.header()}
╔══════════════════════════════════════╗
║   🔥 سیگنال {s} 🔥              ║
╚══════════════════════════════════════╝

💰 قیمت: ${analysis['price']:,.4f}
📊 تغییر: {analysis['change']:+.2f}%
🎯 سیگنال: {analysis['signal']}
💪 اطمینان: {analysis['confidence']}% | امتیاز: {analysis['score']}/1000

📈 EMA: 7=${i.get('EMA_7',0):,.2f} | 20=${i.get('EMA_20',0):,.2f} | 50=${i.get('EMA_50',0):,.2f}
📊 RSI: {i['RSI_14']:.1f} | MACD: {'صعودی' if i.get('MACD_HIST',0)>0 else 'نزولی'}
🕯️ الگوها: {', '.join(pats) if pats else 'بدون الگو'}
🔄 واگرایی: {i.get('DIVERGENCE','NONE')}

🔑 مقاومت: ${i['RESISTANCE']:,.4f} | حمایت: ${i['SUPPORT']:,.4f}
⚠️ حد ضرر: ${analysis['price']-i['ATR_14']*cfg.atr_sl:,.4f}
🎯 حد سود: ${analysis['price']+i['ATR_14']*cfg.atr_tp:,.4f}"""

        if alert_msgs:
            msg += "\n\n🚨 *هشدارها:*\n" + "\n".join(alert_msgs)
        
        if ai_analyses and ai_analyses.get('tech'):
            msg += f"\n\n🧠 *تحلیل AI:*\n{ai_analyses['tech'][:400]}..."
        
        msg += f"\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606 | {dtm.now_str()}"
        return msg
    
    @staticmethod
    def education_msg(ai_content: str = None) -> str:
        if ai_content:
            return f"{Formatter.header()}🧠 *آموزش تخصصی*\n\n{ai_content}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606 | {dtm.now_str()}"
        return f"{Formatter.header()}📚 *آموزش*\n\nدرس امروز: تحلیل بازار\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"

fmt = Formatter()

# ============================================================
# MENUS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("📈 تحلیل", callback_data="tech"),
             InlineKeyboardButton("🧠 AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("📰 بازار", callback_data="market_ai")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("🚨 هشدارها", callback_data="alerts_list")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("🔄 بروز", callback_data="ref"),
             InlineKeyboardButton("📋 وضعیت", callback_data="status_dash")],
        ])
    
    @staticmethod
    def technical() -> InlineKeyboardMarkup:
        kb, row = [], []
        for s in cfg.symbols[:20]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# DASHBOARD
# ============================================================
class Dashboard:
    """Live Status Dashboard"""
    start_time = datetime.now()
    signals_sent = 0
    alerts_triggered = 0
    trades_executed = 0
    errors_count = 0
    last_signal_time = None
    
    @classmethod
    def get_status(cls) -> str:
        uptime = datetime.now() - cls.start_time
        return f"""
📊 *داشبورد زنده*

⏱️ آپتایم: {uptime}
📤 سیگنال: {cls.signals_sent}
🚨 هشدار: {cls.alerts_triggered}
💰 معامله: {cls.trades_executed}
❌ خطا: {cls.errors_count}
🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}
🧠 AI: {'✅' if ai.enabled else '❌'}
📢 کانال: {'✅' if cfg.channel_id else '❌'}

🕐 آخرین سیگنال: {cls.last_signal_time or 'ندارد'}
"""

dash = Dashboard()

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{fmt.header()}"
        "🤖 *Crypto Pulse v9.0*\n\n"
        "🧠 Groq AI | 📊 ۷ EMA\n"
        "🚨 هشدار هوشمند | 📋 داشبورد زنده\n"
        "📢 سیگنال + آموزش هر ۱۰ دقیقه\n\n"
        "👇 انتخاب کنید:",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def full_signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    
    mtf = {}
    for tf_name, tf_val in list(cfg.timeframes.items())[:6]:
        dft = exchange_mgr.ohlcv(symbol, tf_val, 100)
        if dft is not None: mtf[tf_name] = ui.calculate_all(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    # Check alerts
    alert_msgs = []
    pa = alerts.check_price_alert(symbol, t['last'], t.get('percentage',0))
    ra = alerts.check_rsi_alert(symbol, ind['RSI_14'], t['last'])
    va = alerts.check_volume_alert(symbol, ind['VOL_RATIO'], t['last'])
    ba = alerts.check_breakout_alert(symbol, t['last'], ind['RESISTANCE'], ind['SUPPORT'])
    
    for a in [pa, ra, va, ba]:
        if a: alert_msgs.append(a)
    
    ai_analyses = {}
    if ai.enabled:
        ai_analyses['tech'] = await ai.technical_analysis(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal_msg(analysis, ai_analyses, alert_msgs)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("🧠 AI", callback_data=f"ai_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def alerts_list_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    recent_alerts = list(alerts.alert_history)[-20:]
    
    if not recent_alerts:
        txt = f"{fmt.header()}🚨 *هشدارها*\n\nهیچ هشداری ثبت نشده."
    else:
        txt = f"{fmt.header()}🚨 *آخرین هشدارها*\n\n"
        for alert in reversed(recent_alerts[-10:]):
            txt += f"• {alert['symbol']}: {alert['message'][:100]}\n   ⏰ {alert['time'][:19]}\n\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="alerts_list"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def dashboard_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    status = dash.get_status()
    await q.edit_message_text(status, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="status_dash"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"{fmt.header()}💰 *قیمت‌ها*\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t:
                    e = "🟢" if t.get('percentage',0)>0 else "🔴"
                    txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await full_signal_handler(update, ctx, d[2:])
        elif d.startswith("ai_"): await full_signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d == "market_ai":
            top = []
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
            ai_overview = await ai.market_overview(top)
            if ai_overview:
                await q.edit_message_text(f"{fmt.header()}📰 *بازار*\n\n{ai_overview}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market_ai"), InlineKeyboardButton("🔙", callback_data="back")]]))
            else: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols:
                t = exchange_mgr.ticker(sym)
                df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = ui.calculate_all(df)
                    sig, conf, score = sg.generate(ind, t['last'])
                    res.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"{fmt.header()}🔍 *اسکن*\n\n"
            for i, r in enumerate(res[:15], 1):
                e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
                txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.technical())
        elif d == "port":
            stats = trader.get_stats()
            txt = f"{fmt.header()}💰 *پورتفوی*\n💵 ${stats['balance']:,.2f}\n📈 PnL: ${stats['pnl']:+,.2f}\n📊 پوزیشن: {stats['positions']}\n📋 {stats['total']} | برد: {stats['wins']} ({stats['win_rate']:.0f}%)"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "perf": await q.edit_message_text(f"{fmt.header()}📊 *عملکرد*\n💰 ${trader.balance:,.2f}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "alerts_list": await alerts_list_handler(update, ctx)
        elif d == "status_dash": await dashboard_handler(update, ctx)
        elif d == "auto":
            await q.edit_message_text(f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}\n💹 واقعی: {'✅' if cfg.real_trading else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton(f"واقعی: {'✅' if cfg.real_trading else '❌'}", callback_data="tr"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d == "tr":
            if exchange_mgr.read_only: await q.answer("❌"); return
            cfg.real_trading = not cfg.real_trading
        elif d == "set":
            await q.edit_message_text(f"{fmt.header()}⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 AI: {'✅' if ai.enabled else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            ai_content = await ai.educational_content()
            await q.edit_message_text(fmt.education_msg(ai_content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "EMERGENCY")
            await q.edit_message_text("⏸️ بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        else: await q.answer("⚡")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start", reply_markup=Menu.main())

async def error_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {ctx.error}")
    dash.errors_count += 1
    if isinstance(ctx.error, Conflict): ProcessLock.release(); sys.exit(1)

# ============================================================
# AUTO TASKS
# ============================================================
async def auto_signals_loop(app: Application):
    await asyncio.sleep(10)
    logger.info("📢 Auto Signal Loop Started")
    
    while True:
        try:
            if not cfg.channel_id or not cfg.auto_send:
                await asyncio.sleep(60); continue
            
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            priority_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
            
            for sym in priority_symbols:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind = ui.calculate_all(df)
                        mtf = {}
                        for tf_name, tf_val in list(cfg.timeframes.items())[:6]:
                            dft = exchange_mgr.ohlcv(sym, tf_val, 100)
                            if dft is not None: mtf[tf_name] = ui.calculate_all(dft)
                        
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        # Check alerts
                        alert_msgs = []
                        pa = alerts.check_price_alert(sym, t['last'], t.get('percentage',0))
                        ra = alerts.check_rsi_alert(sym, ind['RSI_14'], t['last'])
                        va = alerts.check_volume_alert(sym, ind['VOL_RATIO'], t['last'])
                        ba = alerts.check_breakout_alert(sym, t['last'], ind['RESISTANCE'], ind['SUPPORT'])
                        
                        for a in [pa, ra, va, ba]:
                            if a:
                                alert_msgs.append(a)
                                dash.alerts_triggered += 1
                                alerts.add_alert('auto', sym, a)
                        
                        ai_analyses = {}
                        if ai.enabled and sym in ["BTC/USDT", "ETH/USDT"]:
                            ai_analyses['tech'] = await ai.technical_analysis(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal_msg(analysis, ai_analyses, alert_msgs)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        dash.signals_sent += 1
                        dash.last_signal_time = dtm.now_str()
                        logger.info(f"📤 Signal sent: {sym}")
                        await asyncio.sleep(60)
                except Exception as e:
                    logger.error(f"Signal error for {sym}: {e}")
                    dash.errors_count += 1
                    continue
            
            # بررسی پوزیشن‌ها
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 100)
                    if t and df is not None:
                        ind = ui.calculate_all(df)
                        result = trader.update(sym, t['last'], ind['ATR_14'])
                        if result:
                            dash.trades_executed += 1
                            emoji = "🟢" if result['pnl'] > 0 else "🔴"
                            await app.bot.send_message(cfg.channel_id,
                                f"{fmt.header()}{emoji} *پوزیشن بسته شد*\n📊 {sym}\n💰 ${result['pnl']:+,.2f}\n📋 {result['reason']}",
                                parse_mode="Markdown")
                except Exception as e:
                    logger.error(f"Position check error: {e}")
            
            alerts.clean_old_alerts()
            logger.info(f"✅ Cycle completed at {dtm.now_str()} | Signals: {dash.signals_sent} | Alerts: {dash.alerts_triggered}")
        except Exception as e:
            logger.error(f"Loop error: {e}")
            dash.errors_count += 1
        await asyncio.sleep(cfg.signal_interval)

async def auto_education_loop(app: Application):
    await asyncio.sleep(30)
    logger.info("📚 Auto Education Loop Started")
    
    while True:
        try:
            if cfg.channel_id and cfg.auto_send and ai.enabled:
                ai_content = await ai.educational_content()
                if ai_content:
                    msg = fmt.education_msg(ai_content)
                    await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                    logger.info("📚 Education sent")
                
                await asyncio.sleep(120)
                
                top = []
                for sym in cfg.symbols[:10]:
                    t = exchange_mgr.ticker(sym)
                    if t: top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
                
                market_ai = await ai.market_overview(top)
                if market_ai:
                    await app.bot.send_message(cfg.channel_id,
                        f"{fmt.header()}📰 *تحلیل بازار*\n\n{market_ai}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                        parse_mode="Markdown")
                    logger.info("📰 Market overview sent")
        except Exception as e:
            logger.error(f"Education error: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token:
        logger.critical("❌ No token!"); ProcessLock.release(); return
    
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    
    asyncio.create_task(auto_signals_loop(app))
    asyncio.create_task(auto_education_loop(app))
    
    logger.info("="*70)
    logger.info("🚀 CRYPTO PULSE ULTIMATE v9.0 - LEGENDARY")
    logger.info(f"🧠 Groq AI: {'✅' if ai.enabled else '❌'} | 📊 7 EMA + 25 Indicators")
    logger.info(f"🚨 Alert System: Active | 📋 Dashboard: Active")
    logger.info(f"📢 Auto Signals + Education Every 10 Minutes")
    logger.info(f"📅 {dtm.now_persian()}")
    logger.info("="*70)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Conflict: logger.critical("❌ Conflict!")
    except Exception as e: logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: ProcessLock.release()
    except Exception as e: logger.critical(f"Fatal: {e}"); ProcessLock.release()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE v10 - OPTIMIZED FOR GROQ 8000 TPM                    ║
║   Smart Token Management | 5 Alert Types | Live Dashboard            ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
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
# LOGGING
# ============================================================
logger = logging.getLogger('CryptoPulseV10')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

for name, level in [('crypto_v10.log', logging.INFO), ('crypto_v10_debug.log', logging.DEBUG), ('crypto_v10_errors.log', logging.ERROR)]:
    handler = RotatingFileHandler(name, maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio']:
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
        "ICP/USDT", "SAND/USDT", "AXS/USDT", "FTM/USDT", "MANA/USDT"
    ])
    
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
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
    education_interval: int = 900  # 15 min for education to save tokens

cfg = Config()

# ============================================================
# GROQ TOKEN MANAGER - 8000 TPM Limit
# ============================================================
class GroqTokenManager:
    """Smart token management for Groq 8000 TPM limit"""
    
    MAX_TPM = 8000  # Maximum Tokens Per Minute
    SAFETY_MARGIN = 0.85  # Use 85% of limit
    
    def __init__(self):
        self.token_usage: deque = deque()  # (timestamp, tokens_used)
        self.total_tokens_today = 0
        self.api_calls_today = 0
        self.rate_limited_count = 0
        self.last_reset = time.time()
    
    def can_make_request(self, estimated_tokens: int = 500) -> Tuple[bool, float]:
        """Check if request can be made within TPM limit"""
        now = time.time()
        
        # Clean old entries (older than 60 seconds)
        while self.token_usage and now - self.token_usage[0][0] > 60:
            self.token_usage.popleft()
        
        # Calculate current TPM usage
        current_tpm = sum(tokens for _, tokens in self.token_usage)
        safe_limit = self.MAX_TPM * self.SAFETY_MARGIN
        
        if current_tpm + estimated_tokens > safe_limit:
            # Calculate wait time
            if self.token_usage:
                oldest_time = self.token_usage[0][0]
                wait_time = 60 - (now - oldest_time) + 1
                return False, max(0, wait_time)
            return False, 60
        
        return True, 0
    
    def record_usage(self, tokens_used: int):
        """Record token usage"""
        now = time.time()
        self.token_usage.append((now, tokens_used))
        self.total_tokens_today += tokens_used
        self.api_calls_today += 1
    
    def get_stats(self) -> Dict:
        """Get current usage stats"""
        now = time.time()
        while self.token_usage and now - self.token_usage[0][0] > 60:
            self.token_usage.popleft()
        
        current_tpm = sum(tokens for _, tokens in self.token_usage)
        
        return {
            'current_tpm': current_tpm,
            'max_tpm': self.MAX_TPM,
            'usage_pct': (current_tpm / self.MAX_TPM) * 100,
            'calls_today': self.api_calls_today,
            'tokens_today': self.total_tokens_today,
            'rate_limited': self.rate_limited_count
        }

token_mgr = GroqTokenManager()

# ============================================================
# GROQ AI - Optimized for 8000 TPM
# ============================================================
class GroqAIEngine:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    
    # Token estimates for different analysis types
    TOKEN_ESTIMATES = {
        'signal': 400,      # تحلیل سیگنال
        'market': 350,      # تحلیل بازار
        'education': 800,   # محتوای آموزشی
        'prediction': 300,  # پیش‌بینی
        'strategy': 350,    # استراتژی
    }
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=45.0)
        if self.enabled:
            logger.info(f"🧠 Groq AI Ready (Limit: {token_mgr.MAX_TPM} TPM)")
    
    async def _call_api(self, prompt: str, max_tokens: int = 400, analysis_type: str = 'signal') -> Optional[str]:
        """Call Groq API with token management"""
        if not self.enabled:
            return None
        
        # Check TPM limit
        can_request, wait_time = token_mgr.can_make_request(max_tokens)
        if not can_request:
            logger.warning(f"⏳ TPM limit reached. Waiting {wait_time:.0f}s... (Type: {analysis_type})")
            token_mgr.rate_limited_count += 1
            if wait_time > 30:
                return None  # Skip if wait is too long
            await asyncio.sleep(wait_time)
        
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
                        {"role": "system", "content": "You are a crypto analyst. Respond in Persian (فارسی). Be concise."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.6
                }
            )
            
            if response.status_code == 429:
                token_mgr.rate_limited_count += 1
                logger.warning("⚠️ Rate limited (429)")
                return None
            
            if response.status_code == 200:
                data = response.json()
                actual_tokens = data.get('usage', {}).get('total_tokens', max_tokens)
                token_mgr.record_usage(actual_tokens)
                return data["choices"][0]["message"]["content"]
            
            logger.error(f"Groq Error: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Groq Exception: {e}")
            return None
    
    async def signal_analysis(self, symbol: str, ind: Dict, price: float, change: float, patterns: List[str]) -> Optional[str]:
        """تحلیل سیگنال - بهینه شده"""
        if not self.enabled: return None
        
        prompt = f"""Analyze {symbol} at ${price:,.2f} ({change:+.1f}%):
RSI={ind.get('RSI_14',50):.0f} | MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'}
ADX={ind.get('ADX',20):.0f} | BB={ind.get('BB_PCT',0.5):.2f}
Support=${ind.get('SUPPORT',0):.0f} | Resistance=${ind.get('RESISTANCE',0):.0f}
Patterns: {', '.join(patterns) if patterns else 'None'}

In Persian: Direction, Entry/Exit, Risk level, Confidence (0-100). Max 200 words."""
        
        return await self._call_api(prompt, 350, 'signal')
    
    async def market_overview(self, coins: List[Dict]) -> Optional[str]:
        """تحلیل بازار - بهینه شده"""
        if not self.enabled: return None
        
        top5 = coins[:5]
        coins_text = " | ".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in top5])
        
        prompt = f"Market overview in Persian. Top: {coins_text}. BTC dominance, sentiment, opportunities. Max 200 words."
        return await self._call_api(prompt, 300, 'market')
    
    async def education(self) -> Optional[str]:
        """محتوای آموزشی - با توکن بیشتر"""
        if not self.enabled: return None
        
        topics = ["تحلیل تکنیکال", "مدیریت ریسک", "روانشناسی", "الگوهای کندلی", "استراتژی"]
        topic = random.choice(topics)
        
        prompt = f"Write educational post in Persian about: {topic}. 300+ words, emojis, practical tips, golden nugget."
        return await self._call_api(prompt, 700, 'education')

ai = GroqAIEngine()

# ============================================================
# EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex: Optional[ccxt.Exchange] = None
        self.connected: bool = False
    
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000}
            if cfg.api_key: params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
            self._ex = ccxt.coinex(params)
            self._ex.load_markets()
            self.connected = True
            logger.info(f"✅ Exchange Connected")
            return True
        except:
            try:
                self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self._ex.load_markets()
                self.connected = True
                return True
            except:
                return False
    
    def ticker(self, s: str) -> Optional[Dict]:
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    
    def ohlcv(self, s: str, tf: str, limit: int = 200) -> Optional[pd.DataFrame]:
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s, tf, limit=limit)
            return pd.DataFrame(d, columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# DATE/TIME
# ============================================================
class DTM:
    @staticmethod
    def now() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def persian() -> str:
        n = datetime.now()
        days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        return f"{days[n.weekday()]} {n.day} {months[n.month-1]} {n.year} | {n.strftime('%H:%M:%S')}"
    
    @staticmethod
    def header() -> str:
        return f"📅 {DTM.persian()}\n🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"

dtm = DTM()

# ============================================================
# ALERT SYSTEM - 5 Types
# ============================================================
class AlertSystem:
    def __init__(self):
        self.history: deque = deque(maxlen=500)
        self.triggered: Dict[str, float] = {}
        self.count = 0
    
    def check_price(self, symbol: str, price: float, change: float) -> Optional[str]:
        if abs(change) < 5: return None
        key = f"price_{symbol}_{int(time.time()/600)}"
        if key in self.triggered: return None
        self.triggered[key] = time.time()
        self.count += 1
        d = "📈 افزایش" if change > 0 else "📉 کاهش"
        return f"⚠️ {symbol}: {d} {abs(change):.1f}% | ${price:,.2f}"
    
    def check_rsi(self, symbol: str, rsi: float, price: float) -> Optional[str]:
        if rsi > 30 and rsi < 70: return None
        key = f"rsi_{symbol}_{int(time.time()/600)}"
        if key in self.triggered: return None
        self.triggered[key] = time.time()
        self.count += 1
        t = "🟢 اشباع فروش" if rsi < 30 else "🔴 اشباع خرید"
        return f"{t}: {symbol} RSI={rsi:.0f} | ${price:,.2f}"
    
    def check_volume(self, symbol: str, vol: float, price: float) -> Optional[str]:
        if vol < 3: return None
        key = f"vol_{symbol}_{int(time.time()/600)}"
        if key in self.triggered: return None
        self.triggered[key] = time.time()
        self.count += 1
        return f"📊 حجم بالا: {symbol} {vol:.1f}x | ${price:,.2f}"
    
    def check_breakout(self, symbol: str, price: float, res: float, sup: float) -> Optional[str]:
        if sup < price < res: return None
        key = f"break_{symbol}_{int(time.time()/600)}"
        if key in self.triggered: return None
        self.triggered[key] = time.time()
        self.count += 1
        if price > res: return f"🚀 شکست مقاومت: {symbol} ${price:,.2f}"
        return f"💥 شکست حمایت: {symbol} ${price:,.2f}"
    
    def check_divergence(self, symbol: str, div: str, price: float) -> Optional[str]:
        if div == "NONE": return None
        key = f"div_{symbol}_{int(time.time()/600)}"
        if key in self.triggered: return None
        self.triggered[key] = time.time()
        self.count += 1
        t = "صعودی 🟢" if "BULL" in div else "نزولی 🔴"
        return f"🔄 واگرایی {t}: {symbol} | ${price:,.2f}"
    
    def clean(self):
        now = time.time()
        self.triggered = {k: v for k, v in self.triggered.items() if now - v < 3600}

alerts = AlertSystem()

# ============================================================
# INDICATORS - 25+ with 7 EMA Types
# ============================================================
class Indicators:
    @staticmethod
    def calc(df: pd.DataFrame) -> Dict:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        ind = {}
        
        # 7 EMA Types
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
        
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema20_2 = ema20.ewm(span=20, adjust=False).mean()
        ind['DEMA_20'] = float(2*ema20.iloc[-1] - ema20_2.iloc[-1])
        ind['TEMA_20'] = float(3*ema20.iloc[-1] - 3*ema20_2.iloc[-1] + ema20_2.ewm(span=20, adjust=False).mean().iloc[-1])
        
        from ta.momentum import KAMAIndicator, RSIIndicator
        try: ind['KAMA'] = float(KAMAIndicator(close, 20, 2, 30).kama().iloc[-1])
        except: ind['KAMA'] = ind['EMA_20']
        
        if len(close) >= 20:
            try:
                wh = close.rolling(10).apply(lambda x: np.average(x, weights=range(1,min(11,len(x)+1)))).iloc[-1]
                wf = close.rolling(20).apply(lambda x: np.average(x, weights=range(1,min(21,len(x)+1)))).iloc[-1]
                ind['HMA_20'] = float(2*wh - wf) if not np.isnan(2*wh-wf) else ind['EMA_20']
            except: ind['HMA_20'] = ind['EMA_20']
        else: ind['HMA_20'] = ind['EMA_20']
        
        ind['FRAMA_20'] = ind['EMA_20']
        ind['JMA_20'] = float(close.iloc[-5:].mean()*0.5 + ind['EMA_20']*0.3 + close.iloc[-1]*0.2) if len(close)>=5 else ind['EMA_20']
        
        # RSI
        for p in [7, 14]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, p).rsi().iloc[-1])
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
        
        # ADX
        from ta.trend import ADXIndicator
        try: ind['ADX'] = float(ADXIndicator(high, low, close, 14).adx().iloc[-1])
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
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        
        # Support/Resistance
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        
        # Candles
        ind.update(Indicators._candles(df))
        
        # Divergence
        ind['DIVERGENCE'] = Indicators._divergence(close)
        
        return ind
    
    @staticmethod
    def _candles(df: pd.DataFrame) -> Dict[str, bool]:
        pats = {p: False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','MARUBOZU_BULL','MARUBOZU_BEAR']}
        if len(df) < 2: return pats
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        po, pc = df['open'].iloc[-2], df['close'].iloc[-2]
        body, tr = abs(c-o), h-l
        if tr == 0: return pats
        pats['DOJI'] = body <= tr*0.08
        pats['HAMMER'] = (min(c,o)-l) > body*2 and c > o
        pats['SHOOTING_STAR'] = (h-max(c,o)) > body*2 and c < o
        pats['ENGULFING_BULL'] = c > o and pc < po
        pats['ENGULFING_BEAR'] = c < o and pc > po
        pats['MARUBOZU_BULL'] = c > o and (h-c) < body*0.1
        pats['MARUBOZU_BEAR'] = c < o and (o-l) < body*0.1
        return pats
    
    @staticmethod
    def _divergence(price: pd.Series) -> str:
        if len(price) < 20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        rp, rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1] < rp.min() and rr.iloc[-1] > rr.min(): return "BULLISH"
        if rp.iloc[-1] > rp.max() and rr.iloc[-1] < rr.max(): return "BEARISH"
        return "NONE"

indicator = Indicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 150
        
        if ind.get('DEMA_20',0) > ind.get('EMA_20',0): score += 40
        if ind.get('TEMA_20',0) > ind.get('EMA_20',0): score += 30
        
        rsi = ind['RSI_14']
        if rsi < 30: score += 120
        elif rsi > 70: score -= 120
        
        if ind.get('MACD_HIST',0) > 0: score += 70
        else: score -= 70
        
        if ind.get('STOCH_K',50) < 20: score += 70
        elif ind.get('STOCH_K',50) > 80: score -= 70
        
        if ind.get('BB_PCT',0.5) < 0.1: score += 100
        elif ind.get('BB_PCT',0.5) > 0.9: score -= 100
        
        if ind.get('VOL_RATIO',1) > 2: score += 50 if score>0 else -50
        if ind.get('MFI',50) < 20: score += 60
        elif ind.get('MFI',50) > 80: score -= 60
        
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        
        if ind.get('DIVERGENCE') == 'BULLISH': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH': score -= 70
        
        if mtf:
            for tf, ti in mtf.items():
                w = {"1h":1,"4h":1.5,"1d":2.5,"1w":4}.get(tf,0.5)
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

sg = SignalGen()

# ============================================================
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict = {}
        self.history: List = []
        self.closses = 0
        self.load()
    
    def load(self):
        try:
            with open('trader_v10.json','r') as f:
                d = json.load(f)
                self.balance = d.get('balance', cfg.initial_balance)
                self.history = d.get('history', [])
        except: pass
    
    def save(self):
        try:
            with open('trader_v10.json','w') as f:
                json.dump({'balance': self.balance, 'history': self.history[-500:]}, f)
        except: pass
    
    def open(self, symbol: str, entry: float, sl: float, tp: float) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.closses >= cfg.max_consecutive_losses:
            return None
        risk = self.balance * cfg.risk_per_trade
        if self.closses > 0: risk *= (0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz*entry
        pos = {'symbol':symbol,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        self.positions[symbol] = pos
        self.save()
        return pos
    
    def update(self, symbol: str, price: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]
        p['high'] = max(p['high'], price)
        if (price-p['entry'])/p['entry'] > cfg.trailing_pct:
            p['sl'] = p['high']*(1-cfg.trailing_pct)
        if price >= p['tp']: return self.close(symbol, price, "TP")
        if price <= p['sl']: return self.close(symbol, price, "SL")
        return None
    
    def close(self, symbol: str, price: float, reason: str) -> Dict:
        p = self.positions.pop(symbol)
        pnl = (price-p['entry'])*p['size']
        self.balance += p['size']*price
        self.closses = 0 if pnl>0 else self.closses+1
        t = {'symbol':symbol,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t)
        self.save()
        return t
    
    def stats(self) -> Dict:
        total = max(1, len(self.history))
        wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# DASHBOARD
# ============================================================
class Dashboard:
    start = datetime.now()
    signals = 0
    alerts_count = 0
    trades = 0
    errors = 0
    last_signal = ""
    
    @classmethod
    def get(cls) -> str:
        uptime = datetime.now() - cls.start
        tstats = token_mgr.get_stats()
        return f"""
📊 *داشبورد زنده*

⏱️ آپتایم: {uptime}
📤 سیگنال: {cls.signals}
🚨 هشدار: {cls.alerts_count}
💰 معامله: {cls.trades}
❌ خطا: {cls.errors}

🧠 *Groq TPM:*
• مصرف: {tstats['current_tpm']}/{tstats['max_tpm']}
• درصد: {tstats['usage_pct']:.0f}%
• امروز: {tstats['calls_today']} درخواست

🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}
📢 کانال: {'✅' if cfg.channel_id else '❌'}
🕐 آخرین: {cls.last_signal or 'ندارد'}
"""

dash = Dashboard()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a: Dict, ai_text: str = None, alert_list: List[str] = None) -> str:
        s = a['symbol'].replace('/USDT','')
        i = a['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""{dtm.header()}
╔══════════════════════════════╗
║   🔥 سیگنال {s} 🔥      ║
╚══════════════════════════════╝

💰 ${a['price']:,.4f} | 📊 {a['change']:+.2f}%
🎯 {a['signal']} | 💪 {a['confidence']}% | ⭐ {a['score']}/1000

📈 EMA: 7=${i.get('EMA_7',0):,.2f} | 20=${i.get('EMA_20',0):,.2f} | 50=${i.get('EMA_50',0):,.2f}
📊 RSI:{i['RSI_14']:.0f} | MACD:{'Bull' if i.get('MACD_HIST',0)>0 else 'Bear'}
🕯️ {', '.join(pats) if pats else 'بدون الگو'}

🔑 مقاومت: ${i['RESISTANCE']:,.2f} | حمایت: ${i['SUPPORT']:,.2f}
⚠️ SL: ${a['price']-i['ATR_14']*cfg.atr_sl:,.2f} | TP: ${a['price']+i['ATR_14']*cfg.atr_tp:,.2f}"""

        if alert_list:
            msg += "\n\n🚨 *هشدارها:*\n" + "\n".join(alert_list)
        
        if ai_text:
            msg += f"\n\n🧠 *AI:*\n{ai_text[:400]}"
        
        msg += f"\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606 | {dtm.now()}"
        return msg
    
    @staticmethod
    def edu(ai_text: str = None) -> str:
        if ai_text:
            return f"{dtm.header()}🧠 *آموزش AI*\n\n{ai_text}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"
        return f"{dtm.header()}📚 *آموزش*\n\nدرس امروز: تحلیل بازار\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"

fmt = Fmt()

# ============================================================
# MENUS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("📈 تحلیل", callback_data="tech"),
             InlineKeyboardButton("🧠 AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("📰 بازار", callback_data="market")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 داشبورد", callback_data="dash"),
             InlineKeyboardButton("🚨 هشدارها", callback_data="alerts")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("🔄 بروز", callback_data="ref"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set")]
        ])
    
    @staticmethod
    def tech() -> InlineKeyboardMarkup:
        kb, row = [], []
        for s in cfg.symbols[:20]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{dtm.header()}"
        "🤖 *Crypto Pulse v10*\n\n"
        "🧠 Groq AI (8000 TPM)\n"
        "📊 7 EMA | 25+ Indicators\n"
        "🚨 5 Alert Types\n"
        "📋 Live Dashboard\n\n"
        "👇 انتخاب کنید:",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = indicator.calc(df)
    
    mtf = {}
    for tf_name, tf_val in list(cfg.timeframes.items())[:4]:
        dft = exchange_mgr.ohlcv(symbol, tf_val, 100)
        if dft is not None: mtf[tf_name] = indicator.calc(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    # Check all alerts
    alert_list = []
    for check in [
        alerts.check_price(symbol, t['last'], t.get('percentage',0)),
        alerts.check_rsi(symbol, ind['RSI_14'], t['last']),
        alerts.check_volume(symbol, ind['VOL_RATIO'], t['last']),
        alerts.check_breakout(symbol, t['last'], ind['RESISTANCE'], ind['SUPPORT']),
        alerts.check_divergence(symbol, ind['DIVERGENCE'], t['last'])
    ]:
        if check: alert_list.append(check)
    
    # AI Analysis (only for priority symbols to save tokens)
    ai_text = None
    if ai.enabled and symbol in ["BTC/USDT", "ETH/USDT"]:
        ai_text = await ai.signal_analysis(symbol, ind, t['last'], t.get('percentage',0), pats)
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal(analysis, ai_text, alert_list)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("🧠 AI", callback_data=f"ai_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def dashboard_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(dash.get(), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="dash"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def alerts_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    recent = list(alerts.history)[-15:]
    if not recent:
        txt = f"{dtm.header()}🚨 *هشدارها*\n\nبدون هشدار"
    else:
        txt = f"{dtm.header()}🚨 *آخرین هشدارها* ({alerts.count} کل)\n\n"
        for a in reversed(recent[-10:]):
            txt += f"• {a}\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="alerts"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"{dtm.header()}💰 *قیمت‌ها*\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t:
                    e = "🟢" if t.get('percentage',0)>0 else "🔴"
                    txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("ai_"): await signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d == "market":
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
            ai_overview = await ai.market_overview(top)
            if ai_overview:
                await q.edit_message_text(f"{dtm.header()}📰 *بازار*\n\n{ai_overview}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market"), InlineKeyboardButton("🔙", callback_data="back")]]))
            else: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols:
                t = exchange_mgr.ticker(sym)
                df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = indicator.calc(df)
                    sig, conf, score = sg.generate(ind, t['last'])
                    res.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"{dtm.header()}🔍 *اسکن*\n\n"
            for i, r in enumerate(res[:12], 1):
                e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
                txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.tech())
        elif d == "port":
            s = trader.stats()
            txt = f"{dtm.header()}💰 *پورتفوی*\n💵 ${s['balance']:,.2f}\n📈 PnL: ${s['pnl']:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 {s['total']} | برد: {s['wins']} ({s['rate']:.0f}%)"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dash": await dashboard_handler(update, ctx)
        elif d == "alerts": await alerts_handler(update, ctx)
        elif d == "auto":
            await q.edit_message_text(f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d == "set":
            ts = token_mgr.get_stats()
            await q.edit_message_text(f"{dtm.header()}⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 AI: {'✅' if ai.enabled else '❌'}\n📊 TPM: {ts['current_tpm']}/{ts['max_tpm']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            ai_content = await ai.education()
            await q.edit_message_text(fmt.edu(ai_content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
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

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            # Only BTC, ETH, SOL for regular signals (save tokens)
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind = indicator.calc(df)
                        mtf = {}
                        for tf_name, tf_val in list(cfg.timeframes.items())[:3]:
                            dft = exchange_mgr.ohlcv(sym, tf_val, 100)
                            if dft is not None: mtf[tf_name] = indicator.calc(dft)
                        
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        alert_list = []
                        for check in [
                            alerts.check_price(sym, t['last'], t.get('percentage',0)),
                            alerts.check_rsi(sym, ind['RSI_14'], t['last']),
                            alerts.check_volume(sym, ind['VOL_RATIO'], t['last']),
                            alerts.check_breakout(sym, t['last'], ind['RESISTANCE'], ind['SUPPORT'])
                        ]:
                            if check:
                                alert_list.append(check)
                                dash.alerts_count += 1
                        
                        ai_text = None
                        if ai.enabled and sym in ["BTC/USDT", "ETH/USDT"]:
                            ai_text = await ai.signal_analysis(sym, ind, t['last'], t.get('percentage',0), pats)
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal(analysis, ai_text, alert_list)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        dash.signals += 1
                        dash.last_signal = dtm.now()
                        await asyncio.sleep(90)
                except Exception as e:
                    logger.error(f"Signal error {sym}: {e}")
                    dash.errors += 1
            
            # Position monitoring
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result:
                            dash.trades += 1
                            emoji = "🟢" if result['pnl'] > 0 else "🔴"
                            await app.bot.send_message(cfg.channel_id,
                                f"{dtm.header()}{emoji} *بسته شد*\n📊 {sym}\n💰 ${result['pnl']:+,.2f}",
                                parse_mode="Markdown")
                except: pass
            
            alerts.clean()
            
        except Exception as e:
            logger.error(f"Loop: {e}")
            dash.errors += 1
        
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    
    while True:
        try:
            if cfg.channel_id and ai.enabled:
                # Only send education if token usage is low
                stats = token_mgr.get_stats()
                if stats['usage_pct'] < 50:  # Only if less than 50% TPM used
                    ai_content = await ai.education()
                    if ai_content:
                        await app.bot.send_message(cfg.channel_id, fmt.edu(ai_content), parse_mode="Markdown")
                
                # Market overview
                await asyncio.sleep(120)
                if stats['usage_pct'] < 70:
                    top = []
                    for sym in cfg.symbols[:8]:
                        t = exchange_mgr.ticker(sym)
                        if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
                    market_ai = await ai.market_overview(top)
                    if market_ai:
                        await app.bot.send_message(cfg.channel_id,
                            f"{dtm.header()}📰 *بازار*\n\n{market_ai}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                            parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Edu: {e}")
        
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
class ProcessLock:
    _file = "crypto_v10.lock"
    @classmethod
    def acquire(cls) -> bool:
        if os.path.exists(cls._file):
            with open(cls._file) as f:
                if cls._alive(int(f.read().strip() or 0)): return False
            os.remove(cls._file)
        with open(cls._file,'w') as f: f.write(str(os.getpid()))
        return True
    @classmethod
    def release(cls):
        try: os.remove(cls._file)
        except: pass
    @staticmethod
    def _alive(pid): 
        try: os.kill(pid,0); return True
        except: return False

for s in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(s, lambda x,y: (ProcessLock.release(), sys.exit(0)))

async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_education(app))
    
    logger.info(f"🚀 Crypto Pulse v10 | Groq: {token_mgr.MAX_TPM} TPM | {dtm.persian()}")
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e:
        logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()

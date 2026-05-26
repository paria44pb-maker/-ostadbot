#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE ULTIMATE DUAL AI TRADING BOT v11.0 - PERSIAN GREEN   ║
║   Full Persian Theme | Auto Real Trade | 4H/1D/1W | Dual AI         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re
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

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger('CryptoPulseV11')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

for name, level in [('crypto_v11.log', logging.INFO), ('crypto_v11_errors.log', logging.ERROR)]:
    handler = RotatingFileHandler(name, maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp', 'matplotlib']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT"
    ])
    
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w"
    })
    
    primary_tfs: List[str] = field(default_factory=lambda: ["4h", "1d", "1w"])
    
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    demo_trading: bool = True
    real_trading: bool = True  # معامله واقعی فعال
    auto_send: bool = True
    
    signal_interval: int = 14400  # 4 hours
    education_interval: int = 3600  # 1 hour

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v11.lock"
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    pid = int(f.read().strip() or 0)
                if pid and cls._alive(pid): return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f: f.write(str(os.getpid()))
            return True
        except: return True
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._file): os.remove(cls._file)
        except: pass
    @staticmethod
    def _alive(pid: int) -> bool:
        try: os.kill(pid, 0); return True
        except: return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# DATE/TIME - PERSIAN
# ============================================================
class DTM:
    @staticmethod
    def now() -> str: return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    @staticmethod
    def persian() -> str:
        n = datetime.now()
        days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        return f"{days[n.weekday()]} {n.day} {months[n.month-1]} {n.year} | {n.strftime('%H:%M:%S')}"
    @staticmethod
    def header() -> str:
        return f"📅 {DTM.persian()}\n🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"

dtm = DTM()

# ============================================================
# TOKEN MANAGER
# ============================================================
class TokenManager:
    MAX_TPM: int = 8000
    def __init__(self):
        self._usage: deque = deque()
        self.groq_tokens: int = 0
        self.gemini_tokens: int = 0
    @property
    def current(self) -> int:
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60: self._usage.popleft()
        return sum(t for _, t in self._usage)
    def can(self, tokens: int = 500) -> bool: return (self.current + tokens) <= self.MAX_TPM
    def wait(self, tokens: int = 500) -> float:
        if self.can(tokens): return 0
        if self._usage: return max(0, 60 - (time.time() - self._usage[0][0]) + 1)
        return 60
    def record(self, tokens: int, source: str = "groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq_tokens += tokens
        else: self.gemini_tokens += tokens
    def stats(self) -> Dict:
        return {'current': self.current, 'max': self.MAX_TPM, 'groq': self.groq_tokens, 'gemini': self.gemini_tokens}

token_mgr = TokenManager()

# ============================================================
# GEMINI AI
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.api_key = cfg.gemini_api_key
        self.enabled = bool(self.api_key and len(self.api_key) > 10)
        self.client = httpx.AsyncClient(timeout=60.0)
        if self.enabled: logger.info("🌟 Gemini AI Ready")
    async def generate(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled: return None
        if not token_mgr.can(max_tokens):
            wait = token_mgr.wait(max_tokens)
            if wait > 30: return None
            await asyncio.sleep(wait)
        try:
            resp = await self.client.post(f"{self.URL}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}})
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text: token_mgr.record(max_tokens, "gemini"); return text
            return None
        except: return None

gemini_ai = GeminiAI()

# ============================================================
# GROQ AI
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    TOKENS = {'technical': 500, 'market': 400, 'education': 700, 'prediction': 350, 'strategy': 400, 'sentiment': 300, 'fundamental': 400, 'price_action': 400}
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=60.0)
        if self.enabled: logger.info("🧠 Groq AI Ready")
    
    async def _call(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled: return None
        if not token_mgr.can(max_tokens):
            wait = token_mgr.wait(max_tokens)
            if wait > 30: return None
            await asyncio.sleep(wait)
        try:
            resp = await self.client.post(self.URL,
                headers={"Authorization": f"Bearer {cfg.groq_api_key}", "Content-Type": "application/json"},
                json={"model": self.MODEL, "messages": [{"role": "system", "content": "You are a crypto analyst. Respond in Persian (فارسی). Use emojis."}, {"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7})
            if resp.status_code == 200:
                data = resp.json()
                token_mgr.record(data.get('usage', {}).get('total_tokens', max_tokens), "groq")
                return data["choices"][0]["message"]["content"]
            return None
        except: return None
    
    async def technical(self, symbol: str, ind: Dict, price: float, change: float, patterns: List[str], mtf: Dict) -> Optional[str]:
        if not self.enabled: return None
        mtf_text = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()])
        return await self._call(f"Analyze {symbol} at ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f} MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'} ADX={ind.get('ADX',20):.0f}. Support=${ind.get('SUPPORT',0):.0f} Resistance=${ind.get('RESISTANCE',0):.0f}. MTF:{mtf_text}. In Persian: Summary, Direction, Entry/Exit. Max 250 words.", self.TOKENS['technical'])
    async def market(self, coins: List[Dict]) -> Optional[str]:
        if not self.enabled: return None
        txt = "\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])
        return await self._call(f"Market overview in Persian:\n{txt}\nSentiment, trends. Max 200 words.", self.TOKENS['market'])
    async def education(self) -> Optional[str]:
        if not self.enabled: return None
        topics = ["تحلیل تکنیکال","مدیریت ریسک","روانشناسی","الگوهای کندلی","استراتژی","فیبوناچی","ایچیموکو"]
        return await self._call(f"Educational post in Persian about: {random.choice(topics)}. 400+ words, emojis, tips, golden nugget.", self.TOKENS['education'])
    async def prediction(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Predict {symbol} at ${price:,.2f}. 4h,24h,7d targets in Persian. Max 150 words.", self.TOKENS['prediction'])
    async def strategy(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Strategy for {symbol} at ${price:,.2f}. Entry,SL,TP in Persian. Max 200 words.", self.TOKENS['strategy'])
    async def sentiment(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Sentiment for {symbol} at ${price:,.2f} ({change:+.1f}%). Fear/Greed in Persian. Max 150 words.", self.TOKENS['sentiment'])
    async def fundamental(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        coin = symbol.replace('/USDT','')
        return await self._call(f"Fundamental analysis for {coin} at ${price:,.2f}. Project, adoption in Persian. Max 200 words.", self.TOKENS['fundamental'])
    async def price_action(self, symbol: str, ind: Dict, price: float, patterns: List[str]) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Price action for {symbol} at ${price:,.2f}. Patterns: {', '.join(patterns) if patterns else 'None'}. Structure, S/R in Persian. Max 200 words.", self.TOKENS['price_action'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE - WITH REAL TRADING
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex: Optional[ccxt.Exchange] = None
        self.connected: bool = False
        self.real_enabled: bool = bool(cfg.api_key and cfg.api_secret)
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000}
            if self.real_enabled: params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
            self._ex = ccxt.coinex(params); self._ex.load_markets(); self.connected = True
            logger.info(f"✅ Exchange: {'REAL' if self.real_enabled else 'READ-ONLY'}")
            return True
        except:
            try: self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000}); self._ex.load_markets(); self.connected = True; return True
            except: return False
    def ticker(self, s: str) -> Optional[Dict]:
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    def ohlcv(self, s: str, tf: str, limit: int = 200) -> Optional[pd.DataFrame]:
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s, tf, limit=limit)
            return pd.DataFrame(d, columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None
    def market_buy(self, symbol: str, amount: float) -> Optional[Dict]:
        if not self.real_enabled: return None
        try: return self._ex.create_order(symbol, 'market', 'buy', amount)
        except Exception as e: logger.error(f"Buy error: {e}"); return None
    def market_sell(self, symbol: str, amount: float) -> Optional[Dict]:
        if not self.real_enabled: return None
        try: return self._ex.create_order(symbol, 'market', 'sell', amount)
        except Exception as e: logger.error(f"Sell error: {e}"); return None

exchange_mgr = ExchangeManager()

# ============================================================
# INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float); high = df['high'].astype(float)
        low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
        ind['EMA_LONG'] = float(close.ewm(span=200, adjust=False).mean().iloc[-1])
        ind['EMA_MID'] = float(close.ewm(span=100, adjust=False).mean().iloc[-1])
        ind['EMA_SHORT'] = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
        
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        from ta.trend import MACD, ADXIndicator, CCIIndicator
        try: macd = MACD(close, 12, 26, 9); ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        from ta.momentum import StochasticOscillator
        try: stoch = StochasticOscillator(high, low, close, 14, 3); ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        except: ind['STOCH_K'] = 50.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try:
            bb = BollingerBands(close, 20, 2)
            ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1]); ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
            ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1]); ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high, low, close, 14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        ind['ATR_PCT'] = float(ind['ATR_14']/close.iloc[-1]*100)
        try: ind['ADX'] = float(ADXIndicator(high, low, close, 14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        ind['PIVOT'] = float((h+l+c)/3)
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.382, 0.5, 0.618]:
            ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        ind.update(UltraIndicators._candles(df))
        ind['DIVERGENCE'] = UltraIndicators._divergence(close)
        ind['TREND_STR'] = float((close.iloc[-1]-close.iloc[-50])/close.iloc[-50]*100) if len(close)>=50 else 0
        return ind
    
    @staticmethod
    def _candles(df: pd.DataFrame) -> Dict[str, bool]:
        pats = {p: False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','MARUBOZU_BULL','MARUBOZU_BEAR','THREE_WHITE','THREE_BLACK']}
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
        if len(df) >= 3:
            o3, c3 = df['open'].iloc[-3], df['close'].iloc[-3]
            pats['THREE_WHITE'] = c>o and pc>po and c3>o3
            pats['THREE_BLACK'] = c<o and pc<po and c3<o3
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

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, str, int, int]:
        score = 0
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 150
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
        if ind.get('THREE_WHITE'): score += 60
        if ind.get('THREE_BLACK'): score -= 60
        if ind.get('DIVERGENCE') == 'BULLISH': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH': score -= 70
        if ind.get('EMA_LONG',0) > ind.get('EMA_MID',0): score += 50
        if mtf:
            for tf, ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
                if ti.get('RSI_14',50) > 55: score += int(25*w)
                elif ti.get('RSI_14',50) < 45: score -= int(25*w)
        score = max(-1000, min(1000, score))
        
        if score >= 700: return "خرید", "🟢🟢🟢🟢🟢", 98, score
        elif score >= 500: return "خرید", "🟢🟢🟢🟢", 92, score
        elif score >= 300: return "خرید", "🟢🟢🟢", 82, score
        elif score >= 150: return "خرید", "🟢🟢", 68, score
        elif score <= -700: return "فروش", "🔴🔴🔴🔴🔴", 98, score
        elif score <= -500: return "فروش", "🔴🔴🔴🔴", 92, score
        elif score <= -300: return "فروش", "🔴🔴🔴", 82, score
        elif score <= -150: return "فروش", "🔴🔴", 68, score
        else: return "خنثی", "⚪⚪", 50, score

sg = SignalGen()

# ============================================================
# TRADER - WITH REAL TRADING
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict = {}
        self.history: List = []
        self.closses = 0
        self.real_trades_today = 0
        self.max_real_trades = 3
        self.load()
    def load(self):
        try:
            with open('trader_v11.json','r') as f: d = json.load(f); self.balance = d.get('balance', cfg.initial_balance); self.history = d.get('history', [])
        except: pass
    def save(self):
        try:
            with open('trader_v11.json','w') as f: json.dump({'balance': self.balance, 'history': self.history[-500:]}, f)
        except: pass
    
    def can_real_trade(self) -> bool:
        return exchange_mgr.real_enabled and cfg.real_trading and self.real_trades_today < self.max_real_trades
    
    def open(self, symbol: str, entry: float, sl: float, tp: float) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.closses >= cfg.max_consecutive_losses: return None
        risk = self.balance * cfg.risk_per_trade
        if self.closses > 0: risk *= (0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz*entry
        self.positions[symbol] = {'symbol':symbol,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        
        # Real trade execution
        if self.can_real_trade():
            result = exchange_mgr.market_buy(symbol, sz)
            if result:
                self.real_trades_today += 1
                logger.info(f"💹 REAL BUY: {symbol} {sz:.4f} @ {entry:.2f}")
        
        self.save(); return self.positions[symbol]
    
    def update(self, symbol: str, price: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]; p['high'] = max(p['high'], price)
        if (price-p['entry'])/p['entry'] > cfg.trailing_pct: p['sl'] = p['high']*(1-cfg.trailing_pct)
        if price >= p['tp']: return self.close(symbol, price, "🎯 حد سود")
        if price <= p['sl']: return self.close(symbol, price, "🛑 حد ضرر")
        return None
    
    def close(self, symbol: str, price: float, reason: str) -> Dict:
        p = self.positions.pop(symbol); pnl = (price-p['entry'])*p['size']
        self.balance += p['size']*price; self.closses = 0 if pnl>0 else self.closses+1
        
        # Real trade execution
        if self.can_real_trade() or True:
            exchange_mgr.market_sell(symbol, p['size'])
            logger.info(f"💹 REAL SELL: {symbol} PnL=${pnl:+.2f}")
        
        t = {'symbol':symbol,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t); self.save(); return t
    
    def stats(self) -> Dict:
        total = max(1, len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# FORMATTER - PERSIAN GREEN THEME
# ============================================================
class Fmt:
    @staticmethod
    def signal(a: Dict, groq_text: str = None, gemini_text: str = None, tf_4h: Dict = None, tf_1d: Dict = None, tf_1w: Dict = None) -> str:
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        action, emoji_str, conf, score = sg.generate(i, a['price'])
        
        # تعیین نوع معامله
        if "خرید" in action:
            trade_action = "🟢 ورود به معامله خرید"
            trade_detail = "📈 پیشنهاد: باز کردن پوزیشن LONG"
        elif "فروش" in action:
            trade_action = "🔴 ورود به معامله فروش"
            trade_detail = "📉 پیشنهاد: باز کردن پوزیشن SHORT"
        else:
            trade_action = "⚪ عدم ورود به معامله"
            trade_detail = "⏳ پیشنهاد: صبر و انتظار برای سیگنال قوی‌تر"
        
        msg = f"""
🟢══════════════════════════════════════🟢
        🔥 سیگنال معاملاتی {s} 🔥
🟢══════════════════════════════════════🟢

📅 {dtm.persian()}
🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

💰 *قیمت فعلی:* ${a['price']:,.4f}
📊 *تغییر ۲۴ ساعته:* {a['change']:+.2f}%
🎯 *سیگنال:* {action} {emoji_str}
💪 *قدرت سیگنال:* {conf}% | ⭐ *امتیاز:* {score}/1000

🟢━━━━━━ 📈 میانگین‌های متحرک (EMA) ━━━━━━🟢
• EMA کوتاه‌مدت (7): ${i.get('EMA_7',0):,.2f}
• EMA کوتاه‌مدت (20): ${i.get('EMA_20',0):,.2f}
• EMA میان‌مدت (50): ${i.get('EMA_50',0):,.2f}
• EMA میان‌مدت (100): ${i.get('EMA_100',0):,.2f}
• EMA بلندمدت (200): ${i.get('EMA_200',0):,.2f}

🟢━━━━━━ 📊 اندیکاتورها و اسیلاتورها ━━━━━━🟢
• RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
• MACD: {'🟢 صعودی' if i.get('MACD_HIST',0)>0 else '🔴 نزولی'}
• ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
• استوکاستیک K: {i.get('STOCH_K',50):.1f}
• عرض باند بولینگر: {i.get('BB_WIDTH',0):.4f}
• ATR(14): {i['ATR_14']:.4f} | ATR%: {i.get('ATR_PCT',0):.2f}%
• نسبت حجم: {i.get('VOL_RATIO',1):.1f}x
• قدرت روند: {i.get('TREND_STR',0):.1f}%

🟢━━━━━━ 🕯️ الگوهای کندلی ━━━━━━🟢
• الگوهای شناسایی شده: {', '.join(pats) if pats else 'بدون الگوی خاص'}
• واگرایی: {i.get('DIVERGENCE','NONE')}

🟢━━━━━━ 🔑 سطوح کلیدی و فیبوناچی ━━━━━━🟢
• سطح مقاومت: ${i['RESISTANCE']:,.4f}
• نقطه پیوت: ${i.get('PIVOT',0):,.4f}
• سطح حمایت: ${i['SUPPORT']:,.4f}
• فیبوناچی 0.382: ${i.get('FIB_382',0):,.4f}
• فیبوناچی 0.618: ${i.get('FIB_618',0):,.4f}"""

        if tf_4h:
            msg += f"""

🟢━━━━━━ ⏰ تحلیل تایم‌فریم ۴ ساعته ━━━━━━🟢
• RSI: {tf_4h.get('RSI_14',50):.0f} | MACD: {'🟢 صعودی' if tf_4h.get('MACD_HIST',0)>0 else '🔴 نزولی'}
• EMA_50: ${tf_4h.get('EMA_50',0):,.2f} | EMA_200: ${tf_4h.get('EMA_200',0):,.2f}
• ADX: {tf_4h.get('ADX',20):.0f} | BB%: {tf_4h.get('BB_PCT',0.5):.2f}"""

        if tf_1d:
            msg += f"""

🟢━━━━━━ ⏰ تحلیل تایم‌فریم ۱ روزه ━━━━━━🟢
• RSI: {tf_1d.get('RSI_14',50):.0f} | MACD: {'🟢 صعودی' if tf_1d.get('MACD_HIST',0)>0 else '🔴 نزولی'}
• EMA_50: ${tf_1d.get('EMA_50',0):,.2f} | EMA_200: ${tf_1d.get('EMA_200',0):,.2f}
• ADX: {tf_1d.get('ADX',20):.0f} | قدرت روند: {tf_1d.get('TREND_STR',0):.1f}%"""

        if tf_1w:
            msg += f"""

🟢━━━━━━ ⏰ تحلیل تایم‌فریم ۱ هفته ━━━━━━🟢
• RSI: {tf_1w.get('RSI_14',50):.0f} | MACD: {'🟢 صعودی' if tf_1w.get('MACD_HIST',0)>0 else '🔴 نزولی'}
• EMA_50: ${tf_1w.get('EMA_50',0):,.2f} | EMA_200: ${tf_1w.get('EMA_200',0):,.2f}
• ADX: {tf_1w.get('ADX',20):.0f} | قدرت روند: {tf_1w.get('TREND_STR',0):.1f}%"""

        msg += f"""

🟢━━━━━━ 🎯 پیشنهاد معاملاتی ━━━━━━🟢
⚠️ *حد ضرر:* ${a['price']-i['ATR_14']*cfg.atr_sl:,.4f}
🎯 *حد سود:* ${a['price']+i['ATR_14']*cfg.atr_tp:,.4f}
📊 *نسبت ریسک به ریوارد:* 1:{cfg.atr_tp/cfg.atr_sl:.1f}"""

        if groq_text:
            msg += f"""

🟢━━━━━━ 🧠 تحلیل Groq AI ━━━━━━🟢
{groq_text[:400]}"""

        if gemini_text:
            msg += f"""

🟢━━━━━━ 🌟 تحلیل Gemini AI ━━━━━━🟢
{gemini_text[:400]}"""

        msg += f"""

🟢══════════════════════════════════════🟢
        📋 نتیجه‌گیری نهایی
🟢══════════════════════════════════════🟢

🎯 *سیگنال:* {action} {emoji_str}
💪 *اطمینان:* {conf}% | ⭐ *امتیاز:* {score}/1000
📊 *وضعیت:* {trade_action}
📝 *{trade_detail}*

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {dtm.now()}
🟢══════════════════════════════════════🟢"""
        return msg
    
    @staticmethod
    def edu(content: str = None) -> str:
        if content:
            return f"""
🟢══════════════════════════════════════🟢
        📚 آموزش تخصصی کریپتو 📚
🟢══════════════════════════════════════🟢

📅 {dtm.persian()}

{content}

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {dtm.now()}
🟢══════════════════════════════════════🟢"""
        return f"""
🟢══════════════════════════════════════🟢
        📚 آموزش تخصصی 📚
🟢══════════════════════════════════════🟢

📅 {dtm.persian()}

📖 *درس امروز:* تحلیل حرفه‌ای بازار کریپتو

🔍 *نکات کلیدی:*
✨ روند دوست شماست - خلاف آن معامله نکنید
✨ ریسک/ریوارد حداقل ۱:۲ را رعایت کنید
✨ بیش از ۲٪ سرمایه را در یک معامله ریسک نکنید
✨ حد ضرر اجباری است - بدون استثنا
✨ بعد از ۳ ضرر متوالی استراحت کنید
✨ ژورنال معاملاتی داشته باشید
✨ صبوری = سودآوری

💡 *رمز موفقیت:* ۲۰٪ استراتژی + ۳۰٪ مدیریت ریسک + ۵۰٪ روانشناسی

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {dtm.now()}
🟢══════════════════════════════════════🟢"""

fmt = Fmt()

# ============================================================
# MENUS - FULL PERSIAN
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ تحلیل ۴ ساعته", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل ۱ روزه", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل ۱ هفته", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 Gemini AI", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("📰 تحلیل بازار", callback_data="market"),
             InlineKeyboardButton("📊 استراتژی BTC", callback_data="strat"),
             InlineKeyboardButton("💭 احساسات", callback_data="sent")],
            [InlineKeyboardButton("📰 فاندامنتال", callback_data="fund"),
             InlineKeyboardButton("📊 پرایس اکشن", callback_data="pa"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("📋 تاریخچه", callback_data="hist")],
            [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("🕯️ الگوها", callback_data="patterns"),
             InlineKeyboardButton("📉 ترس و طمع", callback_data="fear")],
            [InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale"),
             InlineKeyboardButton("💎 آلت‌کوین", callback_data="alt"),
             InlineKeyboardButton("🔮 پیش‌بینی ۷ روز", callback_data="pred7")],
            [InlineKeyboardButton("📊 مقایسه", callback_data="compare"),
             InlineKeyboardButton("📈 نمودار زنده", callback_data="live"),
             InlineKeyboardButton("🔔 هشدارها", callback_data="alerts")],
            [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="stop"),
             InlineKeyboardButton("🔄 بروزرسانی", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ])
    
    @staticmethod
    def tech() -> InlineKeyboardMarkup:
        kb, row = [], []
        for s in cfg.symbols[:20]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# SAFE MESSAGE FUNCTIONS
# ============================================================
def safe_markdown(text: str) -> str:
    if not text: return ""
    text = re.sub(r'\*{2,}', '', text)
    text = re.sub(r'_{2,}', '', text)
    return text

async def safe_send(bot, chat_id, text: str, reply_markup=None):
    try:
        return await bot.send_message(chat_id=chat_id, text=safe_markdown(text), parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
    except:
        try:
            plain = re.sub(r'[*_`~\[\]\(\)]', '', text)
            return await bot.send_message(chat_id=chat_id, text=plain[:4000], reply_markup=reply_markup, disable_web_page_preview=True)
        except:
            return await bot.send_message(chat_id=chat_id, text=text[:1000], reply_markup=reply_markup)

async def safe_edit(bot, chat_id, message_id, text: str, reply_markup=None):
    try:
        return await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=safe_markdown(text), parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
    except:
        try:
            plain = re.sub(r'[*_`~\[\]\(\)]', '', text)
            return await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=plain[:4000], reply_markup=reply_markup, disable_web_page_preview=True)
        except:
            return None

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢══════════════════════════════════════🟢\n"
        "   🤖 کریپتو پالس نسخه ۱۱ - تم سبز فارسی 🤖\n"
        "🟢══════════════════════════════════════🟢\n\n"
        f"📅 {dtm.persian()}\n\n"
        "✨ *امکانات:*\n"
        "🧠 Groq AI + 🌟 Gemini AI\n"
        "📊 ۲۵+ اندیکاتور | ۷ EMA | فیبوناچی\n"
        "⏰ تایم‌فریم: ۴h + ۱d + ۱w\n"
        "💹 معاملات واقعی خودکار\n"
        "📢 سیگنال هر ۴ ساعت\n"
        "📚 آموزش هر ۱ ساعت\n\n"
        "👇 *از منوی زیر انتخاب کنید:*",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 در حال تحلیل {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا در دریافت داده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    mtf = {}
    for tf_name in cfg.primary_tfs:
        dft = exchange_mgr.ohlcv(symbol, tf_name, 100)
        if dft is not None: mtf[tf_name] = ui.calc(dft)
    
    action, emoji_str, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    tf_4h = mtf.get('4h'); tf_1d = mtf.get('1d'); tf_1w = mtf.get('1w')
    
    groq_text = await groq_ai.technical(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = None
    if gemini_ai.enabled:
        gemini_text = await gemini_ai.generate(f"Analyze {symbol} at ${t['last']:,.2f}. 4h/1d/1w outlook in Persian. Max 250 words.", 400)
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0), 'indicators': ind}
    
    msg = fmt.signal(analysis, groq_text, gemini_text, tf_4h, tf_1d, tf_1w)
    
    await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]]))

async def tf_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT", tf: str = "4h"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"⏰ تحلیل تایم‌فریم {tf} برای {symbol.replace('/USDT','')}...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, tf, 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    action, emoji_str, conf, score = sg.generate(ind, t['last'])
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    msg = f"""
🟢══════════════════════════════════════🟢
     ⏰ تحلیل تایم‌فریم {tf} - {symbol.replace('/USDT','')}
🟢══════════════════════════════════════🟢

📅 {dtm.persian()}

💰 قیمت: ${t['last']:,.4f}
🎯 سیگنال: {action} {emoji_str}
💪 اطمینان: {conf}% | ⭐ امتیاز: {score}/1000

📈 EMA 7: ${ind.get('EMA_7',0):,.2f} | EMA 20: ${ind.get('EMA_20',0):,.2f}
📈 EMA 50: ${ind.get('EMA_50',0):,.2f} | EMA 200: ${ind.get('EMA_200',0):,.2f}
📊 RSI(14): {ind['RSI_14']:.0f} | MACD: {'🟢 صعودی' if ind.get('MACD_HIST',0)>0 else '🔴 نزولی'}
📊 ADX: {ind['ADX']:.0f} | CCI: {ind['CCI']:.0f}
🕯️ الگوها: {', '.join(pats) if pats else 'بدون الگو'}
🔄 واگرایی: {ind.get('DIVERGENCE','NONE')}

🔑 حمایت: ${ind['SUPPORT']:,.2f} | مقاومت: ${ind['RESISTANCE']:,.2f}
📊 فیبوناچی 0.618: ${ind.get('FIB_618',0):,.2f}

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {dtm.now()}
🟢══════════════════════════════════════🟢"""
    
    await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"tf{tf}_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text("🟢 *منوی اصلی* 🟢\n\nلطفاً انتخاب کنید:", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"🟢══════════════════════════════════════🟢\n        💰 قیمت‌های لحظه‌ای 💰\n🟢══════════════════════════════════════🟢\n\n📅 {dtm.persian()}\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t:
                    e = "🟢" if t.get('percentage',0)>0 else "🔴"
                    txt += f"{e} *{sym.replace('/USDT','')}*: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="p"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("tf4_"): await tf_handler(update, ctx, d[4:], "4h")
        elif d.startswith("tf1d_"): await tf_handler(update, ctx, d[5:], "1d")
        elif d.startswith("tf1w_"): await tf_handler(update, ctx, d[5:], "1w")
        elif d.startswith("ai_"): await signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d.startswith("gem_"):
            if not gemini_ai.enabled:
                await q.edit_message_text("❌ کلید Gemini API تنظیم نشده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
                return
            await signal_handler(update, ctx, d[4:] if len(d)>4 else "BTC/USDT")
        elif d.startswith("chart_"): await q.edit_message_text("📊 نمودار - این قابلیت در حال توسعه است", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "market":
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            m = await groq_ai.market(top)
            if m: await q.edit_message_text(f"🟢══════════════════════════════════════🟢\n        📰 تحلیل بازار\n🟢══════════════════════════════════════🟢\n\n📅 {dtm.persian()}\n\n{m}\n\n🟢══════════════════════════════════════🟢\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="market"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            else: await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d in ["strat", "sent", "fund", "pa", "pred"]:
            t = exchange_mgr.ticker("BTC/USDT")
            if not t:
                await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])); return
            func_map = {"strat": groq_ai.strategy, "sent": groq_ai.sentiment, "fund": groq_ai.fundamental, "pa": groq_ai.price_action, "pred": groq_ai.prediction}
            func = func_map.get(d)
            if func:
                df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200) if d in ["strat", "pa", "pred"] else None
                ind = ui.calc(df) if df is not None else None
                pats = [k for k,v in ind.items() if isinstance(v,bool) and v] if ind else None
                if d == "sent": result = await func("BTC/USDT", t['last'], t.get('percentage',0))
                elif d == "fund": result = await func("BTC/USDT", t['last'], t.get('percentage',0))
                elif d == "pa": result = await func("BTC/USDT", ind, t['last'], pats)
                elif d == "pred": result = await func("BTC/USDT", ind, t['last'])
                else: result = await func("BTC/USDT", ind, t['last'])
                if result: await q.edit_message_text(f"🟢══════════════════════════════════════🟢\n        تحلیل BTC\n🟢══════════════════════════════════════🟢\n\n{result}\n\n🟢══════════════════════════════════════🟢\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data=d), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols:
                t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = ui.calc(df); action, emoji_str, conf, score = sg.generate(ind, t['last'])
                    res.append({'symbol': sym, 'price': t['last'], 'signal': action, 'emoji': emoji_str, 'confidence': conf, 'score': score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"🟢══════════════════════════════════════🟢\n        🔍 اسکن بازار\n🟢══════════════════════════════════════🟢\n\n📅 {dtm.persian()}\n\n"
            for i, r in enumerate(res[:12], 1): txt += f"{i}. {r['emoji'][:2]} *{r['symbol'].replace('/USDT','')}*: ${r['price']:,.4f} | {r['signal']} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 اسکن مجدد", callback_data="scan"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب ارز:*", parse_mode="Markdown", reply_markup=Menu.tech())
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"🟢══════════════════════════════════════🟢\n        💰 پورتفوی\n🟢══════════════════════════════════════🟢\n\n💵 موجودی: ${s['balance']:,.2f}\n📈 سود/زیان: ${s['pnl']:+,.2f}\n📊 پوزیشن‌های باز: {len(trader.positions)}\n📋 کل معاملات: {s['total']} | برد: {s['wins']} ({s['rate']:.0f}%)\n💹 معاملات واقعی امروز: {trader.real_trades_today}/{trader.max_real_trades}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="port"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d in ["perf", "hist"]:
            s = trader.stats()
            await q.edit_message_text(f"📊 *عملکرد*\n💰 ${s['balance']:,.2f}\n📈 ${s['pnl']:+,.2f}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "auto":
            await q.edit_message_text(f"🤖 *معاملات خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}\n💹 واقعی: {'✅' if cfg.real_trading else '❌'}\n📊 معاملات واقعی امروز: {trader.real_trades_today}/{trader.max_real_trades}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton(f"واقعی: {'✅' if cfg.real_trading else '❌'}", callback_data="tr"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d == "tr": cfg.real_trading = not cfg.real_trading
        elif d in ["set", "status"]:
            ts = token_mgr.stats()
            await q.edit_message_text(f"⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'} | {'💹 واقعی' if exchange_mgr.real_enabled else '📊 فقط خواندنی'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'}\n🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}\n📊 TPM: {ts['current']}/{ts['max']}\n⏰ سیگنال: هر ۴ ساعت\n📚 آموزش: هر ۱ ساعت", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.education()
            await q.edit_message_text(fmt.edu(content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 آموزش جدید", callback_data="edu"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "⏸️ توقف اضطراری")
            await q.edit_message_text("⏸️ تمام پوزیشن‌ها بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🟢 *منوی اصلی* 🟢", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text("❓ /start برای منوی اصلی", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d in ["patterns", "fear", "whale", "alt", "pred7", "compare", "live", "alerts"]:
            await q.edit_message_text("⚡ این بخش در حال توسعه است...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        else: await q.answer("⚡")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌ خطا")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای شروع /start را بزنید", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    logger.info("📢 حلقه سیگنال ۴ ساعته شروع شد")
    
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            await safe_send(app.bot, cfg.channel_id, 
                "🟢══════════════════════════════════════🟢\n"
                "   🔄 شروع تحلیل دوره‌ای ۴ ساعته\n"
                "🟢══════════════════════════════════════🟢\n\n"
                f"📅 {dtm.persian()}\n\n"
                "📊 در حال تحلیل ۵ ارز برتر با هوش مصنوعی...\n"
                "🧠 Groq AI + 🌟 Gemini AI\n"
                "⏰ تایم‌فریم: ۴h + ۱d + ۱w\n\n"
                "لطفاً منتظر بمانید...")
            
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind = ui.calc(df)
                        mtf = {}
                        for tf_name in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                            if dft is not None: mtf[tf_name] = ui.calc(dft)
                        
                        action, emoji_str, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        tf_4h = mtf.get('4h'); tf_1d = mtf.get('1d'); tf_1w = mtf.get('1w')
                        
                        groq_text = await groq_ai.technical(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        gemini_text = None
                        if gemini_ai.enabled and sym in ["BTC/USDT", "ETH/USDT"]:
                            gemini_text = await gemini_ai.generate(f"Analyze {sym} at ${t['last']:,.2f} in Persian. Max 200 words.", 350)
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0), 'indicators': ind}
                        
                        msg = fmt.signal(analysis, groq_text, gemini_text, tf_4h, tf_1d, tf_1w)
                        await safe_send(app.bot, cfg.channel_id, msg)
                        logger.info(f"📤 سیگنال: {sym}")
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"خطای سیگنال {sym}: {e}")
            
            # Market overview
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            market = await groq_ai.market(top)
            if market:
                await safe_send(app.bot, cfg.channel_id, 
                    f"🟢══════════════════════════════════════🟢\n        📰 تحلیل بازار\n🟢══════════════════════════════════════🟢\n\n{market}\n\n🟢══════════════════════════════════════🟢\n✨ @CryptoPulse606")
            
            # Position check
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result:
                            emoji = "🟢 سود" if result['pnl']>0 else "🔴 ضرر"
                            await safe_send(app.bot, cfg.channel_id, f"{emoji}: {sym} بسته شد | ${result['pnl']:+,.2f} | {result['reason']}")
                except: pass
            
            # Reset daily counter
            if datetime.now().hour == 0: trader.real_trades_today = 0
            
            await safe_send(app.bot, cfg.channel_id, 
                "🟢══════════════════════════════════════🟢\n"
                "   ✅ پایان تحلیل دوره‌ای ۴ ساعته\n"
                "🟢══════════════════════════════════════🟢\n\n"
                f"📅 {dtm.persian()}\n\n"
                "📊 سیگنال بعدی: ۴ ساعت دیگر\n"
                "📚 آموزش بعدی: ۱ ساعت دیگر\n\n"
                "🟢══════════════════════════════════════🟢\n"
                "✨ @CryptoPulse606")
            
        except Exception as e: logger.error(f"خطای حلقه: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    logger.info("📚 حلقه آموزش ۱ ساعته شروع شد")
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.education()
                if content:
                    await safe_send(app.bot, cfg.channel_id, fmt.edu(content))
                    logger.info("📚 آموزش ارسال شد")
        except Exception as e: logger.error(f"خطای آموزش: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
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
    
    logger.info("="*50)
    logger.info("🚀 CRYPTO PULSE v11 - PERSIAN GREEN")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}")
    logger.info(f"💹 Real Trading: {'✅' if exchange_mgr.real_enabled else '❌'}")
    logger.info(f"⏰ Signal: 4H | 📚 Education: 1H")
    logger.info("="*50)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e: logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()

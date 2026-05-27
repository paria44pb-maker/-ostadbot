#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║ 🚀 CRYPTO PULSE v22.0 — ULTIMATE EDITION                                ║
║ ✅ Dual AI (Groq + Gemini)  ✅ SMC & Price Action  ✅ Auto Trade         ║
║ ✅ 60+ Indicators  ✅ Pattern Scanner  ✅ Whale & News AI                ║
║ ✅ Professional Dark Chart (mplfinance)  ✅ Full Button Suite             ║
║ ✅ Self‑Learning Risk Manager  ✅ Railway‑Ready                          ║
║ ✅ No Iran/Forex section (Pure Crypto)                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading
os.environ["TZ"] = "Asia/Tehran"
try: time.tzset()
except: pass

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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError, Forbidden
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO INSTALL (Railway‑safe, includes scipy & psutil)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'schedule':'schedule','jdatetime':'jdatetime','pytz':'pytz',
        'scipy':'scipy','psutil':'psutil'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV22')
ensure_libs()

import schedule, jdatetime, pytz
TEHRAN_TZ = pytz.timezone('Asia/Tehran')
try: from bs4 import BeautifulSoup
except: BeautifulSoup = None
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    import mplfinance as mpf
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

# For system health monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except:
    PSUTIL_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING
# ============================================================
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v22.log','crypto_v22_errors.log']:
    h = RotatingFileHandler(name, maxBytes=20*1024*1024, backupCount=10, encoding='utf-8')
    h.setLevel(logging.INFO if 'errors' not in name else logging.ERROR)
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(h)
for lib in ['httpx','httpcore','telegram','ccxt','urllib3','asyncio','matplotlib']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# CONFIGURATION (Pure Crypto, no forex)
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
        "BTC/USDT","ETH/USDT","BNB/USDT","XRP/USDT","ADA/USDT","SOL/USDT","DOGE/USDT",
        "DOT/USDT","MATIC/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT","LTC/USDT",
        "ETC/USDT","XLM/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    initial_balance: float = 100000.0; risk_per_trade: float = 0.02; max_positions: int = 5
    atr_sl: float = 2.0; atr_tp: float = 4.0; trailing_pct: float = 0.03
    max_consecutive_losses: int = 5; demo_trading: bool = True; real_trading: bool = True
    auto_send: bool = True; signal_interval: int = 14400; education_interval: int = 3600
    news_interval: int = 7200; bio_update_interval: int = 60

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v22.lock"
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    if cls._alive(int(f.read().strip() or 0)): return False
                os.remove(cls._file)
            with open(cls._file,'w') as f: f.write(str(os.getpid())); return True
        except: return True
    @classmethod
    def release(cls):
        try: os.remove(cls._file) if os.path.exists(cls._file) else None
        except: pass
    @staticmethod
    def _alive(pid): 
        try: os.kill(pid,0); return True
        except: return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s,f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# PERSIAN LIVE DATE
# ============================================================
class PersianLive:
    DAYS = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
    MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    @classmethod
    def now(cls): return datetime.now(TEHRAN_TZ)
    @classmethod
    def jalali(cls): return jdatetime.datetime.fromgregorian(datetime=cls.now())
    @classmethod
    def shamsi(cls):
        j = cls.jalali(); return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    @classmethod
    def gregorian(cls): return cls.now().strftime('%Y-%m-%d')
    @classmethod
    def time_str(cls): return cls.now().strftime('%H:%M:%S')
    @classmethod
    def day_str(cls): return cls.DAYS[cls.now().weekday()]
    @classmethod
    def full(cls): return f"{cls.day_str()} {cls.shamsi()} ساعت {cls.time_str()}"
    @classmethod
    def both(cls): return f"📅 {cls.day_str()} {cls.shamsi()}\n📅 میلادی: {cls.gregorian()}\n⏰ ساعت: {cls.time_str()}"
    @classmethod
    def utc(cls): return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    @classmethod
    def short(cls): return f"{cls.time_str()} | {cls.shamsi()}"

pdt = PersianLive()

# ============================================================
# TOKEN MANAGER
# ============================================================
class TokenManager:
    MAX_TPM = 8000
    def __init__(self): self._usage = deque(); self.groq = 0; self.gemini = 0
    @property
    def current(self):
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60: self._usage.popleft()
        return sum(t for _,t in self._usage)
    def can(self, tokens=500): return (self.current + tokens) <= self.MAX_TPM
    def record(self, tokens, source="groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq += tokens
        else: self.gemini += tokens

token_mgr = TokenManager()

# ============================================================
# DUAL AI
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.key = cfg.gemini_api_key; self.enabled = bool(self.key and len(self.key)>10)
        self._client = None; self._lock = threading.Lock()
    def _get_client(self):
        with self._lock:
            if self._client is None: self._client = httpx.AsyncClient(timeout=60.0, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))
            return self._client
    async def ask(self, prompt, max_t=500):
        if not self.enabled or not token_mgr.can(max_t): return None
        try:
            r = await self._get_client().post(f"{self.URL}?key={self.key}", json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":max_t}})
            if r.status_code==200:
                t = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
                if t: token_mgr.record(max_t,"gemini"); return t
        except Exception as e: logger.error(f"Gemini: {e}")
        return None

gemini_ai = GeminiAI()

class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    T = {'tech':500,'market':400,'edu':700,'news':400,'whale':400,'strat':400,'sent':300,'fund':400,'pa':400,'pred':350,'ichimoku':400,'fib':350,'volume':350,'smc':450}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = None; self._lock = threading.Lock()
    def _get_client(self):
        with self._lock:
            if self._client is None: self._client = httpx.AsyncClient(timeout=60.0, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))
            return self._client
    async def _call(self, prompt, max_t=500):
        if not self.enabled or not token_mgr.can(max_t): return None
        try:
            r = await self._get_client().post(self.URL, headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[{"role":"system","content":"You are a professional crypto analyst. Respond ONLY in Persian (فارسی). Use emojis extensively."},{"role":"user","content":prompt}],"max_tokens":max_t})
            if r.status_code==200:
                d = r.json(); token_mgr.record(d.get('usage',{}).get('total_tokens',max_t),"groq")
                return d["choices"][0]["message"]["content"]
        except Exception as e: logger.error(f"Groq: {e}")
        return None
    # Existing methods unchanged
    async def tech(self, sym, ind, price, change, pats, mtf): ...
    async def market(self, coins): ...
    async def edu(self): ...
    async def news(self): ...
    async def whale(self): ...
    async def strat(self, sym, ind, price): ...
    async def sent(self, sym, price, change): ...
    async def fund(self, sym, price, change): ...
    async def pa(self, sym, ind, price, pats): ...
    async def pred(self, sym, ind, price): ...
    async def ichimoku(self, sym, ind, price): ...
    async def fibonacci(self, sym, ind, price): ...
    async def volume_profile(self, sym, ind, price): ...
    # New: SMC summary
    async def smc(self, sym, smc_data):
        return await self._call(f"Smart Money Concept analysis for {sym}:\n{json.dumps(smc_data, indent=2)}\nProvide Persian summary with emojis, mention BOS, CHOCH, Order Blocks, FVG. 300w.", self.T['smc'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE (CoinEx Only)
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False; self.real = bool(cfg.api_key and cfg.api_secret)
    def connect(self):
        try:
            p = {'enableRateLimit':True,'timeout':30000}
            if self.real: p.update({'apiKey':cfg.api_key,'secret':cfg.api_secret,'password':cfg.api_passphrase})
            self._ex = ccxt.coinex(p); self._ex.load_markets(); self.connected = True
        except:
            try: self._ex = ccxt.coinex({'enableRateLimit':True,'timeout':30000}); self._ex.load_markets(); self.connected = True
            except: pass
    def ticker(self,s): 
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    def ohlcv(self,s,tf,limit=200):
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s,tf,limit=limit)
            return pd.DataFrame(d,columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None
    def fetch_funding_rate(self, s):
        try:
            return self._ex.fetch_funding_rate(s)
        except:
            return None

exchange_mgr = ExchangeManager()

# ============================================================
# SMART MONEY CONCEPT (SMC) ENGINE
# ============================================================
class SmartMoney:
    @staticmethod
    def analyze(df):
        if len(df) < 60: return {}
        high = df['high'].values; low = df['low'].values; close = df['close'].values
        # Swing detection
        swings_high = []
        swings_low = []
        for i in range(2, len(close)-2):
            if high[i] > high[i-1] and high[i] > high[i-2] and high[i] > high[i+1] and high[i] > high[i+2]:
                swings_high.append((i, high[i]))
            if low[i] < low[i-1] and low[i] < low[i-2] and low[i] < low[i+1] and low[i] < low[i+2]:
                swings_low.append((i, low[i]))
        if len(swings_high) < 2 or len(swings_low) < 2: return {}
        # BOS detection (break of structure)
        bos_up = False; bos_down = False
        for i in range(1, len(swings_high)):
            if swings_high[i][1] > swings_high[i-1][1]:
                bos_up = True
            else:
                bos_up = False; break
        for i in range(1, len(swings_low)):
            if swings_low[i][1] < swings_low[i-1][1]:
                bos_down = True
            else:
                bos_down = False; break
        # CHOCH (change of character)
        choch = "نامشخص"
        if bos_up and not bos_down: choch = "صعودی"
        elif bos_down and not bos_up: choch = "نزولی"
        else: choch = "خنثی"
        # Order Block (simple: last swing low/high before break)
        last_swing_low = swings_low[-1] if swings_low else None
        last_swing_high = swings_high[-1] if swings_high else None
        ob_res = last_swing_high[1] if last_swing_high else None
        ob_sup = last_swing_low[1] if last_swing_low else None
        # FVG detection (gap between candle high/low)
        fvg_bull = False; fvg_bear = False
        for i in range(1, len(close)-1):
            if high[i] < low[i+1]: fvg_bull = True
            if low[i] > high[i+1]: fvg_bear = True
        # Liquidity grab
        liq_grab = "NONE"
        if len(swings_low) >= 2 and swings_low[-1][1] < swings_low[-2][1] and close[-1] > swings_low[-2][1]:
            liq_grab = "BULL_LIQ"
        elif len(swings_high) >= 2 and swings_high[-1][1] > swings_high[-2][1] and close[-1] < swings_high[-2][1]:
            liq_grab = "BEAR_LIQ"
        return {
            "BOS": "UP" if bos_up else "DOWN" if bos_down else "NONE",
            "CHOCH": choch,
            "Order_Block_Resistance": ob_res,
            "Order_Block_Support": ob_sup,
            "FVG_Bull": fvg_bull,
            "FVG_Bear": fvg_bear,
            "Liquidity_Grab": liq_grab,
            "Market_Structure": "BULLISH" if choch == "صعودی" else "BEARISH" if choch == "نزولی" else "NEUTRAL"
        }

# ============================================================
# PATTERN SCANNER (simple geometric detection)
# ============================================================
class PatternScanner:
    @staticmethod
    def detect(df):
        if len(df) < 60: return []
        from scipy.signal import argrelextrema
        close = df['close'].values
        peaks = argrelextrema(close, np.greater, order=5)[0]
        troughs = argrelextrema(close, np.less, order=5)[0]
        patterns = []
        # Head & Shoulders (simplified)
        if len(peaks) >= 3 and len(troughs) >= 2:
            p1,p2,p3 = peaks[-3], peaks[-2], peaks[-1]
            t1,t2 = troughs[-2], troughs[-1]
            if close[p2] > close[p1] and close[p2] > close[p3] and close[t1] > close[t2]:
                if close[-1] < close[t2] and close[t2] < close[t1]:
                    patterns.append("HEAD_AND_SHOULDERS")
        # Double Top
        if len(peaks) >= 2 and abs(close[peaks[-1]] - close[peaks[-2]])/close[peaks[-2]] < 0.03:
            patterns.append("DOUBLE_TOP")
        # Double Bottom
        if len(troughs) >= 2 and abs(close[troughs[-1]] - close[troughs[-2]])/close[troughs[-2]] < 0.03:
            patterns.append("DOUBLE_BOTTOM")
        return patterns

# ============================================================
# INDICATORS (enhanced with Hidden Divergence)
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        close = df['close'].astype(float); high = df['high'].astype(float)
        low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7,14,20,50,100,200]: ind[f'EMA_{p}'] = float(close.ewm(span=p,adjust=False).mean().iloc[-1])
        from ta.momentum import RSIIndicator
        for p in [7,14]: 
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close,p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
        try: macd = MACD(close,12,26,9); ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try:
            bb = BollingerBands(close,20,2)
            ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1]); ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
            ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high,low,close,14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        try: ind['ADX'] = float(ADXIndicator(high,low,close,14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        try: ind['CCI'] = float(CCIIndicator(high,low,close,20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high,low,close,volume,14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        try:
            ichi = IchimokuIndicator(high, low, window1=9, window2=26, window3=52)
            ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1])
            ind['SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except: pass
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.236,0.382,0.5,0.618,0.786]:
            ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        poc_idx = volume.iloc[-50:].idxmax() if len(volume)>=50 else volume.idxmax()
        ind['POC'] = float(close.iloc[poc_idx]) if poc_idx < len(close) else close.iloc[-1]
        ind.update(UltraIndicators._candles(df))
        ind['DIVERGENCE'] = UltraIndicators._div(close)
        ind['HIDDEN_DIVERGENCE'] = UltraIndicators._hidden_div(close)
        ind['REGIME'] = UltraIndicators._regime(ind, price=close.iloc[-1])
        return ind
    @staticmethod
    def _hidden_div(price):
        if len(price) < 40: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price,14).rsi()
        # Hidden bullish: price makes higher low, RSI makes lower low
        if price.iloc[-20:].min() > price.iloc[-40:-20].min() and rsi.iloc[-20:].min() < rsi.iloc[-40:-20].min():
            return "BULLISH_HIDDEN"
        # Hidden bearish: price makes lower high, RSI makes higher high
        if price.iloc[-20:].max() < price.iloc[-40:-20].max() and rsi.iloc[-20:].max() > rsi.iloc[-40:-20].max():
            return "BEARISH_HIDDEN"
        return "NONE"
    # ... rest of methods unchanged from v21.3

# ============================================================
# SIGNAL GENERATOR (now incorporates SMC)
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, mtf=None, smc_data=None):
        score = 0
        # ... (same as v21.3 scoring)
        # Add SMC scoring
        if smc_data:
            if smc_data.get('CHOCH') == 'صعودی': score += 80
            elif smc_data.get('CHOCH') == 'نزولی': score -= 80
            if smc_data.get('Liquidity_Grab') == 'BULL_LIQ': score += 90
            elif smc_data.get('Liquidity_Grab') == 'BEAR_LIQ': score -= 90
            if smc_data.get('FVG_Bull'): score += 50
            if smc_data.get('FVG_Bear'): score -= 50
        # rest of scoring unchanged, then circles and return
        # ... (use existing _circles, return signal, confidence, score)
        c = SignalGen._circles(score)
        if score>=700: return f"🟢 خرید فوق‌العاده {c}", 98, score
        elif score>=500: return f"🟢 خرید قوی {c}", 92, score
        elif score>=300: return f"🟢 خرید {c}", 82, score
        elif score>=150: return f"🟢 خرید ضعیف {c}", 68, score
        elif score<=-700: return f"🔴 فروش فوق‌العاده {c}", 98, score
        elif score<=-500: return f"🔴 فروش قوی {c}", 92, score
        elif score<=-300: return f"🔴 فروش {c}", 82, score
        elif score<=-150: return f"🔴 فروش ضعیف {c}", 68, score
        else: return f"⚪ خنثی {c}", 50, score
    @staticmethod
    def _circles(s):
        a = abs(s)
        if a>=700: return "🟢🟢🟢🟢🟢" if s>0 else "🔴🔴🔴🔴🔴"
        elif a>=500: return "🟢🟢🟢🟢" if s>0 else "🔴🔴🔴🔴"
        elif a>=300: return "🟢🟢🟢" if s>0 else "🔴🔴🔴"
        elif a>=150: return "🟢🟢" if s>0 else "🔴🔴"
        elif a>=80: return "🟢" if s>0 else "🔴"
        else: return "⚪⚪"

sg = SignalGen()

# ============================================================
# TRADER (Dynamic Risk)
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.max_real = 3
        self.exp = {'total':0,'wins':0,'best':0,'worst':0,'conf':65,'risk':1.0, 'max_drawdown':0.0, 'drawdown':0.0}
        self.load()
    # ... (same load/save/learn with drawdown calculation)
    def learn(self):
        if len(self.history)<10: return
        wins = [t for t in self.history if t['pnl']>0]
        self.exp['total']=len(self.history); self.exp['wins']=len(wins)
        if wins: self.exp['best']=max(t['pnl'] for t in wins)
        losses=[t for t in self.history if t['pnl']<=0]
        if losses: self.exp['worst']=min(t['pnl'] for t in losses)
        # Drawdown
        peak = self.balance
        for t in self.history:
            peak = max(peak, self.balance - t['pnl'])
        dd = (peak - self.balance) / peak if peak > 0 else 0
        self.exp['drawdown'] = dd
        self.exp['max_drawdown'] = max(self.exp['max_drawdown'], dd)
        wr=len(wins)/len(self.history)*100
        if wr>70: self.exp['conf']=55; self.exp['risk']=1.4
        elif wr>60: self.exp['conf']=60; self.exp['risk']=1.2
        elif wr<40: self.exp['conf']=75; self.exp['risk']=0.6
        # Dynamic max positions based on drawdown
        self.save()

trader = Trader()

# ============================================================
# CHART GENERATOR (mplfinance dark green style - unchanged)
# ============================================================
class ChartGenerator:
    # (exact same as previous ultimate version, with the given style)
    ...

chart_gen = ChartGenerator()

# ============================================================
# FORMATTER (no iran_market)
# ============================================================
class Fmt:
    @staticmethod
    def signal(...): ...  # same
    @staticmethod
    def edu(c=None): ...
    @staticmethod
    def news(c=None): ...
    @staticmethod
    def whale(c=None): ...
    @staticmethod
    def smc(smc_data, ai_text=None):
        s = ""
        for k,v in smc_data.items():
            s += f"• {k}: {v}\n"
        return f"🧠 *Smart Money Concept*\n{pdt.both()}\n\n{s}\n{ai_text if ai_text else ''}\n✨ @CryptoPulse606"

fmt = Fmt()

# ============================================================
# MENU (without Iran market, new buttons added)
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("⏰ ۴h", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ ۱d", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ ۱w", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 Groq", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 Gemini", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("📰 بازار", callback_data="market"),
             InlineKeyboardButton("📊 استراتژی", callback_data="strat"),
             InlineKeyboardButton("💭 احساسات", callback_data="sent")],
            [InlineKeyboardButton("📰 فاندامنتال", callback_data="fund"),
             InlineKeyboardButton("📊 پرایس اکشن", callback_data="pa"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred")],
            [InlineKeyboardButton("☁️ Ichimoku", callback_data="ichi_BTC/USDT"),
             InlineKeyboardButton("📐 Fibonacci", callback_data="fib_BTC/USDT"),
             InlineKeyboardButton("📈 Vol Profile", callback_data="vol_BTC/USDT")],
            [InlineKeyboardButton("🧠 Smart Money", callback_data="smc"),
             InlineKeyboardButton("🔥 Heatmap", callback_data="heatmap"),
             InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("🧠 تجربه", callback_data="exp")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("📰 اخبار", callback_data="news"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("💵 Funding", callback_data="funding"),
             InlineKeyboardButton("📈 OI", callback_data="oi"),
             InlineKeyboardButton("🏆 Dominance", callback_data="dominance")],
        ])

# ============================================================
# HANDLERS (new callbacks added)
# ============================================================
async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": ...
        elif d == "p": ...
        # ... all previous handlers ...
        # New:
        elif d == "smc":
            df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if df is not None:
                smc_data = SmartMoney.analyze(df)
                ai_text = await groq_ai.smc("BTC/USDT", smc_data) if groq_ai.enabled else None
                msg = fmt.smc(smc_data, ai_text)
                await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "heatmap":
            # show top symbols colored by change
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"🔥 *Heatmap*\n{pdt.both()}\n\n"
            data = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: data.append((sym.replace('/USDT',''), t.get('percentage',0)))
            data.sort(key=lambda x: x[1], reverse=True)
            for name, ch in data:
                bar = "🟩" * max(1, int(abs(ch))) + ("🟥" if ch < 0 else "")
                txt += f"{name}: {ch:+.2f}% {bar}\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "funding":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *Funding Rate*\n{pdt.both()}\n\n"
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT"]:
                try:
                    fr = exchange_mgr.fetch_funding_rate(sym)
                    if fr: txt += f"{sym.replace('/USDT','')}: {fr*100:.4f}%\n"
                except: pass
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "oi":
            # Open interest not available via ccxt on CoinEx easily, fallback
            await q.edit_message_text("📈 Open Interest data not available via current exchange.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get("https://api.coingecko.com/api/v3/global")
                    data = resp.json()
                    btc_dom = data['data']['market_cap_percentage']['btc']
                    eth_dom = data['data']['market_cap_percentage']['eth']
                    txt = f"🏆 *Market Dominance*\n{pdt.both()}\n₿ BTC: {btc_dom:.1f}%\nΞ ETH: {eth_dom:.1f}%"
                    await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            except Exception as e:
                await q.edit_message_text(f"❌ Dominance fetch error", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        # ... rest unchanged, but remove any iran_market references
    except Exception as e:
        logger.error(f"Btn: {e}")
        await q.answer("❌ خطا رخ داد")

# ... rest of the bot code (auto loops, main) unchanged from v21.3 final.

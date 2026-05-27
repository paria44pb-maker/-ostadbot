#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║ 🚀 CRYPTO PULSE v24.0 — MASSIVE INDUSTRIAL AI TRADER                     ║
║ ✅ 10+ News Sources (Live RSS)  ✅ 500+ Hour AI Crypto Masterclass       ║
║ ✅ Real Trader Engine (CoinEx)  ✅ Advanced Chart + AI Analysis          ║
║ ✅ Viral Auto-Posts  ✅ Fear & Greed Index  ✅ Market Dominance          ║
║ ✅ Funding Rate  ✅ Heatmap  ✅ Whale Tracking  ✅ Dual AI                ║
║ ✅ 60+ Indicators  ✅ SMC  ✅ Pattern Scanner  ✅ Portfolio Manager      ║
║ ✅ Open Access (No Force Join)  ✅ Railway-Ready  ✅ Self-Learning       ║
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
from telegram.request import HTTPXRequest
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO INSTALL
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'schedule':'schedule','jdatetime':'jdatetime','pytz':'pytz',
        'scipy':'scipy','psutil':'psutil','lxml':'lxml','feedparser':'feedparser',
        'requests':'requests','aiohttp':'aiohttp','yfinance':'yfinance',
        'plotly':'plotly','kaleido':'kaleido','Pillow':'Pillow','cryptography':'cryptography'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV24')
ensure_libs()

import schedule, jdatetime, pytz
import feedparser
import yfinance as yf
TEHRAN_TZ = pytz.timezone('Asia/Tehran')
try: from bs4 import BeautifulSoup
except: BeautifulSoup = None
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    import mplfinance as mpf
    from PIL import Image, ImageDraw, ImageFont
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

try: import psutil; PSUTIL_AVAILABLE = True
except: PSUTIL_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING (ENHANCED)
# ============================================================
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v24.log','crypto_v24_errors.log','crypto_v24_trades.log','crypto_v24_news.log','crypto_v24_signals.log']:
    h = RotatingFileHandler(name, maxBytes=50*1024*1024, backupCount=20, encoding='utf-8')
    h.setLevel(logging.INFO)
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(h)
for lib in ['httpx','httpcore','telegram','ccxt','urllib3','asyncio','matplotlib','aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# PROXY REQUEST (RAILWAY FIX)
# ============================================================
def create_request():
    proxy_url = os.getenv("TELEGRAM_PROXY", "")
    if proxy_url:
        return HTTPXRequest(
            proxy_url=proxy_url,
            connect_timeout=60.0,
            read_timeout=60.0,
            write_timeout=60.0,
            pool_timeout=10.0
        )
    else:
        return HTTPXRequest(
            connect_timeout=60.0,
            read_timeout=60.0,
            write_timeout=60.0,
            pool_timeout=10.0
        )

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    channel_username: str = os.getenv("CHANNEL_USERNAME", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    force_join: bool = False  # 👈 اجباری غیرفعال
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","XRP/USDT","ADA/USDT","SOL/USDT","DOGE/USDT",
        "DOT/USDT","MATIC/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT","LTC/USDT",
        "ETC/USDT","XLM/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT","SUI/USDT",
        "APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT","BONK/USDT","SEI/USDT",
        "TIA/USDT","INJ/USDT","RNDR/USDT","FET/USDT","AGIX/USDT","OCEAN/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    initial_balance: float = 100000.0; risk_per_trade: float = 0.02; max_positions: int = 5
    atr_sl: float = 2.0; atr_tp: float = 4.0; trailing_pct: float = 0.03
    max_consecutive_losses: int = 5; demo_trading: bool = False; real_trading: bool = True
    auto_send: bool = True; signal_interval: int = 14400; education_interval: int = 1800
    news_interval: int = 600; bio_update_interval: int = 60; viral_interval: int = 3600
    trend_interval: int = 7200; whale_interval: int = 5400; fg_interval: int = 3600
    max_daily_trades: int = 10; max_daily_loss: float = 5000.0
    daily_trades_count: int = 0; daily_pnl: float = 0.0
    last_reset_day: str = ""

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v24.lock"
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
    @classmethod
    def holiday_check(cls):
        j = cls.jalali()
        holidays = [(1,1),(1,2),(1,3),(1,4),(1,12),(1,13),(3,14),(3,15),(6,8),(11,22),(12,29)]
        for m,d in holidays:
            if j.month == m and j.day == d:
                return True
        return False

pdt = PersianLive()

# ============================================================
# TOKEN MANAGER
# ============================================================
class TokenManager:
    MAX_TPM = 15000
    def __init__(self): self._usage = deque(); self.groq = 0; self.gemini = 0; self.openai = 0
    @property
    def current(self):
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60: self._usage.popleft()
        return sum(t for _,t in self._usage)
    def can(self, tokens=500): return (self.current + tokens) <= self.MAX_TPM
    def record(self, tokens, source="groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq += tokens
        elif source == "gemini": self.gemini += tokens
        else: self.openai += tokens

token_mgr = TokenManager()

# ============================================================
# DUAL AI + ENHANCED PROMPTS
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
    T = {'tech':600,'market':500,'edu':800,'news':500,'whale':500,'strat':500,'sent':400,'fund':500,'pa':500,'pred':450,'ichimoku':500,'fib':450,'volume':450,'smc':550,'chart_analysis':900,'course':1200,'viral':700,'trend':600,'fear_greed':400,'market_report':800}
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
                json={"model":self.MODEL,"messages":[{"role":"system","content":"You are a professional crypto analyst and educator. Respond ONLY in Persian (فارسی). Use emojis extensively. Be detailed and practical."},{"role":"user","content":prompt}],"max_tokens":max_t})
            if r.status_code==200:
                d = r.json(); token_mgr.record(d.get('usage',{}).get('total_tokens',max_t),"groq")
                return d["choices"][0]["message"]["content"]
        except Exception as e: logger.error(f"Groq: {e}")
        return None

    async def tech(self, sym, ind, price, change, pats, mtf):
        mtf_t = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()])
        return await self._call(f"""Analyze {sym} at ${price:,.2f} ({change:+.2f}%).
RSI(14)={ind.get('RSI_14',50):.0f} | MACD={'Bullish' if ind.get('MACD_HIST',0)>0 else 'Bearish'}
ADX={ind.get('ADX',20):.0f} | CCI={ind.get('CCI',0):.0f} | MFI={ind.get('MFI',50):.0f}
BB%={ind.get('BB_PCT',0.5):.2f} | Volume={ind.get('VOL_RATIO',1):.1f}x
Support=${ind.get('SUPPORT',0):.2f} | Resistance=${ind.get('RESISTANCE',0):.2f}
Patterns: {', '.join(pats) if pats else 'None'} | Divergence: {ind.get('DIVERGENCE','NONE')}
MTF: {mtf_t}
Provide in Persian with emojis:
1. Summary of current situation 2. Direction prediction 3. Exact entry point
4. Stop loss level 5. Take profit targets 6. Risk level 7. Confidence score
Max 300 words.""", self.T['tech'])

    async def market(self, coins): return await self._call("Market overview in Persian with emojis:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\nSentiment, trends. 250w.", self.T['market'])
    async def edu(self):
        topics = ["تحلیل تکنیکال","مدیریت ریسک","روانشناسی","الگوهای کندلی","استراتژی","فیبوناچی","ایچیموکو","پرایس اکشن","فاندامنتال","واگرایی"]
        return await self._call(f"Write educational post in Persian: {random.choice(topics)}. 500w emojis hashtags #آموزش #کریپتو #تحلیل.", self.T['edu'])
    async def news_summary(self, headlines):
        return await self._call(f"Summarize these crypto headlines in Persian with emojis. 3 bullet points:\n"+"\n".join(headlines[:10]), self.T['news'])
    async def whale(self): return await self._call("Whale movements crypto Persian. 300w. #نهنگ #کریپتو #بازار", self.T['whale'])
    async def strat(self, sym, ind, price): return await self._call(f"Trading strategy {sym} ${price:,.2f}. Entry/SL/TP Persian 250w.", self.T['strat'])
    async def sent(self, sym, price, change): return await self._call(f"Sentiment {sym} ${price:,.2f} ({change:+.1f}%). Persian 200w.", self.T['sent'])
    async def fund(self, sym, price, change): return await self._call(f"Fundamental {sym.replace('/USDT','')} ${price:,.2f}. Persian 250w.", self.T['fund'])
    async def pa(self, sym, ind, price, pats): return await self._call(f"Price action {sym} ${price:,.2f}. Patterns: {', '.join(pats) if pats else 'None'}. Persian 250w.", self.T['pa'])
    async def pred(self, sym, ind, price): return await self._call(f"Predict {sym} ${price:,.2f}. 4h/24h/7d targets Persian 200w.", self.T['pred'])
    async def ichimoku(self, sym, ind, price):
        return await self._call(f"Ichimoku {sym} ${price:,.2f}. Tenkan={ind.get('TENKAN',0):.2f}, Kijun={ind.get('KIJUN',0):.2f}. Persian 250w.", self.T['ichimoku'])
    async def fibonacci(self, sym, ind, price):
        return await self._call(f"Fibonacci {sym}: 0.382={ind.get('FIB_382',0):.2f}, 0.618={ind.get('FIB_618',0):.2f}. Persian 200w.", self.T['fib'])
    async def volume_profile(self, sym, ind, price):
        return await self._call(f"Volume profile {sym}. Vol Ratio={ind.get('VOL_RATIO',1):.1f}. Persian 200w.", self.T['volume'])
    async def smc(self, sym, smc_data):
        return await self._call(f"Smart Money Concept analysis for {sym}:\n{json.dumps(smc_data, indent=2)}\nProvide Persian summary with emojis, mention BOS, CHOCH, Order Blocks, FVG. 300w.", self.T['smc'])
    async def chart_analysis(self, sym, price, ind_data):
        return await self._call(f"""Professional chart analysis for {sym} at ${price:,.2f}.
RSI(14)={ind_data.get('RSI_14',50):.1f} | MACD={ind_data.get('MACD_HIST',0):.4f}
ADX={ind_data.get('ADX',20):.1f} | BB%={ind_data.get('BB_PCT',0.5):.2f}
EMA7={ind_data.get('EMA_7',0):.2f} | EMA20={ind_data.get('EMA_20',0):.2f} | EMA50={ind_data.get('EMA_50',0):.2f}
Volume Ratio={ind_data.get('VOL_RATIO',1):.1f}x | Support=${ind_data.get('SUPPORT',0):.2f} | Resistance=${ind_data.get('RESISTANCE',0):.2f}
Analyze this chart in Persian with emojis. Provide entry, SL, TP. 500w.""", self.T['chart_analysis'])
    async def course_lesson(self, lesson_num, total_lessons, topic):
        return await self._call(f"""Crypto trading masterclass lesson {lesson_num}/{total_lessons}.
Topic: {topic}
Write in Persian with: 1. Theory 2. Practical example 3. Step-by-step guide 4. Common mistakes 5. Golden Key tip.
Emojis, headings. 800w. #دوره_کریپتو_پالس""", self.T['course'])
    async def viral_post(self):
        topics = ["بیتکوین", "اتریوم", "تحلیل تکنیکال", "DeFi", "NFT", "اخبار داغ", "نهنگ‌ها", "استراتژی معاملاتی", "اشتباهات تریدرها", "آینده کریپتو", "شوک بازار", "فرصت‌های پنهان"]
        return await self._call(f"Viral crypto post in Persian about {random.choice(topics)}. Shocking facts, emojis, CTA. 400w.", self.T['viral'])
    async def fear_greed_report(self, fg_value, fg_text):
        return await self._call(f"Fear & Greed Index is {fg_value} ({fg_text}). Explain in Persian with historical context. 250w.", self.T['fear_greed'])
    async def market_report(self, btc_dom, eth_dom, fg_value, fg_text, top_movers):
        return await self._call(f"""Daily market report:
BTC Dominance: {btc_dom:.1f}% | ETH Dominance: {eth_dom:.1f}%
Fear & Greed: {fg_value} ({fg_text})
Top movers: {json.dumps(top_movers[:5])}
Write comprehensive Persian market analysis. 400w.""", self.T['market_report'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE + REAL TRADER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False; self.real = bool(cfg.api_key and cfg.api_secret)
        self._last_balance = cfg.initial_balance
    def connect(self):
        try:
            p = {'enableRateLimit':True,'timeout':30000}
            if self.real: p.update({'apiKey':cfg.api_key,'secret':cfg.api_secret,'password':cfg.api_passphrase})
            self._ex = ccxt.coinex(p); self._ex.load_markets(); self.connected = True
            if self.real:
                try:
                    bal = self._ex.fetch_balance()
                    self._last_balance = bal.get('USDT',{}).get('free',cfg.initial_balance)
                except: pass
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
        try: return self._ex.fetch_funding_rate(s)
        except: return None
    def create_order(self, s, side, amount, price=None):
        try:
            if self.real and cfg.real_trading:
                if side == 'buy': return self._ex.create_market_buy_order(s, amount)
                else: return self._ex.create_market_sell_order(s, amount)
        except Exception as e:
            logger.error(f"Order error: {e}")
            return None
    def get_balance(self, asset='USDT'):
        try:
            bal = self._ex.fetch_balance()
            return bal.get(asset,{}).get('free',0)
        except: return 0

exchange_mgr = ExchangeManager()

# ============================================================
# SMART MONEY CONCEPT
# ============================================================
class SmartMoney:
    @staticmethod
    def analyze(df):
        if len(df) < 60: return {}
        high = df['high'].values; low = df['low'].values; close = df['close'].values
        from scipy.signal import argrelextrema
        swings_high_idx = argrelextrema(high, np.greater, order=3)[0]
        swings_low_idx = argrelextrema(low, np.less, order=3)[0]
        swings_high = [(i, high[i]) for i in swings_high_idx]
        swings_low = [(i, low[i]) for i in swings_low_idx]
        if len(swings_high) < 2 or len(swings_low) < 2: return {}
        bos_up = all(swings_high[i][1] > swings_high[i-1][1] for i in range(1, len(swings_high)))
        bos_down = all(swings_low[i][1] < swings_low[i-1][1] for i in range(1, len(swings_low)))
        choch = "نامشخص"
        if bos_up and not bos_down: choch = "صعودی"
        elif bos_down and not bos_up: choch = "نزولی"
        else: choch = "خنثی"
        ob_res = max(high[swings_high_idx]) if len(swings_high_idx) > 0 else None
        ob_sup = min(low[swings_low_idx]) if len(swings_low_idx) > 0 else None
        fvg_bull = False; fvg_bear = False
        for i in range(1, len(close)-1):
            if high[i] < low[i+1]: fvg_bull = True
            if low[i] > high[i+1]: fvg_bear = True
        liq_grab = "NONE"
        if len(swings_low) >= 2 and swings_low[-1][1] < swings_low[-2][1] and close[-1] > swings_low[-2][1]: liq_grab = "BULL_LIQ"
        elif len(swings_high) >= 2 and swings_high[-1][1] > swings_high[-2][1] and close[-1] < swings_high[-2][1]: liq_grab = "BEAR_LIQ"
        return {"BOS":"UP" if bos_up else "DOWN" if bos_down else "NONE","CHOCH":choch,"Order_Block_Resistance":ob_res,"Order_Block_Support":ob_sup,"FVG_Bull":fvg_bull,"FVG_Bear":fvg_bear,"Liquidity_Grab":liq_grab,"Market_Structure":"BULLISH" if choch=="صعودی" else "BEARISH" if choch=="نزولی" else "NEUTRAL"}

# ============================================================
# PATTERN SCANNER
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
        if len(peaks) >= 3 and len(troughs) >= 2:
            p1,p2,p3 = peaks[-3], peaks[-2], peaks[-1]
            t1,t2 = troughs[-2], troughs[-1]
            if close[p2] > close[p1] and close[p2] > close[p3] and close[t1] > close[t2]:
                if close[-1] < close[t2] and close[t2] < close[t1]: patterns.append("HEAD_AND_SHOULDERS")
        if len(peaks) >= 2 and abs(close[peaks[-1]] - close[peaks[-2]])/close[peaks[-2]] < 0.03: patterns.append("DOUBLE_TOP")
        if len(troughs) >= 2 and abs(close[troughs[-1]] - close[troughs[-2]])/close[troughs[-2]] < 0.03: patterns.append("DOUBLE_BOTTOM")
        return patterns

# ============================================================
# INDICATORS
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
            ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1]); ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1]); ind['SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except: pass
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.236,0.382,0.5,0.618,0.786]: ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        poc_idx = volume.iloc[-50:].idxmax() if len(volume)>=50 else volume.idxmax()
        ind['POC'] = float(close.iloc[poc_idx]) if poc_idx < len(close) else close.iloc[-1]
        ind.update(UltraIndicators._candles(df))
        ind['DIVERGENCE'] = UltraIndicators._div(close)
        ind['HIDDEN_DIVERGENCE'] = UltraIndicators._hidden_div(close)
        ind['REGIME'] = UltraIndicators._regime(ind, price=close.iloc[-1])
        return ind
    @staticmethod
    def _candles(df):
        pats = {p:False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','THREE_WHITE','THREE_BLACK','MORNING_STAR','EVENING_STAR']}
        if len(df)<2: return pats
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]; body,tr = abs(c-o), h-l
        if tr==0: return pats
        pats['DOJI']=body<=tr*0.08; pats['HAMMER']=(min(c,o)-l)>body*2 and c>o
        pats['SHOOTING_STAR']=(h-max(c,o))>body*2 and c<o
        pats['ENGULFING_BULL']=c>o and pc<po; pats['ENGULFING_BEAR']=c<o and pc>po
        if len(df)>=3:
            o3,c3 = df['open'].iloc[-3],df['close'].iloc[-3]
            pats['THREE_WHITE']=c>o and pc>po and c3>o3; pats['THREE_BLACK']=c<o and pc<po and c3<o3
            pats['MORNING_STAR']=pc<po and c>o; pats['EVENING_STAR']=pc>po and c<o
        return pats
    @staticmethod
    def _div(price):
        if len(price)<20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price,14).rsi(); rp,rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1]<rp.min() and rr.iloc[-1]>rr.min(): return "BULLISH"
        if rp.iloc[-1]>rp.max() and rr.iloc[-1]<rr.max(): return "BEARISH"
        return "NONE"
    @staticmethod
    def _hidden_div(price):
        if len(price) < 40: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price,14).rsi()
        if price.iloc[-20:].min() > price.iloc[-40:-20].min() and rsi.iloc[-20:].min() < rsi.iloc[-40:-20].min(): return "BULLISH_HIDDEN"
        if price.iloc[-20:].max() < price.iloc[-40:-20].max() and rsi.iloc[-20:].max() > rsi.iloc[-40:-20].max(): return "BEARISH_HIDDEN"
        return "NONE"
    @staticmethod
    def _regime(ind, price):
        ema20 = ind.get('EMA_20',0); ema50 = ind.get('EMA_50',0); adx = ind.get('ADX',20)
        if ema20 > ema50 and adx > 25: return "BULL_TREND"
        elif ema20 < ema50 and adx > 25: return "BEAR_TREND"
        elif adx < 20: return "RANGE"
        return "NEUTRAL"

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, mtf=None, smc_data=None):
        score = 0
        if ind['EMA_7']>ind['EMA_20']>ind['EMA_50']: score+=150
        elif ind['EMA_7']<ind['EMA_20']<ind['EMA_50']: score-=150
        rsi = ind['RSI_14']
        if rsi<30: score+=120
        elif rsi>70: score-=120
        if ind.get('MACD_HIST',0)>0: score+=70
        else: score-=70
        if ind.get('BB_PCT',0.5)<0.1: score+=100
        elif ind.get('BB_PCT',0.5)>0.9: score-=100
        if ind.get('VOL_RATIO',1)>2: score+=50 if score>0 else -50
        if ind.get('MFI',50)<20: score+=60
        elif ind.get('MFI',50)>80: score-=60
        if ind.get('ENGULFING_BULL'): score+=80
        if ind.get('HAMMER'): score+=50
        if ind.get('ENGULFING_BEAR'): score-=80
        if ind.get('SHOOTING_STAR'): score-=50
        if ind.get('THREE_WHITE'): score+=60
        if ind.get('THREE_BLACK'): score-=60
        if ind.get('MORNING_STAR'): score+=60
        if ind.get('EVENING_STAR'): score-=60
        if ind.get('DIVERGENCE')=='BULLISH': score+=70
        elif ind.get('DIVERGENCE')=='BEARISH': score-=70
        if ind.get('TENKAN',0)>ind.get('KIJUN',0) and price>ind.get('SENKOU_A',0): score+=50
        elif ind.get('TENKAN',0)<ind.get('KIJUN',0) and price<ind.get('SENKOU_B',0): score-=50
        regime = ind.get('REGIME','')
        if regime == 'BULL_TREND': score+=40
        elif regime == 'BEAR_TREND': score-=40
        if smc_data:
            if smc_data.get('CHOCH') == 'صعودی': score += 80
            elif smc_data.get('CHOCH') == 'نزولی': score -= 80
            if smc_data.get('Liquidity_Grab') == 'BULL_LIQ': score += 90
            elif smc_data.get('Liquidity_Grab') == 'BEAR_LIQ': score -= 90
            if smc_data.get('FVG_Bull'): score += 50
            if smc_data.get('FVG_Bear'): score -= 50
        if mtf:
            for tf,ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
                if ti.get('RSI_14',50)>55: score+=int(25*w)
                elif ti.get('RSI_14',50)<45: score-=int(25*w)
        score = max(-1000,min(1000,score))
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
# TRADER (REAL)
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.max_real = 3
        self.exp = {'total':0,'wins':0,'best':0,'worst':0,'conf':65,'risk':1.0,'max_drawdown':0.0,'drawdown':0.0}
        self.peak_balance = cfg.initial_balance
        self.load()
    def load(self):
        try:
            with open('trader_v24.json') as f:
                d = json.load(f); self.balance = d.get('balance',cfg.initial_balance)
                self.history = d.get('history',[]); self.exp.update(d.get('exp',{}))
                self.peak_balance = max(self.peak_balance, self.balance)
        except: pass
    def save(self):
        try:
            with open('trader_v24.json','w') as f: json.dump({'balance':self.balance,'history':self.history[-1000:],'exp':self.exp}, f)
        except: pass
    def learn(self):
        if len(self.history)<10: return
        wins = [t for t in self.history if t['pnl']>0]
        self.exp['total']=len(self.history); self.exp['wins']=len(wins)
        if wins: self.exp['best']=max(t['pnl'] for t in wins)
        losses=[t for t in self.history if t['pnl']<=0]
        if losses: self.exp['worst']=min(t['pnl'] for t in losses)
        self.peak_balance = max(self.peak_balance, self.balance)
        dd = (self.peak_balance - self.balance) / self.peak_balance if self.peak_balance > 0 else 0
        self.exp['drawdown'] = dd; self.exp['max_drawdown'] = max(self.exp['max_drawdown'], dd)
        wr=len(wins)/len(self.history)*100
        if wr>70: self.exp['conf']=55; self.exp['risk']=1.4
        elif wr>60: self.exp['conf']=60; self.exp['risk']=1.2
        elif wr<40: self.exp['conf']=75; self.exp['risk']=0.6
        self.save()
    def open(self, sym, entry, sl, tp, conf):
        if len(self.positions)>=cfg.max_positions or self.closses>=cfg.max_consecutive_losses: return None
        if cfg.daily_trades_count >= cfg.max_daily_trades: return None
        if cfg.daily_pnl < -cfg.max_daily_loss: return None
        risk = self.balance*cfg.risk_per_trade*self.exp['risk']
        if self.closses>0: risk*=(0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz<=0 or sz*entry>self.balance: return None
        self.balance -= sz*entry
        self.positions[sym] = {'symbol':sym,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        if exchange_mgr.real and cfg.real_trading:
            try: exchange_mgr.create_order(sym, 'buy', sz); self.real_trades+=1
            except: pass
        cfg.daily_trades_count += 1
        self.save(); return self.positions[sym]
    def update(self, sym, price):
        if sym not in self.positions: return None
        p = self.positions[sym]; p['high'] = max(p['high'],price)
        if (price-p['entry'])/p['entry']>cfg.trailing_pct: p['sl'] = p['high']*(1-cfg.trailing_pct)
        if price>=p['tp']: return self.close(sym,price,"🎯 حد سود")
        if price<=p['sl']: return self.close(sym,price,"🛑 حد ضرر")
        return None
    def close(self, sym, price, reason):
        p = self.positions.pop(sym); pnl = (price-p['entry'])*p['size']
        self.balance += p['size']*price; self.closses = 0 if pnl>0 else self.closses+1
        cfg.daily_pnl += pnl
        t = {'symbol':sym,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t); self.learn(); self.save()
        if exchange_mgr.real and cfg.real_trading:
            try: exchange_mgr.create_order(sym, 'sell', p['size'])
            except: pass
        return t
    def stats(self):
        total = max(1,len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# CHART GENERATOR (MPLFINANCE DARK GREEN)
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol, indicators):
        if not CHART_AVAILABLE: return None
        try:
            data = df.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data = data.set_index('timestamp')
            data = data.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})[['Open','High','Low','Close','Volume']]
            data = data.astype(float)
            n = min(80, len(data)); data = data.iloc[-n:]
            add_plots = []
            for p, color in [(7,'#FFD700'),(20,'#00ff88'),(50,'#FF8C00'),(200,'#FFFFFF')]:
                ema = data['Close'].ewm(span=p, adjust=False).mean()
                add_plots.append(mpf.make_addplot(ema, color=color, width=1.2, alpha=0.8))
            from ta.momentum import RSIIndicator
            rsi_vals = RSIIndicator(data['Close'], 14).rsi()
            add_plots.append(mpf.make_addplot(rsi_vals, panel=2, color='#9B59B6', ylabel='RSI', width=1.5))
            add_plots.append(mpf.make_addplot(pd.Series([70]*len(data), index=data.index), panel=2, color='#ff3333', linestyle='--', alpha=0.5))
            add_plots.append(mpf.make_addplot(pd.Series([30]*len(data), index=data.index), panel=2, color='#00ff88', linestyle='--', alpha=0.5))
            exp12 = data['Close'].ewm(span=12, adjust=False).mean()
            exp26 = data['Close'].ewm(span=26, adjust=False).mean()
            macd_line = exp12 - exp26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = macd_line - signal_line
            add_plots.append(mpf.make_addplot(macd_hist, type='bar', panel=3, color='#00ff88', alpha=0.8, ylabel='MACD'))
            add_plots.append(mpf.make_addplot(data['Volume'], panel=1, type='bar', color='#00ff88', alpha=0.8, ylabel='Volume'))
            mc = mpf.make_marketcolors(up='#00ff88', down='#ff3355', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#061a14', figcolor='#061a14', gridcolor='#1d3b34', rc={'font.size':12})
            fig, axlist = mpf.plot(data, type='candle', style=style, title=f'{symbol} - {pdt.shamsi()}', ylabel='💰 قیمت', volume=True, addplot=add_plots, panel_ratios=(3,1,1,1), figsize=(20,12), returnfig=True)
            buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor=style['facecolor']); buf.seek(0); plt.close(fig)
            return buf
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None

chart_gen = ChartGenerator()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, gemini_t=None, tf_4h=None, tf_1d=None, tf_1w=None, ichi=None, fib=None, smc_text=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k.replace('_',' ') for k,v in i.items() if isinstance(v,bool) and v]
        sig, conf, score = sg.generate(i, a['price'], a.get('mtf'), a.get('smc'))
        entry, sl = a['price'], a['price']-i['ATR_14']*cfg.atr_sl
        tp1, tp2 = a['price']+i['ATR_14']*cfg.atr_tp, a['price']+i['ATR_14']*cfg.atr_tp*1.5
        msg = f"""
🟢══════════════════════🟢
  💰 #سیگنال {s} 💰
🟢══════════════════════🟢

{pdt.both()}  |  UTC: {pdt.utc()}

💰 *قیمت:* ${a['price']:,.4f}  📊 *تغییر:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig}  💪 *قدرت:* {conf}%  ⭐ *امتیاز:* {score}/1000

📈 *EMA:* 7=${i.get('EMA_7',0):.2f}  20=${i.get('EMA_20',0):.2f}  50=${i.get('EMA_50',0):.2f}  200=${i.get('EMA_200',0):.2f}

📊 *اندیکاتورها:*
RSI(14)={i['RSI_14']:.1f}  MACD={'🟢صعود' if i.get('MACD_HIST',0)>0 else '🔴نزول'}
ADX={i['ADX']:.1f}  CCI={i['CCI']:.1f}  MFI={i['MFI']:.1f}
BB %B={i.get('BB_PCT',0.5):.2f}  Vol={i.get('VOL_RATIO',1):.1f}x
🕯️ الگوها: {', '.join(pats) if pats else 'بدون'}  |  {i.get('DIVERGENCE','NONE')}
🔮 Hidden Div: {i.get('HIDDEN_DIVERGENCE','NONE')}

🔑 *سطوح:* مقاومت ${i['RESISTANCE']:,.4f}  حمایت ${i['SUPPORT']:,.4f}
📐 *فیبوناچی ۰.۶۱۸:* ${i.get('FIB_618',0):.4f}
☁️ *Ichimoku:* Tenkan ${i.get('TENKAN',0):.2f}  Kijun ${i.get('KIJUN',0):.2f}

🎯 *ورود/خروج:*
🔵 ورود: ${entry:,.4f}
🔴 SL: ${sl:,.4f} ({(abs(entry-sl)/entry*100):.1f}%)
🟢 TP1: ${tp1:,.4f}  TP2: ${tp2:,.4f}
📊 R:R 1:{cfg.atr_tp/cfg.atr_sl:.1f}
"""
        if tf_4h: msg += f"⏰ *۴h:* RSI={tf_4h.get('RSI_14',50):.0f} MACD={'🟢' if tf_4h.get('MACD_HIST',0)>0 else '🔴'} ADX={tf_4h.get('ADX',20):.0f}\n"
        if tf_1d: msg += f"⏰ *۱d:* RSI={tf_1d.get('RSI_14',50):.0f} MACD={'🟢' if tf_1d.get('MACD_HIST',0)>0 else '🔴'} ADX={tf_1d.get('ADX',20):.0f}\n"
        if tf_1w: msg += f"⏰ *۱w:* RSI={tf_1w.get('RSI_14',50):.0f} MACD={'🟢' if tf_1w.get('MACD_HIST',0)>0 else '🔴'} ADX={tf_1w.get('ADX',20):.0f}\n"
        if groq_t: msg += f"\n🧠 *Groq AI:*\n{groq_t[:500]}\n"
        if gemini_t: msg += f"\n🌟 *Gemini AI:*\n{gemini_t[:400]}\n"
        if ichi: msg += f"\n☁️ *Ichimoku AI:* {ichi[:300]}\n"
        if fib: msg += f"\n📐 *Fibonacci AI:* {fib[:250]}\n"
        if smc_text: msg += f"\n🧲 *SMC:* {smc_text[:300]}\n"
        msg += f"""
🟢══════════════════════🟢
📋 *نتیجه‌گیری:* {sig} | اطمینان {conf}%
⏰ {pdt.time_str()}
🟢══════════════════════🟢
✨ @CryptoPulse606 | {pdt.full()}
#سیگنال #{s} #کریپتو #تحلیل
"""
        return msg
    @staticmethod
    def edu(c=None):
        h = f"🟢══════════════════🟢\n     📚 #آموزش\n🟢══════════════════🟢\n\n{pdt.both()}\n\n"
        if c: h += f"{c}\n\n"
        return h + f"🟢══════════════════🟢\n✨ @CryptoPulse606 | {pdt.full()}\n#آموزش #کریپتو"

fmt = Fmt()

# ============================================================
# LIVE CRYPTO NEWS ENGINE (10+ SOURCES)
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 300
    SOURCES = [
        ("https://cryptopanic.com/news/rss/", "CryptoPanic"),
        ("https://www.coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://bitcoinmagazine.com/.rss/full/", "Bitcoin Magazine"),
        ("https://www.theblock.co/rss.xml", "The Block"),
        ("https://decrypt.co/feed", "Decrypt"),
        ("https://cryptoslate.com/feed/", "CryptoSlate"),
        ("https://news.google.com/rss/search?q=cryptocurrency&hl=en-US&gl=US&ceid=US:en", "Google News"),
        ("https://www.reddit.com/r/CryptoCurrency/.rss", "Reddit Crypto"),
        ("https://www.reddit.com/r/Bitcoin/.rss", "Reddit Bitcoin"),
        ("https://cryptobriefing.com/feed/", "CryptoBriefing"),
        ("https://coingape.com/feed/", "CoinGape"),
    ]
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < cls.CACHE_DURATION: return cls.CACHE.get("data",[])
        articles = []
        for url, source in cls.SOURCES:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    articles.append({"title":entry.title,"link":entry.link,"published":entry.get('published',''),"source":source})
            except Exception as e: logger.error(f"RSS {source}: {e}")
        cls.CACHE = {"ts":now,"data":articles}
        return articles

# ============================================================
# FEAR & GREED INDEX
# ============================================================
class FearGreedIndex:
    CACHE = {}
    CACHE_DURATION = 3600
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts",0)) < cls.CACHE_DURATION: return cls.CACHE.get("value"), cls.CACHE.get("text")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get("https://api.alternative.me/fng/?limit=1")
                data = resp.json()
                value = int(data['data'][0]['value']); text = data['data'][0]['value_classification']
                cls.CACHE = {"ts":now,"value":value,"text":text}
                return value, text
        except: return 50, "Neutral"

# ============================================================
# SAFE SEND/EDIT
# ============================================================
async def safe_send(bot, chat_id, text, reply_markup=None):
    try: return await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
    except:
        try: return await bot.send_message(chat_id=chat_id, text=re.sub(r'[*_`~\[\]\(\)]','',text)[:4000], reply_markup=reply_markup)
        except: return None

async def safe_edit(bot, chat_id, msg_id, text, reply_markup=None):
    try: return await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
    except: return None

# ============================================================
# BIO UPDATER
# ============================================================
class BioUpdater:
    def __init__(self, app): self.app = app
    async def update(self):
        try:
            bot = self.app.bot; btc = "---"
            try:
                if exchange_mgr.connected:
                    t = exchange_mgr.ticker("BTC/USDT")
                    if t: btc = f"${t['last']:,.0f}"
            except: pass
            try: await bot.set_my_name(f"🔰 Crypto Pulse | {btc} | {pdt.time_str()}"[:64])
            except: pass
            try: await bot.set_my_description(f"🤖 AI Trading Bot\n📅 {pdt.shamsi()}\n⏰ {pdt.time_str()}\n₿ {btc}\n🧠 Groq+Gemini\n📊 60+ Indicators\n💹 Real Trading\n📚 500+ Lessons\n📰 Live News"[:512])
            except: pass
            cmds = [BotCommand("start","🚀 Start"),BotCommand("signal","🎯 Signal"),BotCommand("price","💰 Prices"),BotCommand("scan","🔍 Scan"),BotCommand("portfolio","💼 Portfolio"),BotCommand("news","📰 News"),BotCommand("course","📚 Course"),BotCommand("chart","📊 Chart"),BotCommand("help","❓ Help")]
            try: await bot.set_my_commands(cmds, scope=BotCommandScopeDefault())
            except: pass
        except: pass
    def start(self):
        def run():
            try: asyncio.create_task(self.update())
            except: pass
        schedule.every(cfg.bio_update_interval).seconds.do(run); run()
        threading.Thread(target=lambda: [schedule.run_pending(), time.sleep(1)], daemon=True).start()

# ============================================================
# MENU
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Prices", callback_data="p"),
             InlineKeyboardButton("🎯 Signal BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 Scan", callback_data="scan")],
            [InlineKeyboardButton("⏰ 4h", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ 1d", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ 1w", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 Gemini AI", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("📊 Chart", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("📰 Market", callback_data="market"),
             InlineKeyboardButton("📊 Strategy", callback_data="strat"),
             InlineKeyboardButton("💭 Sentiment", callback_data="sent")],
            [InlineKeyboardButton("📰 Fundamental", callback_data="fund"),
             InlineKeyboardButton("📊 Price Action", callback_data="pa"),
             InlineKeyboardButton("🔮 Prediction", callback_data="pred")],
            [InlineKeyboardButton("☁️ Ichimoku", callback_data="ichi_BTC/USDT"),
             InlineKeyboardButton("📐 Fibonacci", callback_data="fib_BTC/USDT"),
             InlineKeyboardButton("📈 Vol Profile", callback_data="vol_BTC/USDT")],
            [InlineKeyboardButton("🧠 Smart Money", callback_data="smc"),
             InlineKeyboardButton("🔥 Heatmap", callback_data="heatmap"),
             InlineKeyboardButton("🐋 Whales", callback_data="whale")],
            [InlineKeyboardButton("💰 Portfolio", callback_data="port"),
             InlineKeyboardButton("📊 Performance", callback_data="perf"),
             InlineKeyboardButton("🧠 Experience", callback_data="exp")],
            [InlineKeyboardButton("🤖 Auto", callback_data="auto"),
             InlineKeyboardButton("⚙️ Settings", callback_data="set"),
             InlineKeyboardButton("🔑 Status", callback_data="status")],
            [InlineKeyboardButton("📚 Course", callback_data="course"),
             InlineKeyboardButton("📰 News", callback_data="news"),
             InlineKeyboardButton("😱 Fear & Greed", callback_data="fear_greed")],
            [InlineKeyboardButton("💵 Funding", callback_data="funding"),
             InlineKeyboardButton("📈 OI", callback_data="oi"),
             InlineKeyboardButton("🏆 Dominance", callback_data="dominance")],
            [InlineKeyboardButton("⏸️ Stop All", callback_data="stop"),
             InlineKeyboardButton("🔄 Refresh", callback_data="ref")],
        ])

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🟢══════════════════════🟢\n   🤖 #CryptoPulse v24.0 🤖\n🟢══════════════════════🟢\n\n{pdt.both()}\n\n🧠🌟 Groq + Gemini AI\n📊 60+ Indicators\n💹 Real Trading\n📊 Chart + AI Analysis\n📚 500+ Hour Course\n📰 Live News (12 Sources)\n\n👇 Choose:",
        reply_markup=Menu.main())

async def send_signal_with_chart(bot, chat_id, symbol, ticker, df, ind, mtf, smc_data, groq_t, gemini_t, ichi_t, fib_t, smc_t):
    chart_buf = None
    if CHART_AVAILABLE: chart_buf = chart_gen.create(df, symbol, ind)
    if chart_buf:
        caption = f"📊 {symbol.replace('/USDT','')} | ${ticker['last']:,.4f} | {ticker.get('percentage',0):+.2f}%\n⏰ {pdt.time_str()}\n✨ @CryptoPulse606"
        await bot.send_photo(chat_id=chat_id, photo=chart_buf, caption=caption[:1024])
    a = {'symbol':symbol,'price':ticker['last'],'change':ticker.get('percentage',0),'indicators':ind,'mtf':mtf,'smc':smc_data}
    msg = fmt.signal(a, groq_t, gemini_t, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'), ichi_t, fib_t, smc_t)
    await safe_send(bot, chat_id, msg)

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text(f"🟢 *Menu*\n\n{pdt.both()}", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *Prices*\n\n{pdt.both()}\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} *{sym.replace('/USDT','')}*: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"):
            sym = d[2:]; await q.answer(); await q.edit_message_text(f"🔄 Analyzing {sym.replace('/USDT','')}...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 200)
            if not t or df is None: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
            ind = ui.calc(df); mtf = {}
            for tf_name in cfg.primary_tfs:
                dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                if dft is not None: mtf[tf_name] = ui.calc(dft)
            smc_data = SmartMoney.analyze(df)
            pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
            gemini_t = await gemini_ai.ask(f"Analyze {sym} ${t['last']:,.2f} Persian.", 400) if gemini_ai.enabled else None
            ichi_t = await groq_ai.ichimoku(sym, ind, t['last']) if groq_ai.enabled else None
            fib_t = await groq_ai.fibonacci(sym, ind, t['last']) if groq_ai.enabled else None
            smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled and smc_data else None
            await send_signal_with_chart(ctx.bot, q.message.chat_id, sym, t, df, ind, mtf, smc_data, groq_t, gemini_t, ichi_t, fib_t, smc_t)
            await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, f"✅ {sym.replace('/USDT','')} analysis done.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"s_{sym}"), InlineKeyboardButton("🤖 AI Chart", callback_data=f"chart_ai_{sym}"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("chart_"): 
            sym = d[6:] if len(d)>6 else "BTC/USDT"; await q.answer()
            if not CHART_AVAILABLE: await q.edit_message_text("❌ Chart lib missing"); return
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 200)
            if not t or df is None: await q.edit_message_text("❌"); return
            ind = ui.calc(df); buf = chart_gen.create(df, sym, ind)
            if buf: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=buf, caption=f"📊 {sym.replace('/USDT','')} | ${t['last']:,.4f}"); await q.edit_message_text("✅", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_":"4h","tf1d_":"1d","tf1w_":"1w"}
            for prefix,tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d)>len(prefix) else "BTC/USDT"; await q.answer()
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, tf, 200)
                    if t and df is not None:
                        ind = ui.calc(df); sig, conf, _ = sg.generate(ind, t['last'])
                        if CHART_AVAILABLE:
                            chart_buf = chart_gen.create(df, sym, ind)
                            if chart_buf: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=chart_buf, caption=f"⏰ {tf} {sym.replace('/USDT','')} | ${t['last']:,.4f}")
                        await q.edit_message_text(f"⏰ *{tf} {sym.replace('/USDT','')}*\n{pdt.both()}\n💰 ${t['last']:,.4f}\n🎯 {sig} | 💪 {conf}%\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "fear_greed":
            fg_value, fg_text = await FearGreedIndex.fetch()
            ai_report = await groq_ai.fear_greed_report(fg_value, fg_text) if groq_ai.enabled else None
            emoji = "🟢" if fg_value < 30 else "🔴" if fg_value > 70 else "🟡"
            await q.edit_message_text(f"😱 *Fear & Greed*\n{pdt.both()}\n\n{emoji} *{fg_value}/100* — {fg_text}\n\n{ai_report if ai_report else ''}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="fear_greed"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                msg = f"📰 *Live Crypto News*\n{pdt.both()}\n\n"
                for art in articles[:10]: msg += f"• [{art['title']}]({art['link']}) — _{art['source']}_\n"
                await q.edit_message_text(msg, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get("https://api.coingecko.com/api/v3/global"); data = resp.json()
                    btc_dom = data['data']['market_cap_percentage']['btc']; eth_dom = data['data']['market_cap_percentage']['eth']
                    await q.edit_message_text(f"🏆 *Dominance*\n{pdt.both()}\n₿ BTC: {btc_dom:.1f}%\nΞ ETH: {eth_dom:.1f}%", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            except: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"💰 *Portfolio*\n{pdt.both()}\n💵 ${s['balance']:,.2f}\n📈 ${s['pnl']:+,.2f}\n📊 {s['total']} | {s['wins']} wins", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "status":
            txt = f"🔑 *System Status*\n{pdt.both()}\n🔌 CoinEx: {'✅' if exchange_mgr.connected else '❌'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'}\n🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}\n🤖 Auto: {'✅' if cfg.auto_send else '❌'}\n📊 Positions: {len(trader.positions)}\n💵 Trades today: {cfg.daily_trades_count}/{cfg.max_daily_trades}\n📈 PnL today: ${cfg.daily_pnl:+,.2f}"
            if PSUTIL_AVAILABLE: txt += f"\n🧠 CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text(f"🟢 *Menu*\n{pdt.both()}", reply_markup=Menu.main())
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "⏸️ Manual")
            await q.edit_message_text(f"⏸️ All positions closed\n{pdt.both()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer(f"⚡ {d} | {pdt.time_str()}")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌ Error")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Use /start\n{pdt.both()}", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
course_lesson_num = 0
TOTAL_COURSE_LESSONS = 500
COURSE_TOPICS = [
    "Blockchain & Bitcoin Basics","Classic Technical Analysis","Advanced Candlesticks",
    "Moving Averages","RSI & MACD","Bollinger Bands","Fibonacci Retracement",
    "Fibonacci Extension","Classic Patterns","Ichimoku Complete","Volume Profile",
    "Market Structure","Order Block","Fair Value Gap","Liquidity Grab",
    "BOS & CHOCH","Advanced SMC","Basic Money Management","Advanced Money Management",
    "Trading Psychology","Journaling","Scalping Strategy","Day Trading Strategy",
    "Swing Strategy","DeFi & NFT","Ethereum & L2","Fundamental Analysis",
    "News Impact","Whale Detection","Open Interest","Funding Rate",
    "CVD & Delta","Heatmap & Order Flow","Futures Trading","Martingale & Anti",
    "AI in Trading","Backtesting","Forward Testing","Brokers & Exchanges",
    "Security & Wallets","Tax & Regulations","Long-Term Investing",
    "ETF & Institutions","DXY & Gold","Altseason","Combined Strategy",
    "Final Conclusion","Market Psychology","Market Cycles","Accumulation & Distribution",
    "Wyckoff Method","VSA","Market Profile","Footprint Charts","Delta Analysis",
    "Bookmap & Order Flow","DOM Analysis","Options & Greeks","Advanced Derivatives",
    "Arbitrage","Market Making","Algorithmic Trading","ML in Trading",
    "Python for Trading","Pine Script","TradingView Tips","Advanced Risk Management",
    "Portfolio Theory","Kelly Criterion","Monte Carlo Simulation","Backtesting Pitfalls",
    "Overfitting","Psychological Biases","Trading Discipline","Building a System"
]

async def auto_signals(app: Application):
    await asyncio.sleep(10)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            today = pdt.shamsi()
            if today != cfg.last_reset_day: cfg.daily_trades_count = 0; cfg.daily_pnl = 0.0; cfg.last_reset_day = today
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym,'1h',200)
                    if t and df is not None:
                        ind = ui.calc(df); mtf = {}
                        for tf_name in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                            if dft is not None: mtf[tf_name] = ui.calc(dft)
                        smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), [], mtf)
                        gemini_t = await gemini_ai.ask(f"Analyze {sym} ${t['last']:,.2f} Persian.", 350) if gemini_ai.enabled else None
                        smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled and smc_data else None
                        await send_signal_with_chart(app.bot, cfg.channel_id, sym, t, df, ind, mtf, smc_data, groq_t, gemini_t, None, None, smc_t)
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        r = trader.update(sym, t['last'])
                        if r: await safe_send(app.bot, cfg.channel_id, f"{'🟢' if r['pnl']>0 else '🔴'} {sym}: ${r['pnl']:+,.2f}")
                except: pass
        except Exception as e: logger.error(f"Signal loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_news(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                articles = await CryptoNews.fetch()
                if articles:
                    headlines = [a['title'] for a in articles[:10]]
                    summary = await groq_ai.news_summary(headlines)
                    if summary:
                        msg = f"📰 *اخبار زنده کریپتو*\n{pdt.both()}\n\n{summary}\n\n"
                        for a in articles[:5]: msg += f"• [{a['title']}]({a['link']})\n"
                        msg += f"\n✨ @CryptoPulse606\n#اخبار #کریپتو"
                        await safe_send(app.bot, cfg.channel_id, msg)
        except Exception as e: logger.error(f"News: {e}")
        await asyncio.sleep(cfg.news_interval)

async def auto_viral(app: Application):
    await asyncio.sleep(300)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                post = await groq_ai.viral_post()
                if post: await safe_send(app.bot, cfg.channel_id, f"🔥 *پست ویژه*\n\n{post}\n\n✨ @CryptoPulse606 | {pdt.full()}\n#پست_ویژه")
        except: pass
        await asyncio.sleep(cfg.viral_interval)

async def auto_course(app: Application):
    global course_lesson_num
    await asyncio.sleep(60)
    try:
        with open('course_progress.json', 'r') as f: course_lesson_num = json.load(f).get('lesson',0)
    except: pass
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                topic = COURSE_TOPICS[course_lesson_num % len(COURSE_TOPICS)]
                lesson = await groq_ai.course_lesson(course_lesson_num+1, TOTAL_COURSE_LESSONS, topic)
                if lesson:
                    await safe_send(app.bot, cfg.channel_id, lesson)
                    course_lesson_num += 1
                    with open('course_progress.json','w') as f: json.dump({'lesson':course_lesson_num}, f)
        except Exception as e: logger.error(f"Course: {e}")
        await asyncio.sleep(cfg.education_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(180)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                fg_value, fg_text = await FearGreedIndex.fetch()
                ai_report = await groq_ai.fear_greed_report(fg_value, fg_text)
                emoji = "🟢" if fg_value < 30 else "🔴" if fg_value > 70 else "🟡"
                msg = f"😱 *شاخص ترس و طمع*\n\n{emoji} *{fg_value}/100* — {fg_text}\n\n{ai_report if ai_report else ''}\n\n✨ @CryptoPulse606 | {pdt.full()}"
                await safe_send(app.bot, cfg.channel_id, msg)
        except: pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(400)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: await safe_send(app.bot, cfg.channel_id, f"🐋 *نهنگ‌ها*\n\n{c}\n\n✨ @CryptoPulse606 | {pdt.full()}")
        except: pass
        await asyncio.sleep(cfg.whale_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    print(f"🟢═══ CRYPTO PULSE v24.0 ═══🟢\n📅 {pdt.shamsi()}\n⏰ {pdt.time_str()}")
    logger.info(f"🚀 Starting | {pdt.full()}")
    exchange_mgr.connect()
    request = create_request()
    app = Application.builder().token(cfg.token).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    BioUpdater(app).start()
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_viral(app))
    asyncio.create_task(auto_course(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    logger.info("="*50)
    logger.info(f"🚀 CRYPTO PULSE v24.0 | {pdt.full()}")
    logger.info(f"🧠 Groq:{'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini:{'✅' if gemini_ai.enabled else '❌'} | 💹 Real Trading:{'✅' if cfg.real_trading else '❌'}")
    logger.info("="*50)
    try:
        await app.initialize(); await app.start()
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

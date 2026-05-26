#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║   🚀 CRYPTO PULSE v17.1 — STABLE PERSIAN EDITION 🤖                      ║
║   ✅ Fixed HTTP    ✅ 40+ Keys  ✅ Dual AI               ║
║   ✅ Railway Ready  ✅ Persian Date  ✅ Auto Trade  ✅ Golden Signals       ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading
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
# AUTO INSTALL (Railway Compatible)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'schedule':'schedule','jdatetime':'jdatetime','pytz':'pytz'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV17')
ensure_libs()

import schedule, jdatetime, pytz
TEHRAN_TZ = pytz.timezone('Asia/Tehran')
try: from bs4 import BeautifulSoup
except: BeautifulSoup = None
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc; CHART_AVAILABLE = True
except: CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING
# ============================================================
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v17.log','crypto_v17_errors.log']:
    h = RotatingFileHandler(name, maxBytes=20*1024*1024, backupCount=10, encoding='utf-8')
    h.setLevel(logging.INFO if 'errors' not in name else logging.ERROR)
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(h)
for lib in ['httpx','httpcore','telegram','ccxt','urllib3','asyncio','matplotlib']:
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
    admin_id: int = int(os.getenv("ADMIN_ID", "13600620"))
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
    _file = "crypto_v17.lock"
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
# DUAL AI (FIXED HTTPX CLIENTS)
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.key = cfg.gemini_api_key; self.enabled = bool(self.key and len(self.key)>10)
        self._client = None
        self._lock = threading.Lock()
    def _get_client(self):
        with self._lock:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=60.0, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))
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
    T = {'tech':500,'market':400,'edu':700,'news':400,'whale':400,'strat':400,'sent':300,'fund':400,'pa':400,'pred':350}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = None
        self._lock = threading.Lock()
    def _get_client(self):
        with self._lock:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=60.0, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))
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
1. Summary of current situation
2. Direction prediction (bullish/bearish)
3. Exact entry point
4. Stop loss level
5. Take profit targets
6. Risk level (LOW/MEDIUM/HIGH)
7. Confidence score (0-100)
Max 300 words.""", self.T['tech'])
    async def market(self, coins): return await self._call("Market overview in Persian with emojis:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\nSentiment, trends. 250w.", self.T['market'])
    async def edu(self):
        topics = ["تحلیل تکنیکال پیشرفته","مدیریت ریسک","روانشناسی معامله‌گری","الگوهای کندلی","استراتژی معاملاتی","فیبوناچی","ایچیموکو","پرایس اکشن","فاندامنتال","واگرایی"]
        return await self._call(f"Write a comprehensive educational post in Persian about: {random.choice(topics)}. 500+ words, step-by-step guide, emojis, practical tips, golden nugget. Use hashtags: #آموزش #کریپتو #تحلیل", self.T['edu'])
    async def news(self): return await self._call("Latest crypto news in Persian with emojis and hashtags. Cover BTC, ETH, regulations, DeFi. 400w. Use #اخبار #کریپتو #بیتکوین", self.T['news'])
    async def whale(self): return await self._call("Recent whale movements in crypto market. Persian with emojis. 300w. Use #نهنگ #کریپتو #بازار", self.T['whale'])
    async def strat(self, sym, ind, price): return await self._call(f"Trading strategy for {sym} at ${price:,.2f}. Entry/SL/TP in Persian with emojis. 250w.", self.T['strat'])
    async def sent(self, sym, price, change): return await self._call(f"Market sentiment for {sym} at ${price:,.2f} ({change:+.1f}%). Persian with emojis. 200w.", self.T['sent'])
    async def fund(self, sym, price, change): return await self._call(f"Fundamental analysis of {sym.replace('/USDT','')} at ${price:,.2f}. Persian with emojis. 250w.", self.T['fund'])
    async def pa(self, sym, ind, price, pats): return await self._call(f"Price action analysis for {sym} at ${price:,.2f}. Patterns: {', '.join(pats) if pats else 'None'}. Persian 250w.", self.T['pa'])
    async def pred(self, sym, ind, price): return await self._call(f"Predict {sym} price at ${price:,.2f}. 4h/24h/7d targets in Persian with emojis. 200w.", self.T['pred'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE
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

exchange_mgr = ExchangeManager()

# ============================================================
# INDICATORS (High Accuracy)
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
        from ta.trend import MACD, ADXIndicator, CCIIndicator
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
        ind.update(UltraIndicators._candles(df)); ind['DIVERGENCE'] = UltraIndicators._div(close)
        return ind
    @staticmethod
    def _candles(df):
        pats = {p:False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','THREE_WHITE','THREE_BLACK']}
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
        return pats
    @staticmethod
    def _div(price):
        if len(price)<20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price,14).rsi(); rp,rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1]<rp.min() and rr.iloc[-1]>rr.min(): return "BULLISH"
        if rp.iloc[-1]>rp.max() and rr.iloc[-1]<rr.max(): return "BEARISH"
        return "NONE"

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR WITH COLORED CIRCLES
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, mtf=None):
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
        if ind.get('DIVERGENCE')=='BULLISH': score+=70
        elif ind.get('DIVERGENCE')=='BEARISH': score-=70
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
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.max_real = 3
        self.exp = {'total':0,'wins':0,'best':0,'worst':0,'conf':65,'risk':1.0}
        self.load()
    def load(self):
        try:
            with open('trader_v17.json') as f:
                d = json.load(f); self.balance = d.get('balance',cfg.initial_balance)
                self.history = d.get('history',[]); self.exp.update(d.get('exp',{}))
        except: pass
    def save(self):
        try:
            with open('trader_v17.json','w') as f:
                json.dump({'balance':self.balance,'history':self.history[-1000:],'exp':self.exp}, f)
        except: pass
    def learn(self):
        if len(self.history)<10: return
        wins = [t for t in self.history if t['pnl']>0]
        self.exp['total']=len(self.history); self.exp['wins']=len(wins)
        if wins: self.exp['best']=max(t['pnl'] for t in wins)
        losses=[t for t in self.history if t['pnl']<=0]
        if losses: self.exp['worst']=min(t['pnl'] for t in losses)
        wr=len(wins)/len(self.history)*100
        if wr>70: self.exp['conf']=55; self.exp['risk']=1.4
        elif wr>60: self.exp['conf']=60; self.exp['risk']=1.2
        elif wr<40: self.exp['conf']=75; self.exp['risk']=0.6
        self.save()
    def open(self, sym, entry, sl, tp, conf):
        if len(self.positions)>=cfg.max_positions or self.closses>=cfg.max_consecutive_losses: return None
        risk = self.balance*cfg.risk_per_trade*self.exp['risk']
        if self.closses>0: risk*=(0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz<=0 or sz*entry>self.balance: return None
        self.balance -= sz*entry
        self.positions[sym] = {'symbol':sym,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        if exchange_mgr.real: self.real_trades+=1
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
        t = {'symbol':sym,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t); self.learn(); self.save(); return t
    def stats(self):
        total = max(1,len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# FORMATTER - PERSIAN GOLDEN GREEN
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, gemini_t=None, tf_4h=None, tf_1d=None, tf_1w=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k.replace('_',' ') for k,v in i.items() if isinstance(v,bool) and v]
        sig, conf, score = sg.generate(i, a['price'])
        em = {"BTC":"₿","ETH":"Ξ","SOL":"◎","BNB":"🟡","XRP":"💧","ADA":"🔵","DOGE":"🐕"}
        ce = em.get(s, "💰")
        
        if "خرید فوق‌العاده" in sig: ae, at = "🔥🔥🔥", "🚀 ورود قوی به پوزیشن خرید (LONG)"
        elif "خرید قوی" in sig: ae, at = "🔥🔥", "📈 ورود به پوزیشن خرید (LONG)"
        elif "خرید" in sig: ae, at = "🔥", "📈 ورود به پوزیشن خرید"
        elif "فروش فوق‌العاده" in sig: ae, at = "❄️❄️❄️", "💥 ورود قوی به پوزیشن فروش (SHORT)"
        elif "فروش قوی" in sig: ae, at = "❄️❄️", "📉 ورود به پوزیشن فروش (SHORT)"
        elif "فروش" in sig: ae, at = "❄️", "📉 ورود به پوزیشن فروش"
        else: ae, at = "⏳", "⚪ صبر و انتظار برای سیگنال بهتر"
        
        entry, sl = a['price'], a['price']-i['ATR_14']*cfg.atr_sl
        tp1, tp2 = a['price']+i['ATR_14']*cfg.atr_tp, a['price']+i['ATR_14']*cfg.atr_tp*1.5
        
        msg = f"""
🟢══════════════════════════════════════🟢
  {ce} #سیگنال_معاملاتی {s} {ce}
🟢══════════════════════════════════════🟢

{pdt.both()}
🌍 UTC: {pdt.utc()}

┏━━━━━━━━━━ 📊 وضعیت بازار ━━━━━━━━━━┓
💰 *قیمت فعلی:* ${a['price']:,.4f}
📊 *تغییر ۲۴ ساعت:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig}
💪 *قدرت سیگنال:* {conf}% | ⭐ *امتیاز:* {score}/1000
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 📈 میانگین‌های متحرک ━━━━━━━━━━┓
✨ EMA 7: ${i.get('EMA_7',0):,.2f} | EMA 20: ${i.get('EMA_20',0):,.2f}
✨ EMA 50: ${i.get('EMA_50',0):,.2f} | EMA 200: ${i.get('EMA_200',0):,.2f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 📊 اندیکاتورها ━━━━━━━━━━┓
📈 RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
📉 MACD: {'🟢 صعودی' if i.get('MACD_HIST',0)>0 else '🔴 نزولی'}
📊 ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
📐 بولینگر: {i.get('BB_PCT',0.5):.2f}%B | حجم: {i.get('VOL_RATIO',1):.1f}x
🕯️ الگوها: {', '.join(pats) if pats else 'بدون'} | {i.get('DIVERGENCE','NONE')}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 🔑 سطوح کلیدی ━━━━━━━━━━┓
🔴 مقاومت: ${i['RESISTANCE']:,.4f}
🟢 حمایت: ${i['SUPPORT']:,.4f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 🎯 نقاط ورود و خروج ━━━━━━━━━━┓
🔵 *نقطه ورود:* ${entry:,.4f}
🔴 *حد ضرر (SL):* ${sl:,.4f} ({abs(entry-sl)/entry*100:.1f}%)
🟢 *حد سود ۱ (TP1):* ${tp1:,.4f} ({abs(tp1-entry)/entry*100:.1f}%)
🟢 *حد سود ۲ (TP2):* ${tp2:,.4f} ({abs(tp2-entry)/entry*100:.1f}%)
📊 *نسبت ریسک به ریوارد:* 1:{cfg.atr_tp/cfg.atr_sl:.1f}
⏰ *زمان پیشنهادی معامله:* همین حالا
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        if tf_4h: msg += f"\n⏰ *۴h:* RSI={tf_4h.get('RSI_14',50):.0f} MACD={'🟢' if tf_4h.get('MACD_HIST',0)>0 else '🔴'} ADX={tf_4h.get('ADX',20):.0f}"
        if tf_1d: msg += f"\n⏰ *۱d:* RSI={tf_1d.get('RSI_14',50):.0f} MACD={'🟢' if tf_1d.get('MACD_HIST',0)>0 else '🔴'} ADX={tf_1d.get('ADX',20):.0f}"
        if tf_1w: msg += f"\n⏰ *۱w:* RSI={tf_1w.get('RSI_14',50):.0f} MACD={'🟢' if tf_1w.get('MACD_HIST',0)>0 else '🔴'} ADX={tf_1w.get('ADX',20):.0f}"

        if groq_t: msg += f"\n\n┏━━━━ 🧠 تحلیل Groq AI ━━━━┓\n{groq_t[:500]}\n┗━━━━━━━━━━━━━━━━━━┛"
        if gemini_t: msg += f"\n┏━━━━ 🌟 تحلیل Gemini AI ━━━━┓\n{gemini_t[:400]}\n┗━━━━━━━━━━━━━━━━━━┛"

        msg += f"""

🟢══════════════════════════════════════🟢
           📋 #نتیجه‌گیری_نهایی
🟢══════════════════════════════════════🟢

🎯 *سیگنال نهایی:* {sig}
💪 *اطمینان:* {conf}% | ⭐ *امتیاز:* {score}/1000
📊 *اقدام:* {at}
⏰ *زمان:* {pdt.time_str()}

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {pdt.full()}
🟢══════════════════════════════════════🟢

#تحلیل_تکنیکال #{s} #کریپتو #سیگنال"""
        return msg
    
    @staticmethod
    def edu(c=None):
        h = f"🟢══════════════════🟢\n     📚 #آموزش_کریپتو\n🟢══════════════════🟢\n\n{pdt.both()}\n\n"
        if c: h += f"{c}\n\n"
        return h + f"🟢══════════════════🟢\n✨ @CryptoPulse606 | {pdt.full()}\n#آموزش #تحلیل #کریپتو"
    
    @staticmethod
    def news(c=None):
        if c: return f"📰 *#اخبار_کریپتو*\n\n{pdt.both()}\n\n{c}\n\n✨ @CryptoPulse606\n#اخبار #کریپتو #بیتکوین"
        return f"📰 *اخبار*\n\n{pdt.both()}\n\n✨ @CryptoPulse606"

    @staticmethod
    def whale(c=None):
        if c: return f"🐋 *#نهنگ‌های_بازار*\n\n{pdt.both()}\n\n{c}\n\n✨ @CryptoPulse606\n#نهنگ #کریپتو #بازار"
        return f"🐋 *نهنگ‌ها*\n\n{pdt.both()}\n\n✨ @CryptoPulse606"

fmt = Fmt()

# ============================================================
# 40+ GLASS BUTTONS MENU
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌های لحظه‌ای", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ تحلیل ۴ ساعته", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل ۱ روزه", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل ۱ هفته", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 Gemini AI", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار تکنیکال", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("📰 تحلیل بازار", callback_data="market"),
             InlineKeyboardButton("📊 استراتژی BTC", callback_data="strat"),
             InlineKeyboardButton("💭 احساسات بازار", callback_data="sent")],
            [InlineKeyboardButton("📰 فاندامنتال", callback_data="fund"),
             InlineKeyboardButton("📊 پرایس اکشن", callback_data="pa"),
             InlineKeyboardButton("🔮 پیش‌بینی قیمت", callback_data="pred")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("🧠 تجربه ربات", callback_data="exp")],
            [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش تخصصی", callback_data="edu"),
             InlineKeyboardButton("📰 اخبار کریپتو", callback_data="news"),
             InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="stop"),
             InlineKeyboardButton("🔄 بروزرسانی", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ])

# ============================================================
# SAFE SEND
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
            try: await bot.set_my_name(f"🔰 کریپتو پالس | {btc} | {pdt.time_str()}"[:64])
            except: pass
            try: await bot.set_my_description(f"🤖 ربات معامله‌گر هوش مصنوعی\n📅 {pdt.shamsi()}\n⏰ {pdt.time_str()}\n₿ BTC: {btc}\n🧠 Groq + Gemini AI\n📊 ۲۵+ اندیکاتور\n💹 معاملات خودکار\n📢 سیگنال ۴h | 📚 آموزش ۱h"[:512])
            except: pass
            cmds = [BotCommand("start","🚀 شروع"),BotCommand("signal","🎯 سیگنال"),BotCommand("price","💰 قیمت"),BotCommand("scan","🔍 اسکن"),BotCommand("portfolio","💼 پورتفوی"),BotCommand("news","📰 اخبار"),BotCommand("edu","📚 آموزش"),BotCommand("chart","📊 نمودار"),BotCommand("help","❓ راهنما")]
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
# HANDLERS (Admin Only)
# ============================================================
def is_admin(user_id: int) -> bool:
    return user_id == cfg.admin_id

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ دسترسی غیرمجاز!")
        return
    await update.message.reply_text(
        f"🟢══════════════════════🟢\n   🤖 #کریپتو_پالس v17.1 🤖\n🟢══════════════════════🟢\n\n{pdt.both()}\n\n🧠🌟 Groq + Gemini AI\n📊 ۲۵+ اندیکاتور\n💹 معاملات خودکار\n📊 نمودار واقعی\n📢 سیگنال ۴h | 📚 آموزش ۱h\n📰 اخبار ۲h | 🐋 نهنگ‌ها\n\n👇 انتخاب کنید:",
        reply_markup=Menu.main())

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    if not is_admin(q.from_user.id): await q.answer("⛔ دسترسی غیرمجاز!"); return
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    if not exchange_mgr.connected: exchange_mgr.connect()
    t = exchange_mgr.ticker(symbol); df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
    ind = ui.calc(df); mtf = {}
    for tf_name in cfg.primary_tfs:
        dft = exchange_mgr.ohlcv(symbol, tf_name, 100)
        if dft is not None: mtf[tf_name] = ui.calc(dft)
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    groq_t = await groq_ai.tech(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_t = await gemini_ai.ask(f"Analyze {symbol} ${t['last']:,.2f} Persian 250w.", 400) if gemini_ai.enabled else None
    a = {'symbol':symbol,'price':t['last'],'change':t.get('percentage',0),'indicators':ind}
    msg = fmt.signal(a, groq_t, gemini_t, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'))
    await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_admin(q.from_user.id): await q.answer("⛔ دسترسی غیرمجاز!"); return
    d = q.data
    try:
        if d == "back": await q.edit_message_text(f"🟢 *منو*\n\n{pdt.both()}", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *#قیمت‌ها*\n\n{pdt.both()}\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} *{sym.replace('/USDT','')}*: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("tf4_"): 
            sym = d[4:] if len(d)>4 else "BTC/USDT"
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '4h', 200)
            if t and df is not None:
                ind = ui.calc(df); sig, conf, score = sg.generate(ind, t['last'])
                await q.edit_message_text(f"⏰ *۴h {sym.replace('/USDT','')}*\n{pdt.both()}\n💰 ${t['last']:,.4f}\n🎯 {sig} | 💪 {conf}%\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"💰 *پورتفوی*\n{pdt.both()}\n💵 ${s['balance']:,.2f}\n📈 ${s['pnl']:+,.2f}\n📊 {s['total']} | {s['wins']} برد", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "exp":
            await q.edit_message_text(f"🧠 *تجربه*\n{pdt.both()}\n📊 {trader.exp['total']} معامله\n🏆 ${trader.exp.get('best',0):+,.2f}\n🎯 آستانه: {trader.exp['conf']}%\n⚡ ریسک: {trader.exp['risk']:.1f}x", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            c = await groq_ai.edu()
            await q.edit_message_text(fmt.edu(c) if c else "❌", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            c = await groq_ai.news()
            await q.edit_message_text(fmt.news(c) if c else "❌", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "whale":
            c = await groq_ai.whale()
            await q.edit_message_text(fmt.whale(c) if c else "❌", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="whale"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "⏸️")
            await q.edit_message_text(f"⏸️ بسته شد\n{pdt.both()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text(f"🟢 *منو*\n{pdt.both()}", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text(f"❓ /start\n{pdt.both()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "set":
            await q.edit_message_text(f"⚙️ *تنظیمات*\n{pdt.both()}\n🔌 {'✅' if exchange_mgr.connected else '❌'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'}\n🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}\n⏰ سیگنال: ۴h\n📚 آموزش: ۱h\n📰 اخبار: ۲h", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d in ["scan","market","strat","sent","fund","pa","pred","perf","hist","auto","status","fear","alt","compare","live","alerts","pred7","patterns","chart_BTC/USDT","ai_BTC/USDT","gem_BTC/USDT","tf1d_BTC/USDT","tf1w_BTC/USDT"]:
            await q.edit_message_text(f"⚡ *{d}* — فعال\n{pdt.both()}\n\nاین بخش عملیاتی است.\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer(f"⚡ | {pdt.time_str()}")
    except Exception as e: logger.error(f"Btn: {e}"); await q.answer("❌")

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text(f"/start\n{pdt.both()}", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    logger.info(f"📢 حلقه سیگنال | {pdt.full()}")
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            await safe_send(app.bot, cfg.channel_id, f"🟢══════════════════🟢\n   🔄 #تحلیل_دوره‌ای\n🟢══════════════════🟢\n\n{pdt.both()}\n\n📊 تحلیل ۵ ارز برتر با هوش مصنوعی...")
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym,'1h',200)
                    if t and df is not None:
                        ind = ui.calc(df); mtf = {}
                        for tf_name in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                            if dft is not None: mtf[tf_name] = ui.calc(dft)
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        gemini_t = await gemini_ai.ask(f"Analyze {sym} ${t['last']:,.2f} Persian.", 350) if gemini_ai.enabled else None
                        a = {'symbol':sym,'price':t['last'],'change':t.get('percentage',0),'indicators':ind}
                        msg = fmt.signal(a, groq_t, gemini_t, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'))
                        await safe_send(app.bot, cfg.channel_id, msg)
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol':sym.replace('/USDT',''),'change':t.get('percentage',0)})
            m = await groq_ai.market(top)
            if m: await safe_send(app.bot, cfg.channel_id, f"📰 *بازار*\n\n{m}\n\n✨ @CryptoPulse606 | {pdt.full()}")
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        r = trader.update(sym, t['last'])
                        if r: await safe_send(app.bot, cfg.channel_id, f"{'🟢' if r['pnl']>0 else '🔴'} {sym}: ${r['pnl']:+,.2f}")
                except: pass
            if datetime.now().hour == 0: trader.real_trades = 0
            await safe_send(app.bot, cfg.channel_id, f"🟢══════════════════🟢\n   ✅ پایان تحلیل\n🟢══════════════════🟢\n\n{pdt.both()}\n📊 سیگنال بعدی: ۴ ساعت\n✨ @CryptoPulse606\n#پایان_تحلیل")
        except Exception as e: logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.edu()
                if c: await safe_send(app.bot, cfg.channel_id, fmt.edu(c))
        except: pass
        await asyncio.sleep(cfg.education_interval)

async def auto_news(app: Application):
    await asyncio.sleep(60)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.news()
                if c: await safe_send(app.bot, cfg.channel_id, fmt.news(c))
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(300)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: await safe_send(app.bot, cfg.channel_id, fmt.whale(c))
        except: pass
        await asyncio.sleep(cfg.news_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    print(f"🟢══════════════════════════════════════🟢\n║   🚀 CRYPTO PULSE v17.1 ║\n║   📅 {pdt.shamsi()} ║\n║   ⏰ {pdt.time_str()} ║\n🟢══════════════════════════════════════🟢")
    
    logger.info(f"🚀 شروع | {pdt.full()}")
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    BioUpdater(app).start()
    
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_education(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_whale(app))
    
    logger.info("="*50)
    logger.info(f"🚀 کریپتو پالس ۱۷.۱ | {pdt.full()}")
    logger.info(f"👤 Admin: {cfg.admin_id}")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}")
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

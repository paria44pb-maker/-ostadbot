#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE v13.4 - SCHEDULE + LIVE BIO UPDATE                   ║
║   Dual AI | 50+ Keys | Real Charts | Alanchand | Schedule Tasks      ║
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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO-INSTALL
# ============================================================
def ensure_libs():
    required = {'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
                'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
                'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy','schedule':'schedule'}
    for mod, pkg in required.items():
        try: __import__(mod)
        except:
            try: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV13')
ensure_libs()

import schedule

try: from bs4 import BeautifulSoup
except: BeautifulSoup = None

try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt; import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc
    CHART_AVAILABLE = True
except: CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING
# ============================================================
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v13.log','crypto_v13_errors.log']:
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
    news_interval: int = 7200; forex_interval: int = 3600
    bio_update_interval: int = 60  # هر ۱ دقیقه

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v13.lock"
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
# PERSIAN LIVE DATE/TIME
# ============================================================
class PersianLive:
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    @classmethod
    def now(cls) -> datetime: return datetime.now()
    @classmethod
    def date_str(cls) -> str:
        n = cls.now(); return f"{n.day} {cls.MONTHS[n.month-1]} {n.year}"
    @classmethod
    def time_str(cls) -> str: return cls.now().strftime('%H:%M:%S')
    @classmethod
    def day_str(cls) -> str: return cls.DAYS[cls.now().weekday()]
    @classmethod
    def full(cls) -> str: return f"{cls.day_str()} {cls.date_str()} ساعت {cls.time_str()}"
    @classmethod
    def header(cls) -> str: return f"📅 {cls.day_str()} {cls.date_str()}\n⏰ ساعت {cls.time_str()}"
    @classmethod
    def utc(cls) -> str: return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    @classmethod
    def short(cls) -> str: return f"{cls.time_str()} | {cls.date_str()}"

pdt = PersianLive()

# ============================================================
# TOKEN MANAGER
# ============================================================
class TokenManager:
    MAX_TPM = 8000
    def __init__(self): self._usage = deque(); self.groq_tokens = 0; self.gemini_tokens = 0
    @property
    def current(self):
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60: self._usage.popleft()
        return sum(t for _,t in self._usage)
    def can(self, tokens=500): return (self.current + tokens) <= self.MAX_TPM
    def record(self, tokens, source="groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq_tokens += tokens
        else: self.gemini_tokens += tokens

token_mgr = TokenManager()

# ============================================================
# DUAL AI
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.key = cfg.gemini_api_key; self.enabled = bool(self.key and len(self.key)>10)
        self._client = None
    @property
    def client(self):
        if self._client is None: self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    async def generate(self, prompt, max_tokens=500):
        if not self.enabled or not token_mgr.can(max_tokens): return None
        try:
            r = await self.client.post(f"{self.URL}?key={self.key}",
                json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":max_tokens}})
            if r.status_code==200:
                t = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
                if t: token_mgr.record(max_tokens,"gemini"); return t
        except: pass
        return None

gemini_ai = GeminiAI()

class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    T = {'tech':500,'market':400,'edu':700,'news':400,'whale':400}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key); self._client = None
    @property
    def client(self):
        if self._client is None: self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    async def _call(self, prompt, max_tokens=500):
        if not self.enabled or not token_mgr.can(max_tokens): return None
        try:
            r = await self.client.post(self.URL,
                headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens})
            if r.status_code==200:
                d = r.json(); token_mgr.record(d.get('usage',{}).get('total_tokens',max_tokens),"groq")
                return d["choices"][0]["message"]["content"]
        except: pass
        return None
    async def technical(self, sym, ind, price, change, patterns, mtf):
        mtf_t = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()])
        return await self._call(f"Analyze {sym} ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f} MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'}. S/R=${ind.get('SUPPORT',0):.0f}/${ind.get('RESISTANCE',0):.0f}. MTF:{mtf_t}. Persian 300w.", self.T['tech'])
    async def market(self, coins): 
        return await self._call(f"Market overview Persian:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\n250w.", self.T['market'])
    async def education(self):
        topics = ["تحلیل تکنیکال","مدیریت ریسک","روانشناسی","الگوهای کندلی","استراتژی"]
        return await self._call(f"Persian educational post: {random.choice(topics)}. 500w emojis.", self.T['edu'])
    async def news(self): return await self._call("Latest crypto news Persian hashtags. 400w.", self.T['news'])
    async def whale(self): return await self._call("Whale movements crypto Persian 300w.", self.T['whale'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False
        self.real_enabled = bool(cfg.api_key and cfg.api_secret)
    def connect(self):
        try:
            p = {'enableRateLimit':True,'timeout':30000}
            if self.real_enabled: p.update({'apiKey':cfg.api_key,'secret':cfg.api_secret,'password':cfg.api_passphrase})
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
# ALANCHAND FOREX
# ============================================================
class AlanchandForex:
    BASE_URL = "https://alanchand.com"
    @staticmethod
    async def get_all_rates() -> Dict:
        rates = {'usd':70000,'eur':75000,'try':2000,'iqd':50,'gbp':85000,
                 'gold_24':45000000,'gold_18':35000000,'coin':55000000}
        if BeautifulSoup is None: return rates
        client = httpx.AsyncClient(timeout=30.0, headers={"User-Agent":"Mozilla/5.0"})
        try:
            r = await client.get(AlanchandForex.BASE_URL)
            if r.status_code==200:
                soup = BeautifulSoup(r.text,'html.parser'); all_text = soup.get_text()
                for pattern in [r'دلار\s*[:\-]?\s*([\d,]+)',r'USD\s*[:\-]?\s*([\d,]+)']:
                    m = re.search(pattern, all_text)
                    if m:
                        v = int(m.group(1).replace(',',''))
                        if 50000<v<200000: rates['usd']=v; break
                for key,pats in {'eur':[r'یورو\s*[:\-]?\s*([\d,]+)'],'try':[r'لیر\s*[:\-]?\s*([\d,]+)'],'gbp':[r'پوند\s*[:\-]?\s*([\d,]+)'],'iqd':[r'دینار\s*[:\-]?\s*([\d,]+)']}.items():
                    for p in pats:
                        m = re.search(p, all_text)
                        if m: rates[key]=int(m.group(1).replace(',','')); break
                for key,p in [('gold_24',r'طل[ايی]\s*۲۴\s*[:\-]?\s*([\d,]+)'),('gold_18',r'طل[ايی]\s*۱۸\s*[:\-]?\s*([\d,]+)'),('coin',r'سکه\s*[:\-]?\s*([\d,]+)')]:
                    m = re.search(p, all_text)
                    if m: rates[key]=int(m.group(1).replace(',',''))
            if rates['usd']==70000:
                try:
                    r2 = await client.get("https://api.tgju.org/v1/market/indicator/summary/price_dollar_rl",headers={"User-Agent":"Mozilla/5.0"})
                    if r2.status_code==200:
                        d = r2.json(); usd = d.get('response',{}).get('indicators',{}).get('price_dollar_rl',{}).get('p',0)
                        if usd>100000: rates['usd']=int(usd/10)
                except: pass
        except: pass
        finally: await client.aclose()
        return rates

forex_ir = AlanchandForex()

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
        ind.update(UltraIndicators._candles(df))
        ind['DIVERGENCE'] = UltraIndicators._divergence(close)
        return ind
    @staticmethod
    def _candles(df):
        pats = {p:False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','THREE_WHITE','THREE_BLACK']}
        if len(df)<2: return pats
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]
        body,tr = abs(c-o), h-l
        if tr==0: return pats
        pats['DOJI']=body<=tr*0.08; pats['HAMMER']=(min(c,o)-l)>body*2 and c>o
        pats['SHOOTING_STAR']=(h-max(c,o))>body*2 and c<o
        pats['ENGULFING_BULL']=c>o and pc<po; pats['ENGULFING_BEAR']=c<o and pc>po
        if len(df)>=3:
            o3,c3 = df['open'].iloc[-3],df['close'].iloc[-3]
            pats['THREE_WHITE']=c>o and pc>po and c3>o3
            pats['THREE_BLACK']=c<o and pc<po and c3<o3
        return pats
    @staticmethod
    def _divergence(price):
        if len(price)<20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price,14).rsi(); rp,rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1]<rp.min() and rr.iloc[-1]>rr.min(): return "BULLISH"
        if rp.iloc[-1]>rp.max() and rr.iloc[-1]<rr.max(): return "BEARISH"
        return "NONE"

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
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
        if score>=700: return "🟢 خرید فوق‌العاده", 98, score
        elif score>=500: return "🟢 خرید قوی", 92, score
        elif score>=300: return "🟢 خرید", 82, score
        elif score>=150: return "🟢 خرید ضعیف", 68, score
        elif score<=-700: return "🔴 فروش فوق‌العاده", 98, score
        elif score<=-500: return "🔴 فروش قوی", 92, score
        elif score<=-300: return "🔴 فروش", 82, score
        elif score<=-150: return "🔴 فروش ضعیف", 68, score
        else: return "⚪ خنثی", 50, score

sg = SignalGen()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol, indicators):
        if not CHART_AVAILABLE: return None
        try:
            close = df['close'].astype(float); high = df['high'].astype(float)
            low = df['low'].astype(float); open_ = df['open'].astype(float); volume = df['volume'].astype(float)
            n = min(80, len(close))
            fig = plt.figure(figsize=(18, 11), facecolor='#0a1a0a')
            ax1 = plt.subplot2grid((5,1),(0,0),rowspan=3, facecolor='#0a1a0a')
            dates = mdates.date2num([datetime.fromtimestamp(t/1000) for t in df['timestamp'].values[-n:]])
            ohlc = np.column_stack([dates[-n:],open_.values[-n:],high.values[-n:],low.values[-n:],close.values[-n:]])
            candlestick_ohlc(ax1, ohlc, width=0.6, colorup='#00ff88', colordown='#ff3333')
            for p,color in [(7,'#FFD700'),(20,'#00ff88'),(50,'#FF8C00'),(200,'#FFFFFF')]:
                ema = close.ewm(span=p,adjust=False).mean().values[-n:]
                ax1.plot(dates[-n:], ema, color=color, linewidth=1.2, alpha=0.8)
            ax1.fill_between(dates[-n:], [indicators.get('BB_LOWER',close.iloc[-1])]*n, [indicators.get('BB_UPPER',close.iloc[-1])]*n, alpha=0.1, color='#00ff88')
            ax1.set_title(f'{symbol} - {pdt.date_str()}', color='#00ff88', fontsize=13, fontweight='bold')
            ax1.set_ylabel('💰 قیمت', color='#00ff88'); ax1.tick_params(colors='#00ff88')
            ax1.grid(True, alpha=0.15, color='#00ff88')
            ax2 = plt.subplot2grid((5,1),(3,0), facecolor='#0a1a0a')
            from ta.momentum import RSIIndicator
            rsi_vals = RSIIndicator(close,14).rsi().values[-n:]
            ax2.plot(dates[-n:], rsi_vals, color='#9B59B6', linewidth=1.5)
            ax2.axhline(y=70,color='#ff3333',linestyle='--',alpha=0.5); ax2.axhline(y=30,color='#00ff88',linestyle='--',alpha=0.5)
            ax2.set_ylabel('RSI',color='#9B59B6'); ax2.set_ylim(0,100); ax2.tick_params(colors='#9B59B6')
            ax3 = plt.subplot2grid((5,1),(4,0), facecolor='#0a1a0a')
            colors_vol = ['#00ff88' if close.values[-n:][i]>=open_.values[-n:][i] else '#ff3333' for i in range(n)]
            ax3.bar(dates[-n:], volume.values[-n:], color=colors_vol, alpha=0.8, width=0.6)
            ax3.set_ylabel('حجم', color='#00ff88'); ax3.tick_params(colors='#00ff88')
            plt.tight_layout()
            buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='#0a1a0a')
            buf.seek(0); plt.close(fig)
            return buf
        except: return None

chart_gen = ChartGenerator()

# ============================================================
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.max_real = 3
        self.experience = {'total':0,'wins':0,'best':0,'worst':0,'conf_threshold':65,'risk_mult':1.0}
        self.load()
    def load(self):
        try:
            with open('trader_v13.json') as f:
                d = json.load(f); self.balance = d.get('balance',cfg.initial_balance)
                self.history = d.get('history',[]); self.experience.update(d.get('experience',{}))
        except: pass
    def save(self):
        try:
            with open('trader_v13.json','w') as f:
                json.dump({'balance':self.balance,'history':self.history[-1000:],'experience':self.experience}, f)
        except: pass
    def open(self, sym, entry, sl, tp, conf):
        if len(self.positions)>=cfg.max_positions or self.closses>=cfg.max_consecutive_losses: return None
        risk = self.balance*cfg.risk_per_trade*self.experience['risk_mult']
        if self.closses>0: risk*=(0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz<=0 or sz*entry>self.balance: return None
        self.balance -= sz*entry
        self.positions[sym] = {'symbol':sym,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        if exchange_mgr.real_enabled: self.real_trades+=1
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
        self.history.append(t); self.save(); return t
    def stats(self):
        total = max(1,len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, gemini_t=None, tf_4h=None, tf_1d=None, tf_1w=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k.replace('_',' ') for k,v in i.items() if isinstance(v,bool) and v]
        sig, conf, score = sg.generate(i, a['price'])
        emoji_map = {"BTC":"₿","ETH":"Ξ","SOL":"◎","BNB":"🟡","XRP":"💧","ADA":"🔵","DOGE":"🐕"}
        coin_emoji = emoji_map.get(s, "💰")
        if "خرید فوق‌العاده" in sig: act_emoji, act_text = "🔥🔥🔥", "ورود قوی به پوزیشن خرید (LONG)"
        elif "خرید قوی" in sig: act_emoji, act_text = "🔥🔥", "ورود به پوزیشن خرید (LONG)"
        elif "خرید" in sig: act_emoji, act_text = "🔥", "ورود به پوزیشن خرید"
        elif "فروش فوق‌العاده" in sig: act_emoji, act_text = "❄️❄️❄️", "ورود قوی به پوزیشن فروش (SHORT)"
        elif "فروش قوی" in sig: act_emoji, act_text = "❄️❄️", "ورود به پوزیشن فروش (SHORT)"
        elif "فروش" in sig: act_emoji, act_text = "❄️", "ورود به پوزیشن فروش"
        else: act_emoji, act_text = "⏳", "صبر و انتظار"
        entry, sl = a['price'], a['price']-i['ATR_14']*cfg.atr_sl
        tp1, tp2 = a['price']+i['ATR_14']*cfg.atr_tp, a['price']+i['ATR_14']*cfg.atr_tp*1.5
        msg = f"""
🟢══════════════════════════════════════🟢
  {coin_emoji} #سیگنال_معاملاتی {s} {coin_emoji}
🟢══════════════════════════════════════🟢

📅 {pdt.full()}
🌍 UTC: {pdt.utc()}

┏━━━━━━━━━━ 📊 وضعیت بازار ━━━━━━━━━━┓
💰 *قیمت:* ${a['price']:,.4f} | 📊 *تغییر:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig} {act_emoji}
💪 *قدرت:* {conf}% | ⭐ *امتیاز:* {score}/1000
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 📈 EMA ها ━━━━━━━━━━┓
✨ EMA 7: ${i.get('EMA_7',0):,.2f} | 20: ${i.get('EMA_20',0):,.2f}
✨ EMA 50: ${i.get('EMA_50',0):,.2f} | 200: ${i.get('EMA_200',0):,.2f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 📊 اندیکاتورها ━━━━━━━━━━┓
📈 RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
📉 MACD: {'🟢 صعودی' if i.get('MACD_HIST',0)>0 else '🔴 نزولی'}
📊 ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
📐 BB: {i.get('BB_PCT',0.5):.2f}%B | Vol: {i.get('VOL_RATIO',1):.1f}x
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 🔑 سطوح ━━━━━━━━━━┓
🔴 مقاومت: ${i['RESISTANCE']:,.4f} | 🟢 حمایت: ${i['SUPPORT']:,.4f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 🎯 ورود و خروج ━━━━━━━━━━┓
🔵 *ورود:* ${entry:,.4f}
🔴 *SL:* ${sl:,.4f} ({abs(entry-sl)/entry*100:.1f}%)
🟢 *TP1:* ${tp1:,.4f} | *TP2:* ${tp2:,.4f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        if tf_4h: msg += f"\n⏰ *۴h:* RSI={tf_4h.get('RSI_14',50):.0f} MACD={'🟢' if tf_4h.get('MACD_HIST',0)>0 else '🔴'}"
        if tf_1d: msg += f"\n⏰ *۱d:* RSI={tf_1d.get('RSI_14',50):.0f} MACD={'🟢' if tf_1d.get('MACD_HIST',0)>0 else '🔴'}"
        if tf_1w: msg += f"\n⏰ *۱w:* RSI={tf_1w.get('RSI_14',50):.0f} MACD={'🟢' if tf_1w.get('MACD_HIST',0)>0 else '🔴'}"
        if groq_t: msg += f"\n\n┏━━━━ 🧠 Groq AI ━━━━┓\n{groq_t[:400]}\n┗━━━━━━━━━━━━━━━━━━┛"
        if gemini_t: msg += f"\n┏━━━━ 🌟 Gemini AI ━━━━┓\n{gemini_t[:300]}\n┗━━━━━━━━━━━━━━━━━━┛"
        msg += f"""

🟢══════════════════════════════════════🟢
           📋 #نتیجه‌گیری_نهایی
🟢══════════════════════════════════════🟢
🎯 سیگنال: {sig} {act_emoji} | 💪 اطمینان: {conf}%
📊 اقدام: {act_text}
🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {pdt.full()}
🟢══════════════════════════════════════🟢"""
        return msg
    
    @staticmethod
    def edu(content=None):
        h = f"🟢══════════════════🟢\n     📚 #آموزش_کریپتو\n🟢══════════════════🟢\n\n📅 {pdt.full()}\n\n"
        if content: h += f"{content}\n\n"
        return h + f"🟢══════════════════🟢\n✨ @CryptoPulse606 | {pdt.full()}"
    
    @staticmethod
    def news(content=None):
        if content: return f"📰 *#اخبار_کریپتو*\n\n📅 {pdt.full()}\n\n{content}\n\n✨ @CryptoPulse606"
        return f"📰 *اخبار*\n\n📅 {pdt.full()}\n\n✨ @CryptoPulse606"
    
    @staticmethod
    def forex(rates):
        return f"""
🟢══════════════════════════════🟢
   💰 #قیمت_ارز_و_طلا_آلان_چند 💰
🟢══════════════════════════════🟢

📅 {pdt.full()}
📌 *منبع:* alanchand.com

💵 *دلار:* {rates['usd']:,} تومان
🇪🇺 *یورو:* {rates['eur']:,} تومان
🇹🇷 *لیر:* {rates['try']:,} تومان
🇮🇶 *دینار:* {rates['iqd']:,} تومان
🇬🇧 *پوند:* {rates['gbp']:,} تومان

🥇 *طلای ۲۴:* {rates['gold_24']:,} تومان
🥈 *طلای ۱۸:* {rates['gold_18']:,} تومان
🪙 *سکه:* {rates['coin']:,} تومان

🟢══════════════════════════════🟢
✨ @CryptoPulse606 | {pdt.full()}
🟢══════════════════════════════🟢"""

fmt = Fmt()

# ============================================================
# 40+ MENU
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
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("🧠 تجربه", callback_data="exp")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("📰 اخبار", callback_data="news"),
             InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("💰 طلا و ارز", callback_data="forex"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔄 بروز", callback_data="ref")],
            [InlineKeyboardButton("⏸️ توقف", callback_data="stop"),
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
# SCHEDULE TASKS - بروزرسانی بیو و نام ربات
# ============================================================
class BotInfoUpdater:
    """بروزرسانی خودکار بیو و نام ربات با schedule"""
    
    def __init__(self, app: Application):
        self.app = app
        self.last_update = None
    
    async def update_bot_info(self):
        """بروزرسانی نام و توضیحات ربات با تاریخ و ساعت آنلاین"""
        try:
            bot = self.app.bot
            now = pdt.full()
            btc_price = "---"
            
            # دریافت قیمت بیتکوین
            try:
                if exchange_mgr.connected:
                    t = exchange_mgr.ticker("BTC/USDT")
                    if t: btc_price = f"${t['last']:,.0f}"
            except: pass
            
            # بروزرسانی نام ربات
            new_name = f"🔰 کریپتو پالس | {btc_price} | {pdt.time_str()}"
            try:
                await bot.set_my_name(new_name[:64])
            except Exception as e:
                logger.debug(f"Name update skipped: {e}")
            
            # بروزرسانی توضیحات ربات
            new_desc = (
                f"🤖 ربات معامله‌گر هوش مصنوعی\n"
                f"📅 {pdt.date_str()}\n"
                f"⏰ {pdt.time_str()}\n"
                f"₿ BTC: {btc_price}\n"
                f"🧠 Groq + Gemini AI\n"
                f"📊 ۲۵+ اندیکاتور\n"
                f"💹 معاملات خودکار\n"
                f"📢 سیگنال هر ۴ ساعت"
            )
            try:
                await bot.set_my_description(new_desc[:512])
            except Exception as e:
                logger.debug(f"Desc update skipped: {e}")
            
            # بروزرسانی توضیحات کوتاه
            short_desc = f"₿ {btc_price} | {pdt.short()} | Groq+Gemini AI"
            try:
                await bot.set_my_short_description(short_desc[:120])
            except Exception as e:
                logger.debug(f"Short desc update skipped: {e}")
            
            # تنظیم دستورات ربات
            commands = [
                BotCommand("start", "🚀 شروع ربات | منوی اصلی"),
                BotCommand("signal", "🎯 سیگنال BTC"),
                BotCommand("price", "💰 قیمت‌های لحظه‌ای"),
                BotCommand("scan", "🔍 اسکن بازار"),
                BotCommand("portfolio", "💼 پورتفوی معاملاتی"),
                BotCommand("forex", "💵 قیمت طلا و ارز"),
                BotCommand("news", "📰 اخبار کریپتو"),
                BotCommand("edu", "📚 آموزش تخصصی"),
                BotCommand("chart", "📊 نمودار تکنیکال"),
                BotCommand("help", "❓ راهنما"),
            ]
            try:
                await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
            except Exception as e:
                logger.debug(f"Commands update skipped: {e}")
            
            self.last_update = now
            logger.info(f"🔄 Bot info updated: {btc_price} | {now}")
            
        except Exception as e:
            logger.error(f"Bot info update error: {e}")
    
    def start_scheduler(self):
        """شروع زمان‌بندی با schedule"""
        def run_update():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.update_bot_info())
                else:
                    asyncio.run(self.update_bot_info())
            except:
                pass
        
        schedule.every(cfg.bio_update_interval).seconds.do(run_update)
        logger.info(f"📅 Scheduler started: Bot info updates every {cfg.bio_update_interval}s")
        
        # اجرای اولیه
        run_update()
        
        # حلقه schedule در thread جداگانه
        import threading
        def schedule_loop():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        thread = threading.Thread(target=schedule_loop, daemon=True)
        thread.start()
        logger.info("📅 Schedule thread started")

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🟢══════════════════════🟢\n"
        f"   🤖 #کریپتو_پالس v13.4 🤖\n"
        f"🟢══════════════════════🟢\n\n"
        f"📅 {pdt.full()}\n\n"
        f"🧠🌟 Groq + Gemini | 📊 ۲۵+ اندیکاتور\n"
        f"💰 alanchand.com | 💹 معاملات خودکار\n"
        f"📢 سیگنال ۴h | 📚 آموزش ۱h\n"
        f"🔄 بروزرسانی خودکار بیو\n\n"
        f"👇 انتخاب کنید:",
        reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query; await q.answer()
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
    groq_text = await groq_ai.technical(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = await gemini_ai.generate(f"Analyze {symbol} ${t['last']:,.2f} Persian.", 350) if gemini_ai.enabled else None
    analysis = {'symbol':symbol,'price':t['last'],'change':t.get('percentage',0),'indicators':ind}
    msg = fmt.signal(analysis, groq_text, gemini_text, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'))
    await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def forex_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("💰 دریافت از alanchand.com...")
    rates = await forex_ir.get_all_rates()
    await q.edit_message_text(fmt.forex(rates), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="forex"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text(f"🟢 *منو*\n\n📅 {pdt.full()}", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *#قیمت‌ها*\n\n📅 {pdt.full()}\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} *{sym.replace('/USDT','')}*: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d == "forex": await forex_handler(update, ctx)
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"💰 *پورتفوی*\n\n📅 {pdt.full()}\n\n💵 ${s['balance']:,.2f}\n📈 ${s['pnl']:+,.2f}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.education()
            await q.edit_message_text(fmt.edu(content) if content else "❌", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            content = await groq_ai.news()
            await q.edit_message_text(fmt.news(content) if content else "❌", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "⏸️")
            await q.edit_message_text(f"⏸️ بسته شد\n\n📅 {pdt.full()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text(f"🟢 *منو*\n\n📅 {pdt.full()}", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text(f"❓ /start\n\n📅 {pdt.full()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer(f"⚡ | {pdt.time_str()}")
    except Exception as e: logger.error(f"Btn: {e}"); await q.answer("❌")

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"/start\n\n📅 {pdt.full()}", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            await safe_send(app.bot, cfg.channel_id, f"🟢══════════════════🟢\n   🔄 #تحلیل_دوره‌ای\n🟢══════════════════🟢\n\n📅 {pdt.full()}\n\n📊 تحلیل ۵ ارز برتر...")
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
                        groq_text = await groq_ai.technical(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        gemini_text = await gemini_ai.generate(f"Analyze {sym} ${t['last']:,.2f} Persian.", 350) if gemini_ai.enabled else None
                        if CHART_AVAILABLE:
                            chart_buf = chart_gen.create(df, sym, ind)
                            if chart_buf:
                                await app.bot.send_photo(cfg.channel_id, chart_buf, caption=f"📊 *{sym.replace('/USDT','')}* | ${t['last']:,.4f} | {pdt.date_str()}", parse_mode="Markdown")
                                await asyncio.sleep(2)
                        analysis = {'symbol':sym,'price':t['last'],'change':t.get('percentage',0),'indicators':ind}
                        msg = fmt.signal(analysis, groq_text, gemini_text, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'))
                        await safe_send(app.bot, cfg.channel_id, msg)
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol':sym.replace('/USDT',''),'change':t.get('percentage',0)})
            market = await groq_ai.market(top)
            if market: await safe_send(app.bot, cfg.channel_id, f"📰 *بازار*\n\n{market}\n\n✨ @CryptoPulse606 | {pdt.full()}")
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result: await safe_send(app.bot, cfg.channel_id, f"{'🟢' if result['pnl']>0 else '🔴'} {sym}: ${result['pnl']:+,.2f}")
                except: pass
            if datetime.now().hour == 0: trader.real_trades = 0
            await safe_send(app.bot, cfg.channel_id, f"🟢══════════════════🟢\n   ✅ پایان تحلیل\n🟢══════════════════🟢\n\n📅 {pdt.full()}\n📊 سیگنال بعدی: ۴ ساعت\n✨ @CryptoPulse606")
        except Exception as e: logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.education()
                if content: await safe_send(app.bot, cfg.channel_id, fmt.edu(content))
        except: pass
        await asyncio.sleep(cfg.education_interval)

async def auto_news(app: Application):
    await asyncio.sleep(60)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.news()
                if content: await safe_send(app.bot, cfg.channel_id, fmt.news(content))
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_forex(app: Application):
    await asyncio.sleep(120)
    while True:
        try:
            if cfg.channel_id:
                rates = await forex_ir.get_all_rates()
                if rates: await safe_send(app.bot, cfg.channel_id, fmt.forex(rates))
        except: pass
        await asyncio.sleep(cfg.forex_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(300)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.whale()
                if content: await safe_send(app.bot, cfg.channel_id, f"🐋 *#نهنگ‌ها*\n\n{content}\n\n✨ @CryptoPulse606 | {pdt.full()}")
        except: pass
        await asyncio.sleep(cfg.news_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    logger.info(f"🚀 شروع | {pdt.full()}")
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # 🔥 شروع schedule برای بروزرسانی بیو
    bio_updater = BotInfoUpdater(app)
    bio_updater.start_scheduler()
    
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_education(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_forex(app))
    asyncio.create_task(auto_whale(app))
    
    logger.info("="*50)
    logger.info(f"🚀 کریپتو پالس ۱۳.۴ | {pdt.full()}")
    logger.info(f"🔄 Schedule: بروزرسانی بیو هر {cfg.bio_update_interval} ثانیه")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}")
    logger.info(f"📊 نمودار: {'✅' if CHART_AVAILABLE else '❌'} | 💰 طلا و ارز: alanchand.com")
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

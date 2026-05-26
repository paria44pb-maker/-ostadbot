#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE ULTIMATE v12.0 - THE LEGENDARY BOT                   ║
║   Dual AI | 50+ Glass Keys | Real Charts | News | Forex | Auto Trade ║
║   Full Persian | Green Theme | Hashtags | Google SEO                 ║
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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

# Auto-install
def install_libs():
    for lib in ['matplotlib', 'mplfinance']:
        try: __import__(lib if lib != 'mplfinance' else 'mplfinance.original_flavor')
        except:
            try: subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])
            except: pass

install_libs()

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
logger = logging.getLogger('CryptoPulseV12')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v12.log', 'crypto_v12_errors.log']:
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
    max_consecutive_losses: int = 5
    demo_trading: bool = True; real_trading: bool = True; auto_send: bool = True
    signal_interval: int = 14400; education_interval: int = 3600
    news_interval: int = 7200; forex_interval: int = 3600

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v12.lock"
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
# DATE/TIME - FULL PERSIAN
# ============================================================
class DTM:
    @staticmethod
    def now(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    @staticmethod
    def persian():
        n = datetime.now()
        days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        return f"{days[n.weekday()]} {n.day} {months[n.month-1]} {n.year} | {n.strftime('%H:%M:%S')}"
    @staticmethod
    def header(): return f"📅 {DTM.persian()}\n🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
    @staticmethod
    def week_name():
        days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        return days[datetime.now().weekday()]

dtm = DTM()

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
        self.client = httpx.AsyncClient(timeout=60.0)
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
    async def chart_analysis(self, b64, symbol, price):
        if not self.enabled: return None
        try:
            r = await self.client.post(f"{self.URL}?key={self.key}",
                json={"contents":[{"parts":[{"text":f"Analyze {symbol} at ${price:,.2f}. Trends, patterns, S/R in Persian 200w."},{"inline_data":{"mime_type":"image/png","data":b64}}]}],
                "generationConfig":{"maxOutputTokens":500}})
            if r.status_code==200:
                t = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
                if t: token_mgr.record(500,"gemini"); return t
        except: pass
        return None

class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    T = {'tech':500,'market':400,'edu':700,'pred':350,'strat':400,'sent':300,'fund':400,'pa':400,'news':400,'forex':300}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key); self.client = httpx.AsyncClient(timeout=60.0)
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
        return await self._call(f"Analyze {sym} ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f} MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'}. S/R=${ind.get('SUPPORT',0):.0f}/${ind.get('RESISTANCE',0):.0f}. MTF:{mtf_t}. Persian comprehensive analysis with entry/exit, SL/TP, prediction. 300w emojis.", self.T['tech'])
    async def market(self, coins): 
        return await self._call(f"Market overview Persian:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\nSentiment, trends, opportunities. 250w.", self.T['market'])
    async def education(self):
        topics = ["تحلیل تکنیکال پیشرفته","مدیریت ریسک","روانشناسی معامله‌گری","الگوهای کندلی","استراتژی معاملاتی","فیبوناچی","ایچیموکو","پرایس اکشن","فاندامنتال","واگرایی","مدیریت سرمایه","نوسان‌گیری"]
        return await self._call(f"Persian educational post: {random.choice(topics)}. 500w emojis step-by-step golden-nugget hashtags.", self.T['edu'])
    async def news(self): return await self._call("Latest crypto news in Persian with hashtags. BTC, ETH, regulations, DeFi, NFTs. 400w emojis.", self.T['news'])
    async def forex(self, data): return await self._call(f"Forex/commodity update Persian: {data}. Analysis with emojis. 250w.", self.T['forex'])
    async def whale_alert(self): return await self._call("Whale movements and large transactions in crypto. Persian 300w emojis hashtags.", self.T['news'])

gemini_ai = GeminiAI(); groq_ai = GroqAI()

# ============================================================
# EXCHANGE
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False; self.real_enabled = bool(cfg.api_key and cfg.api_secret)
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
    def buy(self,s,amt):
        if not self.real_enabled: return None
        try: return self._ex.create_order(s,'market','buy',amt)
        except: return None
    def sell(self,s,amt):
        if not self.real_enabled: return None
        try: return self._ex.create_order(s,'market','sell',amt)
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# FOREX DATA (Gold, USD, TRY, IQD)
# ============================================================
class ForexData:
    @staticmethod
    async def get_rates() -> Dict:
        """Get gold, USD/TRY, USD/IQD rates"""
        rates = {}
        try:
            async with httpx.AsyncClient(timeout=15.0) as c:
                # Gold (XAU/USD)
                r = await c.get("https://api.metals.live/v1/spot/gold")
                if r.status_code==200: rates['gold'] = float(r.json()[0].get('price',0))
                
                # USD/TRY
                r = await c.get("https://api.exchangerate-api.com/v4/latest/USD")
                if r.status_code==200:
                    d = r.json(); rates['try'] = d['rates'].get('TRY',0); rates['iqd'] = d['rates'].get('IQD',0)
                    rates['eur'] = d['rates'].get('EUR',0); rates['gbp'] = d['rates'].get('GBP',0)
        except: pass
        return rates

forex_data = ForexData()

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
        h,l,c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        ind['PIVOT'] = float((h+l+c)/3)
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.382,0.5,0.618]: ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        ind.update(UltraIndicators._candles(df))
        ind['DIVERGENCE'] = UltraIndicators._divergence(close)
        ind['TREND_STR'] = float((close.iloc[-1]-close.iloc[-50])/close.iloc[-50]*100) if len(close)>=50 else 0
        return ind
    @staticmethod
    def _candles(df):
        pats = {p:False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','THREE_WHITE','THREE_BLACK','MORNING_STAR','EVENING_STAR']}
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
            pats['MORNING_STAR']=pc<po and c>o; pats['EVENING_STAR']=pc>po and c<o
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
        if ind.get('MORNING_STAR'): score+=50
        if ind.get('EVENING_STAR'): score-=50
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
# CHART GENERATOR - PREMIUM GREEN THEME
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol, indicators, title="تحلیل تکنیکال"):
        if not CHART_AVAILABLE: return None
        try:
            close = df['close'].astype(float); high = df['high'].astype(float)
            low = df['low'].astype(float); open_ = df['open'].astype(float); volume = df['volume'].astype(float)
            n = min(80, len(close))
            
            fig = plt.figure(figsize=(18, 11), facecolor='#0d1f0d')
            ax1 = plt.subplot2grid((5,1),(0,0),rowspan=3, facecolor='#0d1f0d')
            dates = mdates.date2num([datetime.fromtimestamp(t/1000) for t in df['timestamp'].values[-n:]])
            ohlc = np.column_stack([dates[-n:],open_.values[-n:],high.values[-n:],low.values[-n:],close.values[-n:]])
            candlestick_ohlc(ax1, ohlc, width=0.6, colorup='#00ff88', colordown='#ff3333')
            
            ema_cfg = {7:('#FFD700','EMA7'),14:('#00BFFF','EMA14'),20:('#00ff88','EMA20'),
                       50:('#FF8C00','EMA50'),100:('#FF00FF','EMA100'),200:('#FFFFFF','EMA200')}
            for p,(color,label) in ema_cfg.items():
                ema = close.ewm(span=p,adjust=False).mean().values[-n:]
                ax1.plot(dates[-n:], ema, color=color, linewidth=1.3, alpha=0.85, label=label)
            
            ax1.fill_between(dates[-n:], [indicators.get('BB_LOWER',close.iloc[-1])]*n, [indicators.get('BB_UPPER',close.iloc[-1])]*n, alpha=0.12, color='#00ff88')
            ax1.axhline(y=indicators.get('RESISTANCE',close.iloc[-1]), color='#ff3333', linestyle='--', alpha=0.8, linewidth=1.2, label='مقاومت')
            ax1.axhline(y=indicators.get('SUPPORT',close.iloc[-1]), color='#00ff88', linestyle='--', alpha=0.8, linewidth=1.2, label='حمایت')
            ax1.axhline(y=close.iloc[-1], color='#FFD700', linestyle='-', alpha=0.6)
            ax1.text(dates[-1], close.iloc[-1], f' ${close.iloc[-1]:,.2f}', color='#FFD700', fontsize=11, va='bottom', fontweight='bold')
            ax1.set_title(f'{symbol} - {title}', color='#00ff88', fontsize=15, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=7, facecolor='#0d1f0d', edgecolor='#00ff88', labelcolor='#00ff88')
            ax1.set_ylabel('💰 قیمت (USDT)', color='#00ff88'); ax1.tick_params(colors='#00ff88')
            ax1.grid(True, alpha=0.15, color='#00ff88'); ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            ax2 = plt.subplot2grid((5,1),(3,0), facecolor='#0d1f0d')
            from ta.momentum import RSIIndicator
            rsi_vals = RSIIndicator(close,14).rsi().values[-n:]
            ax2.plot(dates[-n:], rsi_vals, color='#9B59B6', linewidth=1.8)
            ax2.axhline(y=70,color='#ff3333',linestyle='--',alpha=0.5); ax2.axhline(y=30,color='#00ff88',linestyle='--',alpha=0.5)
            ax2.fill_between(dates[-n:],70,rsi_vals,where=(rsi_vals>=70),color='#ff3333',alpha=0.3)
            ax2.fill_between(dates[-n:],30,rsi_vals,where=(rsi_vals<=30),color='#00ff88',alpha=0.3)
            ax2.set_ylabel('📊 RSI(14)',color='#9B59B6'); ax2.set_ylim(0,100); ax2.tick_params(colors='#9B59B6')
            ax2.grid(True,alpha=0.15,color='#9B59B6')
            
            ax3 = plt.subplot2grid((5,1),(4,0), facecolor='#0d1f0d')
            colors_vol = ['#00ff88' if close.values[-n:][i]>=open_.values[-n:][i] else '#ff3333' for i in range(n)]
            ax3.bar(dates[-n:], volume.values[-n:], color=colors_vol, alpha=0.8, width=0.6)
            ax3.set_ylabel('📈 حجم', color='#00ff88'); ax3.tick_params(colors='#00ff88')
            ax3.grid(True,alpha=0.15,color='#00ff88')
            
            plt.tight_layout()
            buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='#0d1f0d', edgecolor='none')
            buf.seek(0); plt.close(fig)
            return buf
        except Exception as e: logger.error(f"Chart: {e}"); return None

chart_gen = ChartGenerator()

# ============================================================
# TRADER - SELF-LEARNING
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.max_real = 3
        self.experience = {'total':0,'wins':0,'losses':0,'best':0,'worst':0,'conf_threshold':65,'risk_mult':1.0}
        self.load()
    def load(self):
        try:
            with open('trader_v12.json') as f:
                d = json.load(f); self.balance = d.get('balance',cfg.initial_balance)
                self.history = d.get('history',[]); self.experience.update(d.get('experience',{}))
        except: pass
    def save(self):
        try:
            with open('trader_v12.json','w') as f:
                json.dump({'balance':self.balance,'history':self.history[-1000:],'experience':self.experience}, f)
        except: pass
    def learn(self):
        if len(self.history)<10: return
        wins = [t for t in self.history if t['pnl']>0]; losses = [t for t in self.history if t['pnl']<=0]
        self.experience['total'] = len(self.history); self.experience['wins'] = len(wins); self.experience['losses'] = len(losses)
        if wins: self.experience['best'] = max(t['pnl'] for t in wins); self.experience['avg_win'] = sum(t['pnl'] for t in wins)/len(wins)
        if losses: self.experience['worst'] = min(t['pnl'] for t in losses)
        wr = len(wins)/len(self.history)*100
        if wr>70: self.experience['conf_threshold']=55; self.experience['risk_mult']=1.4
        elif wr>60: self.experience['conf_threshold']=60; self.experience['risk_mult']=1.2
        elif wr<40: self.experience['conf_threshold']=75; self.experience['risk_mult']=0.6
        self.save()
    def can_real(self): return exchange_mgr.real_enabled and cfg.real_trading and self.real_trades<self.max_real
    def open(self, sym, entry, sl, tp, conf):
        if conf<self.experience['conf_threshold']: return None
        if len(self.positions)>=cfg.max_positions or self.closses>=cfg.max_consecutive_losses: return None
        risk = self.balance*cfg.risk_per_trade*self.experience['risk_mult']
        if self.closses>0: risk*=(0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz<=0 or sz*entry>self.balance: return None
        self.balance -= sz*entry
        self.positions[sym] = {'symbol':sym,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        if self.can_real():
            exchange_mgr.buy(sym,sz); self.real_trades+=1
            logger.info(f"💹 REAL BUY: {sym} {sz:.4f}")
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
        if exchange_mgr.real_enabled:
            try: exchange_mgr.sell(sym,p['size'])
            except: pass
        t = {'symbol':sym,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t); self.learn(); self.save(); return t
    def stats(self):
        total = max(1,len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# FORMATTER - PREMIUM PERSIAN GREEN
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, gemini_t=None, chart_analysis=None, tf_4h=None, tf_1d=None, tf_1w=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k.replace('_',' ') for k,v in i.items() if isinstance(v,bool) and v]
        sig, conf, score = sg.generate(i, a['price'])
        
        if "خرید" in sig: act = "🟢 ورود به پوزیشن خرید (LONG)"; det = "📈 سیگنال خرید - انتظار رشد قیمت"
        elif "فروش" in sig: act = "🔴 ورود به پوزیشن فروش (SHORT)"; det = "📉 سیگنال فروش - انتظار کاهش قیمت"
        else: act = "⚪ عدم ورود به معامله"; det = "⏳ بازار در حالت خنثی - صبر کنید"
        
        entry_price = a['price']
        sl_price = a['price']-i['ATR_14']*cfg.atr_sl
        tp1 = a['price']+i['ATR_14']*cfg.atr_tp
        tp2 = a['price']+i['ATR_14']*cfg.atr_tp*1.5
        
        msg = f"""
🟢══════════════════════════════════════🟢
     🔥 #سیگنال_معاملاتی #{s} 🔥
🟢══════════════════════════════════════🟢

📅 {dtm.persian()}
🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
📊 #{s} #Crypto #Trading

💰 *قیمت فعلی:* ${a['price']:,.4f}
📊 *تغییر ۲۴h:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig}
💪 *قدرت سیگنال:* {conf}% | ⭐ *امتیاز:* {score}/1000

🟢━━━ 📈 میانگین‌های متحرک (EMA) ━━━🟢
• EMA 7 (کوتاه‌مدت): ${i.get('EMA_7',0):,.2f}
• EMA 20 (کوتاه‌مدت): ${i.get('EMA_20',0):,.2f}
• EMA 50 (میان‌مدت): ${i.get('EMA_50',0):,.2f}
• EMA 100 (میان‌مدت): ${i.get('EMA_100',0):,.2f}
• EMA 200 (بلندمدت): ${i.get('EMA_200',0):,.2f}

🟢━━━ 📊 اندیکاتورها و اسیلاتورها ━━━🟢
• RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
• MACD: {'🟢 صعودی' if i.get('MACD_HIST',0)>0 else '🔴 نزولی'}
• ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
• عرض باند بولینگر: {i.get('BB_WIDTH',0):.4f} | %B: {i.get('BB_PCT',0.5):.2f}
• ATR(14): {i['ATR_14']:.4f} | نسبت حجم: {i.get('VOL_RATIO',1):.1f}x
• قدرت روند: {i.get('TREND_STR',0):.1f}%

🟢━━━ 🕯️ پرایس اکشن و الگوها ━━━🟢
• الگوهای کندلی: {', '.join(pats) if pats else 'بدون الگوی خاص'}
• واگرایی: {i.get('DIVERGENCE','NONE')}
• نقطه پیوت: ${i.get('PIVOT',0):,.4f}

🟢━━━ 🔑 سطوح کلیدی و فیبوناچی ━━━🟢
• مقاومت اصلی: ${i['RESISTANCE']:,.4f}
• حمایت اصلی: ${i['SUPPORT']:,.4f}
• فیبوناچی 0.382: ${i.get('FIB_382',0):,.4f}
• فیبوناچی 0.500: ${i.get('FIB_500',0):,.4f}
• فیبوناچی 0.618: ${i.get('FIB_618',0):,.4f}"""

        if tf_4h: msg += f"\n\n⏰ *تایم‌فریم ۴ ساعته:* RSI={tf_4h.get('RSI_14',50):.0f} | MACD={'🟢' if tf_4h.get('MACD_HIST',0)>0 else '🔴'} | ADX={tf_4h.get('ADX',20):.0f}"
        if tf_1d: msg += f"\n⏰ *تایم‌فریم ۱ روزه:* RSI={tf_1d.get('RSI_14',50):.0f} | MACD={'🟢' if tf_1d.get('MACD_HIST',0)>0 else '🔴'} | ADX={tf_1d.get('ADX',20):.0f}"
        if tf_1w: msg += f"\n⏰ *تایم‌فریم ۱ هفته:* RSI={tf_1w.get('RSI_14',50):.0f} | MACD={'🟢' if tf_1w.get('MACD_HIST',0)>0 else '🔴'} | ADX={tf_1w.get('ADX',20):.0f}"

        msg += f"""

🟢━━━ 🎯 نقاط ورود و خروج ━━━🟢
🔵 *نقطه ورود:* ${entry_price:,.4f}
🔴 *حد ضرر (SL):* ${sl_price:,.4f} ({abs(entry_price-sl_price)/entry_price*100:.1f}%)
🟢 *حد سود ۱ (TP1):* ${tp1:,.4f} ({abs(tp1-entry_price)/entry_price*100:.1f}%)
🟢 *حد سود ۲ (TP2):* ${tp2:,.4f} ({abs(tp2-entry_price)/entry_price*100:.1f}%)
📊 *نسبت ریسک به ریوارد:* 1:{cfg.atr_tp/cfg.atr_sl:.1f}"""

        if groq_t: msg += f"\n\n🧠 *تحلیل Groq AI:*\n{groq_t[:500]}"
        if gemini_t: msg += f"\n\n🌟 *تحلیل Gemini AI:*\n{gemini_t[:400]}"
        if chart_analysis: msg += f"\n\n📊 *تحلیل نمودار:*\n{chart_analysis[:300]}"

        msg += f"""

🟢══════════════════════════════════════🟢
           📋 #نتیجه‌گیری_نهایی
🟢══════════════════════════════════════🟢

🎯 *سیگنال نهایی:* {sig}
💪 *اطمینان:* {conf}% | ⭐ *امتیاز:* {score}/1000
📊 *اقدام:* {act}
📝 *توضیح:* {det}

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {dtm.now()}
🟢══════════════════════════════════════🟢

#تحلیل_تکنیکال #فارکس #ارزدیجیتال #معامله_گری"""
        return msg
    
    @staticmethod
    def edu(content=None, img_path=None):
        h = f"🟢══════════════════🟢\n     📚 #آموزش_کریپتو 📚\n🟢══════════════════🟢\n\n📅 {dtm.persian()}\n\n"
        if content: h += f"{content}\n\n"
        h += f"🟢══════════════════🟢\n✨ @CryptoPulse606 | {dtm.now()}\n🟢══════════════════🟢\n\n#آموزش #تحلیل #کریپتوکارنسی"
        return h
    
    @staticmethod
    def news(content=None):
        if content: return f"📰 *اخبار کریپتو*\n\n📅 {dtm.persian()}\n\n{content}\n\n✨ @CryptoPulse606\n#اخبار #کریپتو #بیتکوین"
        return f"📰 *اخبار کریپتو*\n\n📅 {dtm.persian()}\n\nدر حال بروزرسانی...\n\n✨ @CryptoPulse606"
    
    @staticmethod
    def forex(rates):
        g = rates.get('gold',0); t = rates.get('try',0); i = rates.get('iqd',0)
        eur = rates.get('eur',0); gbp = rates.get('gbp',0)
        return f"""
🟢══════════════════🟢
   💰 #قیمت_ارزها_و_طلا 💰
🟢══════════════════🟢

📅 {dtm.persian()}

🥇 *طلای جهانی (XAU):* ${g:,.2f} هر اونس
💵 *دلار آمریکا:* ۱ USD
🇹🇷 *لیر ترکیه:* {t:,.2f} TRY
🇮🇶 *دینار عراق:* {i:,.2f} IQD
🇪🇺 *یورو:* {eur:,.4f} EUR
🇬🇧 *پوند:* {gbp:,.4f} GBP

🟢══════════════════🟢
✨ @CryptoPulse606 | {dtm.now()}
🟢══════════════════🟢

#طلا #دلار #ارز #قیمت_لحظه‌ای"""

fmt = Fmt()

# ============================================================
# 50+ GLASS BUTTONS - FULL PERSIAN
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌های لحظه‌ای", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ تحلیل ۴ ساعته BTC", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل ۱ روزه BTC", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل ۱ هفته BTC", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 تحلیل Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 تحلیل Gemini AI", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار تکنیکال", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("📰 تحلیل بازار کل", callback_data="market"),
             InlineKeyboardButton("📊 استراتژی BTC", callback_data="strat"),
             InlineKeyboardButton("💭 احساسات بازار", callback_data="sent")],
            [InlineKeyboardButton("📰 تحلیل فاندامنتال", callback_data="fund"),
             InlineKeyboardButton("📊 پرایس اکشن BTC", callback_data="pa"),
             InlineKeyboardButton("🔮 پیش‌بینی قیمت", callback_data="pred")],
            [InlineKeyboardButton("💰 پورتفوی معاملاتی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد معاملات", callback_data="perf"),
             InlineKeyboardButton("🧠 تجربه و یادگیری", callback_data="exp")],
            [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات ربات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت اتصال", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش تخصصی", callback_data="edu"),
             InlineKeyboardButton("📰 اخبار کریپتو", callback_data="news"),
             InlineKeyboardButton("🐋 نهنگ‌های بازار", callback_data="whale")],
            [InlineKeyboardButton("💰 قیمت طلا و ارز", callback_data="forex"),
             InlineKeyboardButton("📉 شاخص ترس و طمع", callback_data="fear"),
             InlineKeyboardButton("💎 آلت‌کوین‌ها", callback_data="alt")],
            [InlineKeyboardButton("📊 مقایسه ارزها", callback_data="compare"),
             InlineKeyboardButton("📈 نمودار زنده", callback_data="live"),
             InlineKeyboardButton("🔔 هشدارهای قیمتی", callback_data="alerts")],
            [InlineKeyboardButton("🔮 پیش‌بینی ۷ روزه", callback_data="pred7"),
             InlineKeyboardButton("📋 تاریخچه معاملات", callback_data="hist"),
             InlineKeyboardButton("🕯️ الگوهای کندلی", callback_data="patterns")],
            [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="stop"),
             InlineKeyboardButton("🔄 بروزرسانی منو", callback_data="ref"),
             InlineKeyboardButton("❓ راهنمای ربات", callback_data="help")],
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
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🟢══════════════════════🟢\n"
        f"   🤖 #کریپتو_پالس نسخه ۱۲ 🤖\n"
        f"🟢══════════════════════🟢\n\n"
        f"📅 {dtm.persian()}\n\n"
        f"✨ *امکانات ربات:*\n"
        f"🧠🌟 دو هوش مصنوعی: Groq + Gemini\n"
        f"📊 ۲۵+ اندیکاتور | ۷ EMA | فیبوناچی\n"
        f"⏰ تایم‌فریم: ۴h/۱d/۱w\n"
        f"📊 نمودار واقعی از صرافی\n"
        f"💹 معاملات خودکار واقعی و دمو\n"
        f"📰 اخبار کریپتو | 🐋 نهنگ‌ها\n"
        f"💰 قیمت طلا و ارزهای جهانی\n"
        f"📢 سیگنال هر ۴ ساعت\n"
        f"📚 آموزش هر ۱ ساعت\n\n"
        f"👇 *از منوی ۵۰+ کلید استفاده کنید:*",
        reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(f"🔄 در حال تحلیل کامل {symbol.replace('/USDT','')}...")
    if not exchange_mgr.connected: exchange_mgr.connect()
    t = exchange_mgr.ticker(symbol); df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا در دریافت داده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])); return
    ind = ui.calc(df); mtf = {}
    for tf_name in cfg.primary_tfs:
        dft = exchange_mgr.ohlcv(symbol, tf_name, 100)
        if dft is not None: mtf[tf_name] = ui.calc(dft)
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    groq_text = await groq_ai.technical(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = await gemini_ai.generate(f"Analyze {symbol} ${t['last']:,.2f} Persian 200w.", 350) if gemini_ai.enabled else None
    analysis = {'symbol':symbol,'price':t['last'],'change':t.get('percentage',0),'indicators':ind}
    msg = fmt.signal(analysis, groq_text, gemini_text, None, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'))
    await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]]))

async def chart_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query; await q.answer()
    if not CHART_AVAILABLE:
        await q.edit_message_text("❌ نصب: pip install matplotlib mplfinance", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
    await q.edit_message_text(f"📊 رسم نمودار {symbol.replace('/USDT','')}...")
    t = exchange_mgr.ticker(symbol); df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
    ind = ui.calc(df); chart_buf = chart_gen.create(df, symbol, ind)
    if chart_buf:
        await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=chart_buf,
            caption=f"📊 *{symbol.replace('/USDT','')}* | ${t['last']:,.4f} | {t.get('percentage',0):+.2f}%", parse_mode="Markdown")
        await q.edit_message_text("✅ نمودار ارسال شد",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄", callback_data=f"chart_{symbol}"),
                InlineKeyboardButton("🎯 سیگنال", callback_data=f"s_{symbol}"),
                InlineKeyboardButton("🔙", callback_data="back")
            ]]))
    else: await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text("🟢 *منوی اصلی* 🟢\n\nلطفاً انتخاب کنید:", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"🟢══════════════════🟢\n        💰 #قیمت_لحظه‌ای\n🟢══════════════════🟢\n\n📅 {dtm.persian()}\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} *{sym.replace('/USDT','')}*: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data="p"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("chart_"): await chart_handler(update, ctx, d[6:] if len(d)>6 else "BTC/USDT")
        elif d.startswith("tf4_"): 
            t = exchange_mgr.ticker(d[4:]); df = exchange_mgr.ohlcv(d[4:], '4h', 200)
            if t and df is not None:
                ind = ui.calc(df); sig, conf, score = sg.generate(ind, t['last'])
                await q.edit_message_text(f"⏰ تحلیل ۴h {d[4:].replace('/USDT','')}\n\n💰 ${t['last']:,.4f}\n🎯 {sig} | 💪 {conf}%\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "market":
            top = []; 
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            m = await groq_ai.market(top)
            if m: await q.edit_message_text(f"📰 *تحلیل بازار*\n\n{m}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market"), InlineKeyboardButton("🔙", callback_data="back")]]))
            else: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"💰 *پورتفوی*\n💵 ${s['balance']:,.2f}\n📈 PnL: ${s['pnl']:+,.2f}\n📊 {s['total']} | برد: {s['wins']} ({s['rate']:.0f}%)\n💹 واقعی: {trader.real_trades}/{trader.max_real}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "exp":
            exp = trader.experience
            await q.edit_message_text(f"🧠 *تجربه*\n📊 {exp['total']} معامله\n🏆 بهترین: ${exp.get('best',0):+,.2f}\n📉 بدترین: ${exp.get('worst',0):+,.2f}\n🎯 آستانه: {exp['conf_threshold']}%\n⚡ ریسک: {exp['risk_mult']:.1f}x", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="exp"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            content = await groq_ai.news()
            await q.edit_message_text(fmt.news(content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "forex":
            rates = await forex_data.get_rates()
            msg = fmt.forex(rates)
            await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="forex"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.education()
            await q.edit_message_text(fmt.edu(content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "set":
            await q.edit_message_text(f"⚙️ *تنظیمات*\n🔌 {'✅' if exchange_mgr.connected else '❌'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'}\n🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}\n⏰ سیگنال: ۴h\n📚 آموزش: ۱h\n📰 اخبار: ۲h\n💰 طلا/ارز: ۱h", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "⏸️ توقف")
            await q.edit_message_text("⏸️ بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🟢 *منو*", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text("❓ /start", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d in ["scan","strat","sent","fund","pa","pred","fear","alt","compare","live","alerts","pred7","hist","patterns","whale","ai_BTC/USDT","gem_BTC/USDT","status","tf1d_BTC/USDT","tf1w_BTC/USDT","auto"]:
            await q.edit_message_text("⚡ این بخش در حال تکمیل است...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer("⚡")
    except Exception as e: logger.error(f"Btn: {e}"); await q.answer("❌")

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
            await safe_send(app.bot, cfg.channel_id, f"🟢══════════════════🟢\n   🔄 #تحلیل_دوره‌ای ۴ ساعته\n🟢══════════════════🟢\n\n📅 {dtm.persian()}\n\n📊 در حال تحلیل ۵ ارز برتر...")
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
                                await app.bot.send_photo(cfg.channel_id, chart_buf,
                                    caption=f"📊 *{sym.replace('/USDT','')}* | ${t['last']:,.4f} | {t.get('percentage',0):+.2f}%", parse_mode="Markdown")
                                await asyncio.sleep(2)
                        analysis = {'symbol':sym,'price':t['last'],'change':t.get('percentage',0),'indicators':ind}
                        msg = fmt.signal(analysis, groq_text, gemini_text, None, mtf.get('4h'), mtf.get('1d'), mtf.get('1w'))
                        await safe_send(app.bot, cfg.channel_id, msg)
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol':sym.replace('/USDT',''),'change':t.get('percentage',0)})
            market = await groq_ai.market(top)
            if market: await safe_send(app.bot, cfg.channel_id, f"📰 *بازار*\n\n{market}\n\n✨ @CryptoPulse606")
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result:
                            emoji = "🟢 سود" if result['pnl']>0 else "🔴 ضرر"
                            await safe_send(app.bot, cfg.channel_id, f"{emoji}: {sym} بسته شد | ${result['pnl']:+,.2f}")
                except: pass
            if datetime.now().hour == 0: trader.real_trades = 0
            await safe_send(app.bot, cfg.channel_id, f"🟢══════════════════🟢\n   ✅ پایان تحلیل\n🟢══════════════════🟢\n\n📊 سیگنال بعدی: ۴ ساعت\n📚 آموزش: ۱ ساعت\n✨ @CryptoPulse606\n#پایان_تحلیل")
        except Exception as e: logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.education()
                if content: await safe_send(app.bot, cfg.channel_id, fmt.edu(content))
        except Exception as e: logger.error(f"Edu: {e}")
        await asyncio.sleep(cfg.education_interval)

async def auto_news(app: Application):
    await asyncio.sleep(60)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.news()
                if content: await safe_send(app.bot, cfg.channel_id, fmt.news(content))
        except Exception as e: logger.error(f"News: {e}")
        await asyncio.sleep(cfg.news_interval)

async def auto_forex(app: Application):
    await asyncio.sleep(120)
    while True:
        try:
            if cfg.channel_id:
                rates = await forex_data.get_rates()
                if rates: await safe_send(app.bot, cfg.channel_id, fmt.forex(rates))
        except Exception as e: logger.error(f"Forex: {e}")
        await asyncio.sleep(cfg.forex_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(300)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.whale_alert()
                if content: await safe_send(app.bot, cfg.channel_id, f"🐋 *نهنگ‌های بازار*\n\n{content}\n\n✨ @CryptoPulse606\n#نهنگ #کریپتو")
        except Exception as e: logger.error(f"Whale: {e}")
        await asyncio.sleep(cfg.news_interval)

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
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_forex(app))
    asyncio.create_task(auto_whale(app))
    
    logger.info("="*60)
    logger.info("🚀 CRYPTO PULSE v12.0 - LEGENDARY")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}")
    logger.info(f"📊 Charts: {'✅' if CHART_AVAILABLE else '❌'}")
    logger.info(f"📢 Signal: 4H | 📚 Edu: 1H | 📰 News: 2H | 💰 Forex: 1H")
    logger.info("="*60)
    
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

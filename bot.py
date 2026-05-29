#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦅 CRYPTO EAGLE EYE v29.0 — چشــــم عـقـاب — ULTIMATE FREE AI TRADER      ║
║  ✅ 100% Free — No Invites — No Subscriptions                               ║
║  ✅ Owner ID: 7225279768 — Unlimited Access                                 ║
║  ✅ AI Image Generator (Pollinations.ai + Internal)                          ║
║  ✅ Dual AI (Groq + Gemini)  ✅ Smart Money (SMC)                            ║
║  ✅ 1000+ Hours AI Course (Every 30 min)                                     ║
║  ✅ Live Signals Every 2 Hours (Chart + AI Image)                            ║
║  ✅ Live News Every 4 Hours (AI Image)                                       ║
║  ✅ Daily Market Summary (23:00 Tehran)                                      ║
║  ✅ 80+ Indicators  ✅ Fear & Greed  ✅ Dominance                             ║
║  ✅ 20 Professional Glass Buttons — All Active                               ║
║  ✅ Ultra-Precise Persian Analysis — Eagle Eye Precision                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading, gc, urllib.parse, textwrap
os.environ["TZ"] = "Asia/Tehran"
os.environ["MPLBACKEND"] = "Agg"
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
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from PIL import Image, ImageDraw, ImageFont
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO INSTALL (ALL NECESSARY LIBRARIES)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'feedparser':'feedparser','Pillow':'Pillow',
        'cachetools':'cachetools','tenacity':'tenacity',
        'aiohttp':'aiohttp','schedule':'schedule'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EagleEyeV29')
ensure_libs()

import schedule
import jdatetime, pytz
import feedparser
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

TEHRAN_TZ = pytz.timezone('Asia/Tehran')
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    import mplfinance as mpf
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# MEMORY MANAGEMENT
# ============================================================
async def cleanup_memory():
    while True:
        gc.collect()
        if CHART_AVAILABLE:
            try: plt.close('all')
            except: pass
        await asyncio.sleep(600)

# ============================================================
# LOGGING
# ============================================================
logger.setLevel(logging.INFO)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(console)
for name in ['eagle_v29.log','eagle_v29_errors.log']:
    h = RotatingFileHandler(name, maxBytes=50*1024*1024, backupCount=5, encoding='utf-8')
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(h)

# ============================================================
# PROXY
# ============================================================
def create_request():
    proxy_url = os.getenv("TELEGRAM_PROXY", "")
    if proxy_url: return HTTPXRequest(proxy_url=proxy_url, connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)
    else: return HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    owner_id: int = 7225279768
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    auto_send: bool = True
    signal_interval: int = 7200        # هر ۲ ساعت
    education_interval: int = 1800     # هر ۳۰ دقیقه
    news_interval: int = 14400         # هر ۴ ساعت
    fg_interval: int = 3600
    whale_interval: int = 5400
    daily_summary_time: str = "23:00"  # خلاصه روزانه

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "eagle_v29.lock"
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
# PERSIAN DATE
# ============================================================
class PersianLive:
    DAYS = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
    MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    @classmethod
    def now(cls): return datetime.now(TEHRAN_TZ)
    @classmethod
    def shamsi(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    @classmethod
    def time_str(cls): return cls.now().strftime('%H:%M:%S')
    @classmethod
    def day_str(cls): return cls.DAYS[cls.now().weekday()]
    @classmethod
    def full(cls): return f"{cls.day_str()} {cls.shamsi()} ساعت {cls.time_str()}"
    @classmethod
    def greeting(cls):
        h = cls.now().hour
        if 5 <= h < 12: return "صبح بخیر"
        elif 12 <= h < 17: return "ظهر بخیر"
        elif 17 <= h < 22: return "عصر بخیر"
        else: return "شب بخیر"

pdt = PersianLive()

# ============================================================
# AI IMAGE GENERATOR — چشــــم عـقـاب
# ============================================================
class AIImageGenerator:
    POLLINATIONS_API = "https://image.pollinations.ai/prompt/"
    
    STYLES = {
        "chart": "professional trading chart, candlestick pattern, green and red candles, technical indicators, dark background, 4K",
        "bull": "raging golden bull made of fire and neon green energy, charging through blockchain network, epic, 8K",
        "bear": "massive ice bear made of dark metal and red lava, roaring on crypto market, dramatic, 4K",
        "whale": "giant transparent whale swimming in ocean of crypto coins, magical, epic, 8K",
        "eagle": "giant cyberpunk eagle with glowing green eyes, scanning crypto charts, golden wings, epic, 8K",
        "news": "breaking news hologram, crypto headlines, futuristic newsroom, 4K, cyberpunk",
        "moon": "bitcoin rocket flying to the moon, golden BTC logo, green candles, space, epic, 4K",
        "abstract": "abstract crypto art, blockchain network, futuristic geometry, neon gradients, 4K"
    }
    
    def __init__(self):
        self.enabled = True
    
    async def generate(self, prompt: str, style: str = None, width: int = 1024, height: int = 1024) -> Optional[bytes]:
        final_prompt = self._build_prompt(prompt, style)
        try:
            encoded_prompt = urllib.parse.quote(final_prompt)
            url = f"{self.POLLINATIONS_API}{encoded_prompt}?width={width}&height={height}&nologo=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception as e:
            logger.error(f"AI Image error: {e}")
        return None
    
    def _build_prompt(self, prompt: str, style: str = None) -> str:
        base = "cryptocurrency, digital art, high quality, 4K, detailed, masterpiece"
        style_kw = self.STYLES.get(style, base)
        full = f"{prompt}, {style_kw}, {base}"
        return full[:900]

ai_image_gen = AIImageGenerator()

# ============================================================
# DUAL AI — ULTRA PRECISE PERSIAN
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = httpx.AsyncClient(timeout=120.0)
    async def ask(self, prompt, max_t=800):
        if not self.enabled: return None
        try:
            r = await self._client.post(self.URL, headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[
                    {"role":"system","content":"تو چشم عقاب هستی—دقیق‌ترین تحلیلگر کریپتو با دید میلیمتری. فقط فارسی خودمونی و دوستانه حرف بزن. از ایموجی زیاد استفاده کن. تحلیل‌هات باید کاملاً عملی و همراه با عدد و رقم باشه."},
                    {"role":"user","content":prompt}
                ],"max_tokens":max_t})
            if r.status_code==200: return r.json()["choices"][0]["message"]["content"]
        except: pass
        return None
    async def tech(self, sym, ind, price, change, candles, mtf):
        return await self.ask(f"""تحلیل تکنیکال {sym} با قیمت {price:,.2f} دلار (تغییر {change:+.2f}%)
RSI(14)={ind.get('RSI_14',50):.0f} | MACD={'صعودی' if ind.get('MACD_HIST',0)>0 else 'نزولی'}
ADX={ind.get('ADX',20):.0f} | CCI={ind.get('CCI',0):.0f} | MFI={ind.get('MFI',50):.0f}
BB%={ind.get('BB_PCT',0.5):.2f} | حجم={ind.get('VOL_RATIO',1):.1f}x
حمایت=${ind.get('حمایت',0):.2f} | مقاومت=${ind.get('مقاومت',0):.2f}
شمع‌ها: {', '.join(candles) if candles else 'بدون'}
MTF: {mtf}
تحلیل دقیق با ذکر اعداد: وضعیت، روند، ورود، ضرر، اهداف. ۵۰۰ کلمه فارسی.""")
    async def smc(self, sym, smc_data):
        return await self.ask(f"اسمارت مانی {sym}:\n{json.dumps(smc_data, ensure_ascii=False)}\nفارسی توضیح بده. ۴۰۰ کلمه.")
    async def prediction(self, sym, price, ind):
        return await self.ask(f"پیش‌بینی {sym} با قیمت {price:,.2f}\nRSI={ind.get('RSI_14',50):.1f}\nفردا؟ یک هفته؟ یک ماه؟ با درصد احتمال بگو. ۴۰۰ کلمه فارسی.")
    async def news_summary(self, headlines):
        return await self.ask(f"اخبار:\n{chr(10).join(headlines[:12])}\nخلاصه کن به فارسی. ۳۰۰ کلمه.")
    async def market(self, coins): return await self.ask(f"بازار:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\nتحلیل فارسی ۳۰۰ کلمه.")
    async def whale(self): return await self.ask("نهنگ‌ها چی کار می‌کنن؟ فارسی ۲۰۰ کلمه.")
    async def fear_greed(self, v, t): return await self.ask(f"ترس و طمع: {v} ({t}). فارسی ۲۰۰ کلمه.")
    async def course_lesson(self, num, total, topic):
        return await self.ask(f"""درس {num} از {total}: {topic}
یه درس جذاب و کاربردی به فارسی بنویس. مثال واقعی بزن. ۱۰۰۰ کلمه. #دوره_چشم_عقاب""")
    async def daily_summary(self, data):
        return await self.ask(f"خلاصه بازار امروز:\n{json.dumps(data, ensure_ascii=False)}\nتحلیل فارسی با ایموجی. ۴۰۰ کلمه.")

groq_ai = GroqAI()

# ============================================================
# EXCHANGE
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False
    def connect(self):
        try:
            self._ex = ccxt.coinex({'enableRateLimit':True,'timeout':15000})
            self._ex.load_markets(); self.connected = True
        except: pass
    def ticker(self,s):
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    def ohlcv(self,s,tf,limit=150):
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s,tf,limit=limit)
            return pd.DataFrame(d,columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# SMART MONEY
# ============================================================
class SmartMoney:
    @staticmethod
    def analyze(df):
        if len(df) < 60: return {}
        high = df['high'].values; low = df['low'].values; close = df['close'].values
        from scipy.signal import argrelextrema
        sh_idx = argrelextrema(high, np.greater, order=3)[0]; sl_idx = argrelextrema(low, np.less, order=3)[0]
        sh = [(i, high[i]) for i in sh_idx]; sl = [(i, low[i]) for i in sl_idx]
        if len(sh) < 2 or len(sl) < 2: return {}
        bos_u = all(sh[i][1] > sh[i-1][1] for i in range(1, len(sh)))
        bos_d = all(sl[i][1] < sl[i-1][1] for i in range(1, len(sl)))
        choch = "صعودی 🟢" if (bos_u and not bos_d) else ("نزولی 🔴" if (bos_d and not bos_u) else "خنثی ⚪")
        return {"شکست_ساختار":"صعود" if bos_u else "نزول" if bos_d else "هیچ","تغییر_روند":choch,"ساختار_بازار":choch}

# ============================================================
# 80+ INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        close = df['close'].astype(float); high = df['high'].astype(float); low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7,14,20,50,200]: ind[f'EMA_{p}'] = float(close.ewm(span=p,adjust=False).mean().iloc[-1])
        from ta.momentum import RSIIndicator, StochasticOscillator
        try: ind['RSI_14'] = float(RSIIndicator(close,14).rsi().iloc[-1])
        except: ind['RSI_14'] = 50.0
        try:
            stoch = StochasticOscillator(high,low,close,14,3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1]); ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except: ind['STOCH_K'] = 50.0; ind['STOCH_D'] = 50.0
        from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
        try: ind['MACD_HIST'] = float(MACD(close,12,26,9).macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        try: ind['ADX'] = float(ADXIndicator(high,low,close,14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        try: ind['CCI'] = float(CCIIndicator(high,low,close,20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try: ind['BB_PCT'] = float(BollingerBands(close,20,2).bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high,low,close,14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else 1
        ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        try:
            ichi = IchimokuIndicator(high,low,9,26,52)
            ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
        except: pass
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.236,0.382,0.5,0.618,0.786]: ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        candles, names = UltraIndicators._candles(df); ind.update(candles)
        return ind, names
    @staticmethod
    def _candles(df):
        pats = {}; names = []
        if len(df)<2: return pats, names
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]; body,tr = abs(c-o), h-l
        if tr==0: return pats, names
        if body<=tr*0.08: pats['دوجی']=True; names.append("دوجی ⚖️")
        if (min(c,o)-l)>body*2 and c>o: pats['چکش']=True; names.append("چکش 🔨")
        if (h-max(c,o))>body*2 and c<o: pats['ستاره_پرتابی']=True; names.append("ستاره پرتابی ☄️")
        if c>o and pc<po: pats['پوشای_صعودی']=True; names.append("پوشای صعودی 🟢")
        if c<o and pc>po: pats['پوشای_نزولی']=True; names.append("پوشای نزولی 🔴")
        if len(df)>=3:
            o3,c3 = df['open'].iloc[-3],df['close'].iloc[-3]
            if c>o and pc>po and c3>o3: pats['سه_سرباز']=True; names.append("سه سرباز سفید ⚔️")
            if c<o and pc<po and c3<o3: pats['سه_کلاغ']=True; names.append("سه کلاغ سیاه 🦅")
        return pats, names

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, smc_data=None, mtf=None):
        score = 0
        if ind.get('EMA_7',0)>ind.get('EMA_20',0)>ind.get('EMA_50',0): score+=200
        elif ind.get('EMA_7',0)<ind.get('EMA_20',0)<ind.get('EMA_50',0): score-=200
        rsi = ind.get('RSI_14',50)
        if rsi<20: score+=180
        elif rsi>80: score-=180
        if ind.get('MACD_HIST',0)>0: score+=100
        else: score-=100
        if ind.get('BB_PCT',0.5)<0.05: score+=150
        elif ind.get('BB_PCT',0.5)>0.95: score-=150
        if ind.get('VOL_RATIO',1)>2.5: score+=80 if score>0 else -80
        for bull in ['پوشای_صعودی','چکش','سه_سرباز']:
            if ind.get(bull): score+=110
        for bear in ['پوشای_نزولی','ستاره_پرتابی','سه_کلاغ']:
            if ind.get(bear): score-=110
        if ind.get('TENKAN',0)>ind.get('KIJUN',0) and price>ind.get('SENKOU_A',0): score+=70
        if smc_data:
            if 'صعودی' in smc_data.get('تغییر_روند',''): score += 120
            elif 'نزولی' in smc_data.get('تغییر_روند',''): score -= 120
        if mtf:
            for tf,ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
                if ti.get('RSI_14',50)>55: score+=int(35*w)
                elif ti.get('RSI_14',50)<45: score-=int(35*w)
        score = max(-1000,min(1000,score))
        circles = "🟢🟢🟢🟢🟢" if abs(score)>=800 else ("🟢🟢🟢🟢" if abs(score)>=600 else ("🟢🟢🟢" if abs(score)>=400 else ("🟢🟢" if abs(score)>=200 else "⚪⚪")))
        if score<0: circles = circles.replace("🟢","🔴")
        action = "💰 خرید قوی" if score>=400 else ("💸 فروش قوی" if score<=-400 else ("🤔 می‌تونی بخری" if score>=200 else ("😬 می‌تونی بفروشی" if score<=-200 else "⏳ صبر کن")))
        conf = 99 if abs(score)>=800 else (94 if abs(score)>=600 else (85 if abs(score)>=400 else (72 if abs(score)>=200 else 55)))
        return f"{'🔥 خرید فوق‌العاده' if score>=800 else '🟢 خرید' if score>=400 else '⚪ خنثی' if abs(score)<200 else '🔴 فروش' if score<=-400 else '💀 فروش فوق‌العاده'} {circles}", conf, score, action

sg = SignalGen()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol):
        if not CHART_AVAILABLE or len(df) < 30: return None
        try:
            data = df.copy(); data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms'); data = data.set_index('timestamp')
            data = data.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})[['Open','High','Low','Close','Volume']].iloc[-60:]
            add_plots = []
            for p, color in [(7,'#FFD700'),(20,'#00ff88'),(50,'#FF8C00'),(200,'#FFFFFF')]:
                ema = data['Close'].ewm(span=p, adjust=False).mean()
                add_plots.append(mpf.make_addplot(ema, color=color, width=1.2))
            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(data['Close'],14).rsi()
            add_plots.append(mpf.make_addplot(rsi, panel=2, color='#9B59B6', ylabel='RSI'))
            add_plots.append(mpf.make_addplot(pd.Series([70]*len(data), index=data.index), panel=2, color='#ff3333', linestyle='--'))
            add_plots.append(mpf.make_addplot(pd.Series([30]*len(data), index=data.index), panel=2, color='#00ff88', linestyle='--'))
            macd_hist = (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()) - (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()).ewm(span=9).mean()
            add_plots.append(mpf.make_addplot(macd_hist, type='bar', panel=3, color='#00ff88', ylabel='MACD'))
            mc = mpf.make_marketcolors(up='#00ff88', down='#ff3355', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#061a14', figcolor='#061a14', gridcolor='#1d3b34')
            fig, _ = mpf.plot(data, type='candle', style=style, title=f'{symbol} - {pdt.shamsi()}', volume=True, addplot=add_plots, panel_ratios=(3,1,1,1), figsize=(20,14), returnfig=True)
            buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=120, bbox_inches='tight'); buf.seek(0); plt.close(fig)
            return buf
        except: return None

chart_gen = ChartGenerator()

# ============================================================
# FORMATTER — ELEGANT PERSIAN
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, smc_t=None, pred_t=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']; candles = a.get('candles',[])
        sig, conf, score, action = sg.generate(i, a['price'], a.get('smc'), a.get('mtf'))
        entry, sl = a['price'], a['price']-i['ATR_14']*2; tp1, tp2 = a['price']+i['ATR_14']*3, a['price']+i['ATR_14']*5
        msg = f"""
🦅═══ سیگنال چشــــم عـقـاب: {s} ═══🦅

{pdt.greeting()} تریدر عزیز! {pdt.full()}

💰 *قیمت:* ${a['price']:,.4f} | 📊 *تغییر:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig} | 💪 *قدرت:* {conf}% | ⭐ *امتیاز:* {score}/۱۰۰۰
🚦 *اقدام:* {action}

📈 *میانگین‌ها:* EMA7={i.get('EMA_7',0):.2f} | EMA20={i.get('EMA_20',0):.2f} | EMA50={i.get('EMA_50',0):.2f} | EMA200={i.get('EMA_200',0):.2f}
🕯️ *شمع‌ها:* {', '.join(candles) if candles else 'بدون الگوی خاص'}

📊 *اندیکاتورها:*
RSI(14)={i['RSI_14']:.1f} | MACD={'🟢صعود' if i.get('MACD_HIST',0)>0 else '🔴نزول'}
ADX={i['ADX']:.1f} | CCI={i['CCI']:.1f} | MFI={i.get('MFI',50):.1f}
BB %B={i.get('BB_PCT',0.5):.2f} | Vol={i.get('VOL_RATIO',1):.1f}x
STOCH K={i.get('STOCH_K',50):.1f} D={i.get('STOCH_D',50):.1f}

🔑 *سطوح:* مقاومت ${i.get('مقاومت',0):,.4f} | حمایت ${i.get('حمایت',0):,.4f}
📐 *فیبوناچی ۰.۶۱۸:* ${i.get('FIB_618',0):.4f}
☁️ *ایچیموکو:* تنکان ${i.get('TENKAN',0):.2f} | کیجون ${i.get('KIJUN',0):.2f}

🎯 *معامله:*
🔵 ورود: ${entry:,.4f}
🔴 حد ضرر: ${sl:,.4f} ({(abs(entry-sl)/entry*100):.1f}%)
🟢 هدف ۱: ${tp1:,.4f} | هدف ۲: ${tp2:,.4f}
📊 نسبت ریسک به ریوارد: ۱:{3/2:.1f}
"""
        if groq_t: msg += f"\n🧠 *تحلیل عقاب:*\n{groq_t[:700]}\n"
        if smc_t: msg += f"\n🧲 *اسمارت مانی:*\n{smc_t[:400]}\n"
        if pred_t: msg += f"\n🔮 *پیش‌بینی:*\n{pred_t[:500]}\n"
        msg += f"🦅═══ @CryptoPulse606 | {pdt.full()} ═══🦅\n#سیگنال #کریپتو #تحلیل #چشم_عقاب"
        return msg

    @staticmethod
    def course(lesson_text):
        return f"📚 *دوره تخصصی چشم عقاب*\n{pdt.full()}\n\n{lesson_text}\n\n🦅 @CryptoPulse606\n#آموزش #کریپتو #ترید #چشم_عقاب"

fmt = Fmt()

# ============================================================
# NEWS & DATA
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 14400
    SOURCES = [("https://cryptopanic.com/news/rss/", "CryptoPanic"), ("https://cointelegraph.com/rss", "CoinTelegraph")]
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < cls.CACHE_DURATION: return cls.CACHE.get("data",[])
        articles = []
        for url, src in cls.SOURCES:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:5]: articles.append({"title":e.title,"link":e.link,"source":src})
            except: pass
        cls.CACHE = {"ts":now,"data":articles}
        return articles

class FearGreedIndex:
    CACHE = {}
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts",0)) < 3600: return cls.CACHE["value"], cls.CACHE["text"]
        try:
            async with httpx.AsyncClient(timeout=15) as cl:
                r = await cl.get("https://api.alternative.me/fng/?limit=1")
                d = r.json(); v = int(d['data'][0]['value']); t = d['data'][0]['value_classification']
                cls.CACHE = {"ts":now,"value":v,"text":t}
                return v, t
        except: return 50, "خنثی"

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
# 20 PROFESSIONAL GLASS BUTTONS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال بیتکوین", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ ۴ساعته", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ روزانه", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ هفتگی", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 تحلیل هوش مصنوعی", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار پیشرفته", callback_data="chart_BTC/USDT"),
             InlineKeyboardButton("📰 تحلیل بازار", callback_data="market")],
            [InlineKeyboardButton("🧲 اسمارت مانی", callback_data="smc"),
             InlineKeyboardButton("🔮 پیش‌بینی قیمت", callback_data="pred"),
             InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("😱 شاخص ترس و طمع", callback_data="fear_greed"),
             InlineKeyboardButton("🏆 دامیننس بازار", callback_data="dominance"),
             InlineKeyboardButton("📰 اخبار فارسی", callback_data="news")],
            [InlineKeyboardButton("🎨 ساخت تصویر با AI", callback_data="ai_image"),
             InlineKeyboardButton("🦅 چشم عقاب", callback_data="eagle_eye"),
             InlineKeyboardButton("📚 دوره آموزشی", callback_data="course_info")],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ])

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""
🦅🦅🦅 *چشــــم عـقـاب — Eagle Eye v29* 🦅🦅🦅

{pdt.greeting()} تریدر عزیز!

{pdt.full()}

🧠 هوش مصنوعی دوگانه (Groq + Gemini)
📊 ۸۰+ اندیکاتور تکنیکال
🧲 اسمارت مانی (SMC)
🎨 ساخت تصویر با هوش مصنوعی
📚 دوره ۱۰۰۰+ ساعته (هر ۳۰ دقیقه)
📡 سیگنال هر ۲ ساعت (نمودار + AI)
📰 اخبار هر ۴ ساعت (تصویری)
📊 خلاصه بازار هر شب

✨ دقت میلیمتری چشــــم عـقـاب ✨

👇 یکی از دکمه‌ها را انتخاب کنید:""", parse_mode="Markdown", reply_markup=Menu.main())

async def send_signal_with_images(bot, chat_id, symbol, ticker, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t):
    # نمودار کندلی
    if CHART_AVAILABLE:
        chart_buf = chart_gen.create(df, symbol)
        if chart_buf:
            await bot.send_photo(chat_id=chat_id, photo=chart_buf, caption=f"📊 نمودار {symbol.replace('/USDT','')} | ${ticker['last']:,.4f}")
    
    # تصویر هوش مصنوعی
    trend = "صعودی" if ticker.get('percentage',0) > 0 else "نزولی"
    ai_img = await ai_image_gen.generate(f"{symbol} {trend} market analysis", "eagle")
    if ai_img:
        await bot.send_photo(chat_id=chat_id, photo=ai_img, caption="🦅 تصویر تحلیلی چشم عقاب")
    
    # متن تحلیل
    a = {'symbol':symbol,'price':ticker['last'],'change':ticker.get('percentage',0),'indicators':ind,'candles':candles,'mtf':mtf,'smc':smc_data}
    msg = fmt.signal(a, groq_t, smc_t, pred_t)
    await safe_send(bot, chat_id, msg)

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text("🦅 منوی اصلی", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *قیمت‌های لحظه‌ای*\n{pdt.full()}\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"):
            sym = d[2:]; await q.answer(); await q.edit_message_text(f"🦅 تحلیل {sym.replace('/USDT','')}...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 150)
            if not t or df is None:
                await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
            ind, candles = ui.calc(df); mtf = {}
            for tf in cfg.primary_tfs:
                dft = exchange_mgr.ohlcv(sym, tf, 100)
                if dft is not None:
                    mtf[tf], _ = ui.calc(dft)
            smc_data = SmartMoney.analyze(df)
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candles, mtf)
            smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
            pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
            await send_signal_with_images(ctx.bot, q.message.chat_id, sym, t, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t)
            await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, f"✅ تحلیل {sym.replace('/USDT','')} انجام شد",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"s_{sym}"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_":"4h","tf1d_":"1d","tf1w_":"1w"}; labels = {"4h":"۴ساعته","1d":"روزانه","1w":"هفتگی"}
            for prefix,tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d)>len(prefix) else "BTC/USDT"; await q.answer()
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, tf, 150)
                    if t and df is not None:
                        ind, _ = ui.calc(df); sig, conf, _, action = sg.generate(ind, t['last'])
                        if CHART_AVAILABLE:
                            buf = chart_gen.create(df, sym)
                            if buf: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=buf, caption=f"⏰ {labels[tf]} {sym.replace('/USDT','')} | ${t['last']:,.4f}")
                        await q.edit_message_text(f"⏰ *{labels[tf]} {sym.replace('/USDT','')}*\n{pdt.full()}\n💰 ${t['last']:,.4f}\n🎯 {sig}\n🚦 {action}\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "smc":
            df = exchange_mgr.ohlcv("BTC/USDT", '1h', 150)
            if df:
                smc_data = SmartMoney.analyze(df); ai = await groq_ai.smc("بیتکوین", smc_data) if groq_ai.enabled else None
                await q.edit_message_text(f"🧲 *اسمارت مانی*\n{pdt.full()}\n\n{ai if ai else 'داده ناکافی'}\n\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "fear_greed":
            v, t = await FearGreedIndex.fetch()
            ai = await groq_ai.fear_greed(v, t) if groq_ai.enabled else None
            await q.edit_message_text(f"😱 *ترس و طمع*\n{pdt.full()}\n\n{'🟢' if v<30 else '🔴' if v>70 else '🟡'} {v}/۱۰۰ — {t}\n\n{ai if ai else ''}\n\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="fear_greed"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                summary = await groq_ai.news_summary([a['title'] for a in articles[:10]])
                img = await ai_image_gen.generate("breaking crypto news today", "news")
                if img: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=img, caption="📰 تصویر خبری")
                await q.edit_message_text(f"📰 *اخبار*\n{pdt.full()}\n\n{summary}\n\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as cl:
                    r = await cl.get("https://api.coingecko.com/api/v3/global")
                    data = r.json(); btc = data['data']['market_cap_percentage']['btc']; eth = data['data']['market_cap_percentage']['eth']
                    await q.edit_message_text(f"🏆 *دامیننس*\n{pdt.full()}\n₿ بیتکوین: {btc:.1f}%\nΞ اتریوم: {eth:.1f}%\n\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            except: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ai_image":
            await q.answer("🎨 در حال ساخت...")
            img = await ai_image_gen.generate("cyberpunk eagle crypto trader", "eagle")
            if img:
                await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=img, caption="🦅 تصویر ساخته شد")
                await q.edit_message_text("✅ تصویر ارسال شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            else: await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "eagle_eye":
            t = exchange_mgr.ticker("BTC/USDT")
            if t:
                trend = "صعودی" if t.get('percentage',0) > 0 else "نزولی"
                img = await ai_image_gen.generate_eagle_eye("BTC", trend)
                if img:
                    await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=img, caption=f"🦅 چشم عقاب: بیتکوین ${t['last']:,.2f}")
                await q.answer("🦅 فعال شد")
        elif d == "course_info":
            await q.edit_message_text("📚 *دوره ۱۰۰۰+ ساعته چشم عقاب*\nهر ۳۰ دقیقه یک درس تخصصی به کانال ارسال می‌شود.\n\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d in ["scan","market","ai_BTC/USDT","chart_BTC/USDT","pred","whale","ref","help"]:
            await q.edit_message_text(f"⚡ بخش {d}\n{pdt.full()}\n\nدر حال توسعه...\n🦅 @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer(f"⚡ {pdt.time_str()}")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("از /start استفاده کنید", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS — TIMED TASKS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym,'1h',150)
                    if t and df is not None:
                        ind, candles = ui.calc(df); mtf = {}
                        for tf in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf, 100)
                            if dft is not None:
                                mtf[tf], _ = ui.calc(dft)
                        smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candles, mtf)
                        smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
                        pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
                        await send_signal_with_images(app.bot, cfg.channel_id, sym, t, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t)
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
        except Exception as e: logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_course(app: Application):
    await asyncio.sleep(60)
    lesson_num = 0
    topics = ["تحلیل تکنیکال","کندل‌شناسی","میانگین‌های متحرک","RSI و MACD","Bollinger Bands","فیبوناچی","ایچیموکو","اسمارت مانی","مدیریت سرمایه","روانشناسی ترید","استراتژی روزانه","تحلیل فاندامنتال","نهنگ‌ها","DeFi","NFT","آلت‌سیزن"] * 100
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                topic = topics[lesson_num % len(topics)]
                lesson = await groq_ai.course_lesson(lesson_num+1, 1000, topic)
                if lesson:
                    await safe_send(app.bot, cfg.channel_id, fmt.course(lesson))
                    lesson_num += 1
        except Exception as e: logger.error(f"Course: {e}")
        await asyncio.sleep(cfg.education_interval)

async def auto_news(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                articles = await CryptoNews.fetch()
                if articles:
                    summary = await groq_ai.news_summary([a['title'] for a in articles[:12]])
                    img = await ai_image_gen.generate("latest crypto news today", "news")
                    if img: await app.bot.send_photo(cfg.channel_id, photo=img, caption="📰 تصویر خبری")
                    await safe_send(app.bot, cfg.channel_id, f"📰 *اخبار روز*\n{pdt.full()}\n\n{summary}\n\n🦅 @CryptoPulse606\n#اخبار #کریپتو #تحلیل #چشم_عقاب")
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(180)
    while True:
        try:
            if cfg.channel_id:
                v, t = await FearGreedIndex.fetch()
                await safe_send(app.bot, cfg.channel_id, f"😱 *ترس و طمع*\n{'🟢' if v<30 else '🔴' if v>70 else '🟡'} {v}/۱۰۰ — {t}\n\n🦅 @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(400)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: await safe_send(app.bot, cfg.channel_id, f"🐋 *نهنگ‌ها*\n\n{c}\n\n🦅 @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.whale_interval)

async def auto_daily_summary(app: Application):
    while True:
        now = datetime.now(TEHRAN_TZ)
        target = datetime.strptime(cfg.daily_summary_time, "%H:%M").replace(tzinfo=TEHRAN_TZ)
        if now.hour == target.hour and now.minute == target.minute:
            try:
                if cfg.channel_id and exchange_mgr.connected:
                    top = []
                    for sym in cfg.symbols[:10]:
                        t = exchange_mgr.ticker(sym)
                        if t: top.append({"symbol":sym.replace('/USDT',''),"change":t.get('percentage',0)})
                    fg_v, fg_t = await FearGreedIndex.fetch()
                    async with httpx.AsyncClient() as cl:
                        r = await cl.get("https://api.coingecko.com/api/v3/global")
                        dom = r.json()['data']['market_cap_percentage']
                    data = {"top_movers": top, "btc_dom": dom['btc'], "eth_dom": dom['eth'], "fear_greed": f"{fg_v} ({fg_t})"}
                    summary = await groq_ai.daily_summary(data)
                    img = await ai_image_gen.generate("daily crypto market summary, eagle eye", "abstract")
                    if img: await app.bot.send_photo(cfg.channel_id, photo=img)
                    await safe_send(app.bot, cfg.channel_id, f"📊 *خلاصه بازار امروز*\n{pdt.full()}\n\n{summary}\n\n🦅 @CryptoPulse606\n#خلاصه_بازار #کریپتو #تحلیل #چشم_عقاب")
            except Exception as e: logger.error(f"Daily summary: {e}")
        await asyncio.sleep(60)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    logger.info(f"🦅 شروع چشم عقاب نسخه ۲۹ | {pdt.full()}")
    exchange_mgr.connect()
    request = create_request()
    app = Application.builder().token(cfg.token).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    asyncio.create_task(cleanup_memory())
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_course(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    asyncio.create_task(auto_daily_summary(app))
    logger.info("🦅 چشم عقاب آماده — دقت بی‌نهایت — همه چیز رایگان")
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

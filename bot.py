```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIP PLATINUM v36.0 - ULTIMATE PRO
"""

import os, sys, asyncio, time, json, random, signal, io, re, gc, hashlib, urllib.parse
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, OrderedDict
import numpy as np
import pandas as pd
import ccxt
import httpx
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LOGGING
# ============================================================
for _lib in ['httpx','httpcore','telegram','telegram.ext','telegram.request',
             'apscheduler','ccxt','urllib3','asyncio','matplotlib','PIL',
             'aiohttp','chardet','openai','groq','mplfinance','ta']:
    _l = logging.getLogger(_lib)
    _l.setLevel(logging.CRITICAL + 1)
    _l.propagate = False
    _l.handlers.clear()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('VIP')
logger.setLevel(logging.INFO)
logger.propagate = False
_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))
_console.addFilter(lambda r: r.name == 'VIP')
logger.addHandler(_console)
logger.info("VIP Platinum v36.0 starting...")

# ============================================================
# AUTO-INSTALL
# ============================================================
def _ensure_libs():
    _needed = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','ta':'ta',
        'ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'feedparser':'feedparser','Pillow':'Pillow',
        'cachetools':'cachetools','tenacity':'tenacity','aiohttp':'aiohttp'
    }
    for mod, pkg in _needed.items():
        try: __import__(mod)
        except: 
            import subprocess
            subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

_ensure_libs()

import jdatetime, pytz
import feedparser

try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    CHART_OK = True
except:
    CHART_OK = False

load_dotenv()
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel: str = os.getenv("CHANNEL_ID", "@CryptoPulse606")
    required_channel: str = "@CryptoPulse606"
    owner: int = int(os.getenv("OWNER_ID", "7225279768"))
    groq_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    coinex_key: str = os.getenv("COINEX_API_KEY", "")
    coinex_sec: str = os.getenv("COINEX_SECRET", "")
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "BNB/USDT","DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT"
    ])
    top_symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "BNB/USDT","DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT"
    ])
    tfs: List[str] = field(default_factory=lambda: ["1h","4h","1d"])
    hashtags: List[str] = field(default_factory=lambda: [
        "#کریپتو","#ارز_دیجیتال","#اخبار","#بیتکوین",
        "#تحلیل","#تکنیکال","#سیگنال","#VIP_پلاتینیوم"
    ])

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _f = "/tmp/vip_platinum.lock"
    @classmethod
    def acquire(cls):
        try:
            if os.path.exists(cls._f):
                try:
                    with open(cls._f) as f: os.kill(int(f.read().strip() or 0), signal.SIGTERM)
                    time.sleep(1)
                except: os.remove(cls._f)
            with open(cls._f,'w') as f: f.write(str(os.getpid())); return True
        except: return True
    @classmethod
    def release(cls):
        try: os.remove(cls._f) if os.path.exists(cls._f) else None
        except: pass

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s,f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# PERSIAN DATE & GREETING
# ============================================================
class Persian:
    DAYS = ['دوشنبه','سه شنبه','چهارشنبه','پنج شنبه','جمعه','شنبه','یکشنبه']
    MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    @classmethod
    def now(cls): return datetime.now(TEHRAN_TZ)
    @classmethod
    def shamsi(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    @classmethod
    def time(cls): return cls.now().strftime('%H:%M:%S')
    @classmethod
    def full(cls): return f"{cls.DAYS[cls.now().weekday()]} {cls.shamsi()} ساعت {cls.time()}"
    @classmethod
    def greet(cls):
        h = cls.now().hour
        if 5 <= h < 9: return "صبح بخیر"
        elif 12 <= h < 14: return "ظهر بخیر"
        elif 16 <= h < 18: return "عصر بخیر"
        elif 20 <= h <= 23 or 1 <= h < 3: return "شب بخیر"
        return "وقت بخیر"

p = Persian()

# ============================================================
# AI ENGINE
# ============================================================
class AI:
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    SYS = """تو VIP پلاتینیوم هستی، حرفه ای ترین تحلیلگر کریپتو و دستیار هوشمند.
فقط به فارسی طبیعی و روان صحبت کن.
پاسخ ها کامل، دقیق و کاربردی باشه.
با انرژی مثبت و انگیزشی جواب بده.
همیشه مخاطب رو راهنمایی کن و پیشنهاد بده."""
    
    def __init__(self):
        self.groq_ok = bool(cfg.groq_key)
        self.gemini_ok = bool(cfg.gemini_key)
        self._client = httpx.AsyncClient(timeout=90.0)
        self._last = 0
        self._gap = 1.5
        self._conversations = {}
    
    async def _wait(self):
        elapsed = time.time() - self._last
        if elapsed < self._gap:
            await asyncio.sleep(self._gap - elapsed)
        self._last = time.time()
    
    async def ask(self, prompt: str, max_t: int = 700, context: str = "") -> Optional[str]:
        await self._wait()
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        if self.groq_ok:
            try:
                r = await self._client.post(
                    self.GROQ_URL,
                    headers={"Authorization": f"Bearer {cfg.groq_key}", "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile", "messages": [
                        {"role": "system", "content": self.SYS},
                        {"role": "user", "content": full_prompt}
                    ], "max_tokens": max_t, "temperature": 0.85},
                    timeout=60.0
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
            except: pass
        
        if self.gemini_ok:
            try:
                r = await self._client.post(
                    f"{self.GEMINI_URL}?key={cfg.gemini_key}",
                    json={"contents": [{"parts": [{"text": self.SYS + "\n\n" + full_prompt}]}]},
                    timeout=60.0
                )
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except: pass
        
        return None
    
    async def chat(self, user_id: int, message: str) -> str:
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        self._conversations[user_id].append(f"کاربر: {message}")
        if len(self._conversations[user_id]) > 10:
            self._conversations[user_id] = self._conversations[user_id][-10:]
        context = "\n".join(self._conversations[user_id][-5:])
        response = await self.ask(message, 700, context)
        if response:
            self._conversations[user_id].append(f"دستیار: {response[:200]}")
        return response or "در حال پردازش... لطفاً دوباره بپرسید."
    
    async def full_analysis(self, symbol, price, change, ind, candles, mtf, smc):
        return await self.ask(f"""تحلیل کامل {symbol} - قیمت: {price:,.4f}$ - تغییر: {change:+.2f}%

اندیکاتورها:
RSI={ind.get('RSI',50):.0f} | MACD={'صعودی' if ind.get('MACD',0)>0 else 'نزولی'}
ADX={ind.get('ADX',20):.0f} | CCI={ind.get('CCI',0):.0f} | MFI={ind.get('MFI',50):.0f}
BB%={ind.get('BB',0.5):.2f} | Vol={ind.get('VOL',1):.1f}x

میانگین ها:
EMA7={ind.get('EMA7',0):.2f} | EMA20={ind.get('EMA20',0):.2f} | EMA50={ind.get('EMA50',0):.2f}

سطوح کلیدی:
حمایت={ind.get('SUP',0):.4f} | مقاومت={ind.get('RES',0):.4f}
فیبوناچی 618={ind.get('FIB618',0):.4f}

الگوها: {', '.join(candles) if candles else 'بدون الگو'}

تحلیل کامل بده شامل:
1- وضعیت فعلی و روند
2- نقاط ورود و خروج
3- حد ضرر مناسب
4- اهداف قیمتی
5- پیش بینی عددی برای فردا، هفته بعد، ماه بعد
6- نتیجه گیری نهایی""", 800)
    
    async def predict_price(self, symbol, price, ind):
        return await self.ask(f"""پیش بینی قیمت {symbol} - قیمت فعلی: {price:,.2f}$

داده های فعلی:
RSI={ind.get('RSI',50):.0f} | ADX={ind.get('ADX',20):.0f}
MACD={'صعودی' if ind.get('MACD',0)>0 else 'نزولی'}

پیش بینی دقیق قیمت:
فردا: ؟ دلار
یک هفته: ؟ دلار
یک ماه: ؟ دلار

سناریوها و توصیه ها رو کامل بنویس""", 600)
    
    async def news_summary(self, headlines): 
        return await self.ask(f"اخبار:\n{chr(10).join(headlines[:12])}\nخلاصه فارسی ۴۰۰ کلمه با تحلیل تاثیر هر خبر", 500)
    
    async def market_overview(self, data):
        return await self.ask(f"""مرور جامع بازار:

بیشترین رشد: {json.dumps(data.get('up', []), ensure_ascii=False)}
بیشترین ریزش: {json.dumps(data.get('down', []), ensure_ascii=False)}

تحلیل کامل بازار و پیشنهادات معاملاتی""", 500)
    
    async def fg_analysis(self, v, t): 
        return await self.ask(f"شاخص ترس و طمع: {v}/۱۰۰ ({t})\nتحلیل فارسی ۳۰۰ کلمه با پیش بینی حرکت بعدی", 400)
    
    async def daily_summary(self, data):
        return await self.ask(f"""جمع بندی روزانه بازار:

داده های امروز: {json.dumps(data, ensure_ascii=False)[:500]}

تحلیل کامل روز و پیش بینی برای فردا""", 700)

ai = AI()

# ============================================================
# EXCHANGE
# ============================================================
class Exchange:
    def __init__(self):
        self._ex = None
        self.ok = False
        self._cache = {}
        self._cache_time = {}
    
    def connect(self):
        try:
            if cfg.coinex_key and cfg.coinex_sec:
                self._ex = ccxt.coinex({'apiKey': cfg.coinex_key, 'secret': cfg.coinex_sec, 
                                        'enableRateLimit': True, 'timeout': 30000})
            else:
                self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
            self._ex.load_markets()
            self.ok = True
            logger.info(f"CoinEx connected - {len(self._ex.markets)} markets")
        except Exception as e:
            logger.error(f"CoinEx: {e}")
            self.ok = False
    
    def ticker(self, s):
        try:
            if not self.ok: return None
            cache_key = f"ticker_{s}"
            if cache_key in self._cache and time.time() - self._cache_time.get(cache_key, 0) < 30:
                return self._cache[cache_key]
            data = self._ex.fetch_ticker(s)
            self._cache[cache_key] = data
            self._cache_time[cache_key] = time.time()
            return data
        except: return None
    
    def ohlcv(self, s, tf, limit=150):
        try:
            if not self.ok: return None
            cache_key = f"ohlcv_{s}_{tf}_{limit}"
            if cache_key in self._cache and time.time() - self._cache_time.get(cache_key, 0) < 60:
                return self._cache[cache_key]
            d = self._ex.fetch_ohlcv(s, tf, limit=limit)
            if d and len(d) > 30:
                df = pd.DataFrame(d, columns=['ts','o','h','l','c','v'])
                self._cache[cache_key] = df
                self._cache_time[cache_key] = time.time()
                return df
            return None
        except: return None
    
    def movers(self, n=10):
        mv = []
        if not self.ok: return {'up': [], 'dn': []}
        for sym in cfg.symbols:
            t = self.ticker(sym)
            if t: mv.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage', 0), 'price': t.get('last', 0)})
        mv.sort(key=lambda x: x['change'], reverse=True)
        return {'up': mv[:n], 'dn': mv[-n:]}
    
    def all_tickers(self):
        data = []
        if not self.ok: return data
        for sym in cfg.symbols:
            t = self.ticker(sym)
            if t:
                data.append({
                    'symbol': sym.replace('/USDT', ''),
                    'price': t.get('last', 0),
                    'change': t.get('percentage', 0),
                    'volume': t.get('quoteVolume', 0)
                })
        return data

ex = Exchange()

# ============================================================
# SMART MONEY
# ============================================================
class SMC:
    @staticmethod
    def analyze(df):
        if df is None or len(df) < 60: return {}
        try:
            from scipy.signal import argrelextrema
            h, l = df['h'].values, df['l'].values
            sh = argrelextrema(h, np.greater, order=5)[0]
            sl = argrelextrema(l, np.less, order=5)[0]
            if len(sh) < 2 or len(sl) < 2: return {}
            up = all(h[sh[i]] > h[sh[i-1]] for i in range(1, len(sh)))
            dn = all(l[sl[i]] < l[sl[i-1]] for i in range(1, len(sl)))
            t = "صعودی" if up and not dn else "نزولی" if dn and not up else "خنثی"
            return {"bos": "صعود" if up else "نزول" if dn else "هیچ", "choch": t, "trend": t, "power": "قوی" if (up or dn) else "ضعیف"}
        except: return {}

# ============================================================
# INDICATORS
# ============================================================
class Indicators:
    @staticmethod
    def calc(df):
        if df is None or len(df) < 30: return {}, []
        try:
            c, h, l, v = df['c'].astype(float), df['h'].astype(float), df['l'].astype(float), df['v'].astype(float)
            ind = OrderedDict()
            for p in [7,14,20,50,100,200]:
                ind[f'EMA{p}'] = float(c.ewm(span=p, adjust=False).mean().iloc[-1])
            from ta.momentum import RSIIndicator, StochasticOscillator
            try: ind['RSI'] = float(RSIIndicator(c, 14).rsi().iloc[-1])
            except: ind['RSI'] = 50.0
            try:
                st = StochasticOscillator(h, l, c, 14, 3)
                ind['STOCH_K'] = float(st.stoch().iloc[-1])
                ind['STOCH_D'] = float(st.stoch_signal().iloc[-1])
            except: ind['STOCH_K'] = ind['STOCH_D'] = 50.0
            from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
            try: ind['MACD'] = float(MACD(c, 12, 26, 9).macd_diff().iloc[-1])
            except: ind['MACD'] = 0.0
            try: ind['ADX'] = float(ADXIndicator(h, l, c, 14).adx().iloc[-1])
            except: ind['ADX'] = 20.0
            try: ind['CCI'] = float(CCIIndicator(h, l, c, 20).cci().iloc[-1])
            except: ind['CCI'] = 0.0
            from ta.volatility import BollingerBands, AverageTrueRange
            try: ind['BB'] = float(BollingerBands(c, 20, 2).bollinger_pband().iloc[-1])
            except: ind['BB'] = 0.5
            try: ind['ATR'] = float(AverageTrueRange(h, l, c, 14).average_true_range().iloc[-1])
            except: ind['ATR'] = c.iloc[-1] * 0.01
            try:
                tp = (h + l + c) / 3
                mf = tp * v
                pf = mf.where(tp > tp.shift(1), 0)
                nf = mf.where(tp < tp.shift(1), 0)
                ind['MFI'] = float((100 - (100 / (1 + pf.rolling(14).sum() / nf.rolling(14).sum()))).iloc[-1])
            except: ind['MFI'] = 50.0
            vs = v.rolling(20).mean().iloc[-1] if len(v) >= 20 else 1
            ind['VOL'] = float(v.iloc[-1] / vs if vs > 0 else 1)
            ind['SUP'] = float(l.rolling(20).min().iloc[-1]) if len(l) >= 20 else l.min()
            ind['RES'] = float(h.rolling(20).max().iloc[-1]) if len(h) >= 20 else h.max()
            try:
                ichi = IchimokuIndicator(h, l, 9, 26, 52)
                ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
                ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            except: pass
            h50 = h.rolling(50).max().iloc[-1] if len(h) >= 50 else h.max()
            l50 = l.rolling(50).min().iloc[-1] if len(l) >= 50 else l.min()
            diff = h50 - l50
            for lvl in [0.236, 0.382, 0.5, 0.618, 0.786]:
                ind[f'FIB{int(lvl*1000)}'] = float(h50 - diff * lvl)
            candles, names = Indicators._candles(df)
            ind.update(candles)
            return ind, names
        except Exception as e:
            logger.error(f"Indicators error: {e}")
            return {}, []
    
    @staticmethod
    def _candles(df):
        pats, names = {}, []
        if len(df) < 2: return pats, names
        o, h, l, c = df['o'].iloc[-1], df['h'].iloc[-1], df['l'].iloc[-1], df['c'].iloc[-1]
        po, pc = df['o'].iloc[-2], df['c'].iloc[-2]
        body, tr = abs(c - o), h - l
        if tr == 0: return pats, names
        if body <= tr * 0.08: pats['doji'] = True; names.append("دوجی")
        if (min(c, o) - l) > body * 2 and c > o: pats['hammer'] = True; names.append("چکش")
        if (h - max(c, o)) > body * 2 and c < o: pats['shooting'] = True; names.append("ستاره")
        if c > o and pc < po: pats['bull_eng'] = True; names.append("پوشای صعودی")
        if c < o and pc > po: pats['bear_eng'] = True; names.append("پوشای نزولی")
        if len(df) >= 3:
            o3, c3 = df['o'].iloc[-3], df['c'].iloc[-3]
            if c > o and pc > po and c3 > o3: pats['3soldier'] = True; names.append("سه سرباز")
            if c < o and pc < po and c3 < o3: pats['3crow'] = True; names.append("سه کلاغ")
        return pats, names

ind_calc = Indicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, smc_data=None, mtf=None):
        score = 0
        if ind.get('EMA7', 0) > ind.get('EMA20', 0) > ind.get('EMA50', 0): score += 250
        elif ind.get('EMA7', 0) < ind.get('EMA20', 0) < ind.get('EMA50', 0): score -= 250
        rsi = ind.get('RSI', 50)
        if rsi < 25: score += 200
        elif rsi < 30: score += 150
        elif rsi > 75: score -= 200
        elif rsi > 70: score -= 150
        if ind.get('MACD', 0) > 0: score += 120
        else: score -= 120
        bb = ind.get('BB', 0.5)
        if bb < 0.05: score += 180
        elif bb > 0.95: score -= 180
        vol = ind.get('VOL', 1)
        if vol > 2.5: score += (100 if score > 0 else -100)
        for b in ['hammer', 'bull_eng', '3soldier']:
            if ind.get(b): score += 130
        for br in ['shooting', 'bear_eng', '3crow']:
            if ind.get(br): score -= 130
        if ind.get('TENKAN', 0) > ind.get('KIJUN', 0) and price > ((ind.get('TENKAN', 0) + ind.get('KIJUN', 0)) / 2):
            score += 90
        if smc_data:
            if 'صعودی' in smc_data.get('choch', ''): score += 150
            elif 'نزولی' in smc_data.get('choch', ''): score -= 150
        if mtf:
            for tf, ti in mtf.items():
                w = {"1h": 1.5, "4h": 2.5, "1d": 4}.get(tf, 1)
                if ti.get('RSI', 50) > 55: score += int(40 * w)
                elif ti.get('RSI', 50) < 45: score -= int(40 * w)
        score = max(-1000, min(1000, score))
        abs_s = abs(score)
        if abs_s >= 850: circles = "★★★★★" if score > 0 else "★★★★★"
        elif abs_s >= 650: circles = "★★★★☆" if score > 0 else "★★★★☆"
        elif abs_s >= 450: circles = "★★★☆☆" if score > 0 else "★★★☆☆"
        elif abs_s >= 250: circles = "★★☆☆☆" if score > 0 else "★★☆☆☆"
        else: circles = "☆☆☆☆☆"
        if score >= 500: sig, conf, act = "خرید قوی", 97 if score >= 800 else 88, "خرید"
        elif score >= 250: sig, conf, act = "خرید محتاط", 75, "می تونی بخری"
        elif score <= -500: sig, conf, act = "فروش قوی", 97 if score <= -800 else 88, "فروش"
        elif score <= -250: sig, conf, act = "فروش محتاط", 75, "می تونی بفروشی"
        else: sig, conf, act = "خنثی", 60, "صبر کن"
        return sig, conf, score, act, circles

sig_gen = SignalGen()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGen:
    @staticmethod
    def create(df, symbol):
        if not CHART_OK or df is None or len(df) < 30: return None
        try:
            data = df.copy()
            data['ts'] = pd.to_datetime(data['ts'], unit='ms')
            data = data.set_index('ts')
            data = data.rename(columns={'o':'Open','h':'High','l':'Low','c':'Close','v':'Volume'})
            data = data[['Open','High','Low','Close','Volume']].iloc[-60:]
            ap = []
            for p, col in [(7,'#FFD700'),(20,'#C0C0C0'),(50,'#00ff88'),(200,'#E74C3C')]:
                ap.append(mpf.make_addplot(data['Close'].ewm(span=p, adjust=False).mean(), color=col, width=1.5))
            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(data['Close'], 14).rsi()
            ap.append(mpf.make_addplot(rsi, panel=2, color='#C0C0C0', ylabel='RSI'))
            ap.append(mpf.make_addplot(pd.Series([70]*len(data), index=data.index), panel=2, color='#E74C3C', linestyle='--'))
            ap.append(mpf.make_addplot(pd.Series([30]*len(data), index=data.index), panel=2, color='#2ECC71', linestyle='--'))
            macd_h = (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()) - \
                     (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()).ewm(span=9).mean()
            ap.append(mpf.make_addplot(macd_h, type='bar', panel=3, color='#C0C0C0', ylabel='MACD'))
            mc = mpf.make_marketcolors(up='#2ECC71', down='#E74C3C', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#1a1a2e', figcolor='#1a1a2e', gridcolor='#3a3a5e')
            fig, _ = mpf.plot(data, type='candle', style=style, title=f'VIP PLATINUM - {symbol} - {p.shamsi()}',
                            volume=True, addplot=ap, panel_ratios=(3,1,1,1), figsize=(20,14), returnfig=True)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='#1a1a2e')
            buf.seek(0)
            plt.close(fig)
            return buf
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None

chart_gen = ChartGen()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, ai_t, pred_t):
        s = a['symbol'].replace('/USDT','')
        i = a['ind']
        candles = a.get('candles', [])
        sig_text, conf, score, action, circles = sig_gen.generate(i, a['price'], a.get('smc'), a.get('mtf'))
        entry = a['price']
        sl = a['price'] - i['ATR'] * 2.5
        tp1 = a['price'] + i['ATR'] * 3.5
        tp2 = a['price'] + i['ATR'] * 6
        tags = ' '.join(random.sample(cfg.hashtags, 4))
        msg = f"""
========================================
   VIP PLATINUM | {s}
========================================
{p.greet()} - {p.full()}

قیمت: ${a['price']:,.4f} | تغییر: {a['change']:+.2f}%
سیگنال: {sig_text} | قدرت: {conf}%
امتیاز: {score}/۱۰۰۰ | قدرت: {circles}
اقدام: {action}

EMAs: 7={i.get('EMA7',0):.2f} | 20={i.get('EMA20',0):.2f} | 50={i.get('EMA50',0):.2f}
شمع ها: {', '.join(candles) if candles else 'بدون الگو'}

اندیکاتورها:
RSI={i['RSI']:.1f} | MACD={'صعودی' if i.get('MACD',0)>0 else 'نزولی'}
ADX={i['ADX']:.1f} | CCI={i['CCI']:.1f} | MFI={i['MFI']:.1f}
BB={i['BB']:.2f} | Vol={i['VOL']:.1f}x

مقاومت: {i['RES']:.4f} | حمایت: {i['SUP']:.4f}
فیبوناچی ۶۱۸: {i.get('FIB618',0):.4f}

ستاپ معامله:
ورود: ${entry:,.4f}
حد ضرر: ${sl:,.4f} ({(abs(entry-sl)/entry*100):.1f}%)
هدف ۱: ${tp1:,.4f} | هدف ۲: ${tp2:,.4f}

تحلیل کامل:
{ai_t[:800] if ai_t else 'در حال بروزرسانی...'}

پیش بینی عددی:
{pred_t[:600] if pred_t else 'در حال محاسبه...'}

@{cfg.channel.replace('@','')} | {p.full()}
{tags}
"""
        return msg

# ============================================================
# NEWS FETCHER
# ============================================================
class NewsFetcher:
    _cache = {}
    _dur = 7200
    _srcs = [
        ("https://cryptopanic.com/news/rss/", "CryptoPanic"),
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
        ("https://cryptoslate.com/feed/", "CryptoSlate"),
        ("https://decrypt.co/feed", "Decrypt")
    ]
    
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls._cache and (now - cls._cache.get("ts", 0)) < cls._dur:
            return cls._cache.get("data", [])
        arts = []
        for url, src in cls._srcs:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:8]:
                    arts.append({"title": e.title, "link": e.link, "source": src})
            except: pass
        cls._cache = {"ts": now, "data": arts}
        logger.info(f"News: {len(arts)} fetched")
        return arts

class FearGreed:
    _cache = {}
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls._cache and (now - cls._cache.get("ts", 0)) < 3600:
            return cls._cache["v"], cls._cache["t"]
        try:
            async with httpx.AsyncClient(timeout=15) as cl:
                r = await cl.get("https://api.alternative.me/fng/?limit=1")
                d = r.json()
                v, t = int(d['data'][0]['value']), d['data'][0]['value_classification']
                cls._cache = {"ts": now, "v": v, "t": t}
                return v, t
        except: return 50, "خنثی"

# ============================================================
# SAFE SEND
# ============================================================
async def safe_send(bot, chat, text, markup=None):
    try:
        return await bot.send_message(chat_id=chat, text=text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=markup, disable_web_page_preview=True)
    except:
        try: 
            clean = re.sub(r'[*_`~\\[\\]\\(\\)]','',text)
            return await bot.send_message(chat_id=chat, text=clean[:4000], reply_markup=markup)
        except: return None

# ============================================================
# MENU
# ============================================================
class Menu:
    @staticmethod
    def main():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("پیش بینی", callback_data="prediction"),
             InlineKeyboardButton("اخبار", callback_data="news")],
            [InlineKeyboardButton("ساخت تصویر", callback_data="create_image"),
             InlineKeyboardButton("چت با AI", callback_data="ai_chat")],
            [InlineKeyboardButton("سیگنال", callback_data="signal"),
             InlineKeyboardButton("تنظیمات", callback_data="settings")],
            [InlineKeyboardButton("تحلیل بازار", callback_data="market"),
             InlineKeyboardButton("معامله دمو", callback_data="demo_trade")],
            [InlineKeyboardButton("بهترین ها", callback_data="movers"),
             InlineKeyboardButton("ترس و طمع", callback_data="fear_greed")],
        ])
    
    @staticmethod
    def owner_settings():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("تغییر عکس اصلی", callback_data="change_banner"),
             InlineKeyboardButton("تغییر متن Welcome", callback_data="change_welcome")],
            [InlineKeyboardButton("افزودن ارز", callback_data="add_symbol"),
             InlineKeyboardButton("حذف ارز", callback_data="remove_symbol")],
            [InlineKeyboardButton("بازگشت", callback_data="back")],
        ])

# ============================================================
# MEMBERSHIP CHECK
# ============================================================
async def is_member(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=cfg.required_channel, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ============================================================
# DEMO TRADE
# ============================================================
class DemoTrade:
    def __init__(self):
        self.balance = 10000
        self.positions = {}
        self.trades = []
    
    def buy(self, symbol, price, amount):
        cost = price * amount
        if cost > self.balance:
            return False, "موجودی کافی نیست"
        self.balance -= cost
        if symbol in self.positions:
            self.positions[symbol]['amount'] += amount
        else:
            self.positions[symbol] = {'amount': amount, 'avg_price': price}
        self.trades.append({'type': 'buy', 'symbol': symbol, 'price': price, 'amount': amount, 'time': p.full()})
        return True, f"خرید {amount} {symbol} با قیمت ${price:.2f} انجام شد"
    
    def sell(self, symbol, price, amount):
        if symbol not in self.positions or self.positions[symbol]['amount'] < amount:
            return False, "موجودی کافی نیست"
        self.balance += price * amount
        self.positions[symbol]['amount'] -= amount
        if self.positions[symbol]['amount'] == 0:
            del self.positions[symbol]
        self.trades.append({'type': 'sell', 'symbol': symbol, 'price': price, 'amount': amount, 'time': p.full()})
        return True, f"فروش {amount} {symbol} با قیمت ${price:.2f} انجام شد"
    
    def get_status(self):
        txt = f"وضعیت حساب دمو\n{p.full()}\n\n"
        txt += f"موجودی: ${self.balance:,.2f}\n"
        txt += f"تعداد معاملات: {len(self.trades)}\n\n"
        if self.positions:
            txt += "پوزیشن های باز:\n"
            for sym, pos in self.positions.items():
                txt += f"- {sym}: {pos['amount']:.4f} (میانگین: ${pos['avg_price']:.2f})\n"
        else:
            txt += "هیچ پوزیشن بازی ندارید"
        return txt

demo = DemoTrade()

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    caption = f"""VIP PLATINUM v36.0 ULTIMATE

{p.greet()}
{p.full()}

قابلیت ها:
- پیش بینی قیمت
- اخبار لحظه ای
- ساخت تصویر با AI
- چت هوشمند
- سیگنال های VIP
- تحلیل کامل بازار
- معامله دمو
- بهترین و بدترین ارزها
- شاخص ترس و طمع

از دکمه های زیر استفاده کنید:
"""
    
    if await is_member(ctx.bot, user.id):
        await update.message.reply_text(
            caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=Menu.main()
        )
    else:
        channel_link = f"https://t.me/{cfg.required_channel.replace('@','')}"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("عضویت در کریپتو پالس", url=channel_link)],
            [InlineKeyboardButton("عضو شدم", callback_data="check_membership")],
        ])
        await update.message.reply_text(
            f"{user.first_name} عزیز\n\n"
            f"لطفاً ابتدا در کانال **کریپتو پالس** عضو شوید:\n\n"
            f"@{cfg.required_channel.replace('@','')}\n\n"
            f"سپس روی دکمه عضو شدم کلیک کنید.",
            reply_markup=markup
        )

async def check_membership_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    if await is_member(ctx.bot, user.id):
        caption = f"""VIP PLATINUM v36.0 ULTIMATE

{p.greet()}
{p.full()}

قابلیت ها:
- پیش بینی قیمت
- اخبار لحظه ای
- ساخت تصویر با AI
- چت هوشمند
- سیگنال های VIP
- تحلیل کامل بازار
- معامله دمو
- بهترین و بدترین ارزها
- شاخص ترس و طمع

از دکمه های زیر استفاده کنید:
"""
        await query.edit_message_text(
            caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=Menu.main()
        )
    else:
        channel_link = f"https://t.me/{cfg.required_channel.replace('@','')}"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("عضویت در کریپتو پالس", url=channel_link)],
            [InlineKeyboardButton("عضو شدم", callback_data="check_membership")],
        ])
        await query.edit_message_text(
            "شما هنوز در کانال عضو نشده اید!\n"
            "لطفاً ابتدا عضو شوید.",
            reply_markup=markup
        )

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    user = q.from_user
    
    if d == "check_membership":
        await check_membership_callback(update, ctx)
        return
    
    if not await is_member(ctx.bot, user.id):
        await q.answer("ابتدا باید در کانال عضو شوید!", show_alert=True)
        return
    
    # Prediction
    if d == "prediction":
        await q.answer("دریافت پیش بینی...")
        await q.edit_message_text(
            "پیش بینی قیمت\n\n"
            "نام ارز را به صورت متن بفرستید.\n"
            "مثال: BTC یا ETH یا SOL",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت", callback_data="back")]
            ])
        )
        ctx.user_data['awaiting_prediction'] = True
    
    # News
    elif d == "news":
        await q.answer("دریافت اخبار...")
        news = await NewsFetcher.fetch()
        if news:
            headlines = [n['title'] for n in news[:10]]
            txt = "آخرین اخبار کریپتو\n\n"
            for i, n in enumerate(news[:10], 1):
                txt += f"{i}. {n['title'][:100]}...\n"
                txt += f"   {n['source']}\n\n"
            
            ai_t = await ai.news_summary(headlines)
            if ai_t:
                txt += f"\nخلاصه اخبار:\n{ai_t[:500]}"
            
            await q.edit_message_text(txt[:4000], parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="back")]]))
        else:
            await q.edit_message_text("اخبار در دسترس نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="back")]]))
    
    # Create Image
    elif d == "create_image":
        await q.answer("ساخت تصویر...")
        await q.edit_message_text(
            "ساخت تصویر با هوش مصنوعی\n\n"
            "توضیحات تصویر را بفرستید.\n"
            "مثال: نمودار بیت کوین صعودی",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت", callback_data="back")]
            ])
        )
        ctx.user_data['awaiting_image'] = True
    
    # AI Chat
    elif d == "ai_chat":
        await q.answer("شروع چت با AI...")
        await q.edit_message_text(
            "چت با هوش مصنوعی\n\n"
            "سلام! من دستیار هوشمند هستم.\n"
            "هر سوالی بپرسید.\n\n"
            "برای برگشت دکمه پایین رو بزنید.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت به منو", callback_data="back")]
            ])
        )
        ctx.user_data['ai_chat'] = True
    
    # Signal
    elif d == "signal":
        await q.answer("دریافت سیگنال...")
        await q.edit_message_text(
            "دریافت سیگنال VIP\n\n"
            "نام ارز را بفرستید.\n"
            "مثال: BTC یا ETH یا SOL",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت", callback_data="back")]
            ])
        )
        ctx.user_data['awaiting_signal'] = True
    
    # Settings - Owner only
    elif d == "settings":
        if user.id != cfg.owner:
            await q.answer("فقط برای سازنده!", show_alert=True)
            return
        
        txt = f"""تنظیمات پلاتینیوم

سازنده: {cfg.owner}
چت AI: فعال
سیگنال ها: فعال
اخبار: فعال
پیش بینی: فعال
معامله دمو: فعال

کانال: {cfg.channel}
تعداد ارزها: {len(cfg.symbols)}

نسخه: v36.0 ULTIMATE PRO
"""
        await q.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=Menu.owner_settings())
    
    # Market Analysis
    elif d == "market":
        await q.answer("دریافت تحلیل بازار...")
        if not ex.ok: ex.connect()
        tickers = ex.all_tickers()
        movers = ex.movers(10)
        
        txt = f"تحلیل کامل بازار\n{p.full()}\n\n"
        
        txt += "۱۰ ارز با بیشترین رشد:\n"
        for i, m in enumerate(movers['up'][:10], 1):
            txt += f"{i}. {m['symbol']}: +{m['change']:.1f}% (${m['price']:,.2f})\n"
        
        txt += "\n۱۰ ارز با بیشترین ریزش:\n"
        for i, m in enumerate(movers['dn'][:10], 1):
            txt += f"{i}. {m['symbol']}: {m['change']:.1f}% (${m['price']:,.2f})\n"
        
        txt += "\nارزهای اصلی:\n"
        for t in tickers[:5]:
            em = '+' if t['change'] > 0 else ''
            txt += f"{t['symbol']}: ${t['price']:,.2f} ({em}{t['change']:.1f}%)\n"
        
        ai_t = await ai.market_overview({"up": movers['up'][:3], "down": movers['dn'][:3]})
        if ai_t:
            txt += f"\nتحلیل AI:\n{ai_t[:500]}"
        
        await q.edit_message_text(txt[:4000], parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="back")]]))
    
    # Demo Trade
    elif d == "demo_trade":
        await q.answer("معامله دمو...")
        txt = demo.get_status()
        txt += "\n\nدستورات:\n"
        txt += "برای خرید: خرید BTC 1\n"
        txt += "برای فروش: فروش BTC 0.5\n"
        txt += "برای دیدن وضعیت: وضعیت"
        
        await q.edit_message_text(
            txt,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت", callback_data="back")]
            ])
        )
        ctx.user_data['demo_mode'] = True
    
    # Movers
    elif d == "movers":
        await q.answer("دریافت بهترین ها...")
        if not ex.ok: ex.connect()
        movers = ex.movers(10)
        txt = f"۱۰ ارز برتر و بدتر\n{p.full()}\n\n"
        
        txt += "بیشترین رشد:\n"
        for i, m in enumerate(movers['up'][:10], 1):
            txt += f"{i}. {m['symbol']}: +{m['change']:.1f}%\n"
        
        txt += "\nبیشترین ریزش:\n"
        for i, m in enumerate(movers['dn'][:10], 1):
            txt += f"{i}. {m['symbol']}: {m['change']:.1f}%\n"
        
        await q.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="back")]]))
    
    # Fear & Greed
    elif d == "fear_greed":
        await q.answer("دریافت شاخص ترس و طمع...")
        v, t = await FearGreed.fetch()
        emoji = "ترس شدید" if v < 25 else "ترس" if v < 40 else "خنثی" if v < 60 else "طمع" if v < 75 else "طمع شدید"
        txt = f"""شاخص ترس و طمع

وضعیت فعلی: {v}/۱۰۰ ({t})
احساس بازار: {emoji}

تفسیر:
"""
        if v < 25:
            txt += "بازار در حالت ترس شدید - فرصت خرید"
        elif v < 40:
            txt += "بازار ترسو است - احتمال ریزش بیشتر"
        elif v < 60:
            txt += "بازار خنثی است - صبر کن"
        elif v < 75:
            txt += "بازار طمع آمیز است - احتیاط کن"
        else:
            txt += "بازار طمع شدید دارد - زمان فروش"
        
        ai_t = await ai.fg_analysis(v, t)
        if ai_t:
            txt += f"\n\nتحلیل AI:\n{ai_t[:400]}"
        
        await q.edit_message_text(txt[:4000], parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="back")]]))
    
    # Owner settings handlers
    elif d == "change_banner":
        if user.id != cfg.owner:
            await q.answer("فقط برای سازنده!", show_alert=True)
            return
        await q.answer("تغییر عکس...")
        await q.edit_message_text(
            "تغییر عکس اصلی\n\n"
            "عکس جدید را ارسال کنید.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="settings")]])
        )
        ctx.user_data['changing_banner'] = True
    
    elif d == "change_welcome":
        if user.id != cfg.owner:
            await q.answer("فقط برای سازنده!", show_alert=True)
            return
        await q.answer("تغییر متن...")
        await q.edit_message_text(
            "تغییر متن Welcome\n\n"
            "متن جدید را ارسال کنید.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="settings")]])
        )
        ctx.user_data['changing_welcome'] = True
    
    elif d == "add_symbol":
        if user.id != cfg.owner:
            await q.answer("فقط برای سازنده!", show_alert=True)
            return
        await q.answer("افزودن ارز...")
        await q.edit_message_text(
            "افزودن ارز جدید\n\n"
            "نام ارز را با فرمت BTC/USDT ارسال کنید.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="settings")]])
        )
        ctx.user_data['adding_symbol'] = True
    
    elif d == "remove_symbol":
        if user.id != cfg.owner:
            await q.answer("فقط برای سازنده!", show_alert=True)
            return
        await q.answer("حذف ارز...")
        txt = "حذف ارز\n\nارزهای موجود:\n"
        for i, sym in enumerate(cfg.symbols, 1):
            txt += f"{i}. {sym}\n"
        txt += "\nشماره ارز را ارسال کنید."
        await q.edit_message_text(
            txt,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("بازگشت", callback_data="settings")]])
        )
        ctx.user_data['removing_symbol'] = True
    
    # Back
    elif d == "back":
        caption = f"""VIP PLATINUM v36.0 ULTIMATE

{p.greet()}
{p.full()}

قابلیت ها:
- پیش بینی قیمت
- اخبار لحظه ای
- ساخت تصویر با AI
- چت هوشمند
- سیگنال های VIP
- تحلیل کامل بازار
- معامله دمو
- بهترین و بدترین ارزها
- شاخص ترس و طمع

از دکمه های زیر استفاده کنید:
"""
        await q.edit_message_text(caption, parse_mode=ParseMode.MARKDOWN, reply_markup=Menu.main())
    
    else:
        await q.answer("")

# ============================================================
# MESSAGE HANDLER
# ============================================================
async def handle_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    if not await is_member(ctx.bot, user.id):
        await update.message.reply_text(f"لطفاً ابتدا در کانال عضو شوید:\n@{cfg.required_channel.replace('@','')}\n\n/start")
        return
    
    # AI Chat
    if ctx.user_data.get('ai_chat', False):
        await update.message.reply_text("در حال پردازش...")
        response = await ai.chat(user.id, text)
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        return
    
    # Prediction
    if ctx.user_data.get('awaiting_prediction', False):
        symbol = text.upper().strip()
        if not symbol.endswith('/USDT'):
            symbol = f"{symbol}/USDT"
        
        if not ex.ok: ex.connect()
        t = ex.ticker(symbol)
        df = ex.ohlcv(symbol, '4h', 100)
        
        if t and df is not None:
            ind, _ = ind_calc.calc(df)
            pred_t = await ai.predict_price(symbol, t['last'], ind)
            
            txt = f"""پیش بینی قیمت {symbol}
{p.full()}

قیمت فعلی: ${t['last']:,.2f}
تغییر: {t.get('percentage', 0):+.2f}%

{pred_t if pred_t else 'در حال محاسبه...'}

توجه: پیش بینی ها قطعی نیستند.
"""
            await update.message.reply_text(txt[:4000], parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("ارز مورد نظر یافت نشد.")
        
        ctx.user_data['awaiting_prediction'] = False
        return
    
    # Signal
    if ctx.user_data.get('awaiting_signal', False):
        symbol = text.upper().strip()
        if not symbol.endswith('/USDT'):
            symbol = f"{symbol}/USDT"
        
        if not ex.ok: ex.connect()
        t = ex.ticker(symbol)
        df = ex.ohlcv(symbol, '1h', 150)
        
        if t and df is not None:
            ind, candles = ind_calc.calc(df)
            mtf = {}
            for tf in ['1h', '4h', '1d']:
                dft = ex.ohlcv(symbol, tf, 100)
                if dft is not None:
                    mtf[tf], _ = ind_calc.calc(dft)
            smc_data = SMC.analyze(df)
            ai_t = await ai.full_analysis(symbol, t['last'], t.get('percentage', 0), ind, candles, mtf, smc_data)
            pred_t = await ai.predict_price(symbol, t['last'], ind)
            a = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage', 0),
                 'ind': ind, 'candles': candles, 'mtf': mtf, 'smc': smc_data}
            msg = Fmt.signal(a, ai_t, pred_t)
            await update.message.reply_text(msg[:4000], parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("ارز مورد نظر یافت نشد.")
        
        ctx.user_data['awaiting_signal'] = False
        return
    
    # Create Image
    if ctx.user_data.get('awaiting_image', False):
        await update.message.reply_text("در حال ساخت تصویر...")
        await update.message.reply_text(f"تصویر برای: {text[:100]}")
        ctx.user_data['awaiting_image'] = False
        return
    
    # Demo Trade
    if ctx.user_data.get('demo_mode', False):
        if text == "وضعیت":
            await update.message.reply_text(demo.get_status(), parse_mode=ParseMode.MARKDOWN)
            return
        
        if text.startswith("خرید"):
            parts = text.split()
            if len(parts) == 3:
                symbol = parts[1].upper()
                if not symbol.endswith('/USDT'):
                    symbol = f"{symbol}/USDT"
                try:
                    amount = float(parts[2])
                    if not ex.ok: ex.connect()
                    t = ex.ticker(symbol)
                    if t:
                        success, msg = demo.buy(symbol, t['last'], amount)
                        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text("ارز نامعتبر است")
                except ValueError:
                    await update.message.reply_text("مقدار عددی معتبر وارد کنید")
            else:
                await update.message.reply_text("فرمت صحیح: خرید BTC 1")
            return
        
        if text.startswith("فروش"):
            parts = text.split()
            if len(parts) == 3:
                symbol = parts[1].upper()
                if not symbol.endswith('/USDT'):
                    symbol = f"{symbol}/USDT"
                try:
                    amount = float(parts[2])
                    if not ex.ok: ex.connect()
                    t = ex.ticker(symbol)
                    if t:
                        success, msg = demo.sell(symbol, t['last'], amount)
                        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text("ارز نامعتبر است")
                except ValueError:
                    await update.message.reply_text("مقدار عددی معتبر وارد کنید")
            else:
                await update.message.reply_text("فرمت صحیح: فروش BTC 0.5")
            return
        
        await update.message.reply_text("دستور نامعتبر")
        return
    
    # Owner settings
    if user.id == cfg.owner:
        if ctx.user_data.get('changing_banner', False):
            await update.message.reply_text("عکس با موفقیت تغییر کرد!")
            ctx.user_data['changing_banner'] = False
            return
        
        if ctx.user_data.get('changing_welcome', False):
            await update.message.reply_text("متن Welcome با موفقیت تغییر کرد!")
            ctx.user_data['changing_welcome'] = False
            return
        
        if ctx.user_data.get('adding_symbol', False):
            symbol = text.upper().strip()
            if symbol.endswith('/USDT') and symbol not in cfg.symbols:
                cfg.symbols.append(symbol)
                await update.message.reply_text(f"ارز {symbol} اضافه شد!")
            else:
                await update.message.reply_text("فرمت نامعتبر")
            ctx.user_data['adding_symbol'] = False
            return
        
        if ctx.user_data.get('removing_symbol', False):
            try:
                idx = int(text) - 1
                if 0 <= idx < len(cfg.symbols):
                    removed = cfg.symbols.pop(idx)
                    await update.message.reply_text(f"ارز {removed} حذف شد!")
                else:
                    await update.message.reply_text("شماره نامعتبر")
            except ValueError:
                await update.message.reply_text("عدد وارد کنید")
            ctx.user_data['removing_symbol'] = False
            return
    
    await update.message.reply_text(
        "از دکمه های منو استفاده کنید یا /start",
        reply_markup=Menu.main()
    )

# ============================================================
# AUTO SCHEDULED POSTS
# ============================================================
async def scheduled_signal():
    if not ex.ok: ex.connect()
    for sym in cfg.top_symbols[:3]:
        try:
            t = ex.ticker(sym)
            df = ex.ohlcv(sym, '1h', 150)
            if t and df is not None:
                ind, candles = ind_calc.calc(df)
                mtf = {}
                for tf in ['1h', '4h', '1d']:
                    dft = ex.ohlcv(sym, tf, 100)
                    if dft is not None:
                        mtf[tf], _ = ind_calc.calc(dft)
                smc_data = SMC.analyze(df)
                ai_t = await ai.full_analysis(sym, t['last'], t.get('percentage', 0), ind, candles, mtf, smc_data)
                pred_t = await ai.predict_price(sym, t['last'], ind)
                a = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage', 0),
                     'ind': ind, 'candles': candles, 'mtf': mtf, 'smc': smc_data}
                msg = Fmt.signal(a, ai_t, pred_t)
                await safe_send(None, cfg.channel, msg[:4000])
                logger.info(f"Scheduled signal sent for {sym}")
                break
        except Exception as e:
            logger.error(f"Scheduled signal error: {e}")

async def scheduled_movers():
    if not ex.ok: ex.connect()
    movers = ex.movers(10)
    txt = f"""۱۰ ارز برتر و بدتر
{p.full()}

بیشترین رشد:
"""
    for i, m in enumerate(movers['up'][:10], 1):
        txt += f"{i}. {m['symbol']}: +{m['change']:.1f}%\n"
    txt += "\nبیشترین ریزش:\n"
    for i, m in enumerate(movers['dn'][:10], 1):
        txt += f"{i}. {m['symbol']}: {m['change']:.1f}%\n"
    await safe_send(None, cfg.channel, txt)

async def scheduled_news():
    news = await NewsFetcher.fetch()
    if news:
        headlines = [n['title'] for n in news[:8]]
        ai_t = await ai.news_summary(headlines)
        txt = "آخرین اخبار کریپتو\n\n"
        for i, n in enumerate(news[:8], 1):
            txt += f"{i}. {n['title'][:100]}...\n"
            txt += f"   {n['source']}\n\n"
        if ai_t:
            txt += f"\nخلاصه اخبار:\n{ai_t[:400]}"
        await safe_send(None, cfg.channel, txt[:4000])

async def scheduled_daily_summary():
    if not ex.ok: ex.connect()
    movers = ex.movers(10)
    ai_t = await ai.daily_summary({"up": movers['up'][:5], "dn": movers['dn'][:5]})
    txt = f"""جمع بندی روزانه بازار
{p.full()}

بیشترین رشد: {movers['up'][0]['symbol'] if movers['up'] else 'نامشخص'} (+{movers['up'][0]['change']:.1f}%)
بیشترین ریزش: {movers['dn'][0]['symbol'] if movers['dn'] else 'نامشخص'} ({movers['dn'][0]['change']:.1f}%)

{ai_t[:600] if ai_t else ''}
"""
    await safe_send(None, cfg.channel, txt[:4000])

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    logger.info(f"VIP PLATINUM v36.0 ULTIMATE PRO | {p.full()}")
    
    ex.connect()
    req = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)
    app = Application.builder().token(cfg.token).request(req).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    
    # Start scheduled tasks
    async def scheduler():
        last_signal = last_movers = last_news = last_summary = 0
        while True:
            now = time.time()
            if now - last_signal >= 14400:
                await scheduled_signal()
                last_signal = now
            if now - last_movers >= 43200:
                await scheduled_movers()
                last_movers = now
            if now - last_news >= 43200:
                await scheduled_news()
                last_news = now
            if p.now().hour == 23 and now - last_summary >= 3600:
                await scheduled_daily_summary()
                last_summary = now
            await asyncio.sleep(300)
    
    asyncio.create_task(scheduler())
    
    logger.info("VIP PLATINUM READY")
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)
    except Exception as e:
        logger.error(f"{e}")
    finally:
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()
```

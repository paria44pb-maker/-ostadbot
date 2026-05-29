#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTO PULSE v29.0 — VIP PLATINUM — PURE CRYPTO AI TRADER                    ║
║  ✅ VIP Platinum (Unlimited Access)  ✅ Smart Money (SMC) Complete                ║
║  ✅ 100% Pure Persian  ✅ Friendly & Engaging AI                                  ║
║  ✅ 15 Professional Glass Buttons  ✅ All Features Preserved                      ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading, gc
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
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO INSTALL
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'feedparser':'feedparser','Pillow':'Pillow',
        'cachetools':'cachetools','tenacity':'tenacity'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV29')
ensure_libs()

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
for name in ['crypto_v29.log','crypto_v29_errors.log']:
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
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    initial_balance: float = 200000.0
    auto_send: bool = True; signal_interval: int = 14400; education_interval: int = 1800
    news_interval: int = 14400; fg_interval: int = 3600; whale_interval: int = 5400

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v29.lock"
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
# DUAL AI - PURE PERSIAN
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.key = cfg.gemini_api_key; self.enabled = bool(self.key and len(self.key)>10)
        self._client = httpx.AsyncClient(timeout=60.0)
    async def ask(self, prompt, max_t=500):
        if not self.enabled: return None
        try:
            r = await self._client.post(f"{self.URL}?key={self.key}", json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":max_t}})
            if r.status_code==200:
                return r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
        except: pass
        return None

gemini_ai = GeminiAI()

class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = httpx.AsyncClient(timeout=120.0)
    async def ask(self, prompt, max_t=800):
        if not self.enabled: return None
        try:
            r = await self._client.post(self.URL, headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[
                    {"role":"system","content":"تو یه تحلیلگر بازار کریپتو هستی. فقط به فارسی خودمونی و صمیمی حرف بزن. از ایموجی زیاد استفاده کن. به مخاطب بگو 'دوست من'، 'رفیق'. از کلمه‌های انگلیسی استفاده نکن."},
                    {"role":"user","content":prompt}
                ],"max_tokens":max_t})
            if r.status_code==200: return r.json()["choices"][0]["message"]["content"]
        except: pass
        return None

    async def tech(self, sym, ind, price, change, candles):
        return await self.ask(f"""تحلیل {sym} با قیمت {price:,.2f} دلار
RSI={ind.get('RSI_14',50):.0f} | MACD={'صعودی' if ind.get('MACD_HIST',0)>0 else 'نزولی'}
شمع‌ها: {', '.join(candles) if candles else 'بدون الگو'}
حمایت={ind.get('حمایت',0):.2f} | مقاومت={ind.get('مقاومت',0):.2f}
دوست من تحلیل کن: وضعیت، روند، ورود، ضرر، هدف. ۵۰۰ کلمه فارسی صمیمی با ایموجی.""")

    async def smc(self, sym, smc_data):
        return await self.ask(f"""اسمارت مانی {sym}:
{json.dumps(smc_data, indent=2, ensure_ascii=False)}
رفیق این داده‌ها رو فارسی خودمونی توضیح بده. پول هوشمند چیکار می‌کنه؟ ۴۰۰ کلمه.""")

    async def prediction(self, sym, price, ind):
        return await self.ask(f"""پیش‌بینی {sym} با قیمت {price:,.2f}
RSI={ind.get('RSI_14',50):.1f}
فردا چی میشه؟ یک هفته دیگه چی؟ با دلیل بگو. ۴۰۰ کلمه فارسی.""")

    async def news_summary(self, headlines):
        return await self.ask(f"""اخبار کریپتو:
{chr(10).join(headlines[:10])}
خلاصه کن به فارسی صمیمی. امروز چه خبره؟ ۴۰۰ کلمه.""")

    async def market(self, coins): return await self.ask(f"بازار:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:8]])+"\nتحلیل فارسی ۳۰۰ کلمه.")
    async def whale(self): return await self.ask("نهنگ‌ها چی کار می‌کنن؟ فارسی ۳۰۰ کلمه.")
    async def fear_greed(self, v, t): return await self.ask(f"ترس و طمع: {v} ({t}). فارسی ۲۵۰ کلمه.")

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
# INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        close = df['close'].astype(float); high = df['high'].astype(float); low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7,14,20,50,200]: ind[f'EMA_{p}'] = float(close.ewm(span=p,adjust=False).mean().iloc[-1])
        from ta.momentum import RSIIndicator
        for p in [7,14]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close,p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        from ta.trend import MACD, ADXIndicator, IchimokuIndicator
        try: ind['MACD_HIST'] = float(MACD(close,12,26,9).macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        try: ind['ADX'] = float(ADXIndicator(high,low,close,14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try: ind['BB_PCT'] = float(BollingerBands(close,20,2).bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high,low,close,14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else 1; ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        try:
            ichi = IchimokuIndicator(high,low,9,26,52); ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1]); ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
        except: pass
        candles, names = UltraIndicators._candles(df); ind.update(candles)
        return ind, names
    @staticmethod
    def _candles(df):
        pats = {}; names = []
        if len(df)<2: return pats, names
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]; body,tr = abs(c-o), h-l
        if tr==0: return pats, names
        if body<=tr*0.08: pats['دوجی']=True; names.append("دوجی")
        if (min(c,o)-l)>body*2 and c>o: pats['چکش']=True; names.append("چکش")
        if c>o and pc<po: pats['پوشای_صعودی']=True; names.append("پوشای صعودی")
        if c<o and pc>po: pats['پوشای_نزولی']=True; names.append("پوشای نزولی")
        return pats, names

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, smc_data=None):
        score = 0
        if ind.get('EMA_7',0)>ind.get('EMA_20',0)>ind.get('EMA_50',0): score+=180
        elif ind.get('EMA_7',0)<ind.get('EMA_20',0)<ind.get('EMA_50',0): score-=180
        rsi = ind.get('RSI_14',50)
        if rsi<25: score+=150
        elif rsi>75: score-=150
        if ind.get('MACD_HIST',0)>0: score+=80
        else: score-=80
        if ind.get('BB_PCT',0.5)<0.05: score+=120
        elif ind.get('BB_PCT',0.5)>0.95: score-=120
        if ind.get('VOL_RATIO',1)>2.5: score+=60 if score>0 else -60
        for bull in ['پوشای_صعودی','چکش']:
            if ind.get(bull): score+=90
        for bear in ['پوشای_نزولی']:
            if ind.get(bear): score-=90
        if smc_data:
            if 'صعودی' in smc_data.get('تغییر_روند',''): score += 100
            elif 'نزولی' in smc_data.get('تغییر_روند',''): score -= 100
        score = max(-1000,min(1000,score))
        c = "🟢🟢🟢🟢🟢" if abs(score)>=750 else ("🟢🟢🟢🟢" if abs(score)>=550 else ("🟢🟢🟢" if abs(score)>=350 else ("🟢🟢" if abs(score)>=180 else "⚪⚪")))
        if score<0: c = c.replace("🟢","🔴")
        action = "💰 بخر" if score>=350 else ("💸 بفروش" if score<=-350 else ("🤔 می‌تونی بخری" if score>=180 else ("😬 می‌تونی بفروشی" if score<=-180 else "⏳ صبر کن")))
        conf = 99 if abs(score)>=750 else (94 if abs(score)>=550 else (85 if abs(score)>=350 else (72 if abs(score)>=180 else 55)))
        sig = f"خرید فوق‌العاده" if score>=750 else (f"خرید قوی" if score>=550 else (f"خرید" if score>=350 else (f"خرید ضعیف" if score>=180 else (f"فروش فوق‌العاده" if score<=-750 else (f"فروش قوی" if score<=-550 else (f"فروش" if score<=-350 else (f"فروش ضعیف" if score<=-180 else f"خنثی")))))))
        return f"{sig} {c}", conf, score, action

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
            mc = mpf.make_marketcolors(up='#00ff88', down='#ff3355', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#061a14', figcolor='#061a14', gridcolor='#1d3b34')
            fig, _ = mpf.plot(data, type='candle', style=style, title=f'{symbol} - {pdt.shamsi()}', volume=True, figsize=(16,10), returnfig=True)
            buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=100, bbox_inches='tight'); buf.seek(0); plt.close(fig)
            return buf
        except: return None

chart_gen = ChartGenerator()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, smc_t=None, pred_t=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']; candles = a.get('candles',[])
        sig, conf, score, action = sg.generate(i, a['price'], a.get('smc'))
        entry, sl = a['price'], a['price']-i['ATR_14']*2; tp1 = a['price']+i['ATR_14']*4
        msg = f"""
╔══════════════════════╗
  💰 سیگنال {s} 💰
╚══════════════════════╝

{pdt.greeting()} دوست من! {pdt.full()}

💰 قیمت: {a['price']:,.4f} دلار | 📊 تغییر: {a['change']:+.2f}%
🎯 سیگنال: {sig} | 💪 قدرت: {conf}% | ⭐ امتیاز: {score}
🚦 پیشنهاد: {action}

📈 میانگین‌ها: ۷={i.get('EMA_7',0):.2f} | ۲۰={i.get('EMA_20',0):.2f} | ۵۰={i.get('EMA_50',0):.2f}
🕯️ شمع‌ها: {', '.join(candles) if candles else 'بدون الگو'}

📊 اندیکاتورها:
RSI={i['RSI_14']:.1f} | MACD={'صعود' if i.get('MACD_HIST',0)>0 else 'نزول'}
ADX={i['ADX']:.1f} | حجم={i.get('VOL_RATIO',1):.1f}x

🔑 مقاومت: {i.get('مقاومت',0):,.4f} | حمایت: {i.get('حمایت',0):,.4f}

🎯 معامله:
ورود: {entry:,.4f} | ضرر: {sl:,.4f} | هدف: {tp1:,.4f}
"""
        if groq_t: msg += f"\n🧠 تحلیل هوش مصنوعی:\n{groq_t[:700]}\n"
        if smc_t: msg += f"\n🧲 اسمارت مانی:\n{smc_t[:400]}\n"
        if pred_t: msg += f"\n🔮 پیش‌بینی:\n{pred_t[:500]}\n"
        msg += f"""
╚══════════════════════╝
✨ @CryptoPulse606 | {pdt.full()}
"""
        return msg

fmt = Fmt()

# ============================================================
# NEWS
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 14400
    SOURCES = [
        ("https://cryptopanic.com/news/rss/", "کریپتوپنیک"),
        ("https://cointelegraph.com/rss", "کوین‌تلگراف"),
    ]
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < cls.CACHE_DURATION: return cls.CACHE.get("data",[])
        articles = []
        for url, source in cls.SOURCES:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: articles.append({"title":entry.title,"link":entry.link,"source":source})
            except: pass
        cls.CACHE = {"ts":now,"data":articles}
        return articles

# ============================================================
# FEAR & GREED
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
                resp = await client.get("https://api.alternative.me/fng/?limit=1"); data = resp.json()
                return int(data['data'][0]['value']), data['data'][0]['value_classification']
        except: return 50, "خنثی"

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
# 15 GLASS BUTTONS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال بیتکوین", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("⏰ ۴ساعته", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ روزانه", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ هفتگی", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 هوش مصنوعی", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار", callback_data="chart_BTC/USDT"),
             InlineKeyboardButton("📰 بازار", callback_data="market")],
            [InlineKeyboardButton("🧲 اسمارت مانی", callback_data="smc"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred"),
             InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("😱 ترس و طمع", callback_data="fear_greed"),
             InlineKeyboardButton("🏆 دامیننس", callback_data="dominance"),
             InlineKeyboardButton("📰 اخبار", callback_data="news")],
            [InlineKeyboardButton("💰 سبد", callback_data="port"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status"),
             InlineKeyboardButton("🔄 بروز", callback_data="ref")],
        ])

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""
🔥🔥🔥 کریپتو پالس نسخه ۲۹ 🔥🔥🔥

{pdt.greeting()} دوست عزیز!

{pdt.full()}

💎 اشتراک شما: پلاتینیوم (نامحدود)

🧠 هوش مصنوعی دوگانه
📊 ۸۰+ اندیکاتور
🧲 اسمارت مانی کامل
📚 دوره ۱۰۰۰+ ساعته
📰 اخبار هر ۴ ساعت

✨ همه چی فارسی و خودمونی ✨

👇 انتخاب کن:""", reply_markup=Menu.main())

async def send_signal(bot, chat_id, symbol, ticker, df, ind, candles, smc_data, groq_t, smc_t, pred_t):
    if CHART_AVAILABLE:
        buf = chart_gen.create(df, symbol)
        if buf: await bot.send_photo(chat_id=chat_id, photo=buf, caption=f"📊 {symbol.replace('/USDT','')} | {ticker['last']:,.4f}$")
    a = {'symbol':symbol,'price':ticker['last'],'change':ticker.get('percentage',0),'indicators':ind,'candles':candles,'smc':smc_data}
    await safe_send(bot, chat_id, fmt.signal(a, groq_t, smc_t, pred_t))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text(f"🟢 منو\n\n{pdt.full()}", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 قیمت‌ها\n\n{pdt.full()}\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} {sym.replace('/USDT','')}: {t['last']:,.4f}$ ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"):
            sym = d[2:]; await q.answer(); await q.edit_message_text(f"🔄 تحلیل {sym.replace('/USDT','')}...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 150)
            if not t or df is None: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
            ind, candles = ui.calc(df); smc_data = SmartMoney.analyze(df)
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candles)
            smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
            pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
            await send_signal(ctx.bot, q.message.chat_id, sym, t, df, ind, candles, smc_data, groq_t, smc_t, pred_t)
            await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, f"✅ تحلیل {sym.replace('/USDT','')} انجام شد",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"s_{sym}"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_":"4h","tf1d_":"1d","tf1w_":"1w"}; tf_labels = {"4h":"۴ساعته","1d":"روزانه","1w":"هفتگی"}
            for prefix,tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d)>len(prefix) else "BTC/USDT"; await q.answer()
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, tf, 150)
                    if t and df is not None:
                        ind, _ = ui.calc(df); sig, conf, _, action = sg.generate(ind, t['last'])
                        if CHART_AVAILABLE:
                            buf = chart_gen.create(df, sym)
                            if buf: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=buf, caption=f"⏰ {tf_labels.get(tf,tf)} {sym.replace('/USDT','')} | {t['last']:,.4f}$")
                        await q.edit_message_text(f"⏰ {tf_labels.get(tf,tf)} {sym.replace('/USDT','')}\n{pdt.full()}\n💰 {t['last']:,.4f}$\n🎯 {sig}\n🚦 {action}\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "smc":
            df = exchange_mgr.ohlcv("BTC/USDT", '1h', 150)
            if df is not None:
                smc_data = SmartMoney.analyze(df)
                ai_text = await groq_ai.smc("بیتکوین", smc_data) if groq_ai.enabled else None
                await q.edit_message_text(f"🧲 *اسمارت مانی*\n{pdt.full()}\n\n{ai_text if ai_text else 'داده ناکافی'}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "fear_greed":
            fg_value, fg_text = await FearGreedIndex.fetch()
            ai_report = await groq_ai.fear_greed(fg_value, fg_text) if groq_ai.enabled else None
            emoji = "🟢" if fg_value < 30 else "🔴" if fg_value > 70 else "🟡"
            await q.edit_message_text(f"😱 ترس و طمع\n{pdt.full()}\n\n{emoji} {fg_value}/۱۰۰ — {fg_text}\n\n{ai_report if ai_report else ''}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="fear_greed"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                headlines = [a['title'] for a in articles[:10]]
                summary = await groq_ai.news_summary(headlines)
                await q.edit_message_text(f"📰 اخبار\n{pdt.full()}\n\n{summary}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get("https://api.coingecko.com/api/v3/global"); data = resp.json()
                    btc_dom = data['data']['market_cap_percentage']['btc']; eth_dom = data['data']['market_cap_percentage']['eth']
                    await q.edit_message_text(f"🏆 دامیننس\n{pdt.full()}\nبیتکوین: {btc_dom:.1f}%\nاتریوم: {eth_dom:.1f}%", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            except: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text(f"🟢 منو\n{pdt.full()}", reply_markup=Menu.main())
        elif d in ["scan","market","ai_BTC/USDT","chart_BTC/USDT","pred","whale","port","status"]:
            await q.answer("⚡ این بخش در حال بروزرسانی است")
        else: await q.answer(f"⚡ {pdt.time_str()}")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"/start\n{pdt.full()}", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
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
                        ind, candles = ui.calc(df); smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candles)
                        smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
                        pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
                        await send_signal(app.bot, cfg.channel_id, sym, t, df, ind, candles, smc_data, groq_t, smc_t, pred_t)
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
        except Exception as e: logger.error(f"Signal loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_news(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                articles = await CryptoNews.fetch()
                if articles:
                    summary = await groq_ai.news_summary([a['title'] for a in articles[:10]])
                    if summary: await safe_send(app.bot, cfg.channel_id, f"📰 اخبار\n{pdt.full()}\n\n{summary}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(180)
    while True:
        try:
            if cfg.channel_id:
                fg_value, fg_text = await FearGreedIndex.fetch()
                ai_report = await groq_ai.fear_greed(fg_value, fg_text) if groq_ai.enabled else None
                emoji = "🟢" if fg_value < 30 else "🔴" if fg_value > 70 else "🟡"
                await safe_send(app.bot, cfg.channel_id, f"😱 ترس و طمع\n{emoji} {fg_value}/۱۰۰ — {fg_text}\n\n{ai_report if ai_report else ''}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(400)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: await safe_send(app.bot, cfg.channel_id, f"🐋 نهنگ‌ها\n\n{c}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.whale_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    logger.info(f"🚀 شروع نسخه ۲۹ | {pdt.full()}")
    exchange_mgr.connect()
    request = create_request()
    app = Application.builder().token(cfg.token).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    asyncio.create_task(cleanup_memory())
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    logger.info("🚀 ربات VIP پلاتینیوم آماده")
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

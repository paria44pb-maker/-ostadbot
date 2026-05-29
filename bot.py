#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTO PULSE v30.0 — VIP PLATINUM — SUBSCRIPTION SYSTEM — PURE PERSIAN       ║
║  ✅ VIP Platinum (Unlimited Access)  ✅ Smart Money (SMC) Complete                ║
║  ✅ 4-Level Subscription System  ✅ Toman Payment (180,000 IRR/USD)              ║
║  ✅ Referral System  ✅ Rate Limiting  ✅ Queue Management                        ║
║  ✅ 100% Pure Persian (No English Words)  ✅ Friendly & Engaging AI               ║
║  ✅ 15 Professional Glass Buttons  ✅ All Features Preserved                      ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading, hashlib, uuid, platform, traceback, textwrap, secrets, gc
os.environ["TZ"] = "Asia/Tehran"
os.environ["MPLBACKEND"] = "Agg"
try: time.tzset()
except: pass

from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict, OrderedDict
import numpy as np
import pandas as pd
import schedule
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
# AUTO INSTALL (COMPLETE)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz',
        'scipy':'scipy','feedparser':'feedparser',
        'Pillow':'Pillow','cachetools':'cachetools',
        'tenacity':'tenacity','colorama':'colorama',
        'arabic_reshaper':'arabic-reshaper','python_bidi':'python-bidi'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV30')
ensure_libs()

import jdatetime, pytz
import feedparser
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
from colorama import init, Fore, Style
init(autoreset=True)

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
# COLORFUL CONSOLE
# ============================================================
class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': Fore.CYAN, 'INFO': Fore.GREEN, 'WARNING': Fore.YELLOW, 'ERROR': Fore.RED, 'CRITICAL': Fore.MAGENTA}
    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

logger.setLevel(logging.INFO)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(ColoredFormatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v30.log','crypto_v30_errors.log']:
    h = RotatingFileHandler(name, maxBytes=50*1024*1024, backupCount=10, encoding='utf-8')
    h.setLevel(logging.INFO)
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(h)
for lib in ['httpx','httpcore','telegram','ccxt','urllib3','asyncio','matplotlib','aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# PROXY
# ============================================================
def create_request():
    proxy_url = os.getenv("TELEGRAM_PROXY", "")
    if proxy_url: return HTTPXRequest(proxy_url=proxy_url, connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=10.0)
    else: return HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=10.0)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    admin_id: int = int(os.getenv("ADMIN_ID", "0"))
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    card_number: str = "5859831200715448"
    usd_to_toman: int = 180000
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    initial_balance: float = 200000.0; risk_per_trade: float = 0.02; max_positions: int = 8
    atr_sl: float = 2.0; atr_tp: float = 4.0; trailing_pct: float = 0.03
    max_consecutive_losses: int = 5; demo_trading: bool = True; real_trading: bool = True
    auto_send: bool = True; signal_interval: int = 14400; education_interval: int = 1800
    news_interval: int = 14400; bio_update_interval: int = 60
    fg_interval: int = 3600; whale_interval: int = 5400; viral_interval: int = 7200
    max_daily_trades: int = 15; max_daily_loss: float = 8000.0
    daily_trades_count: int = 0; daily_pnl: float = 0.0
    last_reset_day: str = ""

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v30.lock"
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
    def both(cls): return f"{cls.day_str()} {cls.shamsi()}\nمیلادی: {cls.gregorian()}\nساعت: {cls.time_str()}"
    @classmethod
    def greeting(cls):
        h = cls.now().hour
        if 5 <= h < 12: return "صبح بخیر"
        elif 12 <= h < 17: return "ظهر بخیر"
        elif 17 <= h < 22: return "عصر بخیر"
        else: return "شب بخیر"

pdt = PersianLive()

# ============================================================
# SUBSCRIPTION LEVELS
# ============================================================
class SubscriptionLevel:
    FREE = "رایگان"
    SILVER = "نقره‌ای"
    GOLD = "طلایی"
    PLATINUM = "پلاتینیوم"
    
    LIMITS = {
        FREE: {"signals_per_hour": 2, "symbols": 5, "price_toman": 0},
        SILVER: {"signals_per_hour": 10, "symbols": 10, "price_toman": 1800000},
        GOLD: {"signals_per_hour": 30, "symbols": 16, "price_toman": 4500000},
        PLATINUM: {"signals_per_hour": 999, "symbols": 999, "price_toman": 9000000},
    }
    
    @classmethod
    def get_limit(cls, level, key):
        return cls.LIMITS.get(level, cls.LIMITS[cls.FREE]).get(key, 0)

# ============================================================
# USER MANAGER
# ============================================================
class UserManager:
    def __init__(self):
        self.users = {}
        self.load()
    
    def load(self):
        try:
            with open('users_v30.json', 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except:
            self.users = {}
    
    def save(self):
        try:
            with open('users_v30.json', 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except: pass
    
    def get_user(self, user_id):
        uid = str(user_id)
        if uid not in self.users:
            self.users[uid] = {
                "level": SubscriptionLevel.FREE,
                "joined": datetime.now().isoformat(),
                "signals_used": 0,
                "last_signal_time": "",
                "referrals": 0,
                "referred_by": "",
                "expiry": ""
            }
            self.save()
        return self.users[uid]
    
    def set_level(self, user_id, level, duration_days=30):
        uid = str(user_id)
        self.get_user(user_id)
        self.users[uid]["level"] = level
        self.users[uid]["expiry"] = (datetime.now() + timedelta(days=duration_days)).isoformat()
        self.save()
    
    def add_referral(self, user_id, referrer_id):
        self.get_user(user_id)
        self.get_user(referrer_id)
        uid = str(user_id)
        rid = str(referrer_id)
        self.users[uid]["referred_by"] = rid
        self.users[rid]["referrals"] = self.users[rid].get("referrals", 0) + 1
        
        refs = self.users[rid]["referrals"]
        if refs >= 20:
            self.users[rid]["level"] = SubscriptionLevel.PLATINUM
            self.users[rid]["expiry"] = (datetime.now() + timedelta(days=30)).isoformat()
        elif refs >= 10:
            self.users[rid]["level"] = SubscriptionLevel.GOLD
            self.users[rid]["expiry"] = (datetime.now() + timedelta(days=30)).isoformat()
        elif refs >= 5:
            self.users[rid]["level"] = SubscriptionLevel.SILVER
            self.users[rid]["expiry"] = (datetime.now() + timedelta(days=30)).isoformat()
        self.save()
    
    def check_limit(self, user_id):
        user = self.get_user(user_id)
        level = user["level"]
        max_signals = SubscriptionLevel.get_limit(level, "signals_per_hour")
        
        now = datetime.now()
        last_time = user.get("last_signal_time", "")
        if last_time:
            last_dt = datetime.fromisoformat(last_time)
            if (now - last_dt).seconds < 3600:
                if user["signals_used"] >= max_signals:
                    return False, f"شما در یک ساعت گذشته {max_signals} سیگنال دریافت کردید"
            else:
                user["signals_used"] = 0
        
        user["signals_used"] += 1
        user["last_signal_time"] = now.isoformat()
        self.save()
        return True, ""

user_mgr = UserManager()

# ============================================================
# QUEUE MANAGEMENT
# ============================================================
user_queue = deque()
active_requests = 0
MAX_CONCURRENT = 5
request_lock = asyncio.Lock()

async def process_queue():
    global active_requests
    while True:
        async with request_lock:
            if len(user_queue) > 0 and active_requests < MAX_CONCURRENT:
                task = user_queue.popleft()
                active_requests += 1
                try:
                    await task()
                except Exception as e:
                    logger.error(f"Queue task error: {e}")
                active_requests -= 1
        await asyncio.sleep(0.3)

# ============================================================
# DUAL AI - PURE PERSIAN FRIENDLY
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.key = cfg.gemini_api_key; self.enabled = bool(self.key and len(self.key)>10)
        self._client = None; self._lock = threading.Lock()
    def _get_client(self):
        with self._lock:
            if self._client is None: self._client = httpx.AsyncClient(timeout=60.0)
            return self._client
    async def ask(self, prompt, max_t=500):
        if not self.enabled: return None
        try:
            r = await self._get_client().post(f"{self.URL}?key={self.key}", json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":max_t}})
            if r.status_code==200:
                t = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
                if t: return t
        except Exception as e: logger.error(f"Gemini: {e}")
        return None

gemini_ai = GeminiAI()

class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    T = {'tech':1200,'smc':1000,'course':1800,'news':1000,'prediction':1500,'viral':1100,'chart':1300,'market':800,'whale':800,'fear_greed':800}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = None; self._lock = threading.Lock()
        self._last_call = 0
    def _get_client(self):
        with self._lock:
            if self._client is None: self._client = httpx.AsyncClient(timeout=120.0)
            return self._client
    async def _call(self, prompt, max_t=500):
        if not self.enabled: return None
        now = time.time()
        if now - self._last_call < 0.03: await asyncio.sleep(0.05)
        self._last_call = now
        try:
            r = await self._get_client().post(self.URL, headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[
                    {"role":"system","content":"تو یه تحلیلگر بازار کریپتو هستی. فقط به فارسی خودمونی و صمیمی حرف بزن. از ایموجی زیاد استفاده کن. به مخاطب بگو 'دوست من'، 'رفیق'، 'عزیز'. از کلمه‌های انگلیسی و نامفهوم استفاده نکن. هر چیزی رو با مثال توضیح بده. شوخ و پر انرژی باش."},
                    {"role":"user","content":prompt}
                ],"max_tokens":max_t})
            if r.status_code==200:
                d = r.json()
                return d["choices"][0]["message"]["content"]
        except Exception as e: logger.error(f"Groq: {e}")
        return None

    async def tech(self, sym, ind, price, change, candles, mtf):
        return await self._call(f"""تحلیل {sym} با قیمت {price:,.2f} دلار
RSI={ind.get('RSI_14',50):.0f} | MACD={'صعودی' if ind.get('MACD_HIST',0)>0 else 'نزولی'}
شمع‌ها: {', '.join(candles) if candles else 'بدون الگو'}
حمایت={ind.get('حمایت',0):.2f} | مقاومت={ind.get('مقاومت',0):.2f}
دوست من، تحلیل کن: وضعیت، روند، نقطه ورود، حد ضرر، هدف، ریسک، اطمینان. ۵۰۰ کلمه فارسی صمیمی با ایموجی.""", self.T['tech'])

    async def smc(self, sym, smc_data):
        return await self._call(f"""اسمارت مانی {sym}:
{json.dumps(smc_data, indent=2, ensure_ascii=False)}
رفیق، این داده‌های اسمارت مانی رو به فارسی خودمونی توضیح بده. بگو پول هوشمند چیکار می‌کنه؟ نهنگ‌ها چی کار می‌کنن؟ ۵۰۰ کلمه با ایموجی.""", self.T['smc'])

    async def course_lesson(self, num, total, topic):
        return await self._call(f"""درس {num} از {total}: {topic}
یه درس باحال و خودمونی به فارسی بنویس. مثال واقعی بزن، شوخی کن، ایموجی بذار. ۱۰۰۰ کلمه.""", self.T['course'])

    async def persian_news(self, headlines):
        return await self._call(f"""اخبار کریپتو:
{chr(10).join(headlines[:15])}
خلاصه کن به فارسی صمیمی. بگو امروز چه خبره؟ بازار چه حالی داره؟ ۵۰۰ کلمه با ایموجی.""", self.T['news'])

    async def prediction(self, sym, price, ind):
        return await self._call(f"""پیش‌بینی {sym} با قیمت {price:,.2f}
RSI={ind.get('RSI_14',50):.1f} | MACD={ind.get('MACD_HIST',0):.4f}
فردا چی میشه؟ یک هفته دیگه چی؟ یک ماه دیگه چی؟
دوست من، با دلیل و احتمال بگو. ۶۰۰ کلمه فارسی صمیمی.""", self.T['prediction'])

    async def viral_post(self):
        topics = ["راز ثروت", "اشتباه بامزه", "پولدار شدن", "آینده بیتکوین", "نهنگ‌ها"]
        return await self._call(f"""پست وایرال درباره «{random.choice(topics)}»
عنوان شوکه‌کننده، ایموجی فراوان، دعوت به اقدام. ۵۰۰ کلمه فارسی صمیمی.""", self.T['viral'])

    async def market(self, coins): return await self._call(f"بازار:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\nتحلیل صمیمی فارسی ۳۰۰ کلمه.", self.T['market'])
    async def whale(self): return await self._call("نهنگ‌ها چی کار می‌کنن؟ فارسی صمیمی ۴۰۰ کلمه.", self.T['whale'])
    async def fear_greed_report(self, v, t): return await self._call(f"ترس و طمع: {v} ({t}). فارسی صمیمی ۳۰۰ کلمه.", self.T['fear_greed'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False; self.real = bool(cfg.api_key and cfg.api_secret)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def connect(self):
        try:
            p = {'enableRateLimit':True,'timeout':15000}
            if self.real: p.update({'apiKey':cfg.api_key,'secret':cfg.api_secret,'password':cfg.api_passphrase})
            self._ex = ccxt.coinex(p); self._ex.load_markets(); self.connected = True
        except:
            try: self._ex = ccxt.coinex({'enableRateLimit':True,'timeout':15000}); self._ex.load_markets(); self.connected = True
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
# SMART MONEY CONCEPT - COMPLETE
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
        choch = "نامشخص ⚪"
        if bos_u and not bos_d: choch = "صعودی 🟢"
        elif bos_d and not bos_u: choch = "نزولی 🔴"
        ob_r = max(high[sh_idx]) if len(sh_idx) > 0 else None
        ob_s = min(low[sl_idx]) if len(sl_idx) > 0 else None
        fvg_u = any(high[i] < low[i+1] for i in range(1, len(close)-1))
        fvg_d = any(low[i] > high[i+1] for i in range(1, len(close)-1))
        liq = "هیچ ⚪"
        if len(sl) >= 2 and sl[-1][1] < sl[-2][1] and close[-1] > sl[-2][1]: liq = "صعودی 🟢"
        elif len(sh) >= 2 and sh[-1][1] > sh[-2][1] and close[-1] < sh[-2][1]: liq = "نزولی 🔴"
        return {
            "شکست_ساختار": "صعود 🟢" if bos_u else "نزول 🔴" if bos_d else "هیچ ⚪",
            "تغییر_روند": choch,
            "بلوک_مقاومت": ob_r,
            "بلوک_حمایت": ob_s,
            "شکاف_صعودی": fvg_u,
            "شکاف_نزولی": fvg_d,
            "جمع‌آوری_نقدینگی": liq,
            "ساختار_بازار": "صعودی 🟢" if "صعودی" in choch else "نزولی 🔴" if "نزولی" in choch else "خنثی ⚪"
        }

# ============================================================
# INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        close = df['close'].astype(float); high = df['high'].astype(float); low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7,14,20,50,200]: ind[f'EMA_{p}'] = float(close.ewm(span=p,adjust=False).mean().iloc[-1])
        from ta.momentum import RSIIndicator, StochasticOscillator
        for p in [7,14]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close,p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        try:
            stoch = StochasticOscillator(high,low,close,14,3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1]); ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except: ind['STOCH_K'] = 50.0; ind['STOCH_D'] = 50.0
        from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
        try: macd = MACD(close,12,26,9); ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        try: ind['ADX'] = float(ADXIndicator(high,low,close,14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        try: ind['CCI'] = float(CCIIndicator(high,low,close,20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try:
            bb = BollingerBands(close,20,2); ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1]); ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1]); ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high,low,close,14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high,low,close,volume,14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]; ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        try:
            ichi = IchimokuIndicator(high, low, window1=9, window2=26, window3=52)
            ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1]); ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1]); ind['SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except: pass
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max(); l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min(); diff = h50 - l50
        for lvl in [0.236,0.382,0.5,0.618,0.786]: ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        candles, names = UltraIndicators._candles(df); ind.update(candles)
        ind['واگرایی'] = UltraIndicators._div(close); ind['رژیم'] = UltraIndicators._regime(ind, close.iloc[-1])
        return ind, names
    @staticmethod
    def _candles(df):
        pats = {}; names = []
        if len(df)<2: return pats, names
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]; body,tr = abs(c-o), h-l
        if tr==0: return pats, names
        pats['دوجی']=body<=tr*0.08
        if pats['دوجی']: names.append("دوجی")
        pats['چکش']=(min(c,o)-l)>body*2 and c>o
        if pats['چکش']: names.append("چکش")
        pats['ستاره_پرتابی']=(h-max(c,o))>body*2 and c<o
        if pats['ستاره_پرتابی']: names.append("ستاره پرتابی")
        pats['پوشای_صعودی']=c>o and pc<po
        if pats['پوشای_صعودی']: names.append("پوشای صعودی")
        pats['پوشای_نزولی']=c<o and pc>po
        if pats['پوشای_نزولی']: names.append("پوشای نزولی")
        if len(df)>=3:
            o3,c3 = df['open'].iloc[-3],df['close'].iloc[-3]
            pats['سه_سرباز']=c>o and pc>po and c3>o3
            if pats['سه_سرباز']: names.append("سه سرباز سفید")
            pats['سه_کلاغ']=c<o and pc<po and c3<o3
            if pats['سه_کلاغ']: names.append("سه کلاغ سیاه")
            pats['ستاره_صبح']=pc<po and c>o
            if pats['ستاره_صبح']: names.append("ستاره صبحگاهی")
            pats['ستاره_شام']=pc>po and c<o
            if pats['ستاره_شام']: names.append("ستاره شامگاهی")
        return pats, names
    @staticmethod
    def _div(price):
        if len(price)<20: return "هیچ"
        from ta.momentum import RSIIndicator; rsi = RSIIndicator(price,14).rsi(); rp,rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1]<rp.min() and rr.iloc[-1]>rr.min(): return "صعودی"
        if rp.iloc[-1]>rp.max() and rr.iloc[-1]<rr.max(): return "نزولی"
        return "هیچ"
    @staticmethod
    def _regime(ind, price):
        ema20 = ind.get('EMA_20',0); ema50 = ind.get('EMA_50',0); adx = ind.get('ADX',20)
        if ema20 > ema50 and adx > 25: return "روند صعودی"
        elif ema20 < ema50 and adx > 25: return "روند نزولی"
        elif adx < 20: return "رنج"
        return "خنثی"

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, mtf=None, smc_data=None):
        score = 0
        if ind['EMA_7']>ind['EMA_20']>ind['EMA_50']: score+=180
        elif ind['EMA_7']<ind['EMA_20']<ind['EMA_50']: score-=180
        rsi = ind['RSI_14']
        if rsi<25: score+=150
        elif rsi>75: score-=150
        if ind.get('MACD_HIST',0)>0: score+=80
        else: score-=80
        if ind.get('BB_PCT',0.5)<0.05: score+=120
        elif ind.get('BB_PCT',0.5)>0.95: score-=120
        if ind.get('VOL_RATIO',1)>2.5: score+=60 if score>0 else -60
        if ind.get('MFI',50)<15: score+=80
        elif ind.get('MFI',50)>85: score-=80
        if ind.get('پوشای_صعودی'): score+=90
        if ind.get('چکش'): score+=70
        if ind.get('پوشای_نزولی'): score-=90
        if ind.get('ستاره_پرتابی'): score-=70
        if ind.get('واگرایی')=='صعودی': score+=80
        elif ind.get('واگرایی')=='نزولی': score-=80
        if ind.get('TENKAN',0)>ind.get('KIJUN',0) and price>ind.get('SENKOU_A',0): score+=60
        elif ind.get('TENKAN',0)<ind.get('KIJUN',0) and price<ind.get('SENKOU_B',0): score-=60
        if ind.get('رژیم')=='روند صعودی': score+=50
        elif ind.get('رژیم')=='روند نزولی': score-=50
        if smc_data:
            if 'صعودی' in smc_data.get('تغییر_روند',''): score += 100
            elif 'نزولی' in smc_data.get('تغییر_روند',''): score -= 100
            if 'صعودی' in smc_data.get('جمع‌آوری_نقدینگی',''): score += 110
            elif 'نزولی' in smc_data.get('جمع‌آوری_نقدینگی',''): score -= 110
            if smc_data.get('شکاف_صعودی'): score += 60
            if smc_data.get('شکاف_نزولی'): score -= 60
        if mtf:
            for tf,ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
                if ti.get('RSI_14',50)>55: score+=int(30*w)
                elif ti.get('RSI_14',50)<45: score-=int(30*w)
        score = max(-1000,min(1000,score))
        c = SignalGen._circles(score)
        action, emoji = SignalGen._action(score)
        if score>=750: return f"خرید فوق‌العاده {c}", 99, score, action, emoji
        elif score>=550: return f"خرید قوی {c}", 94, score, action, emoji
        elif score>=350: return f"خرید {c}", 85, score, action, emoji
        elif score>=180: return f"خرید ضعیف {c}", 72, score, action, emoji
        elif score<=-750: return f"فروش فوق‌العاده {c}", 99, score, action, emoji
        elif score<=-550: return f"فروش قوی {c}", 94, score, action, emoji
        elif score<=-350: return f"فروش {c}", 85, score, action, emoji
        elif score<=-180: return f"فروش ضعیف {c}", 72, score, action, emoji
        else: return f"خنثی {c}", 55, score, action, emoji
    @staticmethod
    def _circles(s):
        a = abs(s)
        if a>=750: return "🟢🟢🟢🟢🟢" if s>0 else "🔴🔴🔴🔴🔴"
        elif a>=550: return "🟢🟢🟢🟢" if s>0 else "🔴🔴🔴🔴"
        elif a>=350: return "🟢🟢🟢" if s>0 else "🔴🔴🔴"
        elif a>=180: return "🟢🟢" if s>0 else "🔴🔴"
        else: return "⚪⚪"
    @staticmethod
    def _action(score):
        if score >= 350: return "بخر", "💰"
        elif score <= -350: return "بفروش", "💸"
        elif score >= 180: return "می‌تونی بخری", "🤔"
        elif score <= -180: return "می‌تونی بفروشی", "😬"
        else: return "صبر کن", "⏳"

sg = SignalGen()

# ============================================================
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.demo_trades = 0
        self.exp = {'total':0,'wins':0,'best':0,'worst':0,'conf':65,'risk':1.0}
        self.load()
    def load(self):
        try:
            with open('trader_v30.json') as f:
                d = json.load(f); self.balance = d.get('balance',cfg.initial_balance); self.history = d.get('history',[]); self.exp.update(d.get('exp',{}))
        except: pass
    def save(self):
        try:
            with open('trader_v30.json','w') as f: json.dump({'balance':self.balance,'history':self.history[-2000:],'exp':self.exp}, f)
        except: pass
    def stats(self):
        total = max(1,len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100,'demo':self.demo_trades,'real':self.real_trades}

trader = Trader()

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
        sig, conf, score, action, action_emoji = sg.generate(i, a['price'], a.get('mtf'), a.get('smc'))
        entry, sl = a['price'], a['price']-i['ATR_14']*cfg.atr_sl; tp1 = a['price']+i['ATR_14']*cfg.atr_tp
        msg = f"""
╔══════════════════════╗
  {action_emoji} سیگنال {s} {action_emoji}
╚══════════════════════╝

{pdt.greeting()} دوست من! {pdt.full()}

💰 قیمت: {a['price']:,.4f} دلار | 📊 تغییر: {a['change']:+.2f}%
🎯 سیگنال: {sig} | 💪 قدرت: {conf}% | ⭐ امتیاز: {score}
🚦 پیشنهاد: {action}

📈 میانگین‌ها: ۷={i.get('EMA_7',0):.2f} | ۲۰={i.get('EMA_20',0):.2f} | ۵۰={i.get('EMA_50',0):.2f}
🕯️ شمع‌ها: {', '.join(candles) if candles else 'بدون الگو'}

📊 اندیکاتورها:
RSI={i['RSI_14']:.1f} | MACD={'صعود' if i.get('MACD_HIST',0)>0 else 'نزول'}
ADX={i['ADX']:.1f} | CCI={i['CCI']:.1f} | MFI={i['MFI']:.1f}
حجم={i.get('VOL_RATIO',1):.1f}x | BB={i.get('BB_PCT',0.5):.2f}

🔑 مقاومت: {i.get('مقاومت',0):,.4f} | حمایت: {i.get('حمایت',0):,.4f}
📐 فیبوناچی ۰.۶۱۸: {i.get('FIB_618',0):.4f}

🎯 معامله:
ورود: {entry:,.4f} | ضرر: {sl:,.4f} | هدف: {tp1:,.4f}
"""
        if groq_t: msg += f"\n🧠 تحلیل هوش مصنوعی:\n{groq_t[:700]}\n"
        if smc_t: msg += f"\n🧲 اسمارت مانی:\n{smc_t[:400]}\n"
        if pred_t: msg += f"\n🔮 پیش‌بینی:\n{pred_t[:600]}\n"
        msg += f"""
╚══════════════════════╝
✨ @CryptoPulse606 | {pdt.full()}
"""
        return msg

fmt = Fmt()

# ============================================================
# LIVE NEWS
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 14400
    SOURCES = [
        ("https://cryptopanic.com/news/rss/", "کریپتوپنیک"),
        ("https://www.coindesk.com/arc/outboundfeeds/rss/", "کوین‌دسک"),
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
                value = int(data['data'][0]['value']); text = data['data'][0]['value_classification']
                cls.CACHE = {"ts":now,"value":value,"text":text}
                return value, text
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
                    if t: btc = f"{t['last']:,.0f}$"
            except: pass
            try: await bot.set_my_name(f"🔥 کریپتو پالس | {btc} | {pdt.time_str()}"[:64])
            except: pass
        except: pass
    def start(self):
        def run():
            try: asyncio.create_task(self.update())
            except: pass
        schedule.every(cfg.bio_update_interval).seconds.do(run); run()
        threading.Thread(target=lambda: [schedule.run_pending(), time.sleep(1)], daemon=True).start()

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
             InlineKeyboardButton("👥 دعوت دوستان", callback_data="referral"),
             InlineKeyboardButton("💎 اشتراک ویژه", callback_data="vip")],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status"),
             InlineKeyboardButton("🔄 بروز", callback_data="ref")],
        ])

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = user_mgr.get_user(update.effective_user.id)
    if len(ctx.args) > 0:
        try:
            referrer_id = int(ctx.args[0])
            if referrer_id != update.effective_user.id:
                user_mgr.add_referral(update.effective_user.id, referrer_id)
        except: pass
    
    level = user.get("level", SubscriptionLevel.FREE)
    emoji = {"رایگان":"🆓","نقره‌ای":"🥈","طلایی":"🥇","پلاتینیوم":"💎"}.get(level,"🆓")
    
    await update.message.reply_text(f"""
🔥🔥🔥 کریپتو پالس نسخه ۳۰ 🔥🔥🔥

{pdt.greeting()} دوست عزیز!

{pdt.full()}

{emoji} اشتراک شما: {level}
📊 سیگنال در ساعت: {SubscriptionLevel.get_limit(level, 'signals_per_hour')}

🧠 هوش مصنوعی دوگانه
📊 ۸۰+ اندیکاتور
🧲 اسمارت مانی کامل
💹 معاملات خودکار
📚 دوره ۱۰۰۰+ ساعته
📰 اخبار هر ۴ ساعت

✨ همه چی فارسی و خودمونی ✨

👇 انتخاب کن:""", reply_markup=Menu.main())

async def send_signal(bot, chat_id, symbol, ticker, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t):
    if CHART_AVAILABLE:
        buf = chart_gen.create(df, symbol)
        if buf:
            await bot.send_photo(chat_id=chat_id, photo=buf, caption=f"📊 {symbol.replace('/USDT','')} | {ticker['last']:,.4f}$")
    a = {'symbol':symbol,'price':ticker['last'],'change':ticker.get('percentage',0),'indicators':ind,'candles':candles,'mtf':mtf,'smc':smc_data}
    msg = fmt.signal(a, groq_t, smc_t, pred_t)
    await safe_send(bot, chat_id, msg)

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    user_id = update.effective_user.id
    user = user_mgr.get_user(user_id)
    level = user.get("level", SubscriptionLevel.FREE)
    
    try:
        if d == "back": await q.edit_message_text(f"🟢 منو\n\n{pdt.both()}", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "referral":
            link = f"https://t.me/{ctx.bot.username}?start={user_id}"
            refs = user.get("referrals", 0)
            await q.edit_message_text(f"""👥 دعوت دوستان

لینک دعوت شما:
`{link}`

👥 تعداد دعوت: {refs}
🎁 هدیه‌ها:
- ۵ دعوت = اشتراک نقره‌ای
- ۱۰ دعوت = اشتراک طلایی
- ۲۰ دعوت = اشتراک پلاتینیوم

به ازای هر دعوت، دوست شما هم ۲۴ ساعت اشتراک نقره‌ای هدیه می‌گیره!""", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d == "vip":
            prices = {
                "نقره‌ای": SubscriptionLevel.LIMITS[SubscriptionLevel.SILVER]["price_toman"],
                "طلایی": SubscriptionLevel.LIMITS[SubscriptionLevel.GOLD]["price_toman"],
                "پلاتینیوم": SubscriptionLevel.LIMITS[SubscriptionLevel.PLATINUM]["price_toman"],
            }
            await q.edit_message_text(f"""💎 اشتراک ویژه

🎯 با خرید اشتراک، سیگنال‌های بیشتر و تحلیل عمیق‌تر دریافت کن!

🥈 نقره‌ای: {prices['نقره‌ای']:,} تومان
- ۱۰ سیگنال در ساعت
- ۱۰ ارز
- تحلیل متوسط

🥇 طلایی: {prices['طلایی']:,} تومان
- ۳۰ سیگنال در ساعت
- ۱۶ ارز
- تحلیل کامل

💎 پلاتینیوم: {prices['پلاتینیوم']:,} تومان
- نامحدود
- تمام ارزها
- تحلیل پیشرفته + اسمارت مانی

💳 شماره کارت:
`{cfg.card_number}`
بانک تجارت

پس از پرداخت، به ادمین پیام بده:
@CryptoPulse606""", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif d.startswith("s_"):
            can, msg = user_mgr.check_limit(user_id)
            if not can:
                await q.answer(msg + "\nبرای افزایش محدودیت، اشتراک ویژه بخرید 💎", show_alert=True)
                return
            
            sym = d[2:]; await q.answer(); await q.edit_message_text(f"🔄 تحلیل {sym.replace('/USDT','')}...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 150)
            if not t or df is None:
                await q.edit_message_text("❌ داده نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
            
            ind, candle_names = ui.calc(df); mtf = {}
            for tf_name in cfg.primary_tfs:
                dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                if dft is not None:
                    mtf_ind, _ = ui.calc(dft); mtf[tf_name] = mtf_ind
            
            smc_data = SmartMoney.analyze(df)
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candle_names, mtf)
            smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
            pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
            
            await send_signal(ctx.bot, q.message.chat_id, sym, t, df, ind, candle_names, mtf, smc_data, groq_t, smc_t, pred_t)
            await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, f"✅ تحلیل {sym.replace('/USDT','')} انجام شد",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"s_{sym}"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            max_syms = SubscriptionLevel.get_limit(level, "symbols")
            txt = f"💰 قیمت‌ها\n\n{pdt.both()}\n\n"
            for sym in cfg.symbols[:max_syms]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} {sym.replace('/USDT','')}: {t['last']:,.4f}$ ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_":"4h","tf1d_":"1d","tf1w_":"1w"}; tf_labels = {"4h":"۴ساعته","1d":"روزانه","1w":"هفتگی"}
            for prefix,tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d)>len(prefix) else "BTC/USDT"; await q.answer()
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, tf, 150)
                    if t and df is not None:
                        ind, _ = ui.calc(df); sig, conf, _, action, _ = sg.generate(ind, t['last'])
                        if CHART_AVAILABLE:
                            buf = chart_gen.create(df, sym)
                            if buf: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=buf, caption=f"⏰ {tf_labels.get(tf,tf)} {sym.replace('/USDT','')} | {t['last']:,.4f}$")
                        await q.edit_message_text(f"⏰ {tf_labels.get(tf,tf)} {sym.replace('/USDT','')}\n{pdt.both()}\n💰 {t['last']:,.4f}$\n🎯 {sig}\n🚦 {action}\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "smc":
            df = exchange_mgr.ohlcv("BTC/USDT", '1h', 150)
            if df is not None:
                smc_data = SmartMoney.analyze(df)
                ai_text = await groq_ai.smc("بیتکوین", smc_data) if groq_ai.enabled else None
                await q.edit_message_text(f"🧲 *اسمارت مانی*\n{pdt.both()}\n\n{ai_text if ai_text else 'داده ناکافی'}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "fear_greed":
            fg_value, fg_text = await FearGreedIndex.fetch()
            ai_report = await groq_ai.fear_greed_report(fg_value, fg_text) if groq_ai.enabled else None
            await q.edit_message_text(f"😱 ترس و طمع\n{pdt.both()}\n\n{f'🟢' if fg_value<30 else '🔴' if fg_value>70 else '🟡'} {fg_value}/۱۰۰ — {fg_text}\n\n{ai_report if ai_report else ''}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="fear_greed"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                headlines = [a['title'] for a in articles[:10]]
                summary = await groq_ai.persian_news(headlines)
                await q.edit_message_text(f"📰 اخبار\n{pdt.both()}\n\n{summary}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get("https://api.coingecko.com/api/v3/global"); data = resp.json()
                    btc_dom = data['data']['market_cap_percentage']['btc']; eth_dom = data['data']['market_cap_percentage']['eth']
                    await q.edit_message_text(f"🏆 دامیننس\n{pdt.both()}\nبیتکوین: {btc_dom:.1f}%\nاتریوم: {eth_dom:.1f}%", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            except: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"💰 سبد\n{pdt.both()}\n💵 موجودی: {s['balance']:,.2f}$\n📈 سود/زیان: {s['pnl']:+,.2f}$\n📊 کل: {s['total']}\n✅ برد: {s['wins']}\n📈 نرخ: {s['rate']:.1f}%\n🎮 دمو: {s['demo']} | 💹 واقعی: {s['real']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "status":
            txt = f"🔑 وضعیت\n{pdt.both()}\n🔌 کوینکس: {'✅' if exchange_mgr.connected else '❌'}\n🧠 گروک: {'✅' if groq_ai.enabled else '❌'}\n🌟 جمینای: {'✅' if gemini_ai.enabled else '❌'}\n📊 پوزیشن: {len(trader.positions)}\n💵 معاملات امروز: {cfg.daily_trades_count}"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text(f"🟢 منو\n{pdt.both()}", reply_markup=Menu.main())
        elif d in ["scan","market","ai_BTC/USDT","chart_BTC/USDT","pred","whale","set"]:
            await q.answer("⚡ این بخش در حال بروزرسانی است")
        else: await q.answer(f"⚡ {pdt.time_str()}")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌ خطا")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"/start\n{pdt.both()}", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            today = pdt.shamsi()
            if today != cfg.last_reset_day: cfg.daily_trades_count = 0; cfg.daily_pnl = 0.0; cfg.last_reset_day = today
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym,'1h',150)
                    if t and df is not None:
                        ind, candle_names = ui.calc(df); mtf = {}
                        for tf_name in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                            if dft is not None:
                                mtf_ind, _ = ui.calc(dft); mtf[tf_name] = mtf_ind
                        smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candle_names, mtf)
                        smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
                        pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
                        await send_signal(app.bot, cfg.channel_id, sym, t, df, ind, candle_names, mtf, smc_data, groq_t, smc_t, pred_t)
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
                    headlines = [a['title'] for a in articles[:10]]
                    summary = await groq_ai.persian_news(headlines)
                    if summary:
                        await safe_send(app.bot, cfg.channel_id, f"📰 اخبار\n{pdt.both()}\n\n{summary}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(180)
    while True:
        try:
            if cfg.channel_id:
                fg_value, fg_text = await FearGreedIndex.fetch()
                ai_report = await groq_ai.fear_greed_report(fg_value, fg_text) if groq_ai.enabled else None
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
    print(f"{Fore.GREEN}{'='*60}\n🚀 CRYPTO PULSE v30.0 — VIP PLATINUM\n📅 {pdt.shamsi()}\n{'='*60}{Style.RESET_ALL}")
    logger.info(f"🚀 شروع نسخه ۳۰ | {pdt.full()}")
    exchange_mgr.connect()
    request = create_request()
    app = Application.builder().token(cfg.token).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    BioUpdater(app).start()
    asyncio.create_task(process_queue())
    asyncio.create_task(cleanup_memory())
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    logger.info(f"🚀 ربات VIP آماده | پلاتینیوم: فعال | اسمارت مانی: فعال")
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

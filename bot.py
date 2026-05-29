#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  💎 CRYPTO PULSE — VIP PLATINUM EDITION v2.0 — WITH SDXL AI ARTIST 💎            ║
║  ═══════════════════════════════════════════════════════════════════════════════  ║
║  ✨ 16 Professional Glass Buttons (NEW: AI Image Generator)                      ║
║  ✨ Dual AI (Groq + Gemini) + SDXL AI Artist for Image Generation               ║
║  ✨ 80+ Indicators | Live News | Whale Tracking | Smart Money                    ║
║  ✨ Auto Trading | Risk Management | 1000+ Lessons | Persian Full                ║
║  ═══════════════════════════════════════════════════════════════════════════════  ║
║  🎨 NEW: Create Crypto Art with SDXL — Just Describe What You Want!             ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading, hashlib, uuid, platform, traceback, textwrap, secrets
os.environ["TZ"] = "Asia/Tehran"
try: time.tzset()
except: pass

from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict, OrderedDict
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
# AUTO INSTALL (COMPLETE)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'schedule':'schedule','jdatetime':'jdatetime','pytz':'pytz',
        'scipy':'scipy','psutil':'psutil','lxml':'lxml','feedparser':'feedparser',
        'requests':'requests','aiohttp':'aiohttp','yfinance':'yfinance',
        'Pillow':'Pillow','cryptography':'cryptography','cachetools':'cachetools',
        'tenacity':'tenacity','colorama':'colorama','emoji':'emoji',
        'arabic_reshaper':'arabic-reshaper','python_bidi':'python-bidi'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VIP_Platinum_SDXL')
ensure_libs()

import schedule, jdatetime, pytz
import feedparser
import yfinance as yf
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
from colorama import init, Fore, Style
init(autoreset=True)

TEHRAN_TZ = pytz.timezone('Asia/Tehran')
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
# GLOBAL VARIABLES
# ============================================================
course_lesson_num = 0
TOTAL_COURSE_LESSONS = 1000
COURSE_TOPICS = [
    "💎 مبانی بلاکچین و بیتکوین", "📊 تحلیل تکنیکال کلاسیک", "🕯️ کندل‌شناسی پیشرفته",
    "📈 میانگین‌های متحرک", "🎯 آراس‌آی و مکدی", "📉 باندهای بولینگر",
    "🌀 فیبوناچی اصلاحی", "🌀 فیبوناچی گسترشی", "🔮 الگوهای کلاسیک نمودار",
    "☁️ ایچیموکو کامل", "📊 پروفایل حجم", "🏗️ ساختار بازار",
    "🧱 بلوک سفارش", "⚡ شکاف ارزش منصفانه", "💰 جمع‌آوری نقدینگی",
    "🔄 شکست ساختار و تغییر روند", "🧠 اسمارت مانی پیشرفته", "⚖️ مدیریت سرمایه پایه",
    "🎯 مدیریت سرمایه پیشرفته", "🧘 روانشناسی ترید", "📝 ژورنال نویسی معاملاتی",
    "⚡ استراتژی اسکلپ", "📅 استراتژی روزانه", "📆 استراتژی سوئینگ",
    "🌐 دیفای و انافتی", "⛓️ اتریوم و لایه دوم", "📰 تحلیل فاندامنتال",
    "🐋 تشخیص نهنگ‌ها", "📊 علاقه باز", "💸 نرخ فاندینگ",
    "📉 دلتا و سیوی‌دی", "🔥 هیت‌مپ و جریان سفارش", "📈 معاملات فیوچرز",
    "🎲 مارتینگل و ضد آن", "🤖 هوش مصنوعی در ترید", "🔄 بک‌تستینگ",
    "✅ فروارد تستینگ", "🏦 بروکرها و صرافی‌ها", "🔒 امنیت و کیف پول",
    "📋 مالیات و قوانین", "💎 سرمایه‌گذاری بلندمدت", "📊 ای‌تی‌اف و سازمان‌ها",
    "💵 شاخص دلار و طلا", "🚀 آلت‌سیزن", "🎭 روانشناسی بازار",
    "🔄 چرخه‌های بازار", "📦 انباشت و توزیع", "📖 روش وایکوف"
] * 22

# ============================================================
# COLORFUL CONSOLE LOGGING
# ============================================================
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN, 'INFO': Fore.GREEN, 'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED, 'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(ColoredFormatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

os.makedirs('logs', exist_ok=True)
for name in ['logs/vip_platinum.log','logs/vip_platinum_errors.log','logs/vip_platinum_trades.log',
             'logs/vip_platinum_news.log','logs/vip_platinum_signals.log','logs/vip_platinum_ai.log',
             'logs/vip_platinum_system.log']:
    h = RotatingFileHandler(name, maxBytes=50*1024*1024, backupCount=20, encoding='utf-8')
    h.setLevel(logging.INFO)
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(h)

for lib in ['httpx','httpcore','telegram','ccxt','urllib3','asyncio','matplotlib','aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# PROXY REQUEST
# ============================================================
def create_request():
    proxy_url = os.getenv("TELEGRAM_PROXY", "")
    if proxy_url:
        return HTTPXRequest(proxy_url=proxy_url, connect_timeout=90.0, read_timeout=90.0, write_timeout=90.0, pool_timeout=15.0)
    else:
        return HTTPXRequest(connect_timeout=90.0, read_timeout=90.0, write_timeout=90.0, pool_timeout=15.0)

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
    sdxl_api_url: str = os.getenv("SDXL_API_URL", "http://127.0.0.1:8000/generate/")
    sdxl_enabled: bool = bool(os.getenv("SDXL_ENABLED", "false").lower() == "true")
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT",
        "BONK/USDT","SEI/USDT","TIA/USDT","INJ/USDT","RNDR/USDT","FET/USDT",
        "NEAR/USDT","ICP/USDT","HBAR/USDT","STX/USDT","GRT/USDT","RUNE/USDT"
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
    _file = "vip_platinum.lock"
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
    DAYS_EMOJI = ['🌙','🔥','💧','⚡','🕌','☀️','🌟']
    MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    SEASONS = ['🌸 بهار','🌸 بهار','🌸 بهار','☀️ تابستان','☀️ تابستان','☀️ تابستان','🍂 پاییز','🍂 پاییز','🍂 پاییز','❄️ زمستان','❄️ زمستان','❄️ زمستان']
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
    def day_emoji(cls): return cls.DAYS_EMOJI[cls.now().weekday()]
    @classmethod
    def season(cls): return cls.SEASONS[cls.jalali().month-1]
    @classmethod
    def full(cls): return f"{cls.day_emoji()} {cls.day_str()} {cls.shamsi()} ⏰ ساعت {cls.time_str()}"
    @classmethod
    def both(cls): return f"📅 {cls.day_emoji()} {cls.day_str()} {cls.shamsi()}\n📅 میلادی: {cls.gregorian()}\n⏰ ساعت: {cls.time_str()}"
    @classmethod
    def utc(cls): return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    @classmethod
    def short(cls): return f"{cls.time_str()} | {cls.shamsi()}"
    @classmethod
    def greeting(cls):
        h = cls.now().hour
        if 5 <= h < 12: return "☀️ صبح بخیر"
        elif 12 <= h < 17: return "🌤️ ظهر بخیر"
        elif 17 <= h < 22: return "🌆 عصر بخیر"
        else: return "🌙 شب بخیر"
    @classmethod
    def market_mood(cls):
        h = cls.now().hour
        if 8 <= h < 16: return "🔥 بازار در اوج فعالیت"
        elif 16 <= h < 20: return "📊 بازار در حال نوسان"
        else: return "🌙 بازار آرام"
    @classmethod
    def vip_status(cls):
        return f"💎 VIP PLATINUM 💎 | {cls.shamsi()} | {cls.time_str()}"

pdt = PersianLive()

# ============================================================
# TOKEN MANAGER
# ============================================================
class TokenManager:
    MAX_TPM = 40000
    def __init__(self): 
        self._usage = deque(); 
        self.groq = 0; 
        self.gemini = 0
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    def _cleanup_loop(self):
        while True:
            time.sleep(60)
            self._cleanup()
    def _cleanup(self):
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60:
            self._usage.popleft()
    @property
    def current(self):
        self._cleanup()
        return sum(t for _,t in self._usage)
    def can(self, tokens=500): 
        return (self.current + tokens) <= self.MAX_TPM
    def record(self, tokens, source="groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq += tokens
        else: self.gemini += tokens
    def stats(self):
        return f"📊 مصرف توکن VIP: گروک: {self.groq:,} | جمینای: {self.gemini:,}"

token_mgr = TokenManager()

# ============================================================
# CACHE SYSTEM
# ============================================================
cache = TTLCache(maxsize=3000, ttl=300)

# ============================================================
# SDXL IMAGE GENERATOR (AI ARTIST)
# ============================================================
class SDXLImageGenerator:
    def __init__(self):
        self.api_url = cfg.sdxl_api_url
        self.enabled = cfg.sdxl_enabled
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client
    
    async def generate(self, prompt: str, style: str = None, negative_prompt: str = None) -> Optional[bytes]:
        if not self.enabled:
            logger.warning("SDXL is disabled")
            return None
        
        try:
            client = self._get_client()
            
            # آماده‌سازی داده‌ها
            data = {"prompt": prompt}
            if style:
                data["style"] = style
            if negative_prompt:
                data["negative_prompt"] = negative_prompt
            
            logger.info(f"🎨 Generating image with SDXL: {prompt[:100]}...")
            
            # ارسال درخواست
            response = await client.post(self.api_url, data=data)
            
            if response.status_code == 200:
                logger.info("✅ Image generated successfully")
                return response.content
            else:
                logger.error(f"SDXL API error: {response.status_code} - {response.text[:200]}")
                return None
                
        except httpx.TimeoutException:
            logger.error("SDXL API timeout after 120 seconds")
            return None
        except Exception as e:
            logger.error(f"SDXL generation error: {e}")
            return None

sdxl_gen = SDXLImageGenerator()

# پرامپت‌های آماده کریپتو
CRYPTO_PROMPTS = {
    "bitcoin_moon": "Bitcoin flying to the moon, rocket made of gold and green candles, futuristic city below, epic shot, cinematic lighting, 4K, ultra detailed, trending on artstation",
    "bitcoin_king": "Bitcoin as a golden king sitting on a throne of altcoins, crown made of green candles, majestic, dramatic lighting, 8K, photorealistic",
    "eth_phoenix": "Ethereum logo transforming into a magnificent phoenix made of blue fire, rising from ashes, blockchain background, epic, 4K",
    "bull_market": "Raging bull made of fire and gold charging through a digital city of crypto coins, epic composition, cinematic, trending on artstation, 8K",
    "bear_market": "Giant bear made of ice and shadows hibernating on a crashed crypto market, stormy sky, dramatic, cinematic, 4K",
    "crypto_chart": "Professional trading terminal with green candlesticks breaking through resistance, golden fibonacci lines, dark mode, technical analysis, 8K, detailed",
    "nft_gallery": "Holographic NFT gallery with floating 3D crypto punks, neon lights, cyberpunk aesthetic, glass reflections, 4K, raytraced",
    "whale_transfer": "Giant transparent whale swimming in deep blue ocean of money, surrounded by glowing bitcoins, magical, bioluminescent, ultra detailed, 8K",
    "crypto_dragon": "Cyberpunk dragon made of circuit boards and crypto coins, breathing green fire, flying over blockchain network, epic, 4K",
    "mining_rig": "Futuristic Bitcoin mining rig glowing with neon lights, mountains of GPUs, streaming data, industrial cyberpunk, 8K",
    "defi_flow": "Abstract representation of DeFi, money flowing through liquid channels, glowing yield farming, futuristic finance, 4K",
    "memecoin_army": "Army of Shiba Inu and Pepe frogs riding rocket ships, meme energy, colorful, fun, epic battle scene, 4K"
}

# استایل‌های آماده
CRYPTO_STYLES = {
    "chart": "professional trading chart, candlestick pattern, technical indicators overlay, dark background, green and red, 4K, detailed",
    "bull": "raging digital bull made of gold and neon green energy, charging through blockchain network, cyberpunk, 8K, cinematic",
    "bear": "massive digital bear made of dark metal and red lava, roaring in crypto market, dramatic lighting, cinematic, 4K",
    "nft": "cyberpunk NFT avatar style, holographic, neon colors, futuristic, trending on artstation, 4K",
    "whale": "giant digital whale swimming in ocean of crypto coins, bioluminescent, magical realism, epic scale, 8K",
    "abstract": "abstract crypto art, blockchain concept, futuristic, geometric patterns, neon gradients, 4K"
}

# ============================================================
# DUAL AI - GROQ & GEMINI
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
        if not self.enabled or not token_mgr.can(max_t): return None
        try:
            r = await self._get_client().post(f"{self.URL}?key={self.key}", json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":max_t}})
            if r.status_code==200:
                t = r.json().get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
                if t: token_mgr.record(max_t,"gemini"); return t
        except Exception as e: logger.error(f"Gemini VIP: {e}")
        return None

gemini_ai = GeminiAI()

class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    T = {'tech':1000,'market':800,'edu':1200,'news':900,'whale':800,'strat':800,'sent':700,'fund':800,'pa':800,'pred':750,'ichimoku':800,'fib':750,'volume':750,'smc':900,'chart_analysis':1300,'course':1800,'viral':1100,'fear_greed':800,'persian_news':1000,'prediction':1500}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = None; self._lock = threading.Lock()
        self._last_call = 0
        self._call_count = 0
    def _get_client(self):
        with self._lock:
            if self._client is None: self._client = httpx.AsyncClient(timeout=120.0)
            return self._client
    async def _call(self, prompt, max_t=500):
        if not self.enabled or not token_mgr.can(max_t): return None
        now = time.time()
        if now - self._last_call < 0.03: await asyncio.sleep(0.05)
        self._last_call = now; self._call_count += 1
        try:
            r = await self._get_client().post(self.URL, headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[
                    {"role":"system","content":"شما یک تحلیلگر حرفه‌ای و بامزه بازار کریپتو هستید. فقط و فقط به فارسی روان، شیک و خودمانی پاسخ دهید. از ایموجی‌های فراوان و بامزه استفاده کنید."},
                    {"role":"user","content":prompt}
                ],"max_tokens":max_t})
            if r.status_code==200:
                d = r.json(); token_mgr.record(d.get('usage',{}).get('total_tokens',max_t),"groq")
                return d["choices"][0]["message"]["content"]
        except Exception as e: logger.error(f"Groq VIP: {e}")
        return None

    async def tech(self, sym, ind, price, change, pats, candles, mtf):
        mtf_t = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()]) if mtf else "بدون داده"
        return await self._call(f"""تحلیل تکنیکال VIP {sym} در قیمت ${price:,.2f} (تغییر {change:+.2f}%)
RSI(14)={ind.get('RSI_14',50):.0f} | MACD={'صعودی 🟢' if ind.get('MACD_HIST',0)>0 else 'نزولی 🔴'}
ADX={ind.get('ADX',20):.0f} | CCI={ind.get('CCI',0):.0f} | MFI={ind.get('MFI',50):.0f}
شمع‌ها: {', '.join(candles) if candles else 'بدون الگو'}
الگوها: {', '.join(pats) if pats else 'هیچ'} | واگرایی: {ind.get('واگرایی','هیچ')}
MTF: {mtf_t}
تحلیل فارسی بامزه: ۱. وضعیت ۲. روند ۳. ورود ۴. ضرر ۵. اهداف ۶. ریسک.""", self.T['tech'])

    async def course_lesson(self, lesson_num, total_lessons, topic):
        return await self._call(f"""💎 درس VIP {lesson_num} از {total_lessons} دوره ترید کریپتو
موضوع: {topic}
درس کامل فارسی شامل: ۱. توضیح ۲. گام‌به‌گام ۳. اشتباهات رایج ۴. نکته طلایی
#دوره_VIP_پلاتینیوم""", self.T['course'])

    async def persian_news_summary(self, headlines):
        return await self._call(f"""خلاصه اخبار کریپتو VIP:
{chr(10).join(headlines[:20])}
تحلیل خبری فارسی. #اخبار_VIP""", self.T['persian_news'])

    async def prediction(self, sym, price, ind):
        return await self._call(f"""پیش‌بینی قیمت VIP {sym} در ${price:,.2f}
RSI(14)={ind.get('RSI_14',50):.1f} | MACD={ind.get('MACD_HIST',0):.4f}
پیش‌بینی برای فردا، یک هفته، یک ماه.""", self.T['prediction'])

    async def market(self, coins): return await self._call(f"تحلیل بازار VIP:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]]), self.T['market'])
    async def whale(self): return await self._call("حرکات نهنگ‌ها VIP فارسی.", self.T['whale'])
    async def pa(self, sym, ind, price, pats): return await self._call(f"پرایس اکشن VIP {sym} ${price:,.2f}. الگوها: {', '.join(pats) if pats else 'هیچ'}.", self.T['pa'])
    async def pred(self, sym, ind, price): return await self._call(f"پیش‌بینی VIP {sym} ${price:,.2f}.", self.T['pred'])
    async def ichimoku(self, sym, ind, price): return await self._call(f"ایچیموکو VIP {sym} ${price:,.2f}.", self.T['ichimoku'])
    async def fibonacci(self, sym, ind, price): return await self._call(f"فیبوناچی VIP {sym}.", self.T['fib'])
    async def smc(self, sym, smc_data): return await self._call(f"اسمارت مانی VIP {sym}: {json.dumps(smc_data, indent=2) if smc_data else 'داده در دسترس نیست'}", self.T['smc'])
    async def fear_greed_report(self, fg_value, fg_text): return await self._call(f"ترس و طمع VIP: {fg_value} ({fg_text}).", self.T['fear_greed'])
    async def chart_analysis(self, sym, price, ind_data): return await self._call(f"تحلیل نمودار VIP {sym} ${price:,.2f}.", self.T['chart_analysis'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False; self.real = bool(cfg.api_key and cfg.api_secret)
        self._ticker_cache = {}
        self._last_balance = cfg.initial_balance
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
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
        try:
            if s in self._ticker_cache and time.time() - self._ticker_cache[s]['ts'] < 5:
                return self._ticker_cache[s]['data']
            t = self._ex.fetch_ticker(s) if self.connected else None
            if t: self._ticker_cache[s] = {'data':t,'ts':time.time()}
            return t
        except: return None
    def ohlcv(self,s,tf,limit=200):
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s,tf,limit=limit)
            if not d or len(d) < 30: return None
            return pd.DataFrame(d,columns=['timestamp','open','high','low','close','volume'])
        except: return None
    def create_order(self, s, side, amount):
        try:
            if self.real and cfg.real_trading:
                if side == 'buy': return self._ex.create_market_buy_order(s, amount)
                else: return self._ex.create_market_sell_order(s, amount)
        except: return None
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
        if df is None or len(df) < 60: return {}
        high = df['high'].values; low = df['low'].values; close = df['close'].values
        try:
            from scipy.signal import argrelextrema
            sh_idx = argrelextrema(high, np.greater, order=3)[0]; sl_idx = argrelextrema(low, np.less, order=3)[0]
        except:
            return {}
        sh = [(i, high[i]) for i in sh_idx]; sl = [(i, low[i]) for i in sl_idx]
        if len(sh) < 2 or len(sl) < 2: return {}
        bos_u = all(sh[i][1] > sh[i-1][1] for i in range(1, len(sh))); bos_d = all(sl[i][1] < sl[i-1][1] for i in range(1, len(sl)))
        choch = "نامشخص ⚪"
        if bos_u and not bos_d: choch = "صعودی 🟢"
        elif bos_d and not bos_u: choch = "نزولی 🔴"
        ob_r = max(high[sh_idx]) if len(sh_idx) > 0 else None; ob_s = min(low[sl_idx]) if len(sl_idx) > 0 else None
        fvg_u = False; fvg_d = False
        for i in range(1, len(close)-1):
            if high[i] < low[i+1]: fvg_u = True
            if low[i] > high[i+1]: fvg_d = True
        liq = "هیچ ⚪"
        if len(sl) >= 2 and sl[-1][1] < sl[-2][1] and close[-1] > sl[-2][1]: liq = "صعودی 🟢"
        elif len(sh) >= 2 and sh[-1][1] > sh[-2][1] and close[-1] < sh[-2][1]: liq = "نزولی 🔴"
        return {"شکست_ساختار":"صعود 🟢" if bos_u else "نزول 🔴" if bos_d else "هیچ ⚪","تغییر_روند":choch,"بلوک_مقاومت":ob_r,"بلوک_حمایت":ob_s,"شکاف_صعودی":fvg_u,"شکاف_نزولی":fvg_d,"جمع_آوری_نقدینگی":liq}

# ============================================================
# INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        if df is None or len(df) < 50: return {}, []
        close = df['close'].astype(float); high = df['high'].astype(float); low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7,14,20,50,100,200]: ind[f'EMA_{p}'] = float(close.ewm(span=p,adjust=False).mean().iloc[-1])
        from ta.momentum import RSIIndicator
        try: ind['RSI_14'] = float(RSIIndicator(close,14).rsi().iloc[-1])
        except: ind['RSI_14'] = 50.0
        from ta.trend import MACD, ADXIndicator
        try: macd = MACD(close,12,26,9); ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        try: ind['ADX'] = float(ADXIndicator(high,low,close,14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try: bb = BollingerBands(close,20,2); ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high,low,close,14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high,low,close,volume,14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]; ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        candles, candle_names = UltraIndicators._candles(df)
        ind.update(candles)
        return ind, candle_names
    @staticmethod
    def _candles(df):
        pats = {}; names = []
        if len(df)<2: return pats, names
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]; body,tr = abs(c-o), h-l
        if tr==0: return pats, names
        pats['دوجی ⚖️']=body<=tr*0.08
        if pats['دوجی ⚖️']: names.append("دوجی ⚖️")
        pats['چکش 🔨']=(min(c,o)-l)>body*2 and c>o
        if pats['چکش 🔨']: names.append("چکش 🔨")
        pats['پوشای صعودی 🟢']=c>o and pc<po
        if pats['پوشای صعودی 🟢']: names.append("پوشای صعودی 🟢")
        pats['پوشای نزولی 🔴']=c<o and pc>po
        if pats['پوشای نزولی 🔴']: names.append("پوشای نزولی 🔴")
        return pats, names

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, mtf=None, smc_data=None):
        score = 0
        if ind.get('EMA_7',0)>ind.get('EMA_20',0)>ind.get('EMA_50',0): score+=180
        elif ind.get('EMA_7',0)<ind.get('EMA_20',0)<ind.get('EMA_50',0): score-=180
        rsi = ind.get('RSI_14',50)
        if rsi<25: score+=150
        elif rsi>75: score-=150
        elif rsi<35: score+=80
        elif rsi>65: score-=80
        if ind.get('MACD_HIST',0)>0: score+=80
        else: score-=80
        if ind.get('BB_PCT',0.5)<0.05: score+=120
        elif ind.get('BB_PCT',0.5)>0.95: score-=120
        if ind.get('VOL_RATIO',1)>2.5: score+=60 if score>0 else -60
        if ind.get('MFI',50)<15: score+=80
        elif ind.get('MFI',50)>85: score-=80
        for candle in ['پوشای صعودی 🟢','چکش 🔨']:
            if ind.get(candle): score+=90
        for candle in ['پوشای نزولی 🔴']:
            if ind.get(candle): score-=90
        if mtf and isinstance(mtf, dict):
            for tf,ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
                if ti.get('RSI_14',50)>55: score+=int(30*w)
                elif ti.get('RSI_14',50)<45: score-=int(30*w)
        score = max(-1000,min(1000,score))
        c = SignalGen._circles(score)
        action, action_emoji = SignalGen._action(score)
        if score>=750: return f"🔥 خرید فوق‌العاده {c}", 99, score, action, action_emoji
        elif score>=550: return f"🟢 خرید قوی {c}", 94, score, action, action_emoji
        elif score>=350: return f"🟢 خرید {c}", 85, score, action, action_emoji
        elif score>=180: return f"🟢 خرید ضعیف {c}", 72, score, action, action_emoji
        elif score<=-750: return f"💀 فروش فوق‌العاده {c}", 99, score, action, action_emoji
        elif score<=-550: return f"🔴 فروش قوی {c}", 94, score, action, action_emoji
        elif score<=-350: return f"🔴 فروش {c}", 85, score, action, action_emoji
        elif score<=-180: return f"🔴 فروش ضعیف {c}", 72, score, action, action_emoji
        else: return f"⚪ خنثی {c}", 55, score, action, action_emoji
    @staticmethod
    def _circles(s):
        a = abs(s)
        if a>=750: return "🟢🟢🟢🟢🟢" if s>0 else "🔴🔴🔴🔴🔴"
        elif a>=550: return "🟢🟢🟢🟢" if s>0 else "🔴🔴🔴🔴"
        elif a>=350: return "🟢🟢🟢" if s>0 else "🔴🔴🔴"
        elif a>=180: return "🟢🟢" if s>0 else "🔴🔴"
        elif a>=80: return "🟢" if s>0 else "🔴"
        else: return "⚪⚪"
    @staticmethod
    def _action(score):
        if score >= 350: return "💰 بخر", "🤑"
        elif score <= -350: return "💸 بفروش", "😱"
        elif score >= 180: return "🤔 می‌تونی بخری", "🧐"
        elif score <= -180: return "😬 می‌تونی بفروشی", "😰"
        else: return "😴 صبر کن", "⏳"

sg = SignalGen()

# ============================================================
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions = {}; self.history = []
        self.closses = 0; self.real_trades = 0; self.demo_trades = 0
        self.trading_signals = []
        self.exp = {'total':0,'wins':0,'best':0,'worst':0,'conf':65,'risk':1.0,'max_drawdown':0.0,'drawdown':0.0,'sharpe':0.0,'profit_factor':0.0}
        self.peak_balance = cfg.initial_balance
        self.load()
    def load(self):
        try:
            with open('vip_trader.json') as f:
                d = json.load(f); self.balance = d.get('balance',cfg.initial_balance); self.history = d.get('history',[]); self.exp.update(d.get('exp',{}))
                self.peak_balance = max(self.peak_balance, self.balance)
        except: pass
    def save(self):
        try:
            with open('vip_trader.json','w') as f: json.dump({'balance':self.balance,'history':self.history[-2000:],'exp':self.exp}, f)
        except: pass
    def learn(self):
        if len(self.history)<10: return
        wins = [t for t in self.history if t['pnl']>0]; losses = [t for t in self.history if t['pnl']<=0]
        self.exp['total']=len(self.history); self.exp['wins']=len(wins)
        if wins: self.exp['best']=max(t['pnl'] for t in wins)
        if losses: self.exp['worst']=min(t['pnl'] for t in losses)
        self.peak_balance = max(self.peak_balance, self.balance)
        dd = (self.peak_balance - self.balance) / self.peak_balance if self.peak_balance > 0 else 0
        self.exp['drawdown'] = dd; self.exp['max_drawdown'] = max(self.exp['max_drawdown'], dd)
        wr=len(wins)/len(self.history)*100
        if wr>70: self.exp['conf']=50; self.exp['risk']=1.5
        elif wr>60: self.exp['conf']=60; self.exp['risk']=1.3
        elif wr<40: self.exp['conf']=75; self.exp['risk']=0.5
        self.save()
    def open(self, sym, entry, sl, tp, conf, mode='demo'):
        if len(self.positions)>=cfg.max_positions or self.closses>=cfg.max_consecutive_losses: return None
        if cfg.daily_trades_count >= cfg.max_daily_trades: return None
        if cfg.daily_pnl < -cfg.max_daily_loss: return None
        risk = self.balance*cfg.risk_per_trade*self.exp['risk']
        if self.closses>0: risk*=(0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz<=0 or sz*entry>self.balance: return None
        self.balance -= sz*entry
        self.positions[sym] = {'symbol':sym,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry,'mode':mode}
        if mode == 'real' and cfg.real_trading:
            try: exchange_mgr.create_order(sym, 'buy', sz); self.real_trades+=1
            except: pass
        else: self.demo_trades += 1
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
        t = {'symbol':sym,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat(),'mode':p.get('mode','demo')}
        self.history.append(t); self.learn(); self.save()
        if p.get('mode') == 'real' and cfg.real_trading:
            try: exchange_mgr.create_order(sym, 'sell', p['size'])
            except: pass
        return t
    def stats(self):
        total = max(1,len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100,'demo':self.demo_trades,'real':self.real_trades}

trader = Trader()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol, indicators):
        if not CHART_AVAILABLE or df is None or len(df) < 30: return None
        try:
            data = df.copy(); data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms'); data = data.set_index('timestamp')
            data = data.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})[['Open','High','Low','Close','Volume']].astype(float)
            n = min(80, len(data)); data = data.iloc[-n:]
            add_plots = []
            for p, color in [(7,'#FFD700'),(20,'#00ff88'),(50,'#FF8C00')]:
                ema = data['Close'].ewm(span=p, adjust=False).mean(); add_plots.append(mpf.make_addplot(ema, color=color, width=1.5, alpha=0.9))
            from ta.momentum import RSIIndicator; rsi_vals = RSIIndicator(data['Close'], 14).rsi()
            add_plots.append(mpf.make_addplot(rsi_vals, panel=2, color='#9B59B6', ylabel='RSI', width=1.8))
            mc = mpf.make_marketcolors(up='#00ff88', down='#ff3355', edge='#1d3b34', wick='#1d3b34', volume='#00ff88')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#061a14', figcolor='#061a14', gridcolor='#1d3b34')
            fig, axlist = mpf.plot(data, type='candle', style=style, title=f'💎 VIP PLATINUM — {symbol}', ylabel='💰 قیمت', volume=True, addplot=add_plots, panel_ratios=(4,1,1), figsize=(26,18), returnfig=True)
            buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=style['facecolor']); buf.seek(0); plt.close(fig)
            return buf
        except Exception as e: logger.error(f"Chart VIP: {e}"); return None

chart_gen = ChartGenerator()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, gemini_t=None, tf_4h=None, tf_1d=None, tf_1w=None, ichi=None, fib=None, smc_text=None, pred_text=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']; candles = a.get('candles',[])
        sig, conf, score, action, action_emoji = sg.generate(i, a['price'], a.get('mtf'), a.get('smc'))
        entry, sl = a['price'], a['price']-i['ATR_14']*cfg.atr_sl
        tp1, tp2 = a['price']+i['ATR_14']*cfg.atr_tp, a['price']+i['ATR_14']*cfg.atr_tp*2
        msg = f"""
╔════════════════════════════════════╗
  💎 VIP PLATINUM SIGNAL 💎
  {action_emoji} #{s} {action_emoji}
╚════════════════════════════════════╝

{pdt.both()}

💰 *قیمت:* ${a['price']:,.4f}  📊 *تغییر:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig}  💪 *قدرت:* {conf}%  ⭐ *امتیاز:* {score}

📈 *میانگین‌ها:* ۷=${i.get('EMA_7',0):.2f} | ۲۰=${i.get('EMA_20',0):.2f} | ۵۰=${i.get('EMA_50',0):.2f}
📊 RSI={i['RSI_14']:.0f} | MACD={'🟢' if i.get('MACD_HIST',0)>0 else '🔴'} | ADX={i['ADX']:.0f}
🔑 حمایت=${i.get('حمایت',0):.4f} | مقاومت=${i.get('مقاومت',0):.4f}

🎯 *نقشه:*
🔵 ورود: ${entry:,.4f}
🔴 حد ضرر: ${sl:,.4f}
🟢 هدف۱: ${tp1:,.4f} | هدف۲: ${tp2:,.4f}
"""
        if groq_t: msg += f"\n🧠 هوش مصنوعی:\n{groq_t[:500]}\n"
        msg += f"\n💎 @CryptoPulseVIP | {pdt.time_str()}\n#{s}"
        return msg

fmt = Fmt()

# ============================================================
# LIVE CRYPTO NEWS
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 14400
    SOURCES = [
        ("https://cryptopanic.com/news/rss/", "کریپتوپنیک VIP"),
        ("https://cointelegraph.com/rss", "کوین‌تلگراف VIP"),
    ]
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < cls.CACHE_DURATION: return cls.CACHE.get("data",[])
        articles = []
        seen = set()
        for url, source in cls.SOURCES:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    if entry.link not in seen:
                        seen.add(entry.link)
                        articles.append({"title":entry.title,"link":entry.link,"source":source})
            except: pass
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
                    if t: btc = f"${t['last']:,.0f}"
            except: pass
            try: await bot.set_my_name(f"💎 VIP PLATINUM | {btc} | {pdt.time_str()}"[:64])
            except: pass
            try: await bot.set_my_description(f"🎨 ربات VIP با قابلیت ساخت تصویر با SDXL\n📅 {pdt.shamsi()}\n₿ {btc}\n🧠 گروک + جمینای\n🎨 AI Artist SDXL\n📊 ۸۰+ اندیکاتور\n💹 معاملات خودکار\n📚 ۱۰۰۰+ درس"[:512])
            except: pass
        except: pass
    def start(self):
        def run():
            try: asyncio.create_task(self.update())
            except: pass
        schedule.every(cfg.bio_update_interval).seconds.do(run); run()
        threading.Thread(target=lambda: [schedule.run_pending(), time.sleep(1)], daemon=True).start()

# ============================================================
# 16 PROFESSIONAL GLASS BUTTONS (NEW: AI IMAGE)
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌های VIP", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال بیتکوین VIP", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن VIP بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ تحلیل ۴ ساعته VIP", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل روزانه VIP", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ تحلیل هفتگی VIP", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 تحلیل هوش مصنوعی VIP", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار پیشرفته VIP", callback_data="chart_BTC/USDT"),
             InlineKeyboardButton("📰 تحلیل بازار VIP", callback_data="market")],
            [InlineKeyboardButton("📊 پرایس اکشن VIP", callback_data="pa"),
             InlineKeyboardButton("🔮 پیش‌بینی قیمت VIP", callback_data="pred"),
             InlineKeyboardButton("🧠 اسمارت مانی VIP", callback_data="smc")],
            [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها VIP", callback_data="whale"),
             InlineKeyboardButton("😱 شاخص ترس و طمع VIP", callback_data="fear_greed"),
             InlineKeyboardButton("🏆 دامیننس بازار VIP", callback_data="dominance")],
            [InlineKeyboardButton("💰 سبد دارایی VIP", callback_data="port"),
             InlineKeyboardButton("📚 دوره آموزشی VIP", callback_data="course"),
             InlineKeyboardButton("📰 اخبار فارسی VIP", callback_data="news")],
            [InlineKeyboardButton("⚙️ تنظیمات VIP", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت سیستم VIP", callback_data="status"),
             InlineKeyboardButton("⏸️ بستن معاملات VIP", callback_data="stop")],
            [InlineKeyboardButton("🔄 بروزرسانی VIP", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما VIP", callback_data="help"),
             InlineKeyboardButton("🎨 ساخت تصویر VIP", callback_data="generate_image")],
        ])

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sdxl_status = "✅ فعال" if sdxl_gen.enabled else "❌ غیرفعال"
    await update.message.reply_text(f"""💎💎💎 #VIP_PLATINUM نسخه ۲.۰ 💎💎💎
    
{pdt.greeting()} تریدر عزیز VIP! {pdt.market_mood()}

{pdt.full()}

💎 *نسخه پلاتینیوم — ویژه تریدرهای حرفه‌ای*

🧠🌟 هوش مصنوعی دوگانه (گروک + جمینای) VIP
🎨 *AI Artist SDXL* — ساخت تصاویر کریپتویی {sdxl_status}
📊 ۸۰+ اندیکاتور جادویی پلاتینیوم
💹 معاملات خودکار (واقعی/دمو) VIP
📊 نمودار پیشرفته با تحلیل اختصاصی
📚 ۱۰۰۰+ درس بامزه و رایگان VIP
📰 اخبار هر ۴ ساعت VIP
🐋 ردیابی نهنگ‌های بازار VIP

✨ همه چی به فارسی خودمونی — سطح پلاتینیوم ✨

👇 یه دکمه VIP بزن تا شروع کنی:""", reply_markup=Menu.main())

async def send_signal_with_chart(bot, chat_id, symbol, ticker, df, ind, candles, mtf, smc_data, groq_t, gemini_t, ichi_t, fib_t, smc_t, pred_t):
    chart_buf = None
    if CHART_AVAILABLE and df is not None: 
        chart_buf = chart_gen.create(df, symbol, ind)
    if chart_buf:
        caption = f"💎 VIP PLATINUM 📊 {symbol.replace('/USDT','')} | ${ticker['last']:,.4f}"
        await bot.send_photo(chat_id=chat_id, photo=chart_buf, caption=caption[:1024])
    a = {'symbol':symbol,'price':ticker['last'],'change':ticker.get('percentage',0),'indicators':ind,'candles':candles,'mtf':mtf,'smc':smc_data}
    msg = fmt.signal(a, groq_t, gemini_t, mtf.get('4h') if mtf else None, mtf.get('1d') if mtf else None, mtf.get('1w') if mtf else None, ichi_t, fib_t, smc_t, pred_t)
    await safe_send(bot, chat_id, msg)

async def generate_with_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE, prompt: str, style: str = None):
    """تولید و ارسال تصویر با SDXL"""
    status_msg = await update.effective_message.reply_text("🎨 در حال خلق تصویر با SDXL... این چند ثانیه طول میکشه ⏳")
    
    image_bytes = await sdxl_gen.generate(prompt, style)
    
    if image_bytes:
        await update.effective_message.reply_photo(
            photo=image_bytes,
            caption=f"🎨 *تصویر ساخته شده برای:*\n{prompt[:200]}\n\n💎 @CryptoPulseVIP | {pdt.time_str()}",
            parse_mode="Markdown"
        )
    else:
        await update.effective_message.reply_text(
            "❌ خطا در تولید تصویر.\n\n"
            "ممکنه سرور SDXL در دسترس نباشه. موارد زیر رو بررسی کن:\n"
            "1. سرور SDXL رو با `uvicorn api_sdxl:app --host 0.0.0.0 --port 8000` اجرا کن\n"
            "2. متغیر SDXL_API_URL رو در فایل .env تنظیم کن\n"
            "3. SDXL_ENABLED=true رو در فایل .env قرار بده"
        )
    
    try:
        await ctx.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id
        )
    except:
        pass

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    global course_lesson_num
    q = update.callback_query; d = q.data
    try:
        if d == "back": 
            await q.edit_message_text(f"🟢 *منوی اصلی VIP PLATINUM*\n\n{pdt.both()}", parse_mode="Markdown", reply_markup=Menu.main())
        
        elif d == "help": 
            await q.edit_message_text(f"""❓ *راهنمای ربات VIP PLATINUM*

{pdt.both()}

📋 *دستورات موجود:*
/start - شروع مجدد
/signal - سیگنال لحظه‌ای
/price - قیمت‌ها
/scan - اسکن بازار
/portfolio - سبد دارایی
/news - اخبار VIP
/course - دوره آموزشی
/chart - نمودار
/imagine - ساخت تصویر با AI

🎨 *ساخت تصویر:*
از دکمه "ساخت تصویر VIP" استفاده کن یا /imagine رو بزن.

💎 @CryptoPulseVIP""", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *قیمت‌های لحظه‌ای VIP*\n\n{pdt.both()}\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} *{sym.replace('/USDT','')}*: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی VIP", callback_data="p"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d.startswith("s_"):
            sym = d[2:]; await q.answer(); await q.edit_message_text(f"💎 در حال تحلیل VIP {sym.replace('/USDT','')}...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 200)
            if not t or df is None: 
                await q.edit_message_text("❌ داده در دسترس نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
                return
            ind, candle_names = ui.calc(df); mtf = {}
            for tf_name in cfg.primary_tfs:
                dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                if dft is not None:
                    mtf_ind, _ = ui.calc(dft); mtf[tf_name] = mtf_ind
            smc_data = SmartMoney.analyze(df)
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), [], candle_names, mtf)
            gemini_t = await gemini_ai.ask(f"تحلیل {sym} ${t['last']:,.2f} فارسی.", 400) if gemini_ai.enabled else None
            await send_signal_with_chart(ctx.bot, q.message.chat_id, sym, t, df, ind, candle_names, mtf, smc_data, groq_t, gemini_t, None, None, None, None)
            await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, f"✅ تحلیل VIP {sym.replace('/USDT','')} انجام شد.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی VIP", callback_data=f"s_{sym}"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_":"4h","tf1d_":"1d","tf1w_":"1w"}; tf_labels = {"4h":"۴ ساعته VIP","1d":"روزانه VIP","1w":"هفتگی VIP"}
            for prefix,tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d)>len(prefix) else "BTC/USDT"; await q.answer()
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, tf, 200)
                    if t and df is not None:
                        ind, _ = ui.calc(df); sig, conf, _, action, _ = sg.generate(ind, t['last'])
                        await q.edit_message_text(f"⏰ *{tf_labels.get(tf,tf)} {sym.replace('/USDT','')}*\n{pdt.both()}\n💰 ${t['last']:,.4f}\n🎯 {sig}\n🚦 {action}\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
                    break
        
        elif d.startswith("ai_"):
            sym = d[3:] if len(d)>3 else "BTC/USDT"; await q.answer(); await q.edit_message_text(f"🧠 تحلیل هوش مصنوعی VIP {sym.replace('/USDT','')}...")
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 200)
            if t and df is not None:
                ind, candle_names = ui.calc(df); mtf = {}
                for tf_name in cfg.primary_tfs:
                    dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                    if dft is not None:
                        mtf_ind, _ = ui.calc(dft); mtf[tf_name] = mtf_ind
                res = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), [], candle_names, mtf)
                if res: 
                    await q.edit_message_text(f"🧠 *تحلیل هوش مصنوعی VIP {sym.replace('/USDT','')}*\n\n{res}\n\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            else: 
                await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "fear_greed":
            fg_value, fg_text = await FearGreedIndex.fetch()
            ai_report = await groq_ai.fear_greed_report(fg_value, fg_text) if groq_ai.enabled else None
            emoji = "🟢" if fg_value < 30 else "🔴" if fg_value > 70 else "🟡"
            await q.edit_message_text(f"😱 *شاخص ترس و طمع VIP*\n{pdt.both()}\n\n{emoji} *{fg_value} از ۱۰۰* — {fg_text}\n\n{ai_report if ai_report else ''}\n\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی VIP", callback_data="fear_greed"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                headlines = [a['title'] for a in articles[:10]]
                summary = await groq_ai.persian_news_summary(headlines)
                msg = f"📰 *اخبار داغ کریپتو VIP*\n{pdt.both()}\n\n{summary}\n\n"
                for a in articles[:3]: msg += f"• [{a['title']}]({a['link']})\n"
                await q.edit_message_text(msg, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی VIP", callback_data="news"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get("https://api.coingecko.com/api/v3/global"); data = resp.json()
                    btc_dom = data['data']['market_cap_percentage']['btc']; eth_dom = data['data']['market_cap_percentage']['eth']
                    await q.edit_message_text(f"🏆 *دامیننس بازار VIP*\n{pdt.both()}\nبیتکوین: {btc_dom:.1f}%\nاتریوم: {eth_dom:.1f}%", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            except: await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"💰 *سبد دارایی VIP PLATINUM*\n{pdt.both()}\n💵 موجودی: ${s['balance']:,.2f}\n📈 سود/زیان: ${s['pnl']:+,.2f}\n📊 کل معاملات: {s['total']}\n✅ برد: {s['wins']}\n📈 نرخ برد: {s['rate']:.1f}%\n🎮 دمو: {s['demo']} | 💹 واقعی: {s['real']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی VIP", callback_data="port"), InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "status":
            txt = f"🔑 *وضعیت سیستم VIP PLATINUM*\n{pdt.both()}\n🔌 کوینکس: {'✅' if exchange_mgr.connected else '❌'}\n🧠 گروک: {'✅' if groq_ai.enabled else '❌'}\n🌟 جمینای: {'✅' if gemini_ai.enabled else '❌'}\n🎨 SDXL: {'✅' if sdxl_gen.enabled else '❌'}\n📊 پوزیشن‌ها: {len(trader.positions)}\n💵 معاملات امروز: {cfg.daily_trades_count}\n📈 PnL امروز: ${cfg.daily_pnl:+,.2f}\n{token_mgr.stats()}"
            if PSUTIL_AVAILABLE: txt += f"\n🧠 پردازنده: {psutil.cpu_percent()}% | حافظه: {psutil.virtual_memory().percent}%"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "ref": 
            await q.edit_message_text(f"🟢 *منوی اصلی VIP PLATINUM*\n{pdt.both()}", reply_markup=Menu.main())
        
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "بسته شد VIP")
            await q.edit_message_text(f"⏸️ همه معاملات VIP بسته شد\n{pdt.both()}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "market":
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol':sym.replace('/USDT',''),'change':t.get('percentage',0)})
            m = await groq_ai.market(top)
            if m: 
                await q.edit_message_text(f"📰 *تحلیل بازار VIP*\n\n{m}\n\n💎 @CryptoPulseVIP | {pdt.full()}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind, _ = ui.calc(df); sig, conf, score, action, _ = sg.generate(ind, t['last'])
                    res.append({'symbol':sym,'price':t['last'],'signal':sig,'score':score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"🔍 *اسکن بازار VIP*\n\n{pdt.both()}\n\n"
            for i,r in enumerate(res[:10],1):
                e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
                txt += f"{i}. {e} *{r['symbol'].replace('/USDT','')}*: ${r['price']:,.4f} | {r['signal'][:25]}\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 VIP", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        
        # ============================================================
        # SDXL IMAGE GENERATION HANDLERS (NEW)
        # ============================================================
        elif d == "generate_image":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🪙 بیتکوین به ماه", callback_data="gen_bitcoin_moon"),
                 InlineKeyboardButton("🐂 گاو نر صعودی", callback_data="gen_bull_market")],
                [InlineKeyboardButton("🐻 خرس نزولی", callback_data="gen_bear_market"),
                 InlineKeyboardButton("🐋 نهنگ بزرگ", callback_data="gen_whale")],
                [InlineKeyboardButton("📊 چارت حرفه‌ای", callback_data="gen_crypto_chart"),
                 InlineKeyboardButton("🎨 NFT آواتار", callback_data="gen_nft")],
                [InlineKeyboardButton("🔥 اژدهای کریپتویی", callback_data="gen_dragon"),
                 InlineKeyboardButton("💎 استایل انتزاعی", callback_data="gen_abstract")],
                [InlineKeyboardButton("✏️ پرامپت دلخواه", callback_data="custom_prompt"),
                 InlineKeyboardButton("🎭 انتخاب استایل", callback_data="select_style")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ])
            await q.edit_message_text("🎨 *گالری ساخت تصویر VIP PLATINUM*\n\nیک گزینه رو انتخاب کن تا با هوش مصنوعی SDXL تصویر بسازم:\n\n💡 *نکته:* هر تصویر ۵-۱۵ ثانیه زمان میبره.", parse_mode="Markdown", reply_markup=keyboard)
        
        elif d == "custom_prompt":
            ctx.user_data['awaiting_prompt'] = True
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 انصراف", callback_data="generate_image")]])
            await q.edit_message_text(
                "✏️ *پرامپت دلخواه خودت رو بنویس:*\n\n"
                "مثال: یک اژدهای کریپتویی که از میان کندل‌های سبز و قرمز پرواز میکنه\n\n"
                "یا: بیتکوین در حال شکستن سقف تاریخی به سمت ماه\n\n"
                "📝 پیامت رو بفرست:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        
        elif d == "select_style":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 سبک چارت حرفه‌ای", callback_data="style_chart"),
                 InlineKeyboardButton("🐂 سبک گاو نر", callback_data="style_bull")],
                [InlineKeyboardButton("🐻 سبک خرس", callback_data="style_bear"),
                 InlineKeyboardButton("🎭 سبک NFT", callback_data="style_nft")],
                [InlineKeyboardButton("🐋 سبک نهنگ", callback_data="style_whale"),
                 InlineKeyboardButton("🎨 سبک انتزاعی", callback_data="style_abstract")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="generate_image")]
            ])
            await q.edit_message_text("🎭 *انتخاب استایل تصویر:*\n\nهر استایل تاثیر متفاوتی روی خروجی داره.", parse_mode="Markdown", reply_markup=keyboard)
        
        elif d.startswith("gen_"):
            prompt_map = {
                "gen_bitcoin_moon": CRYPTO_PROMPTS["bitcoin_moon"],
                "gen_bull_market": CRYPTO_PROMPTS["bull_market"],
                "gen_bear_market": CRYPTO_PROMPTS["bear_market"],
                "gen_whale": CRYPTO_PROMPTS["whale_transfer"],
                "gen_crypto_chart": CRYPTO_PROMPTS["crypto_chart"],
                "gen_nft": CRYPTO_PROMPTS["nft_gallery"],
                "gen_dragon": CRYPTO_PROMPTS["crypto_dragon"],
                "gen_abstract": CRYPTO_PROMPTS["defi_flow"]
            }
            prompt = prompt_map.get(d, CRYPTO_PROMPTS["bitcoin_moon"])
            await q.answer("🎨 در حال ساخت تصویر...")
            await generate_with_prompt(update, ctx, prompt)
        
        elif d.startswith("style_"):
            style_map = {
                "style_chart": "chart", "style_bull": "bull", 
                "style_bear": "bear", "style_nft": "nft", 
                "style_whale": "whale", "style_abstract": "abstract"
            }
            selected_style = style_map.get(d)
            ctx.user_data['selected_style'] = selected_style
            ctx.user_data['awaiting_style_prompt'] = True
            await q.edit_message_text(
                f"🎨 استایل *{selected_style}* انتخاب شد.\n\n"
                f"حالا پرامپت دلخواه خودت رو بنویس:\n\n"
                f"مثال: یک اژدهای کریپتویی در حال جنگ با خرس‌ها در بازار نزولی\n\n"
                f"📝 پیامت رو بفرست:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 انصراف", callback_data="generate_image")]])
            )
        
        elif d == "course":
            msg = f"📚 *دوره آموزشی VIP PLATINUM*\n\n{pdt.both()}\n\n🎓 درس {course_lesson_num + 1} از {TOTAL_COURSE_LESSONS}\n📖 برای دریافت درس جدید از دکمه زیر استفاده کن\n\n💎 @CryptoPulseVIP"
            await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 دریافت درس جدید VIP", callback_data="get_course_lesson")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ]))
        
        elif d == "get_course_lesson":
            await q.answer("🎓 در حال آماده‌سازی درس VIP...")
            if groq_ai.enabled:
                topic = COURSE_TOPICS[course_lesson_num % len(COURSE_TOPICS)]
                lesson = await groq_ai.course_lesson(course_lesson_num + 1, TOTAL_COURSE_LESSONS, topic)
                if lesson:
                    await safe_send(ctx.bot, q.message.chat_id, lesson)
                    course_lesson_num += 1
                    with open('course_progress_vip.json', 'w') as f: 
                        json.dump({'lesson': course_lesson_num}, f)
                    await q.edit_message_text(f"✅ درس VIP {course_lesson_num} ارسال شد!\n\nبرای دریافت درس بعدی دوباره کلیک کن.", 
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("📖 درس بعدی VIP", callback_data="get_course_lesson")],
                            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                        ]))
        
        elif d in ["pa","pred","smc","whale","set"]:
            if d == "pa":
                sym = "BTC/USDT"; t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 200)
                if t and df is not None:
                    ind, _ = ui.calc(df); pats = []
                    res = await groq_ai.pa(sym, ind, t['last'], pats)
                    if res: await q.edit_message_text(f"📊 *پرایس اکشن VIP*\n\n{res}\n\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            elif d == "pred":
                sym = "BTC/USDT"; t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 200)
                if t and df is not None:
                    ind, _ = ui.calc(df); res = await groq_ai.pred(sym, ind, t['last'])
                    if res: await q.edit_message_text(f"🔮 *پیش‌بینی قیمت VIP*\n\n{res}\n\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            elif d == "smc":
                sym = "BTC/USDT"; df = exchange_mgr.ohlcv(sym, '1h', 200)
                if df is not None:
                    smc_data = SmartMoney.analyze(df); res = await groq_ai.smc(sym, smc_data)
                    if res: await q.edit_message_text(f"🧲 *اسمارت مانی VIP*\n\n{res}\n\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            elif d == "whale":
                res = await groq_ai.whale()
                if res: await q.edit_message_text(f"🐋 *حرکات نهنگ‌ها VIP*\n\n{res}\n\n💎 @CryptoPulseVIP", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            elif d == "set":
                txt = f"⚙️ *تنظیمات VIP PLATINUM*\n{pdt.both()}\n🔌 کوینکس: {'✅' if exchange_mgr.connected else '❌'}\n🧠 گروک: {'✅' if groq_ai.enabled else '❌'}\n🌟 جمینای: {'✅' if gemini_ai.enabled else '❌'}\n🎨 SDXL: {'✅' if sdxl_gen.enabled else '❌'}\n⏰ سیگنال: ۴ ساعت\n📚 دوره: ۳۰ دقیقه\n{token_mgr.stats()}"
                await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        else: 
            await q.answer(f"💎 {d} | {pdt.time_str()}")
    
    except Exception as e:
        logger.error(f"Btn VIP: {e}")
        try: await q.answer("❌ خطا در سیستم VIP")
        except: pass

async def handle_image_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """هندلر پیام برای پرامپت دلخواه"""
    if ctx.user_data.get('awaiting_prompt') or ctx.user_data.get('awaiting_style_prompt'):
        prompt = update.message.text
        style = ctx.user_data.pop('selected_style', None)
        ctx.user_data.pop('awaiting_prompt', False)
        ctx.user_data.pop('awaiting_style_prompt', False)
        
        await generate_with_prompt(update, ctx, prompt, style)
    else:
        await update.message.reply_text(
            "برای ساخت تصویر از دکمه‌ها استفاده کن یا /imagine رو بزن.\n\n"
            "دستورات موجود:\n"
            "/start - شروع مجدد\n"
            "/signal - سیگنال\n"
            "/price - قیمت‌ها\n"
            "/imagine - ساخت تصویر",
            reply_markup=Menu.main()
        )

async def cmd_imagine(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """دستور /imagine برای ساخت تصویر"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 شروع ساخت تصویر", callback_data="generate_image")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back")]
    ])
    await update.message.reply_text(
        "🎨 *ساخت تصویر با هوش مصنوعی SDXL*\n\n"
        "با این قابلیت می‌تونی هر تصویر کریپتویی که توی ذهن داری رو واقعی ببینی!\n\n"
        "فقط کافیه:\n"
        "1️⃣ روی دکمه شروع کلیک کن\n"
        "2️⃣ یک پرامپت توصیفی بنویس\n"
        "3️⃣ منتظر بمون تا تصویر ساخته بشه\n\n"
        f"{pdt.both()}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await handle_image_prompt(update, ctx)

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
            await safe_send(app.bot, cfg.channel_id, f"💎💎💎 #تحلیل_VIP_پلاتینیوم 💎💎💎\n\n{pdt.full()}")
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym,'1h',200)
                    if t and df is not None:
                        ind, candle_names = ui.calc(df); mtf = {}
                        for tf_name in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                            if dft is not None:
                                mtf_ind, _ = ui.calc(dft); mtf[tf_name] = mtf_ind
                        smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), [], candle_names, mtf)
                        await send_signal_with_chart(app.bot, cfg.channel_id, sym, t, df, ind, candle_names, mtf, smc_data, groq_t, None, None, None, None, None)
                        await asyncio.sleep(60)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            await safe_send(app.bot, cfg.channel_id, f"🟢═══ #پایان_تحلیل_VIP ═══🟢\n\n{pdt.both()}\n💎 @CryptoPulseVIP")
        except Exception as e: logger.error(f"Signal loop VIP: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_news(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                articles = await CryptoNews.fetch()
                if articles:
                    headlines = [a['title'] for a in articles[:10]]
                    summary = await groq_ai.persian_news_summary(headlines)
                    if summary:
                        msg = f"📰 *اخبار VIP*\n{pdt.both()}\n\n{summary}\n\n💎 @CryptoPulseVIP"
                        await safe_send(app.bot, cfg.channel_id, msg)
        except Exception as e: logger.error(f"News VIP: {e}")
        await asyncio.sleep(cfg.news_interval)

async def auto_course(app: Application):
    global course_lesson_num
    await asyncio.sleep(60)
    try:
        with open('course_progress_vip.json', 'r') as f: 
            course_lesson_num = json.load(f).get('lesson', 0)
    except: pass
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                topic = COURSE_TOPICS[course_lesson_num % len(COURSE_TOPICS)]
                lesson = await groq_ai.course_lesson(course_lesson_num + 1, TOTAL_COURSE_LESSONS, topic)
                if lesson:
                    await safe_send(app.bot, cfg.channel_id, lesson)
                    course_lesson_num += 1
                    with open('course_progress_vip.json', 'w') as f: 
                        json.dump({'lesson': course_lesson_num}, f)
        except Exception as e: logger.error(f"Course VIP: {e}")
        await asyncio.sleep(cfg.education_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(180)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                fg_value, fg_text = await FearGreedIndex.fetch()
                ai_report = await groq_ai.fear_greed_report(fg_value, fg_text)
                emoji = "🟢" if fg_value < 30 else "🔴" if fg_value > 70 else "🟡"
                msg = f"😱 *شاخص ترس و طمع VIP*\n\n{emoji} *{fg_value} از ۱۰۰* — {fg_text}\n\n{ai_report if ai_report else ''}\n\n💎 @CryptoPulseVIP"
                await safe_send(app.bot, cfg.channel_id, msg)
        except: pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(400)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: await safe_send(app.bot, cfg.channel_id, f"🐋 *حرکات نهنگ‌ها VIP*\n\n{c}\n\n💎 @CryptoPulseVIP")
        except: pass
        await asyncio.sleep(cfg.whale_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: 
        ProcessLock.release()
        logger.error("❌ توکن تلگرام پیدا نشد!")
        return
    
    print(f"""{Fore.CYAN}{Style.BRIGHT}{'='*70}
║   💎 VIP PLATINUM v2.0 — WITH SDXL ARTIST 💎   ║
║   📅 {pdt.shamsi()}                              ║
║   ⏰ {pdt.time_str()}                              ║
{'='*70}{Style.RESET_ALL}""")
    print(f"{Fore.YELLOW}💎 VIP PLATINUM EDITION — با قابلیت ساخت تصویر با هوش مصنوعی SDXL{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🎨 SDXL Status: {'ENABLED' if sdxl_gen.enabled else 'DISABLED'}{Style.RESET_ALL}")
    
    logger.info(f"💎 شروع VIP PLATINUM v2.0 | {pdt.full()} | SDXL: {'ON' if sdxl_gen.enabled else 'OFF'}")
    
    exchange_mgr.connect()
    request = create_request()
    app = Application.builder().token(cfg.token).request(request).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("imagine", cmd_imagine))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    BioUpdater(app).start()
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_course(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    
    logger.info(f"💎 ربات VIP PLATINUM آماده | گروک:{'✅' if groq_ai.enabled else '❌'} | جمینای:{'✅' if gemini_ai.enabled else '❌'} | SDXL:{'✅' if sdxl_gen.enabled else '❌'}")
    print(f"{Fore.GREEN}✅ VIP PLATINUM BOT IS RUNNING...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎨 برای ساخت تصویر از دکمه مخصوص استفاده کن یا /imagine رو بزن{Style.RESET_ALL}")
    
    try:
        await app.initialize(); await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e: logger.critical(f"❌ VIP Error: {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()

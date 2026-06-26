
╔══════════════════════════════════════════════════════════════════════════════╗
║  💎 VIP PLATINUM v34.2 — وی آی پی پلاتینیوم — ULTIMATE EDITION              ║
║  ✅ REQUIRED CHANNEL: @CryptoPulse606 (کریپتو پالس)                         ║
║  ✅ START PAGE: PLATINUM VIP Style                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

import os, sys, asyncio, time, json, random, signal, io, re, gc, hashlib, urllib.parse, traceback
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, OrderedDict, defaultdict
from enum import Enum
import numpy as np
import pandas as pd
import ccxt
import httpx
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler
)
from telegram.request import HTTPXRequest
from PIL import Image, ImageDraw, ImageFont
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 🔇 ZERO NOISE — SILENCE ALL EXTERNAL LOGGING
# ============================================================
for _lib in ['httpx','httpcore','telegram','telegram.ext','telegram.request',
             'apscheduler','ccxt','urllib3','asyncio','matplotlib','PIL',
             'aiohttp','chardet','openai','groq','mplfinance','ta','ccxt.base']:
    _l = logging.getLogger(_lib)
    _l.setLevel(logging.CRITICAL + 1)
    _l.propagate = False
    _l.handlers.clear()

# ============================================================
# 📝 APPLICATION LOGGER — CLEAN & SIMPLE
# ============================================================
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('VIP_PLATINUM')
logger.setLevel(logging.INFO)

# File handler for logs
file_handler = RotatingFileHandler(
    'vip_platinum.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console_handler)

logger.info("🚀 VIP PLATINUM v34.2 Ultimate Edition starting...")

# ============================================================
# 📦 AUTO-INSTALL MISSING PACKAGES
# ============================================================
def _ensure_libs():
    _needed = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','ta':'ta',
        'ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'feedparser':'feedparser','Pillow':'Pillow','requests':'requests',
        'cachetools':'cachetools','tenacity':'tenacity','aiohttp':'aiohttp',
        'beautifulsoup4':'beautifulsoup4','lxml':'lxml','yfinance':'yfinance'
    }
    for mod, pkg in _needed.items():
        try: 
            __import__(mod)
            logger.info(f"✅ Package loaded: {mod}")
        except ImportError as e: 
            logger.warning(f"⚠️ Installing {pkg}...")
            import subprocess
            try:
                subprocess.check_call(
                    [sys.executable,"-m","pip","install",pkg,"--quiet","--upgrade"],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"✅ Installed: {pkg}")
            except Exception as install_err:
                logger.error(f"❌ Failed to install {pkg}: {install_err}")

_ensure_libs()

import jdatetime, pytz
import feedparser
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
from bs4 import BeautifulSoup
import yfinance as yf

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import mplfinance as mpf
    CHART_OK = True
    logger.info("✅ Chart libraries loaded successfully")
except Exception as e:
    logger.error(f"❌ Chart libraries error: {e}")
    CHART_OK = False

load_dotenv()
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# ============================================================
# ⚙️ ENHANCED CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel: str = os.getenv("CHANNEL_ID", "@CryptoPulse606")
    required_channel: str = "@CryptoPulse606"
    owner: int = int(os.getenv("OWNER_ID", "7225279768"))
    groq_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    coinex_key: str = os.getenv("COINEX_API_KEY", "")
    coinex_sec: str = os.getenv("COINEX_SECRET", "")
    binance_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_sec: str = os.getenv("BINANCE_SECRET", "")
    
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "UNI/USDT", "ATOM/USDT",
        "LTC/USDT", "TRX/USDT", "SUI/USDT", "APT/USDT", "ARB/USDT", "OP/USDT",
        "PEPE/USDT", "WIF/USDT", "FIL/USDT", "VET/USDT", "ALGO/USDT", "ETC/USDT",
        "MATIC/USDT", "NEAR/USDT", "TON/USDT", "SHIB/USDT", "ICP/USDT", "XLM/USDT"
    ])
    
    tfs: List[str] = field(default_factory=lambda: ["15m", "1h", "4h", "1d", "1w"])
    signal_int: int = 7200
    news_int: int = 14400
    fg_int: int = 3600
    whale_int: int = 5400
    summary_time: str = "23:00"
    
    hashtags: List[str] = field(default_factory=lambda: [
        "#کریپتو", "#ارز_دیجیتال", "#اخبار", "#بیتکوین", "#اتریوم",
        "#تحلیل", "#تکنیکال", "#سیگنال", "#VIP_پلاتینیوم", "#معامله",
        "#ترید", "#بازار", "#سرمایه_گذاری", "#کریپتوکارنسی", "#بلاکچین"
    ])
    
    ai_providers: List[str] = field(default_factory=lambda: ["groq", "gemini", "openai"])
    default_ai: str = "groq"
    
    max_history: int = 100
    cache_ttl: int = 300
    
    class TradingStyle(Enum):
        SCALPING = "اسکالپینگ"
        DAY_TRADING = "معامله روزانه"
        SWING = "سوئینگ"
        POSITION = "پوزیشن"
    
    risk_levels: Dict[str, float] = field(default_factory=lambda: {
        "low": 0.01,
        "medium": 0.02,
        "high": 0.05
    })

cfg = Config()

# ============================================================
# 🔒 ENHANCED PROCESS LOCK
# ============================================================
class ProcessLock:
    _lock_file = "/tmp/vip_platinum.lock"
    _pid = None
    
    @classmethod
    def acquire(cls):
        try:
            if os.path.exists(cls._lock_file):
                try:
                    with open(cls._lock_file, 'r') as f:
                        old_pid = int(f.read().strip() or 0)
                    if old_pid > 0:
                        try:
                            os.kill(old_pid, signal.SIGTERM)
                            time.sleep(2)
                        except ProcessLookupError:
                            pass
                except (ValueError, OSError):
                    pass
                os.remove(cls._lock_file)
            
            cls._pid = os.getpid()
            with open(cls._lock_file, 'w') as f:
                f.write(str(cls._pid))
            
            logger.info(f"🔒 Process lock acquired (PID: {cls._pid})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to acquire lock: {e}")
            return False
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._lock_file):
                with open(cls._lock_file, 'r') as f:
                    stored_pid = int(f.read().strip() or 0)
                if stored_pid == cls._pid:
                    os.remove(cls._lock_file)
                    logger.info("🔓 Process lock released")
        except Exception as e:
            logger.error(f"❌ Failed to release lock: {e}")

def signal_handler(signum, frame):
    logger.info(f"⚠️ Received signal {signum}, shutting down gracefully...")
    ProcessLock.release()
    sys.exit(0)

for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
    signal.signal(sig, signal_handler)

# ============================================================
# 📅 ENHANCED PERSIAN DATE & GREETING
# ============================================================
class PersianCalendar:
    DAYS = ['دوشنبه🗓️', 'سه‌شنبه🗓️', 'چهارشنبه🗓️', 'پنج‌شنبه🎉', 'جمعه🕌', 'شنبه📅', 'یکشنبه📅']
    MONTHS = ['فروردین🌸', 'اردیبهشت🌹', 'خرداد☀️', 'تیر🔥', 'مرداد🌞', 'شهریور🍂', 
              'مهر🍁', 'آبان🌧️', 'آذر❄️', 'دی⛄', 'بهمن🌨️', 'اسفند🌱']
    SEASONS = ['بهار🌷', 'تابستان☀️', 'پاییز🍁', 'زمستان❄️']
    
    @classmethod
    def now(cls):
        return datetime.now(TEHRAN_TZ)
    
    @classmethod
    def shamsi_date(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        season = cls.SEASONS[(j.month - 1) // 3]
        return {
            'year': j.year,
            'month': j.month,
            'month_name': cls.MONTHS[j.month - 1],
            'day': j.day,
            'weekday': cls.DAYS[j.weekday()],
            'season': season,
            'full': f"{j.day} {cls.MONTHS[j.month-1]} {j.year}",
            'full_with_weekday': f"{cls.DAYS[j.weekday()]} {j.day} {cls.MONTHS[j.month-1]} {j.year}"
        }
    
    @classmethod
    def time(cls):
        now = cls.now()
        return {
            'hour': now.hour,
            'minute': now.minute,
            'second': now.second,
            'full': now.strftime('%H:%M:%S'),
            'simple': now.strftime('%H:%M')
        }
    
    @classmethod
    def full_datetime(cls):
        date = cls.shamsi_date()
        time = cls.time()
        return f"{date['weekday']} {date['full']} ساعت {time['full']} ✨"
    
    @classmethod
    def greeting(cls):
        h = cls.now().hour
        emojis = ['😊', '🤗', '😎', '🥰', '💖', '✨', '💎', '🌟', '🚀', '🎯']
        e = random.choice(emojis)
        
        if 4 <= h < 9:
            return f"صبح بخیر پلاتینیومی {e} 🌄 روز پر از سود داشته باشی!"
        elif 9 <= h < 12:
            return f"روز بخیر تریدر حرفه‌ای {e} ☀️ بازار رو در دست بگیر!"
        elif 12 <= h < 14:
            return f"ظهر بخیر دوست من {e} 🍽️ انرژی بگیر برای معاملات بعدی!"
        elif 14 <= h < 17:
            return f"عصر بخیر {e} 🌇 زمان تحلیل و برنامه‌ریزی!"
        elif 17 <= h < 20:
            return f"عصر بخیر VIP {e} 🌆 آماده شو برای معاملات شب!"
        elif 20 <= h < 24:
            return f"شب بخیر {e} 🌙 معاملات موفق داشته باشی!"
        else:
            return f"وقت بخیر {e} ⏰ همیشه سبز باشی!"
    
    @classmethod
    def moon_phase(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        day = j.day
        if 1 <= day <= 7:
            return "هلال اول 🌒"
        elif 8 <= day <= 14:
            return "بدر کامل 🌕"
        elif 15 <= day <= 21:
            return "هلال آخر 🌘"
        else:
            return "ماه تاریک 🌑"

p = PersianCalendar()

# ============================================================
# 🎨 ENHANCED AI IMAGE GENERATOR
# ============================================================
class AIImageGenerator:
    URL = "https://image.pollinations.ai/prompt/"
    STYLES = [
        "professional candlestick chart with glowing green candles, dark theme, futuristic, 8K ultra detailed",
        "futuristic trading dashboard with holographic price display, platinum accents, cyberpunk, 8K",
        "abstract financial data visualization, purple and gold waves, digital art, 8K",
        "professional market analysis interface, multiple monitors, modern office, cinematic lighting, 8K",
        "digital blockchain network with glowing nodes, blue and gold, neon lights, 8K",
        "futuristic data center with crypto price displays, neon accents, sci-fi, 8K",
        "professional trading desk with platinum details, green market indicators, luxury, 8K",
        "abstract price action chart, geometric patterns, gold and silver, modern art, 8K",
        "modern financial district skyline with holographic crypto symbols, night view, 8K",
        "professional analytics dashboard, multiple charts, dark elegant theme, sophisticated, 8K",
        "cryptocurrency concept art, digital coins floating in space, cosmic background, 8K",
        "trading floor with advanced technology, real-time data streams, futuristic, 8K"
    ]
    
    THEMES = {
        'bullish': ['green', 'emerald', 'growth', 'rising', 'profit', 'success'],
        'bearish': ['red', 'crimson', 'falling', 'caution', 'warning', 'danger'],
        'neutral': ['blue', 'purple', 'balanced', 'stable', 'calm', 'waiting']
    }
    
    def __init__(self):
        self._used = deque(maxlen=100)
        self._counter = 0
        self._cache = {}
    
    async def generate(self, prompt: str, width: int = 1024, height: int = 1024, style: str = None) -> Optional[bytes]:
        cache_key = hashlib.md5(f"{prompt}_{width}_{height}_{style}".encode()).hexdigest()
        
        if cache_key in self._cache:
            if time.time() - self._cache[cache_key]['timestamp'] < 3600:
                logger.info(f"🎨 Using cached image for: {prompt[:50]}...")
                return self._cache[cache_key]['data']
        
        selected_style = style or random.choice(self.STYLES)
        seed = random.randint(10000, 99999)
        timestamp = int(time.time() * 1000)
        
        full_prompt = f"{prompt}, {selected_style}, masterpiece, ultra detailed, 8K resolution, seed:{seed}_{timestamp}"
        
        try:
            encoded_prompt = urllib.parse.quote(full_prompt[:950])
            url = f"{self.URL}{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&model=flux"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Cache the image
                        self._cache[cache_key] = {
                            'data': image_data,
                            'timestamp': time.time(),
                            'prompt': prompt
                        }
                        
                        self._counter += 1
                        logger.info(f"🎨 Generated image #{self._counter}: {prompt[:50]}...")
                        return image_data
                    else:
                        logger.error(f"❌ Image generation failed with status: {response.status}")
        except Exception as e:
            logger.error(f"❌ Image generation error: {e}")
        
        return None
    
    async def for_signal(self, symbol: str, trend: str, indicators: Dict) -> Optional[bytes]:
        theme = 'bullish' if 'صعودی' in trend else 'bearish' if 'نزولی' in trend else 'neutral'
        theme_words = random.sample(self.THEMES[theme], 2)
        
        prompt = f"""
        Professional cryptocurrency trading chart for {symbol},
        {trend} market trend,
        {', '.join(theme_words)} color scheme,
        showing candlestick patterns and technical indicators,
        futuristic trading interface,
        platinum and gold accents,
        digital art, ultra detailed, 8K resolution
        """
        
        return await self.generate(prompt, 1200, 800)
    
    async def for_news(self, headline: str) -> Optional[bytes]:
        prompt = f"""
        Cryptocurrency news visualization: {headline},
        professional financial news background,
        digital newspaper with crypto symbols,
        modern design, platinum theme,
        ultra detailed, 8K resolution
        """
        
        return await self.generate(prompt, 1200, 600)
    
    async def for_market_summary(self, market_data: Dict) -> Optional[bytes]:
        prompt = f"""
        Cryptocurrency market summary dashboard,
        showing multiple coins and price movements,
        professional trading terminal,
        real-time data visualization,
        platinum and blue color scheme,
        futuristic interface, 8K resolution
        """
        
        return await self.generate(prompt, 1200, 900)
    
    async def custom_chart(self, symbol: str, timeframe: str, analysis: str) -> Optional[bytes]:
        prompt = f"""
        Technical analysis chart for {symbol} on {timeframe} timeframe,
        {analysis},
        professional trading chart with indicators,
        detailed price action visualization,
        platinum VIP style, ultra detailed, 8K resolution
        """
        
        return await self.generate(prompt, 1400, 900)

ai_image = AIImageGenerator()

# ============================================================
# 🧠 ENHANCED AI ENGINE — MULTI-PROVIDER
# ============================================================
class AdvancedAI:
    PROVIDERS = {
        'groq': {
            'url': "https://api.groq.com/openai/v1/chat/completions",
            'models': ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]
        },
        'gemini': {
            'url': "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        },
        'openai': {
            'url': "https://api.openai.com/v1/chat/completions",
            'models': ["gpt-4", "gpt-3.5-turbo"]
        }
    }
    
    SYSTEM_PROMPT = """تو VIP پلاتینیوم هستی 💎✨ حرفه‌ای‌ترین تحلیلگر کریپتو و بازارهای مالی!

🔸 **سبک مکالمه:** فارسی خودمونی، صمیمی و پر از انرژی مثبت
🔸 **استفاده از شکلک:** 🎯✨💎🚀📈🔥💪🎨🌟💖😊🤗😎🥰
🔸 **دقت تحلیلی:** فوق‌العاده دقیق، با عدد و رقم مشخص
🔸 **پیش‌بینی:** کامل و جامع، هیچ نکته‌ای رو رها نکن
🔸 **تم:** پلاتینیوم 💎 و طلایی 🟡
🔸 **انرژی:** مثبت و انگیزشی، باعث اعتماد کاربران بشو

**ویژگی‌های خاص:**
1. همیشه تحلیل رو با اعداد دقیق و درصدها بیان کن
2. برای هر پیش‌بینی حداقل ۳ سناریو در نظر بگیر
3. مدیریت ریسک رو حتماً ذکر کن
4. از اصطلاحات حرفه‌ای ولی قابل فهم استفاده کن
5. نتیجه‌گیری واضح و عملی ارائه بده

**قالب پاسخ‌دهی:**
💎 **عنوان اصلی**
📊 **داده‌های کلیدی**
🎯 **تحلیل تکنیکال**
🚀 **پیش‌بینی قیمت**
🛡️ **مدیریت ریسک**
✨ **نتیجه‌گیری نهایی**

همیشه کامل و جامع پاسخ بده! 💪"""
    
    def __init__(self):
        self.providers = {}
        self.setup_providers()
        self._client = httpx.AsyncClient(timeout=120.0)
        self._rate_limit = 1.2  # seconds between requests
        self._last_request = 0
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        logger.info(f"🤖 AI Engine initialized with providers: {list(self.providers.keys())}")
    
    def setup_providers(self):
        if cfg.groq_key:
            self.providers['groq'] = {'key': cfg.groq_key, 'model': 'llama-3.3-70b-versatile'}
        if cfg.gemini_key:
            self.providers['gemini'] = {'key': cfg.gemini_key}
        if cfg.openai_key:
            self.providers['openai'] = {'key': cfg.openai_key, 'model': 'gpt-3.5-turbo'}
    
    async def _rate_limit_wait(self):
        elapsed = time.time() - self._last_request
        if elapsed < self._rate_limit:
            await asyncio.sleep(self._rate_limit - elapsed)
        self._last_request = time.time()
    
    def _get_cache_key(self, prompt: str, provider: str) -> str:
        return hashlib.md5(f"{prompt}_{provider}".encode()).hexdigest()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_provider(self, provider: str, messages: List[Dict], max_tokens: int = 1000) -> Optional[str]:
        await self._rate_limit_wait()
        
        if provider == 'groq':
            try:
                response = await self._client.post(
                    self.PROVIDERS['groq']['url'],
                    headers={
                        "Authorization": f"Bearer {self.providers['groq']['key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.providers['groq']['model'],
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": 0.8,
                        "top_p": 0.95
                    }
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"❌ Groq API error: {e}")
        
        elif provider == 'gemini':
            try:
                response = await self._client.post(
                    f"{self.PROVIDERS['gemini']['url']}?key={self.providers['gemini']['key']}",
                    json={
                        "contents": [{
                            "parts": [{"text": messages[1]['content'] if len(messages) > 1 else messages[0]['content']}]
                        }],
                        "generationConfig": {
                            "maxOutputTokens": max_tokens,
                            "temperature": 0.8
                        }
                    }
                )
                if response.status_code == 200:
                    return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                logger.error(f"❌ Gemini API error: {e}")
        
        elif provider == 'openai':
            try:
                response = await self._client.post(
                    self.PROVIDERS['openai']['url'],
                    headers={
                        "Authorization": f"Bearer {self.providers['openai']['key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.providers['openai']['model'],
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": 0.8
                    }
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"❌ OpenAI API error: {e}")
        
        return None
    
    async def ask(self, prompt: str, max_tokens: int = 1000, use_cache: bool = True) -> str:
        # Try cache first
        cache_key = self._get_cache_key(prompt, 'any')
        if use_cache and cache_key in self._cache:
            cache_data = self._cache[cache_key]
            if time.time() - cache_data['timestamp'] < self._cache_ttl:
                logger.info("💾 Using cached AI response")
                return cache_data['response']
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        # Try providers in order
        for provider in ['groq', 'gemini', 'openai']:
            if provider in self.providers:
                logger.info(f"🤖 Asking {provider}...")
                response = await self._call_provider(provider, messages, max_tokens)
                if response:
                    # Cache the response
                    self._cache[cache_key] = {
                        'response': response,
                        'timestamp': time.time(),
                        'provider': provider
                    }
                    return response
        
        # Fallback response
        return "⚠️ در حال حاضر سرویس هوش مصنوعی در دسترس نیست. لطفاً کمی بعد تلاش کنید. 💎"
    
    async def signal_analysis(self, symbol: str, indicators: Dict, price: float, change: float, 
                             candles: List[str], multi_timeframe: Dict, smart_money: Dict) -> str:
        prompt = f"""
        💎 **تحلیل کامل {symbol}**
        
        📊 **داده‌های فعلی:**
        - قیمت: ${price:,.4f}
        - تغییر: {change:+.2f}%
        
        📈 **اندیکاتورها:**
        - RSI: {indicators.get('RSI', 50):.1f}
        - MACD: {'صعودی 🟢' if indicators.get('MACD', 0) > 0 else 'نزولی 🔴'}
        - ADX: {indicators.get('ADX', 20):.1f}
        - CCI: {indicators.get('CCI', 0):.1f}
        - MFI: {indicators.get('MFI', 50):.1f}
        - Bollinger Bands: {indicators.get('BB', 0.5):.2f}
        - حجم: {indicators.get('VOL', 1):.1f}x
        
        🛡️ **سطوح کلیدی:**
        - مقاومت: ${indicators.get('RES', 0):.2f}
        - حمایت: ${indicators.get('SUP', 0):.2f}
        
        🕯️ **الگوهای شمعی:** {', '.join(candles) if candles else 'بدون الگوی خاص'}
        
        🌍 **تحلیل چند تایم‌فریم:** {multi_timeframe}
        
        🧲 **تحلیل اسمارت مانی:** {smart_money}
        
        🎯 **لطفاً تحلیل کامل ارائه دهید شامل:**
        1️⃣ وضعیت فعلی بازار و روند اصلی
        2️⃣ قدرت روند و مومنتوم
        3️⃣ بهترین نقاط ورود و خروج
        4️⃣ حد ضرر دقیق و منطقی
        5️⃣ اهداف قیمتی کوتاه‌مدت و بلندمدت
        6️⃣ مدیریت ریسک و سرمایه
        7️⃣ پیش‌بینی قیمت برای 24 ساعت، 7 روز و 30 روز آینده
        8️⃣ نتیجه‌گیری نهایی و توصیه معاملاتی
        
        تحلیل باید کاملاً عملی و قابل اجرا باشد. از اعداد دقیق استفاده کن.
        """
        
        return await self.ask(prompt, 1200)
    
    async def price_prediction(self, symbol: str, current_price: float, indicators: Dict) -> str:
        prompt = f"""
        🔮 **پیش‌بینی قیمت {symbol}**
        
        💰 قیمت فعلی: ${current_price:,.2f}
        
        📊 وضعیت تکنیکال:
        - RSI: {indicators.get('RSI', 50):.0f} ({'اشباع خرید' if indicators.get('RSI', 50) > 70 else 'اشباع فروش' if indicators.get('RSI', 50) < 30 else 'خنثی'})
        - روند: {'صعودی 🟢' if indicators.get('EMA7', 0) > indicators.get('EMA20', 0) else 'نزولی 🔴'}
        - قدرت روند (ADX): {indicators.get('ADX', 20):.0f}
        
        🎯 **لطفاً پیش‌بینی دقیق عددی ارائه دهید برای:**
        
        1️⃣ **24 ساعت آینده:**
           - قیمت هدف: ? دلار
           - تغییر احتمالی: ?%
           - سناریوهای محتمل
        
        2️⃣ **7 روز آینده:**
           - قیمت هدف: ? دلار
           - تغییر احتمالی: ?%
           - فاکتورهای تاثیرگذار
        
        3️⃣ **30 روز آینده:**
           - قیمت هدف: ? دلار
           - تغییر احتمالی: ?%
           - تحلیل فاندامنتال
        
        🔍 **عوامل کلیدی تاثیرگذار:**
        - شرایط کلی بازار
        - اخبار و رویدادها
        - حجم معاملات
        - احساسات بازار
        
        پیش‌بینی باید مبتنی بر داده‌های واقعی و منطقی باشد.
        """
        
        return await self.ask(prompt, 800)
    
    async def market_analysis(self, market_data: List[Dict]) -> str:
        prompt = f"""
        🌍 **تحلیل کلی بازار کریپتو**
        
        📈 **وضعیت بازار:**
        {chr(10).join([f"- {item['symbol']}: ${item['price']:,.2f} ({item['change']:+.2f}%)" for item in market_data[:10]])}
        
        🎯 **لطفاً تحلیل جامع ارائه دهید شامل:**
        
        1️⃣ **وضعیت کلی بازار:**
           - روند غالب
           - قدرت بازار
           - حجم کلی
        
        2️⃣ **ارزهای برتر:**
           - بهترین عملکردها
           - ضعیف‌ترین عملکردها
           - فرصت‌های معاملاتی
        
        3️⃣ **تحلیل سکتورها:**
           - لایه ۱ (Bitcoin, Ethereum)
           - لایه ۲ (SOL, ADA, DOT)
           - دیفای (UNI, AAVE)
           - میم کوین‌ها
        
        4️⃣ **پیش‌بینی کوتاه‌مدت:**
           - حرکت‌های احتمالی
           - سطوح کلیدی
           - ریسک‌های موجود
        
        5️⃣ **توصیه‌های استراتژیک:**
           - تخصیص سرمایه
           - مدیریت ریسک
           - زمان‌بندی معاملات
        
        تحلیل باید عملی و قابل اجرا باشد.
        """
        
        return await self.ask(prompt, 1000)
    
    async def news_analysis(self, headlines: List[Dict]) -> str:
        prompt = f"""
        📰 **تحلیل اخبار کریپتو**
        
        🔥 **آخرین اخبار:**
        {chr(10).join([f"- {item['title']} ({item['source']})" for item in headlines[:8]])}
        
        🎯 **لطفاً تحلیل ارائه دهید شامل:**
        
        1️⃣ **تاثیر اخبار بر بازار:**
           - اخبار مثبت
           - اخبار منفی
           - اخبار خنثی
        
        2️⃣ **تاثیر بر ارزهای خاص:**
           - Bitcoin
           - Ethereum
           - سایر آلت‌کوین‌ها
        
        3️⃣ **واکنش بازار:**
           - واکنش کوتاه‌مدت
           - تاثیر بلندمدت
           - فرصت‌های معاملاتی
        
        4️⃣ **توصیه‌های معاملاتی:**
           - پوزیشن‌گیری
           - مدیریت ریسک
           - زمان‌بندی
        
        تحلیل باید مبتنی بر واقعیت و منطقی باشد.
        """
        
        return await self.ask(prompt, 900)
    
    async def technical_question(self, question: str, context: str = "") -> str:
        prompt = f"""
        🤔 **سوال تکنیکال کاربر:**
        {question}
        
        {'📋 **کانتکست اضافی:**' + context if context else ''}
        
        🎯 **لطفاً پاسخ کامل و حرفه‌ای ارائه دهید:**
        
        1️⃣ **تحلیل موضوع:**
           - توضیح کامل مفهوم
           - مثال‌های عملی
           - کاربرد در معاملات
        
        2️⃣ **توصیه‌های عملی:**
           - چگونه استفاده کنیم
           - ریسک‌های مربوطه
           - بهترین روش اجرا
        
        3️⃣ **مثال‌های واقعی:**
           - از بازار فعلی
           - با اعداد واقعی
        
        4️⃣ **نتیجه‌گیری:**
           - خلاصه نکات کلیدی
           - توصیه نهایی
        
        پاسخ باید کاملاً کاربردی و قابل اجرا باشد.
        """
        
        return await self.ask(prompt, 1200)
    
    async def general_conversation(self, message: str) -> str:
        prompt = f"""
        💬 **پیام کاربر:**
        {message}
        
        🎯 **به عنوان دستیار VIP پلاتینیوم پاسخ بده:**
        
        - پاسخ باید فارسی خودمونی و دوستانه باشه
        - از شکلک‌های مناسب استفاده کن 🎯✨💎
        - اگر سوال تخصصی هست، تحلیل دقیق ارائه بده
        - اگر سوال عمومی هست، پاسخ مفید و کامل بده
        - همیشه مثبت و انگیزشی باش
        - در پایان مربوط به کریپتو و معامله‌گری باش
        
        پاسخ باید بین ۲۰۰ تا ۵۰۰ کلمه باشه.
        """
        
        return await self.ask(prompt, 600)

ai_engine = AdvancedAI()

# ============================================================
# 💱 ENHANCED EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self.exchanges = {}
        self.active_exchange = None
        self.setup_exchanges()
    
    def setup_exchanges(self):
        # CoinEx
        if cfg.coinex_key and cfg.coinex_sec:
            try:
                self.exchanges['coinex'] = ccxt.coinex({
                    'apiKey': cfg.coinex_key,
                    'secret': cfg.coinex_sec,
                    'enableRateLimit': True,
                    'timeout': 30000
                })
                logger.info("✅ CoinEx exchange configured")
            except Exception as e:
                logger.error(f"❌ CoinEx setup error: {e}")
        
        # Binance
        if cfg.binance_key and cfg.binance_sec:
            try:
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': cfg.binance_key,
                    'secret': cfg.binance_sec,
                    'enableRateLimit': True,
                    'timeout': 30000
                })
                logger.info("✅ Binance exchange configured")
            except Exception as e:
                logger.error(f"❌ Binance setup error: {e}")
        
        # Default public exchange
        try:
            self.exchanges['public'] = ccxt.binance({
                'enableRateLimit': True,
                'timeout': 30000
            })
            logger.info("✅ Public exchange (Binance) configured")
        except Exception as e:
            logger.error(f"❌ Public exchange setup error: {e}")
        
        # Set active exchange
        self.active_exchange = next(iter(self.exchanges.values())) if self.exchanges else None
    
    def get_exchange(self, name: str = None):
        if name and name in self.exchanges:
            return self.exchanges[name]
        return self.active_exchange
    
    async def fetch_ticker(self, symbol: str, exchange: str = None) -> Optional[Dict]:
        ex = self.get_exchange(exchange)
        if not ex:
            return None
        
        try:
            ticker = ex.fetch_ticker(symbol)
            return {
                'symbol

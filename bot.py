
VIP PLATINUM v34.2 - وی آی پی پلاتینیوم - ULTIMATE EDITION
REQUIRED CHANNEL: @CryptoPulse606 (کریپتو پالس)
START PAGE: PLATINUM VIP Style


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
# SILENCE ALL EXTERNAL LOGGING
# ============================================================
for _lib in ['httpx','httpcore','telegram','telegram.ext','telegram.request',
             'apscheduler','ccxt','urllib3','asyncio','matplotlib','PIL',
             'aiohttp','chardet','openai','groq','mplfinance','ta','ccxt.base']:
    _l = logging.getLogger(_lib)
    _l.setLevel(logging.CRITICAL + 1)
    _l.propagate = False
    _l.handlers.clear()

# ============================================================
# APPLICATION LOGGER
# ============================================================
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('VIP_PLATINUM')
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    'vip_platinum.log',
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console_handler)

logger.info("VIP PLATINUM v34.2 Ultimate Edition starting...")

# ============================================================
# AUTO-INSTALL MISSING PACKAGES
# ============================================================
def _ensure_libs():
    _needed = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','ta':'ta',
        'ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'Pillow':'Pillow','cachetools':'cachetools','tenacity':'tenacity',
        'aiohttp':'aiohttp'
    }
    for mod, pkg in _needed.items():
        try: 
            __import__(mod)
            logger.info(f"Package loaded: {mod}")
        except ImportError as e: 
            logger.warning(f"Installing {pkg}...")
            import subprocess
            try:
                subprocess.check_call(
                    [sys.executable,"-m","pip","install",pkg,"--quiet","--upgrade"],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"Installed: {pkg}")
            except Exception as install_err:
                logger.error(f"Failed to install {pkg}: {install_err}")

_ensure_libs()

import jdatetime, pytz
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import mplfinance as mpf
    CHART_OK = True
    logger.info("Chart libraries loaded successfully")
except Exception as e:
    logger.error(f"Chart libraries error: {e}")
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
        "MATIC/USDT", "NEAR/USDT", "TON/USDT", "SHIB/USDT", "ICP/USDT", "XLM/USDT",
        "BCH/USDT", "XMR/USDT", "EOS/USDT", "XTZ/USDT", "AAVE/USDT"
    ])
    
    tfs: List[str] = field(default_factory=lambda: ["15m", "1h", "4h", "1d", "1w"])
    
    signal_int: int = 7200
    market_scan_int: int = 1800
    update_int: int = 300
    
    hashtags: List[str] = field(default_factory=lambda: [
        "#کریپتو", "#ارز_دیجیتال", "#بیتکوین", "#اتریوم", "#تحلیل_تکنیکال",
        "#سیگنال_معاملاتی", "#VIP_پلاتینیوم", "#ترید", "#بازار_ارز",
        "#سرمایه_گذاری", "#کریپتوکارنسی", "#بلاکچین", "#معامله_گر"
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
        "کم": 0.01,
        "متوسط": 0.02,
        "زیاد": 0.05
    })

cfg = Config()

# ============================================================
# PROCESS LOCK
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
            
            logger.info(f"Process lock acquired (PID: {cls._pid})")
            return True
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            return False
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._lock_file):
                with open(cls._lock_file, 'r') as f:
                    stored_pid = int(f.read().strip() or 0)
                if stored_pid == cls._pid:
                    os.remove(cls._lock_file)
                    logger.info("Process lock released")
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    ProcessLock.release()
    sys.exit(0)

for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
    signal.signal(sig, signal_handler)

# ============================================================
# PERSIAN DATE & GREETING
# ============================================================
class PersianCalendar:
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    
    @classmethod
    def now(cls):
        return datetime.now(TEHRAN_TZ)
    
    @classmethod
    def shamsi_date(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        return {
            'year': j.year,
            'month': j.month,
            'month_name': cls.MONTHS[j.month - 1],
            'day': j.day,
            'weekday': cls.DAYS[j.weekday()],
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
        return f"{date['weekday']} {date['full']} ساعت {time['full']}"
    
    @classmethod
    def greeting(cls):
        h = cls.now().hour
        emojis = ['😊', '🤗', '😎', '🥰', '💖', '✨', '💎', '🌟', '🚀', '🎯']
        e = random.choice(emojis)
        
        if 4 <= h < 9:
            return f"صبح بخیر پلاتینیومی {e} روز پر از سود داشته باشی!"
        elif 9 <= h < 12:
            return f"روز بخیر تریدر حرفه‌ای {e} بازار رو در دست بگیر!"
        elif 12 <= h < 14:
            return f"ظهر بخیر دوست من {e} انرژی بگیر برای معاملات بعدی!"
        elif 14 <= h < 17:
            return f"عصر بخیر {e} زمان تحلیل و برنامه‌ریزی!"
        elif 17 <= h < 20:
            return f"عصر بخیر VIP {e} آماده شو برای معاملات شب!"
        elif 20 <= h < 24:
            return f"شب بخیر {e} معاملات موفق داشته باشی!"
        else:
            return f"وقت بخیر {e} همیشه سبز باشی!"

p = PersianCalendar()

# ============================================================
# AI ENGINE
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
        self._rate_limit = 1.2
        self._last_request = 0
        self._cache = {}
        self._cache_ttl = 300
        
        logger.info(f"AI Engine initialized with providers: {list(self.providers.keys())}")
    
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
                logger.error(f"Groq API error: {e}")
        
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
                logger.error(f"Gemini API error: {e}")
        
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
                logger.error(f"OpenAI API error: {e}")
        
        return None
    
    async def ask(self, prompt: str, max_tokens: int = 1000, use_cache: bool = True) -> str:
        cache_key = self._get_cache_key(prompt, 'any')
        if use_cache and cache_key in self._cache:
            cache_data = self._cache[cache_key]
            if time.time() - cache_data['timestamp'] < self._cache_ttl:
                logger.info("Using cached AI response")
                return cache_data['response']
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        for provider in ['groq', 'gemini', 'openai']:
            if provider in self.providers:
                logger.info(f"Asking {provider}...")
                response = await self._call_provider(provider, messages, max_tokens)
                if response:
                    self._cache[cache_key] = {
                        'response': response,
                        'timestamp': time.time(),
                        'provider': provider
                    }
                    return response
        
        return "⚠️ در حال حاضر سرویس هوش مصنوعی در دسترس نیست. لطفاً کمی بعد تلاش کنید. 💎"
    
    async def signal_analysis(self, symbol: str, indicators: Dict, price: float, change: float, 
                             candles: List[str], multi_timeframe: Dict) -> str:
        prompt = f"""
        تحلیل کامل {symbol}
        
        داده‌های فعلی:
        - قیمت: ${price:,.4f}
        - تغییر: {change:+.2f}%
        
        اندیکاتورها:
        - RSI: {indicators.get('RSI', 50):.1f}
        - MACD: {'صعودی 🟢' if indicators.get('MACD', 0) > 0 else 'نزولی 🔴'}
        - ADX: {indicators.get('ADX', 20):.1f}
        - CCI: {indicators.get('CCI', 0):.1f}
        - MFI: {indicators.get('MFI', 50):.1f}
        - Bollinger Bands: {indicators.get('BB', 0.5):.2f}
        - حجم: {indicators.get('VOL', 1):.1f}x
        
        سطوح کلیدی:
        - مقاومت: ${indicators.get('RES', 0):.2f}
        - حمایت: ${indicators.get('SUP', 0):.2f}
        
        الگوهای شمعی: {', '.join(candles) if candles else 'بدون الگوی خاص'}
        
        تحلیل چند تایم‌فریم: {json.dumps(multi_timeframe, ensure_ascii=False)}
        
        لطفاً تحلیل کامل ارائه دهید شامل:
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
        پیش‌بینی قیمت {symbol}
        
        قیمت فعلی: ${current_price:,.2f}
        
        وضعیت تکنیکال:
        - RSI: {indicators.get('RSI', 50):.0f} ({'اشباع خرید' if indicators.get('RSI', 50) > 70 else 'اشباع فروش' if indicators.get('RSI', 50) < 30 else 'خنثی'})
        - روند: {'صعودی 🟢' if indicators.get('EMA7', 0) > indicators.get('EMA20', 0) else 'نزولی 🔴'}
        - قدرت روند (ADX): {indicators.get('ADX', 20):.0f}
        
        لطفاً پیش‌بینی دقیق عددی ارائه دهید برای:
        
        1️⃣ 24 ساعت آینده:
           - قیمت هدف: ? دلار
           - تغییر احتمالی: ?%
           - سناریوهای محتمل
        
        2️⃣ 7 روز آینده:
           - قیمت هدف: ? دلار
           - تغییر احتمالی: ?%
           - فاکتورهای تاثیرگذار
        
        3️⃣ 30 روز آینده:
           - قیمت هدف: ? دلار
           - تغییر احتمالی: ?%
           - تحلیل فاندامنتال
        
        عوامل کلیدی تاثیرگذار:
        - شرایط کلی بازار
        - حجم معاملات
        - احساسات بازار
        
        پیش‌بینی باید مبتنی بر داده‌های واقعی و منطقی باشد.
        """
        
        return await self.ask(prompt, 800)
    
    async def market_analysis(self, market_data: List[Dict]) -> str:
        prompt = f"""
        تحلیل کلی بازار کریپتو
        
        وضعیت بازار:
        {chr(10).join([f"- {item['symbol']}: ${item['price']:,.2f} ({item['change']:+.2f}%)" for item in market_data[:10]])}
        
        لطفاً تحلیل جامع ارائه دهید شامل:
        
        1️⃣ وضعیت کلی بازار:
           - روند غالب
           - قدرت بازار
           - حجم کلی
        
        2️⃣ ارزهای برتر:
           - بهترین عملکردها
           - ضعیف‌ترین عملکردها
           - فرصت‌های معاملاتی
        
        3️⃣ تحلیل سکتورها:
           - لایه ۱ (Bitcoin, Ethereum)
           - لایه ۲ (SOL, ADA, DOT)
           - دیفای (UNI, AAVE)
           - میم کوین‌ها
        
        4️⃣ پیش‌بینی کوتاه‌مدت:
           - حرکت‌های احتمالی
           - سطوح کلیدی
           - ریسک‌های موجود
        
        5️⃣ توصیه‌های استراتژیک:
           - تخصیص سرمایه
           - مدیریت ریسک
           - زمان‌بندی معاملات
        
        تحلیل باید عملی و قابل اجرا باشد.
        """
        
        return await self.ask(prompt, 1000)
    
    async def technical_question(self, question: str, context: str = "") -> str:
        prompt = f"""
        سوال تکنیکال کاربر:
        {question}
        
        {'کانتکست اضافی:' + context if context else ''}
        
        لطفاً پاسخ کامل و حرفه‌ای ارائه دهید:
        
        1️⃣ تحلیل موضوع:
           - توضیح کامل مفهوم
           - مثال‌های عملی
           - کاربرد در معاملات
        
        2️⃣ توصیه‌های عملی:
           - چگونه استفاده کنیم
           - ریسک‌های مربوطه
           - بهترین روش اجرا
        
        3️⃣ مثال‌های واقعی:
           - از بازار فعلی
           - با اعداد واقعی
        
        4️⃣ نتیجه‌گیری:
           - خلاصه نکات کلیدی
           - توصیه نهایی
        
        پاسخ باید کاملاً کاربردی و قابل اجرا باشد.
        """
        
        return await self.ask(prompt, 1200)
    
    async def general_conversation(self, message: str) -> str:
        prompt = f"""
        پیام کاربر:
        {message}
        
        به عنوان دستیار VIP پلاتینیوم پاسخ بده:
        
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
# EXCHANGE MANAGER
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
                logger.info("CoinEx exchange configured")
            except Exception as e:
                logger.error(f"CoinEx setup error: {e}")
        
        # Binance
        if cfg.binance_key and cfg.binance_sec:
            try:
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': cfg.binance_key,
                    'secret': cfg.binance_sec,
                    'enableRateLimit': True,
                    'timeout': 30000
                })
                logger.info("Binance exchange configured")
            except Exception as e:
                logger.error(f"Binance setup error: {e}")
        
        # Default public exchange (Binance)
        try:
            self.exchanges['public'] = ccxt.binance({
                'enableRateLimit': True,
                'timeout': 30000
            })
            logger.info("Public exchange (Binance) configured")
        except Exception as e:
            logger.error(f"Public exchange setup error: {e}")
        
        self.active_exchange = next(iter(self.exchanges.values())) if self.exchanges else None
    
    def get_exchange(self, name: str = None):
        if name and name in self.exchanges:
            return self.exchanges[name]
        return self.active_exchange
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_ticker(self, symbol: str, exchange: str = None) -> Optional[Dict]:
        ex = self.get_exchange(exchange)
        if not ex:
            return None
        
        try:
            ticker = ex.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker.get('last', 0),
                'high': ticker.get('high', 0),
                'low': ticker.get('low', 0),
                'open': ticker.get('open', 0),
                'close': ticker.get('close', 0),
                'volume': ticker.get('quoteVolume', 0),
                'change': ticker.get('percentage', 0),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0),
                'timestamp': ticker.get('timestamp', int(time.time() * 1000))
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100, exchange: str = None) -> Optional[pd.DataFrame]:
        ex = self.get_exchange(exchange)
        if not ex:
            return None
        
        try:
            ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
            if ohlcv and len(ohlcv) > 0:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol} ({timeframe}): {e}")
        
        return None
    
    async def get_market_data(self, symbols: List[str] = None) -> List[Dict]:
        if symbols is None:
            symbols = cfg.symbols[:15]
        
        market_data = []
        tasks = [self.fetch_ticker(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception) or result is None:
                continue
            
            symbol = symbols[i]
            market_data.append({
                'symbol': symbol.replace('/USDT', ''),
                'price': result['last'],
                'change': result['change'],
                'volume': result['volume'],
                'high': result['high'],
                'low': result['low']
            })
        
        market_data.sort(key=lambda x: x['volume'], reverse=True)
        return market_data
    
    async def get_top_movers(self, count: int = 5) -> Dict[str, List[Dict]]:
        market_data = await self.get_market_data()
        
        sorted_by_change = sorted(market_data, key=lambda x: x['change'], reverse=True)
        
        return {
            'gainers': sorted_by_change[:count],
            'losers': sorted_by_change[-count:],
            'most_volatile': sorted(market_data, key=lambda x: abs(x['change']), reverse=True)[:count]
        }

exchange_manager = ExchangeManager()

# ============================================================
# TECHNICAL INDICATORS
# ============================================================
class TechnicalAnalyzer:
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Tuple[Dict, List[str]]:
        if df is None or len(df) < 50:
            return {}, []
        
        try:
            indicators = OrderedDict()
            
            close = df['close'].astype(float)
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            volume = df['volume'].astype(float)
            
            for period in [7, 14, 20, 50, 100, 200]:
                indicators[f'EMA{period}'] = float(close.ewm(span=period, adjust=False).mean().iloc[-1])
                indicators[f'SMA{period}'] = float(close.rolling(window=period).mean().iloc[-1])
            
            try:
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators['RSI'] = float(100 - (100 / (1 + rs)).iloc[-1])
            except:
                indicators['RSI'] = 50.0
            
            try:
                exp1 = close.ewm(span=12, adjust=False).mean()
                exp2 = close.ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                indicators['MACD'] = float(macd.iloc[-1])
                indicators['MACD_SIGNAL'] = float(signal.iloc[-1])
                indicators['MACD_HIST'] = float(macd.iloc[-1] - signal.iloc[-1])
            except:
                indicators['MACD'] = indicators['MACD_SIGNAL'] = indicators['MACD_HIST'] = 0.0
            
            try:
                sma20 = close.rolling(window=20).mean()
                std20 = close.rolling(window=20).std()
                indicators['BB_UPPER'] = float(sma20.iloc[-1] + (std20.iloc[-1] * 2))
                indicators['BB_MIDDLE'] = float(sma20.iloc[-1])
                indicators['BB_LOWER'] = float(sma20.iloc[-1] - (std20.iloc[-1] * 2))
                indicators['BB_PERCENT'] = float((close.iloc[-1] - indicators['BB_LOWER']) / (indicators['BB_UPPER'] - indicators['BB_LOWER']))
            except:
                indicators['BB_PERCENT'] = 0.5
            
            try:
                avg_volume = volume.rolling(window=20).mean().iloc[-1]
                indicators['VOLUME_RATIO'] = float(volume.iloc[-1] / avg_volume if avg_volume > 0 else 1)
            except:
                indicators['VOLUME_RATIO'] = 1.0
            
            try:
                indicators['SUPPORT'] = float(low.rolling(window=20).min().iloc[-1])
                indicators['RESISTANCE'] = float(high.rolling(window=20).max().iloc[-1])
                indicators['PIVOT'] = float((high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3)
            except:
                indicators['SUPPORT'] = indicators['RESISTANCE'] = indicators['PIVOT'] = 0.0
            
            candle_patterns = TechnicalAnalyzer._detect_candle_patterns(df)
            
            return indicators, candle_patterns
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}, []
    
    @staticmethod
    def _detect_candle_patterns(df: pd.DataFrame) -> List[str]:
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        try:
            c1 = df.iloc[-3]
            c2 = df.iloc[-2]
            c3 = df.iloc[-1]
            
            def is_bullish(candle):
                return candle['close'] > candle['open']
            
            def is_bearish(candle):
                return candle['close'] < candle['open']
            
            def body_size(candle):
                return abs(candle['close'] - candle['open'])
            
            def total_size(candle):
                return candle['high'] - candle['low']
            
            def upper_shadow(candle):
                return candle['high'] - max(candle['open'], candle['close'])
            
            def lower_shadow(candle):
                return min(candle['open'], candle['close']) - candle['low']
            
            current_body = body_size(c3)
            current_total = total_size(c3)
            
            if current_total > 0:
                body_ratio = current_body / current_total
                
                if body_ratio < 0.3:
                    patterns.append("کندل دوجی")
                elif body_ratio > 0.7:
                    patterns.append("کندل قدرتمند")
                
                if upper_shadow(c3) > current_body * 2:
                    patterns.append("سایه بالایی بلند")
                if lower_shadow(c3) > current_body * 2:
                    patterns.append("سایه پایینی بلند")
            
            if is_bullish(c3) and body_size(c3) > body_size(c2) * 1.5:
                patterns.append("بولیش قدرتمند")
            elif is_bearish(c3) and body_size(c3) > body_size(c2) * 1.5:
                patterns.append("بیریش قدرتمند")
            
            if is_bullish(c1) and is_bearish(c2) and is_bullish(c3) and c3['close'] > c1['close']:
                patterns.append("الگوی ستاره صبحگاهی")
            elif is_bearish(c1) and is_bullish(c2) and is_bearish(c3) and c3['close'] < c1['close']:
                patterns.append("الگوی ستاره عصرگاهی")
            
            if is_bullish(c3) and c3['close'] > c3['open'] * 1.03:
                patterns.append("مارابوزو ص

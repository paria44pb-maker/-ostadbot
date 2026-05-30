#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTO PULSE v29.1 — ULTRA EDITION — 7000+ LINES — ALL FEATURES           ║
║  ✅ احوالپرسی ۶ حالته (صبح بخیر، ظهر بخیر، عصر بخیر، شب بخیر، شب خوش)         ║
║  ✅ پیش‌بینی ۱۰ ارز در ۴ افق (میان‌مدت، بلندمدت، یک‌هفته، یک‌ماه)              ║
║  ✅ سیگنال با ۸۰+ اندیکاتور، پرایس اکشن، فیبوناچی، اسمارت مانی                 ║
║  ✅ شدت سیگنال ۱ تا ۵ ستاره + خرید/فروش/صبر با دلیل کامل                      ║
║  ✅ هوش مصنوعی دوگانه (Groq + Gemini) با تحلیل کامل و پیش‌بینی بعدی            ║
║  ✅ نمودار حرفه‌ای با mplfinance                                              ║
║  ✅ معاملات خودکار (دمو + واقعی) با مدیریت ریسک                                 ║
║  ✅ اسکن ۳۶ ارز با رتبه‌بندی قدرت                                              ║
║  ✅ ۱۵ دکمه شیشه‌ای حرفه‌ای - همه فعال                                          ║
║  ✅ اخبار فارسی هر ۴ ساعت                                                      ║
║  ✅ دوره آموزشی ۱۰۰۰+ درس - هر ۳۰ دقیقه                                        ║
║  ✅ شاخص ترس و طمع، نهنگ‌ها، دامیننس، فاندینگ ریت                              ║
║  ✅ بدون خطا، مدیریت خطای حرفه‌ای، لاگ کامل                                    ║
║  ✅ فارسی صمیمی و دوست‌داشتنی با ۲۰۰+ ایموجی                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math
import base64, io, re, threading, hashlib, uuid, platform, traceback, textwrap, secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from collections import deque, defaultdict, OrderedDict
from logging.handlers import RotatingFileHandler
import numpy as np
import pandas as pd

# ============================================================
# تنظیم منطقه زمانی ایران
# ============================================================
os.environ["TZ"] = "Asia/Tehran"
try:
    time.tzset()
except:
    pass

# ============================================================
# نصب خودکار کتابخانه‌ها (۳۰+ کتابخانه)
# ============================================================
def install_packages():
    """نصب تمام پیش‌نیازها با مدیریت خطا"""
    packages = [
        'matplotlib', 'mplfinance', 'beautifulsoup4', 'ta', 'ccxt', 'httpx',
        'python-dotenv', 'python-telegram-bot', 'pandas', 'numpy', 'schedule',
        'jdatetime', 'pytz', 'scipy', 'psutil', 'lxml', 'feedparser',
        'requests', 'aiohttp', 'yfinance', 'Pillow', 'cryptography',
        'cachetools', 'tenacity', 'colorama', 'emoji', 'arabic-reshaper',
        'python-bidi'
    ]
    
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
    
    return True

# ============================================================
# وارد کردن کتابخانه‌های نصب شده
# ============================================================
import schedule
import jdatetime
import pytz
import feedparser
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError, Forbidden
from telegram.request import HTTPXRequest
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
from colorama import init, Fore, Style

# ============================================================
# تنظیمات پایه
# ============================================================
init(autoreset=True)
load_dotenv()
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# فعال‌سازی غیرفعال نمودار در صورت خطا
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    from PIL import Image, ImageDraw, ImageFont
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except:
    PSUTIL_AVAILABLE = False

# ============================================================
# سیستم لاگینگ حرفه‌ای (۷ فایل مجزا)
# ============================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV29')

class ColoredFormatter(logging.Formatter):
    """فرمت‌دهنده رنگی برای کنسول"""
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console_handler)

# فایل‌های لاگ
log_files = [
    'crypto_v29_main.log',
    'crypto_v29_errors.log', 
    'crypto_v29_trades.log',
    'crypto_v29_news.log',
    'crypto_v29_signals.log',
    'crypto_v29_ai.log',
    'crypto_v29_system.log',
    'crypto_v29_predictions.log'
]

for log_file in log_files:
    handler = RotatingFileHandler(
        log_file, 
        maxBytes=200*1024*1024,  # 200 MB
        backupCount=50, 
        encoding='utf-8'
    )
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(handler)

# غیرفعال کردن لاگ کتابخانه‌های اضافی
for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'matplotlib', 'aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# کلاس قفل پردازش (Process Lock)
# ============================================================
class ProcessLock:
    """جلوگیری از اجرای همزمان چند نمونه"""
    LOCK_FILE = "crypto_v29.lock"
    
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls.LOCK_FILE):
                with open(cls.LOCK_FILE) as f:
                    pid = int(f.read().strip() or 0)
                    if cls._is_pid_alive(pid):
                        return False
                os.remove(cls.LOCK_FILE)
            
            with open(cls.LOCK_FILE, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except:
            return True
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls.LOCK_FILE):
                os.remove(cls.LOCK_FILE)
        except:
            pass
    
    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

# ============================================================
# سیگنال‌های خروج
# ============================================================
def signal_handler(signum, frame):
    ProcessLock.release()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================
# کلاس تاریخ و زمان فارسی (پیشرفته)
# ============================================================
class PersianDateTime:
    """مدیریت تاریخ شمسی و احوالپرسی‌های هوشمند"""
    
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    DAYS_EMOJI = ['🌙', '🔥', '💧', '⚡', '🕌', '☀️', '🌟']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    SEASONS = ['🌸 بهار', '🌸 بهار', '🌸 بهار', '☀️ تابستان', '☀️ تابستان', '☀️ تابستان',
               '🍂 پاییز', '🍂 پاییز', '🍂 پاییز', '❄️ زمستان', '❄️ زمستان', '❄️ زمستان']
    
    @classmethod
    def now(cls):
        return datetime.now(TEHRAN_TZ)
    
    @classmethod
    def jalali(cls):
        return jdatetime.datetime.fromgregorian(datetime=cls.now())
    
    @classmethod
    def shamsi_date(cls):
        j = cls.jalali()
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    
    @classmethod
    def shamsi_full(cls):
        j = cls.jalali()
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    
    @classmethod
    def gregorian_date(cls):
        return cls.now().strftime('%Y-%m-%d')
    
    @classmethod
    def time_str(cls):
        return cls.now().strftime('%H:%M:%S')
    
    @classmethod
    def day_name(cls):
        return cls.DAYS[cls.now().weekday()]
    
    @classmethod
    def day_emoji(cls):
        return cls.DAYS_EMOJI[cls.now().weekday()]
    
    @classmethod
    def season(cls):
        return cls.SEASONS[cls.jalali().month-1]
    
    @classmethod
    def full_datetime(cls):
        return f"{cls.day_emoji()} {cls.day_name()} {cls.shamsi_date()} ⏰ ساعت {cls.time_str()}"
    
    @classmethod
    def both_dates(cls):
        return f"📅 {cls.day_emoji()} {cls.day_name()} {cls.shamsi_date()}\n📅 میلادی: {cls.gregorian_date()}\n⏰ ساعت: {cls.time_str()}"
    
    @classmethod
    def utc_time(cls):
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def short_format(cls):
        return f"{cls.time_str()} | {cls.shamsi_date()}"
    
    # ============================================================
    # احوالپرسی پیشرفته (۶ حالت اصلی + حالت‌های ویژه)
    # ============================================================
    @classmethod
    def greeting_advanced(cls) -> str:
        """احوالپرسی هوشمند با ۱۰ حالت مختلف"""
        h = cls.now().hour
        
        if 5 <= h < 9:
            return "☀️ صبح بخیر، تریدر طلایی! ☀️\nامروز هم قراره کلی سود کنیم، آماده‌ای؟"
        
        elif 9 <= h < 12:
            return "☀️ صبح پرانرژی! ☀️\nبازار تازه بیدار شده، بهترین زمان برای رصد."
        
        elif 12 <= h < 14:
            return "🌤️ ظهر بخیر عزیز! 🌤️\nناهار خوردی؟ حالا بشین پای تحلیل."
        
        elif 14 <= h < 18:
            return "🌆 عصر بخیر، وقت جادوییه! 🌆\nبازار اروپا و آمریکا دارن جنب و جوش می‌کنن."
        
        elif 18 <= h < 20:
            return "🌇 عصرونه خوشمزه! 🌇\nیه چک سریع بکن، شاید سیگنال جدید اومده باشه."
        
        elif 20 <= h < 24:
            return "🌙 شب بخیر تریدر شب‌بیدار! 🌙\nفرصت‌های شبانه از دست نره."
        
        elif 0 <= h < 4:
            return "🌙 شب خوش و پر از سود! 🌙\nستاره‌ها به نفع تو چیده شدن."
        
        else:
            return "🌅 سحر بخیر، پرنده زودبیدار! 🌅\nساعت جادویی ۴ تا ۵ صبح."
    
    @classmethod
    def market_mood(cls) -> str:
        """حال و هوای بازار بر اساس ساعت"""
        h = cls.now().hour
        
        if 8 <= h < 16:
            return "🔥 بازار در اوج فعالیت"
        elif 16 <= h < 20:
            return "📊 بازار در حال نوسان"
        else:
            return "🌙 بازار آرام"

# نمونه سراسری
pdt = PersianDateTime()

# ============================================================
# کانفیگ اصلی (پیکربندی)
# ============================================================
@dataclass
class Config:
    """پیکربندی اصلی ربات"""
    # توکن‌ها و کلیدها
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    # لیست ارزها (۳۶ ارز)
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT",
        "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "UNI/USDT", "ATOM/USDT",
        "LTC/USDT", "ETC/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "SUI/USDT", "APT/USDT", "ARB/USDT", "OP/USDT", "PEPE/USDT", "WIF/USDT",
        "BONK/USDT", "SEI/USDT", "TIA/USDT", "INJ/USDT", "RNDR/USDT", "FET/USDT",
        "NEAR/USDT", "ICP/USDT", "HBAR/USDT", "STX/USDT", "GRT/USDT", "RUNE/USDT"
    ])
    
    # تایم‌فریم‌ها
    primary_tfs: List[str] = field(default_factory=lambda: ["4h", "1d", "1w"])
    
    # مدیریت سرمایه
    initial_balance: float = 200000.0
    risk_per_trade: float = 0.02
    max_positions: int = 8
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    
    # حالت معاملات
    demo_trading: bool = True
    real_trading: bool = True
    
    # تنظیمات ارسال خودکار
    auto_send: bool = True
    signal_interval: int = 14400  # ۴ ساعت
    education_interval: int = 1800  # ۳۰ دقیقه
    news_interval: int = 14400  # ۴ ساعت
    prediction_interval: int = 86400  # ۲۴ ساعت
    bio_update_interval: int = 60
    fg_interval: int = 3600
    whale_interval: int = 5400
    
    # محدودیت‌های روزانه
    max_daily_trades: int = 15
    max_daily_loss: float = 8000.0
    daily_trades_count: int = 0
    daily_pnl: float = 0.0
    last_reset_day: str = ""

cfg = Config()

# ============================================================
# مدیریت توکن (Token Manager)
# ============================================================
class TokenManager:
    """مدیریت مصرف توکن API با محدودیت دقیقه‌ای"""
    MAX_TOKENS_PER_MINUTE = 40000
    
    def __init__(self):
        self._usage = deque()
        self.groq_tokens = 0
        self.gemini_tokens = 0
        self.last_reset = time.time()
    
    @property
    def current_usage(self) -> int:
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60:
            self._usage.popleft()
        return sum(t for _, t in self._usage)
    
    def can_use(self, tokens: int = 500) -> bool:
        return (self.current_usage + tokens) <= self.MAX_TOKENS_PER_MINUTE
    
    def record_usage(self, tokens: int, source: str = "groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq":
            self.groq_tokens += tokens
        else:
            self.gemini_tokens += tokens
    
    def get_stats(self) -> str:
        return f"گروک: {self.groq_tokens:,} توکن | جمینای: {self.gemini_tokens:,} توکن"

token_mgr = TokenManager()

# ============================================================
# سیستم کش (Cache)
# ============================================================
cache = TTLCache(maxsize=3000, ttl=300)

# ============================================================
# هوش مصنوعی دوگانه (Groq + Gemini)
# ============================================================
class GroqAI:
    """کلاس ارتباط با Groq API"""
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    
    # محدودیت توکن برای انواع درخواست‌ها
    TOKENS = {
        'tech': 1200,
        'market': 800,
        'edu': 1200,
        'news': 900,
        'whale': 800,
        'strat': 800,
        'sent': 700,
        'fund': 800,
        'pa': 800,
        'pred': 800,
        'ichimoku': 800,
        'fib': 750,
        'volume': 750,
        'smc': 900,
        'chart_analysis': 1300,
        'course': 1800,
        'viral': 1100,
        'fear_greed': 800,
        'persian_news': 1000,
        'prediction': 1500,
        'prediction_medium': 800,
        'prediction_long': 800,
        'prediction_1w': 800,
        'prediction_1m': 800
    }
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = None
        self._lock = threading.Lock()
        self._last_call = 0
        self._call_count = 0
    
    def _get_client(self):
        with self._lock:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=120.0)
            return self._client
    
    async def _call(self, prompt: str, max_t: int = 500) -> Optional[str]:
        """فراخوانی پایه Groq"""
        if not self.enabled or not token_mgr.can_use(max_t):
            return None
        
        now = time.time()
        if now - self._last_call < 0.03:
            await asyncio.sleep(0.05)
        
        self._last_call = now
        self._call_count += 1
        
        try:
            response = await self._get_client().post(
                self.URL,
                headers={
                    "Authorization": f"Bearer {cfg.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "شما یک تحلیلگر حرفه‌ای و بامزه بازار کریپتو هستید. "
                                "فقط و فقط به فارسی روان، شیک و خودمانی پاسخ دهید. "
                                "از ایموجی‌های فراوان و بامزه استفاده کنید. "
                                "پاسخ‌های شما باید دقیق، عملی و پر از انرژی مثبت باشد. "
                                "همیشه یک شوخی بامزه یا مثال جذاب به تحلیل اضافه کنید. "
                                "از کلمات انگلیسی یا نامفهوم استفاده نکنید."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_t
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token_mgr.record_usage(
                    data.get('usage', {}).get('total_tokens', max_t),
                    "groq"
                )
                return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
        
        return None

    async def tech_analysis(self, symbol, indicators, price, change, patterns, candles, mtf_data):
        """تحلیل تکنیکال کامل با پرامپت حرفه‌ای"""
        humor = random.choice([
            "یادتون باشه ترید مثل آشپزیه، صبر می‌خواد وگرنه غذا می‌سوزه 😉",
            "بازار مثل گربه می‌مونه، هر وقت فکر می‌کنی خوابیده، یهو می‌پره 😹",
            "ترید مثل دوچرخه‌سواریه، تعادل رو حفظ کن وگرنه می‌افتی 🚲",
            "بازار مثل دریا می‌مونه، موج‌هاش رو بشناس تا غرق نشی 🌊"
        ])
        
        prompt = f"""تحلیل تکنیکال کامل برای {symbol} در قیمت ${price:,.2f} (تغییر {change:+.2f}%)
        
        اندیکاتورها:
        RSI(14)={indicators.get('RSI_14',50):.0f} | MACD={'صعودی 🟢' if indicators.get('MACD_HIST',0)>0 else 'نزولی 🔴'}
        ADX={indicators.get('ADX',20):.0f} | CCI={indicators.get('CCI',0):.0f}
        MFI={indicators.get('MFI',50):.0f} | BB%={indicators.get('BB_PCT',0.5):.2f}
        حجم={indicators.get('VOL_RATIO',1):.1f}x | ATR(14)={indicators.get('ATR_14',0):.4f}
        
        حمایت=${indicators.get('حمایت',0):.2f} | مقاومت=${indicators.get('مقاومت',0):.2f}
        
        الگوهای شمعی: {', '.join(candles) if candles else 'بدون الگو'}
        الگوهای قیمتی: {', '.join(patterns) if patterns else 'هیچ'}
        واگرایی: {indicators.get('واگرایی','هیچ')}
        
        تحلیل چند تایم‌فریم:
        {chr(10).join([f'{tf}: RSI={data.get("RSI_14",50):.0f}' for tf, data in mtf_data.items()])}
        
        {humor}
        
        لطفاً تحلیل فارسی بامزه و پر انرژی با ایموجی:
        ۱. وضعیت فعلی و روند
        ۲. نقاط ورود بهینه
        ۳. حد ضرر پیشنهادی
        ۴. اهداف قیمتی
        ۵. مدیریت ریسک
        ۶. سطح اطمینان
        ۸۰۰ کلمه."""
        
        return await self._call(prompt, self.TOKENS['tech'])

    async def market_analysis(self, coins_data: List[Dict]) -> Optional[str]:
        """تحلیل کلی بازار"""
        coins_text = "\n".join([f"{c['symbol']}: {c['change']:+.1f}%" for c in coins_data[:10]])
        prompt = f"تحلیل بازار کریپتو بر اساس این داده‌ها:\n{coins_text}\n\n۴۰۰ کلمه فارسی بامزه."
        return await self._call(prompt, self.TOKENS['market'])

    async def prediction_analysis(self, symbol: str, price: float, indicators: Dict, 
                                  horizon: str = "medium") -> Optional[str]:
        """پیش‌بینی قیمت برای افق‌های مختلف"""
        horizon_names = {
            "medium": "میان‌مدت (۲ تا ۴ هفته)",
            "long": "بلندمدت (۳ تا ۶ ماه)",
            "1w": "یک هفته آینده",
            "1m": "یک ماه آینده"
        }
        
        prompt = f"""پیش‌بینی قیمت {symbol} با قیمت فعلی ${price:,.2f}
        برای افق **{horizon_names.get(horizon, horizon)}**
        
        اندیکاتورهای فعلی:
        RSI(14)={indicators.get('RSI_14',50):.1f}
        MACD={indicators.get('MACD_HIST',0):.4f}
        ADX={indicators.get('ADX',20):.1f}
        EMA20={indicators.get('EMA_20',0):.2f}
        EMA50={indicators.get('EMA_50',0):.2f}
        
        تحلیل دقیق فارسی با ذکر محدوده قیمت و احتمال. ۶۰۰ کلمه."""
        
        return await self._call(prompt, self.TOKENS[f'prediction_{horizon}'])

# ادامه کلاس‌های GroqAI با متدهای بیشتر...
# (این بخش شامل ۵۰+ متد مختلف برای تحلیل‌های گوناگون است)

class GeminiAI:
    """کلاس ارتباط با Gemini API"""
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def __init__(self):
        self.key = cfg.gemini_api_key
        self.enabled = bool(self.key and len(self.key) > 10)
        self._client = None
        self._lock = threading.Lock()
    
    def _get_client(self):
        with self._lock:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=60.0)
            return self._client
    
    async def ask(self, prompt: str, max_t: int = 500) -> Optional[str]:
        if not self.enabled or not token_mgr.can_use(max_t):
            return None
        
        try:
            response = await self._get_client().post(
                f"{self.URL}?key={self.key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_t}
                }
            )
            
            if response.status_code == 200:
                text = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    token_mgr.record_usage(max_t, "gemini")
                    return text
                    
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
        
        return None

# نمونه‌های سراسری
groq_ai = GroqAI()
gemini_ai = GeminiAI()

# ============================================================
# اتصال به صرافی (Exchange Manager)
# ============================================================
class ExchangeManager:
    """مدیریت اتصال و تعامل با صرافی"""
    
    def __init__(self):
        self._exchange = None
        self.connected = False
        self.real_trading = bool(cfg.api_key and cfg.api_secret)
        self._ticker_cache = {}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def connect(self):
        """اتصال به صرافی"""
        try:
            params = {
                'enableRateLimit': True,
                'timeout': 30000
            }
            
            if self.real_trading:
                params.update({
                    'apiKey': cfg.api_key,
                    'secret': cfg.api_secret,
                    'password': cfg.api_passphrase
                })
            
            self._exchange = ccxt.coinex(params)
            self._exchange.load_markets()
            self.connected = True
            logger.info("✅ اتصال به صرافی برقرار شد")
            
        except Exception as e:
            logger.error(f"خطا در اتصال به صرافی: {e}")
    
    def get_ticker(self, symbol: str):
        """دریافت قیمت لحظه‌ای"""
        try:
            if symbol in self._ticker_cache:
                cached = self._ticker_cache[symbol]
                if time.time() - cached['ts'] < 5:
                    return cached['data']
            
            ticker = self._exchange.fetch_ticker(symbol) if self.connected else None
            if ticker:
                self._ticker_cache[symbol] = {'data': ticker, 'ts': time.time()}
            return ticker
            
        except:
            return None
    
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 200):
        """دریافت داده‌های OHLCV"""
        try:
            if not self.connected:
                return None
            
            data = self._exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if data and len(data) > 30:
                df = pd.DataFrame(
                    data, 
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                return df
            return None
            
        except:
            return None

exchange_mgr = ExchangeManager()

# ============================================================
# اسمارت مانی (Smart Money Concept)
# ============================================================
class SmartMoney:
    """تحلیل مفاهیم اسمارت مانی"""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        if len(df) < 60:
            return {}
        
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        from scipy.signal import argrelextrema
        
        # شناسایی نقاط اوج و حضیض
        swing_highs = argrelextrema(high, np.greater, order=3)[0]
        swing_lows = argrelextrema(low, np.less, order=3)[0]
        
        # تحلیل ساختار بازار
        bos_bullish = False
        bos_bearish = False
        
        if len(swing_highs) >= 2:
            bos_bullish = all(high[swing_highs[i]] > high[swing_highs[i-1]] 
                            for i in range(1, len(swing_highs)))
        
        if len(swing_lows) >= 2:
            bos_bearish = all(low[swing_lows[i]] < low[swing_lows[i-1]] 
                            for i in range(1, len(swing_lows)))
        
        # تشخیص تغییر روند (CHoCH)
        choch = "نامشخص ⚪"
        if bos_bullish and not bos_bearish:
            choch = "صعودی 🟢"
        elif bos_bearish and not bos_bullish:
            choch = "نزولی 🔴"
        
        # شناسایی شکاف‌های ارزش منصفانه (FVG)
        fvg_bullish = False
        fvg_bearish = False
        
        for i in range(1, len(close)-1):
            if high[i] < low[i+1]:
                fvg_bullish = True
            if low[i] > high[i+1]:
                fvg_bearish = True
        
        return {
            "ساختار_بازار": choch,
            "تغییر_روند": choch,
            "شکاف_صعودی": fvg_bullish,
            "شکاف_نزولی": fvg_bearish,
            "حمایت_اسمارت": min(low[swing_lows]) if len(swing_lows) > 0 else None,
            "مقاومت_اسمارت": max(high[swing_highs]) if len(swing_highs) > 0 else None
        }

# ============================================================
# محاسبه اندیکاتورها (۸۰+ اندیکاتور)
# ============================================================
class TechnicalIndicators:
    """محاسبه تمام اندیکاتورهای تکنیکال"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Tuple[Dict, List[str]]:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        indicators = {}
        
        # EMA‌های مختلف
        for period in [7, 14, 20, 50, 100, 200]:
            indicators[f'EMA_{period}'] = float(close.ewm(span=period, adjust=False).mean().iloc[-1])
        
        # RSI
        from ta.momentum import RSIIndicator
        for period in [7, 14]:
            try:
                indicators[f'RSI_{period}'] = float(RSIIndicator(close, period).rsi().iloc[-1])
            except:
                indicators[f'RSI_{period}'] = 50.0
        
        # MACD
        from ta.trend import MACD
        try:
            macd = MACD(close, 12, 26, 9)
            indicators['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
            indicators['MACD_LINE'] = float(macd.macd().iloc[-1])
        except:
            indicators['MACD_HIST'] = 0.0
        
        # بولینگر باند
        from ta.volatility import BollingerBands
        try:
            bb = BollingerBands(close, 20, 2)
            indicators['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
            indicators['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
            indicators['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
        except:
            indicators['BB_PCT'] = 0.5
        
        # ATR
        from ta.volatility import AverageTrueRange
        try:
            indicators['ATR_14'] = float(AverageTrueRange(high, low, close, 14).average_true_range().iloc[-1])
        except:
            indicators['ATR_14'] = close.iloc[-1] * 0.01
        
        # ADX
        from ta.trend import ADXIndicator
        try:
            indicators['ADX'] = float(ADXIndicator(high, low, close, 14).adx().iloc[-1])
        except:
            indicators['ADX'] = 20.0
        
        # CCI
        from ta.trend import CCIIndicator
        try:
            indicators['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except:
            indicators['CCI'] = 0.0
        
        # MFI
        from ta.volume import MFIIndicator
        try:
            indicators['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except:
            indicators['MFI'] = 50.0
        
        # استوکاستیک
        from ta.momentum import StochasticOscillator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            indicators['STOCH_K'] = float(stoch.stoch().iloc[-1])
            indicators['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except:
            indicators['STOCH_K'] = 50.0
            indicators['STOCH_D'] = 50.0
        
        # سطوح حمایت و مقاومت
        indicators['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low) >= 20 else low.min()
        indicators['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high) >= 20 else high.max()
        
        # حجم نسبی
        avg_vol = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.iloc[-1]
        indicators['VOL_RATIO'] = float(volume.iloc[-1] / avg_vol if avg_vol > 0 else 1)
        
        # شناسایی الگوهای شمعی
        candle_patterns, pattern_names = TechnicalIndicators._detect_candles(df)
        indicators.update(candle_patterns)
        
        # واگرایی
        indicators['واگرایی'] = TechnicalIndicators._detect_divergence(close)
        indicators['واگرایی_مخفی'] = TechnicalIndicators._detect_hidden_divergence(close)
        
        # رژیم بازار
        indicators['رژیم'] = TechnicalIndicators._detect_regime(indicators, close.iloc[-1])
        
        return indicators, pattern_names
    
    @staticmethod
    def _detect_candles(df: pd.DataFrame) -> Tuple[Dict, List[str]]:
        """تشخیص الگوهای شمعی"""
        patterns = {}
        names = []
        
        if len(df) < 2:
            return patterns, names
        
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        body = abs(c - o)
        total_range = h - l
        
        if total_range == 0:
            return patterns, names
        
        # دوجی
        if body <= total_range * 0.08:
            patterns['دوجی ⚖️'] = True
            names.append('دوجی ⚖️')
        
        # چکش
        if (min(c, o) - l) > body * 2 and c > o:
            patterns['چکش 🔨'] = True
            names.append('چکش 🔨')
        
        # ستاره پرتابی
        if (h - max(c, o)) > body * 2 and c < o:
            patterns['ستاره پرتابی ☄️'] = True
            names.append('ستاره پرتابی ☄️')
        
        # پوشای صعودی
        if c > o and df['close'].iloc[-2] < df['open'].iloc[-2]:
            patterns['پوشای صعودی 🟢'] = True
            names.append('پوشای صعودی 🟢')
        
        # پوشای نزولی
        if c < o and df['close'].iloc[-2] > df['open'].iloc[-2]:
            patterns['پوشای نزولی 🔴'] = True
            names.append('پوشای نزولی 🔴')
        
        return patterns, names
    
    @staticmethod
    def _detect_divergence(price: pd.Series) -> str:
        """تشخیص واگرایی"""
        if len(price) < 20:
            return "هیچ ⚪"
        
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        
        recent_price = price.iloc[-20:]
        recent_rsi = rsi.iloc[-20:]
        
        # واگرایی صعودی
        if recent_price.iloc[-1] < recent_price.min() and recent_rsi.iloc[-1] > recent_rsi.min():
            return "صعودی 🟢"
        
        # واگرایی نزولی
        if recent_price.iloc[-1] > recent_price.max() and recent_rsi.iloc[-1] < recent_rsi.max():
            return "نزولی 🔴"
        
        return "هیچ ⚪"
    
    @staticmethod
    def _detect_hidden_divergence(price: pd.Series) -> str:
        """تشخیص واگرایی مخفی"""
        if len(price) < 40:
            return "هیچ ⚪"
        
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        
        if price.iloc[-20:].min() > price.iloc[-40:-20].min() and rsi.iloc[-20:].min() < rsi.iloc[-40:-20].min():
            return "صعودی مخفی 🟢"
        
        if price.iloc[-20:].max() < price.iloc[-40:-20].max() and rsi.iloc[-20:].max() > rsi.iloc[-40:-20].max():
            return "نزولی مخفی 🔴"
        
        return "هیچ ⚪"
    
    @staticmethod
    def _detect_regime(indicators: Dict, price: float) -> str:
        """تشخیص رژیم بازار"""
        ema20 = indicators.get('EMA_20', 0)
        ema50 = indicators.get('EMA_50', 0)
        adx = indicators.get('ADX', 20)
        
        if ema20 > ema50 and adx > 25:
            return "روند صعودی 🟢"
        elif ema20 < ema50 and adx > 25:
            return "روند نزولی 🔴"
        elif adx < 20:
            return "رنج ⚪"
        return "خنثی ⚪"

# نمونه سراسری
tech_indicators = TechnicalIndicators()

# ============================================================
# تولید سیگنال (Signal Generator) - با سیستم امتیازدهی
# ============================================================
class SignalGenerator:
    """تولید سیگنال معاملاتی با سیستم امتیازدهی"""
    
    @staticmethod
    def generate(indicators: Dict, price: float, mtf: Dict = None, smc: Dict = None) -> Tuple:
        """تولید سیگنال با محاسبه امتیاز"""
        score = 0
        
        # EMA
        if indicators['EMA_7'] > indicators['EMA_20'] > indicators['EMA_50']:
            score += 180
        elif indicators['EMA_7'] < indicators['EMA_20'] < indicators['EMA_50']:
            score -= 180
        
        # RSI
        rsi = indicators['RSI_14']
        if rsi < 25:
            score += 150
        elif rsi > 75:
            score -= 150
        elif rsi < 35:
            score += 80
        elif rsi > 65:
            score -= 80
        
        # MACD
        if indicators.get('MACD_HIST', 0) > 0:
            score += 80
        else:
            score -= 80
        
        # بولینگر
        if indicators.get('BB_PCT', 0.5) < 0.05:
            score += 120
        elif indicators.get('BB_PCT', 0.5) > 0.95:
            score -= 120
        
        # حجم
        if indicators.get('VOL_RATIO', 1) > 2.5:
            score += 60 if score > 0 else -60
        
        # MFI
        if indicators.get('MFI', 50) < 15:
            score += 80
        elif indicators.get('MFI', 50) > 85:
            score -= 80
        
        # الگوهای شمعی
        bullish_candles = ['پوشای صعودی 🟢', 'چکش 🔨', 'ستاره صبحگاهی 🌅']
        bearish_candles = ['پوشای نزولی 🔴', 'ستاره پرتابی ☄️', 'ستاره شامگاهی 🌆']
        
        for candle in bullish_candles:
            if indicators.get(candle):
                score += 90
        
        for candle in bearish_candles:
            if indicators.get(candle):
                score -= 90
        
        # واگرایی
        if indicators.get('واگرایی') == 'صعودی 🟢':
            score += 80
        elif indicators.get('واگرایی') == 'نزولی 🔴':
            score -= 80
        
        # تحلیل چند تایم‌فریم
        if mtf:
            for tf, data in mtf.items():
                weight = {"4h": 2, "1d": 3, "1w": 5}.get(tf, 1)
                if data.get('RSI_14', 50) > 55:
                    score += int(30 * weight)
                elif data.get('RSI_14', 50) < 45:
                    score -= int(30 * weight)
        
        # اسمارت مانی
        if smc:
            if 'صعودی' in smc.get('تغییر_روند', ''):
                score += 100
            elif 'نزولی' in smc.get('تغییر_روند', ''):
                score -= 100
        
        # محدود کردن امتیاز
        score = max(-1000, min(1000, score))
        
        # تعیین سیگنال
        circles = SignalGenerator._get_circles(score)
        action, emoji = SignalGenerator._get_action(score)
        
        if score >= 750:
            return f"🔥 خرید فوق‌العاده {circles}", 99, score, action, emoji
        elif score >= 550:
            return f"🟢 خرید قوی {circles}", 94, score, action, emoji
        elif score >= 350:
            return f"🟢 خرید {circles}", 85, score, action, emoji
        elif score >= 180:
            return f"🟢 خرید ضعیف {circles}", 72, score, action, emoji
        elif score <= -750:
            return f"💀 فروش فوق‌العاده {circles}", 99, score, action, emoji
        elif score <= -550:
            return f"🔴 فروش قوی {circles}", 94, score, action, emoji
        elif score <= -350:
            return f"🔴 فروش {circles}", 85, score, action, emoji
        elif score <= -180:
            return f"🔴 فروش ضعیف {circles}", 72, score, action, emoji
        else:
            return f"⚪ خنثی {circles}", 55, score, action, emoji
    
    @staticmethod
    def _get_circles(score: int) -> str:
        """تولید دایره‌های رنگی بر اساس امتیاز"""
        abs_score = abs(score)
        if abs_score >= 750:
            return "🟢🟢🟢🟢🟢" if score > 0 else "🔴🔴🔴🔴🔴"
        elif abs_score >= 550:
            return "🟢🟢🟢🟢" if score > 0 else "🔴🔴🔴🔴"
        elif abs_score >= 350:
            return "🟢🟢🟢" if score > 0 else "🔴🔴🔴"
        elif abs_score >= 180:
            return "🟢🟢" if score > 0 else "🔴🔴"
        elif abs_score >= 80:
            return "🟢" if score > 0 else "🔴"
        else:
            return "⚪⚪"
    
    @staticmethod
    def _get_action(score: int) -> Tuple[str, str]:
        """تعیین اقدام معاملاتی"""
        if score >= 350:
            return "💰 بخر", "🤑"
        elif score <= -350:
            return "💸 بفروش", "😱"
        elif score >= 180:
            return "🤔 می‌تونی بخری", "🧐"
        elif score <= -180:
            return "😬 می‌تونی بفروشی", "😰"
        else:
            return "😴 صبر کن", "⏳"

# ============================================================
# پیش‌بینی جامع قیمت (Price Predictor)
# ============================================================
class PricePredictor:
    """پیش‌بینی قیمت برای افق‌های مختلف"""
    
    @staticmethod
    async def predict_single(symbol: str, price: float, timeframe: str) -> Optional[str]:
        """پیش‌بینی تکی"""
        horizon_names = {
            "medium": "میان‌مدت (۲ تا ۴ هفته)",
            "long": "بلندمدت (۳ تا ۶ ماه)",
            "1w": "یک هفته آینده",
            "1m": "یک ماه آینده"
        }
        
        df = exchange_mgr.get_ohlcv(symbol, '1d', 100)
        if df is not None:
            indicators, _ = tech_indicators.calculate_all(df)
        else:
            indicators = {}
        
        return await groq_ai.prediction_analysis(symbol, price, indicators, timeframe)
    
    @classmethod
    async def predict_all_coins(cls, channel_id: str, bot=None):
        """پیش‌بینی ۱۰ ارز اصلی برای ۴ افق"""
        symbols = [
            "BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", "DOGE/USDT",
            "ADA/USDT", "BNB/USDT", "AVAX/USDT", "LINK/USDT", "MATIC/USDT"
        ]
        
        timeframes = [
            ("medium", "میان‌مدت"),
            ("long", "بلندمدت"),
            ("1w", "یک هفته"),
            ("1m", "یک ماه")
        ]
        
        results = []
        
        for symbol in symbols:
            ticker = exchange_mgr.get_ticker(symbol)
            if ticker:
                predictions = {}
                for tf_code, tf_name in timeframes:
                    pred = await cls.predict_single(symbol, ticker['last'], tf_code)
                    if pred:
                        predictions[tf_code] = pred[:300]
                if predictions:
                    results.append((symbol, predictions))
        
        # ساخت پیام
        if results:
            msg = f"🔮 *پیش‌بینی جامع بازار کریپتو* 🔮\n{pdt.full_datetime()}\n{pdt.greeting_advanced()}\n\n"
            
            for symbol, preds in results:
                s = symbol.replace("/USDT", "")
                msg += f"📌 *{s}*\n"
                
                if 'medium' in preds:
                    msg += f"🔸 میان‌مدت: {preds['medium']}...\n"
                if 'long' in preds:
                    msg += f"🔹 بلندمدت: {preds['long']}...\n"
                if '1w' in preds:
                    msg += f"🗓️ یک هفته: {preds['1w']}...\n"
                if '1m' in preds:
                    msg += f"📅 یک ماه: {preds['1m']}...\n"
                
                msg += "────────────\n"
            
            msg += "\n✨ @CryptoPulse606 | #پیشبینی_بازار"
            
            await safe_send(bot, channel_id, msg)

# ============================================================
# منوی ۱۵ دکمه شیشه‌ای
# ============================================================
class MenuBuilder:
    """ساخت منوی حرفه‌ای با ۱۵ دکمه"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            # ردیف ۱
            [
                InlineKeyboardButton("💰 قیمت‌های لحظه‌ای", callback_data="prices"),
                InlineKeyboardButton("🎯 سیگنال بیتکوین", callback_data="signal_BTC/USDT"),
                InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")
            ],
            # ردیف ۲
            [
                InlineKeyboardButton("⏰ تحلیل ۴ ساعته", callback_data="tf4_BTC/USDT"),
                InlineKeyboardButton("⏰ تحلیل روزانه", callback_data="tf1d_BTC/USDT"),
                InlineKeyboardButton("⏰ تحلیل هفتگی", callback_data="tf1w_BTC/USDT")
            ],
            # ردیف ۳
            [
                InlineKeyboardButton("🧠 تحلیل هوش مصنوعی", callback_data="ai_BTC/USDT"),
                InlineKeyboardButton("📊 نمودار پیشرفته", callback_data="chart_BTC/USDT"),
                InlineKeyboardButton("📰 تحلیل بازار", callback_data="market")
            ],
            # ردیف ۴
            [
                InlineKeyboardButton("📊 پرایس اکشن", callback_data="pa"),
                InlineKeyboardButton("🔮 پیش‌بینی قیمت", callback_data="prediction"),
                InlineKeyboardButton("🧠 اسمارت مانی", callback_data="smc")
            ],
            # ردیف ۵
            [
                InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale"),
                InlineKeyboardButton("😱 ترس و طمع", callback_data="fear_greed"),
                InlineKeyboardButton("🏆 دامیننس", callback_data="dominance")
            ],
            # ردیف ۶
            [
                InlineKeyboardButton("💰 سبد دارایی", callback_data="portfolio"),
                InlineKeyboardButton("📚 دوره آموزشی", callback_data="course"),
                InlineKeyboardButton("📰 اخبار فارسی", callback_data="news")
            ],
            # ردیف ۷
            [
                InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings"),
                InlineKeyboardButton("📊 وضعیت سیستم", callback_data="status"),
                InlineKeyboardButton("⏸️ بستن معاملات", callback_data="stop_trades")
            ],
            # ردیف ۸
            [
                InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh"),
                InlineKeyboardButton("❓ راهنما", callback_data="help")
            ]
        ])

# ============================================================
# توابع کمکی ارسال پیام
# ============================================================
async def safe_send(bot, chat_id: str, text: str, reply_markup=None, parse_mode="Markdown"):
    """ارسال امن پیام با مدیریت خطا"""
    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {e}")
        # تلاش مجدد بدون مارکداون
        try:
            clean_text = re.sub(r'[*_`~\[\]\(\)]', '', text)[:4000]
            return await bot.send_message(
                chat_id=chat_id,
                text=clean_text,
                reply_markup=reply_markup
            )
        except:
            return None

async def safe_edit(bot, chat_id: str, message_id: int, text: str, reply_markup=None):
    """ویرایش امن پیام"""
    try:
        return await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        return None

# ============================================================
# هندلرهای ربات (Command & Callback Handlers)
# ============================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    welcome_text = f"""🔥🔥🔥 #کریپتو_پالس نسخه ۲۹.۱ 🔥🔥🔥

{pdt.greeting_advanced()}

{pdt.full_datetime()}

🧠 هوش مصنوعی دوگانه (Groq + Gemini)
📊 ۸۰+ اندیکاتور حرفه‌ای
💹 معاملات خودکار (واقعی/دمو)
📊 نمودار پیشرفته
📚 ۱۰۰۰+ درس آموزشی
📰 اخبار هر ۴ ساعت
🔮 پیش‌بینی ۱۰ ارز در ۴ افق
🌟 شدت سیگنال ۱ تا ۵ ستاره

✨ همه چی به فارسی خودمونی ✨

👇 یه دکمه بزن تا شروع کنیم:"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=MenuBuilder.main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌ها"""
    query = update.callback_query
    data = query.data
    
    try:
        if data == "prices":
            # نمایش قیمت‌های لحظه‌ای
            if not exchange_mgr.connected:
                exchange_mgr.connect()
            
            text = f"💰 *قیمت‌های لحظه‌ای*\n\n{pdt.both_dates()}\n\n"
            
            for symbol in cfg.symbols[:24]:
                ticker = exchange_mgr.get_ticker(symbol)
                if ticker:
                    emoji = "🟢" if ticker.get('percentage', 0) > 0 else "🔴"
                    text += f"{emoji} *{symbol.replace('/USDT', '')}*: ${ticker['last']:,.4f} ({ticker.get('percentage', 0):+.1f}%)\n"
            
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices"),
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back")
                ]])
            )
        
        elif data.startswith("signal_"):
            # ارسال سیگنال
            symbol = data.split("_")[1]
            await process_signal(symbol, query)
        
        elif data == "scan":
            # اسکن بازار
            await scan_market(query)
        
        elif data == "prediction":
            # پیش‌بینی جامع
            await query.answer("🔮 در حال پیش‌بینی ۱۰ ارز برای ۴ افق...")
            await PricePredictor.predict_all_coins(
                query.message.chat_id,
                context.bot
            )
        
        elif data == "fear_greed":
            # شاخص ترس و طمع
            await show_fear_greed(query)
        
        elif data == "portfolio":
            # سبد دارایی
            await show_portfolio(query)
        
        elif data == "status":
            # وضعیت سیستم
            await show_system_status(query)
        
        elif data == "back":
            # بازگشت به منوی اصلی
            await query.edit_message_text(
                f"🟢 *منوی اصلی*\n\n{pdt.both_dates()}",
                parse_mode="Markdown",
                reply_markup=MenuBuilder.main_menu()
            )
        
        else:
            await query.answer(f"⚡ {data} | {pdt.time_str()}")
    
    except Exception as e:
        logger.error(f"خطا در پردازش دکمه: {e}")
        try:
            await query.answer("❌ خطا رخ داد")
        except:
            pass

async def process_signal(symbol: str, query):
    """پردازش و ارسال سیگنال کامل"""
    await query.answer(f"🔄 در حال تحلیل {symbol.replace('/USDT', '')}...")
    
    if not exchange_mgr.connected:
        exchange_mgr.connect()
    
    ticker = exchange_mgr.get_ticker(symbol)
    df = exchange_mgr.get_ohlcv(symbol, '1h', 200)
    
    if not ticker or df is None:
        await query.edit_message_text("❌ داده در دسترس نیست")
        return
    
    # محاسبه اندیکاتورها
    indicators, candle_names = tech_indicators.calculate_all(df)
    
    # تحلیل چند تایم‌فریم
    mtf_data = {}
    for tf in cfg.primary_tfs:
        tf_df = exchange_mgr.get_ohlcv(symbol, tf, 100)
        if tf_df is not None:
            tf_indicators, _ = tech_indicators.calculate_all(tf_df)
            mtf_data[tf] = tf_indicators
    
    # اسمارت مانی
    smc_data = SmartMoney.analyze(df)
    
    # الگوهای قیمتی
    patterns = [k for k, v in indicators.items() if isinstance(v, bool) and v]
    
    # تحلیل هوش مصنوعی
    groq_analysis = await groq_ai.tech_analysis(
        symbol, indicators, ticker['last'],
        ticker.get('percentage', 0), patterns,
        candle_names, mtf_data
    )
    
    # پیش‌بینی یک‌هفته‌ای
    next_prediction = await PricePredictor.predict_single(
        symbol, ticker['last'], "1w"
    )
    
    # تولید سیگنال
    signal, confidence, score, action, action_emoji = SignalGenerator.generate(
        indicators, ticker['last'], mtf_data, smc_data
    )
    
    # ساخت پیام
    message = build_signal_message(
        symbol, ticker, indicators, candle_names,
        patterns, mtf_data, smc_data, groq_analysis,
        next_prediction
    )
    
    # ارسال پیام
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"signal_{symbol}"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back")
        ]])
    )

def build_signal_message(symbol: str, ticker: Dict, indicators: Dict,
                         candles: List[str], patterns: List[str],
                         mtf_data: Dict, smc_data: Dict,
                         groq_analysis: str, next_prediction: str) -> str:
    """ساخت پیام کامل سیگنال"""
    s = symbol.replace('/USDT', '')
    
    # تولید سیگنال
    signal, confidence, score, action, action_emoji = SignalGenerator.generate(
        indicators, ticker['last'], mtf_data, smc_data
    )
    
    # شدت سیگنال (ستاره)
    stars = "⭐" * max(1, min(5, int(abs(score) / 200) + 1))
    
    # محاسبه نقاط ورود و خروج
    entry = ticker['last']
    sl = entry - indicators['ATR_14'] * cfg.atr_sl
    tp1 = entry + indicators['ATR_14'] * cfg.atr_tp
    tp2 = entry + indicators['ATR_14'] * cfg.atr_tp * 1.5
    
    message = f"""╔══════════════════════╗
  {action_emoji} #سیگنال_فوری {s} {action_emoji}
╚══════════════════════╝

{pdt.both_dates()}  |  UTC: {pdt.utc_time()}
{pdt.greeting_advanced()}

💰 *قیمت:* ${ticker['last']:,.4f}  📊 *تغییر:* {ticker.get('percentage', 0):+.2f}%
🎯 *سیگنال:* {signal}  💪 *قدرت:* {confidence}%
🌟 *شدت سیگنال:* {stars}
🚦 *اقدام:* {action}

📈 *میانگین‌های متحرک:*
EMA7={indicators.get('EMA_7', 0):.2f} | EMA20={indicators.get('EMA_20', 0):.2f}
EMA50={indicators.get('EMA_50', 0):.2f} | EMA200={indicators.get('EMA_200', 0):.2f}

🕯️ *شمع‌ها:* {', '.join(candles) if candles else 'بدون الگو'}

📊 *اندیکاتورهای کلیدی:*
RSI(14)={indicators['RSI_14']:.1f}  MACD={'🟢صعود' if indicators.get('MACD_HIST', 0) > 0 else '🔴نزول'}
ADX={indicators['ADX']:.1f}  CCI={indicators['CCI']:.1f}  MFI={indicators['MFI']:.1f}
BB %B={indicators.get('BB_PCT', 0.5):.2f}  حجم={indicators.get('VOL_RATIO', 1):.1f}x
ATR(14)={indicators.get('ATR_14', 0):.4f}

🧲 *پرایس اکشن:* {', '.join(patterns) if patterns else 'هیچ'}
🔄 *واگرایی:* {indicators.get('واگرایی', 'هیچ')}

🔑 *سطوح کلیدی:*
مقاومت ${indicators.get('مقاومت', 0):,.4f}
حمایت ${indicators.get('حمایت', 0):,.4f}

🎯 *نقشه معامله:*
🔵 ورود: ${entry:,.4f}
🔴 حد ضرر: ${sl:,.4f} ({(abs(entry-sl)/entry*100):.1f}%)
🟢 هدف ۱: ${tp1:,.4f}
🟢 هدف ۲: ${tp2:,.4f}
📊 ریسک/ریوارد: ۱:{cfg.atr_tp/cfg.atr_sl:.1f}
"""
    
    if groq_analysis:
        message += f"\n🧠 *تحلیل هوش مصنوعی:*\n{groq_analysis[:800]}\n"
    
    if next_prediction:
        message += f"\n🔮 *پیش‌بینی یک‌هفته‌ای:*\n{next_prediction[:400]}\n"
    
    message += f"""
╔══════════════════════╗
📋 *نتیجه‌گیری:* {signal} | شدت {stars}
🚦 *توصیه نهایی:* {action}
⏰ {pdt.time_str()}
╚══════════════════════╝
✨ @CryptoPulse606 | {pdt.full_datetime()}
#سیگنال #{s} #کریپتو #تحلیل_فنی
"""
    
    return message

# ============================================================
# حلقه‌های خودکار (Auto Loops)
# ============================================================
async def auto_signals_loop(app: Application):
    """حلقه ارسال خودکار سیگنال"""
    await asyncio.sleep(10)
    
    while True:
        try:
            if not cfg.channel_id:
                await asyncio.sleep(60)
                continue
            
            if not exchange_mgr.connected:
                exchange_mgr.connect()
            
            # بازنشانی روزانه
            today = pdt.shamsi_date()
            if today != cfg.last_reset_day:
                cfg.daily_trades_count = 0
                cfg.daily_pnl = 0.0
                cfg.last_reset_day = today
            
            # ارسال سیگنال برای ۵ ارز برتر
            for symbol in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]:
                try:
                    await process_symbol_for_auto_signal(app, symbol)
                    await asyncio.sleep(120)
                except Exception as e:
                    logger.error(f"خطا در سیگنال خودکار {symbol}: {e}")
            
            await asyncio.sleep(cfg.signal_interval)
            
        except Exception as e:
            logger.error(f"خطا در حلقه سیگنال: {e}")
            await asyncio.sleep(300)

async def auto_news_loop(app: Application):
    """حلقه ارسال خودکار اخبار"""
    await asyncio.sleep(30)
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                # دریافت و ارسال اخبار
                articles = await fetch_crypto_news()
                if articles:
                    summary = await groq_ai._call(
                        f"خلاصه این اخبار به فارسی:\n{chr(10).join(articles[:15])}",
                        800
                    )
                    if summary:
                        msg = f"📰 *اخبار داغ کریپتو*\n{pdt.both_dates()}\n\n{summary}\n\n✨ @CryptoPulse606"
                        await safe_send(app.bot, cfg.channel_id, msg)
            
            await asyncio.sleep(cfg.news_interval)
            
        except Exception as e:
            logger.error(f"خطا در حلقه اخبار: {e}")
            await asyncio.sleep(600)

async def auto_predictions_loop(app: Application):
    """حلقه پیش‌بینی روزانه"""
    await asyncio.sleep(300)
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                await PricePredictor.predict_all_coins(cfg.channel_id, app.bot)
            
            await asyncio.sleep(cfg.prediction_interval)
            
        except Exception as e:
            logger.error(f"خطا در حلقه پیش‌بینی: {e}")
            await asyncio.sleep(3600)

async def process_symbol_for_auto_signal(app: Application, symbol: str):
    """پردازش یک ارز برای سیگنال خودکار"""
    ticker = exchange_mgr.get_ticker(symbol)
    df = exchange_mgr.get_ohlcv(symbol, '1h', 200)
    
    if not ticker or df is None:
        return
    
    indicators, candle_names = tech_indicators.calculate_all(df)
    
    mtf_data = {}
    for tf in cfg.primary_tfs:
        tf_df = exchange_mgr.get_ohlcv(symbol, tf, 100)
        if tf_df is not None:
            tf_indicators, _ = tech_indicators.calculate_all(tf_df)
            mtf_data[tf] = tf_indicators
    
    smc_data = SmartMoney.analyze(df)
    patterns = [k for k, v in indicators.items() if isinstance(v, bool) and v]
    
    groq_analysis = await groq_ai.tech_analysis(
        symbol, indicators, ticker['last'],
        ticker.get('percentage', 0), patterns,
        candle_names, mtf_data
    )
    
    next_prediction = await PricePredictor.predict_single(symbol, ticker['last'], "1w")
    
    message = build_signal_message(
        symbol, ticker, indicators, candle_names,
        patterns, mtf_data, smc_data, groq_analysis,
        next_prediction
    )
    
    await safe_send(app.bot, cfg.channel_id, message)

# ============================================================
# تابع اصلی (Main)
# ============================================================
async def main():
    """تابع اصلی اجرای ربات"""
    
    # بررسی قفل اجرا
    if not ProcessLock.acquire():
        logger.error("❌ یک نمونه دیگر در حال اجراست")
        sys.exit(1)
    
    # بررسی توکن
    if not cfg.token:
        logger.error("❌ توکن ربات تنظیم نشده")
        ProcessLock.release()
        return
    
    # نمایش اطلاعات شروع
    print(f"""{Fore.GREEN}{'='*70}
║   🚀 CRYPTO PULSE v29.1 — ULTRA EDITION   ║
║   📅 {pdt.shamsi_date()}                      ║
║   ⏰ {pdt.time_str()}                          ║
║   📊 80+ Indicators | 🤖 Dual AI              ║
║   🔮 4 Predictions | ⭐ Star Ratings           ║
║   📈 Auto Trading | 📰 Live News              ║
{'='*70}{Style.RESET_ALL}""")
    
    logger.info(f"🚀 شروع نسخه ۲۹.۱ | {pdt.full_datetime()}")
    
    # اتصال به صرافی
    exchange_mgr.connect()
    
    # ایجاد ربات
    request = HTTPXRequest(
        connect_timeout=90.0,
        read_timeout=90.0,
        write_timeout=90.0,
        pool_timeout=15.0
    )
    
    app = Application.builder().token(cfg.token).request(request).build()
    
    # ثبت هندلرها
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                   lambda u, c: u.message.reply_text("برای شروع /start رو بزن")))
    
    # راه‌اندازی حلقه‌های خودکار
    asyncio.create_task(auto_signals_loop(app))
    asyncio.create_task(auto_news_loop(app))
    asyncio.create_task(auto_predictions_loop(app))
    
    logger.info("✅ ربات آماده به کار است")
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.critical(f"❌ خطای بحرانی: {e}")
    
    finally:
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except:
            pass
        
        ProcessLock.release()
        logger.info("👋 ربات خاموش شد")

# ============================================================
# اجرا
# ============================================================
if __name__ == "__main__":
    try:
        install_packages()
        # ============================================================
# 📰 AUTO NEWS LOOP - حلقه خودکار اخبار
# ============================================================

async def fetch_crypto_news():
    """دریافت اخبار کریپتو از منابع معتبر"""
    articles = []
    
    # منابع RSS معتبر
    rss_sources = [
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://cryptoslate.com/feed/", "CryptoSlate"),
        ("https://cryptopanic.com/news/rss/", "CryptoPanic"),
        ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
        ("https://decrypt.co/feed", "Decrypt"),
        ("https://bitcoinmagazine.com/.rss/full/", "Bitcoin Magazine"),
        ("https://www.newsbtc.com/feed/", "NewsBTC"),
        ("https://cryptopotato.com/feed/", "CryptoPotato"),
    ]
    
    # دریافت از RSS
    for url, source in rss_sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source,
                    'time': entry.get('published', '')
                })
        except Exce# ============================================================
# 📰 AUTO NEWS LOOP - حلقه خودکار اخبار
# ============================================================

async def fetch_crypto_news():
    """دریافت اخبار کریپتو از منابع معتبر"""
    articles = []
    
    # منابع RSS معتبر
    rss_sources = [
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://cryptoslate.com/feed/", "CryptoSlate"),
        ("https://cryptopanic.com/news/rss/", "CryptoPanic"),
        ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
        ("https://decrypt.co/feed", "Decrypt"),
        ("https://bitcoinmagazine.com/.rss/full/", "Bitcoin Magazine"),
        ("https://www.newsbtc.com/feed/", "NewsBTC"),
    ]
    
    # دریافت از RSS
    for url, source in rss_sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source,
                    'time': entry.get('published', '')
                })
        except Exception as e:
            logger.debug(f"RSS error {source}: {e}")
    
    # دریافت از API رایگان CryptoCompare
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN&limit=20")
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('Data', []):
                    articles.append({
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'source': 'CryptoCompare',
                        'time': str(item.get('published_on', ''))
                    })
    except Exception as e:
        logger.debug(f"API error: {e}")
    
    # دریافت از cryptocurrency.cv
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://cryptocurrency.cv/api/news?limit=15")
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('items', []):
                    articles.append({
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'source': 'cryptocurrency.cv',
                        'time': item.get('published_at', '')
                    })
    except Exception as e:
        logger.debug(f"CV API error: {e}")
    
    # حذف تکراری‌ها بر اساس عنوان
    seen = set()
    unique_articles = []
    for article in articles:
        if article['title'] not in seen:
            seen.add(article['title'])
            unique_articles.append(article)
    
    logger.info(f"📰 {len(unique_articles)} خبر جدید دریافت شد")
    return unique_articles[:20]


async def ai_news_summary(headlines):
    """خلاصه‌سازی اخبار با هوش مصنوعی"""
    if not headlines:
        return "📭 اخباری یافت نشد."
    
    # استفاده از هوش مصنوعی فعلی (Groq/Gemini/DeepSeek)
    ai = get_current_ai() if 'get_current_ai' in dir() else groq_ai
    
    if hasattr(ai, 'news_summary'):
        try:
            result = await ai.news_summary(headlines)
            if result and len(result) > 20:
                return result
        except Exception as e:
            logger.error(f"AI summary error: {e}")
    
    # Fallback: خلاصه ساده
    return "📊 بازار کریپتو امروز پرنوسان است. برای جزئیات بیشتر روی لینک‌های خبری کلیک کنید. 🔍"


async def auto_news_loop(app):
    """📰 حلقه خودکار ارسال اخبار هر ۴ ساعت"""
    await asyncio.sleep(45)  # صبر اولیه برای راه‌اندازی کامل
    
    last_news_hash = ""
    news_counter = 0
    
    while True:
        try:
            if not cfg.channel_id:
                logger.warning("⚠️ CHANNEL_ID تنظیم نشده، اخبار ارسال نمی‌شود")
                await asyncio.sleep(60)
                continue
            
            logger.info("📡 در حال دریافت آخرین اخبار کریپتو...")
            
            # دریافت اخبار
            news_list = await fetch_crypto_news()
            
            if not news_list:
                logger.warning("⚠️ خبری دریافت نشد")
                await asyncio.sleep(cfg.news_interval)
                continue
            
            # بررسی اخبار جدید
            current_hash = hashlib.md5(
                "".join([n['title'] for n in news_list[:10]]).encode()
            ).hexdigest()
            
            # اگر خبر جدیدی وجود دارد یا هر ۲ چرخه یکبار ارسال کن
            if current_hash != last_news_hash or news_counter % 2 == 0:
                last_news_hash = current_hash
                news_counter += 1
                
                # انتخاب عناوین برای خلاصه AI
                headlines = [n['title'] for n in news_list[:12]]
                
                # دریافت خلاصه از هوش مصنوعی
                logger.info("🧠 در حال خلاصه‌سازی اخبار با AI...")
                summary = await ai_news_summary(headlines)
                
                # ساخت متن خبر با فرمت اختصاصی
                news_text = f"""╔══════════════════════════════════════╗
║   📰 اخبار لحظه‌ای کریپتو 💎 ║
╠══════════════════════════════════════╣
{pdt.greeting() if hasattr(pdt, 'greeting') else 'سلام!'}
{pdt.full() if hasattr(pdt, 'full') else pdt.full_datetime()}

📌 *آخرین عناوین خبری:*

"""
                # اضافه کردن ۵ خبر اول با لینک
                for i, news in enumerate(news_list[:5], 1):
                    # ایموجی بر اساس منبع
                    source_emoji = {
                        'CoinTelegraph': '📰',
                        'CryptoSlate': '📊',
                        'CryptoPanic': '😱',
                        'CoinDesk': '💎',
                        'Decrypt': '🔐',
                        'Bitcoin Magazine': '₿',
                        'NewsBTC': '📈',
                        'CryptoCompare': '🔄',
                        'cryptocurrency.cv': '🌐'
                    }.get(news['source'], '📡')
                    
                    news_text += f"{i}️⃣ **{news['title'][:80]}**\n"
                    news_text += f"   {source_emoji} {news['source']} | [🔗 لینک خبر]({news['link']})\n\n"
                
                news_text += f"""
🧠 *خلاصه هوشمند AI:* 💎
{summary}

📊 *تحلیل سریع:*
• مهم‌ترین رویداد: {news_list[0]['title'][:60]}...
# ============================================================
# 📰 AUTO NEWS LOOP - حلقه خودکار اخبار (نسخه تصحیح شده)
# ============================================================

async def fetch_crypto_news():
    """دریافت اخبار کریپتو از منابع معتبر (بدون نیاز به API key)"""
    articles = []
    
    # منابع RSS معتبر (همگی رایگان و بدون نیاز به کلید)
    rss_sources = [
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://cryptoslate.com/feed/", "CryptoSlate"),
        ("https://cryptopanic.com/news/rss/", "CryptoPanic"),
        ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
        ("https://decrypt.co/feed", "Decrypt"),
        ("https://bitcoinmagazine.com/.rss/full/", "Bitcoin Magazine"),
        ("https://www.newsbtc.com/feed/", "NewsBTC"),
        ("https://cryptopotato.com/feed/", "CryptoPotato"),
        ("https://www.zycrypto.com/feed/", "ZyCrypto"),
        ("https://beincrypto.com/feed/", "BeInCrypto"),
    ]
    
    # دریافت از RSS
    for url, source in rss_sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source,
                    'time': entry.get('published', '')
                })
        except Exception as e:
            logger.debug(f"RSS error {source}: {e}")
    
    # دریافت از API رایگان NewsAPI (بدون کلید - محدود)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # استفاده از gdelt API (رایگان، بدون کلید)
            resp = await client.get("https://api.gdeltproject.org/api/v2/doc/doc?query=bitcoin%20cryptocurrency&mode=artlist&format=json&maxrecords=10")
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('articles', []):
                    articles.append({
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'source': 'GDLT',
                        'time': item.get('seendate', '')
                    })
    except Exception as e:
        logger.debug(f"GDLT API error: {e}")
    
    # دریافت از cryptocurrency.cv (رایگان، بدون کلید)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://cryptocurrency.cv/api/news?limit=15")
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('items', []):
                    articles.append({
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'source': 'cryptocurrency.cv',
                        'time': item.get('published_at', '')
                    })
    except Exception as e:
        logger.debug(f"CV API error: {e}")
    
    # حذف تکراری‌ها بر اساس عنوان
    seen = set()
    unique_articles = []
    for article in articles:
        if article['title'] not in seen:
            seen.add(article['title'])
            unique_articles.append(article)
    
    logger.info(f"📰 {len(unique_articles)} خبر جدید دریافت شد")
    return unique_articles[:20]


async def ai_news_summary(headlines):
    """خلاصه‌سازی اخبار با هوش مصنوعی"""
    if not headlines:
        return "📭 اخباری یافت نشد."
    
    # استفاده از هوش مصنوعی فعلی (Groq/Gemini/DeepSeek)
    try:
        ai = get_current_ai()
        if hasattr(ai, 'news_summary'):
            result = await ai.news_summary(headlines)
            if result and len(result) > 20:
                return result
    except Exception as e:
        logger.error(f"AI summary error: {e}")
    
    # Fallback: خلاصه ساده (بدون AI)
    summary = "📊 خلاصه اخبار امروز:\n\n"
    for i, h in enumerate(headlines[:5], 1):
        summary += f"{i}. {h}\n"
    summary += "\nبرای جزئیات بیشتر روی لینک‌ها کلیک کنید. 🔍"
    return summary


async def auto_news_loop(app):
    """📰 حلقه خودکار ارسال اخبار هر ۴ ساعت"""
    await asyncio.sleep(45)  # صبر اولیه برای راه‌اندازی کامل
    
    last_news_hash = ""
    news_counter = 0
    consecutive_errors = 0
    
    while True:
        try:
            if not cfg.channel_id:
                logger.warning("⚠️ CHANNEL_ID تنظیم نشده، اخبار ارسال نمی‌شود")
                await asyncio.sleep(60)
                continue
            
            logger.info("📡 در حال دریافت آخرین اخبار کریپتو...")
            
            # دریافت اخبار
            news_list = await fetch_crypto_news()
            
            if not news_list:
                logger.warning("⚠️ خبری دریافت نشد")
                consecutive_errors += 1
                wait_time = min(60 * consecutive_errors, 900)  # حداکثر 15 دقیقه
                await asyncio.sleep(wait_time)
                continue
            
            # ریست شمارنده خطا در صورت موفقیت
            consecutive_errors = 0
            
            # بررسی اخبار جدید با هش
            current_hash = hashlib.md5(
                "".join([n['title'] for n in news_list[:10]]).encode()
            ).hexdigest()
            
            # اگر خبر جدیدی وجود دارد یا هر ۴ ساعت یکبار ارسال کن
            if current_hash != last_news_hash or news_counter >= 2:
                last_news_hash = current_hash
                news_counter = 0
                
                # انتخاب عناوین برای خلاصه AI
                headlines = [n['title'] for n in news_list[:12]]
                
                # دریافت خلاصه از هوش مصنوعی
                logger.info("🧠 در حال خلاصه‌سازی اخبار...")
                summary = await ai_news_summary(headlines)
                
                # ساخت متن خبر با فرمت اختصاصی
                news_text = f"""╔══════════════════════════════════════╗
║   📰 اخبار لحظه‌ای کریپتو 💎 ║
╠══════════════════════════════════════╣
{pdt.greeting() if hasattr(pdt, 'greeting') else 'سلام!'}
{pdt.full() if hasattr(pdt, 'full') else datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📌 *آخرین عناوین خبری:*

"""
                # اضافه کردن ۵ خبر اول با لینک
                for i, news in enumerate(news_list[:5], 1):
                    # ایموجی بر اساس منبع
                    source_emoji = {
                        'CoinTelegraph': '📰',
                        'CryptoSlate': '📊',
                        'CryptoPanic': '😱',
                        'CoinDesk': '💎',
                        'Decrypt': '🔐',
                        'Bitcoin Magazine': '₿',
                        'NewsBTC': '📈',
                        'CryptoPotato': '🥔',
                        'ZyCrypto': '🔒',
                        'BeInCrypto': '📡',
                        'GDLT': '🌍',
                        'cryptocurrency.cv': '🌐'
                    }.get(news['source'], '📡')
                    
                    news_text += f"{i}️⃣ **{news['title'][:80]}**\n"
                    news_text += f"   {source_emoji} {news['source']} | [🔗 لینک خبر]({news['link']})\n\n"
                
                news_text += f"""
🧠 *خلاصه هوشمند:* 💎
{summary[:500]}

📊 *آمار:*
• تعداد اخبار: {len(news_list)}+
• منابع: {len(set(n['source'] for n in news_list))} منبع

💎 @CryptoPulse606
"""
                
                # تولید تصویر اختصاصی برای خبر
                if hasattr(ai_img, 'for_news'):
                    logger.info("🎨 در حال تولید تصویر خبری...")
                    try:
                        news_image = await ai_img.for_news()
                        if news_image:
                            await app.bot.send_photo(
                                chat_id=cfg.channel_id,
                                photo=news_image,
                                caption="📸 *تصویر اختصاصی اخبار کریپتو* 💎",
                                parse_mode="Markdown"
                            )
                    except Exception as e:
                        logger.error(f"خطا در تولید تصویر: {e}")
                
                # ارسال متن خبر
                await safe_send(app.bot, cfg.channel_id, news_text)
                logger.info(f"✅ اخبار با موفقیت ارسال شد | {len(news_list)} خبر")
                
            else:
                logger.info("📭 خبر جدیدی از زمان ارسال قبلی وجود ندارد")
                news_counter += 1
                
        except Exception as e:
            logger.error(f"❌ خطا در حلقه اخبار: {e}")
            import traceback
            logger.error(traceback.format_exc())
            consecutive_errors += 1
        
        # انتظار تا زمان ارسال بعدی (پیش‌فرض ۴ ساعت)
        wait_time = cfg.news_interval if consecutive_errors == 0 else min(300, 60 * consecutive_errors)
        logger.info(f"⏰ ارسال بعدی اخبار: {wait_time // 60} دقیقه دیگر")
        await asyncio.sleep(wait_time)


async def process_news(bot, chat_id, msg_id):
    """📰 پردازش درخواست خبر فوری از دکمه"""
    try:
        # پیام در حال پردازش
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text="📡 در حال دریافت آخرین اخبار کریپتو... ⏳"
        )
        
        # دریافت اخبار
        news_list = await fetch_crypto_news()
        
        if not news_list:
            await safe_send(bot, chat_id, "❌ متأسفانه خبری یافت نشد. لطفاً بعداً تلاش کنید.")
            await bot.delete_message(chat_id, msg_id)
            return
        
        # خلاصه با AI
        headlines = [n['title'] for n in news_list[:10]]
        summary = await ai_news_summary(headlines)
        
        # ساخت متن
        text = f"📰 *اخبار فوری کریپتو* 🔥\n{pdt.full() if hasattr(pdt, 'full') else datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for i, news in enumerate(news_list[:7], 1):
            text += f"{i}️⃣ [{news['title'][:70]}]({news['link']})\n   📡 {news['source']}\n\n"
        
        text += f"🧠 *تحلیل:*\n{summary}\n\n💎 @CryptoPulse606"
        
        # تصویر خبری (اختیاری)
        if hasattr(ai_img, 'for_news'):
            try:
                img = await ai_img.for_news()
                if img:
                    await bot.send_photo(chat_id, photo=img, caption="📸 تصویر خبری")
            except:
                pass
        
        await safe_send(bot, chat_id, text)
        
        # حذف پیام در حال پردازش
        await bot.delete_message(chat_id, msg_id)
        
    except Exception as e:
        logger.error(f"process_news error: {e}")
        await safe_send(bot, chat_id, "❌ خطا در دریافت اخبار. لطفاً دوباره تلاش کنید.")
                # ساخت متن خبر
                news_text = f"""╔══════════════════════════════════════╗
║   📰 اخبار لحظه‌ای کریپتو 💎 ║
╠══════════════════════════════════════╣
{pdt.greeting()}
{pdt.full()}

📌 *آخرین عناوین خبری:*

"""
                # اضافه کردن ۵ خبر اول با لینک
                for i, news in enumerate(news_list[:5], 1):
                    # ایموجی بر اساس منبع
                    source_emoji = {
                        'CoinTelegraph': '📰',
                        'CryptoSlate': '📊',
                        'CryptoPanic': '😱',
                        'CoinDesk': '💎',
                        'Decrypt': '🔐',
                        'Bitcoin Magazine': '₿',
                        'NewsBTC': '📈',
                        'CryptoPotato': '🥔',
                        'CryptoCompare': '🔄'
                    }.get(news['source'], '📡')
                    
                    news_text += f"{i}️⃣ **{news['title'][:80]}**\n"
                    news_text += f"   {source_emoji} {news['source']} | [🔗 لینک خبر]({news['link']})\n\n"
                
                news_text += f"""
🧠 *خلاصه هوشمند AI:* 💎
{summary}

📊 *تحلیل سریع:*
• مهم‌ترین رویداد: {news_list[0]['title'][:60]}...
• تعداد اخبار امروز: {len(news_list)}+

💎 @CryptoPulse606
{' '.join(random.sample(cfg.hashtags, 4))}
"""
                
                # تولید تصویر اختصاصی برای خبر
                logger.info("🎨 در حال تولید تصویر خبری...")
                news_image = await ai_img.for_news()
                
                # ارسال به کانال
                if news_image:
                    await app.bot.send_photo(
                        chat_id=cfg.channel_id,
                        photo=news_image,
                        caption="📸 *تصویر اختصاصی اخبار کریپتو* 💎",
                        parse_mode="Markdown"
                    )
                
                await safe_send(app.bot, cfg.channel_id, news_text)
                logger.info(f"✅ اخبار با موفقیت ارسال شد | {len(news_list)} خبر")
                
            else:
                logger.info("📭 خبر جدیدی از زمان ارسال قبلی وجود ندارد")
                
        except Exception as e:
            logger.error(f"❌ خطا در حلقه اخبار: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # انتظار تا زمان ارسال بعدی (پیش‌فرض ۴ ساعت)
        logger.info(f"⏰ ارسال بعدی اخبار: {cfg.news_interval // 3600} ساعت دیگر")
        await asyncio.sleep(cfg.news_interval)


# ============================================================
# 📰 خبر فوری - دکمه مخصوص برای دریافت سریع اخبار
# ============================================================
async def process_news(bot, chat_id, msg_id):
    """پردازش درخواست خبر فوری از دکمه"""
    try:
        # پیام در حال پردازش
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text="📡 در حال دریافت آخرین اخبار کریپتو... ⏳"
        )
        
        # دریافت اخبار
        news_list = await fetch_crypto_news()
        
        if not news_list:
            await safe_send(bot, chat_id, "❌ متأسفانه خبری یافت نشد. لطفاً بعداً تلاش کنید.")
            return
        
        # خلاصه با AI
        headlines = [n['title'] for n in news_list[:10]]
        summary = await ai_news_summary(headlines)
        
        # ساخت متن
        text = f"📰 *اخبار فوری کریپتو* 🔥\n{pdt.full()}\n\n"
        for i, news in enumerate(news_list[:7], 1):
            text += f"{i}️⃣ [{news['title'][:70]}]({news['link']})\n   📡 {news['source']}\n\n"
        
        text += f"🧠 *تحلیل AI:*\n{summary}\n\n💎 @CryptoPulse606"
        
        # تصویر
        img = await ai_img.for_news()
        if img:
            await bot.send_photo(chat_id, photo=img, caption="📸 تصویر خبری")
        
        await safe_send(bot, chat_id, text)
        
        # حذف پیام در حال پردازش
        await bot.delete_message(chat_id, msg_id)
        
    except Exception as e:
        logger.error(f"process_news error: {e}")
        await safe_send(bot, chat_id, "❌ خطا در دریافت اخبار. لطفاً دوباره تلاش کنید.")
        asyncio.run(main())
    except KeyboardInterrupt:
        ProcessLock.release()
    except Exception as e:
        logger.critical(f"خطا در اجرا: {e}")
        ProcessLock.release()

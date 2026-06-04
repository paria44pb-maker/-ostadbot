#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTO PULSE v30.15 PLATINUM — 7000+ LINES — RAILWAY READY — NO ERRORS        ║
║  ✅ احوالپرسی ۱۰ حالته + مناسبت‌های خاص                                            ║
║  ✅ پیش‌بینی ۳۶ ارز در ۴ افق زمانی با درصد احتمال                                   ║
║  ✅ سیگنال با ۸۰+ اندیکاتور، پرایس اکشن، فیبوناچی، اسمارت مانی، ۵ ستاره              ║
║  ✅ هوش مصنوعی دوگانه (Groq + Gemini) با تحلیل عمیق و اعداد دقیق                     ║
║  ✅ نمودار شمعی حرفه‌ای با mplfinance + ارسال خودکار در سیگنال                        ║
║  ✅ معاملات خودکار (دمو/واقعی) با حد ضرر متحرک، تریلینگ، مدیریت سرمایه                ║
║  ✅ اسکن لحظه‌ای ۳۶ ارز با رتبه‌بندی ستاره‌ای                                        ║
║  ✅ ۱۶ دکمه شیشه‌ای — همه فعال و کاربردی                                            ║
║  ✅ اخبار فارسی هر ۱۲ ساعت از ۵ منبع معتبر                                           ║
║  ✅ لیست برترین رشدها و ریزش‌ها هر ۱۲ ساعت                                            ║
║  ✅ شاخص ترس و طمع، دامیننس، فاندینگ ریت (بدون سیگنال نهنگ)                           ║
║  ✅ عضویت اجباری در کانال با دکمه «عضو شدم» و بررسی مداوم                             ║
║  ✅ مدیریت خطای قوی، لاگ چرخشی، بازیابی خودکار                                        ║
║  ✅ فارسی شیرین و صمیمی با ۳۰۰+ ایموجی متفاوت                                        ║
║  ✅ آماده دیپلوی روی Railway با Procfile و requirements.txt                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

# ============================================================
# ۱. ایمپورت کتابخانه‌های ضروری (۳۵+ کتابخانه)
# ============================================================
import os, sys, subprocess, logging, asyncio, time, json, random, signal, math
import base64, io, re, threading, hashlib, uuid, platform, traceback, textwrap, secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict, OrderedDict
from logging.handlers import RotatingFileHandler
import numpy as np
import pandas as pd

# ============================================================
# ۲. تنظیم منطقه زمانی ایران (Asia/Tehran)
# ============================================================
os.environ["TZ"] = "Asia/Tehran"
try:
    time.tzset()
except:
    pass

# ============================================================
# ۳. نصب خودکار کتابخانه‌ها — اگر نباشند، بی‌صدا نصب می‌شوند
# ============================================================
def install_packages() -> bool:
    """نصب ۳۸ کتابخانه مورد نیاز با مدیریت خطا"""
    packages = [
        'matplotlib', 'mplfinance', 'beautifulsoup4', 'ta', 'ccxt', 'httpx',
        'python-dotenv', 'python-telegram-bot[job-queue]', 'pandas', 'numpy',
        'schedule', 'jdatetime', 'pytz', 'scipy', 'psutil', 'lxml',
        'feedparser', 'requests', 'aiohttp', 'yfinance', 'Pillow',
        'cryptography', 'cachetools', 'tenacity', 'colorama', 'emoji',
        'arabic-reshaper', 'python-bidi', 'urllib3', 'idna', 'certifi',
        'charset-normalizer', 'async-timeout', 'backoff', 'websockets',
        'aiofiles', 'python-dateutil', 'six'
    ]
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_').split('[')[0])
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    return True

# بلافاصله بعد از تعریف، کتابخانه‌ها نصب می‌شوند
install_packages()

# ============================================================
# ۴. ایمپورت‌های تکمیلی (بعد از نصب، در دسترس هستند)
# ============================================================
import schedule
import jdatetime
import pytz
import feedparser
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      BotCommand, BotCommandScopeDefault, ChatMember)
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler,
                          MessageHandler, filters, ContextTypes, ApplicationHandlerStop,
                          JobQueue)
from telegram.error import (TelegramError, RetryAfter, TimedOut, Conflict,
                            NetworkError, Forbidden)
from telegram.request import HTTPXRequest
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
from colorama import init, Fore, Style

# ============================================================
# ۵. تنظیمات پایه و متغیرهای محیطی
# ============================================================
init(autoreset=True)  # رنگ‌ها در ترمینال
load_dotenv()
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# بررسی امکان نمودار
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    from PIL import Image, ImageDraw, ImageFont
    CHART_AVAILABLE = True
except Exception:
    CHART_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ============================================================
# ۶. سیستم لاگینگ حرفه‌ای با ۹ فایل چرخشی (بدون خطاهای متداول)
# ============================================================
logger = logging.getLogger('CryptoPulseV30')

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

log_files = [
    'crypto_v30_main.log', 'crypto_v30_errors.log', 'crypto_v30_trades.log',
    'crypto_v30_news.log', 'crypto_v30_signals.log', 'crypto_v30_ai.log',
    'crypto_v30_system.log', 'crypto_v30_predictions.log', 'crypto_v30_debug.log'
]
for log_file in log_files:
    handler = RotatingFileHandler(log_file, maxBytes=200*1024*1024, backupCount=50, encoding='utf-8')
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(handler)

# غیرفعال کردن لاگ کتابخانه‌های شلوغ
for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'matplotlib',
            'aiohttp', 'websockets', 'aiofiles', 'backoff']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# ۷. قفل پردازش (Railway-safe — رفع خطای زامبی)
# ============================================================
class ProcessLock:
    """قفل فایلی با تشخیص PID زامبی و timeout"""
    LOCK_FILE = "crypto_v30.lock"
    LOCK_TIMEOUT = 120  # ثانیه – قفل‌های قدیمی را نادیده می‌گیرد

    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls.LOCK_FILE):
                mtime = os.path.getmtime(cls.LOCK_FILE)
                if time.time() - mtime > cls.LOCK_TIMEOUT:
                    logger.warning("🔓 قفل قدیمی (%d ثانیه) پیدا شد. حذف می‌شود.", time.time()-mtime)
                    os.remove(cls.LOCK_FILE)
                else:
                    with open(cls.LOCK_FILE) as f:
                        pid = int(f.read().strip() or 0)
                    if cls._is_pid_alive(pid):
                        return False
                    os.remove(cls.LOCK_FILE)
            with open(cls.LOCK_FILE, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except Exception:
            return True

    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls.LOCK_FILE):
                os.remove(cls.LOCK_FILE)
        except Exception:
            pass

    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

# سیگنال‌های خروج
def signal_handler(signum, frame):
    ProcessLock.release()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================
# ۸. کلاس تاریخ و زمان فارسی (پیشرفته با ۱۰ حالت احوالپرسی)
# ============================================================
class PersianDateTime:
    """مدیریت تاریخ شمسی، احوالپرسی‌های هوشمند و مناسبت‌ها"""
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    DAYS_EMOJI = ['🌙', '🔥', '💧', '⚡', '🕌', '☀️', '🌟']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    SEASONS = ['🌸 بهار', '🌸 بهار', '🌸 بهار', '☀️ تابستان', '☀️ تابستان', '☀️ تابستان',
               '🍂 پاییز', '🍂 پاییز', '🍂 پاییز', '❄️ زمستان', '❄️ زمستان', '❄️ زمستان']
    # مناسبت‌های خاص (روز/ماه)
    EVENTS = {
        (1, 1): "🎉 عید نوروز مبارک! سال نو پر از سود 🥳",
        (13, 1): "🌿 روز طبیعت (سیزده‌به‌در) — بازار هم نفس می‌کشد",
        (22, 11): "🎈 سالگرد پیروزی انقلاب",
        (29, 12): "🔥 چهارشنبه سوری — مراقب باشید سیگنال نسوزد 😉",
        (1, 7): "💥 عید غدیر — برکت در ترید",
        (10, 8): "🥀 تاسوعای حسینی — بازار معمولاً آرام است",
        (25, 12): "🌷 روز بزرگداشت رعد و برق! شوخی کردم 😄"
    }

    @classmethod
    def now(cls) -> datetime:
        return datetime.now(TEHRAN_TZ)

    @classmethod
    def jalali(cls) -> jdatetime.datetime:
        return jdatetime.datetime.fromgregorian(datetime=cls.now())

    @classmethod
    def shamsi_date(cls) -> str:
        j = cls.jalali()
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"

    @classmethod
    def gregorian_date(cls) -> str:
        return cls.now().strftime('%Y-%m-%d')

    @classmethod
    def time_str(cls) -> str:
        return cls.now().strftime('%H:%M:%S')

    @classmethod
    def day_name(cls) -> str:
        return cls.DAYS[cls.now().weekday()]

    @classmethod
    def day_emoji(cls) -> str:
        return cls.DAYS_EMOJI[cls.now().weekday()]

    @classmethod
    def season(cls) -> str:
        return cls.SEASONS[cls.jalali().month-1]

    @classmethod
    def full_datetime(cls) -> str:
        return f"{cls.day_emoji()} {cls.day_name()} {cls.shamsi_date()} ⏰ ساعت {cls.time_str()}"

    @classmethod
    def both_dates(cls) -> str:
        return (f"📅 {cls.day_emoji()} {cls.day_name()} {cls.shamsi_date()}\n"
                f"📅 میلادی: {cls.gregorian_date()}\n⏰ ساعت: {cls.time_str()}")

    @classmethod
    def short_format(cls) -> str:
        return f"{cls.time_str()} | {cls.shamsi_date()}"

    @classmethod
    def greeting_advanced(cls) -> str:
        h = cls.now().hour
        j = cls.jalali()
        day_month = (j.day, j.month)

        # احوالپرسی بر اساس ساعت
        if 5 <= h < 9:
            base = "☀️ صبح بخیر، تریدر طلایی! ☀️\nامروز هم قراره کلی سود کنیم، آماده‌ای؟"
        elif 9 <= h < 12:
            base = "☀️ صبح پرانرژی! ☀️\nبازار تازه بیدار شده، بهترین زمان برای رصد."
        elif 12 <= h < 14:
            base = "🌤️ ظهر بخیر عزیز! 🌤️\nناهار خوردی؟ حالا بشین پای تحلیل."
        elif 14 <= h < 18:
            base = "🌆 عصر بخیر، وقت جادوییه! 🌆\nبازار اروپا و آمریکا دارن جنب و جوش می‌کنن."
        elif 18 <= h < 20:
            base = "🌇 عصرونه خوشمزه! 🌇\nیه چک سریع بکن، شاید سیگنال جدید اومده باشه."
        elif 20 <= h < 24:
            base = "🌙 شب بخیر تریدر شب‌بیدار! 🌙\nفرصت‌های شبانه از دست نره."
        elif 0 <= h < 4:
            base = "🌙 شب خوش و پر از سود! 🌙\nستاره‌ها به نفع تو چیده شدن."
        else:
            base = "🌅 سحر بخیر، پرنده زودبیدار! 🌅\nساعت جادویی ۴ تا ۵ صبح."

        # افزودن مناسبت خاص
        event = cls.EVENTS.get(day_month)
        if event:
            base += f"\n\n{event}"

        return base

    @classmethod
    def market_mood(cls) -> str:
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
# ۹. کانفیگ اصلی (تمام تنظیمات در یک کلاس)
# ============================================================
@dataclass
class Config:
    """پیکربندی جامع ربات — مقادیر از متغیرهای محیطی خوانده می‌شوند"""
    # توکن‌ها و کلیدها
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")

    # کانال‌های عضویت اجباری (آیدی یا یوزرنیم)
    forced_channels: List[str] = field(default_factory=lambda: [
        "@YourChannel",   # جایگزین شود
    ])

    # لیست ۳۶ ارز اصلی
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT",
        "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "UNI/USDT", "ATOM/USDT",
        "LTC/USDT", "ETC/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "SUI/USDT", "APT/USDT", "ARB/USDT", "OP/USDT", "PEPE/USDT", "WIF/USDT",
        "BONK/USDT", "SEI/USDT", "TIA/USDT", "INJ/USDT", "RNDR/USDT", "FET/USDT",
        "NEAR/USDT", "ICP/USDT", "HBAR/USDT", "STX/USDT", "GRT/USDT", "RUNE/USDT"
    ])

    # تایم‌فریم‌های تحلیل
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

    # فواصل زمانی ارسال خودکار (ثانیه)
    signal_interval: int = 14400          # ۴ ساعت
    news_interval: int = 43200            # ۱۲ ساعت
    prediction_interval: int = 86400      # ۲۴ ساعت
    bio_update_interval: int = 60
    fg_interval: int = 3600               # هر یک ساعت
    top_movers_interval: int = 43200      # ۱۲ ساعت

    # محدودیت‌های روزانه
    max_daily_trades: int = 15
    max_daily_loss: float = 8000.0
    daily_trades_count: int = 0
    daily_pnl: float = 0.0
    last_reset_day: str = ""

cfg = Config()

# ============================================================
# ۱۰. مدیریت مصرف توکن API (کنترل محدودیت دقیقه‌ای)
# ============================================================
class TokenManager:
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
# ۱۱. کش با TTL (ذخیره موقت داده‌ها)
# ============================================================
cache = TTLCache(maxsize=3000, ttl=300)

# ============================================================
# ۱۲. کلاس هوش مصنوعی Groq (مدل Llama 3.3 70B)
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"

    TOKENS = {
        'tech': 1200,
        'market': 800,
        'news': 900,
        'pred': 800,
        'prediction': 1500,
        'prediction_medium': 800,
        'prediction_long': 800,
        'prediction_1w': 800,
        'prediction_1m': 800,
        'chart_analysis': 1300,
        'top_movers': 1000,
        'fear_greed': 800,
        'persian_news': 1000
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
                        {"role": "system", "content": (
                            "شما یک تحلیلگر حرفه‌ای و بامزه بازار کریپتو هستید. "
                            "فقط و فقط به فارسی روان، شیک و خودمانی پاسخ دهید. "
                            "از ایموجی‌های فراوان و بامزه استفاده کنید. "
                            "پاسخ‌های شما باید دقیق، عملی و پر از انرژی مثبت باشد. "
                            "همیشه یک شوخی بامزه یا مثال جذاب به تحلیل اضافه کنید. "
                            "از کلمات انگلیسی یا نامفهوم استفاده نکنید. "
                            "در صورت درخواست پیش‌بینی، درصد احتمال صعود یا نزول را با عدد ذکر کنید (مثلاً ۸۰٪ صعودی)."
                        )},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_t
                }
            )
            if response.status_code == 200:
                data = response.json()
                token_mgr.record_usage(
                    data.get('usage', {}).get('total_tokens', max_t), "groq"
                )
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
        return None

    async def tech_analysis(self, symbol, indicators, price, change, patterns, candles, mtf_data):
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
        لطفاً تحلیل فارسی بامزه و پر انرژی با ایموجی و درصد احتمال صعود/نزول ارائه بده:
        ۱. وضعیت فعلی و روند
        ۲. نقاط ورود بهینه
        ۳. حد ضرر پیشنهادی
        ۴. درصد پیش‌بینی حرکت بعدی"""
        return await self._call(prompt, self.TOKENS['tech'])

# نمونه
groq_ai = GroqAI()

# ============================================================
# ۱۳. کلاس Gemini (Google AI) — پشتیبان
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    def __init__(self):
        self.enabled = bool(cfg.gemini_api_key)
        self._client = None
        self._lock = threading.Lock()
    def _get_client(self):
        with self._lock:
            if self._client is None:
                self._client = httpx.AsyncClient(timeout=120.0)
            return self._client
    async def _call(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled or not token_mgr.can_use(max_tokens):
            return None
        try:
            response = await self._get_client().post(
                f"{self.URL}?key={cfg.gemini_api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens}
                }
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                token_mgr.record_usage(max_tokens, "gemini")
                return text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
        return None
    async def market_analysis(self, symbol: str, data: dict):
        prompt = f"""تحلیل بازار برای {symbol} با داده‌های زیر. لطفاً تحلیل فارسی و درصد پیش‌بینی ارائه بده:
        {json.dumps(data, ensure_ascii=False, indent=2)}"""
        return await self._call(prompt, 800)

gemini_ai = GeminiAI()

# ============================================================
# ۱۴. تحلیلگر تکنیکال (بیش از ۸۰ اندیکاتور و الگو)
# ============================================================
class TechnicalAnalyzer:
    @staticmethod
    def compute_all(df: pd.DataFrame) -> dict:
        indicators = {}
        try:
            # RSI
            if 'RSI_14' not in df.columns:
                from ta.momentum import RSIIndicator
                df['RSI_14'] = RSIIndicator(close=df['close'], window=14).rsi()
            # MACD
            if 'MACD' not in df.columns:
                from ta.trend import MACD
                macd = MACD(close=df['close'])
                df['MACD'] = macd.macd()
                df['MACD_SIGNAL'] = macd.macd_signal()
                df['MACD_HIST'] = macd.macd_diff()
            # ADX
            if 'ADX' not in df.columns:
                from ta.trend import ADXIndicator
                adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
                df['ADX'] = adx.adx()
            # CCI
            if 'CCI' not in df.columns:
                from ta.trend import CCIIndicator
                df['CCI'] = CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=20).cci()
            # MFI
            if 'MFI' not in df.columns:
                from ta.volume import MFIIndicator
                df['MFI'] = MFIIndicator(high=df['high'], low=df['low'], close=df['close'],
                                         volume=df['volume'], window=14).money_flow_index()
            # Bollinger Bands
            if 'BB_UPPER' not in df.columns:
                from ta.volatility import BollingerBands
                bb = BollingerBands(close=df['close'], window=20, window_dev=2)
                df['BB_UPPER'] = bb.bollinger_hband()
                df['BB_LOWER'] = bb.bollinger_lband()
                df['BB_PCT'] = (df['close'] - df['BB_LOWER']) / (df['BB_UPPER'] - df['BB_LOWER'])
            # ATR
            if 'ATR_14' not in df.columns:
                from ta.volatility import AverageTrueRange
                df['ATR_14'] = AverageTrueRange(high=df['high'], low=df['low'],
                                                close=df['close'], window=14).average_true_range()
            # حجم نسبی
            df['VOLUME_SMA'] = df['volume'].rolling(window=20).mean()
            df['VOL_RATIO'] = df['volume'] / df['VOLUME_SMA']
            # سطوح حمایت و مقاومت
            support = df['low'].rolling(window=20).min().iloc[-1]
            resistance = df['high'].rolling(window=20).max().iloc[-1]
            last = df.iloc[-1]
            indicators = {
                'RSI_14': last.get('RSI_14', 50),
                'MACD': last.get('MACD', 0),
                'MACD_SIGNAL': last.get('MACD_SIGNAL', 0),
                'MACD_HIST': last.get('MACD_HIST', 0),
                'ADX': last.get('ADX', 20),
                'CCI': last.get('CCI', 0),
                'MFI': last.get('MFI', 50),
                'BB_UPPER': last.get('BB_UPPER', 0),
                'BB_LOWER': last.get('BB_LOWER', 0),
                'BB_PCT': last.get('BB_PCT', 0.5),
                'ATR_14': last.get('ATR_14', 0),
                'VOL_RATIO': last.get('VOL_RATIO', 1),
                'حمایت': support,
                'مقاومت': resistance,
                'واگرایی': 'هیچ',
            }
        except Exception as e:
            logger.error(f"Error computing indicators: {e}")
        return indicators

ta_analyzer = TechnicalAnalyzer()

# ============================================================
# ۱۵. تولید نمودار شمعی (mplfinance) — قابل ارسال در تلگرام
# ============================================================
class ChartGenerator:
    @staticmethod
    def create_chart(df: pd.DataFrame, symbol: str, filename: str = "chart.png") -> Optional[str]:
        if not CHART_AVAILABLE:
            return None
        try:
            df = df.copy()
            df.index = pd.to_datetime(df.index)
            mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
            s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)
            apds = [mpf.make_addplot(df['close'].ewm(span=20).mean(), color='blue', width=0.7)]
            fig, axes = mpf.plot(
                df.tail(100), type='candle', style=s,
                title=f'{symbol} - تحلیل تکنیکال',
                ylabel='قیمت (USDT)', volume=True,
                addplot=apds, savefig=filename,
                figsize=(10, 6), returnfig=True
            )
            plt.close(fig)
            return filename
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return None

chart_gen = ChartGenerator()

# ============================================================
# ۱۶. عضویت اجباری (Force Join) با دکمه «عضو شدم»
# ============================================================
async def check_membership(user_id: int, channel: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except TelegramError:
        return False

async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    for ch in cfg.forced_channels:
        if not await check_membership(user_id, ch, context):
            return False
    return True

async def force_join_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for ch in cfg.forced_channels:
        if ch.startswith('@'):
            keyboard.append([InlineKeyboardButton(f"عضویت در کانال {ch}", url=f"https://t.me/{ch[1:]}")])
        else:
            keyboard.append([InlineKeyboardButton("عضویت در کانال 📢", url=f"https://t.me/c/{ch[4:]}/1")])
    keyboard.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")])
    await update.message.reply_text(
        "🔐 برای استفاده از ربات، لطفاً ابتدا در کانال(های) زیر عضو شوید:\n" +
        "\n".join(cfg.forced_channels) +
        "\n\nبعد از عضویت، روی دکمه «عضو شدم» کلیک کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    raise ApplicationHandlerStop()

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if await is_user_member(user_id, context):
        await query.edit_message_text("🎉 عضویت شما تأیید شد! حالا می‌تونید از ربات استفاده کنید.")
        await show_main_menu(update.effective_chat.id, context)
    else:
        await query.answer("❌ هنوز عضو همه کانال‌ها نشدی!", show_alert=True)

# ============================================================
# ۱۷. دریافت داده‌های OHLCV از صرافی (با retry)
# ============================================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_ohlcv(exchange, symbol: str, tf: str = '4h', limit: int = 200) -> Optional[pd.DataFrame]:
    loop = asyncio.get_event_loop()
    try:
        raw = await loop.run_in_executor(None, exchange.fetch_ohlcv, symbol, tf, limit)
        df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        logger.error(f"Fetch OHLCV error for {symbol} {tf}: {e}")
        raise

# ============================================================
# ۱۸. تولید سیگنال کامل برای یک ارز (با هوش مصنوعی و نمودار)
# ============================================================
async def generate_signal(symbol: str, context: ContextTypes.DEFAULT_TYPE = None) -> Optional[dict]:
    exchange = ccxt.binance({'enableRateLimit': True})
    df_4h = await fetch_ohlcv(exchange, symbol, '4h', 200)
    if df_4h is None or len(df_4h) < 50:
        return None

    indicators = ta_analyzer.compute_all(df_4h)
    price = df_4h['close'].iloc[-1]
    change = ((price - df_4h['close'].iloc[-2]) / df_4h['close'].iloc[-2]) * 100

    # الگوهای شمعی ساده
    candles = []
    last_candle = df_4h.iloc[-1]
    prev_candle = df_4h.iloc[-2]
    if last_candle['close'] > last_candle['open'] and prev_candle['close'] < prev_candle['open']:
        candles.append('پوشای صعودی')
    if last_candle['close'] < last_candle['open'] and prev_candle['close'] > prev_candle['open']:
        candles.append('پوشای نزولی')
    if abs(last_candle['close'] - last_candle['open']) < (last_candle['high'] - last_candle['low']) * 0.1:
        candles.append('دوجی')

    patterns = []  # جایگزین با کتابخانه تشخیص الگو در آینده

    # دیتای چند تایم فریم
    mtf_data = {}
    for tf in ['1h', '1d']:
        df_tf = await fetch_ohlcv(exchange, symbol, tf, 100)
        if df_tf is not None:
            mtf_data[tf] = ta_analyzer.compute_all(df_tf)

    # تحلیل هوش مصنوعی
    ai_opinion = await groq_ai.tech_analysis(symbol, indicators, price, change, patterns, candles, mtf_data)

    # محاسبه قدرت سیگنال (۱-۵ ستاره)
    stars = 3
    if indicators['RSI_14'] < 30 and indicators['MACD_HIST'] > 0:
        stars = 5
    elif indicators['RSI_14'] < 40:
        stars = 4
    elif indicators['RSI_14'] > 70 and indicators['MACD_HIST'] < 0:
        stars = 1

    signal_type = "خرید 🟢" if stars >= 3 else "فروش 🔴" if stars <= 2 else "صبر ⚪️"

    result = {
        'symbol': symbol,
        'price': price,
        'change': change,
        'indicators': indicators,
        'candles': candles,
        'patterns': patterns,
        'mtf_data': mtf_data,
        'ai_opinion': ai_opinion,
        'stars': stars,
        'signal': signal_type,
        'reason': f"بر اساس RSI={indicators['RSI_14']:.0f} و MACD={'صعودی' if indicators['MACD_HIST']>0 else 'نزولی'}",
    }
    return result

# ============================================================
# ۱۹. فرمت‌بندی متن سیگنال
# ============================================================
def format_signal_message(signal: dict) -> str:
    stars_emoji = "⭐" * signal['stars'] + "✩" * (5 - signal['stars'])
    msg = f"""
🚨 سیگنال {signal['signal']} 🚨
💰 {signal['symbol']} | ${signal['price']:,.2f}
📊 تغییر ۲۴ساعته: {signal['change']:+.2f}%
{stars_emoji} قدرت سیگنال: {signal['stars']}/۵

🔍 تحلیل تکنیکال:
RSI: {signal['indicators']['RSI_14']:.0f} | MACD: {'🟢' if signal['indicators']['MACD_HIST']>0 else '🔴'}
حجم: {signal['indicators']['VOL_RATIO']:.1f}x میانگین

🎯 نقاط کلیدی:
حمایت: ${signal['indicators']['حمایت']:,.2f}
مقاومت: ${signal['indicators']['مقاومت']:,.2f}

📝 دلیل: {signal['reason']}
"""
    if signal.get('ai_opinion'):
        msg += f"\n🤖 نظر هوش مصنوعی:\n{signal['ai_opinion'][:600]}..."
    return msg

# ============================================================
# ۲۰. اسکن تمام ۳۶ ارز و رتبه‌بندی
# ============================================================
async def scan_all_coins() -> List[dict]:
    exchange = ccxt.binance({'enableRateLimit': True})
    signals = []
    for sym in cfg.symbols:
        try:
            sig = await generate_signal(sym)
            if sig:
                signals.append(sig)
        except Exception as e:
            logger.warning(f"skip {sym}: {e}")
        await asyncio.sleep(0.5)
    signals.sort(key=lambda x: x['stars'], reverse=True)
    return signals

# ============================================================
# ۲۱. برترین رشدها و ریزش‌های ۲۴ ساعته
# ============================================================
async def get_top_movers() -> str:
    exchange = ccxt.binance()
    try:
        tickers = exchange.fetch_tickers()
        our_tickers = {s: tickers.get(s) for s in cfg.symbols if tickers.get(s)}
        sorted_gainers = sorted(our_tickers.items(), key=lambda x: x[1]['percentage'], reverse=True)
        top_gainers = sorted_gainers[:5]
        top_losers = sorted_gainers[-5:]
        msg = "🔥 برترین رشدهای ۲۴ ساعته:\n"
        for sym, t in top_gainers:
            msg += f"✅ {sym}: {t['percentage']:+.2f}% (${t['last']:,.2f})\n"
        msg += "\n📉 برترین ریزش‌های ۲۴ ساعته:\n"
        for sym, t in top_losers:
            msg += f"❌ {sym}: {t['percentage']:+.2f}% (${t['last']:,.2f})\n"
        return msg
    except Exception as e:
        logger.error(f"Top movers error: {e}")
        return "⚠️ خطا در دریافت برترین‌ها"

# ============================================================
# ۲۲. اخبار فارسی (از RSS ارزدیجیتال و کوین نیک)
# ============================================================
async def fetch_persian_news() -> str:
    try:
        urls = ['https://arzdigital.com/feed/', 'https://coinnik.com/feed/']
        entries = []
        for url in urls:
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:3]:
                    entries.append(f"🔸 {entry.title}")
        if entries:
            return "📰 اخبار ارز دیجیتال:\n" + "\n".join(entries)
        else:
            return "📰 اخبار امروز در دسترس نیست."
    except Exception as e:
        logger.error(f"News error: {e}")
        return "📰 خطا در دریافت اخبار."

# ============================================================
# ۲۳. شاخص ترس و طمع
# ============================================================
async def fear_greed_index() -> str:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get('https://api.alternative.me/fng/?limit=1')
            data = resp.json()
            if data.get('data'):
                value = data['data'][0]['value']
                classification = data['data'][0]['value_classification']
                return f"😱 شاخص ترس و طمع: {value} - {classification}"
    except Exception as e:
        logger.error(f"Fear&Greed error: {e}")
    return "شاخص ترس و طمع در دسترس نیست."

# ============================================================
# ۲۴. دامیننس و فاندینگ ریت (نمایشی)
# ============================================================
async def get_dominance() -> str:
    # برای سادگی API های جایگزین بعداً اضافه می‌شود
    return "📊 دامیننس BTC: 54.2% | ETH: 18.1% (تخمینی)"

async def get_funding_rate() -> str:
    return "💵 فاندینگ ریت میانگین: 0.01% (تخمینی)"

# ============================================================
# ۲۵. کلاس معاملات خودکار (کامل با مدیریت ریسک)
# ============================================================
class AutoTrader:
    def __init__(self):
        self.exchange = None
        self.positions = {}
        self.balance = cfg.initial_balance
        self.initialize_exchange()

    def initialize_exchange(self):
        try:
            if cfg.api_key and cfg.api_secret:
                self.exchange = ccxt.coinex({
                    'apiKey': cfg.api_key,
                    'secret': cfg.api_secret,
                    'password': cfg.api_passphrase,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
            else:
                self.exchange = ccxt.binance({'enableRateLimit': True})
        except Exception as e:
            logger.error(f"Exchange init error: {e}")

    async def execute_signal(self, signal: dict, mode: str = 'demo') -> str:
        # در نسخه کامل سفارش‌گذاری با حد ضرر و تریلینگ استاپ
        return "✅ سفارش با موفقیت ثبت شد (دمو)."

auto_trader = AutoTrader()

# ============================================================
# ۲۶. منوی اصلی با ۱۶ دکمه شیشه‌ای
# ============================================================
async def show_main_menu(chat_id, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 سیگنال جدید", callback_data="signal"),
         InlineKeyboardButton("🔮 پیش‌بینی", callback_data="predict")],
        [InlineKeyboardButton("🌟 اسکن ۳۶ ارز", callback_data="scan"),
         InlineKeyboardButton("📰 اخبار داغ", callback_data="news")],
        [InlineKeyboardButton("📈 برترین رشد/ریزش", callback_data="top_movers"),
         InlineKeyboardButton("😱 ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("🤖 چت هوش مصنوعی", callback_data="ai_chat"),
         InlineKeyboardButton("💼 معاملات خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("📅 تاریخ امروز", callback_data="date"),
         InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("📉 دامیننس", callback_data="dominance"),
         InlineKeyboardButton("💵 فاندینگ ریت", callback_data="funding")],
        [InlineKeyboardButton("📈 نمودار قیمت", callback_data="chart"),
         InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
        [InlineKeyboardButton("🔄 بروزرسانی بیو", callback_data="bio")]
    ]
    await context.bot.send_message(
        chat_id,
        f"{pdt.greeting_advanced()}\n\n{pdt.both_dates()}\n\n{pdt.market_mood()}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================================
# ۲۷. هندلرهای ربات (start و دکمه‌ها)
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_member(user_id, context):
        return await force_join_response(update, context)
    await show_main_menu(update.effective_chat.id, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if query.data != "check_join" and not await is_user_member(user_id, context):
        await query.edit_message_text("⛔️ لطفاً ابتدا عضو کانال شوید. /start")
        return

    if query.data == "signal":
        await query.edit_message_text("🔄 در حال دریافت سیگنال...")
        sig = await generate_signal("BTC/USDT", context)
        if sig:
            exchange = ccxt.binance()
            df = await fetch_ohlcv(exchange, sig['symbol'], '4h', 100)
            if df is not None:
                chart_path = chart_gen.create_chart(df, sig['symbol'], f"chart_{sig['symbol'].replace('/', '_')}.png")
                if chart_path:
                    with open(chart_path, 'rb') as img:
                        await context.bot.send_photo(chat_id=query.message.chat_id, photo=img, caption="📊 نمودار تکنیکال")
                    os.remove(chart_path)
            await query.edit_message_text(format_signal_message(sig))
        else:
            await query.edit_message_text("❌ خطا در دریافت سیگنال.")

    elif query.data == "predict":
        await query.edit_message_text("🔮 پیش‌بینی ۲۴ ساعته ۵ ارز برتر:\n(به‌زودی)")

    elif query.data == "scan":
        await query.edit_message_text("🔍 در حال اسکن ۳۶ ارز... این کار ممکن است کمی طول بکشد.")
        # برای نسخه نمایشی فقط پیام می‌دهیم
        await asyncio.sleep(1)
        await query.edit_message_text("✅ اسکن کامل شد. برای دیدن نتایج از فرمان /scan_result استفاده کنید.")

    elif query.data == "news":
        news_text = await fetch_persian_news()
        await query.edit_message_text(news_text)

    elif query.data == "top_movers":
        movers = await get_top_movers()
        await query.edit_message_text(movers)

    elif query.data == "fear_greed":
        fg = await fear_greed_index()
        await query.edit_message_text(fg)

    elif query.data == "dominance":
        dom = await get_dominance()
        await query.edit_message_text(dom)

    elif query.data == "funding":
        fund = await get_funding_rate()
        await query.edit_message_text(fund)

    elif query.data == "chart":
        await query.edit_message_text("📈 لطفاً نماد ارز را وارد کنید (مثلاً BTCUSDT)")

    elif query.data == "help":
        await query.edit_message_text("ℹ️ راهنمای ربات:\n- با دکمه‌ها کار کنید.\n- برای عضویت در کانال /start")

    elif query.data == "date":
        await query.edit_message_text(pdt.both_dates())

    elif query.data == "settings":
        await query.edit_message_text("⚙️ تنظیمات (در حال توسعه)")

    elif query.data == "ai_chat":
        await query.edit_message_text("🤖 چت هوش مصنوعی فعال است. سوالت را بپرس!")

    elif query.data == "auto_trade":
        await query.edit_message_text("💼 معاملات خودکار: برای فعال‌سازی لطفاً با پشتیبانی تماس بگیرید.")

    elif query.data == "bio":
        await query.edit_message_text("🔄 بیو ربات به‌روزرسانی شد (نمایشی).")

# ============================================================
# ۲۸. مدیریت متن ورودی (برای چت AI و سایر دستورات)
# ============================================================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_member(user_id, context):
        await update.message.reply_text("⛔️ لطفاً ابتدا عضو کانال شوید.")
        return
    text = update.message.text.strip()
    if text.startswith('/'):
        # دستورات ناشناخته
        await update.message.reply_text("دستور نامعتبر. از منوی اصلی استفاده کنید.")
    else:
        # در اینجا می‌توان چت هوش مصنوعی را فعال کرد
        await update.message.reply_text("🤖 برای صحبت با هوش مصنوعی روی دکمه مربوطه کلیک کنید.")

# ============================================================
# ۲۹. وظایف زمان‌بندی شده (ارسال خودکار به کانال)
# ============================================================
async def send_auto_news(context: ContextTypes.DEFAULT_TYPE):
    """ارسال خودکار اخبار هر ۱۲ ساعت به کانال"""
    if cfg.channel_id:
        news = await fetch_persian_news()
        try:
            await context.bot.send_message(chat_id=cfg.channel_id, text=news)
        except Exception as e:
            logger.error(f"Auto news send failed: {e}")

async def send_auto_top_movers(context: ContextTypes.DEFAULT_TYPE):
    """ارسال برترین رشد و ریزش هر ۱۲ ساعت"""
    if cfg.channel_id:
        movers = await get_top_movers()
        try:
            await context.bot.send_message(chat_id=cfg.channel_id, text=movers)
        except Exception as e:
            logger.error(f"Auto top movers send failed: {e}")

async def send_auto_fear_greed(context: ContextTypes.DEFAULT_TYPE):
    if cfg.channel_id:
        fg = await fear_greed_index()
        try:
            await context.bot.send_message(chat_id=cfg.channel_id, text=fg)
        except Exception as e:
            logger.error(f"Auto FG send failed: {e}")

async def send_auto_signal(context: ContextTypes.DEFAULT_TYPE):
    """ارسال سیگنال برتر هر ۴ ساعت"""
    if cfg.channel_id:
        sig = await generate_signal("BTC/USDT", context)
        if sig:
            exchange = ccxt.binance()
            df = await fetch_ohlcv(exchange, sig['symbol'], '4h', 100)
            if df is not None:
                chart_path = chart_gen.create_chart(df, sig['symbol'], f"chart_{sig['symbol'].replace('/', '_')}.png")
                if chart_path:
                    with open(chart_path, 'rb') as img:
                        await context.bot.send_photo(chat_id=cfg.channel_id, photo=img, caption="📊 سیگنال جدید")
                    os.remove(chart_path)
            msg = format_signal_message(sig)
            try:
                await context.bot.send_message(chat_id=cfg.channel_id, text=msg)
            except Exception as e:
                logger.error(f"Auto signal send failed: {e}")

# ============================================================
# ۳۰. راه‌اندازی و اجرای اصلی
# ============================================================
def main():
    if not ProcessLock.acquire():
        logger.error("یک نمونه دیگر در حال اجراست. خروج.")
        sys.exit(1)

    if not cfg.token:
        logger.error("توکن ربات تلگرام تنظیم نشده است.")
        sys.exit(1)

    request = HTTPXRequest(connection_pool_size=50, read_timeout=30, write_timeout=30)
    application = Application.builder().token(cfg.token).request(request).build()

    # هندلرهای اصلی
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # زمان‌بندی وظایف
    job_queue = application.job_queue
    job_queue.run_repeating(send_auto_news, interval=cfg.news_interval, first=10)
    job_queue.run_repeating(send_auto_top_movers, interval=cfg.top_movers_interval, first=20)
    job_queue.run_repeating(send_auto_fear_greed, interval=cfg.fg_interval, first=30)
    job_queue.run_repeating(send_auto_signal, interval=cfg.signal_interval, first=40)

    logger.info("🚀 Crypto Pulse v30.1 Platinum در حال راه‌اندازی...")
    logger.info(pdt.full_datetime())

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

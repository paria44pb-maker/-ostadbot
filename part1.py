"""
🦅 OstadBot v8.0 | Ultimate Professional Trading Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
سازنده: @Amir92aa
کانال: @CryptoPulse606
شماره کارت: 6063-7311-9625-4479
به نام: بهمرد
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ════════════════════════════════════════
# SECTION 1: IMPORTS
# ════════════════════════════════════════
import os, sys, json, time, hmac, hashlib, asyncio, logging, re, math, base64, uuid, random, traceback
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union, Callable, Coroutine
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict, deque
from enum import Enum
from functools import wraps, partial
from pathlib import Path

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False
    import sqlite3

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, StateFilter, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    Update, BotCommand, BotCommandScopeDefault, ReplyKeyboardMarkup,
    KeyboardButton, WebAppInfo, InputFile, BufferedInputFile,
    ReplyKeyboardRemove, ForceReply, ChatMemberUpdated
)
from aiogram.enums import ParseMode, ChatAction, ChatType, ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError

from groq import Groq, RateLimitError as GroqRateLimitError
from groq import APIStatusError as GroqAPIError, APIConnectionError as GroqConnectionError

# ════════════════════════════════════════
# SECTION 2: LOGGING CONFIGURATION
# ════════════════════════════════════════
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ostadbot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("OstadBot")

# ════════════════════════════════════════
# SECTION 3: CONFIGURATION MANAGER
# ════════════════════════════════════════
class ConfigManager:
    """Advanced configuration manager with validation and caching"""
    
    _cache: Dict[str, Any] = {}
    _initialized: bool = False
    
    @classmethod
    def init(cls):
        if cls._initialized:
            return
        cls._cache = {}
        cls._initialized = True
    
    @classmethod
    def get_str(cls, key: str, default: str = "") -> str:
        if key in cls._cache:
            return cls._cache[key]
        val = os.getenv(key, default)
        cls._cache[key] = val
        return val
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        if key in cls._cache:
            return cls._cache[key]
        try:
            val = int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            val = default
        cls._cache[key] = val
        return val
    
    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        if key in cls._cache:
            return cls._cache[key]
        try:
            val = float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            val = default
        cls._cache[key] = val
        return val
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        if key in cls._cache:
            return cls._cache[key]
        val = os.getenv(key, str(default)).lower()
        result = val in ("true", "1", "yes", "on")
        cls._cache[key] = result
        return result
    
    @classmethod
    def get_list(cls, key: str, default: str = "", separator: str = ",") -> List[int]:
        if key in cls._cache:
            return cls._cache[key]
        val = os.getenv(key, default)
        if not val:
            return []
        try:
            result = [int(x.strip()) for x in val.split(separator) if x.strip().isdigit()]
        except (ValueError, TypeError):
            result = []
        cls._cache[key] = result
        return result
    
    @classmethod
    def get_json(cls, key: str, default: dict = None) -> dict:
        if key in cls._cache:
            return cls._cache[key]
        val = os.getenv(key, "")
        if not val:
            return default or {}
        try:
            result = json.loads(val)
        except json.JSONDecodeError:
            result = default or {}
        cls._cache[key] = result
        return result
    
    @classmethod
    def clear_cache(cls):
        cls._cache.clear()
        cls._initialized = False

ConfigManager.init()
cfg = ConfigManager()

# ════════════════════════════════════════
# SECTION 4: APPLICATION CONSTANTS
# ════════════════════════════════════════
BOT_TOKEN = cfg.get_str("BOT_TOKEN")
WEBHOOK_URL = cfg.get_str("WEBHOOK_URL")
WEBHOOK_SECRET = cfg.get_str("WEBHOOK_SECRET", "ostadbot_secret_2024")
GROQ_API_KEY = cfg.get_str("GROQ_API_KEY")
DATABASE_PATH = cfg.get_str("DATABASE_PATH", "ostadbot.db")
PORT = cfg.get_int("PORT", 8080)
ADMIN_IDS = cfg.get_list("ADMIN_IDS")
ENVIRONMENT = cfg.get_str("ENVIRONMENT", "production")
LOG_LEVEL = cfg.get_str("LOG_LEVEL", "INFO")

APP_NAME = "OstadBot"
APP_VERSION = "8.0.0"
APP_BUILD = "2026.06.28"
CREATOR_USERNAME = "@Amir92aa"
CHANNEL_USERNAME = "@CryptoPulse606"
CARD_NUMBER = "6063-7311-9625-4479"
CARD_HOLDER = "بهمرد"
SUPPORT_CONTACT = "@Amir92aa"

# ════════════════════════════════════════
# SECTION 5: BUSINESS CONFIGURATION
# ════════════════════════════════════════
class PlanType(Enum):
    FREE = "free"
    VIP = "vip"
    PRO = "pro"
    ELITE = "elite"

PLANS = {
    PlanType.FREE.value: {
        "name": "رایگان 🆓",
        "name_en": "Free",
        "price": 0,
        "price_usd": 0,
        "days": 0,
        "ai_daily_limit": 5,
        "max_alerts": 2,
        "max_watchlist": 5,
        "max_signals_daily": 1,
        "features": [
            "۵ سوال هوش مصنوعی در روز",
            "۲ هشدار قیمت",
            "واچ‌لیست ۵ تایی",
            "تحلیل پایه بازار"
        ],
        "color": "#808080",
        "icon": "🆓"
    },
    PlanType.VIP.value: {
        "name": "VIP 👑",
        "name_en": "VIP",
        "price": 199000,
        "price_usd": 5,
        "days": 30,
        "ai_daily_limit": 50,
        "max_alerts": 15,
        "max_watchlist": 20,
        "max_signals_daily": 5,
        "features": [
            "۵۰ سوال هوش مصنوعی در روز",
            "۱۵ هشدار قیمت",
            "واچ‌لیست ۲۰ تایی",
            "۵ سیگنال VIP در روز",
            "تحلیل تکنیکال پیشرفته",
            "پشتیبانی سریع"
        ],
        "color": "#FFD700",
        "icon": "👑"
    },
    PlanType.PRO.value: {
        "name": "PRO 💎",
        "name_en": "PRO",
        "price": 399000,
        "price_usd": 10,
        "days": 30,
        "ai_daily_limit": 200,
        "max_alerts": 50,
        "max_watchlist": 50,
        "max_signals_daily": 15,
        "features": [
            "۲۰۰ سوال هوش مصنوعی در روز",
            "۵۰ هشدار قیمت",
            "واچ‌لیست ۵۰ تایی",
            "۱۵ سیگنال PRO در روز",
            "کپی تریدینگ",
            "گزارش روزانه بازار",
            "پشتیبانی VIP"
        ],
        "color": "#4169E1",
        "icon": "💎"
    },
    PlanType.ELITE.value: {
        "name": "ELITE 👑💎",
        "name_en": "ELITE",
        "price": 999000,
        "price_usd": 25,
        "days": 90,
        "ai_daily_limit": 999999,
        "max_alerts": 999,
        "max_watchlist": 999,
        "max_signals_daily": 999,
        "features": [
            "تحلیل نامحدود هوش مصنوعی",
            "هشدار نامحدود",
            "واچ‌لیست نامحدود",
            "سیگنال نامحدود",
            "مشاوره خصوصی",
            "پشتیبانی ۲۴/۷"
        ],
        "color": "#FF4500",
        "icon": "👑💎"
    }
}

WELCOME_BONUS_DAYS = 3
REFERRAL_COMMISSION_PERCENT = 20
FREE_DAILY_AI = 5
GROQ_RPM_LIMIT = 25
GROQ_TPM_LIMIT = 5000

# ════════════════════════════════════════
# SECTION 6: TRADING SYMBOLS & DATA
# ════════════════════════════════════════
DEFAULT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "AVAXUSDT",
    "LINKUSDT", "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT",
]

SYMBOL_NAMES_PERSIAN = {
    "BTC": "بیت‌کوین", "ETH": "اتریوم", "SOL": "سولانا",
    "BNB": "بایننس کوین", "XRP": "ریپل", "ADA": "کاردانو",
    "DOGE": "دوج کوین", "DOT": "پولکادات", "MATIC": "پالیگان",
    "AVAX": "آوالانچ", "LINK": "چین لینک", "UNI": "یونی سواپ",
    "ATOM": "کازماس", "LTC": "لایت کوین", "ETC": "اتریوم کلاسیک",
}

TIMEFRAMES = {
    "1m": "۱ دقیقه", "5m": "۵ دقیقه", "15m": "۱۵ دقیقه",
    "30m": "۳۰ دقیقه", "1h": "۱ ساعت", "4h": "۴ ساعت",
    "1d": "روزانه", "1w": "هفتگی", "1M": "ماهانه",
}

# ════════════════════════════════════════
# SECTION 7: EMOJI BANK (COMPLETE)
# ════════════════════════════════════════
class EmojiBank:
    """Complete emoji collection for professional UI"""
    
    # Market & Trading
    ROCKET = "🚀"; FIRE = "🔥"; MONEY = "💰"; COIN = "🪙"
    CHART = "📊"; CHART_UP = "📈"; CHART_DOWN = "📉"
    CANDLE_GREEN = "🟢"; CANDLE_RED = "🔴"; CANDLE_YELLOW = "🟡"; CANDLE_ORANGE = "🟠"
    BULL = "🐂"; BEAR = "🐻"; TARGET = "🎯"
    CRYSTAL = "💠"; DIAMOND = "💎"; GEM = "💎"
    STAR = "⭐"; SPARKLES = "✨"; GLOW = "🌟"
    CROWN = "👑"; RING = "💍"
    
    # Status
    CHECK = "✅"; CHECK2 = "☑️"; CROSS = "❌"; CROSS2 = "✖️"
    WARNING = "⚠️"; INFO = "ℹ️"; QUESTION = "❓"
    LOCK = "🔒"; UNLOCK = "🔓"; KEY = "🔑"; KEY2 = "🗝️"
    HOURGLASS = "⏳"; HOURGLASS_DONE = "⌛"
    LOADING = "🔄"; SYNC = "🔄"
    
    # Users & VIP
    ROBOT = "🤖"; BRAIN = "🧠"; EYE = "👁️"; EAR = "👂"
    COOL = "😎"; WOW = "😍"; LOVE = "🥰"; THINK = "🤔"
    PRAY = "🙏"; CLAP = "👏"; MUSCLE = "💪"; OK = "👌"
    PERSON = "👤"; PEOPLE = "👥"
    
    # UI Elements
    HOME = "🏠"; BACK = "🔙"; FORWARD = "🔜"; SETTINGS = "⚙️"
    SEARCH = "🔍"; PLUS = "➕"; MINUS = "➖"; REFRESH = "🔄"
    BELL = "🔔"; BELL_OFF = "🔕"; MUTE = "🔇"; SPEAKER = "🔊"
    ENVELOPE = "📧"; MAIL = "📨"; PHONE = "📱"; MOBILE = "📲"
    GLOBE = "🌍"; WORLD = "🌎"; MAP = "🗺️"; COMPASS = "🧭"
    CALENDAR = "📅"; CLOCK = "🕐"; WATCH = "⌚"; ALARM = "⏰"
    STOPWATCH = "⏱️"; TIMER = "⏲️"
    
    # Celebration
    GIFT = "🎁"; PARTY = "🎉"; BALLOON = "🎈"; CONFETTI = "🎊"
    TROPHY = "🏆"; MEDAL = "🥇"; MEDAL2 = "🥈"; MEDAL3 = "🥉"
    RIBBON = "🎀"; FLOWER = "🌸"; ROSE = "🌹"
    
    # Power
    LIGHTNING = "⚡"; ZAP = "⚡"; FLASH = "💥"; EXPLOSION = "💥"
    BOMB = "💣"; DROPLET = "💧"; SNOWFLAKE = "❄️"
    
    # Protection
    SHIELD = "🛡️"; SWORD = "⚔️"; CROSSED_SWORDS = "⚔️"
    SCALE = "⚖️"; MAGNET = "🧲"; CHAIN = "🔗"; LINK = "🔗"
    
    # Science
    BULB = "💡"; MICROSCOPE = "🔬"; TELESCOPE = "🔭"
    SATELLITE = "🛰️"; GEAR = "⚙️"; HAMMER = "🔨"; WRENCH = "🔧"
    
    # Weather
    SUN = "☀️"; MOON = "🌙"; CLOUD = "☁️"; RAIN = "🌧️"
    SNOW = "❄️"; UMBRELLA = "☂️"; RAINBOW = "🌈"
    THERMOMETER = "🌡️"; WIND = "💨"; VOLCANO = "🌋"
    MOUNTAIN = "🏔️"; OCEAN = "🌊"; DESERT = "🏜️"; ISLAND = "🏝️"
    
    # Finance
    CARD = "💳"; BANK = "🏦"; ATM = "🏧"; WALLET = "👛"
    PIGGY = "🐷"; BILL = "💵"; BILLS = "💸"; RECEIPT = "🧾"
    CALCULATOR = "🔢"; ABACUS = "🧮"
    
    # Arrows
    UP = "⬆️"; DOWN = "⬇️"; RIGHT = "➡️"; LEFT = "⬅️"
    UP_RIGHT = "↗️"; UP_LEFT = "↖️"; DOWN_RIGHT = "↘️"; DOWN_LEFT = "↙️"
    POINT_UP = "☝️"; POINT_DOWN = "👇"; POINT_RIGHT = "👉"; POINT_LEFT = "👈"
    TOP = "🔝"; NEW = "🆕"; FREE = "🆓"; OK_BTN = "🆗"; COOL_BTN = "🆒"
    
    # Numbers
    N0 = "0️⃣"; N1 = "1️⃣"; N2 = "2️⃣"; N3 = "3️⃣"; N4 = "4️⃣"
    N5 = "5️⃣"; N6 = "6️⃣"; N7 = "7️⃣"; N8 = "8️⃣"; N9 = "9️⃣"; N10 = "🔟"
    WAVE = "👋"
    @classmethod
    def number(cls, n: int) -> str:
        emojis = [cls.N0, cls.N1, cls.N2, cls.N3, cls.N4, cls.N5, cls.N6, cls.N7, cls.N8, cls.N9, cls.N10]
        return emojis[n] if 0 <= n <= 10 else f"#{n}"
    
    @classmethod
    def confidence_stars(cls, confidence: float) -> str:
        stars = max(1, min(5, int(confidence * 5)))
        return "⭐" * stars + "☆" * (5 - stars)
    
    @classmethod
    def plan_icon(cls, plan: str) -> str:
        icons = {"free": cls.FREE, "vip": cls.CROWN, "pro": cls.DIAMOND, "elite": f"{cls.CROWN}{cls.DIAMOND}"}
        return icons.get(plan, cls.FREE)
    
    @classmethod
    def direction_icon(cls, direction: str) -> str:
        d = direction.upper()
        if d in ("LONG", "BUY", "خرید"): return cls.BULL
        if d in ("SHORT", "SELL", "فروش"): return cls.BEAR
        return cls.CHART
    
    @classmethod
    def change_icon(cls, change: float) -> str:
        if change > 0: return cls.CHART_UP
        if change < 0: return cls.CHART_DOWN
        return cls.CHART
    
    @classmethod
    def rsi_status(cls, rsi: float) -> str:
        if rsi < 30: return f"{cls.CANDLE_GREEN} اشباع فروش ({rsi:.1f})"
        if rsi > 70: return f"{cls.CANDLE_RED} اشباع خرید ({rsi:.1f})"
        if rsi > 50: return f"{cls.CANDLE_YELLOW} صعودی ({rsi:.1f})"
        return f"{cls.CANDLE_ORANGE} نزولی ({rsi:.1f})"
    
    @classmethod
    def volume_emoji(cls, ratio: float) -> str:
        if ratio > 2: return "🔥🔥🔥"
        if ratio > 1.5: return "🔥🔥"
        if ratio > 1: return "🔥"
        if ratio < 0.5: return "💤"
        return "📊"
    
    @classmethod
    def trend_icon(cls, trend: str) -> str:
        if "صعودی قوی" in trend: return "🟢🟢"
        if "صعودی" in trend: return "🟢"
        if "نزولی قوی" in trend: return "🔴🔴"
        if "نزولی" in trend: return "🔴"
        return "⚪"

E = EmojiBank()

# ════════════════════════════════════════
# SECTION 8: PERSIAN TEXT TEMPLATES
# ════════════════════════════════════════
class PersianText:
    """Persian text and message templates"""
    
    GREETINGS = {
        "morning": "صبح بخیر ☀️",
        "afternoon": "عصر بخیر 🌤️",
        "evening": "شب بخیر 🌙",
        "night": "نیمه‌شب بخیر 🌙",
        "default": "سلام 👋",
    }
    
    PLAN_NAMES = {
        "free": "رایگان",
        "vip": "VIP",
        "pro": "PRO",
        "elite": "ELITE",
        "banned": "مسدود شده",
    }
    
    RISK_LEVELS = {
        "low": "پایین 🟢",
        "medium": "متوسط 🟡",
        "high": "بالا 🔴",
    }
    
    SIGNAL_DIRECTIONS = {
        "LONG": "خرید 🟢",
        "SHORT": "فروش 🔴",
    }
    
    ALERT_TYPES = {
        "above": "بالاتر از ⬆️",
        "below": "پایین‌تر از ⬇️",
    }
    
    TREND_NAMES = {
        "strong_bullish": "صعودی قوی 🟢",
        "bullish": "صعودی 🟡",
        "neutral": "خنثی ⚪",
        "bearish": "نزولی 🟠",
        "strong_bearish": "نزولی قوی 🔴",
    }
    
    @classmethod
    def greeting(cls, hour: int = None) -> str:
        if hour is None:
            hour = datetime.now().hour
        if hour < 6: return cls.GREETINGS["night"]
        elif hour < 12: return cls.GREETINGS["morning"]
        elif hour < 17: return cls.GREETINGS["afternoon"]
        elif hour < 22: return cls.GREETINGS["evening"]
        return cls.GREETINGS["night"]
    
    @classmethod
    def format_number(cls, number: float, decimals: int = 2) -> str:
        try:
            formatted = f"{number:,.{decimals}f}"
            persian_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
            return formatted.translate(persian_digits)
        except:
            return str(number)
    
    @classmethod
    def format_price(cls, price: float) -> str:
        if price >= 1:
            return f"{price:,.4f}"
        return f"{price:.8f}"
    
    @classmethod
    def format_toman(cls, amount: float) -> str:
        return f"{amount:,.0f} تومان"
    
    @classmethod
    def format_percent(cls, percent: float) -> str:
        emoji = "🟢" if percent > 0 else "🔴" if percent < 0 else "⚪"
        return f"{emoji} {percent:+.2f}%"
    
    @classmethod
    def format_volume(cls, volume: float) -> str:
        if volume >= 1_000_000_000:
            return f"{volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.2f}K"
        return f"{volume:.2f}"

T = PersianText()

# ════════════════════════════════════════
# SECTION 9: TEHRAN TIME ENGINE (FULL)
# ════════════════════════════════════════
class TehranTimeEngine:
    """Advanced Tehran time management system"""
    
    TEHRAN_OFFSET = timedelta(hours=3, minutes=30)
    
    PERSIAN_MONTH_NAMES = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    PERSIAN_DAY_NAMES = [
        "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
    ]
    
    SEASONS = {
        "spring": "بهار 🌸",
        "summer": "تابستان ☀️",
        "autumn": "پاییز 🍂",
        "winter": "زمستان ❄️"
    }
    
    MONTH_DAYS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    
    HOLIDAYS = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 12), (1, 13),
                (3, 14), (3, 15), (4, 13), (6, 15), (8, 22),
                (10, 11), (10, 12), (11, 22), (12, 29)]
    
    @classmethod
    def now(cls) -> datetime:
        return datetime.now(timezone.utc) + cls.TEHRAN_OFFSET
    
    @classmethod
    def timestamp(cls) -> float:
        return cls.now().timestamp()
    
    @classmethod
    def from_timestamp(cls, ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc) + cls.TEHRAN_OFFSET
    
    @classmethod
    def persian_date(cls, dt: datetime = None) -> Tuple[int, int, int]:
        if dt is None:
            dt = cls.now()
        return (cls._persian_year(dt), cls._persian_month(dt), cls._persian_day(dt))
    
    @classmethod
    def _persian_year(cls, dt: datetime) -> int:
        return dt.year - 621 if (dt.month, dt.day) >= (3, 21) else dt.year - 622
    
    @classmethod
    def _persian_month(cls, dt: datetime) -> int:
        if (dt.month, dt.day) >= (3, 21):
            start = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo)
        else:
            start = datetime(dt.year - 1, 3, 21, tzinfo=dt.tzinfo)
        days = (dt - start).days
        for i, md in enumerate(cls.MONTH_DAYS, 1):
            if days < md:
                return i
            days -= md
        return 12
    
    @classmethod
    def _persian_day(cls, dt: datetime) -> int:
        if (dt.month, dt.day) >= (3, 21):
            start = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo)
        else:
            start = datetime(dt.year - 1, 3, 21, tzinfo=dt.tzinfo)
        days = (dt - start).days
        for md in cls.MONTH_DAYS:
            if days < md:
                return days + 1
            days -= md
        return 29
    
    @classmethod
    def format(cls, dt: datetime = None, fmt: str = "full") -> str:
        if dt is None:
            dt = cls.now()
        y, m, d = cls.persian_date(dt)
        
        if fmt == "full":
            return f"{cls.PERSIAN_DAY_NAMES[dt.weekday()]} {d} {cls.PERSIAN_MONTH_NAMES[m-1]} {y} - {dt.strftime('%H:%M:%S')}"
        elif fmt == "time":
            return dt.strftime("%H:%M:%S")
        elif fmt == "time_short":
            return dt.strftime("%H:%M")
        elif fmt == "date":
            return f"{d} {cls.PERSIAN_MONTH_NAMES[m-1]} {y}"
        elif fmt == "date_short":
            return f"{y}/{m:02d}/{d:02d}"
        elif fmt == "datetime_short":
            return f"{y}/{m:02d}/{d:02d} {dt.strftime('%H:%M')}"
        elif fmt == "day_name":
            return cls.PERSIAN_DAY_NAMES[dt.weekday()]
        elif fmt == "relative":
            return cls._relative_time(dt)
        elif fmt == "log":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def _relative_time(cls, dt: datetime) -> str:
        now = cls.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0: return "همین الان"
        if seconds < 10: return "چند لحظه پیش"
        if seconds < 60: return f"{seconds} ثانیه پیش"
        if seconds < 3600: return f"{seconds // 60} دقیقه پیش"
        if seconds < 86400: return f"{seconds // 3600} ساعت پیش"
        if seconds < 604800: return f"{seconds // 86400} روز پیش"
        if seconds < 2592000: return f"{seconds // 604800} هفته پیش"
        return f"{seconds // 2592000} ماه پیش"
    
    @classmethod
    def get_season(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        m = cls._persian_month(dt)
        if m <= 3: return cls.SEASONS["spring"]
        if m <= 6: return cls.SEASONS["summer"]
        if m <= 9: return cls.SEASONS["autumn"]
        return cls.SEASONS["winter"]
    
    @classmethod
    def is_weekend(cls, dt: datetime = None) -> bool:
        if dt is None: dt = cls.now()
        return dt.weekday() == 4
    
    @classmethod
    def is_holiday(cls, dt: datetime = None) -> bool:
        if dt is None: dt = cls.now()
        _, m, d = cls.persian_date(dt)
        return (m, d) in cls.HOLIDAYS or dt.weekday() == 4
    
    @classmethod
    def is_night_time(cls, dt: datetime = None) -> bool:
        if dt is None: dt = cls.now()
        return dt.hour < 6 or dt.hour >= 22
    
    @classmethod
    def trading_session(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        h = dt.hour
        if 3 <= h < 12: return "آسیا 🌏"
        if 12 <= h < 19: return "اروپا 🌍"
        return "آمریکا 🌎"
    
    @classmethod
    def session_details(cls, dt: datetime = None) -> Dict:
        if dt is None: dt = cls.now()
        h = dt.hour
        if 3 <= h < 12: start, end, name = 3, 12, "آسیا 🌏"
        elif 12 <= h < 19: start, end, name = 12, 19, "اروپا 🌍"
        else: start, end, name = 19, 24, "آمریکا 🌎"
        
        elapsed = h - start if h >= start else 0
        remaining = max(0, end - h)
        total = end - start
        progress = round((elapsed / total * 100), 1) if total > 0 else 100
        
        return {
            "name": name, "start": f"{start:02d}:00", "end": f"{end:02d}:00",
            "elapsed": elapsed, "remaining": remaining, "progress": progress
        }
    
    @classmethod
    def greeting(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        return T.greeting(dt.hour)
    
    @classmethod
    def uptime_string(cls, start: datetime) -> str:
        diff = cls.now() - start
        days, hours, minutes = diff.days, diff.seconds // 3600, (diff.seconds % 3600) // 60
        parts = []
        if days > 0: parts.append(f"{days} روز")
        if hours > 0: parts.append(f"{hours} ساعت")
        parts.append(f"{minutes} دقیقه")
        return " و ".join(parts)

TT = TehranTimeEngine()

# ════════════════════════════════════════
# END OF PART 1 - CONTINUE TO PART 2
# ════════════════════════════════════════

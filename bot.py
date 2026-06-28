"""
🦅 CryptoPulse-AI v7.0 | Ultimate Professional 5000 Lines
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
سازنده: @Amir92aa
کانال: @CryptoPulse606
شماره کارت: 6063-7311-9625-4479
به نام: بهمرد
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ═══════════════════════════════════════════════════════════
# SECTION 1: IMPORTS & SETUP
# ═══════════════════════════════════════════════════════════

import os, sys, json, time, hmac, hashlib, asyncio, logging, re, math, base64, uuid, random, traceback
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict, deque
from enum import Enum
from functools import wraps, partial

try:
    import aiosqlite
except ImportError:
    import sqlite3
    class FakeAiosqlite:
        @staticmethod
        async def connect(path):
            return sqlite3.connect(path)
    aiosqlite = FakeAiosqlite()

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pandas as pd
except ImportError:
    pd = None

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, StateFilter, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    Update, BotCommand, BotCommandScopeDefault, ReplyKeyboardMarkup,
    KeyboardButton, WebAppInfo, InputFile, BufferedInputFile,
    ReplyKeyboardRemove, ForceReply
)
from aiogram.enums import ParseMode, ChatAction, ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError

from groq import Groq, RateLimitError as GroqRateLimitError
from groq import APIStatusError as GroqAPIError, APIConnectionError as GroqConnectionError

# ═══════════════════════════════════════════════════════════
# SECTION 2: LOGGING
# ═══════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cryptopulse.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("CryptoPulse-AI")

# ═══════════════════════════════════════════════════════════
# SECTION 3: CONFIGURATION SYSTEM
# ═══════════════════════════════════════════════════════════

class ConfigManager:
    """Advanced configuration manager with validation"""
    
    @staticmethod
    def get_str(key: str, default: str = "") -> str:
        return os.getenv(key, default)
    
    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        val = os.getenv(key, str(default)).lower()
        return val in ("true", "1", "yes", "on")
    
    @staticmethod
    def get_list(key: str, default: str = "", separator: str = ",") -> List[int]:
        val = os.getenv(key, default)
        if not val:
            return []
        try:
            return [int(x.strip()) for x in val.split(separator) if x.strip().isdigit()]
        except:
            return []
    
    @staticmethod
    def get_json(key: str, default: dict = None) -> dict:
        val = os.getenv(key, "")
        if not val:
            return default or {}
        try:
            return json.loads(val)
        except:
            return default or {}

cfg = ConfigManager()

# ═══════════════════════════════════════════════════════════
# SECTION 4: APPLICATION CONSTANTS
# ═══════════════════════════════════════════════════════════

BOT_TOKEN = cfg.get_str("BOT_TOKEN")
WEBHOOK_URL = cfg.get_str("WEBHOOK_URL")
WEBHOOK_SECRET = cfg.get_str("WEBHOOK_SECRET", "cryptopulse_v7_secret")
GROQ_API_KEY = cfg.get_str("GROQ_API_KEY")
DATABASE_PATH = cfg.get_str("DATABASE_PATH", "cryptopulse.db")
PORT = cfg.get_int("PORT", 8080)
ADMIN_IDS = cfg.get_list("ADMIN_IDS")
ENVIRONMENT = cfg.get_str("ENVIRONMENT", "production")
LOG_LEVEL = cfg.get_str("LOG_LEVEL", "INFO")

APP_NAME = "CryptoPulse-AI"
APP_VERSION = "7.0.0"
APP_BUILD = "2026.06.28"
CREATOR_USERNAME = "@Amir92aa"
CHANNEL_USERNAME = "@CryptoPulse606"
CARD_NUMBER = "6063-7311-9625-4479"
CARD_HOLDER = "بهمرد"
SUPPORT_CONTACT = "@Amir92aa"
WEBSITE_URL = "https://t.me/CryptoPulse606"

# ═══════════════════════════════════════════════════════════
# SECTION 5: BUSINESS CONFIGURATION
# ═══════════════════════════════════════════════════════════

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
            "پشتیبانی سریع",
            "گروه VIP"
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
            "تحلیل آنچین",
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
            "مشاوره خصوصی ۱به۱",
            "ربات اختصاصی",
            "API اختصاصی",
            "همه امکانات PRO",
            "پشتیبانی ۲۴/۷"
        ],
        "color": "#FF4500",
        "icon": "👑💎"
    }
}

# ═══════════════════════════════════════════════════════════
# SECTION 6: RATE LIMITS & THRESHOLDS
# ═══════════════════════════════════════════════════════════

RATE_LIMITS = {
    "ai_global_rpm": 25,
    "ai_global_tpm": 5000,
    "ai_per_user_rpm": 3,
    "message_min_interval": 0.5,
    "callback_min_interval": 0.3,
    "max_message_length": 4096,
    "max_callback_data": 64,
}

WELCOME_BONUS_DAYS = 3
REFERRAL_COMMISSION_PERCENT = 20
REFERRAL_LEVEL2_PERCENT = 5
MIN_WITHDRAW_AMOUNT = 100000  # Toman
MAX_WITHDRAW_AMOUNT = 10000000  # Toman

# ═══════════════════════════════════════════════════════════
# SECTION 7: TRADING SYMBOLS
# ═══════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════
# SECTION 8: EMOJI & UI CLASS
# ═══════════════════════════════════════════════════════════

class EmojiBank:
    """Complete emoji collection for professional UI"""
    
    # ── Market & Trading ──
    ROCKET = "🚀"; FIRE = "🔥"; MONEY = "💰"; COIN = "🪙"
    CHART = "📊"; CHART_UP = "📈"; CHART_DOWN = "📉"
    CANDLE_GREEN = "🟢"; CANDLE_RED = "🔴"; CANDLE_YELLOW = "🟡"
    BULL = "🐂"; BEAR = "🐻"; TARGET = "🎯"
    CRYSTAL = "💠"; DIAMOND = "💎"; GEM = "💎"
    STAR = "⭐"; SPARKLES = "✨"; GLOW = "🌟"
    RING = "💍"; CROWN = "👑"
    
    # ── Status ──
    CHECK = "✅"; CHECK2 = "☑️"; CROSS = "❌"; CROSS2 = "✖️"
    WARNING = "⚠️"; INFO = "ℹ️"; QUESTION = "❓"; HELP = "💁"
    LOCK = "🔒"; UNLOCK = "🔓"; KEY = "🔑"; KEY2 = "🗝️"
    HOURGLASS = "⏳"; HOURGLASS_DONE = "⌛"
    LOADING = "🔄"; SYNC = "🔄"
    
    # ── Users & VIP ──
    ROBOT = "🤖"; BRAIN = "🧠"; EYE = "👁️"; EAR = "👂"
    COOL = "😎"; WOW = "😍"; LOVE = "🥰"; THINK = "🤔"
    PRAY = "🙏"; CLAP = "👏"; MUSCLE = "💪"; OK = "👌"
    POOP = "💩"; GHOST = "👻"; ALIEN = "👽"
    BABY = "👶"; OLD = "👴"; PERSON = "👤"; PEOPLE = "👥"
    
    # ── UI Elements ──
    HOME = "🏠"; BACK = "🔙"; FORWARD = "🔜"; SETTINGS = "⚙️"
    SEARCH = "🔍"; PLUS = "➕"; MINUS = "➖"; REFRESH = "🔄"
    BELL = "🔔"; BELL_OFF = "🔕"; MUTE = "🔇"; SPEAKER = "🔊"
    ENVELOPE = "📧"; MAIL = "📨"; PHONE = "📱"; MOBILE = "📲"
    GLOBE = "🌍"; WORLD = "🌎"; MAP = "🗺️"; COMPASS = "🧭"
    CALENDAR = "📅"; CLOCK = "🕐"; WATCH = "⌚"; ALARM = "⏰"
    STOPWATCH = "⏱️"; TIMER = "⏲️"
    
    # ── Celebration ──
    GIFT = "🎁"; PARTY = "🎉"; BALLOON = "🎈"; CONFETTI = "🎊"
    TROPHY = "🏆"; MEDAL = "🥇"; MEDAL2 = "🥈"; MEDAL3 = "🥉"
    RIBBON = "🎀"; FLOWER = "🌸"; ROSE = "🌹"
    
    # ── Energy & Power ──
    LIGHTNING = "⚡"; ZAP = "⚡"; FLASH = "💥"; EXPLOSION = "💥"
    BOMB = "💣"; FIRE2 = "💥"; DROPLET = "💧"; SNOWFLAKE = "❄️"
    
    # ── Protection ──
    SHIELD = "🛡️"; SWORD = "⚔️"; CROSSED_SWORDS = "⚔️"
    SCALE = "⚖️"; MAGNET = "🧲"; CHAIN = "🔗"; LINK = "🔗"
    
    # ── Science & Tech ──
    BULB = "💡"; MICROSCOPE = "🔬"; TELESCOPE = "🔭"
    SATELLITE = "🛰️"; GEAR = "⚙️"; HAMMER = "🔨"; WRENCH = "🔧"
    NUT_BOLT = "🔩"; CHAIN2 = "⛓️"; MAGNET2 = "🧲"
    
    # ── Weather & Nature ──
    SUN = "☀️"; MOON = "🌙"; CLOUD = "☁️"; RAIN = "🌧️"
    SNOW = "❄️"; UMBRELLA = "☂️"; RAINBOW = "🌈"
    THERMOMETER = "🌡️"; WIND = "💨"; VOLCANO = "🌋"
    MOUNTAIN = "🏔️"; OCEAN = "🌊"; DESERT = "🏜️"; ISLAND = "🏝️"
    
    # ── Finance ──
    CARD = "💳"; BANK = "🏦"; ATM = "🏧"; WALLET = "👛"
    PIGGY = "🐷"; BILL = "💵"; BILLS = "💸"; RECEIPT = "🧾"
    CALCULATOR = "🔢"; ABACUS = "🧮"
    
    # ── Arrows ──
    UP = "⬆️"; DOWN = "⬇️"; RIGHT = "➡️"; LEFT = "⬅️"
    UP_RIGHT = "↗️"; UP_LEFT = "↖️"; DOWN_RIGHT = "↘️"; DOWN_LEFT = "↙️"
    POINT_UP = "☝️"; POINT_DOWN = "👇"; POINT_RIGHT = "👉"; POINT_LEFT = "👈"
    TOP = "🔝"; NEW = "🆕"; FREE = "🆓"; OK_BTN = "🆗"; COOL_BTN = "🆒"
    
    # ── Numbers ──
    N0 = "0️⃣"; N1 = "1️⃣"; N2 = "2️⃣"; N3 = "3️⃣"; N4 = "4️⃣"
    N5 = "5️⃣"; N6 = "6️⃣"; N7 = "7️⃣"; N8 = "8️⃣"; N9 = "9️⃣"; N10 = "🔟"
    
    @classmethod
    def number(cls, n: int) -> str:
        emojis = [cls.N0, cls.N1, cls.N2, cls.N3, cls.N4, cls.N5, cls.N6, cls.N7, cls.N8, cls.N9, cls.N10]
        if 0 <= n <= 10:
            return emojis[n]
        return f"#{n}"
    
    @classmethod
    def confidence_stars(cls, confidence: float) -> str:
        stars = int(confidence * 5)
        return "⭐" * stars + "☆" * (5 - stars)
    
    @classmethod
    def plan_icon(cls, plan: str) -> str:
        icons = {"free": cls.FREE, "vip": cls.CROWN, "pro": cls.DIAMOND, "elite": f"{cls.CROWN}{cls.DIAMOND}"}
        return icons.get(plan, cls.FREE)
    
    @classmethod
    def direction_icon(cls, direction: str) -> str:
        if direction.upper() in ("LONG", "BUY", "خرید"): return cls.BULL
        elif direction.upper() in ("SHORT", "SELL", "فروش"): return cls.BEAR
        return cls.CHART
    
    @classmethod
    def change_icon(cls, change: float) -> str:
        if change > 0: return cls.CHART_UP
        elif change < 0: return cls.CHART_DOWN
        return cls.CHART
    
    @classmethod
    def rsi_status(cls, rsi: float) -> str:
        if rsi < 30: return f"{cls.CANDLE_GREEN} اشباع فروش ({rsi:.1f})"
        elif rsi > 70: return f"{cls.CANDLE_RED} اشباع خرید ({rsi:.1f})"
        elif rsi > 50: return f"{cls.CANDLE_YELLOW} صعودی ({rsi:.1f})"
        return f"🟠 نزولی ({rsi:.1f})"
    
    @classmethod
    def volume_emoji(cls, ratio: float) -> str:
        if ratio > 2: return "🔥🔥🔥"
        elif ratio > 1.5: return "🔥🔥"
        elif ratio > 1: return "🔥"
        elif ratio < 0.5: return "💤"
        return "📊"

E = EmojiBank()

# ═══════════════════════════════════════════════════════════
# SECTION 9: PERSIAN TEXT TEMPLATES
# ═══════════════════════════════════════════════════════════

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
        "BUY": "خرید 🟢",
        "SELL": "فروش 🔴",
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
        """Format number with Persian digits"""
        try:
            formatted = f"{number:,.{decimals}f}"
            # Convert to Persian digits
            persian_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
            return formatted.translate(persian_digits)
        except:
            return str(number)
    
    @classmethod
    def format_price(cls, price: float) -> str:
        if price >= 1:
            return cls.format_number(price, 4)
        return cls.format_number(price, 8)
    
    @classmethod
    def format_toman(cls, amount: float) -> str:
        return f"{cls.format_number(amount, 0)} تومان"
    
    @classmethod
    def format_percent(cls, percent: float) -> str:
        emoji = "🟢" if percent > 0 else "🔴" if percent < 0 else "⚪"
        return f"{emoji} {cls.format_number(percent, 2)}%"
    
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

# ═══════════════════════════════════════════════════════════
# SECTION 10: TEHRAN TIME ENGINE (ADVANCED)
# ═══════════════════════════════════════════════════════════

class TehranTimeEngine:
    """
    Advanced Tehran time management system.
    Supports Persian calendar, trading sessions, and relative time.
    """
    
    TEHRAN_OFFSET = timedelta(hours=3, minutes=30)
    
    PERSIAN_MONTH_NAMES = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    PERSIAN_DAY_NAMES = [
        "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
    ]
    
    PERSIAN_DAY_NAMES_SHORT = ["۲ش", "۳ش", "۴ش", "۵ش", "ج", "ش", "۱ش"]
    
    SEASONS = {
        "spring": "بهار 🌸",
        "summer": "تابستان ☀️",
        "autumn": "پاییز 🍂",
        "winter": "زمستان ❄️"
    }
    
    MONTH_DAYS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    
    # Holidays (Persian month, day)
    HOLIDAYS = [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 12), (1, 13),
        (3, 14), (3, 15),
        (4, 13),
        (6, 15),
        (8, 22),
        (10, 11), (10, 12),
        (11, 22),
        (12, 29),
    ]
    
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
        """Returns (year, month, day)"""
        if dt is None:
            dt = cls.now()
        y = cls._persian_year(dt)
        m = cls._persian_month(dt)
        d = cls._persian_day(dt)
        return (y, m, d)
    
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
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def _relative_time(cls, dt: datetime) -> str:
        now = cls.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        
        if seconds < 0:
            return "همین الان"
        elif seconds < 10:
            return "چند لحظه پیش"
        elif seconds < 60:
            return f"{seconds} ثانیه پیش"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} دقیقه پیش"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} ساعت پیش"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days} روز پیش"
        elif seconds < 2592000:
            weeks = seconds // 604800
            return f"{weeks} هفته پیش"
        elif seconds < 31536000:
            months = seconds // 2592000
            return f"{months} ماه پیش"
        else:
            years = seconds // 31536000
            return f"{years} سال پیش"
    
    @classmethod
    def get_season(cls, dt: datetime = None) -> str:
        if dt is None:
            dt = cls.now()
        m = cls._persian_month(dt)
        if m <= 3: return cls.SEASONS["spring"]
        elif m <= 6: return cls.SEASONS["summer"]
        elif m <= 9: return cls.SEASONS["autumn"]
        return cls.SEASONS["winter"]
    
    @classmethod
    def is_weekend(cls, dt: datetime = None) -> bool:
        if dt is None:
            dt = cls.now()
        return dt.weekday() == 4
    
    @classmethod
    def is_holiday(cls, dt: datetime = None) -> bool:
        if dt is None:
            dt = cls.now()
        _, m, d = cls.persian_date(dt)
        return (m, d) in cls.HOLIDAYS or dt.weekday() == 4
    
    @classmethod
    def is_night_time(cls, dt: datetime = None) -> bool:
        if dt is None:
            dt = cls.now()
        return dt.hour < 6 or dt.hour >= 22
    
    @classmethod
    def trading_session(cls, dt: datetime = None) -> str:
        if dt is None:
            dt = cls.now()
        h = dt.hour
        if 3 <= h < 12: return "آسیا 🌏"
        elif 12 <= h < 19: return "اروپا 🌍"
        else: return "آمریکا 🌎"
    
    @classmethod
    def session_details(cls, dt: datetime = None) -> Dict:
        if dt is None:
            dt = cls.now()
        h = dt.hour
        if 3 <= h < 12:
            start, end = 3, 12
            name = "آسیا 🌏"
        elif 12 <= h < 19:
            start, end = 12, 19
            name = "اروپا 🌍"
        else:
            start, end = 19, 24
            name = "آمریکا 🌎"
        
        elapsed = h - start
        remaining = end - h
        total = end - start
        progress = (elapsed / total * 100) if total > 0 else 100
        
        return {
            "name": name,
            "start": f"{start:02d}:00",
            "end": f"{end:02d}:00",
            "elapsed": elapsed,
            "remaining": remaining,
            "progress": round(progress, 1)
        }
    
    @classmethod
    def greeting(cls, dt: datetime = None) -> str:
        if dt is None:
            dt = cls.now()
        return T.greeting(dt.hour)
    
    @classmethod
    def uptime_string(cls, start: datetime) -> str:
        diff = cls.now() - start
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        parts = []
        if days > 0: parts.append(f"{days} روز")
        if hours > 0: parts.append(f"{hours} ساعت")
        parts.append(f"{minutes} دقیقه")
        return " و ".join(parts)
    
    @classmethod
    def next_candle_close(cls, timeframe: str) -> str:
        now = cls.now()
        if timeframe == "1m":
            n = now + timedelta(minutes=1)
            return n.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        elif timeframe == "5m":
            n = now + timedelta(minutes=5 - now.minute % 5)
            return n.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        elif timeframe == "15m":
            n = now + timedelta(minutes=15 - now.minute % 15)
            return n.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        elif timeframe == "1h":
            n = now + timedelta(hours=1)
            return n.replace(minute=0, second=0, microsecond=0).strftime("%H:%M:%S")
        elif timeframe == "4h":
            nh = ((now.hour // 4) + 1) * 4
            if nh >= 24:
                n = now + timedelta(days=1)
                return n.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%H:%M")
            return now.replace(hour=nh, minute=0, second=0, microsecond=0).strftime("%H:%M:%S")
        elif timeframe == "1d":
            n = now + timedelta(days=1)
            return n.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%H:%M")
        return "..."

TT = TehranTimeEngine()

# ═══════════════════════════════════════════════════════════
# CONTINUED IN PART 2...
# ═══════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════
# SECTION 11: DATABASE ENGINE (ADVANCED)
# ═══════════════════════════════════════════════════════════

class DatabaseEngine:
    """
    High-performance async SQLite database manager.
    Implements connection pooling, WAL mode, and comprehensive schema.
    """
    
    SCHEMA_VERSION = 7
    
    FULL_SCHEMA = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        language TEXT DEFAULT 'fa',
        plan TEXT DEFAULT 'free',
        plan_until REAL DEFAULT 0,
        welcome_bonus INTEGER DEFAULT 0,
        risk_level TEXT DEFAULT 'medium',
        total_paid REAL DEFAULT 0,
        total_earnings REAL DEFAULT 0,
        referral_code TEXT DEFAULT '',
        referred_by INTEGER DEFAULT 0,
        total_referrals INTEGER DEFAULT 0,
        referral_earnings REAL DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        notifications_enabled INTEGER DEFAULT 1,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        last_active REAL DEFAULT (strftime('%s', 'now')),
        metadata TEXT DEFAULT '{}'
    );
    
    -- User state for rate limiting
    CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER PRIMARY KEY,
        daily_ai_count INTEGER DEFAULT 0,
        total_ai_count INTEGER DEFAULT 0,
        daily_signal_count INTEGER DEFAULT 0,
        total_signal_count INTEGER DEFAULT 0,
        last_ai_at REAL DEFAULT 0,
        last_signal_at REAL DEFAULT 0,
        last_reset_day TEXT DEFAULT '',
        last_active_at REAL DEFAULT 0
    );
    
    -- Watchlists
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        note TEXT DEFAULT '',
        target_price REAL DEFAULT 0,
        added_at REAL DEFAULT (strftime('%s', 'now')),
        UNIQUE(user_id, symbol)
    );
    
    -- Price alerts
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        target_price REAL NOT NULL,
        alert_type TEXT DEFAULT 'above',
        note TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        triggered INTEGER DEFAULT 0,
        triggered_at REAL DEFAULT 0,
        notification_sent INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Trading signals
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        direction TEXT NOT NULL,
        entry_price REAL NOT NULL,
        stop_loss REAL NOT NULL,
        take_profit1 REAL,
        take_profit2 REAL,
        take_profit3 REAL,
        confidence REAL DEFAULT 0.5,
        timeframe TEXT DEFAULT '4h',
        analysis_type TEXT DEFAULT 'ai',
        status TEXT DEFAULT 'active',
        result TEXT DEFAULT '',
        profit_percent REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        closed_at REAL DEFAULT 0
    );
    
    -- Payments
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'card',
        status TEXT DEFAULT 'pending',
        receipt_file_id TEXT DEFAULT '',
        receipt_message_id INTEGER DEFAULT 0,
        admin_note TEXT DEFAULT '',
        transaction_id TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0,
        processed_by INTEGER DEFAULT 0
    );
    
    -- AI conversations
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        context TEXT DEFAULT '',
        tokens_used INTEGER DEFAULT 0,
        model TEXT DEFAULT 'llama-3.3-70b',
        response_time REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Referrals
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_id INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        earnings REAL DEFAULT 0,
        level INTEGER DEFAULT 1,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Withdrawals
    CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        wallet_address TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        admin_note TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0
    );
    
    -- Bot settings
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT DEFAULT '',
        updated_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Scheduled tasks
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL,
        task_data TEXT DEFAULT '{}',
        status TEXT DEFAULT 'pending',
        scheduled_at REAL DEFAULT 0,
        executed_at REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- System logs
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 0,
        action TEXT NOT NULL,
        level TEXT DEFAULT 'INFO',
        details TEXT DEFAULT '',
        ip_address TEXT DEFAULT '',
        user_agent TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Broadcast messages
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_text TEXT NOT NULL,
        target_plan TEXT DEFAULT 'all',
        status TEXT DEFAULT 'pending',
        sent_count INTEGER DEFAULT 0,
        total_count INTEGER DEFAULT 0,
        created_by INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        sent_at REAL DEFAULT 0
    );
    
    -- Performance indexes
    CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);
    CREATE INDEX IF NOT EXISTS idx_users_referrer ON users(referred_by);
    CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(user_id, active);
    CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
    CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
    CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
    CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
    CREATE INDEX IF NOT EXISTS idx_logs_action ON logs(action);
    CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at);
    CREATE INDEX IF NOT EXISTS idx_ai_conv_user ON ai_conversations(user_id);
    CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlists(user_id);
    CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON withdrawals(status);
    """
    
    def __init__(self, db_path: str = "cryptopulse.db"):
        self.db_path = db_path
        self._write_lock = asyncio.Lock()
        self._connection_pool = []
        self._max_connections = 10
    
    async def initialize(self) -> bool:
        """Initialize database with full schema and optimizations"""
        try:
            async with self._write_lock:
                async with aiosqlite.connect(self.db_path) as conn:
                    # Performance optimizations
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=-16000")
                    await conn.execute("PRAGMA foreign_keys=ON")
                    await conn.execute("PRAGMA busy_timeout=5000")
                    await conn.execute("PRAGMA temp_store=MEMORY")
                    await conn.execute("PRAGMA mmap_size=268435456")
                    
                    # Execute full schema
                    await conn.executescript(self.FULL_SCHEMA)
                    
                    # Track schema version
                    await conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER, applied_at REAL)")
                    cursor = await conn.execute("SELECT MAX(version) FROM schema_version")
                    row = await cursor.fetchone()
                    current_version = row[0] if row and row[0] else 0
                    
                    if current_version < self.SCHEMA_VERSION:
                        await conn.execute(
                            "INSERT INTO schema_version(version, applied_at) VALUES(?, ?)",
                            (self.SCHEMA_VERSION, time.time())
                        )
                    
                    await conn.commit()
                
                logger.info(f"Database initialized (v{self.SCHEMA_VERSION}): {self.db_path}")
                return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}\n{traceback.format_exc()}")
            raise
    
    async def execute(self, query: str, params: tuple = ()) -> int:
        """Execute SQL and return lastrowid"""
        async with self._write_lock:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(query, params)
                await conn.commit()
                return cursor.lastrowid
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple SQL statements"""
        async with self._write_lock:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.executemany(query, params_list)
                await conn.commit()
                return len(params_list)
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row as dictionary"""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dictionaries"""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def fetchval(self, query: str, params: tuple = (), default: Any = None) -> Any:
        """Fetch a single value"""
        row = await self.fetchone(query, params)
        return list(row.values())[0] if row else default
    
    async def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        """Count rows in a table"""
        return await self.fetchval(f"SELECT COUNT(*) FROM {table} WHERE {where}", params, 0)
    
    async def exists(self, table: str, where: str = "1=1", params: tuple = ()) -> bool:
        """Check if any rows exist"""
        return await self.count(table, where, params) > 0
    
    # ── User Operations ──
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get complete user data"""
        return await self.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    async def upsert_user(self, user_id: int, username: str = "", full_name: str = "") -> None:
        """Create or update user"""
        now = time.time()
        await self.execute("""
            INSERT INTO users(user_id, username, full_name, last_active)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(NULLIF(?, ''), users.username),
                full_name = COALESCE(NULLIF(?, ''), users.full_name),
                last_active = ?
        """, (user_id, username, full_name, now, username, full_name, now))
        
        await self.execute(
            "INSERT OR IGNORE INTO user_state(user_id, last_reset_day) VALUES(?, date('now'))",
            (user_id,)
        )
    
    async def get_user_plan(self, user_id: int) -> str:
        """Get effective user plan"""
        user = await self.get_user(user_id)
        if not user:
            return PlanType.FREE.value
        if user.get('is_banned'):
            return "banned"
        if user['plan'] in (PlanType.VIP.value, PlanType.PRO.value, PlanType.ELITE.value):
            if user.get('plan_until') and time.time() < user['plan_until']:
                return user['plan']
        return PlanType.FREE.value
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user has premium access"""
        plan = await self.get_user_plan(user_id)
        return plan not in (PlanType.FREE.value, "banned")
    
    async def set_user_plan(self, user_id: int, plan: str, days: int = 30) -> None:
        """Set user subscription plan"""
        plan_until = time.time() + (days * 86400)
        await self.execute(
            "UPDATE users SET plan = ?, plan_until = ? WHERE user_id = ?",
            (plan, plan_until, user_id)
        )
        await self.log(user_id, f"plan_changed", f"Plan: {plan}, Days: {days}")
    
    async def get_ai_limit(self, user_id: int) -> int:
        """Get user's daily AI limit"""
        plan = await self.get_user_plan(user_id)
        plan_config = PLANS.get(plan, PLANS[PlanType.FREE.value])
        return plan_config.get("ai_daily_limit", FREE_DAILY_AI)
    
    async def get_ai_usage(self, user_id: int) -> int:
        """Get today's AI usage count"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        state = await self.fetchone("SELECT * FROM user_state WHERE user_id = ?", (user_id,))
        
        if not state:
            await self.execute(
                "INSERT OR IGNORE INTO user_state(user_id, last_reset_day) VALUES(?, ?)",
                (user_id, today)
            )
            return 0
        
        if state.get('last_reset_day') != today:
            await self.execute(
                "UPDATE user_state SET daily_ai_count = 0, last_reset_day = ? WHERE user_id = ?",
                (today, user_id)
            )
            return 0
        
        return state.get('daily_ai_count', 0)
    
    async def increment_ai_usage(self, user_id: int) -> int:
        """Increment AI usage counter and return new count"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await self.execute("""
            UPDATE user_state SET
                daily_ai_count = daily_ai_count + 1,
                total_ai_count = total_ai_count + 1,
                last_ai_at = ?,
                last_reset_day = ?
            WHERE user_id = ?
        """, (time.time(), today, user_id))
        return await self.fetchval(
            "SELECT daily_ai_count FROM user_state WHERE user_id = ?",
            (user_id,), 0
        )
    
    async def can_use_ai(self, user_id: int) -> Tuple[bool, int, int]:
        """Check if user can use AI. Returns (can_use, used, limit)"""
        used = await self.get_ai_usage(user_id)
        limit = await self.get_ai_limit(user_id)
        return (used < limit, used, limit)
    
    # ── Payment Operations ──
    
    async def create_payment(self, user_id: int, plan: str, amount: float, method: str = "card") -> int:
        """Create a new payment record"""
        return await self.execute(
            "INSERT INTO payments(user_id, plan, amount, payment_method) VALUES(?, ?, ?, ?)",
            (user_id, plan, amount, method)
        )
    
    async def approve_payment(self, payment_id: int, admin_id: int) -> bool:
        """Approve payment and activate user's plan"""
        payment = await self.fetchone("SELECT * FROM payments WHERE id = ? AND status = 'pending'", (payment_id,))
        if not payment:
            return False
        
        plan_config = PLANS.get(payment['plan'], PLANS[PlanType.VIP.value])
        days = plan_config.get('days', 30)
        
        # Activate plan
        await self.set_user_plan(payment['user_id'], payment['plan'], days)
        
        # Update payment status
        await self.execute(
            "UPDATE payments SET status = 'approved', processed_at = ?, processed_by = ? WHERE id = ?",
            (time.time(), admin_id, payment_id)
        )
        
        # Process referral commission
        user = await self.get_user(payment['user_id'])
        if user and user.get('referred_by') and user['referred_by'] != 0:
            commission = payment['amount'] * (REFERRAL_COMMISSION_PERCENT / 100)
            await self.execute(
                "UPDATE users SET referral_earnings = referral_earnings + ?, total_earnings = total_earnings + ? WHERE user_id = ?",
                (commission, commission, user['referred_by'])
            )
            # Update referral record
            await self.execute(
                "UPDATE referrals SET earnings = earnings + ? WHERE referrer_id = ? AND referred_id = ?",
                (commission, user['referred_by'], payment['user_id'])
            )
        
        await self.log(payment['user_id'], "payment_approved", f"Payment ID: {payment_id}, Plan: {payment['plan']}")
        return True
    
    async def reject_payment(self, payment_id: int, admin_id: int, reason: str = "") -> bool:
        """Reject a payment"""
        await self.execute(
            "UPDATE payments SET status = 'rejected', processed_at = ?, processed_by = ?, admin_note = ? WHERE id = ?",
            (time.time(), admin_id, reason, payment_id)
        )
        payment = await self.fetchone("SELECT * FROM payments WHERE id = ?", (payment_id,))
        if payment:
            await self.log(payment['user_id'], "payment_rejected", f"Payment ID: {payment_id}, Reason: {reason}")
        return True
    
    async def get_pending_payments_count(self) -> int:
        """Get count of pending payments"""
        return await self.count("payments", "status = 'pending'")
    
    # ── Watchlist Operations ──
    
    async def add_to_watchlist(self, user_id: int, symbol: str, note: str = "") -> bool:
        """Add symbol to user's watchlist"""
        max_items = 999 if await self.is_premium(user_id) else 5
        current = await self.count("watchlists", "user_id = ?", (user_id,))
        if current >= max_items:
            return False
        await self.execute(
            "INSERT OR IGNORE INTO watchlists(user_id, symbol, note) VALUES(?, ?, ?)",
            (user_id, symbol.upper(), note)
        )
        return True
    
    async def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """Remove symbol from watchlist"""
        await self.execute(
            "DELETE FROM watchlists WHERE user_id = ? AND symbol = ?",
            (user_id, symbol.upper())
        )
        return True
    
    async def get_watchlist(self, user_id: int) -> List[Dict]:
        """Get user's watchlist"""
        return await self.fetchall(
            "SELECT * FROM watchlists WHERE user_id = ? ORDER BY added_at DESC",
            (user_id,)
        )
    
    # ── Alert Operations ──
    
    async def create_alert(self, user_id: int, symbol: str, target_price: float, alert_type: str = "above") -> int:
        """Create a price alert"""
        return await self.execute(
            "INSERT INTO alerts(user_id, symbol, target_price, alert_type) VALUES(
        # ═══════════════════════════════════════════════════════════
# SECTION 15: FSM STATES
# ═══════════════════════════════════════════════════════════

class BotStates(StatesGroup):
    """Finite State Machine states for bot conversations"""
    # AI
    waiting_for_ai_question = State()
    
    # Payment
    waiting_for_payment_receipt = State()
    waiting_for_payment_amount = State()
    waiting_for_wallet_address = State()
    
    # Custom symbol
    waiting_for_custom_symbol = State()
    
    # Alerts
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()
    waiting_for_alert_type = State()
    
    # Feedback
    waiting_for_feedback = State()
    
    # Broadcast
    waiting_for_broadcast_message = State()
    waiting_for_broadcast_confirm = State()
    
    # Settings
    waiting_for_risk_level = State()
    waiting_for_language = State()
    
    # Withdrawal
    waiting_for_withdrawal_amount = State()
    waiting_for_withdrawal_wallet = State()

# ═══════════════════════════════════════════════════════════
# SECTION 16: KEYBOARD FACTORY
# ═══════════════════════════════════════════════════════════

class KeyboardFactory:
    """Factory class for building all bot keyboards"""
    
    @staticmethod
    def main_menu(plan: str = "free") -> InlineKeyboardMarkup:
        """Build main menu keyboard based on user plan"""
        builder = InlineKeyboardBuilder()
        
        builder.button(text=f"{E.SEARCH} بازار", callback_data="menu_market")
        builder.button(text=f"{E.BRAIN} هوش مصنوعی", callback_data="menu_ai")
        builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="menu_analysis")
        builder.button(text=f"{E.BELL} هشدار قیمت", callback_data="menu_alerts")
        builder.button(text=f"{E.STAR} واچ‌لیست", callback_data="menu_watchlist")
        builder.button(text=f"{E.CLOCK} زمان تهران", callback_data="menu_time")
        
        if plan == PlanType.FREE.value:
            builder.button(text=f"{E.CROWN} ارتقا به VIP", callback_data="menu_vip")
        
        builder.button(text=f"{E.ROBOT} درباره ما", callback_data="menu_about")
        builder.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="menu_support")
        
        builder.adjust(3, 2, 2, 2)
        return builder.as_markup()
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Build admin panel keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.PERSON} کاربران", callback_data="admin_users")
        builder.button(text=f"{E.CARD} پرداخت‌ها", callback_data="admin_payments")
        builder.button(text=f"{E.CHART} سیگنال‌ها", callback_data="admin_signals")
        builder.button(text=f"{E.BELL} هشدارها", callback_data="admin_alerts")
        builder.button(text=f"{E.SETTINGS} تنظیمات", callback_data="admin_settings")
        builder.button(text=f"{E.MAIL} ارسال همگانی", callback_data="admin_broadcast")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2, 2, 2, 1)
        return builder.as_markup()
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """Build VIP subscription plans keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CROWN} VIP - {PLANS['vip']['price']:,} تومان", callback_data="buy_vip")
        builder.button(text=f"{E.DIAMOND} PRO - {PLANS['pro']['price']:,} تومان", callback_data="buy_pro")
        builder.button(text=f"{E.CROWN}{E.DIAMOND} ELITE - {PLANS['elite']['price']:,} تومان", callback_data="buy_elite")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def analysis_symbols() -> InlineKeyboardMarkup:
        """Build symbol selection keyboard for analysis"""
        builder = InlineKeyboardBuilder()
        for sym in DEFAULT_SYMBOLS[:10]:
            name = sym.replace("USDT", "")
            persian = SYMBOL_NAMES_PERSIAN.get(name, name)
            builder.button(text=f"{E.CHART} {name} ({persian})", callback_data=f"analyze_{sym}")
        builder.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_symbol")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def timeframes() -> InlineKeyboardMarkup:
        """Build timeframe selection keyboard"""
        builder = InlineKeyboardBuilder()
        for tf, name in list(TIMEFRAMES.items())[:6]:
            builder.button(text=f"{E.CLOCK} {name}", callback_data=f"tf_{tf}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(3)
        return builder.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Simple back to main menu button"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت به منوی اصلی", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment(plan: str) -> InlineKeyboardMarkup:
        """Build payment confirmation keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} پرداخت کردم ✅", callback_data=f"confirm_pay_{plan}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="menu_vip")
        return builder.as_markup()
    
    @staticmethod
    def admin_payment_actions(payment_id: int) -> InlineKeyboardMarkup:
        """Build admin payment action keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} تایید", callback_data=f"admin_approve_{payment_id}")
        builder.button(text=f"{E.CROSS} رد", callback_data=f"admin_reject_{payment_id}")
        return builder.as_markup()
    
    @staticmethod
    def alert_types(symbol: str) -> InlineKeyboardMarkup:
        """Build alert type selection keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHART_UP} بالاتر از", callback_data=f"alerttype_above_{symbol}")
        builder.button(text=f"{E.CHART_DOWN} پایین‌تر از", callback_data=f"alerttype_below_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="menu_alerts")
        return builder.as_markup()
    
    @staticmethod
    def risk_levels() -> InlineKeyboardMarkup:
        """Build risk level selection keyboard"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"🟢 پایین", callback_data="risk_low")
        builder.button(text=f"🟡 متوسط", callback_data="risk_medium")
        builder.button(text=f"🔴 بالا", callback_data="risk_high")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        return builder.as_markup()

KB = KeyboardFactory()

# ═══════════════════════════════════════════════════════════
# SECTION 17: MESSAGE TEMPLATE ENGINE
# ═══════════════════════════════════════════════════════════

class MessageTemplateEngine:
    """Engine for building all bot message templates"""
    
    @staticmethod
    def welcome_message(user_name: str, plan: str, days_left: int) -> str:
        """Build professional welcome message"""
        now = TT.now()
        plan_icon = E.plan_icon(plan)
        plan_name = T.PLAN_NAMES.get(plan, "رایگان")
        greeting = TT.greeting(now)
        
        return f"""
{E.ROCKET}{E.FIRE}{E.ROCKET} *{APP_NAME}* {E.ROCKET}{E.FIRE}{E.ROCKET}
{E.SPARKLES} نسخه {APP_VERSION}

{E.ROBOT} {greeting} *{user_name}* عزیز!
{E.WAVE} به پیشرفته‌ترین ربات تحلیل کریپتو خوش آمدید!

{E.CLOCK} *زمان تهران:* {TT.format(now, 'full')}
{E.GLOBE} *فصل:* {TT.get_season(now)}
{E.CHART} *سشن معاملاتی:* {TT.trading_session(now)}

{E.DIAMOND}{'━'*20}{E.DIAMOND}
{plan_icon} *پلن فعلی:* {plan_name}
{E.CALENDAR} *اعتبار باقی‌مانده:* {days_left} روز
{E.HOURGLASS} *سوالات AI امروز:* در حال بارگذاری...
{E.DIAMOND}{'━'*20}{E.DIAMOND}

{E.POINT_DOWN} *لطفاً از منوی زیر گزینه مورد نظر را انتخاب کنید:*
"""
    
    @staticmethod
    def market_overview(tickers: Dict[str, Dict]) -> str:
        """Build market overview message"""
        now = TT.now()
        text = f"""{E.GLOBE} *خلاصه بازار ارزهای دیجیتال*
{E.CLOCK} {TT.format(now, 'time')} | {TT.format(now, 'date')}
{E.CHART} سشن: {TT.trading_session(now)}

"""
        
        for symbol, data in tickers.items():
            try:
                price = float(data.get('last', 0))
                change = float(data.get('change_percentage', 0))
                volume = float(data.get('volume', 0))
                
                emoji = E.change_icon(change)
                name = symbol.replace("USDT", "")
                persian = SYMBOL_NAMES_PERSIAN.get(name, name)
                
                text += f"{emoji} *{name}* ({persian})\n"
                text += f"  {E.MONEY} قیمت: ${T.format_price(price)}\n"
                text += f"  {E.CHART} تغییر: {T.format_percent(change)}\n"
                text += f"  {E.WAVE} حجم: {T.format_volume(volume)}\n\n"
            except Exception as e:
                text += f"{E.CROSS} {symbol}: خطا در دریافت اطلاعات\n\n"
        
        text += f"{E.INFO} *نکته:* اطلاعات هر ۳۰ ثانیه بروزرسانی می‌شود."
        return text
    
    @staticmethod
    def technical_analysis_card(
        symbol: str, price: float, change: float,
        rsi: float, macd_line: float, macd_signal: float,
        macd_histogram: float, bollinger_upper: float,
        bollinger_middle: float, bollinger_lower: float,
        support: float, resistance: float,
        fib_levels: Dict[str, float], moving_averages: Dict[str, float],
        trend: str, volume_analysis: Dict, market_structure: Dict,
        ai_analysis: str = ""
    ) -> str:
        """Build comprehensive technical analysis card"""
        
        change_emoji = E.change_icon(change)
        rsi_status = E.rsi_status(rsi)
        trend_icon = "🟢" if "صعودی" in trend else "🔴" if "نزولی" in trend else "⚪"
        
        # Fibonacci text
        fib_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {value:.4f}"
            for name, value in list(fib_levels.items())[:7]
        ])
        
        # Moving averages text
        ma_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {value:.4f}"
            for name, value in list(moving_averages.items())[:4]
        ])
        
        text = f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل تکنیکال {symbol}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت فعلی:* ${T.format_price(price)}
{change_emoji} *تغییر ۲۴ ساعته:* {T.format_percent(change)}

{E.THERMOMETER} *اندیکاتورهای تکنیکال:*
{E.POINT_RIGHT} RSI (14): {rsi_status}
{E.POINT_RIGHT} MACD: {macd_line:.4f} | سیگنال: {macd_signal:.4f} | هیستوگرام: {macd_histogram:.4f}
{E.POINT_RIGHT} بولینگر: بالا {bollinger_upper:.4f} | میانه {bollinger_middle:.4f} | پایین {bollinger_lower:.4f}

{E.SHIELD} *سطوح کلیدی:*
{E.POINT_RIGHT} حمایت: ${support:,.4f}
{E.POINT_RIGHT} مقاومت: ${resistance:,.4f}

{E.CRYSTAL} *سطوح فیبوناچی:*
{fib_text}

{E.MAGNET} *میانگین‌های متحرک:*
{ma_text}

{E.MOUNTAIN} *تحلیل ساختار بازار:*
{E.POINT_RIGHT} روند: {trend_icon} {trend}
{E.POINT_RIGHT} ساختار: {market_structure.get('structure', 'نامشخص')}
{E.POINT_RIGHT} بایاس: {market_structure.get('bias', 'خنثی')}

{E.WAVE} *تحلیل حجم:*
{E.POINT_RIGHT} وضعیت: {volume_analysis.get('trend', 'نرمال')}
{E.POINT_RIGHT} سیگنال: {volume_analysis.get('signal', 'خنثی')}
{E.POINT_RIGHT} نسبت حجم: {volume_analysis.get('current_ratio', 1)}x

{E.CLOCK} *زمان تحلیل:* {TT.format(TT.now(), 'full')}
{E.INFO} *وضعیت بازار:* {'بازار تعطیل 🕌' if TT.is_weekend() else 'بازار فعال ✅'}
"""
        
        if ai_analysis:
            text += f"""
{E.DIAMOND}{'━'*20}{E.DIAMOND}
{E.ROBOT} *تحلیل هوش مصنوعی:*
{ai_analysis}
{E.DIAMOND}{'━'*20}{E.DIAMOND}
"""
        
        text += f"""
{E.WARNING} *سلب مسئولیت:* این تحلیل صرفاً جنبه اطلاع‌رسانی دارد و سیگنال خرید و فروش نمی‌باشد.
"""
        
        return text
    
    @staticmethod
    def vip_plans_info() -> str:
        """Build VIP plans information message"""
        text = f"""
{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های اشتراک VIP* {E.CROWN}{E.CROWN}{E.CROWN}

"""
        for plan_key in ["vip", "pro", "elite"]:
            plan = PLANS[plan_key]
            text += f"""
{plan['icon']} *{plan['name']}*
{E.MONEY} قیمت: *{plan['price']:,} تومان* ({plan['price_usd']} دلار)
{E.CALENDAR} مدت: *{plan['days']} روز*
{E.BRAIN} سوالات AI: *{plan['ai_daily_limit']} عدد در روز*
{E.BELL} هشدارها: *{plan['max_alerts']} عدد*
{E.STAR} واچ‌لیست: *{plan['max_watchlist']} عدد*

*امکانات:*
"""
            for feature in plan['features']:
                text += f"  {E.CHECK} {feature}\n"
            text += "\n" + "─" * 30 + "\n"
        
        text += f"""
{E.GIFT} *هدیه ویژه کاربران جدید:* {WELCOME_BONUS_DAYS} روز VIP رایگان!
{E.CARD} *شماره کارت:* `{CARD_NUMBER}`
{E.PERSON} *به نام:* {CARD_HOLDER}

{E.POINT_DOWN} *برای خرید روی پلن مورد نظر کلیک کنید:*
"""
        return text
    
    @staticmethod
    def payment_instruction(plan_key: str) -> str:
        """Build payment instruction message"""
        plan = PLANS.get(plan_key, PLANS["vip"])
        
        return f"""
{E.CARD} *پرداخت اشتراک {plan['name']}*

{E.MONEY} *مبلغ قابل پرداخت:* {plan['price']:,} تومان
{E.CALENDAR} *مدت اشتراک:* {plan['days']} روز

{E.BANK} *اطلاعات کارت بانکی:*
{E.POINT_RIGHT} شماره کارت: `{CARD_NUMBER}`
{E.POINT_RIGHT} به نام: {CARD_HOLDER}

{E.WARNING} *نکات مهم:*
{E.POINT_RIGHT} مبلغ را دقیقاً به شماره کارت فوق واریز نمایید
{E.POINT_RIGHT} پس از واریز، *رسید پرداخت* را همینجا ارسال کنید
{E.POINT_RIGHT} آیدی تلگرام خود را در توضیحات پرداخت ذکر کنید
{E.POINT_RIGHT} زمان تأیید: ۵ تا ۱۵ دقیقه

{E.ENVELOPE} *پشتیبانی:* {SUPPORT_CONTACT}

{E.POINT_DOWN} *پس از پرداخت روی دکمه زیر کلیک کنید:*
"""
    
    @staticmethod
    def about_bot() -> str:
        """Build about bot message"""
        return f"""
{E.ROBOT} *{APP_NAME}*
{E.SPARKLES} نسخه {APP_VERSION} (Build {APP_BUILD})

{E.LIGHTNING} پیشرفته‌ترین ربات تحلیل کریپتو با هوش مصنوعی

{E.BRAIN} *مشخصات فنی:*
{E.POINT_RIGHT} هوش مصنوعی: Groq (Llama 3.3 70B)
{E.POINT_RIGHT} صرافی: CoinEx
{E.POINT_RIGHT} تحلیل تکنیکال: RSI، MACD، بولینگر، فیبوناچی، MA
{E.POINT_RIGHT} پرایس اکشن و ساختار بازار
{E.POINT_RIGHT} هشدار هوشمند قیمت
{E.POINT_RIGHT} سیستم اشتراک VIP
{E.POINT_RIGHT} واچ‌لیست و مدیریت سبد
{E.POINT_RIGHT} پشتیبانی ۲۴/۷

{E.CROWN} *تیم توسعه:*
{E.POINT_RIGHT} سازنده: {CREATOR_USERNAME}
{E.POINT_RIGHT} کانال رسمی: {CHANNEL_USERNAME}
{E.POINT_RIGHT} پشتیبانی: {SUPPORT_CONTACT}

{E.CLOCK} *زمان سرور:* {TT.format(TT.now(), 'full')}
{E.GLOBE} *وضعیت:* آنلاین و فعال 🟢
"""
    
    @staticmethod
    def support_info() -> str:
        """Build support information message"""
        return f"""
{E.ENVELOPE} *پشتیبانی {APP_NAME}*

{E.PERSON} *راه‌های ارتباطی:*
{E.POINT_RIGHT} تلگرام: {SUPPORT_CONTACT}
{E.POINT_RIGHT} کانال: {CHANNEL_USERNAME}

{E.CLOCK} *ساعات پاسخگویی:*
{E.POINT_RIGHT} همه روزه: ۸ صبح تا ۱۲ شب
{E.POINT_RIGHT} کاربران VIP: پاسخگویی سریع (کمتر از ۱ ساعت)
{E.POINT_RIGHT} کاربران عادی: ۲ تا ۴ ساعت کاری

{E.CARD} *اطلاعات بانکی:*
{E.POINT_RIGHT} شماره کارت: `{CARD_NUMBER}`
{E.POINT_RIGHT} به نام: {CARD_HOLDER}

{E.INFO} *موارد قابل پیگیری:*
{E.POINT_RIGHT} مشکلات پرداخت و اشتراک
{E.POINT_RIGHT} سوالات فنی و راهنما
{E.POINT_RIGHT} پیشنهادات و انتقادات
{E.POINT_RIGHT} گزارش خطا و باگ

{E.WARNING} لطفاً قبل از تماس، توضیحات کامل مشکل را آماده کنید.
"""
    
    @staticmethod
    def time_info_message() -> str:
        """Build time information message"""
        now = TT.now()
        session = TT.session_details(now)
        next_candles = {
            "۱ دقیقه": TT.next_candle_close("1m"),
            "۵ دقیقه": TT.next_candle_close("5m"),
            "۱۵ دقیقه": TT.next_candle_close("15m"),
            "۱ ساعت": TT.next_candle_close("1h"),
            "۴ ساعت": TT.next_candle_close("4h"),
            "روزانه": TT.next_candle_close("1d"),
        }
        
        candles_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {time_val}"
            for name, time_val in next_candles.items()
        ])
        
        return f"""
{E.CLOCK} *اطلاعات زمان و تاریخ تهران*

{E.CALENDAR} *تاریخ امروز:*
{E.POINT_RIGHT} {TT.format(now, 'date')}
{E.POINT_RIGHT} {TT.format(now, 'day_name')}

{E.WATCH} *ساعت فعلی:*
{E.POINT_RIGHT} {TT.format(now, 'time')}

{E.GLOBE} *اطلاعات فصلی:*
{E.POINT_RIGHT} فصل: {TT.get_season(now)}
{E.POINT_RIGHT} تعطیلی: {'بله 🕌' if TT.is_weekend(now) else 'خیر'}
{E.POINT_RIGHT} شب: {'بله 🌙' if TT.is_night_time(now) else 'خیر ☀️'}

{E.CHART} *سشن معاملاتی:*
{E.POINT_RIGHT} فعلی: {session['name']}
{E.POINT_RIGHT} شروع: {session['start']} | پایان: {session['end']}
{E.POINT_RIGHT} پیشرفت: {session['progress']}٪
{E.POINT_RIGHT} باقی‌مانده: {session['remaining']} ساعت

{E.HOURGLASS} *بسته شدن کندل‌های بعدی:*
{candles_text}
"""
    
    @staticmethod
    def admin_stats_message(stats: Dict) -> str:
        """Build admin statistics message"""
        return f"""
{E.SETTINGS} *پنل مدیریت {APP_NAME}*

{E.PERSON} *آمار کاربران:*
{E.POINT_RIGHT} کل کاربران: {stats.get('total_users', 0):,}
{E.POINT_RIGHT} کاربران ویژه: {stats.get('premium_users', 0):,}
{E.POINT_RIGHT} فعال امروز: {stats.get('active_today', 0):,}
{E.POINT_RIGHT} نرخ تبدیل: {stats.get('conversion_rate', 0)}٪

{E.MONEY} *آمار مالی:*
{E.POINT_RIGHT} درآمد کل: {stats.get('total_revenue', 0):,} تومان
{E.POINT_RIGHT} پرداخت‌های معلق: {stats.get('pending_payments', 0)}

{E.BRAIN} *آمار AI:*
{E.POINT_RIGHT} کل پرسش‌ها: {stats.get('total_ai_queries', 0):,}

{E.CHART} *سیگنال‌ها:*
{E.POINT_RIGHT} کل: {stats.get('total_signals', 0)} | فعال: {stats.get('active_signals', 0)}

{E.BELL} *هشدارها:*
{E.POINT_RIGHT} کل: {stats.get('total_alerts', 0)} | فعال: {stats.get('active_alerts', 0)}

{E.CLOCK} {TT.format(TT.now(), 'full')}
"""

MSG = MessageTemplateEngine()

# ═══════════════════════════════════════════════════════════
# SECTION 18: MIDDLEWARE & DECORATORS
# ═══════════════════════════════════════════════════════════

def rate_limit(seconds: float = 0.5):
    """Decorator for rate limiting callbacks"""
    def decorator(func):
        last_called = {}
        
        @wraps(func)
        async def wrapper(callback: CallbackQuery, *args, **kwargs):
            user_id = callback.from_user.id
            now = time.time()
            
            if user_id in last_called:
                elapsed = now - last_called[user_id]
                if elapsed < seconds:
                    await callback.answer("⏳ لطفاً کمی صبر کنید...", show_alert=True)
                    return
            
            last_called[user_id] = now
            return await func(callback, *args, **kwargs)
        
        return wrapper
    return decorator

def require_premium(func):
    """Decorator to require premium access"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        is_prem = await db.is_premium(user_id)
        
        if not is_prem:
            await callback.answer(
                f"{E.LOCK} این قابلیت مخصوص کاربران VIP است.\n{E.POINT_RIGHT} از منوی VIP پلن خود را ارتقا دهید.",
                show_alert=True
            )
            await callback.message.edit_text(
                MSG.vip_plans_info(),
                reply_markup=KB.vip_plans(),
                parse_mode="HTML"
            )
            return
        
        return await func(callback, *args, **kwargs)
    return wrapper

def admin_only(func):
    """Decorator to require admin access"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
            return
        return await func(callback, *args, **kwargs)
    return wrapper

# ═══════════════════════════════════════════════════════════
# SECTION 19: TELEGRAM HANDLERS
# ═══════════════════════════════════════════════════════════

router = Router()

# ── Start Command ──

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "کاربر گرامی"
    username = message.from_user.username or ""
    
    # Register/update user
    await db.upsert_user(user_id, username, full_name)
    
    # Process referral if present
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id != user_id:
                user = await db.get_user(user_id)
                if user and not user.get('referred_by'):
                    await db.execute(
                        "UPDATE users SET referred_by = ? WHERE user_id = ?",
                        (referrer_id, user_id)
                    )
                    await db.execute(
                        "UPDATE users SET total_referrals = total_referrals + 1 WHERE user_id = ?",
                        (referrer_id,)
                    )
                    await db.execute(
                        "INSERT OR IGNORE INTO referrals(referrer_id, referred_id) VALUES(?, ?)",
                        (referrer_id, user_id)
                    )
        except Exception as e:
            logger.warning(f"Referral processing error: {e}")
    
    # Apply welcome bonus for new users
    user = await db.get_user(user_id)
    if user and not user.get('welcome_bonus'):
        await db.execute(
            "UPDATE users SET plan = 'vip', plan_until = ?, welcome_bonus = 1 WHERE user_id = ?",
            (time.time() + WELCOME_BONUS_DAYS * 86400, user_id)
        )
        logger.info(f"Welcome bonus applied for user {user_id}")
    
    # Get current plan and days left
    plan = await db.get_user_plan(user_id)
    days_left = 0
    if user and user.get('plan_until'):
        days_left = max(0, int((user['plan_until'] - time.time()) / 86400))
    
    # Send welcome message
    welcome_text = MSG.welcome_message(full_name, plan, days_left)
    
    await message.answer(
        welcome_text,
        reply_markup=KB.main_menu(plan),
        parse_mode="HTML"
    )
    
    await db.log(user_id, "start", f"Plan: {plan}, Days: {days_left}")

# ── Main Menu ──

@router.callback_query(F.data == "main_menu")
@rate_limit(0.3)
async def callback_main_menu(callback: CallbackQuery):
    """Return to main menu"""
    plan = await db.get_user_plan(callback.from_user.id)
    
    await callback.message.edit_text(
        f"{E.HOME} *منوی اصلی*\n\n{E.POINT_DOWN} لطفاً گزینه مورد نظر را انتخاب کنید:",
        reply_markup=KB.main_menu(plan),
        parse_mode="HTML"
    )
    await callback.answer()

# ── Market Overview ──

@router.callback_query(F.data == "menu_market")
@rate_limit(0.5)
async def callback_market(callback: CallbackQuery):
    """Show market overview"""
    await callback.answer("🔄 در حال دریافت اطلاعات بازار...")
    
    # Get data for top symbols
    symbols = DEFAULT_SYMBOLS[:10]
    tickers = await exchange.get_multiple_tickers(symbols)
    
    if not tickers:
        await callback.message.edit_text(
            f"{E.CROSS} خطا در دریافت اطلاعات بازار.\n{E.INFO} لطفاً دوباره تلاش کنید.",
            reply_markup=KB.back_to_main()
        )
        return
    
    market_text = MSG.market_overview(tickers)
    
    # Build keyboard with refresh option
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data="menu_market")
    builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="menu_analysis")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    builder.adjust(2, 1)
    
    # Split long messages
    if len(market_text) > 4000:
        parts = [market_text[i:i+4000] for i in range(0, len(market_text), 4000)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await callback.message.edit_text(part, reply_markup=builder.as_markup(), parse_mode="HTML")
            else:
                await callback.message.answer(part, parse_mode="HTML")
    else:
        await callback.message.edit_text(market_text, reply_markup=builder.as_markup(), parse_mode="HTML")

# ── AI Question ──

@router.callback_query(F.data == "menu_ai")
@rate_limit(1.0)
async def callback_ai_menu(callback: CallbackQuery, state: FSMContext):
    """Start AI question flow"""
    user_id = callback.from_user.id
    
    # Check AI usage limits
    can_use, used, limit = await db.can_use_ai(user_id)
    
    if not can_use:
        await callback.message.edit_text(
            f"{E.WARNING} *محدودیت هوش مصنوعی*\n\n"
            f"{E.HOURGLASS} شما {used} از {limit} سوال روزانه خود را استفاده کرده‌اید.\n\n"
            f"{E.LOCK} برای سوالات بیشتر، لطفاً پلن خود را ارتقا دهید:\n",
            reply_markup=KB.vip_plans(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    await state.set_state(BotStates.waiting_for_ai_question)
    
    await callback.message.edit_text(
        f"{E.BRAIN} *پرسش از هوش مصنوعی*\n\n"
        f"{E.HOURGLASS} سوالات باقی‌مانده امروز: {limit - used} از {limit}\n\n"
        f"{E.POINT_DOWN} لطفاً سوال خود را به صورت متن ارسال کنید:\n\n"
        f"{E.INFO} *مثال:* تحلیل تکنیکال بیت‌کوین را بده\n"
        f"{E.INFO} *مثال:* سیگنال خرید برای اتریوم\n"
        f"{E.INFO} *مثال:* وضعیت بازار امروز را تحلیل کن",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(StateFilter(BotStates.waiting_for_ai_question))
async def handle_ai_question(message: Message, state: FSMContext):
    """Process AI question"""
    user_id = message.from_user.id
    
    # Verify limits again
    can_use, used, limit = await db.can_use_ai(user_id)
    if not can_use:
        await message.answer(
            f"{E.WARNING} محدودیت روزانه شما تمام شده است.",
            reply_markup=KB.vip_plans()
        )
        await state.clear()
        return
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # Get answer from AI
    start_time = time.time()
    answer = await ai.ask(message.text)
    response_time = time.time() - start_time
    
    # Update usage counter
    new_count = await db.increment_ai_usage(user_id)
    await db.save_ai_conversation(user_id, message.text, answer, 0, response_time)
    await db.log(user_id, "ai_question", message.text[:100])
    
    # Build response keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.BRAIN} سوال جدید", callback_data="menu_ai")
    builder.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
    
    # Send response
    response_text = f"{E.ROBOT} *پاسخ هوش مصنوعی:*\n\n{answer}\n\n{E.HOURGLASS} سوالات باقی‌مانده: {limit - new_count} از {limit}"
    
    if len(response_text) > 4000:
        parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await message.answer(part, reply_markup=builder.as_markup(), parse_mode="HTML")
            else:
                await message.answer(part, parse_mode="HTML")
    else:
        await message.answer(response_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    
    await state.clear()

# ── Technical Analysis ──

@router.callback_query(F.data == "menu_analysis")
@rate_limit(0.3)
async def callback_analysis_menu(callback: CallbackQuery):
    """Show analysis symbol selection"""
    await callback.message.edit_text(
        f"{E.CHART} *تحلیل تکنیکال*\n\n{E.POINT_DOWN} نماد مورد نظر را انتخاب کنید:",
        reply_markup=KB.analysis_symbols(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("analyze_"))
@rate_limit(1.0)
async def callback_analyze_symbol(callback: CallbackQuery):
    """Analyze a specific symbol"""
    symbol = callback.data.replace("analyze_", "")
    await callback.answer(f"🔄 در حال تحلیل {symbol}...")
    
    try:
        # Fetch market data
        ticker = await exchange.get_ticker(symbol)
        if not ticker:
            raise ValueError(f"اطلاعات برای {symbol} یافت نشد")
        
        price = float(ticker.get('last', 0))
        change = float(ticker.get('change_percentage', 0))
        volume_24h = float(ticker.get('volume', 0))
        
        # Fetch klines for technical analysis
        klines = await exchange.get_klines(symbol, "1hour", 100)
        
        if not klines:
            raise ValueError("داده کندل یافت نشد")
        
        closes = [float(c.get('close', 0)) for c in klines]
        highs = [float(c.get('high', 0)) for c in klines]
        lows = [float(c.get('low', 0)) for c in klines]
        volumes = [float(c.get('volume', 0)) for c in klines]
        
        if len(closes) < 30:
            raise ValueError("داده کافی برای تحلیل وجود ندارد")
        
        # Calculate all technical indicators
        rsi = ta.calculate_rsi(closes)
        macd_line, macd_signal, macd_hist = ta.calculate_macd(closes)
        bb_upper, bb_middle, bb_lower = ta.calculate_bollinger_bands(closes)
        support, resistance = ta.calculate_support_resistance(closes)
        fib_levels = ta.calculate_fibonacci(max(highs), min(lows))
        moving_averages = ta.calculate_moving_averages(closes)
        trend = ta.detect_trend(closes)
        volume_analysis = ta.analyze_volume(volumes, closes)
        market_structure = ta.market_structure(highs, lows)
        
        # Get AI analysis
        ai_context = f"""Symbol: {symbol}
Price: {price}
24h Change: {change}%
RSI: {rsi:.1f}
MACD: {macd_line:.4f}
Support: {support:.4f}
Resistance: {resistance:.4f}
Trend: {trend}
Volume: {volume_24h}"""
        
        ai_analysis = await ai.analyze_technically(symbol, ai_context)
        
        # Build the analysis card
        analysis_text = MSG.technical_analysis_card(
            symbol, price, change, rsi, macd_line, macd_signal, macd_hist,
            bb_upper, bb_middle, bb_lower, support, resistance,
            fib_levels, moving_averages, trend, volume_analysis,
            market_structure, ai_analysis
        )
        
        # Build action keyboard
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.BELL} هشدار قیمت", callback_data=f"alert_{symbol}")
        builder.button(text=f"{E.STAR} افزودن به واچ‌لیست", callback_data=f"watch_add_{symbol}")
        builder.button(text=f"{E.ROBOT} تحلیل AI بیشتر", callback_data=f"ai_analyze_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="menu_analysis")
        builder.adjust(2, 1, 1)
        
        # Send the analysis (split if too long)
        if len(analysis_text) > 4000:
            parts = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    await callback.message.edit_text(part, reply_markup=builder.as_markup(), parse_mode="HTML")
                else:
                    await callback.message.answer(part, parse_mode="HTML")
        else:
            await callback.message.edit_text(analysis_text, reply_markup=builder.as_markup(), parse_mode="HTML")
        
        await db.log(callback.from_user.id, "analysis", symbol)
        
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        await callback.message.edit_text(
            f"{E.CROSS} *خطا در تحلیل {symbol}*\n\n{E.INFO} {str(e)}\n\n{E.POINT_RIGHT} لطفاً دوباره تلاش کنید یا نماد دیگری انتخاب کنید.",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )

# ── Time Information ──

@router.callback_query(F.data == "menu_time")
@rate_limit(0.3)
async def callback_time_info(callback: CallbackQuery):
    """Show Tehran time information"""
    time_text = MSG.time_info_message()
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data="menu_time")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(time_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

# ── VIP Plans ──

@router.callback_query(F.data == "menu_vip")
@rate_limit(0.3)
async def callback_vip_menu(callback: CallbackQuery):
    """Show VIP plans"""
    vip_text = MSG.vip_plans_info()
    
    await callback.message.edit_text(vip_text, reply_markup=KB.vip_plans(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
@rate_limit(0.3)
async def callback_buy_plan(callback: CallbackQuery):
    """Handle plan purchase"""
    plan_key = callback.data.replace("buy_", "")
    
    if plan_key not in PLANS:
        await callback.answer("❌ پلن نامعتبر است!", show_alert=True)
        return
    
    payment_text = MSG.payment_instruction(plan_key)
    
    await callback.message.edit_text(
        payment_text,
        reply_markup=KB.confirm_payment(plan_key),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_pay_"))
@rate_limit(0.3)
async def callback_confirm_payment(callback: CallbackQuery, state: FSMContext):
    """Confirm payment and request receipt"""
    plan_key = callback.data.replace("confirm_pay_", "")
    plan = PLANS.get(plan_key, PLANS["vip"])
    
    await state.set_state(BotStates.waiting_for_payment_receipt)
    await state.update_data(plan=plan_key, amount=plan['price'])
    
    await callback.message.edit_text(
        f"{E.ENVELOPE} *ارسال رسید پرداخت*\n\n"
        f"{E.POINT_DOWN} لطفاً *عکس یا اسکرین‌شات* رسید پرداخت را ارسال کنید.\n\n"
        f"{E.WARNING} *توجه:* رسید باید شامل موارد زیر باشد:\n"
        f"{E.POINT_RIGHT} مبلغ واریزی\n"
        f"{E.POINT_RIGHT} تاریخ و ساعت\n"
        f"{E.POINT_RIGHT} شماره کارت مقصد\n\n"
        f"{E.INFO} در صورت تأیید، اشتراک شما در کمتر از ۱۵ دقیقه فعال می‌شود.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="menu_vip")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(StateFilter(BotStates.waiting_for_payment_receipt), F.photo)
async def handle_payment_receipt(message: Message, state: FSMContext):
    """Process payment receipt"""
    user_id = message.from_user.id
    data = await state.get_data()
    plan_key = data.get('plan', 'vip')
    amount = data.get('amount', 0)
    plan = PLANS.get(plan_key, PLANS["vip"])
    
    # Create payment record
    payment_id = await db.create_payment(user_id, plan_key, amount)
    await db.execute(
        "UPDATE payments SET receipt_file_id = ? WHERE id = ?",
        (message.photo[-1].file_id, payment_id)
    )
    
    # Notify all admins
    for admin_id in ADMIN_IDS:
        try:
            admin_text = f"""
{E.BELL} *پرداخت جدید*

{E.PERSON} کاربر: `{user_id}`
{E.CROWN} پلن: {plan['name']}
{E.MONEY} مبلغ: *{amount:,} تومان*
{E.CLOCK} زمان: {TT.format(TT.now(), 'full')}
{E.CARD} شناسه پرداخت: `{payment_id}`

{E.POINT_DOWN} برای بررسی روی دکمه‌های زیر کلیک کنید:
"""
            await message.bot.send_message(
                admin_id,
                admin_text,
                reply_markup=KB.admin_payment_actions(payment_id),
                parse_mode="HTML"
            )
            await message.bot.send_photo(admin_id, message.photo[-1].file_id)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    # Confirm to user
    await message.answer(
        f"{E.CHECK} *رسید پرداخت با موفقیت دریافت شد!*\n\n"
        f"{E.HOURGLASS} پرداخت شما در صف بررسی قرار گرفت.\n"
        f"{E.CLOCK} زمان تقریبی تأیید: *۵ تا ۱۵ دقیقه*\n\n"
        f"{E.INFO} پس از تأیید، اشتراک {plan['name']} شما فعال خواهد شد.\n"
        f"{E.ENVELOPE} در صورت هرگونه سوال: {SUPPORT_CONTACT}\n\n"
        f"{E.PRAY} از صبوری شما متشکریم! 🙏",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    
    await db.log(user_id, "payment_receipt_submitted", f"Payment ID: {payment_id}")
    await state.clear()

# ── Admin Payment Actions ──

@router.callback_query(F.data.startswith("admin_approve_"))
@admin_only
async def callback_admin_approve(callback: CallbackQuery):
    """Admin: approve payment"""
    payment_id = int(callback.data.replace("admin_approve_", ""))
    
    success = await db.approve_payment(payment_id, callback.from_user.id)
    
    if success:
        payment = await db.fetchone("SELECT * FROM payments WHERE id = ?", (payment_id,))
        if payment:
            plan = PLANS.get(payment['plan'], PLANS["vip"])
            # Notify user
            try:
                await callback.bot.send_message(
                    payment['user_id'],
                    f"{E.PARTY}{E.PARTY}{E.PARTY} *تبریک!*\n\n"
                    f"{E.CHECK} پرداخت شما *تأیید* شد!\n\n"
                    f"{E.CROWN} *پلن فعال شده:* {plan['name']}\n"
                    f"{E.CALENDAR} *مدت:* {plan['days']} روز\n"
                    f"{E.BRAIN} *سوالات AI:* {plan['ai_daily_limit']} عدد در روز\n\n"
                    f"{E.ROCKET} از امکانات ویژه خود لذت ببرید!\n"
                    f"{E.ENVELOPE} *پشتیبانی:* {SUPPORT_CONTACT}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify user {payment['user_id']}: {e}")
        
        await callback.message.edit_text(
            f"{E.CHECK} *پرداخت تأیید شد*\n\nشناسه: {payment_id}\nتأیید توسط: {callback.from_user.id}",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ خطا در تأیید پرداخت!", show_alert=True)

@router.callback_query(F.data.startswith("admin_reject_"))
@admin_only
async def callback_admin_reject(callback: CallbackQuery):
    """Admin: reject payment"""
    payment_id = int(callback.data.replace("admin_reject_", ""))
    
    await db.reject_payment(payment_id, callback.from_user.id, "Rejected by admin")
    
    payment = await db.fetchone("SELECT * FROM payments WHERE id = ?", (payment_id,))
    if payment:
        try:
            await callback.bot.send_message(
                payment['user_id'],
                f"{E.CROSS} *پرداخت تأیید نشد*\n\n"
                f"{E.INFO} متأسفانه پرداخت شما تأیید نشد.\n"
                f"{E.POINT_RIGHT} لطفاً با پشتیبانی تماس بگیرید:\n"
                f"{E.ENVELOPE} {SUPPORT_CONTACT}",
                parse_mode="HTML"
            )
        except:
            pass
    
    await callback.message.edit_text(
        f"{E.CROSS} پرداخت {payment_id} رد شد.",
        parse_mode="HTML"
    )

# ── Watchlist ──

@router.callback_query(F.data == "menu_watchlist")
@rate_limit(0.3)
async def callback_watchlist(callback: CallbackQuery):
    """Show user's watchlist"""
    user_id = callback.from_user.id
    items = await db.get_watchlist(user_id)
    
    if not items:
        text = f"{E.STAR} *واچ‌لیست شما*\n\n{E.INFO} واچ‌لیست شما خالی است.\n{E.POINT_RIGHT} از بخش تحلیل تکنیکال می‌توانید نمادها را اضافه کنید."
    else:
        text = f"{E.STAR} *واچ‌لیست شما* ({len(items)} نماد)\n\n"
        for i, item in enumerate(items, 1):
            added_time = TT.format(TT.from_timestamp(item['added_at']), "relative")
            text += f"{E.number(i)} {E.CHART} *{item['symbol']}*\n"
            text += f"   {E.CLOCK} اضافه شده: {added_time}\n"
            if item.get('note'):
                text += f"   {E.INFO} یادداشت: {item['note']}\n"
            text += "\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data="menu_watchlist")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("watch_add_"))
@rate_limit(0.3)
async def callback_watchlist_add(callback: CallbackQuery):
    """Add symbol to watchlist"""
    symbol = callback.data.replace("watch_add_", "")
    user_id = callback.from_user.id
    
    success = await db.add_to_watchlist(user_id, symbol)
    
    if success:
        await callback.answer(f"{E.CHECK} {symbol} به واچ‌لیست اضافه شد!", show_alert=True)
    else:
        await callback.answer(f"{E.CROSS} خطا در افزودن! (محدودیت پلن یا تکراری)", show_alert=True)

# ── Alerts ──

@router.callback_query(F.data == "menu_alerts")
@rate_limit(0.3)
async def callback_alerts_menu(callback: CallbackQuery):
    """Show alerts menu"""
    user_id = callback.from_user.id
    alerts = await db.get_active_alerts(user_id)
    
    if not alerts:
        text = f"{E.BELL} *هشدارهای قیمت*\n\n{E.INFO} هیچ هشدار فعالی ندارید.\n{E.POINT_RIGHT} برای ایجاد هشدار جدید کلیک کنید."
    else:
        text = f"{E.BELL} *هشدارهای فعال شما* ({len(alerts)} عدد)\n\n"
        for i, alert in enumerate(alerts, 1):
            alert_type = T.ALERT_TYPES.get(alert['alert_type'], alert['alert_type'])
            created = TT.format(TT.from_timestamp(alert['created_at']), "relative")
            text += f"{E.number(i)} {E.CHART} *{alert['symbol']}*\n"
            text += f"   {E.TARGET} {alert_type}: {alert['target_price']}\n"
            text += f"   {E.CLOCK} ایجاد: {created}\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.PLUS} هشدار جدید", callback_data="alert_new")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

# ── About & Support ──

@router.callback_query(F.data == "menu_about")
@rate_limit(0.3)
async def callback_about(callback: CallbackQuery):
    """Show about information"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.PHONE} کانال تلگرام", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
    builder.button(text=f"{E.ENVELOPE} ارتباط با سازنده", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(
        MSG.about_bot(),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_support")
@rate_limit(0.3)
async def callback_support(callback: CallbackQuery):
    """Show support information"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.ENVELOPE} پیام به پشتیبان", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(
        MSG.support_info(),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

# ── Admin Panel ──

@router.callback_query(F.data == "admin_panel")
@admin_only
@rate_limit(0.3)
async def callback_admin_panel(callback: CallbackQuery):
    """Show admin panel"""
    stats = await db.get_full_stats()
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی آمار", callback_data="admin_panel")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(
        MSG.admin_stats_message(stats),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

# ═══════════════════════════════════════════════════════════
# SECTION 20: FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════

# Create bot with proper DefaultBotProperties for aiogram 3.7+
try:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    logger.info("Bot instance created successfully")
except Exception as e:
    logger.error(f"Failed to create bot instance: {e}")
    bot = None

# Create dispatcher
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# Set bot commands
async def set_bot_commands():
    """Set bot commands menu"""
    if bot is None:
        return
    
    commands = [
        BotCommand(command="start", description="🚀 شروع ربات"),
        BotCommand(command="help", description="❓ راهنما"),
        BotCommand(command="market", description="📊 بازار"),
        BotCommand(command="ai", description="🤖 هوش مصنوعی"),
        BotCommand(command="vip", description="👑 پلن‌های VIP"),
        BotCommand(command="support", description="📧 پشتیبانی"),
    ]
    
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    except Exception as e:
        logger.error(f"Failed to set commands: {e}")

# Bot start time
bot_start_time = TT.now()

# Background alert checker
async def alert_checker_task():
    """Background task to check price alerts"""
    logger.info("Alert checker started")
    while True:
        try:
            active_alerts = await db.get_active_alerts()
            
            for alert in active_alerts:
                try:
                    ticker = await exchange.get_ticker(alert['symbol'])
                    if not ticker:
                        continue
                    
                    current_price = float(ticker.get('last', 0))
                    target_price = alert['target_price']
                    alert_type = alert['alert_type']
                    
                    triggered = False
                    if alert_type == 'above' and current_price >= target_price:
                        triggered = True
                    elif alert_type == 'below' and current_price <= target_price:
                        triggered = True
                    
                    if triggered:
                        await db.trigger_alert(alert['id'])
                        
                        if bot:
                            try:
                                await bot.send_message(
                                    alert['user_id'],
                                    f"{E.BELL}{E.BELL}{E.BELL} *هشدار قیمت!*\n\n"
                                    f"{E.CHART} *{alert['symbol']}*\n"
                                    f"{E.MONEY} قیمت فعلی: ${current_price:,.4f}\n"
                                    f"{E.TARGET} هدف: {target_price}\n"
                                    f"{E.CLOCK} {TT.format(TT.now(), 'full')}\n\n"
                                    f"{E.INFO} هشدار شما فعال شد!",
                                    parse_mode="HTML"
                                )
                            except:
                                pass
                except:
                    pass
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Alert checker error: {e}")
            await asyncio.sleep(60)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global bot_start_time
    
    logger.info(f"{E.ROCKET} Starting {APP_NAME} v{APP_VERSION}...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {PORT}")
    
    # Initialize database
    try:
        await db.initialize()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        raise
    
    # Set webhook
    if WEBHOOK_URL and bot:
        try:
            await bot.set_webhook(
                url=f"{WEBHOOK_URL}/webhook",
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"Webhook set to: {WEBHOOK_URL}/webhook")
        except Exception as e:
            logger.error(f"Webhook setup failed: {e}")
    
    # Set bot commands
    await set_bot_commands()
    
    # Start background tasks
    alert_task = asyncio.create_task(alert_checker_task())
    
    logger.info(f"{E.ROCKET} {APP_NAME} is ready!")
    logger.info(f"Time: {TT.format(TT.now(), 'full')}")
    logger.info(f"Uptime: {TT.uptime_string(bot_start_time)}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    
    alert_task.cancel()
    
    if bot:
        try:
            await bot.delete_webhook()
        except:
            pass
        try:
            await bot.session.close()
        except:
            pass
    
    await exchange.close()
    
    logger.info(f"{E.WAVE} {APP_NAME} stopped")

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Professional Crypto Trading Bot with AI, Technical Analysis, and VIP System",
    lifespan=lifespan,
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    try:
        # Verify webhook secret
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != WEBHOOK_SECRET:
            logger.warning(f"Invalid webhook secret attempt")
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        
        # Parse update
        data = await request.json()
        update = Update(**data)
        
        # Process update through dispatcher
        if dp and bot:
            await dp.feed_update(bot, update)
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}\n{traceback.format_exc()}")
        return JSONResponse({"status": "error", "message": str(e)[:100]}, status_code=500)

@app.get("/")
async def root_endpoint():
    """Root endpoint"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "build": APP_BUILD,
        "creator": CREATOR_USERNAME,
        "channel": CHANNEL_USERNAME,
        "status": "running",
        "time": TT.format(TT.now(), "full"),
        "timestamp": time.time(),
        "environment": ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "time": TT.format(TT.now(), "full"),
        "version": APP_VERSION,
        "uptime": TT.uptime_string(bot_start_time)
    }

@app.get("/stats")
async def get_stats(request: Request):
    """Get bot statistics (protected endpoint)"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.get_full_stats()
    stats["ai_engine"] = ai.get_stats()
    stats["exchange"] = exchange.get_stats()
    stats["uptime"] = TT.uptime_string(bot_start_time)
    
    return stats

@app.get("/admin")
async def admin_dashboard(request: Request):
    """Simple admin dashboard HTML"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.get_full_stats()
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{APP_NAME} - Admin Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Tahoma', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; min-height: 100vh; padding: 20px; }}
            .header {{ text-align: center; padding: 30px 0; }}
            .header h1 {{ font-size: 2em; color: #e94560; }}
            .header p {{ color: #aaa; margin-top: 10px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #0f3460; border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .card .icon {{ font-size: 3em; margin-bottom: 10px; }}
            .card .value {{ font-size: 2.5em; font-weight: bold; color: #e94560; }}
            .card .label {{ color: #aaa; margin-top: 5px; font-size: 1.1em; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🦅 {APP_NAME}</h1>
            <p>Admin Dashboard v{APP_VERSION}</p>
            <p>{TT.format(TT.now(), 'full')}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="icon">👥</div>
                <div class="value">{stats['total_users']:,}</div>
                <div class="label">کل کاربران</div>
            </div>
            <div class="card">
                <div class="icon">👑</div>
                <div class="value">{stats['premium_users']:,}</div>
                <div class="label">کاربران ویژه</div>
            </div>
            <div class="card">
                <div class="icon">📊</div>
                <div class="value">{stats['conversion_rate']}%</div>
                <div class="label">نرخ تبدیل</div>
            </div>
            <div class="card">
                <div class="icon">💰</div>
                <div class="value">{stats['total_revenue']:,}</div>
                <div class="label">درآمد کل (تومان)</div>
            </div>
            <div class="card">
                <div class="icon">🤖</div>
                <div class="value">{stats['total_ai_queries']:,}</div>
                <div class="label">پرسش‌های AI</div>
            </div>
            <div class="card">
                <div class="icon">📈</div>
                <div class="value">{stats['active_signals']}</div>
                <div class="label">سیگنال‌های فعال</div>
            </div>
        </div>
        
        <div class="footer">
            <p>سازنده: {CREATOR_USERNAME} | کانال: {CHANNEL_USERNAME}</p>
            <p>Uptime: {TT.uptime_string(bot_start_time)}</p>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

# ═══════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🦅 {APP_NAME} v{APP_VERSION} starting on port {PORT}")
    
    uvicorn.run(
        "bot:app",
        host="0.0.0.0",
        port=PORT,
        reload=(ENVIRONMENT == "development"),
        log_level="info",
        access_log=(ENVIRONMENT == "development"),
    )

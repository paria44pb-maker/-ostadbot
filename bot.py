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
        "INSERT INTO alerts(user_id, symbol, target_price, alert_type) VALUES(?, ?, ?, ?)",
        (user_id, symbol.upper(), target_price, alert_type)
    ) 
        

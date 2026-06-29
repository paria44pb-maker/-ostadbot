"""
🦅 OstadBot v10.0 | Ultimate Professional Trading Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
سازنده: @Amir92aa
کانال: @CryptoPulse606
شماره کارت: 6063-7311-9625-4479
به نام: بهمرد
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1: Core Engine - Config, Emoji, Time, Database
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, sys, json, time, hmac, hashlib, asyncio, logging, re, math, base64, uuid, random, traceback
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict, deque
from enum import Enum
from functools import wraps, partial
from pathlib import Path

import aiosqlite
import aiohttp
import numpy as np

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    Update, BotCommand, BotCommandScopeDefault
)
from aiogram.enums import ParseMode, ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError

from groq import Groq, RateLimitError as GroqRateLimitError
from groq import APIStatusError as GroqAPIError

# ════════════════════════════════════════
# LOGGING SETUP
# ════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OstadBot")

# ════════════════════════════════════════
# CONFIGURATION MASTER CLASS
# ════════════════════════════════════════
class Config:
    """Master configuration for OstadBot"""
    
    # Environment Variables
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ostadbot_v10_secret")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "ostadbot.db")
    PORT = int(os.getenv("PORT", "8080"))
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    
    # Application Identity
    APP_NAME = "OstadBot"
    APP_VERSION = "10.0.0"
    APP_BUILD = "2026.06.29"
    CREATOR_USERNAME = "@Amir92aa"
    CHANNEL_USERNAME = "@CryptoPulse606"
    CHANNEL_URL = "https://t.me/CryptoPulse606"
    CREATOR_URL = "https://t.me/Amir92aa"
    
    # Payment Information
    CARD_NUMBER = "6063-7311-9625-4479"
    CARD_HOLDER = "بهمرد"
    SUPPORT_CONTACT = "@Amir92aa"
    
    # Subscription Plans
    PLANS = {
        "vip": {
            "name": "VIP 👑",
            "price": 199000,
            "days": 30,
            "ai_limit": 50,
            "alerts": 10,
            "watchlist": 20,
            "signals": 5,
            "features": [
                "۵۰ تحلیل AI در روز",
                "۱۰ هشدار قیمت فعال",
                "واچ‌لیست ۲۰ ارزی",
                "۵ سیگنال VIP روزانه",
                "تحلیل تکنیکال پیشرفته",
                "پشتیبانی سریع"
            ]
        },
        "pro": {
            "name": "PRO 💎",
            "price": 399000,
            "days": 30,
            "ai_limit": 200,
            "alerts": 30,
            "watchlist": 50,
            "signals": 15,
            "features": [
                "۲۰۰ تحلیل AI در روز",
                "۳۰ هشدار قیمت فعال",
                "واچ‌لیست ۵۰ ارزی",
                "۱۵ سیگنال PRO روزانه",
                "کپی تریدینگ هوشمند",
                "گزارش روزانه بازار",
                "پشتیبانی VIP"
            ]
        },
        "elite": {
            "name": "ELITE 👑💎",
            "price": 999000,
            "days": 90,
            "ai_limit": 999999,
            "alerts": 999,
            "watchlist": 999,
            "signals": 999,
            "features": [
                "تحلیل نامحدود AI",
                "هشدار نامحدود",
                "واچ‌لیست نامحدود",
                "سیگنال نامحدود",
                "مشاوره خصوصی ۱به۱",
                "ربات اختصاصی",
                "پشتیبانی ۲۴/۷"
            ]
        }
    }
    
    # Free Tier Limits
    FREE_AI_PER_DAY = 3
    FREE_SIGNALS_PER_DAY = 1
    FREE_WATCHLIST = 3
    FREE_ALERTS = 1
    WELCOME_BONUS_DAYS = 0
    
    # Rate Limits
    GROQ_RPM = 25
    RATE_LIMIT_SECONDS = 0.3
    
    # Trading Symbols
    SYMBOLS = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "AVAXUSDT",
    ]
    
    SYMBOL_NAMES = {
        "BTC": "بیت‌کوین", "ETH": "اتریوم", "SOL": "سولانا",
        "BNB": "بایننس کوین", "XRP": "ریپل", "ADA": "کاردانو",
        "DOGE": "دوج کوین", "DOT": "پولکادات", "MATIC": "پالیگان",
        "AVAX": "آوالانچ",
    }
    
    TIMEFRAMES = {
        "15m": "۱۵ دقیقه", "1h": "۱ ساعت", "4h": "۴ ساعت", "1d": "روزانه"
    }

cfg = Config()

# ════════════════════════════════════════
# ULTIMATE EMOJI BANK
# ════════════════════════════════════════
class Emoji:
    """Complete emoji collection with all needed icons"""
    
    # Rocket & Energy
    ROCKET = "🚀"; FIRE = "🔥"; MONEY = "💰"; COIN = "🪙"
    CHART = "📊"; CHART_UP = "📈"; CHART_DOWN = "📉"
    CANDLE_GREEN = "🟢"; CANDLE_RED = "🔴"; CANDLE_YELLOW = "🟡"; CANDLE_ORANGE = "🟠"
    CANDLE_BLUE = "🔵"; CANDLE_PURPLE = "🟣"; CANDLE_WHITE = "⚪"
    BULL = "🐂"; BEAR = "🐻"; TARGET = "🎯"
    CRYSTAL = "💠"; DIAMOND = "💎"; GEM = "💎"
    STAR = "⭐"; SPARKLES = "✨"; GLOW = "🌟"
    CROWN = "👑"; RING = "💍"
    
    # Status
    CHECK = "✅"; CROSS = "❌"; WARNING = "⚠️"; INFO = "ℹ️"
    LOCK = "🔒"; UNLOCK = "🔓"; KEY = "🔑"
    HOURGLASS = "⏳"; HOURGLASS_DONE = "⌛"
    LOADING = "🔄"; SYNC = "🔄"
    
    # Users & Emotions
    ROBOT = "🤖"; BRAIN = "🧠"; EYE = "👁️"
    COOL = "😎"; WOW = "😍"; LOVE = "🥰"; THINK = "🤔"
    PRAY = "🙏"; CLAP = "👏"; MUSCLE = "💪"; OK = "👌"
    PERSON = "👤"; PEOPLE = "👥"; WAVE = "👋"
    
    # UI Navigation
    HOME = "🏠"; BACK = "🔙"; SETTINGS = "⚙️"
    SEARCH = "🔍"; PLUS = "➕"; MINUS = "➖"; REFRESH = "🔄"
    BELL = "🔔"; ENVELOPE = "📧"; PHONE = "📱"
    GLOBE = "🌍"; CALENDAR = "📅"; CLOCK = "🕐"; WATCH = "⌚"
    
    # Celebration
    GIFT = "🎁"; PARTY = "🎉"; BALLOON = "🎈"; CONFETTI = "🎊"
    TROPHY = "🏆"; MEDAL = "🥇"; RIBBON = "🎀"; FLOWER = "🌸"
    
    # Power & Energy
    LIGHTNING = "⚡"; ZAP = "⚡"; EXPLOSION = "💥"
    
    # Protection
    SHIELD = "🛡️"; SWORD = "⚔️"; SCALE = "⚖️"; MAGNET = "🧲"
    
    # Science & Tech
    BULB = "💡"; MICROSCOPE = "🔬"; TELESCOPE = "🔭"
    SATELLITE = "🛰️"; GEAR = "⚙️"; HAMMER = "🔨"; WRENCH = "🔧"
    
    # Weather & Nature
    SUN = "☀️"; MOON = "🌙"; CLOUD = "☁️"; RAIN = "🌧️"
    SNOW = "❄️"; UMBRELLA = "☂️"; RAINBOW = "🌈"
    THERMOMETER = "🌡️"; WIND = "💨"
    MOUNTAIN = "🏔️"; OCEAN = "🌊"; VOLCANO = "🌋"
    
    # Finance
    CARD = "💳"; BANK = "🏦"; WALLET = "👛"
    BILL = "💵"; BILLS = "💸"; RECEIPT = "🧾"
    PIGGY = "🐷"; CALCULATOR = "🔢"
    
    # Arrows & Pointers
    UP = "⬆️"; DOWN = "⬇️"; RIGHT = "➡️"; LEFT = "⬅️"
    POINT_UP = "☝️"; POINT_DOWN = "👇"; POINT_RIGHT = "👉"; POINT_LEFT = "👈"
    TOP = "🔝"; NEW = "🆕"; FREE = "🆓"
    
    # Numbers
    N0 = "0️⃣"; N1 = "1️⃣"; N2 = "2️⃣"; N3 = "3️⃣"; N4 = "4️⃣"
    N5 = "5️⃣"; N6 = "6️⃣"; N7 = "7️⃣"; N8 = "8️⃣"; N9 = "9️⃣"; N10 = "🔟"
    
    @classmethod
    def num(cls, n: int) -> str:
        emojis = [cls.N0, cls.N1, cls.N2, cls.N3, cls.N4, cls.N5, cls.N6, cls.N7, cls.N8, cls.N9, cls.N10]
        return emojis[n] if 0 <= n <= 10 else f"#{n}"
    
    @classmethod
    def plan_icon(cls, plan: str) -> str:
        icons = {"free": cls.FREE, "vip": cls.CROWN, "pro": cls.DIAMOND, "elite": f"{cls.CROWN}{cls.DIAMOND}"}
        return icons.get(plan, cls.FREE)
    
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
    def trend_icon(cls, trend: str) -> str:
        if "قوی" in trend and "صعود" in trend: return "🟢🟢"
        if "صعود" in trend: return "🟢"
        if "قوی" in trend and "نزول" in trend: return "🔴🔴"
        if "نزول" in trend: return "🔴"
        return "⚪"

# Short alias
E = Emoji()

# ════════════════════════════════════════
# PERSIAN TEXT HELPER
# ════════════════════════════════════════
class PersianText:
    """Persian text utilities"""
    
    @staticmethod
    def greeting(hour: int = None) -> str:
        if hour is None:
            hour = datetime.now().hour
        if hour < 6: return "نیمه‌شب بخیر 🌙"
        if hour < 12: return "صبح بخیر ☀️"
        if hour < 17: return "عصر بخیر 🌤️"
        return "شب بخیر 🌙"
    
    @staticmethod
    def format_price(price: float) -> str:
        if price >= 1: return f"${price:,.4f}"
        return f"${price:.8f}"
    
    @staticmethod
    def format_toman(amount: float) -> str:
        return f"{amount:,.0f} تومان"
    
    @staticmethod
    def format_percent(p: float) -> str:
        emoji = "🟢" if p > 0 else "🔴" if p < 0 else "⚪"
        return f"{emoji} {p:+.2f}%"

T = PersianText()

# ════════════════════════════════════════
# TEHRAN TIME ENGINE (FULL)
# ════════════════════════════════════════
class TehranTime:
    """
    Complete Tehran time system with Persian calendar.
    Handles all time-related operations for the bot.
    """
    
    OFFSET = timedelta(hours=3, minutes=30)
    
    MONTHS = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    DAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"]
    
    DAYS_SHORT = ["۲ش", "۳ش", "۴ش", "۵ش", "ج", "ش", "۱ش"]
    
    SEASONS = {
        "spring": "بهار 🌸", "summer": "تابستان ☀️",
        "autumn": "پاییز 🍂", "winter": "زمستان ❄️"
    }
    
    SESSIONS = {
        "asian": {"name": "آسیا 🌏", "start": 3, "end": 12},
        "european": {"name": "اروپا 🌍", "start": 12, "end": 19},
        "american": {"name": "آمریکا 🌎", "start": 19, "end": 24},
    }
    
    MONTH_DAYS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    
    HOLIDAYS = [
        (1,1),(1,2),(1,3),(1,4),(1,12),(1,13),
        (3,14),(3,15),(4,13),(6,15),(8,22),
        (10,11),(10,12),(11,22),(12,29),
    ]
    
    @classmethod
    def now(cls) -> datetime:
        return datetime.now(timezone.utc) + cls.OFFSET
    
    @classmethod
    def ts(cls) -> float:
        return cls.now().timestamp()
    
    @classmethod
    def from_ts(cls, ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc) + cls.OFFSET
    
    @classmethod
    def _y(cls, dt: datetime) -> int:
        return dt.year - 621 if (dt.month, dt.day) >= (3, 21) else dt.year - 622
    
    @classmethod
    def _m(cls, dt: datetime) -> int:
        start = datetime(dt.year,3,21,tzinfo=dt.tzinfo) if (dt.month,dt.day)>=(3,21) else datetime(dt.year-1,3,21,tzinfo=dt.tzinfo)
        days = (dt - start).days
        for i, md in enumerate(cls.MONTH_DAYS):
            if days < md: return i + 1
            days -= md
        return 12
    
    @classmethod
    def _d(cls, dt: datetime) -> int:
        start = datetime(dt.year,3,21,tzinfo=dt.tzinfo) if (dt.month,dt.day)>=(3,21) else datetime(dt.year-1,3,21,tzinfo=dt.tzinfo)
        days = (dt - start).days
        for md in cls.MONTH_DAYS:
            if days < md: return days + 1
            days -= md
        return 29
    
    @classmethod
    def format(cls, dt: datetime = None, fmt: str = "full") -> str:
        if dt is None: dt = cls.now()
        y, m, d = cls._y(dt), cls._m(dt), cls._d(dt)
        
        if fmt == "full":
            return f"{cls.DAYS[dt.weekday()]} {d} {cls.MONTHS[m-1]} {y} - {dt.strftime('%H:%M:%S')}"
        elif fmt == "time":
            return dt.strftime("%H:%M:%S")
        elif fmt == "date":
            return f"{d} {cls.MONTHS[m-1]} {y}"
        elif fmt == "short":
            return f"{y}/{m:02d}/{d:02d} - {dt.strftime('%H:%M')}"
        elif fmt == "relative":
            diff = cls.now() - dt
            s = int(diff.total_seconds())
            if s < 0: return "همین الان"
            if s < 60: return f"{s} ثانیه پیش"
            if s < 3600: return f"{s//60} دقیقه پیش"
            if s < 86400: return f"{s//3600} ساعت پیش"
            if s < 604800: return f"{s//86400} روز پیش"
            return f"{s//2592000} ماه پیش"
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def season(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        m = cls._m(dt)
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
        _, m, d = cls._y(dt), cls._m(dt), cls._d(dt)
        return (m, d) in cls.HOLIDAYS or dt.weekday() == 4
    
    @classmethod
    def session(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        h = dt.hour
        if 3 <= h < 12: return cls.SESSIONS["asian"]["name"]
        if 12 <= h < 19: return cls.SESSIONS["european"]["name"]
        return cls.SESSIONS["american"]["name"]
    
    @classmethod
    def session_details(cls, dt: datetime = None) -> Dict:
        if dt is None: dt = cls.now()
        h = dt.hour
        if 3 <= h < 12: s = cls.SESSIONS["asian"]
        elif 12 <= h < 19: s = cls.SESSIONS["european"]
        else: s = cls.SESSIONS["american"]
        
        elapsed = max(0, h - s["start"])
        remaining = max(0, s["end"] - h)
        total = s["end"] - s["start"]
        progress = round((elapsed/total)*100, 1) if total > 0 else 100
        
        return {
            "name": s["name"], "start": f"{s['start']:02d}:00",
            "end": f"{s['end']:02d}:00", "elapsed": elapsed,
            "remaining": remaining, "progress": progress
        }
    
    @classmethod
    def greeting(cls) -> str:
        return T.greeting(cls.now().hour)
    
    @classmethod
    def uptime(cls, start: datetime) -> str:
        diff = cls.now() - start
        d, h, m = diff.days, diff.seconds//3600, (diff.seconds%3600)//60
        parts = []
        if d > 0: parts.append(f"{d} روز")
        if h > 0: parts.append(f"{h} ساعت")
        parts.append(f"{m} دقیقه")
        return " و ".join(parts)

TT = TehranTime()

# ════════════════════════════════════════
# DATABASE ENGINE (COMPLETE)
# ════════════════════════════════════════
class Database:
    """
    High-performance async SQLite database.
    All tables, indexes, and operations in one class.
    """
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        plan TEXT DEFAULT 'free',
        plan_until REAL DEFAULT 0,
        total_paid REAL DEFAULT 0,
        referred_by INTEGER DEFAULT 0,
        total_referrals INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s','now')),
        last_active REAL DEFAULT (strftime('%s','now'))
    );
    
    CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER PRIMARY KEY,
        daily_ai_count INTEGER DEFAULT 0,
        total_ai_count INTEGER DEFAULT 0,
        last_reset_day TEXT DEFAULT ''
    );
    
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        added_at REAL DEFAULT (strftime('%s','now')),
        UNIQUE(user_id, symbol)
    );
    
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        target_price REAL NOT NULL,
        alert_type TEXT DEFAULT 'above',
        active INTEGER DEFAULT 1,
        triggered INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s','now'))
    );
    
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
        status TEXT DEFAULT 'active',
        created_at REAL DEFAULT (strftime('%s','now'))
    );
    
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        receipt_file_id TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s','now')),
        processed_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS ai_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        created_at REAL DEFAULT (strftime('%s','now'))
    );
    
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 0,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s','now'))
    );
    
    CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);
    CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(user_id, active);
    CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
    CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
    CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlists(user_id);
    """
    
    def __init__(self, path: str = "ostadbot.db"):
        self.path = path
        self._lock = asyncio.Lock()
        self._queries = 0
        self._errors = 0
    
    async def init(self):
        """Initialize database"""
        try:
            async with self._lock:
                async with aiosqlite.connect(self.path) as conn:
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=-8000")
                    await conn.execute("PRAGMA foreign_keys=ON")
                    await conn.execute("PRAGMA busy_timeout=5000")
                    await conn.executescript(self.SCHEMA)
                    await conn.commit()
            logger.info(f"Database initialized: {self.path}")
            return True
        except Exception as e:
            logger.error(f"Database init failed: {e}")
            return False
    
    async def execute(self, query: str, params: tuple = ()) -> int:
        self._queries += 1
        try:
            async with aiosqlite.connect(self.path) as conn:
                cursor = await conn.execute(query, params)
                await conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self._errors += 1
            logger.error(f"SQL error: {e}")
            return 0
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        try:
            async with aiosqlite.connect(self.path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, params) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except:
            return None
    
    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        try:
            async with aiosqlite.connect(self.path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, params) as cursor:
                    return [dict(row) for row in await cursor.fetchall()]
        except:
            return []
    
    async def fetchval(self, query: str, params: tuple = (), default=None):
        row = await self.fetchone(query, params)
        return list(row.values())[0] if row else default
    
    async def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        return await self.fetchval(f"SELECT COUNT(*) FROM {table} WHERE {where}", params, 0)
    
    # ── User Operations ──
    
    async def get_user(self, uid: int) -> Optional[Dict]:
        return await self.fetchone("SELECT * FROM users WHERE user_id=?", (uid,))
    
    async def upsert_user(self, uid: int, username: str = "", full_name: str = ""):
        now = time.time()
        await self.execute("""
            INSERT INTO users(user_id, username, full_name, last_active)
            VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
            username=COALESCE(NULLIF(?,''),users.username),
            full_name=COALESCE(NULLIF(?,''),users.full_name),
            last_active=?
        """, (uid, username, full_name, now, username, full_name, now))
        await self.execute("INSERT OR IGNORE INTO user_state(user_id) VALUES(?)", (uid,))
    
    async def get_plan(self, uid: int) -> str:
        user = await self.get_user(uid)
        if not user: return "free"
        if user.get('is_banned'): return "banned"
        if user.get('plan') in ('vip','pro','elite'):
            if user.get('plan_until') and time.time() < user['plan_until']:
                return user['plan']
        return "free"
    
    async def is_premium(self, uid: int) -> bool:
        return await self.get_plan(uid) not in ("free", "banned")
    
    async def set_plan(self, uid: int, plan: str, days: int = 30):
        until = time.time() + (days * 86400)
        await self.execute("UPDATE users SET plan=?, plan_until=? WHERE user_id=?", (plan, until, uid))
        await self.log(uid, f"plan_upgraded", plan)
    
    async def get_ai_count(self, uid: int) -> int:
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        state = await self.fetchone("SELECT * FROM user_state WHERE user_id=?", (uid,))
        if not state:
            await self.execute("INSERT OR IGNORE INTO user_state(user_id,last_reset_day) VALUES(?,?)", (uid, today))
            return 0
        if state.get('last_reset_day') != today:
            await self.execute("UPDATE user_state SET daily_ai_count=0,last_reset_day=? WHERE user_id=?", (today, uid))
            return 0
        return state.get('daily_ai_count', 0)
    
    async def get_ai_limit(self, uid: int) -> int:
        plan = await self.get_plan(uid)
        limits = {"free": cfg.FREE_AI_PER_DAY, "vip": 50, "pro": 200, "elite": 999999}
        return limits.get(plan, cfg.FREE_AI_PER_DAY)
    
    async def inc_ai(self, uid: int) -> int:
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await self.execute(
            "UPDATE user_state SET daily_ai_count=daily_ai_count+1, total_ai_count=total_ai_count+1, last_reset_day=? WHERE user_id=?",
            (today, uid)
        )
        return await self.fetchval("SELECT daily_ai_count FROM user_state WHERE user_id=?", (uid,), 0)
    
    async def can_use_ai(self, uid: int) -> Tuple[bool, int, int]:
        used = await self.get_ai_count(uid)
        limit = await self.get_ai_limit(uid)
        return (used < limit, used, limit)
    
    # ── Payment Operations ──
    
    async def add_payment(self, uid: int, plan: str, amount: float) -> int:
        return await self.execute(
            "INSERT INTO payments(user_id, plan, amount) VALUES(?,?,?)",
            (uid, plan, amount)
        )
    
    async def approve_payment(self, pid: int, aid: int) -> bool:
        payment = await self.fetchone("SELECT * FROM payments WHERE id=? AND status='pending'", (pid,))
        if not payment: return False
        
        plan_days = cfg.PLANS.get(payment['plan'], {}).get('days', 30)
        await self.set_plan(payment['user_id'], payment['plan'], plan_days)
        await self.execute(
            "UPDATE payments SET status='approved', processed_at=? WHERE id=?",
            (time.time(), pid)
        )
        await self.log(payment['user_id'], "payment_approved", str(pid))
        return True
    
    # ── Alert Operations ──
    
    async def create_alert(self, uid: int, symbol: str, price: float, atype: str = "above") -> int:
        return await self.execute(
            "INSERT INTO alerts(user_id, symbol, target_price, alert_type) VALUES(?,?,?,?)",
            (uid, symbol.upper(), price, atype)
        )
    
    async def get_active_alerts(self, uid: int = None) -> List[Dict]:
        if uid:
            return await self.fetchall(
                "SELECT * FROM alerts WHERE user_id=? AND active=1 AND triggered=0 ORDER BY created_at DESC",
                (uid,)
            )
        return await self.fetchall("SELECT * FROM alerts WHERE active=1 AND triggered=0")
    
    async def trigger_alert(self, aid: int):
        await self.execute("UPDATE alerts SET triggered=1, triggered_at=? WHERE id=?", (time.time(), aid))
    
    # ── Watchlist Operations ──
    
    async def add_watchlist(self, uid: int, symbol: str) -> bool:
        max_items = 999 if await self.is_premium(uid) else cfg.FREE_WATCHLIST
        current = await self.count("watchlists", "user_id=?", (uid,))
        if current >= max_items: return False
        await self.execute("INSERT OR IGNORE INTO watchlists(user_id, symbol) VALUES(?,?)", (uid, symbol.upper()))
        return True
    
    async def get_watchlist(self, uid: int) -> List[Dict]:
        return await self.fetchall("SELECT * FROM watchlists WHERE user_id=? ORDER BY added_at DESC", (uid,))
    
    # ── Logging ──
    
    async def log(self, uid: int, action: str, details: str = ""):
        await self.execute("INSERT INTO logs(user_id, action, details) VALUES(?,?,?)", (uid, action, details))
    
    # ── Statistics ──
    
    async def stats(self) -> Dict:
        total = await self.count("users")
        premium = await self.count("users", "plan!='free' AND plan_until>?", (time.time(),))
        revenue = await self.fetchval("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved'", default=0)
        ai_queries = await self.fetchval("SELECT COALESCE(SUM(total_ai_count),0) FROM user_state", default=0)
        return {
            "total_users": total,
            "premium_users": premium,
            "total_revenue": revenue,
            "total_ai_queries": ai_queries,
            "conversion": round((premium/total*100),2) if total > 0 else 0,
        }

# Initialize database
db = Database(cfg.DATABASE_PATH)

# ════════════════════════════════════════
# END OF PART 1 - CONTINUE TO PART 2
# ════════════════════════════════════════

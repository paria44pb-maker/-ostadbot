"""
🦅 CryptoPulse-AI v5.0 | Ultimate Professional Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
سازنده: @Amir92aa
کانال: @CryptoPulse606
شماره کارت: 6063-7311-9625-4479
به نام: بهمرد
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ویژگی‌ها:
• هوش مصنوعی Groq (Llama 3.3)
• صرافی CoinEx
• تحلیل تکنیکال (RSI, MACD, Fibonacci, Price Action)
• زمان و تاریخ تهران
• سیستم VIP و درآمدزایی
• پنل مدیریت
• Railway Ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import json
import time
import hmac
import hashlib
import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from contextlib import asynccontextmanager

# Third-party imports
try:
    import aiosqlite
except ImportError:
    import sqlite3 as aiosqlite
    aiosqlite.connect = lambda path: sqlite3.connect(path)

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    FastAPI = None

try:
    from aiogram import Bot, Dispatcher, Router, F
    from aiogram.filters import CommandStart, StateFilter
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram.types import (
        Message, CallbackQuery, InlineKeyboardMarkup, 
        InlineKeyboardButton, Update
    )
    from aiogram.enums import ParseMode, ChatAction
    from aiogram.utils.keyboard import InlineKeyboardBuilder
except ImportError:
    Bot = Dispatcher = Router = None

try:
    from groq import Groq
except ImportError:
    Groq = None

# ═══════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CryptoPulse-AI")

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

def get_env(key: str, default: Any = "") -> Any:
    """Get environment variable with default"""
    return os.getenv(key, default)

def get_env_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer"""
    try:
        return int(os.getenv(key, str(default)))
    except:
        return default

def get_env_list(key: str, default: str = "") -> List[int]:
    """Get environment variable as list of integers"""
    val = os.getenv(key, default)
    if not val:
        return []
    try:
        return [int(x.strip()) for x in val.split(",") if x.strip().isdigit()]
    except:
        return []

# Bot Configuration
BOT_TOKEN = get_env("BOT_TOKEN")
WEBHOOK_URL = get_env("WEBHOOK_URL")
WEBHOOK_SECRET = get_env("WEBHOOK_SECRET", "cryptopulse_secret_2024")
GROQ_API_KEY = get_env("GROQ_API_KEY")
COINEX_KEY = get_env("COINEX_KEY")
COINEX_SECRET = get_env("COINEX_SECRET")
DATABASE_PATH = get_env("DATABASE_PATH", "cryptopulse.db")
PORT = get_env_int("PORT", 8000)
ADMIN_IDS = get_env_list("ADMIN_IDS")
ENVIRONMENT = get_env("ENVIRONMENT", "production")

# Business Configuration
APP_NAME = "CryptoPulse-AI"
APP_VERSION = "5.0.0"
CREATOR_USERNAME = "@Amir92aa"
CHANNEL_USERNAME = "@CryptoPulse606"
CARD_NUMBER = "6063-7311-9625-4479"
CARD_HOLDER = "بهمرد"
SUPPORT_CONTACT = "@Amir92aa"

# Pricing (Toman)
PRICING = {
    "vip": {"name": "VIP", "price": 199000, "days": 30, "ai_limit": 50, "alerts": 15, "watchlist": 20},
    "pro": {"name": "PRO", "price": 399000, "days": 30, "ai_limit": 200, "alerts": 50, "watchlist": 50},
    "elite": {"name": "ELITE", "price": 999000, "days": 90, "ai_limit": 999999, "alerts": 999, "watchlist": 999},
}

# Rate Limits
FREE_DAILY_AI = 5
GROQ_RPM_LIMIT = 25
GROQ_TPM_LIMIT = 5000
RATE_LIMIT_SECONDS = 1.5
WELCOME_BONUS_DAYS = 3

# ═══════════════════════════════════════════════════════════
# EMOJI BANK
# ═══════════════════════════════════════════════════════════

class Emoji:
    """Centralized emoji collection"""
    
    # Crypto & Trading
    ROCKET = "🚀"
    FIRE = "🔥"
    MONEY = "💰"
    COIN = "🪙"
    CHART = "📊"
    CHART_UP = "📈"
    CHART_DOWN = "📉"
    BULL = "🐂"
    BEAR = "🐻"
    TARGET = "🎯"
    CRYSTAL = "💠"
    DIAMOND = "💎"
    STAR = "⭐"
    SPARKLES = "✨"
    
    # Status
    CHECK = "✅"
    CROSS = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    QUESTION = "❓"
    LOCK = "🔒"
    UNLOCK = "🔓"
    KEY = "🔑"
    HOURGLASS = "⏳"
    
    # VIP & Users
    CROWN = "👑"
    ROBOT = "🤖"
    BRAIN = "🧠"
    EYE = "👁️"
    COOL = "😎"
    WOW = "😍"
    PRAY = "🙏"
    CLAP = "👏"
    MUSCLE = "💪"
    
    # UI Elements
    HOME = "🏠"
    BACK = "🔙"
    SETTINGS = "⚙️"
    SEARCH = "🔍"
    PLUS = "➕"
    MINUS = "➖"
    REFRESH = "🔄"
    BELL = "🔔"
    ENVELOPE = "📧"
    PHONE = "📱"
    GLOBE = "🌍"
    CALENDAR = "📅"
    CLOCK = "🕐"
    
    # Gifts & Celebration
    GIFT = "🎁"
    PARTY = "🎉"
    TROPHY = "🏆"
    MEDAL = "🥇"
    LIGHTNING = "⚡"
    
    # Technical
    SHIELD = "🛡️"
    SWORD = "⚔️"
    SCALE = "⚖️"
    MAGNET = "🧲"
    BULB = "💡"
    THERMOMETER = "🌡️"
    WAVE = "🌊"
    MOUNTAIN = "🏔️"
    SUN = "☀️"
    MOON = "🌙"
    
    # Arrows & Pointers
    UP = "⬆️"
    DOWN = "⬇️"
    RIGHT = "➡️"
    LEFT = "⬅️"
    POINT_UP = "☝️"
    POINT_DOWN = "👇"
    POINT_RIGHT = "👉"
    POINT_LEFT = "👈"
    TOP = "🔝"
    NEW = "🆕"
    FREE = "🆓"
    
    # Payment
    CARD = "💳"
    BANK = "🏦"
    WALLET = "👛"
    
    @classmethod
    def get_plan_icon(cls, plan: str) -> str:
        """Get icon for plan"""
        icons = {
            "free": cls.FREE,
            "vip": cls.CROWN,
            "pro": cls.DIAMOND,
            "elite": f"{cls.CROWN}{cls.DIAMOND}",
            "banned": cls.CROSS
        }
        return icons.get(plan, cls.FREE)
    
    @classmethod
    def get_direction_icon(cls, direction: str) -> str:
        """Get icon for trade direction"""
        if direction.upper() in ("LONG", "BUY", "خرید"):
            return cls.BULL
        elif direction.upper() in ("SHORT", "SELL", "فروش"):
            return cls.BEAR
        return cls.CHART
    
    @classmethod
    def get_change_icon(cls, change: float) -> str:
        """Get icon for price change"""
        if change > 0:
            return cls.CHART_UP
        elif change < 0:
            return cls.CHART_DOWN
        return cls.CHART
    
    @classmethod
    def get_rsi_status(cls, rsi: float) -> str:
        """Get RSI status with emoji"""
        if rsi < 30:
            return f"🟢 اشباع فروش ({rsi:.1f})"
        elif rsi > 70:
            return f"🔴 اشباع خرید ({rsi:.1f})"
        elif rsi > 50:
            return f"🟡 صعودی ({rsi:.1f})"
        else:
            return f"🟠 نزولی ({rsi:.1f})"
    
    @classmethod
    def get_trend_icon(cls, trend: str) -> str:
        """Get icon for trend"""
        if "صعودی" in trend:
            return cls.CHART_UP
        elif "نزولی" in trend:
            return cls.CHART_DOWN
        return cls.CHART

# Short alias
E = Emoji()

# ═══════════════════════════════════════════════════════════
# TEHRAN TIME MANAGER
# ═══════════════════════════════════════════════════════════

class TehranTime:
    """
    Tehran time manager with Persian calendar support.
    Handles timezone conversion, Persian dates, and trading sessions.
    """
    
    # Timezone offset for Tehran (UTC+3:30)
    TEHRAN_OFFSET = timedelta(hours=3, minutes=30)
    
    # Persian month names
    PERSIAN_MONTHS = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    # Persian day names
    PERSIAN_DAYS = [
        "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
    ]
    
    # Season definitions
    SEASONS = {
        "spring": "بهار 🌸",
        "summer": "تابستان ☀️",
        "autumn": "پاییز 🍂",
        "winter": "زمستان ❄️"
    }
    
    # Trading session definitions (Tehran time)
    TRADING_SESSIONS = {
        "asian": {"name": "آسیا 🌏", "start": 3, "end": 12},
        "european": {"name": "اروپا 🌍", "start": 12, "end": 19},
        "american": {"name": "آمریکا 🌎", "start": 19, "end": 24}
    }
    
    # ── Class Methods ──
    
    @classmethod
    def now(cls) -> datetime:
        """Get current Tehran time"""
        return datetime.now(timezone.utc) + cls.TEHRAN_OFFSET
    
    @classmethod
    def timestamp(cls) -> float:
        """Get current Tehran timestamp"""
        return cls.now().timestamp()
    
    @classmethod
    def from_timestamp(cls, ts: float) -> datetime:
        """Convert Unix timestamp to Tehran datetime"""
        return datetime.fromtimestamp(ts, tz=timezone.utc) + cls.TEHRAN_OFFSET
    
    @classmethod
    def format(cls, dt: Optional[datetime] = None, fmt: str = "full") -> str:
        """
        Format datetime in Persian style.
        
        Available formats:
        - full: "شنبه ۱۵ فروردین ۱۴۰۳ - ۱۴:۳۰:۴۵"
        - time: "۱۴:۳۰:۴۵"
        - date: "۱۵ فروردین ۱۴۰۳"
        - short: "۱۴۰۳/۰۱/۱۵ ۱۴:۳۰"
        - relative: "۵ دقیقه پیش"
        """
        if dt is None:
            dt = cls.now()
        
        if fmt == "full":
            day_name = cls.PERSIAN_DAYS[dt.weekday()]
            day = cls._persian_day(dt)
            month = cls.PERSIAN_MONTHS[cls._persian_month(dt) - 1]
            year = cls._persian_year(dt)
            time_str = dt.strftime("%H:%M:%S")
            return f"{day_name} {day} {month} {year} - {time_str}"
        
        elif fmt == "time":
            return dt.strftime("%H:%M:%S")
        
        elif fmt == "time_short":
            return dt.strftime("%H:%M")
        
        elif fmt == "date":
            day = cls._persian_day(dt)
            month = cls.PERSIAN_MONTHS[cls._persian_month(dt) - 1]
            year = cls._persian_year(dt)
            return f"{day} {month} {year}"
        
        elif fmt == "date_short":
            return f"{cls._persian_year(dt)}/{cls._persian_month(dt):02d}/{cls._persian_day(dt):02d}"
        
        elif fmt == "short":
            return f"{cls._persian_year(dt)}/{cls._persian_month(dt):02d}/{cls._persian_day(dt):02d} - {dt.strftime('%H:%M')}"
        
        elif fmt == "relative":
            return cls._relative_time(dt)
        
        elif fmt == "log":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def _persian_year(cls, dt: datetime) -> int:
        """Calculate Persian year"""
        if (dt.month, dt.day) >= (3, 21):
            return dt.year - 621
        return dt.year - 622
    
    @classmethod
    def _persian_month(cls, dt: datetime) -> int:
        """Calculate Persian month (1-12)"""
        if (dt.month, dt.day) >= (3, 21):
            persian_new_year = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo)
        else:
            persian_new_year = datetime(dt.year - 1, 3, 21, tzinfo=dt.tzinfo)
        
        days = (dt - persian_new_year).days
        month_lengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
        
        for i, length in enumerate(month_lengths, 1):
            if days < length:
                return i
            days -= length
        
        return 12
    
    @classmethod
    def _persian_day(cls, dt: datetime) -> int:
        """Calculate Persian day (1-31)"""
        if (dt.month, dt.day) >= (3, 21):
            persian_new_year = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo)
        else:
            persian_new_year = datetime(dt.year - 1, 3, 21, tzinfo=dt.tzinfo)
        
        days = (dt - persian_new_year).days
        month_lengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
        
        for length in month_lengths:
            if days < length:
                return days + 1
            days -= length
        
        return 29
    
    @classmethod
    def _relative_time(cls, dt: datetime) -> str:
        """Convert datetime to Persian relative time"""
        now = cls.now()
        diff = now - dt
        
        if diff.total_seconds() < 0:
            return "همین الان"
        
        seconds = int(diff.total_seconds())
        
        if seconds < 10:
            return "همین الان"
        elif seconds < 60:
            return f"{seconds} ثانیه پیش"
        elif seconds < 3600:
            return f"{seconds // 60} دقیقه پیش"
        elif seconds < 86400:
            return f"{seconds // 3600} ساعت پیش"
        elif seconds < 604800:
            return f"{seconds // 86400} روز پیش"
        elif seconds < 2592000:
            return f"{seconds // 604800} هفته پیش"
        else:
            return f"{seconds // 2592000} ماه پیش"
    
    @classmethod
    def get_season(cls, dt: Optional[datetime] = None) -> str:
        """Get current Persian season"""
        if dt is None:
            dt = cls.now()
        month = cls._persian_month(dt)
        if month <= 3:
            return cls.SEASONS["spring"]
        elif month <= 6:
            return cls.SEASONS["summer"]
        elif month <= 9:
            return cls.SEASONS["autumn"]
        return cls.SEASONS["winter"]
    
    @classmethod
    def is_weekend(cls, dt: Optional[datetime] = None) -> bool:
        """Check if it's Friday (weekend in Iran)"""
        if dt is None:
            dt = cls.now()
        return dt.weekday() == 4
    
    @classmethod
    def is_night(cls, dt: Optional[datetime] = None) -> bool:
        """Check if it's night time"""
        if dt is None:
            dt = cls.now()
        return dt.hour < 6 or dt.hour >= 22
    
    @classmethod
    def trading_session(cls, dt: Optional[datetime] = None) -> str:
        """Get current trading session"""
        if dt is None:
            dt = cls.now()
        hour = dt.hour
        
        if 3 <= hour < 12:
            return cls.TRADING_SESSIONS["asian"]["name"]
        elif 12 <= hour < 19:
            return cls.TRADING_SESSIONS["european"]["name"]
        else:
            return cls.TRADING_SESSIONS["american"]["name"]
    
    @classmethod
    def session_progress(cls, dt: Optional[datetime] = None) -> Dict:
        """Get current session progress details"""
        if dt is None:
            dt = cls.now()
        hour = dt.hour
        
        if 3 <= hour < 12:
            session = cls.TRADING_SESSIONS["asian"]
        elif 12 <= hour < 19:
            session = cls.TRADING_SESSIONS["european"]
        else:
            session = cls.TRADING_SESSIONS["american"]
        
        start = session["start"]
        end = session["end"]
        elapsed = hour - start
        remaining = end - hour
        total = end - start
        progress = (elapsed / total * 100) if total > 0 else 100
        
        return {
            "session": session["name"],
            "start": f"{start:02d}:00",
            "end": f"{end:02d}:00",
            "elapsed_hours": elapsed,
            "remaining_hours": remaining,
            "progress_percent": round(progress, 1)
        }
    
    @classmethod
    def greeting(cls) -> str:
        """Get time-appropriate greeting"""
        now = cls.now()
        hour = now.hour
        
        if hour < 6:
            return "نیمه‌شب بخیر 🌙"
        elif hour < 12:
            return "صبح بخیر ☀️"
        elif hour < 17:
            return "عصر بخیر 🌤️"
        elif hour < 22:
            return "شب بخیر 🌙"
        return "نیمه‌شب بخیر 🌙"

# ═══════════════════════════════════════════════════════════
# DATABASE MANAGER
# ═══════════════════════════════════════════════════════════

class Database:
    """SQLite database manager with async support"""
    
    SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        phone TEXT DEFAULT '',
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
        created_at REAL DEFAULT (strftime('%s', 'now')),
        last_active REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER PRIMARY KEY,
        daily_ai_count INTEGER DEFAULT 0,
        total_ai_count INTEGER DEFAULT 0,
        last_ai_at REAL DEFAULT 0,
        last_reset_day TEXT DEFAULT ''
    );
    
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        note TEXT DEFAULT '',
        added_at REAL DEFAULT (strftime('%s', 'now')),
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
        triggered_at REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
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
        timeframe TEXT DEFAULT '4h',
        status TEXT DEFAULT 'active',
        result TEXT DEFAULT '',
        profit_percent REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        closed_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'card',
        status TEXT DEFAULT 'pending',
        receipt_file_id TEXT DEFAULT '',
        admin_note TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0,
        processed_by INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        tokens_used INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_id INTEGER NOT NULL,
        earnings REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 0,
        action TEXT NOT NULL,
        level TEXT DEFAULT 'INFO',
        details TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);
    CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(user_id, active);
    CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
    CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
    CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
    """
    
    def __init__(self, db_path: str = "cryptopulse.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize database with schema"""
        try:
            async with self._lock:
                async with aiosqlite.connect(self.db_path) as conn:
                    await conn.executescript(self.SCHEMA_SQL)
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=-8000")
                    await conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def execute(self, query: str, params: tuple = ()) -> int:
        """Execute SQL and return lastrowid"""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor.lastrowid
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one row as dictionary"""
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
        """Fetch single value"""
        row = await self.fetchone(query, params)
        return list(row.values())[0] if row else default
    
    async def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        """Count rows"""
        return await self.fetchval(f"SELECT COUNT(*) FROM {table} WHERE {where}", params, 0)
    
    # ── User Methods ──
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return await self.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    async def upsert_user(self, user_id: int, username: str = "", full_name: str = "") -> None:
        """Create or update user"""
        now = time.time()
        await self.execute(
            """INSERT INTO users(user_id, username, full_name, last_active) 
               VALUES(?, ?, ?, ?) 
               ON CONFLICT(user_id) DO UPDATE SET 
               username = COALESCE(NULLIF(?, ''), users.username),
               full_name = COALESCE(NULLIF(?, ''), users.full_name),
               last_active = ?""",
            (user_id, username, full_name, now, username, full_name, now)
        )
        await self.execute(
            "INSERT OR IGNORE INTO user_state(user_id, last_reset_day) VALUES(?, date('now'))",
            (user_id,)
        )
    
    async def get_user_plan(self, user_id: int) -> str:
        """Get user's current effective plan"""
        user = await self.get_user(user_id)
        if not user:
            return "free"
        if user.get('is_banned'):
            return "banned"
        if user['plan'] in ('vip', 'pro', 'elite'):
            if user.get('plan_until') and time.time() < user['plan_until']:
                return user['plan']
        return "free"
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user has premium access"""
        return await self.get_user_plan(user_id) not in ("free", "banned")
    
    async def set_plan(self, user_id: int, plan: str, days: int = 30) -> None:
        """Set user plan"""
        plan_until = time.time() + (days * 86400)
        await self.execute(
            "UPDATE users SET plan = ?, plan_until = ? WHERE user_id = ?",
            (plan, plan_until, user_id)
        )
        await self.log(user_id, f"plan_changed_to_{plan}", f"Days: {days}")
    
    async def get_ai_limit(self, user_id: int) -> int:
        """Get user's daily AI limit"""
        plan = await self.get_user_plan(user_id)
        limits = {
            "free": FREE_DAILY_AI,
            "vip": PRICING["vip"]["ai_limit"],
            "pro": PRICING["pro"]["ai_limit"],
            "elite": PRICING["elite"]["ai_limit"],
            "banned": 0
        }
        return limits.get(plan, FREE_DAILY_AI)
    
    async def get_ai_count(self, user_id: int) -> int:
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
    
    async def increment_ai_count(self, user_id: int) -> int:
        """Increment AI usage counter"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await self.execute(
            """UPDATE user_state 
               SET daily_ai_count = daily_ai_count + 1, 
                   total_ai_count = total_ai_count + 1,
                   last_ai_at = ?,
                   last_reset_day = ?
               WHERE user_id = ?""",
            (time.time(), today, user_id)
        )
        return await self.fetchval(
            "SELECT daily_ai_count FROM user_state WHERE user_id = ?",
            (user_id,), 0
        )
    
    async def add_payment(self, user_id: int, plan: str, amount: float, method: str = "card") -> int:
        """Record a new payment"""
        return await self.execute(
            "INSERT INTO payments(user_id, plan, amount, payment_method) VALUES(?, ?, ?, ?)",
            (user_id, plan, amount, method)
        )
    
    async def approve_payment(self, payment_id: int, admin_id: int) -> bool:
        """Approve payment and activate user plan"""
        payment = await self.fetchone("SELECT * FROM payments WHERE id = ?", (payment_id,))
        if not payment:
            return False
        
        plan_days = PRICING.get(payment['plan'], {}).get('days', 30)
        
        await self.set_plan(payment['user_id'], payment['plan'], plan_days)
        await self.execute(
            "UPDATE payments SET status = 'approved', processed_at = ?, processed_by = ? WHERE id = ?",
            (time.time(), admin_id, payment_id)
        )
        
        # Handle referral commission
        user = await self.get_user(payment['user_id'])
        if user and user.get('referred_by') and user['referred_by'] != 0:
            commission = payment['amount'] * 0.20
            await self.execute(
                """UPDATE users 
                   SET total_earnings = total_earnings + ?, 
                       referral_earnings = referral_earnings + ? 
                   WHERE user_id = ?""",
                (commission, commission, user['referred_by'])
            )
        
        await self.log(payment['user_id'], "payment_approved", f"Payment ID: {payment_id}")
        return True
    
    async def log(self, user_id: int, action: str, details: str = "", level: str = "INFO") -> None:
        """Write to log"""
        await self.execute(
            "INSERT INTO logs(user_id, action, level, details) VALUES(?, ?, ?, ?)",
            (user_id, action, level, details)
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total = await self.count("users")
        premium = await self.count("users", "plan != 'free' AND plan_until > ?", (time.time(),))
        revenue = await self.fetchval(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'approved'", default=0
        )
        today_active = await self.count(
            "users", "date(last_active, 'unixepoch') = date('now')"
        )
        
        return {
            "total_users": total,
            "premium_users": premium,
            "conversion_rate": round((premium / total * 100), 2) if total > 0 else 0,
            "total_revenue": revenue,
            "today_active": today_active,
            "version": APP_VERSION,
            "timestamp": TehranTime.format(TehranTime.now(), "full")
        }

# Initialize database
db = Database(DATABASE_PATH)

# ═══════════════════════════════════════════════════════════
# GROQ AI ENGINE
# ═══════════════════════════════════════════════════════════

class GroqAIEngine:
    """Groq AI integration with rate limiting"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        if self.api_key and Groq is not None:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        self._request_times: List[float] = []
        self._daily_tokens = 0
        self._daily_reset = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    def _check_rate_limit(self) -> bool:
        """Check if within rate limits"""
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if today != self._daily_reset:
            self._daily_tokens = 0
            self._daily_reset = today
        
        return len(self._request_times) < GROQ_RPM_LIMIT and self._daily_tokens < GROQ_TPM_LIMIT
    
    async def ask(
        self,
        prompt: str,
        context: str = "",
        system_type: str = "default",
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> str:
        """Send question to Groq AI"""
        
        if not self.client:
            return "❌ کلید API هوش مصنوعی تنظیم نشده است."
        
        if not self._check_rate_limit():
            await asyncio.sleep(2)
        
        # System prompts
        system_prompts = {
            "default": "شما یک تحلیلگر حرفه‌ای بازار کریپتو به زبان فارسی هستید. تحلیل دقیق، عملی و با ذکر ریسک بدهید. از شکلک‌های مناسب استفاده کنید. هرگز وعده سود قطعی ندهید.",
            "technical": "شما یک تحلیلگر تکنیکال حرفه‌ای هستید. RSI، MACD، حمایت و مقاومت، فیبوناچی و روند را تحلیل کن.",
            "signal": "شما یک سیگنال‌دهنده حرفه‌ای هستید. سیگنال باید شامل: جهت معامله، قیمت ورود، حد ضرر، اهداف، اطمینان و نسبت ریسک به ریوارد باشد.",
        }
        
        system_prompt = system_prompts.get(system_type, system_prompts["default"])
        
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if context:
            messages.append({"role": "system", "content": f"اطلاعات بازار:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_running_loop()
                
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                )
                
                self._request_times.append(time.time())
                if response.usage:
                    self._daily_tokens += response.usage.total_tokens
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower():
                    if attempt < max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 3)
                        continue
                    return "⏳ سیستم هوش مصنوعی در حال حاضر مشغول است. لطفاً چند ثانیه دیگر تلاش کنید."
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                
                logger.error(f"Groq API error: {e}")
                return f"⚠️ خطا در ارتباط با هوش مصنوعی. لطفاً دوباره تلاش کنید."
        
        return "⚠️ پس از چند بار تلاش، پاسخی دریافت نشد."

# Initialize AI
ai_engine = GroqAIEngine()

# ═══════════════════════════════════════════════════════════
# COINEX EXCHANGE CLIENT
# ═══════════════════════════════════════════════════════════

class CoinExClient:
    """CoinEx exchange API client"""
    
    BASE_URL = "https://api.coinex.com/v2"
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key or COINEX_KEY
        self.api_secret = api_secret or COINEX_SECRET
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            if aiohttp is None:
                raise RuntimeError("aiohttp not installed")
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": f"CryptoPulse-AI/{APP_VERSION}"}
            )
        return self._session
    
    async def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if aiohttp is None:
            import urllib.request
            import urllib.parse
            if params:
                url += "?" + urllib.parse.urlencode(params)
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    return json.loads(response.read().decode())
            except Exception as e:
                return {"code": -1, "message": str(e)}
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                self._request_count += 1
                return await response.json()
        except asyncio.TimeoutError:
            return {"code": -1, "message": "Timeout"}
        except Exception as e:
            return {"code": -1, "message": str(e)}
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict:
        """Get ticker data"""
        result = await self._request("/spot/ticker", {"market": symbol})
        return result.get("data", {}) if result.get("code") == 0 else {}
    
    async def get_klines(self, symbol: str = "BTCUSDT", period: str = "1hour", limit: int = 100) -> List[Dict]:
        """Get kline/candlestick data"""
        result = await self._request("/spot/kline", {
            "market": symbol,
            "period": period,
            "limit": str(limit)
        })
        return result.get("data", []) if result.get("code") == 0 else []
    
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get tickers for multiple symbols"""
        results = {}
        for symbol in symbols:
            ticker = await self.get_ticker(symbol)
            if ticker:
                results[symbol] = ticker
        return results
    
    async def close(self):
        """Close session"""
        if self._session and not self._session.closed:
            await self._session.close()

# Initialize exchange
exchange = CoinExClient()

# ═══════════════════════════════════════════════════════════
# TECHNICAL ANALYZER
# ═══════════════════════════════════════════════════════════

class TechnicalAnalyzer:
    """Technical analysis calculator"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if np is None:
            return 50.0
        
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.maximum(deltas, 0)
        losses = np.maximum(-deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100.0
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return float(np.clip(rsi, 0, 100))
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD"""
        if np is None:
            return (0.0, 0.0, 0.0)
        
        if len(prices) < 35:
            return (0.0, 0.0, 0.0)
        
        def ema(data: List[float], period: int) -> float:
            if len(data) < period:
                return data[-1] if data else 0
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = ema12 - ema26
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line
        
        return (float(macd_line), float(signal_line), float(histogram))
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance"""
        if len(prices) < window:
            return (min(prices) if prices else 0, max(prices) if prices else 0)
        
        recent = prices[-window:]
        return (float(min(recent)), float(max(recent)))
    
    @staticmethod
    def fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        ratios = {
            "0%": 0,
            "23.6%": 0.236,
            "38.2%": 0.382,
            "50%": 0.5,
            "61.8%": 0.618,
            "78.6%": 0.786,
            "100%": 1.0
        }
        
        if diff > 0:
            return {name: low + (diff * ratio) for name, ratio in ratios.items()}
        else:
            return {name: high - (abs(diff) * ratio) for name, ratio in ratios.items()}
    
    @staticmethod
    def detect_trend(prices: List[float], short: int = 10, long: int = 30) -> str:
        """Detect market trend"""
        if np is None or len(prices) < long:
            return "خنثی ⚪"
        
        short_ma = np.mean(prices[-short:])
        long_ma = np.mean(prices[-long:])
        
        diff_percent = ((short_ma - long_ma) / long_ma) * 100
        
        if diff_percent > 2:
            return "صعودی قوی 🟢"
        elif diff_percent > 0:
            return "صعودی ملایم 🟡"
        elif diff_percent > -2:
            return "نزولی ملایم 🟠"
        else:
            return "نزولی قوی 🔴"

# Initialize analyzer
analyzer = TechnicalAnalyzer()

# ═══════════════════════════════════════════════════════════
# BOT STATES
# ═══════════════════════════════════════════════════════════

class BotStates(StatesGroup):
    """FSM States"""
    waiting_for_ai_question = State()
    waiting_for_payment_receipt = State()
    waiting_for_custom_symbol = State()
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()
    waiting_for_alert_type = State()

# ═══════════════════════════════════════════════════════════
# KEYBOARD BUILDER
# ═══════════════════════════════════════════════════════════

class KeyboardBuilder:
    """Keyboard factory"""
    
    @staticmethod
    def main_menu(plan: str = "free") -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.SEARCH} بازار", callback_data="menu_market")
        kb.button(text=f"{E.BRAIN} هوش مصنوعی", callback_data="menu_ai")
        kb.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="menu_analysis")
        kb.button(text=f"{E.BELL} هشدار قیمت", callback_data="menu_alerts")
        kb.button(text=f"{E.STAR} واچ‌لیست", callback_data="menu_watchlist")
        kb.button(text=f"{E.CLOCK} زمان تهران", callback_data="menu_time")
        
        if plan == "free":
            kb.button(text=f"{E.CROWN} ارتقا به VIP", callback_data="menu_vip")
        
        kb.button(text=f"{E.ROBOT} درباره ما", callback_data="menu_about")
        kb.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="menu_support")
        kb.adjust(3, 2, 2, 2)
        return kb.as_markup()
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.CROWN} VIP - ۱۹۹ هزار تومان", callback_data="buy_vip")
        kb.button(text=f"{E.DIAMOND} PRO - ۳۹۹ هزار تومان", callback_data="buy_pro")
        kb.button(text=f"{E.CROWN}{E.DIAMOND} ELITE - ۹۹۹ هزار تومان", callback_data="buy_elite")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        kb.adjust(1)
        return kb.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت به منوی اصلی", callback_data="main_menu")]
        ])
    
    @staticmethod
    def analysis_symbols() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]:
            kb.button(text=f"{E.CHART} {sym.replace('USDT', '')}", callback_data=f"analyze_{sym}")
        kb.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_symbol")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        kb.adjust(2)
        return kb.as_markup()

# ═══════════════════════════════════════════════════════════
# MESSAGE TEMPLATES
# ═══════════════════════════════════════════════════════════

class MessageTemplates:
    """Message template builder"""
    
    @staticmethod
    def welcome(user_name: str, plan: str, days_left: int) -> str:
        now = TehranTime.now()
        plan_icon = E.get_plan_icon(plan)
        plan_name = {"free": "رایگان", "vip": "VIP", "pro": "PRO", "elite": "ELITE"}.get(plan, "رایگان")
        
        return f"""
{E.ROCKET}{E.FIRE}{E.ROCKET} *{APP_NAME}* {E.ROCKET}{E.FIRE}{E.ROCKET}

{E.ROBOT} سلام *{user_name}* عزیز!
{E.WAVE} به پیشرفته‌ترین ربات تحلیل کریپتو خوش آمدید!

{E.CLOCK} *زمان تهران:* {TehranTime.format(now, 'full')}
{E.GLOBE} *فصل:* {TehranTime.get_season(now)}
{E.CHART} *سشن:* {TehranTime.trading_session(now)}

{E.DIAMOND}━━━━━━━━━━━━━━━━{E.DIAMOND}
{plan_icon} *پلن:* {plan_name}
{E.CALENDAR} *اعتبار:* {days_left} روز
{E.DIAMOND}━━━━━━━━━━━━━━━━{E.DIAMOND}

{E.POINT_DOWN} *منوی اصلی:*
"""
    
    @staticmethod
    def market_summary(tickers: Dict[str, Dict]) -> str:
        now = TehranTime.now()
        text = f"{E.GLOBE} *خلاصه بازار*\n{E.CLOCK} {TehranTime.format(now, 'time')}\n\n"
        
        for symbol, data in tickers.items():
            try:
                price = float(data.get('last', 0))
                change = float(data.get('change_percentage', 0))
                emoji = E.get_change_icon(change)
                name = symbol.replace('USDT', '')
                text += f"{emoji} *{name}:* ${price:,.2f} ({change:+.2f}%)\n"
            except:
                text += f"{E.CROSS} {symbol}: خطا\n"
        
        return text
    
    @staticmethod
    def technical_analysis(
        symbol: str, price: float, change: float,
        rsi: float, macd_val: float, macd_signal: float,
        support: float, resistance: float,
        fib_levels: Dict[str, float], trend: str,
        ai_analysis: str = ""
    ) -> str:
        change_emoji = E.get_change_icon(change)
        rsi_status = E.get_rsi_status(rsi)
        
        fib_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {value:.4f}"
            for name, value in list(fib_levels.items())[:5]
        ])
        
        return f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل {symbol}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت:* ${price:,.4f}
{change_emoji} *تغییر ۲۴h:* {change:+.2f}%

{E.THERMOMETER} *RSI:* {rsi_status}
{E.WAVE} *MACD:* {macd_val:.4f} | سیگنال: {macd_signal:.4f}

{E.SHIELD} *حمایت:* ${support:,.4f}
{E.SWORD} *مقاومت:* ${resistance:,.4f}

{E.CRYSTAL} *فیبوناچی:*
{fib_text}

{E.MAGNET} *روند:* {trend}

{E.CLOCK} *زمان:* {TehranTime.format(TehranTime.now(), 'full')}
""" + (f"\n\n{E.ROBOT} *تحلیل AI:*\n{ai_analysis}" if ai_analysis else "")
    
    @staticmethod
    def vip_plans_info() -> str:
        return f"""
{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های VIP* {E.CROWN}{E.CROWN}{E.CROWN}

{E.CROWN} *VIP - {PRICING['vip']['price']:,} تومان*
{E.POINT_RIGHT} {PRICING['vip']['ai_limit']} تحلیل AI در روز
{E.POINT_RIGHT} هشدار نامحدود
{E.POINT_RIGHT} پشتیبانی سریع

{E.DIAMOND} *PRO - {PRICING['pro']['price']:,} تومان*
{E.POINT_RIGHT} {PRICING['pro']['ai_limit']} تحلیل AI در روز
{E.POINT_RIGHT} همه امکانات VIP
{E.POINT_RIGHT} کپی تریدینگ

{E.CROWN}{E.DIAMOND} *ELITE - {PRICING['elite']['price']:,} تومان*
{E.POINT_RIGHT} تحلیل نامحدود
{E.POINT_RIGHT} مشاوره خصوصی

{E.GIFT} *هدیه:* {WELCOME_BONUS_DAYS} روز VIP رایگان!
{E.CARD} *شماره کارت:* `{CARD_NUMBER}`
{E.PERSON} *به نام:* {CARD_HOLDER}
"""
    
    @staticmethod
    def payment_instruction(plan: str) -> str:
        plan_info = PRICING.get(plan, PRICING['vip'])
        return f"""
{E.CARD} *پرداخت {plan_info['name']}*

{E.MONEY} *مبلغ:* {plan_info['price']:,} تومان
{E.CALENDAR} *مدت:* {plan_info['days']} روز

{E.BANK} *شماره کارت:*
`{CARD_NUMBER}`
{E.PERSON} *به نام:* {CARD_HOLDER}

{E.WARNING} *نکات:*
{E.POINT_RIGHT} مبلغ را دقیقاً واریز کنید
{E.POINT_RIGHT} رسید را اینجا ارسال کنید

{E.POINT_DOWN} پس از پرداخت روی دکمه زیر کلیک کنید:
"""
    
    @staticmethod
    def about() -> str:
        return f"""
{E.ROBOT} *{APP_NAME}*
{E.SPARKLES} نسخه {APP_VERSION}

{E.POINT_RIGHT} هوش مصنوعی Groq
{E.POINT_RIGHT} صرافی CoinEx
{E.POINT_RIGHT} تحلیل تکنیکال
{E.POINT_RIGHT} RSI, MACD, Fibonacci
{E.POINT_RIGHT} پرایس اکشن

{E.CROWN} *سازنده:* {CREATOR_USERNAME}
{E.PHONE} *کانال:* {CHANNEL_USERNAME}
{E.ENVELOPE} *پشتیبانی:* {SUPPORT_CONTACT}

{E.CLOCK} {TehranTime.format(TehranTime.now(), 'full')}
"""

# ═══════════════════════════════════════════════════════════
# TELEGRAM HANDLERS
# ═══════════════════════════════════════════════════════════

# Create router
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "کاربر"
    username = message.from_user.username or ""
    
    # Register user
    await db.upsert_user(user_id, username, full_name)
    
    # Process referral
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
        except:
            pass
    
    # Welcome bonus
    user = await db.get_user(user_id)
    if user and not user.get('welcome_bonus'):
        await db.execute(
            "UPDATE users SET plan = 'vip', plan_until = ?, welcome_bonus = 1 WHERE user_id = ?",
            (time.time() + WELCOME_BONUS_DAYS * 86400, user_id)
        )
    
    # Get plan info
    plan = await db.get_user_plan(user_id)
    days_left = 0
    if user and user.get('plan_until'):
        days_left = max(0, int((user['plan_until'] - time.time()) / 86400))
    
    # Send welcome
    welcome_text = MessageTemplates.welcome(full_name, plan, days_left)
    
    await message.answer(
        welcome_text,
        reply_markup=KeyboardBuilder.main_menu(plan),
        parse_mode="HTML"
    )
    await db.log(user_id, "start", f"Plan: {plan}")

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Return to main menu"""
    plan = await db.get_user_plan(callback.from_user.id)
    
    await callback.message.edit_text(
        f"{E.HOME} *منوی اصلی*\n\n{E.POINT_DOWN} گزینه مورد نظر را انتخاب کنید:",
        reply_markup=KeyboardBuilder.main_menu(plan),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_market")
async def callback_market(callback: CallbackQuery):
    """Show market overview"""
    await callback.answer("در حال دریافت داده‌ها...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    tickers = await exchange.get_multiple_tickers(symbols)
    
    text = MessageTemplates.market_summary(tickers)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{E.REFRESH} بروزرسانی", callback_data="menu_market")
    kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "menu_ai")
async def callback_ai(callback: CallbackQuery, state: FSMContext):
    """Start AI conversation"""
    user_id = callback.from_user.id
    
    ai_count = await db.get_ai_count(user_id)
    ai_limit = await db.get_ai_limit(user_id)
    
    if ai_count >= ai_limit:
        await callback.message.edit_text(
            f"{E.WARNING} *محدودیت هوش مصنوعی*\n\n"
            f"{E.HOURGLASS} شما {ai_count} از {ai_limit} سوال روزانه را استفاده کرده‌اید.\n\n"
            f"{E.LOCK} برای سوالات بیشتر، پلن خود را ارتقا دهید.",
            reply_markup=KeyboardBuilder.vip_plans(),
            parse_mode="HTML"
        )
        return
    
    await state.set_state(BotStates.waiting_for_ai_question)
    
    await callback.message.edit_text(
        f"{E.BRAIN} *پرسش از هوش مصنوعی*\n\n"
        f"{E.HOURGLASS} سوالات باقی‌مانده: {ai_limit - ai_count} از {ai_limit}\n\n"
        f"{E.POINT_DOWN} سوال خود را بفرستید:\n"
        f"مثال: تحلیل بیت‌کوین رو بده",
        reply_markup=KeyboardBuilder.back_to_main(),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_ai_question))
async def handle_ai_question(message: Message, state: FSMContext):
    """Process AI question"""
    user_id = message.from_user.id
    
    # Check limits
    ai_count = await db.get_ai_count(user_id)
    ai_limit = await db.get_ai_limit(user_id)
    
    if ai_count >= ai_limit:
        await message.answer(
            f"{E.WARNING} محدودیت روزانه تمام شده. لطفاً پلن خود را ارتقا دهید.",
            reply_markup=KeyboardBuilder.vip_plans()
        )
        await state.clear()
        return
    
    # Send typing
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # Get answer from AI
    answer = await ai_engine.ask(message.text)
    
    # Update counter
    await db.increment_ai_count(user_id)
    await db.execute(
        "INSERT INTO ai_conversations(user_id, question, answer) VALUES(?, ?, ?)",
        (user_id, message.text, answer)
    )
    
    new_count = await db.get_ai_count(user_id)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{E.BRAIN} سوال جدید", callback_data="menu_ai")
    kb.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
    
    await message.answer(
        f"{E.ROBOT} *پاسخ هوش مصنوعی:*\n\n{answer}\n\n{E.HOURGLASS} {new_count}/{ai_limit}",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    
    await db.log(user_id, "ai_question", message.text[:100])
    await state.clear()

@router.callback_query(F.data == "menu_analysis")
async def callback_analysis(callback: CallbackQuery):
    """Show analysis menu"""
    await callback.message.edit_text(
        f"{E.CHART} *تحلیل تکنیکال*\n\n{E.POINT_DOWN} نماد را انتخاب کنید:",
        reply_markup=KeyboardBuilder.analysis_symbols(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("analyze_"))
async def callback_analyze(callback: CallbackQuery):
    """Analyze specific symbol"""
    symbol = callback.data.replace("analyze_", "")
    await callback.answer(f"در حال تحلیل {symbol}...")
    
    try:
        # Get market data
        ticker = await exchange.get_ticker(symbol)
        if not ticker:
            raise Exception("No ticker data")
        
        price = float(ticker.get('last', 0))
        change = float(ticker.get('change_percentage', 0))
        
        # Get klines
        klines = await exchange.get_klines(symbol, "1hour", 100)
        
        prices = []
        highs = []
        lows = []
        
        for candle in klines:
            prices.append(float(candle.get('close', 0)))
            highs.append(float(candle.get('high', 0)))
            lows.append(float(candle.get('low', 0)))
        
        if not prices:
            raise Exception("No kline data")
        
        # Technical analysis
        rsi = analyzer.calculate_rsi(prices)
        macd_val, macd_signal, _ = analyzer.calculate_macd(prices)
        support, resistance = analyzer.calculate_support_resistance(prices)
        fib_levels = analyzer.fibonacci_levels(max(highs), min(lows))
        trend = analyzer.detect_trend(prices)
        
        # AI analysis
        ai_prompt = f"تحلیل {symbol} با قیمت {price} و RSI={rsi:.1f} و روند {trend}. سیگنال بده."
        ai_analysis = await ai_engine.ask(ai_prompt, "", "technical")
        
        # Build response
        text = MessageTemplates.technical_analysis(
            symbol, price, change, rsi, macd_val, macd_signal,
            support, resistance, fib_levels, trend, ai_analysis
        )
        
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.BELL} تنظیم هشدار", callback_data=f"alert_set_{symbol}")
        kb.button(text=f"{E.STAR} افزودن به واچ‌لیست", callback_data=f"watch_add_{symbol}")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="menu_analysis")
        kb.adjust(2, 1)
        
        await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await callback.message.edit_text(
            f"{E.CROSS} خطا در تحلیل {symbol}\n\n{E.POINT_RIGHT} لطفاً دوباره تلاش کنید.",
            reply_markup=KeyboardBuilder.back_to_main()
        )

@router.callback_query(F.data == "menu_time")
async def callback_time(callback: CallbackQuery):
    """Show Tehran time info"""
    now = TehranTime.now()
    session = TehranTime.session_progress()
    
    text = f"""
{E.CLOCK} *اطلاعات زمان تهران*

{E.CALENDAR} *تاریخ:* {TehranTime.format(now, 'date')}
{E.CLOCK} *ساعت:* {TehranTime.format(now, 'time')}
{E.GLOBE} *فصل:* {TehranTime.get_season(now)}
{E.WATCH} *روز:* {TehranTime.PERSIAN_DAYS[now.weekday()]}

{E.CHART} *سشن:* {session['session']}
{E.POINT_RIGHT} شروع: {session['start']} | پایان: {session['end']}
{E.POINT_RIGHT} پیشرفت: {session['progress_percent']}%

{E.INFO} *جمعه:* {'بله 🕌' if TehranTime.is_weekend(now) else 'خیر'}
{E.MOON} *شب:* {'بله 🌙' if TehranTime.is_night(now) else 'خیر ☀️'}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardBuilder.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_vip")
async def callback_vip(callback: CallbackQuery):
    """Show VIP plans"""
    await callback.message.edit_text(
        MessageTemplates.vip_plans_info(),
        reply_markup=KeyboardBuilder.vip_plans(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def callback_buy(callback: CallbackQuery):
    """Handle plan purchase"""
    plan = callback.data.replace("buy_", "")
    
    if plan not in PRICING:
        await callback.answer("پلن نامعتبر!", show_alert=True)
        return
    
    await callback.message.edit_text(
        MessageTemplates.payment_instruction(plan),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.CHECK} پرداخت کردم", callback_data=f"confirm_pay_{plan}")],
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="menu_vip")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_pay_"))
async def callback_confirm_pay(callback: CallbackQuery, state: FSMContext):
    """Confirm payment and request receipt"""
    plan = callback.data.replace("confirm_pay_", "")
    plan_info = PRICING.get(plan, PRICING['vip'])
    
    await state.set_state(BotStates.waiting_for_payment_receipt)
    await state.update_data(plan=plan, amount=plan_info['price'])
    
    await callback.message.edit_text(
        f"{E.ENVELOPE} *ارسال رسید پرداخت*\n\n"
        f"{E.POINT_DOWN} لطفاً عکس رسید پرداخت را ارسال کنید.\n\n"
        f"{E.WARNING} رسید باید شامل مبلغ و تاریخ باشد.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="menu_vip")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(StateFilter(BotStates.waiting_for_payment_receipt), F.photo)
async def handle_receipt(message: Message, state: FSMContext):
    """Receive payment receipt"""
    user_id = message.from_user.id
    data = await state.get_data()
    plan = data.get('plan', 'vip')
    amount = data.get('amount', 0)
    
    # Record payment
    payment_id = await db.add_payment(user_id, plan, amount)
    
    # Update with receipt
    await db.execute(
        "UPDATE payments SET receipt_file_id = ? WHERE id = ?",
        (message.photo[-1].file_id, payment_id)
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            admin_text = f"""
{E.BELL} *پرداخت جدید*
{E.PERSON} کاربر: {user_id}
{E.CROWN} پلن: {PRICING.get(plan, {}).get('name', plan)}
{E.MONEY} مبلغ: {amount:,} تومان
{E.CLOCK} زمان: {TehranTime.format(TehranTime.now(), 'full')}
{E.CARD} شناسه: {payment_id}
"""
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.CHECK} تایید", callback_data=f"admin_approve_{payment_id}")
            kb.button(text=f"{E.CROSS} رد", callback_data=f"admin_reject_{payment_id}")
            
            await message.bot.send_message(admin_id, admin_text, reply_markup=kb.as_markup(), parse_mode="HTML")
            await message.bot.send_photo(admin_id, message.photo[-1].file_id)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    # Confirm to user
    await message.answer(
        f"{E.CHECK} *رسید دریافت شد!*\n\n"
        f"{E.HOURGLASS} در حال بررسی...\n"
        f"{E.CLOCK} زمان تایید: ۵-۱۰ دقیقه\n\n"
        f"{E.ENVELOPE} *پشتیبانی:* {SUPPORT_CONTACT}",
        reply_markup=KeyboardBuilder.back_to_main(),
        parse_mode="HTML"
    )
    
    await db.log(user_id, "payment_receipt_sent", f"Payment ID: {payment_id}")
    await state.clear()

@router.callback_query(F.data.startswith("admin_approve_"))
async def callback_admin_approve(callback: CallbackQuery):
    """Admin: approve payment"""
    admin_id = callback.from_user.id
    
    if admin_id not in ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return
    
    payment_id = int(callback.data.replace("admin_approve_", ""))
    
    success = await db.approve_payment(payment_id, admin_id)
    
    if success:
        payment = await db.fetchone("SELECT * FROM payments WHERE id = ?", (payment_id,))
        
        # Notify user
        try:
            await callback.bot.send_message(
                payment['user_id'],
                f"{E.PARTY}{E.PARTY}{E.PARTY} *تبریک!*\n\n"
                f"{E.CHECK} پرداخت شما تایید شد!\n"
                f"{E.CROWN} پلن: {PRICING.get(payment['plan'], {}).get('name', payment['plan'])}\n"
                f"{E.ROCKET} از امکانات ویژه خود لذت ببرید!",
                parse_mode="HTML"
            )
        except:
            pass
        
        await callback.message.edit_text(f"{E.CHECK} پرداخت {payment_id} تایید شد.")
    else:
        await callback.answer("خطا در تایید!", show_alert=True)

@router.callback_query(F.data == "menu_about")
async def callback_about(callback: CallbackQuery):
    """Show about"""
    await callback.message.edit_text(
        MessageTemplates.about(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.PHONE} کانال", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton(text=f"{E.ENVELOPE} سازنده", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_support")
async def callback_support(callback: CallbackQuery):
    """Show support"""
    await callback.message.edit_text(
        f"{E.ENVELOPE} *پشتیبانی*\n\n"
        f"{E.POINT_RIGHT} آیدی: {SUPPORT_CONTACT}\n"
        f"{E.POINT_RIGHT} کانال: {CHANNEL_USERNAME}\n"
        f"{E.CLOCK} ۸ صبح تا ۱۲ شب\n\n"
        f"{E.CARD} *شماره کارت:* `{CARD_NUMBER}`\n"
        f"{E.PERSON} *به نام:* {CARD_HOLDER}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.ENVELOPE} پیام", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_watchlist")
async def callback_watchlist(callback: CallbackQuery):
    """Show watchlist"""
    user_id = callback.from_user.id
    items = await db.fetchall(
        "SELECT symbol, added_at FROM watchlists WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,)
    )
    
    if not items:
        text = f"{E.STAR} *واچ‌لیست*\n\n{E.INFO} هنوز نمادی اضافه نکرده‌اید."
    else:
        text = f"{E.STAR} *واچ‌لیست شما*\n\n"
        for i, item in enumerate(items, 1):
            added = TehranTime.format(TehranTime.from_timestamp(item['added_at']), "relative")
            text += f"{i}. {E.CHART} *{item['symbol']}* ({added})\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=KeyboardBuilder.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("watch_add_"))
async def callback_watch_add(callback: CallbackQuery):
    """Add to watchlist"""
    symbol = callback.data.replace("watch_add_", "")
    user_id = callback.from_user.id
    
    try:
        await db.execute(
            "INSERT OR IGNORE INTO watchlists(user_id, symbol) VALUES(?, ?)",
            (user_id, symbol)
        )
        await callback.answer(f"{E.CHECK} {symbol} به واچ‌لیست اضافه شد!", show_alert=True)
    except:
        await callback.answer(f"{E.CROSS} خطا!", show_alert=True)

@router.callback_query(F.data == "menu_alerts")
async def callback_alerts(callback: CallbackQuery):
    """Show alerts"""
    user_id = callback.from_user.id
    alerts = await db.fetchall(
        "SELECT * FROM alerts WHERE user_id = ? AND active = 1 ORDER BY created_at DESC",
        (user_id,)
    )
    
    if not alerts:
        text = f"{E.BELL} *هشدارها*\n\n{E.INFO} هیچ هشدار فعالی ندارید."
    else:
        text = f"{E.BELL} *هشدارهای فعال*\n\n"
        for alert in alerts:
            alert_type = "بالاتر ⬆️" if alert['alert_type'] == 'above' else "پایین‌تر ⬇️"
            text += f"{E.POINT_RIGHT} *{alert['symbol']}*: {alert_type} از {alert['target_price']}\n"
    
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{E.PLUS} هشدار جدید", callback_data="alert_new")
    kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await callback.answer()

# ═══════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════

# Create bot and dispatcher
try:
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
except Exception as e:
    logger.error(f"Failed to create bot instance: {e}")
    bot = None
dp = Dispatcher(storage=MemoryStorage()) if Dispatcher is not None else None

if dp is not None:
    dp.include_router(router)

# Start time
bot_start_time = TehranTime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    global bot_start_time
    
    logger.info(f"{E.ROCKET} Starting {APP_NAME} v{APP_VERSION}...")
    
    # Initialize database
    await db.initialize()
    
    # Set webhook
    if WEBHOOK_URL and BOT_TOKEN and bot is not None:
        try:
            await bot.set_webhook(
                url=f"{WEBHOOK_URL}/webhook",
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"Webhook set: {WEBHOOK_URL}/webhook")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    
    # Alert checker background task
    async def alert_checker():
        while True:
            try:
                active_alerts = await db.fetchall(
                    "SELECT * FROM alerts WHERE active = 1 AND triggered = 0"
                )
                
                for alert in active_alerts:
                    try:
                        ticker = await exchange.get_ticker(alert['symbol'])
                        if ticker:
                            current_price = float(ticker.get('last', 0))
                            target = alert['target_price']
                            
                            triggered = False
                            if alert['alert_type'] == 'above' and current_price >= target:
                                triggered = True
                            elif alert['alert_type'] == 'below' and current_price <= target:
                                triggered = True
                            
                            if triggered:
                                await db.execute(
                                    "UPDATE alerts SET triggered = 1, triggered_at = ? WHERE id = ?",
                                    (time.time(), alert['id'])
                                )
                                
                                if bot is not None:
                                    try:
                                        await bot.send_message(
                                            alert['user_id'],
                                            f"{E.BELL}{E.BELL}{E.BELL} *هشدار قیمت!*\n\n"
                                            f"{E.CHART} *{alert['symbol']}*\n"
                                            f"{E.MONEY} قیمت: {current_price}\n"
                                            f"{E.TARGET} هدف: {target}\n"
                                            f"{E.CLOCK} {TehranTime.format(TehranTime.now(), 'full')}",
                                            parse_mode="HTML"
                                        )
                                    except:
                                        pass
                    except:
                        pass
                
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Alert checker error: {e}")
                await asyncio.sleep(60)
    
    asyncio.create_task(alert_checker())
    
    logger.info(f"{E.ROCKET} {APP_NAME} started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    
    if bot is not None:
        try:
            await bot.delete_webhook()
        except:
            pass
        try:
            await bot.session.close()
        except:
            pass
    
    try:
        await exchange.close()
    except:
        pass
    
    logger.info(f"{E.WAVE} {APP_NAME} stopped")

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Professional Crypto Trading Bot",
    lifespan=lifespan
)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram webhook"""
    try:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != WEBHOOK_SECRET:
            raise HTTPException(403, "Invalid secret")
        
        data = await request.json()
        
        if dp is not None and bot is not None:
            update = Update(**data)
            await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({"status": "error"}, status_code=500)

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "time": TehranTime.format(TehranTime.now(), "full"),
        "version": APP_VERSION
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "creator": CREATOR_USERNAME,
        "channel": CHANNEL_USERNAME,
        "status": "running",
        "time": TehranTime.format(TehranTime.now(), "full")
    }

@app.get("/stats")
async def stats(request: Request):
    """Statistics (protected)"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(403)
    return await db.get_stats()

# ═══════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {APP_NAME} on port {PORT}")
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT, log_level="info")

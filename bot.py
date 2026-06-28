"""
🦅 CryptoPulse-AI v4.0 | Ultimate Professional Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
سازنده: @Amir92aa
کانال: @CryptoPulse606
شماره کارت: 6063-7311-9625-4479
به نام: بهمرد
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ویژگی‌ها:
• هوش مصنوعی Groq 🤖
• صرافی CoinEx 📊
• تحلیل تکنیکال کامل 📈
• RSI، MACD، فیبوناچی، پرایس اکشن
• زمان و تاریخ تهران 🕐
• سیستم VIP و درآمدزایی 💰
• پنل مدیریت 👑
• Railway Ready 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import re
import json
import time
import hmac
import math
import base64
import asyncio
import hashlib
import logging
import traceback
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
from enum import Enum

# Third-party imports
import aiosqlite
import aiohttp
import numpy as np
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, Update, WebAppInfo,
    InputFile, BufferedInputFile, ReplyKeyboardRemove
)
from aiogram.enums import ParseMode, ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.exceptions import TelegramAPIError
from groq import Groq, RateLimitError as GroqRateLimitError
from groq import APIStatusError as GroqAPIError

# ═══════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cryptopulse.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('CryptoPulse-AI')

# Environment variables with defaults
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "cryptopulse_v4_secret_2024")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_API_SECRET = os.getenv("COINEX_API_SECRET", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", "cryptopulse.db")
REDIS_URL = os.getenv("REDIS_URL", "")
PORT = int(os.getenv("PORT", "8000"))
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")  # development/production

# Constants
APP_NAME = "CryptoPulse-AI"
APP_VERSION = "4.0.0"
CREATOR_USERNAME = "@Amir92aa"
CHANNEL_USERNAME = "@CryptoPulse606"
CARD_NUMBER = "6063-7311-9625-4479"
CARD_HOLDER = "بهمرد"
SUPPORT_CONTACT = "@Amir92aa"

# Pricing (Toman)
PRICING = {
    "vip": {"name": "VIP 👑", "price": 199000, "days": 30, "ai_limit": 50, "alerts": 15, "watchlist": 20},
    "pro": {"name": "PRO 💎", "price": 399000, "days": 30, "ai_limit": 200, "alerts": 50, "watchlist": 50},
    "elite": {"name": "ELITE 👑💎", "price": 999000, "days": 90, "ai_limit": 999999, "alerts": 999, "watchlist": 999},
}

# Rate limits
FREE_DAILY_AI = 5
GROQ_RPM_LIMIT = 25
GROQ_TPM_LIMIT = 5000
RATE_LIMIT_SECONDS = 1.5
WELCOME_BONUS_DAYS = 3

# ═══════════════════════════════════════════════════════════════════════════
# 🎨 EMOJI & UI CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

class Emoji:
    """Comprehensive emoji collection"""
    # Crypto & Trading
    ROCKET = "🚀"
    FIRE = "🔥"
    MONEY = "💰"
    COIN = "🪙"
    CHART = "📊"
    CHART_UP = "📈"
    CHART_DOWN = "📉"
    CANDLE = "🕯️"
    BULL = "🐂"
    BEAR = "🐻"
    TARGET = "🎯"
    CRYSTAL = "💠"
    DIAMOND = "💎"
    GEM = "💎"
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
    HOURGLASS_DONE = "⌛"
    
    # Users & VIP
    CROWN = "👑"
    ROBOT = "🤖"
    BRAIN = "🧠"
    EYE = "👁️"
    COOL = "😎"
    WOW = "😍"
    THINK = "🤔"
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
    MUTE = "🔕"
    ENVELOPE = "📧"
    PHONE = "📱"
    GLOBE = "🌍"
    CALENDAR = "📅"
    CLOCK = "🕐"
    WATCH = "⌚"
    
    # Misc
    GIFT = "🎁"
    PARTY = "🎉"
    BALLOON = "🎈"
    TROPHY = "🏆"
    MEDAL = "🥇"
    RIBBON = "🎀"
    LIGHTNING = "⚡"
    ZAP = "⚡"
    SHIELD = "🛡️"
    SWORD = "⚔️"
    SCALE = "⚖️"
    MAGNET = "🧲"
    BULB = "💡"
    MICROSCOPE = "🔬"
    TELESCOPE = "🔭"
    THERMOMETER = "🌡️"
    WAVE = "🌊"
    MOUNTAIN = "🏔️"
    SUN = "☀️"
    MOON = "🌙"
    CLOUD = "☁️"
    RAIN = "🌧️"
    SNOW = "❄️"
    UMBRELLA = "☂️"
    
    # Numbers
    ONE = "1️⃣"
    TWO = "2️⃣"
    THREE = "3️⃣"
    FOUR = "4️⃣"
    FIVE = "5️⃣"
    
    # Arrows
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

E = Emoji()

# ═══════════════════════════════════════════════════════════════════════════
# 🕐 TEHRAN TIME ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class TehranTime:
    """
    Advanced Tehran time manager with Persian calendar support.
    Handles timezone conversion, Persian dates, trading sessions, and more.
    """
    
    TEHRAN_OFFSET = timedelta(hours=3, minutes=30)
    
    PERSIAN_MONTHS = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    PERSIAN_DAYS = [
        "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
    ]
    
    SEASONS = {
        "spring": "بهار 🌸",
        "summer": "تابستان ☀️",
        "autumn": "پاییز 🍂",
        "winter": "زمستان ❄️"
    }
    
    TRADING_SESSIONS = {
        "asian": {"name": "آسیا 🌏", "start": 3, "end": 12},
        "european": {"name": "اروپا 🌍", "start": 12, "end": 19},
        "american": {"name": "آمریکا 🌎", "start": 19, "end": 24}
    }
    
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
        """Convert timestamp to Tehran datetime"""
        return datetime.fromtimestamp(ts, tz=timezone.utc) + cls.TEHRAN_OFFSET
    
    @classmethod
    def format(cls, dt: datetime = None, fmt: str = "full") -> str:
        """
        Format datetime in various Persian styles.
        
        Formats:
        - full: "شنبه ۱۵ فروردین ۱۴۰۳ - ۱۴:۳۰:۴۵"
        - time: "۱۴:۳۰:۴۵"
        - date: "۱۵ فروردین ۱۴۰۳"
        - short: "۱۴۰۳/۰۱/۱۵ - ۱۴:۳۰"
        - relative: "۵ دقیقه پیش"
        - trading: "۱۴:۳۰ - ۱۵ فروردین"
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
        
        elif fmt == "trading":
            return f"{dt.strftime('%H:%M')} - {cls._persian_day(dt)} {cls.PERSIAN_MONTHS[cls._persian_month(dt)-1]}"
        
        elif fmt == "log":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        
        elif fmt == "file":
            return f"{cls._persian_year(dt)}{cls._persian_month(dt):02d}{cls._persian_day(dt):02d}_{dt.strftime('%H%M%S')}"
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def _persian_year(cls, dt: datetime) -> int:
        """Calculate approximate Persian year"""
        if (dt.month, dt.day) >= (3, 21):
            return dt.year - 621
        return dt.year - 622
    
    @classmethod
    def _persian_month(cls, dt: datetime) -> int:
        """Calculate approximate Persian month (1-12)"""
        # Find start of Persian year (March 21 or 22)
        if (dt.month, dt.day) >= (3, 21):
            persian_new_year = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo)
        else:
            persian_new_year = datetime(dt.year - 1, 3, 21, tzinfo=dt.tzinfo)
        
        days_since_new_year = (dt - persian_new_year).days
        
        # Persian month lengths
        month_lengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
        
        month = 1
        for length in month_lengths:
            if days_since_new_year < length:
                return month
            days_since_new_year -= length
            month += 1
        
        return 12
    
    @classmethod
    def _persian_day(cls, dt: datetime) -> int:
        """Calculate approximate Persian day (1-31)"""
        if (dt.month, dt.day) >= (3, 21):
            persian_new_year = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo)
        else:
            persian_new_year = datetime(dt.year - 1, 3, 21, tzinfo=dt.tzinfo)
        
        days_since_new_year = (dt - persian_new_year).days
        
        month_lengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
        
        for length in month_lengths:
            if days_since_new_year < length:
                return days_since_new_year + 1
            days_since_new_year -= length
        
        return 29  # Last day of Esfand
    
    @classmethod
    def _relative_time(cls, dt: datetime) -> str:
        """Convert datetime to relative Persian time"""
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
    def is_weekend(cls, dt: datetime = None) -> bool:
        """Check if it's Friday (weekend in Iran)"""
        if dt is None:
            dt = cls.now()
        return dt.weekday() == 4  # Friday
    
    @classmethod
    def is_night(cls, dt: datetime = None) -> bool:
        """Check if it's night time in Tehran"""
        if dt is None:
            dt = cls.now()
        return dt.hour < 6 or dt.hour >= 22
    
    @classmethod
    def trading_session(cls, dt: datetime = None) -> str:
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
    def next_session(cls, dt: datetime = None) -> str:
        """Get next trading session"""
        if dt is None:
            dt = cls.now()
        hour = dt.hour
        
        if hour < 3:
            return cls.TRADING_SESSIONS["asian"]["name"]
        elif hour < 12:
            return cls.TRADING_SESSIONS["european"]["name"]
        elif hour < 19:
            return cls.TRADING_SESSIONS["american"]["name"]
        else:
            return cls.TRADING_SESSIONS["asian"]["name"]
    
    @classmethod
    def session_progress(cls, dt: datetime = None) -> Dict:
        """Get current session progress"""
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
        total = end - start
        elapsed = hour - start
        remaining = end - hour
        progress = (elapsed / total) * 100 if total > 0 else 100
        
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
        """Get appropriate greeting based on time"""
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
        else:
            return "نیمه‌شب بخیر 🌙"
    
    @classmethod
    def get_uptime_string(cls, start_time: datetime) -> str:
        """Get uptime string"""
        now = cls.now()
        diff = now - start_time
        
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} روز")
        if hours > 0:
            parts.append(f"{hours} ساعت")
        parts.append(f"{minutes} دقیقه")
        
        return " و ".join(parts)

# ═══════════════════════════════════════════════════════════════════════════
# 🗄️ DATABASE ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class Database:
    """
    High-performance SQLite database manager with async support.
    Implements connection pooling, WAL mode, and optimized queries.
    """
    
    SCHEMA_VERSION = 4
    
    SCHEMA = f"""
    -- Users table
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
        last_active REAL DEFAULT (strftime('%s', 'now')),
        metadata TEXT DEFAULT '{{}}'
    );
    
    -- User state for rate limiting
    CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER PRIMARY KEY,
        daily_ai_count INTEGER DEFAULT 0,
        total_ai_count INTEGER DEFAULT 0,
        last_ai_at REAL DEFAULT 0,
        last_reset_day TEXT DEFAULT '',
        daily_signals INTEGER DEFAULT 0,
        last_signal_at REAL DEFAULT 0
    );
    
    -- Watchlists
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        note TEXT DEFAULT '',
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
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0,
        processed_by INTEGER DEFAULT 0
    );
    
    -- AI Conversations history
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
    
    -- Referral tracking
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_id INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        earnings REAL DEFAULT 0,
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
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Scheduled tasks
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL,
        task_data TEXT DEFAULT '{{}}',
        status TEXT DEFAULT 'pending',
        scheduled_at REAL DEFAULT 0,
        executed_at REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Bot settings
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT DEFAULT '',
        updated_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Schema version tracking
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);
    CREATE INDEX IF NOT EXISTS idx_users_referrer ON users(referred_by);
    CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(user_id, active);
    CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
    CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
    CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
    CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
    CREATE INDEX IF NOT EXISTS idx_logs_action ON logs(action);
    CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_ai_conv_user ON ai_conversations(user_id);
    CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlists(user_id);
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self._lock = asyncio.Lock()
        self._pool = []
        self._max_pool = 10
    
    async def init(self) -> bool:
        """Initialize database with optimized settings"""
        try:
            async with self._lock:
                async with aiosqlite.connect(self.db_path) as conn:
                    # Performance optimizations
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=-8000")  # 8MB cache
                    await conn.execute("PRAGMA foreign_keys=ON")
                    await conn.execute("PRAGMA busy_timeout=5000")
                    await conn.execute("PRAGMA temp_store=MEMORY")
                    
                    # Create schema
                    await conn.executescript(self.SCHEMA)
                    
                    # Check/update schema version
                    cursor = await conn.execute("SELECT MAX(version) FROM schema_version")
                    row = await cursor.fetchone()
                    current_version = row[0] if row[0] else 0
                    
                    if current_version < self.SCHEMA_VERSION:
                        await conn.execute(
                            "INSERT INTO schema_version(version) VALUES(?)",
                            (self.SCHEMA_VERSION,)
                        )
                    
                    await conn.commit()
                
                logger.info(f"Database initialized (v{self.SCHEMA_VERSION})")
                return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def execute(self, query: str, params: tuple = ()) -> int:
        """Execute a query and return lastrowid"""
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(query, params)
                await conn.commit()
                return cursor.lastrowid
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries"""
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.executemany(query, params_list)
                await conn.commit()
                return len(params_list)
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch a single row as dictionary"""
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
    
    async def fetchval(self, query: str, params: tuple = (), default=None):
        """Fetch a single value"""
        row = await self.fetchone(query, params)
        if row:
            return list(row.values())[0] if isinstance(row, dict) else row[0]
        return default
    
    async def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        """Count rows in a table"""
        result = await self.fetchval(
            f"SELECT COUNT(*) FROM {table} WHERE {where}",
            params
        )
        return result or 0
    
    # ═══════════════════════════════════════════
    # USER METHODS
    # ═══════════════════════════════════════════
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return await self.fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
    
    async def upsert_user(self, user_id: int, username: str = "", full_name: str = "") -> bool:
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
        return True
    
    async def get_user_plan(self, user_id: int) -> str:
        """Get user's current plan"""
        user = await self.get_user(user_id)
        if not user:
            return "free"
        
        if user['is_banned']:
            return "banned"
        
        if user['plan'] in ('vip', 'pro', 'elite'):
            if user['plan_until'] and time.time() < user['plan_until']:
                return user['plan']
        
        return "free"
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user has premium access"""
        return await self.get_user_plan(user_id) not in ("free", "banned")
    
    async def set_plan(self, user_id: int, plan: str, days: int = 30) -> bool:
        """Set user's plan"""
        until = time.time() + (days * 86400)
        await self.execute(
            "UPDATE users SET plan=?, plan_until=? WHERE user_id=?",
            (plan, until, user_id)
        )
        await self.log(user_id, f"plan_changed_to_{plan}", f"Days: {days}")
        return True
    
    async def get_ai_limit(self, user_id: int) -> int:
        """Get user's daily AI limit"""
        plan = await self.get_user_plan(user_id)
        limits = {
            "free": FREE_DAILY_AI,
            "vip": PRICING["vip"]["ai_limit"],
            "pro": PRICING["pro"]["ai_limit"],
            "elite": PRICING["elite"]["ai_limit"],
        }
        return limits.get(plan, FREE_DAILY_AI)
    
    async def get_ai_count(self, user_id: int) -> int:
        """Get user's daily AI usage count"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        state = await self.fetchone("SELECT * FROM user_state WHERE user_id=?", (user_id,))
        
        if not state:
            await self.execute(
                "INSERT OR IGNORE INTO user_state(user_id, last_reset_day) VALUES(?, ?)",
                (user_id, today)
            )
            return 0
        
        if state.get('last_reset_day') != today:
            await self.execute(
                "UPDATE user_state SET daily_ai_count=0, last_reset_day=? WHERE user_id=?",
                (today, user_id)
            )
            return 0
        
        return state.get('daily_ai_count', 0)
    
    async def increment_ai_count(self, user_id: int) -> int:
        """Increment user's AI usage count"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await self.execute(
            "UPDATE user_state SET daily_ai_count=daily_ai_count+1, total_ai_count=total_ai_count+1, last_ai_at=?, last_reset_day=? WHERE user_id=?",
            (time.time(), today, user_id)
        )
        count = await self.fetchval(
            "SELECT daily_ai_count FROM user_state WHERE user_id=?", (user_id,)
        )
        return count or 0
    
    async def add_payment(self, user_id: int, plan: str, amount: float, method: str = "card") -> int:
        """Record a payment"""
        return await self.execute(
            "INSERT INTO payments(user_id, plan, amount, payment_method) VALUES(?, ?, ?, ?)",
            (user_id, plan, amount, method)
        )
    
    async def approve_payment(self, payment_id: int, admin_id: int) -> bool:
        """Approve a payment and activate plan"""
        payment = await self.fetchone("SELECT * FROM payments WHERE id=?", (payment_id,))
        if not payment:
            return False
        
        plan_days = PRICING.get(payment['plan'], {}).get('days', 30)
        
        await self.set_plan(payment['user_id'], payment['plan'], plan_days)
        await self.execute(
            "UPDATE payments SET status='approved', processed_at=?, processed_by=? WHERE id=?",
            (time.time(), admin_id, payment_id)
        )
        
        # Handle referral commission
        user = await self.get_user(payment['user_id'])
        if user and user.get('referred_by'):
            commission = payment['amount'] * 0.20
            await self.execute(
                "UPDATE users SET total_earnings=total_earnings+?, referral_earnings=referral_earnings+? WHERE user_id=?",
                (commission, commission, user['referred_by'])
            )
        
        await self.log(payment['user_id'], "payment_approved", f"Payment ID: {payment_id}")
        return True
    
    async def log(self, user_id: int, action: str, details: str = "", level: str = "INFO") -> None:
        """Log an action"""
        await self.execute(
            "INSERT INTO logs(user_id, action, level, details) VALUES(?, ?, ?, ?)",
            (user_id, action, level, details)
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total_users = await self.count("users")
        premium_users = await self.count("users", "plan != 'free' AND plan_until > ?", (time.time(),))
        total_revenue = await self.fetchval(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='approved'"
        )
        today_users = await self.count(
            "users", "date(last_active, 'unixepoch') = date('now')"
        )
        total_ai_queries = await self.fetchval(
            "SELECT COALESCE(SUM(total_ai_count), 0) FROM user_state"
        )
        total_signals = await self.count("signals")
        pending_payments = await self.count("payments", "status='pending'")
        
        return {
            "total_users": total_users or 0,
            "premium_users": premium_users or 0,
            "conversion_rate": round((premium_users / total_users * 100), 2) if total_users else 0,
            "total_revenue": total_revenue or 0,
            "today_active": today_users or 0,
            "total_ai_queries": total_ai_queries or 0,
            "total_signals": total_signals or 0,
            "pending_payments": pending_payments or 0,
            "uptime": "Running",
            "version": APP_VERSION,
            "timestamp": TehranTime.format(TehranTime.now(), "full")
        }
    
    async def cleanup_old_logs(self, days: int = 30) -> int:
        """Clean up old logs"""
        cutoff = time.time() - (days * 86400)
        await self.execute("DELETE FROM logs WHERE created_at < ?", (cutoff,))
        return await self.count("logs")

# Initialize database
db = Database()

# ═══════════════════════════════════════════════════════════════════════════
# 🤖 GROQ AI ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class GroqAIEngine:
    """
    Advanced Groq AI integration with rate limiting, retry logic,
    and conversation context management.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self._request_times: List[float] = []
        self._daily_tokens: int = 0
        self._daily_reset: str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        self._cache: OrderedDict = OrderedDict()
        self._cache_max = 100
        
        # System prompts for different scenarios
        self.system_prompts = {
            "default": """شما یک دستیار حرفه‌ای تحلیل بازار کریپتو به زبان فارسی هستید.
            
            قوانین پاسخگویی:
            ۱. همیشه به فارسی روان و حرفه‌ای پاسخ بده
            ۲. از شکلک‌های مناسب استفاده کن
            ۳. تحلیل دقیق، عملی و بدون حاشیه بده
            ۴. حد ضرر و حد سود را مشخص کن
            ۵. ریسک‌ها را شفاف بگو
            ۶. هرگز وعده سود قطعی نده
            ۷. همیشه یادآوری کن که این تحلیل شخصی است
            ۸. از اعداد و ارقام دقیق استفاده کن
            ۹. روند کلی بازار را در نظر بگیر
            ۱۰. به اخبار و رویدادهای مهم اشاره کن""",
            
            "signal": """شما یک تحلیلگر سیگنال‌دهی کریپتو هستید.
            سیگنال باید شامل موارد زیر باشد:
            ۱. جهت معامله (LONG/SHORT)
            ۲. قیمت ورود دقیق
            ۳. حد ضرر
            ۴. حد سود (۳ سطح)
            ۵. میزان اطمینان (درصد)
            ۶. نسبت ریسک به ریوارد
            ۷. تایم‌فریم پیشنهادی
            ۸. دلیل سیگنال""",
            
            "technical": """شما یک تحلیلگر تکنیکال حرفه‌ای هستید.
            تحلیل باید شامل:
            ۱. وضعیت RSI
            ۲. وضعیت MACD
            ۳. سطوح حمایت و مقاومت
            ۴. سطوح فیبوناچی
            ۵. الگوهای کندل استیک
            ۶. روند کلی
            ۷. حجم معاملات""",
            
            "news": """شما یک تحلیلگر اخبار کریپتو هستید.
            اخبار را تحلیل کن و تاثیر آن بر بازار را بگو.
            به احساسات بازار (سنتیمنت) اشاره کن.""",
            
            "risk": """شما یک مدیر ریسک حرفه‌ای هستید.
            ریسک معامله را بررسی کن و پیشنهادات مدیریت سرمایه بده.
            حداکثر سرمایه مجاز برای این معامله را مشخص کن.""",
        }
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        # Reset daily counter
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if today != self._daily_reset:
            self._daily_tokens = 0
            self._daily_reset = today
        
        if len(self._request_times) >= GROQ_RPM_LIMIT:
            return False
        
        if self._daily_tokens >= GROQ_TPM_LIMIT:
            return False
        
        return True
    
    def _get_cache_key(self, prompt: str, context: str = "") -> str:
        """Generate cache key"""
        content = f"{prompt}:{context}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def ask(
        self,
        prompt: str,
        context: str = "",
        system_type: str = "default",
        user_profile: str = "",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        use_cache: bool = True
    ) -> str:
        """
        Ask Groq AI with full error handling and rate limiting.
        """
        if not self.client:
            return "❌ کلید API هوش مصنوعی تنظیم نشده است. لطفاً با پشتیبانی تماس بگیرید."
        
        # Check cache
        cache_key = self._get_cache_key(prompt, context)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Check rate limits
        if not self._check_rate_limit():
            wait_time = 60 - (time.time() - self._request_times[0]) if self._request_times else 5
            if wait_time > 0:
                await asyncio.sleep(min(wait_time, 5))
        
        # Build system prompt
        system_prompt = self.system_prompts.get(system_type, self.system_prompts["default"])
        if user_profile:
            system_prompt += f"\n\nپروفایل کاربر: {user_profile}"
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"اطلاعات بازار:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        # Call Groq with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_running_loop()
                
                def sync_call():
                    return self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=0.9,
                        frequency_penalty=0.1,
                        presence_penalty=0.1,
                    )
                
                start_time = time.time()
                response = await loop.run_in_executor(None, sync_call)
                response_time = time.time() - start_time
                
                # Update rate limit trackers
                self._request_times.append(time.time())
                if response.usage:
                    self._daily_tokens += response.usage.total_tokens
                
                answer = response.choices[0].message.content.strip()
                
                # Cache the result
                if use_cache and len(self._cache) >= self._cache_max:
                    self._cache.popitem(last=False)
                if use_cache:
                    self._cache[cache_key] = answer
                
                return answer
                
            except GroqRateLimitError:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 3
                    await asyncio.sleep(wait)
                    continue
                return "⏳ سیستم هوش مصنوعی در حال حاضر مشغول است. لطفاً چند ثانیه دیگر تلاش کنید."
                
            except GroqAPIError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                logger.error(f"Groq API error: {e}")
                return f"⚠️ خطا در ارتباط با هوش مصنوعی. لطفاً دوباره تلاش کنید."
                
            except Exception as e:
                logger.error(f"Unexpected Groq error: {e}")
                return f"❌ خطای غیرمنتظره در پردازش درخواست. لطفاً با پشتیبانی تماس بگیرید."
        
        return "⚠️ پس از چند بار تلاش، پاسخی دریافت نشد. لطفاً بعداً امتحان کنید."
    
    async def analyze_market(self, symbol: str, market_data: str = "") -> str:
        """Analyze market for a specific symbol"""
        prompt = f"""لطفاً تحلیل جامعی برای {symbol} ارائه بده شامل:
        ۱. تحلیل تکنیکال
        ۲. نقاط ورود و خروج
        ۳. حد ضرر پیشنهادی
        ۴. اهداف قیمتی
        ۵. ریسک و نسبت ریوارد"""
        return await self.ask(prompt, market_data, "default")
    
    async def generate_signal(self, symbol: str, market_data: str = "") -> str:
        """Generate trading signal"""
        prompt = f"یک سیگنال معاملاتی برای {symbol} صادر کن با ذکر تمام جزئیات."
        return await self.ask(prompt, market_data, "signal")
    
    async def analyze_risk(self, trade_details: str) -> str:
        """Analyze trade risk"""
        return await self.ask(trade_details, "", "risk")
    
    def clear_cache(self):
        """Clear AI response cache"""
        self._cache.clear()
    
    def get_stats(self) -> Dict:
        """Get AI engine statistics"""
        return {
            "requests_this_minute": len(self._request_times),
            "tokens_today": self._daily_tokens,
            "cache_size": len(self._cache),
            "rpm_limit": GROQ_RPM_LIMIT,
            "tpm_limit": GROQ_TPM_LIMIT,
        }

# Initialize AI engine
ai_engine = GroqAIEngine()

# ═══════════════════════════════════════════════════════════════════════════
# 📈 COINEX EXCHANGE CLIENT
# ═══════════════════════════════════════════════════════════════════════════

class CoinExClient:
    """Professional CoinEx exchange API client"""
    
    BASE_URL = "https://api.coinex.com/v2"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or COINEX_API_KEY
        self.api_secret = api_secret or COINEX_API_SECRET
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
        self._last_request_time = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": f"CryptoPulse-AI/{APP_VERSION}"}
            )
        return self._session
    
    def _generate_signature(self, method: str, path: str, body: str = "", timestamp: str = "") -> str:
        """Generate API signature"""
        if not self.api_secret:
            return ""
        message = f"{method}{path}{timestamp}{body}"
        return hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        body: Dict = None,
        auth_required: bool = False
    ) -> Dict[str, Any]:
        """Make API request with error handling"""
        
        # Rate limiting
        now = time.time()
        if now - self._last_request_time < 0.1:
            await asyncio.sleep(0.1)
        
        url = f"{self.BASE_URL}{endpoint}"
        path = endpoint
        
        # Build query string
        if params:
            sorted_params = sorted(params.items())
            qs = "&".join(f"{k}={v}" for k, v in sorted_params)
            url += f"?{qs}"
            path += f"?{qs}"
        
        # Build headers
        headers = {"Content-Type": "application/json"}
        
        if auth_required and self.api_key and self.api_secret:
            timestamp = str(int(time.time() * 1000))
            body_str = json.dumps(body) if body else ""
            headers.update({
                "X-COINEX-KEY": self.api_key,
                "X-COINEX-SIGN": self._generate_signature(method, path, body_str, timestamp),
                "X-COINEX-TIMESTAMP": timestamp,
                "X-COINEX-WINDOWTIME": "5000",
            })
        
        try:
            session = await self._get_session()
            
            if method == "GET":
                async with session.get(url, headers=headers) as response:
                    self._request_count += 1
                    self._last_request_time = time.time()
                    data = await response.json()
            elif method == "POST":
                async with session.post(url, headers=headers, json=body) as response:
                    self._request_count += 1
                    self._last_request_time = time.time()
                    data = await response.json()
            else:
                return {"code": -1, "message": f"Unsupported method: {method}"}
            
            return data
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout: {method} {endpoint}")
            return {"code": -1, "message": "Timeout"}
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error: {e}")
            return {"code": -1, "message": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"code": -1, "message": f"Error: {str(e)}"}
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict:
        """Get ticker for a symbol"""
        result = await self._request("GET", "/spot/ticker", {"market": symbol})
        if result.get("code") == 0:
            return result.get("data", {})
        return {}
    
    async def get_klines(
        self, symbol: str = "BTCUSDT", period: str = "1hour", limit: int = 100
    ) -> List[Dict]:
        """Get kline/candlestick data"""
        result = await self._request("GET", "/spot/kline", {
            "market": symbol,
            "period": period,
            "limit": str(limit)
        })
        if result.get("code") == 0:
            return result.get("data", [])
        return []
    
    async def get_depth(self, symbol: str = "BTCUSDT", limit: int = 20) -> Dict:
        """Get order book depth"""
        result = await self._request("GET", "/spot/depth", {
            "market": symbol,
            "limit": str(limit),
            "interval": "0"
        })
        if result.get("code") == 0:
            return result.get("data", {})
        return {}
    
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get multiple tickers at once"""
        results = {}
        for symbol in symbols:
            ticker = await self.get_ticker(symbol)
            if ticker:
                results[symbol] = ticker
        return results
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

# Initialize exchange client
exchange = CoinExClient()

# ═══════════════════════════════════════════════════════════════════════════
# 📊 TECHNICAL ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class TechnicalAnalyzer:
    """Comprehensive technical analysis calculator"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
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
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Calculate MACD indicator"""
        if len(prices) < slow + signal:
            return (0.0, 0.0, 0.0)
        
        def ema(data: List[float], period: int) -> float:
            if len(data) < period:
                return data[-1] if data else 0
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        
        # Simplified signal line calculation
        signal_line = macd_line * 0.9
        histogram = macd_line - signal_line
        
        return (float(macd_line), float(signal_line), float(histogram))
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        if len(prices) < window:
            return (min(prices) if prices else 0, max(prices) if prices else 0)
        
        recent = prices[-window:]
        return (float(min(recent)), float(max(recent)))
    
    @staticmethod
    def fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        ratios = {
            "0%": 0, "23.6%": 0.236, "38.2%": 0.382,
            "50%": 0.5, "61.8%": 0.618, "78.6%": 0.786, "100%": 1.0
        }
        
        if diff > 0:  # Uptrend
            return {name: low + (diff * ratio) for name, ratio in ratios.items()}
        else:  # Downtrend
            return {name: high - (abs(diff) * ratio) for name, ratio in ratios.items()}
    
    @staticmethod
    def detect_trend(prices: List[float], short: int = 10, long: int = 30) -> str:
        """Detect market trend"""
        if len(prices) < long:
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
    
    @staticmethod
    def volume_profile(volumes: List[float], prices: List[float]) -> Dict:
        """Analyze volume profile"""
        if len(volumes) < 20:
            return {"avg": 0, "trend": "نرمال", "signal": "خنثی"}
        
        avg_vol = np.mean(volumes[-20:])
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        if vol_ratio > 2:
            if prices[-1] > prices[-2]:
                return {"avg": float(avg_vol), "trend": "حجم بسیار بالا", "signal": "خرید قوی"}
            else:
                return {"avg": float(avg_vol), "trend": "حجم بسیار بالا", "signal": "فروش قوی"}
        elif vol_ratio > 1.5:
            return {"avg": float(avg_vol), "trend": "حجم بالا", "signal": "فعال"}
        elif vol_ratio < 0.5:
            return {"avg": float(avg_vol), "trend": "حجم پایین", "signal": "نوسان کم"}
        
        return {"avg": float(avg_vol), "trend": "نرمال", "signal": "خنثی"}
    
    @staticmethod
    def market_structure(highs: List[float], lows: List[float]) -> Dict:
        """Analyze market structure (HH, HL, LH, LL)"""
        if len(highs) < 4 or len(lows) < 4:
            return {"structure": "نامشخص", "bias": "خنثی"}
        
        # Check last two swing highs and lows
        last_high = highs[-1]
        prev_high = highs[-3] if len(highs) >= 3 else highs[-2]
        last_low = lows[-1]
        prev_low = lows[-3] if len(lows) >= 3 else lows[-2]
        
        if last_high > prev_high and last_low > prev_low:
            return {"structure": "HH + HL", "bias": "صعودی 🟢"}
        elif last_high < prev_high and last_low < prev_low:
            return {"structure": "LH + LL", "bias": "نزولی 🔴"}
        else:
            return {"structure": "مختلط", "bias": "خنثی ⚪"}

# Initialize analyzer
analyzer = TechnicalAnalyzer()

# ═══════════════════════════════════════════════════════════════════════════
# 🎮 TELEGRAM BOT HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

class BotStates(StatesGroup):
    """FSM States for bot conversations"""
    # AI
    waiting_for_ai_question = State()
    
    # Payment
    waiting_for_payment_receipt = State()
    waiting_for_payment_amount = State()
    waiting_for_wallet_address = State()
    
    # Custom symbol
    waiting_for_custom_symbol = State()
    
    # Alert
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()
    waiting_for_alert_type = State()
    
    # Feedback
    waiting_for_feedback = State()
    
    # Broadcast
    waiting_for_broadcast_message = State()

# Initialize bot
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
main_router = Router()

# ═══════════════════════════════════════════════════════════
# KEYBOARD BUILDERS
# ═══════════════════════════════════════════════════════════

class Keyboards:
    """Keyboard factory for all bot keyboards"""
    
    @staticmethod
    def main_menu(plan: str = "free") -> InlineKeyboardMarkup:
        """Build main menu keyboard"""
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.SEARCH} بازار", callback_data="menu_market")
        kb.button(text=f"{E.BRAIN} AI", callback_data="menu_ai")
        kb.button(text=f"{E.CHART} تحلیل", callback_data="menu_analysis")
        kb.button(text=f"{E.BELL} هشدار", callback_data="menu_alerts")
        kb.button(text=f"{E.STAR} واچ‌لیست", callback_data="menu_watchlist")
        kb.button(text=f"{E.CLOCK} زمان", callback_data="menu_time")
        
        if plan == "free":
            kb.button(text=f"{E.CROWN} VIP", callback_data="menu_vip")
        
        kb.button(text=f"{E.ROBOT} درباره", callback_data="menu_about")
        kb.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="menu_support")
        kb.adjust(3, 3, 1, 2)
        return kb.as_markup()
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """Build VIP plans keyboard"""
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.CROWN} VIP - ۱۹۹", callback_data="buy_vip")
        kb.button(text=f"{E.DIAMOND} PRO - ۳۹۹", callback_data="buy_pro")
        kb.button(text=f"{E.CROWN}{E.DIAMOND} ELITE - ۹۹۹", callback_data="buy_elite")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        kb.adjust(1)
        return kb.as_markup()
    
    @staticmethod
    def analysis_symbols() -> InlineKeyboardMarkup:
        """Build analysis symbols keyboard"""
        kb = InlineKeyboardBuilder()
        for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]:
            kb.button(text=f"{E.CHART} {sym.replace('USDT', '')}", callback_data=f"analyze_{sym}")
        kb.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_symbol")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        kb.adjust(2)
        return kb.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Simple back button"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت به منوی اصلی", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment(plan: str) -> InlineKeyboardMarkup:
        """Payment confirmation keyboard"""
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.CHECK} پرداخت کردم", callback_data=f"confirm_pay_{plan}")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="menu_vip")
        return kb.as_markup()

# ═══════════════════════════════════════════════════════════
# MESSAGE TEMPLATES
# ═══════════════════════════════════════════════════════════

class Templates:
    """Message template builder"""
    
    @staticmethod
    def welcome(user_name: str, plan: str, days_left: int, greeting: str) -> str:
        """Build welcome message"""
        plan_icons = {"free": "🆓", "vip": "👑", "pro": "💎", "elite": "👑💎", "banned": "🚫"}
        plan_names = {"free": "رایگان", "vip": "VIP", "pro": "PRO", "elite": "ELITE", "banned": "مسدود"}
        
        now = TehranTime.now()
        
        return f"""
{E.ROCKET}{E.FIRE}{E.ROCKET} *{APP_NAME}* {E.ROCKET}{E.FIRE}{E.ROCKET}
{E.SPARKLES} نسخه {APP_VERSION}

{E.ROBOT} {greeting} *{user_name}* عزیز!
{E.WAVE} به پیشرفته‌ترین ربات تحلیل کریپتو خوش آمدید!

{E.CLOCK} *زمان تهران:* {TehranTime.format(now, 'full')}
{E.GLOBE} *فصل:* {TehranTime.get_season(now)}
{E.CHART} *سشن:* {TehranTime.trading_session(now)}

{E.DIAMOND}━{'━'*20}━{E.DIAMOND}
{plan_icons.get(plan, '🆓')} *پلن شما:* {plan_names.get(plan, 'رایگان')}
{E.CALENDAR} *اعتبار:* {days_left} روز
{E.HOURGLASS} *سوالات AI امروز:* در حال بارگذاری...
{E.DIAMOND}━{'━'*20}━{E.DIAMOND}

{E.POINT_DOWN} *منوی اصلی:*"""
    
    @staticmethod
    def market_summary(tickers: Dict[str, Dict]) -> str:
        """Build market summary"""
        now = TehranTime.now()
        text = f"{E.GLOBE} *خلاصه بازار*\n{E.CLOCK} {TehranTime.format(now, 'time')}\n\n"
        
        for symbol, data in tickers.items():
            try:
                price = float(data.get('last', 0))
                change = float(data.get('change_percentage', 0))
                emoji = E.CHART_UP if change > 0 else E.CHART_DOWN
                name = symbol.replace('USDT', '')
                text += f"{emoji} *{name}:* ${price:,.2f} ({change:+.2f}%)\n"
            except:
                text += f"{E.CROSS} {symbol}: خطا\n"
        
        return text
    
    @staticmethod
    def technical_analysis_card(
        symbol: str, price: float, change: float,
        rsi: float, macd: float, macd_signal: float,
        support: float, resistance: float,
        fib_levels: Dict[str, float], trend: str,
        volume_info: Dict, market_structure: Dict,
        ai_analysis: str = ""
    ) -> str:
        """Build comprehensive technical analysis card"""
        
        change_emoji = E.CHART_UP if change > 0 else E.CHART_DOWN
        rsi_status = "🟢 اشباع فروش" if rsi < 30 else "🔴 اشباع خرید" if rsi > 70 else "🟡 خنثی"
        macd_emoji = "📈" if macd > macd_signal else "📉"
        
        fib_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {value:.4f}"
            for name, value in list(fib_levels.items())[:5]
        ])
        
        return f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل {symbol}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت:* ${price:,.4f}
{change_emoji} *تغییر ۲۴h:* {change:+.2f}%

{E.THERMOMETER} *اندیکاتورها:*
{E.POINT_RIGHT} RSI (14): {rsi:.1f} ({rsi_status})
{E.POINT_RIGHT} MACD: {macd:.4f} {macd_emoji}
{E.POINT_RIGHT} سیگنال: {macd_signal:.4f}

{E.SHIELD} *حمایت:* ${support:,.4f}
{E.SWORD} *مقاومت:* ${resistance:,.4f}

{E.CRYSTAL} *فیبوناچی:*
{fib_text}

{E.MAGNET} *روند:* {trend}
{E.WAVE} *حجم:* {volume_info.get('signal', 'نرمال')}
{E.MOUNTAIN} *ساختار:* {market_structure.get('bias', 'خنثی')}

{E.CLOCK} *زمان تحلیل:* {TehranTime.format(TehranTime.now(), 'full')}
""" + (f"\n\n{E.ROBOT} *تحلیل AI:*\n{ai_analysis}" if ai_analysis else "")
    
    @staticmethod
    def vip_plans_info() -> str:
        """Build VIP plans information"""
        return f"""
{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های VIP* {E.CROWN}{E.CROWN}{E.CROWN}

{E.CROWN} *VIP - ۱۹۹,۰۰۰ تومان*
{E.POINT_RIGHT} {PRICING['vip']['ai_limit']} تحلیل AI در روز
{E.POINT_RIGHT} {PRICING['vip']['alerts']} هشدار فعال
{E.POINT_RIGHT} واچ‌لیست {PRICING['vip']['watchlist']} تایی
{E.POINT_RIGHT} سیگنال‌های VIP
{E.POINT_RIGHT} پشتیبانی سریع

{E.DIAMOND} *PRO - ۳۹۹,۰۰۰ تومان*
{E.POINT_RIGHT} {PRICING['pro']['ai_limit']} تحلیل AI در روز
{E.POINT_RIGHT} همه امکانات VIP
{E.POINT_RIGHT} کپی تریدینگ
{E.POINT_RIGHT} گزارش روزانه

{E.CROWN}{E.DIAMOND} *ELITE - ۹۹۹,۰۰۰ تومان*
{E.POINT_RIGHT} تحلیل نامحدود AI
{E.POINT_RIGHT} مشاوره خصوصی
{E.POINT_RIGHT} ربات اختصاصی
{E.POINT_RIGHT} همه امکانات PRO

{E.GIFT} *هدیه:* {WELCOME_BONUS_DAYS} روز VIP رایگان!

{E.CARD} *شماره کارت:* `{CARD_NUMBER}`
{E.PERSON} *به نام:* {CARD_HOLDER}
"""
    
    @staticmethod
    def payment_instruction(plan: str) -> str:
        """Build payment instruction"""
        plan_info = PRICING.get(plan, PRICING['vip'])
        
        return f"""
{E.CARD} *پرداخت اشتراک {plan_info['name']}*

{E.MONEY} *مبلغ:* {plan_info['price']:,} تومان
{E.CALENDAR} *مدت:* {plan_info['days']} روز

{E.BANK} *شماره کارت:*
`{CARD_NUMBER}`

{E.PERSON} *به نام:* {CARD_HOLDER}

{E.WARNING} *نکات مهم:*
{E.POINT_RIGHT} مبلغ را دقیقاً واریز کنید
{E.POINT_RIGHT} پس از پرداخت، رسید را اینجا ارسال کنید
{E.POINT_RIGHT} آیدی تلگرام خود را در توضیحات بنویسید
{E.POINT_RIGHT} تایید پرداخت: ۵-۱۰ دقیقه

{E.POINT_DOWN} پس از پرداخت، روی دکمه زیر کلیک کنید:
"""
    
    @staticmethod
    def about_bot() -> str:
        """Build about bot message"""
        return f"""
{E.ROBOT} *{APP_NAME}*
{E.SPARKLES} نسخه {APP_VERSION}

{E.LIGHTNING} پیشرفته‌ترین ربات تحلیل کریپتو

{E.BRAIN} *امکانات:*
{E.POINT_RIGHT} هوش مصنوعی Groq (Llama 3.3)
{E.POINT_RIGHT} اتصال به صرافی CoinEx
{E.POINT_RIGHT} تحلیل تکنیکال کامل
{E.POINT_RIGHT} RSI, MACD, فیبوناچی
{E.POINT_RIGHT} پرایس اکشن و ساختار بازار
{E.POINT_RIGHT} هشدار هوشمند قیمت
{E.POINT_RIGHT} سیستم VIP و درآمدزایی

{E.CROWN} *سازنده:* {CREATOR_USERNAME}
{E.PHONE} *کانال:* {CHANNEL_USERNAME}
{E.ENVELOPE} *پشتیبانی:* {SUPPORT_CONTACT}

{E.CLOCK} *زمان سرور:* {TehranTime.format(TehranTime.now(), 'full')}
"""

# ═══════════════════════════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════════════════════════

# Start time for uptime tracking
bot_start_time = TehranTime.now()

@main_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "کاربر"
    username = message.from_user.username or ""
    
    # Register/update user
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
                        "UPDATE users SET referred_by=?, total_referrals=total_referrals+1 WHERE user_id=?",
                        (referrer_id, referrer_id)
                    )
                    await db.execute(
                        "INSERT OR IGNORE INTO referrals(referrer_id, referred_id) VALUES(?, ?)",
                        (referrer_id, user_id)
                    )
        except:
            pass
    
    # Apply welcome bonus
    user = await db.get_user(user_id)
    if user and not user.get('welcome_bonus'):
        await db.execute(
            "UPDATE users SET plan='vip', plan_until=?, welcome_bonus=1 WHERE user_id=?",
            (time.time() + WELCOME_BONUS_DAYS * 86400, user_id)
        )
    
    # Get current plan
    plan = await db.get_user_plan(user_id)
    
    # Calculate days left
    days_left = 0
    if user and user.get('plan_until'):
        days_left = max(0, int((user['plan_until'] - time.time()) / 86400))
    
    # Build welcome message
    greeting = TehranTime.greeting()
    welcome_text = Templates.welcome(full_name, plan, days_left, greeting)
    
    await message.answer(
        welcome_text,
        reply_markup=Keyboards.main_menu(plan),
        parse_mode="HTML"
    )
    
    await db.log(user_id, "start", f"Plan: {plan}")

@main_router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    """Return to main menu"""
    user_id = callback.from_user.id
    plan = await db.get_user_plan(user_id)
    
    await callback.message.edit_text(
        f"{E.HOME} *منوی اصلی*\n\n{E.POINT_DOWN} گزینه مورد نظر را انتخاب کنید:",
        reply_markup=Keyboards.main_menu(plan),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data == "menu_market")
async def market_overview(callback: CallbackQuery):
    """Show market overview"""
    await callback.answer("در حال دریافت داده‌های بازار...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    tickers = await exchange.get_multiple_tickers(symbols)
    
    text = Templates.market_summary(tickers)
    
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{E.REFRESH} بروزرسانی", callback_data="menu_market")
    kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@main_router.callback_query(F.data == "menu_ai")
async def ai_menu(callback: CallbackQuery, state: FSMContext):
    """Start AI conversation"""
    user_id = callback.from_user.id
    
    ai_count = await db.get_ai_count(user_id)
    ai_limit = await db.get_ai_limit(user_id)
    
    if ai_count >= ai_limit:
        await callback.message.edit_text(
            f"{E.WARNING} *محدودیت هوش مصنوعی*\n\n"
            f"{E.HOURGLASS} شما {ai_count} از {ai_limit} سوال روزانه را استفاده کرده‌اید.\n\n"
            f"{E.LOCK} برای سوالات بیشتر، پلن خود را ارتقا دهید.",
            reply_markup=Keyboards.vip_plans(),
            parse_mode="HTML"
        )
        return
    
    await state.set_state(BotStates.waiting_for_ai_question)
    
    await callback.message.edit_text(
        f"{E.BRAIN} *پرسش از هوش مصنوعی*\n\n"
        f"{E.HOURGLASS} سوالات باقی‌مانده: {ai_limit - ai_count} از {ai_limit}\n\n"
        f"{E.POINT_DOWN} سوال خود را به صورت متن بفرستید:\n"
        f"مثال: تحلیل بیت‌کوین رو بده",
        reply_markup=Keyboards.back_to_main(),
        parse_mode="HTML"
    )

@main_router.message(StateFilter(BotStates.waiting_for_ai_question))
async def handle_ai_question(message: Message, state: FSMContext):
    """Process AI question"""
    user_id = message.from_user.id
    
    # Check limits
    ai_count = await db.get_ai_count(user_id)
    ai_limit = await db.get_ai_limit(user_id)
    
    if ai_count >= ai_limit:
        await message.answer(
            f"{E.WARNING} محدودیت روزانه تمام شده. لطفاً پلن خود را ارتقا دهید.",
            reply_markup=Keyboards.vip_plans()
        )
        await state.clear()
        return
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # Get market context
    market_context = ""
    question_lower = message.text.lower()
    for sym in ["btc", "bitcoin", "بیت", "eth", "ethereum", "اتریوم", "sol", "solana", "سولانا"]:
        if sym in question_lower:
            try:
                symbol_map = {"btc": "BTCUSDT", "bitcoin": "BTCUSDT", "بیت": "BTCUSDT",
                             "eth": "ETHUSDT", "ethereum": "ETHUSDT", "اتریوم": "ETHUSDT",
                             "sol": "SOLUSDT", "solana": "SOLUSDT", "سولانا": "SOLUSDT"}
                sym_key = sym if sym in symbol_map else "btc"
                ticker = await exchange.get_ticker(symbol_map[sym_key])
                if ticker:
                    market_context = f"قیمت {symbol_map[sym_key]}: {ticker.get('last')} | تغییر ۲۴h: {ticker.get('change_percentage')}%"
                break
            except:
                pass
    
    # Get user profile
    user = await db.get_user(user_id)
    plan = await db.get_user_plan(user_id)
    user_profile = f"پلن: {plan} | سطح ریسک: {user.get('risk_level', 'medium') if user else 'medium'}"
    
    # Ask AI
    answer = await ai_engine.ask(message.text, market_context, "default", user_profile)
    
    # Update counters
    await db.increment_ai_count(user_id)
    await db.execute(
        "INSERT INTO ai_conversations(user_id, question, answer, context) VALUES(?, ?, ?, ?)",
        (user_id, message.text, answer, market_context)
    )
    
    new_count = await db.get_ai_count(user_id)
    
    # Build response
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{E.BRAIN} سوال جدید", callback_data="menu_ai")
    kb.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
    
    response = f"{E.ROBOT} *پاسخ هوش مصنوعی:*\n\n{answer}\n\n{E.HOURGLASS} {new_count}/{ai_limit}"
    
    # Split if too long
    if len(response) > 4000:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await message.answer(part, reply_markup=kb.as_markup(), parse_mode="HTML")
            else:
                await message.answer(part, parse_mode="HTML")
    else:
        await message.answer(response, reply_markup=kb.as_markup(), parse_mode="HTML")
    
    await db.log(user_id, "ai_question", message.text[:100])
    await state.clear()

@main_router.callback_query(F.data == "menu_analysis")
async def analysis_menu(callback: CallbackQuery):
    """Show analysis menu"""
    await callback.message.edit_text(
        f"{E.CHART} *تحلیل تکنیکال*\n\n{E.POINT_DOWN} نماد مورد نظر را انتخاب کنید:",
        reply_markup=Keyboards.analysis_symbols(),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data.startswith("analyze_"))
async def analyze_symbol(callback: CallbackQuery):
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
        
        # Get klines for technical analysis
        klines = await exchange.get_klines(symbol, "1hour", 100)
        
        prices = []
        highs = []
        lows = []
        volumes = []
        
        for candle in klines:
            prices.append(float(candle.get('close', 0)))
            highs.append(float(candle.get('high', 0)))
            lows.append(float(candle.get('low', 0)))
            volumes.append(float(candle.get('volume', 0)))
        
        if not prices:
            raise Exception("No kline data")
        
        # Technical analysis
        rsi = analyzer.calculate_rsi(prices)
        macd_val, macd_signal, macd_hist = analyzer.calculate_macd(prices)
        support, resistance = analyzer.calculate_support_resistance(prices)
        fib_levels = analyzer.fibonacci_levels(max(highs), min(lows))
        trend = analyzer.detect_trend(prices)
        volume_info = analyzer.volume_profile(volumes, prices)
        market_structure = analyzer.market_structure(highs, lows)
        
        # AI analysis
        ai_prompt = f"""
        تحلیل {symbol}:
        قیمت: {price}
        تغییر ۲۴h: {change}%
        RSI: {rsi:.1f}
        MACD: {macd_val:.4f}
        حمایت: {support:.4f}
        مقاومت: {resistance:.4f}
        روند: {trend}
        ساختار: {market_structure.get('bias', 'خنثی')}
        
        لطفاً تحلیل کوتاه و سیگنال احتمالی بده.
        """
        
        ai_analysis = await ai_engine.ask(ai_prompt, "", "technical")
        
        # Build response
        text = Templates.technical_analysis_card(
            symbol, price, change, rsi, macd_val, macd_signal,
            support, resistance, fib_levels, trend,
            volume_info, market_structure, ai_analysis
        )
        
        kb = InlineKeyboardBuilder()
        kb.button(text=f"{E.BELL} تنظیم هشدار", callback_data=f"alert_set_{symbol}")
        kb.button(text=f"{E.STAR} افزودن به واچ‌لیست", callback_data=f"watch_add_{symbol}")
        kb.button(text=f"{E.BACK} بازگشت", callback_data="menu_analysis")
        kb.adjust(2, 1)
        
        await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        await callback.message.edit_text(
            f"{E.CROSS} خطا در تحلیل {symbol}: {str(e)[:100]}\n\nلطفاً دوباره تلاش کنید.",
            reply_markup=Keyboards.back_to_main()
        )

@main_router.callback_query(F.data == "menu_time")
async def time_info(callback: CallbackQuery):
    """Show Tehran time information"""
    now = TehranTime.now()
    session = TehranTime.session_progress()
    
    text = f"""
{E.CLOCK} *اطلاعات زمان تهران*

{E.CALENDAR} *تاریخ:* {TehranTime.format(now, 'date')}
{E.CLOCK} *ساعت:* {TehranTime.format(now, 'time')}
{E.GLOBE} *فصل:* {TehranTime.get_season(now)}
{E.WATCH} *روز:* {TehranTime.PERSIAN_DAYS[now.weekday()]}

{E.CHART} *سشن معاملاتی:*
{E.POINT_RIGHT} فعلی: {session['session']}
{E.POINT_RIGHT} شروع: {session['start']}
{E.POINT_RIGHT} پایان: {session['end']}
{E.POINT_RIGHT} پیشرفت: {session['progress_percent']}%
{E.POINT_RIGHT} باقی‌مانده: {session['remaining_hours']} ساعت

{E.INFO} *تعطیلی:* {'بله 🕌' if TehranTime.is_weekend(now) else 'خیر'}
{E.MOON} *شب:* {'بله 🌙' if TehranTime.is_night(now) else 'خیر ☀️'}

{E.CLOCK} *آپتایم ربات:* {TehranTime.get_uptime_string(bot_start_time)}
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=Keyboards.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data == "menu_vip")
async def vip_menu(callback: CallbackQuery):
    """Show VIP plans"""
    text = Templates.vip_plans_info()
    
    await callback.message.edit_text(
        text,
        reply_markup=Keyboards.vip_plans(),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data.startswith("buy_"))
async def buy_plan(callback: CallbackQuery):
    """Handle plan purchase"""
    plan = callback.data.replace("buy_", "")
    
    if plan not in PRICING:
        await callback.answer("پلن نامعتبر!", show_alert=True)
        return
    
    text = Templates.payment_instruction(plan)
    
    await callback.message.edit_text(
        text,
        reply_markup=Keyboards.confirm_payment(plan),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data.startswith("confirm_pay_"))
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    """Confirm payment and request receipt"""
    plan = callback.data.replace("confirm_pay_", "")
    plan_info = PRICING.get(plan, PRICING['vip'])
    
    await state.set_state(BotStates.waiting_for_payment_receipt)
    await state.update_data(plan=plan, amount=plan_info['price'])
    
    await callback.message.edit_text(
        f"{E.ENVELOPE} *ارسال رسید پرداخت*\n\n"
        f"{E.POINT_DOWN} لطفاً عکس یا اسکرین‌شات رسید پرداخت را ارسال کنید.\n\n"
        f"{E.WARNING} توجه: رسید باید شامل مبلغ، تاریخ و شماره کارت مقصد باشد.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="menu_vip")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.message(StateFilter(BotStates.waiting_for_payment_receipt), F.photo)
async def receive_payment_receipt(message: Message, state: FSMContext):
    """Receive payment receipt"""
    user_id = message.from_user.id
    data = await state.get_data()
    plan = data.get('plan', 'vip')
    amount = data.get('amount', 0)
    
    # Record payment
    payment_id = await db.add_payment(user_id, plan, amount, "card")
    
    # Update payment with receipt
    await db.execute(
        "UPDATE payments SET receipt_file_id=?, receipt_message_id=? WHERE id=?",
        (message.photo[-1].file_id, message.message_id, payment_id)
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

{E.POINT_DOWN} برای تایید یا رد:
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
        f"{E.HOURGLASS} در حال بررسی توسط تیم پشتیبانی...\n"
        f"{E.CLOCK} زمان تقریبی تایید: ۵-۱۰ دقیقه\n\n"
        f"{E.ENVELOPE} در صورت تایید، اشتراک شما فعال و اطلاع‌رسانی خواهد شد.\n\n"
        f"{E.PHONE} *پشتیبانی:* {SUPPORT_CONTACT}",
        reply_markup=Keyboards.back_to_main(),
        parse_mode="HTML"
    )
    
    await db.log(user_id, "payment_receipt_sent", f"Payment ID: {payment_id}")
    await state.clear()

@main_router.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve_payment(callback: CallbackQuery):
    """Admin: Approve payment"""
    admin_id = callback.from_user.id
    
    if admin_id not in ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return
    
    payment_id = int(callback.data.replace("admin_approve_", ""))
    
    success = await db.approve_payment(payment_id, admin_id)
    
    if success:
        payment = await db.fetchone("SELECT * FROM payments WHERE id=?", (payment_id,))
        plan = payment['plan']
        plan_info = PRICING.get(plan, {})
        
        # Notify user
        try:
            await callback.bot.send_message(
                payment['user_id'],
                f"{E.PARTY}{E.PARTY}{E.PARTY} *تبریک!*\n\n"
                f"{E.CHECK} پرداخت شما تایید شد!\n\n"
                f"{E.CROWN} *پلن:* {plan_info.get('name', plan)}\n"
                f"{E.CALENDAR} *اعتبار:* {plan_info.get('days', 30)} روز\n\n"
                f"{E.ROCKET} از امکانات ویژه خود لذت ببرید!",
                parse_mode="HTML"
            )
        except:
            pass
        
        await callback.message.edit_text(
            f"{E.CHECK} پرداخت {payment_id} تایید شد.\nکاربر: {payment['user_id']}\nپلن: {plan}",
            parse_mode="HTML"
        )
    else:
        await callback.answer("خطا در تایید پرداخت!", show_alert=True)

@main_router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject_payment(callback: CallbackQuery):
    """Admin: Reject payment"""
    admin_id = callback.from_user.id
    
    if admin_id not in ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return
    
    payment_id = int(callback.data.replace("admin_reject_", ""))
    
    await db.execute(
        "UPDATE payments SET status='rejected', processed_at=?, processed_by=? WHERE id=?",
        (time.time(), admin_id, payment_id)
    )
    
    payment = await db.fetchone("SELECT * FROM payments WHERE id=?", (payment_id,))
    
    # Notify user
    try:
        await callback.bot.send_message(
            payment['user_id'],
            f"{E.CROSS} *پرداخت ناموفق*\n\n"
            f"متاسفانه پرداخت شما تایید نشد.\n"
            f"لطفاً با پشتیبانی تماس بگیرید: {SUPPORT_CONTACT}",
            parse_mode="HTML"
        )
    except:
        pass
    
    await callback.message.edit_text(
        f"{E.CROSS} پرداخت {payment_id} رد شد.",
        parse_mode="HTML"
    )

@main_router.callback_query(F.data == "menu_about")
async def about_menu(callback: CallbackQuery):
    """Show about information"""
    await callback.message.edit_text(
        Templates.about_bot(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.PHONE} کانال تلگرام", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton(text=f"{E.ENVELOPE} ارتباط با سازنده", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data == "menu_support")
async def support_menu(callback: CallbackQuery):
    """Show support information"""
    await callback.message.edit_text(
        f"{E.ENVELOPE} *پشتیبانی {APP_NAME}*\n\n"
        f"{E.POINT_RIGHT} *آیدی:* {SUPPORT_CONTACT}\n"
        f"{E.POINT_RIGHT} *کانال:* {CHANNEL_USERNAME}\n\n"
        f"{E.CLOCK} *ساعات پاسخگویی:* ۸ صبح تا ۱۲ شب\n"
        f"{E.LIGHTNING} *VIP:* کمتر از ۱ ساعت\n"
        f"{E.HOURGLASS} *رایگان:* ۲-۴ ساعت\n\n"
        f"{E.CARD} *شماره کارت:* `{CARD_NUMBER}`\n"
        f"{E.PERSON} *به نام:* {CARD_HOLDER}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.ENVELOPE} پیام به پشتیبان", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data == "menu_watchlist")
async def watchlist_menu(callback: CallbackQuery):
    """Show user's watchlist"""
    user_id = callback.from_user.id
    
    items = await db.fetchall(
        "SELECT symbol, note, added_at FROM watchlists WHERE user_id=? ORDER BY added_at DESC",
        (user_id,)
    )
    
    if not items:
        text = f"{E.STAR} *واچ‌لیست*\n\n{E.INFO} هنوز نمادی اضافه نکرده‌اید.\nبرای افزودن، از بخش تحلیل تکنیکال استفاده کنید."
    else:
        text = f"{E.STAR} *واچ‌لیست شما*\n\n"
        for i, item in enumerate(items, 1):
            added_time = TehranTime.format(TehranTime.from_timestamp(item['added_at']), "relative")
            text += f"{i}. {E.CHART} *{item['symbol']}* ({added_time})\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=Keyboards.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

@main_router.callback_query(F.data.startswith("watch_add_"))
async def add_to_watchlist(callback: CallbackQuery):
    """Add symbol to watchlist"""
    symbol = callback.data.replace("watch_add_", "")
    user_id = callback.from_user.id
    
    try:
        await db.execute(
            "INSERT OR IGNORE INTO watchlists(user_id, symbol) VALUES(?, ?)",
            (user_id, symbol)
        )
        await callback.answer(f"{E.CHECK} {symbol} به واچ‌لیست اضافه شد!", show_alert=True)
    except Exception as e:
        await callback.answer(f"{E.CROSS} خطا: {str(e)[:50]}", show_alert=True)

@main_router.callback_query(F.data == "menu_alerts")
async def alerts_menu(callback: CallbackQuery):
    """Show alerts menu"""
    user_id = callback.from_user.id
    
    alerts = await db.fetchall(
        "SELECT * FROM alerts WHERE user_id=? AND active=1 ORDER BY created_at DESC",
        (user_id,)
    )
    
    if not alerts:
        text = f"{E.BELL} *هشدارهای قیمت*\n\n{E.INFO} هیچ هشدار فعالی ندارید."
    else:
        text = f"{E.BELL} *هشدارهای فعال*\n\n"
        for alert in alerts:
            alert_type = "بالاتر از ⬆️" if alert['alert_type'] == 'above' else "پایین‌تر از ⬇️"
            created = TehranTime.format(TehranTime.from_timestamp(alert['created_at']), "relative")
            text += f"{E.POINT_RIGHT} *{alert['symbol']}*: {alert_type} {alert['target_price']} ({created})\n"
    
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{E.PLUS} هشدار جدید", callback_data="alert_new")
    kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

# Include router
dp.include_router(main_router)

# ═══════════════════════════════════════════════════════════════════════════
# ⚡ FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global bot_start_time
    
    logger.info(f"{E.ROCKET} Starting {APP_NAME} v{APP_VERSION}...")
    
    # Initialize database
    await db.init()
    logger.info("Database initialized")
    
    # Set webhook
    if WEBHOOK_URL and BOT_TOKEN:
        try:
            await bot.set_webhook(
                url=f"{WEBHOOK_URL}/webhook",
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"Webhook set: {WEBHOOK_URL}/webhook")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    
    # Start background tasks
    async def alert_checker():
        """Background task to check price alerts"""
        while True:
            try:
                active_alerts = await db.fetchall(
                    "SELECT * FROM alerts WHERE active=1 AND triggered=0"
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
                                    "UPDATE alerts SET triggered=1, triggered_at=? WHERE id=?",
                                    (time.time(), alert['id'])
                                )
                                
                                # Notify user
                                try:
                                    await bot.send_message(
                                        alert['user_id'],
                                        f"{E.BELL}{E.BELL}{E.BELL} *هشدار قیمت!*\n\n"
                                        f"{E.CHART} *{alert['symbol']}*\n"
                                        f"{E.MONEY} قیمت فعلی: {current_price}\n"
                                        f"{E.TARGET} هدف: {target}\n"
                                        f"{E.CLOCK} {TehranTime.format(TehranTime.now(), 'full')}",
                                        parse_mode="HTML"
                                    )
                                except:
                                    pass
                    except:
                        pass
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Alert checker error: {e}")
                await asyncio.sleep(60)
    
    async def daily_cleanup():
        """Daily cleanup task"""
        while True:
            try:
                # Clean old logs
                await db.cleanup_old_logs(30)
                
                # Clear AI cache
                ai_engine.clear_cache()
                
                logger.info("Daily cleanup completed")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
            
            await asyncio.sleep(86400)  # Run daily
    
    # Start background tasks
    asyncio.create_task(alert_checker())
    asyncio.create_task(daily_cleanup())
    
    logger.info(f"{E.ROCKET} {APP_NAME} v{APP_VERSION} started successfully!")
    logger.info(f"Time: {TehranTime.format(TehranTime.now(), 'full')}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    
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
    description="Professional Crypto Trading Bot with AI",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint"""
    try:
        # Verify secret
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        
        # Parse update
        data = await request.json()
        update = Update(**data)
        
        # Process update
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}\n{traceback.format_exc()}")
        return JSONResponse({"status": "error", "message": str(e)[:100]}, status_code=500)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "creator": CREATOR_USERNAME,
        "channel": CHANNEL_USERNAME,
        "status": "running",
        "time": TehranTime.format(TehranTime.now(), "full"),
        "uptime": TehranTime.get_uptime_string(bot_start_time)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "time": TehranTime.format(TehranTime.now(), "full"),
        "version": APP_VERSION
    }

@app.get("/stats")
async def get_stats(request: Request):
    """Get bot statistics (protected)"""
    # Simple auth
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.get_stats()
    ai_stats = ai_engine.get_stats()
    
    return {
        **stats,
        "ai_engine": ai_stats,
        "uptime": TehranTime.get_uptime_string(bot_start_time)
    }

@app.get("/admin")
async def admin_panel(request: Request):
    """Simple admin panel (HTML)"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.get_stats()
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <title>{APP_NAME} - Admin Panel</title>
        <style>
            body {{ font-family: Tahoma, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
            .card {{ background: #16213e; border-radius: 10px; padding: 20px; margin: 10px 0; }}
            .stat {{ display: inline-block; margin: 10px; padding: 15px; background: #0f3460; border-radius: 8px; }}
            .value {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        </style>
    </head>
    <body>
        <h1>🦅 {APP_NAME} v{APP_VERSION}</h1>
        <p>زمان: {TehranTime.format(TehranTime.now(), 'full')}</p>
        
        <div class="card">
            <h2>📊 آمار کلی</h2>
            <div class="stat"><div class="value">{stats['total_users']}</div>کل کاربران</div>
            <div class="stat"><div class="value">{stats['premium_users']}</div>کاربران ویژه</div>
            <div class="stat"><div class="value">{stats['today_active']}</div>فعال امروز</div>
            <div class="stat"><div class="value">{stats['total_revenue']:,}</div>درآمد کل (تومان)</div>
        </div>
        
        <p>سازنده: {CREATOR_USERNAME} | کانال: {CHANNEL_USERNAME}</p>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

# ═══════════════════════════════════════════════════════════════════════════
# ⚡ MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} on port {PORT}")
    uvicorn.run(
        "bot:app",
        host="0.0.0.0",
        port=PORT,
        reload=(ENVIRONMENT == "development"),
        log_level="info"
    )

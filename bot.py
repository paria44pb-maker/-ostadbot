"""
🦅 CryptoPulse-AI | ربات تحلیلگر کریپتو
========================================
سازنده: @Amir92aa
کانال: @CryptoPulse606
نسخه: 3.1.0 Professional
Railway Ready | CoinEx + Groq AI
"""

import os
import re
import json
import time
import hmac
import math
import base64
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from contextlib import asynccontextmanager

import aiohttp
import aiosqlite
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.enums import ParseMode, ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from groq import Groq, RateLimitError as GroqRateLimitError
from groq import APIStatusError as GroqAPIError

# ═══════════════════════════════════════════════════════════
# 📊 CONFIGURATION
# ═══════════════════════════════════════════════════════════

class Config:
    """تنظیمات اصلی ربات"""
    
    # Railway Environment Variables
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "https://your-app.railway.app")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "cryptopulse_secret_2024")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "cryptopulse.db")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CoinEx API
    COINEX_KEY: str = os.getenv("COINEX_KEY", "6063731196254479")
    COINEX_SECRET: str = os.getenv("COINEX_SECRET", "بهمرد")
    
    # Bot Settings
    ADMIN_IDS: List[int] = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip().isdigit()]
    CREATOR_USERNAME: str = "@Amir92aa"
    CHANNEL_USERNAME: str = "@CryptoPulse606"
    
    # Rate Limits
    GROQ_RPM: int = 25
    GROQ_TPM: int = 5000
    RATE_LIMIT_SECONDS: float = 1.5
    FREE_DAILY_AI_LIMIT: int = 5
    VIP_DAILY_AI_LIMIT: int = 50
    PRO_DAILY_AI_LIMIT: int = 200
    
    # Pricing (تومان)
    VIP_PRICE: int = 199000
    PRO_PRICE: int = 399000
    ELITE_PRICE: int = 999000
    
    # Features
    MAX_WATCHLIST_FREE: int = 5
    MAX_WATCHLIST_VIP: int = 20
    MAX_ALERTS_FREE: int = 2
    MAX_ALERTS_VIP: int = 15
    WELCOME_BONUS_DAYS: int = 3

config = Config()

# ═══════════════════════════════════════════════════════════
# 🕐 TEHRAN TIME MANAGER
# ═══════════════════════════════════════════════════════════

class TehranTime:
    """مدیریت زمان و تاریخ تهران"""
    
    TEHRAN_OFFSET = timedelta(hours=3, minutes=30)
    
    PERSIAN_MONTHS = [
        "فروردین", "اردیبهشت", "خرداد",
        "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر",
        "دی", "بهمن", "اسفند"
    ]
    
    PERSIAN_DAYS = [
        "دوشنبه", "سه‌شنبه", "چهارشنبه",
        "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"
    ]
    
    SEASONS = {
        "spring": "بهار 🌸",
        "summer": "تابستان ☀️",
        "autumn": "پاییز 🍂",
        "winter": "زمستان ❄️"
    }
    
    @classmethod
    def now(cls) -> datetime:
        return datetime.now(timezone.utc) + cls.TEHRAN_OFFSET
    
    @classmethod
    def now_ts(cls) -> float:
        return cls.now().timestamp()
    
    @classmethod
    def format(cls, dt: datetime = None, fmt: str = "full") -> str:
        if dt is None:
            dt = cls.now()
        
        if fmt == "full":
            return f"{cls.PERSIAN_DAYS[dt.weekday()]} {cls._day(dt)} {cls.PERSIAN_MONTHS[cls._month(dt)-1]} {cls._year(dt)} - {dt.strftime('%H:%M:%S')}"
        elif fmt == "time":
            return dt.strftime("%H:%M:%S")
        elif fmt == "date":
            return f"{cls._day(dt)} {cls.PERSIAN_MONTHS[cls._month(dt)-1]} {cls._year(dt)}"
        elif fmt == "short":
            return f"{cls._year(dt)}/{cls._month(dt):02d}/{cls._day(dt):02d} - {dt.strftime('%H:%M')}"
        elif fmt == "relative":
            diff = cls.now() - dt
            sec = int(diff.total_seconds())
            if sec < 60: return f"{sec} ثانیه پیش"
            elif sec < 3600: return f"{sec//60} دقیقه پیش"
            elif sec < 86400: return f"{sec//3600} ساعت پیش"
            elif sec < 604800: return f"{sec//86400} روز پیش"
            else: return cls.format(dt, "date")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def _year(cls, dt: datetime) -> int:
        return dt.year - 621 if (dt.month, dt.day) >= (3, 21) else dt.year - 622
    
    @classmethod
    def _month(cls, dt: datetime) -> int:
        start = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo) if (dt.month, dt.day) >= (3, 21) else datetime(dt.year-1, 3, 21, tzinfo=dt.tzinfo)
        days = (dt - start).days
        for i, md in enumerate([31,31,31,31,31,31,30,30,30,30,30,29]):
            if days < md: return i + 1
            days -= md
        return 12
    
    @classmethod
    def _day(cls, dt: datetime) -> int:
        start = datetime(dt.year, 3, 21, tzinfo=dt.tzinfo) if (dt.month, dt.day) >= (3, 21) else datetime(dt.year-1, 3, 21, tzinfo=dt.tzinfo)
        days = (dt - start).days
        for md in [31,31,31,31,31,31,30,30,30,30,30,29]:
            if days < md: return days + 1
            days -= md
        return 29
    
    @classmethod
    def get_season(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        m = cls._month(dt)
        if m <= 3: return cls.SEASONS["spring"]
        elif m <= 6: return cls.SEASONS["summer"]
        elif m <= 9: return cls.SEASONS["autumn"]
        return cls.SEASONS["winter"]
    
    @classmethod
    def is_weekend(cls, dt: datetime = None) -> bool:
        if dt is None: dt = cls.now()
        return dt.weekday() == 4
    
    @classmethod
    def trading_session(cls, dt: datetime = None) -> str:
        if dt is None: dt = cls.now()
        h = dt.hour
        if 3 <= h < 12: return "آسیا 🌏"
        elif 12 <= h < 19: return "اروپا 🌍"
        else: return "آمریکا 🌎"
    
    @classmethod
    def candle_closes(cls) -> Dict[str, str]:
        now = cls.now()
        result = {}
        
        n = now + timedelta(minutes=1)
        result["1m"] = n.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        
        n = now + timedelta(minutes=5 - now.minute % 5)
        result["5m"] = n.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        
        n = now + timedelta(minutes=15 - now.minute % 15)
        result["15m"] = n.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        
        n = now + timedelta(hours=1)
        result["1h"] = n.replace(minute=0, second=0, microsecond=0).strftime("%H:%M:%S")
        
        nh = ((now.hour // 4) + 1) * 4
        if nh >= 24:
            n = now + timedelta(days=1)
            result["4h"] = n.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%H:%M")
        else:
            result["4h"] = now.replace(hour=nh, minute=0, second=0, microsecond=0).strftime("%H:%M:%S")
        
        n = now + timedelta(days=1)
        result["1d"] = n.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%H:%M")
        
        return result

# ═══════════════════════════════════════════════════════════
# 🎨 EMOJI BANK
# ═══════════════════════════════════════════════════════════

class E:
    """بانک شکلک‌ها"""
    ROCKET = "🚀"; FIRE = "🔥"; MONEY = "💰"; CROWN = "👑"; DIAMOND = "💎"
    STAR = "⭐"; CHART = "📊"; BULL = "🐂"; BEAR = "🐻"; TARGET = "🎯"
    CHECK = "✅"; CROSS = "❌"; WARNING = "⚠️"; INFO = "ℹ️"; LOCK = "🔒"
    KEY = "🔑"; GIFT = "🎁"; PARTY = "🎉"; ROBOT = "🤖"; BRAIN = "🧠"
    EYE = "👁️"; LIGHTNING = "⚡"; HOURGLASS = "⏳"; CALENDAR = "📅"
    BELL = "🔔"; CHART_UP = "📈"; CHART_DOWN = "📉"; CRYSTAL = "💠"
    CLOCK = "🕐"; GLOBE = "🌍"; HOME = "🏠"; BACK = "🔙"; SEARCH = "🔍"
    PLUS = "➕"; SETTINGS = "⚙️"; ENVELOPE = "📧"; PHONE = "📱"
    POINT_RIGHT = "👉"; POINT_DOWN = "👇"; POINT_LEFT = "👈"
    SHIELD = "🛡️"; SWORD = "⚔️"; SCALE = "⚖️"; TROPHY = "🏆"
    WALLET = "👛"; CARD = "💳"; BANK = "🏦"; COIN = "🪙"
    THERMOMETER = "🌡️"; WAVE = "🌊"; MOUNTAIN = "🏔️"
    SUN = "☀️"; MOON = "🌙"; ZAP = "⚡"; COMET = "☄️"
    BULB = "💡"; MAGNET = "🧲"; MICROSCOPE = "🔬"
    NEW = "🆕"; FREE = "🆓"; TOP = "🔝"; OK = "🆗"
    COOL = "😎"; THINK = "🤔"; WOW = "😍"; CLAP = "👏"; PRAY = "🙏"; MUSCLE = "💪"

# ═══════════════════════════════════════════════════════════
# 🗄️ DATABASE
# ═══════════════════════════════════════════════════════════

class Database:
    """مدیریت دیتابیس SQLite"""
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        plan TEXT DEFAULT 'free',
        plan_until REAL DEFAULT 0,
        welcome_bonus INTEGER DEFAULT 0,
        risk_level TEXT DEFAULT 'medium',
        total_payments REAL DEFAULT 0,
        referral_code TEXT DEFAULT '',
        referred_by INTEGER DEFAULT 0,
        total_referrals INTEGER DEFAULT 0,
        referral_earnings REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        last_active REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER PRIMARY KEY,
        daily_ai_count INTEGER DEFAULT 0,
        last_ai_at REAL DEFAULT 0,
        last_reset TEXT DEFAULT ''
    );
    
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT,
        added_at REAL DEFAULT (strftime('%s', 'now')),
        UNIQUE(user_id, symbol)
    );
    
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT,
        target_price REAL,
        alert_type TEXT DEFAULT 'above',
        active INTEGER DEFAULT 1,
        triggered INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        direction TEXT,
        entry REAL,
        stop_loss REAL,
        take_profit REAL,
        confidence REAL DEFAULT 0.5,
        status TEXT DEFAULT 'active',
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan TEXT,
        amount REAL,
        status TEXT DEFAULT 'pending',
        payment_method TEXT DEFAULT 'card',
        receipt_id TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS ai_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        answer TEXT,
        tokens INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    """
    
    def __init__(self, path: str = "cryptopulse.db"):
        self.path = path
    
    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(self.SCHEMA)
            await db.commit()
    
    async def execute(self, query: str, params: tuple = ()) -> int:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(query, params)
            await db.commit()
            return cur.lastrowid
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(query, params) as cur:
                return await cur.fetchone()
    
    async def fetchall(self, query: str, params: tuple = ()) -> List[tuple]:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(query, params) as cur:
                return await cur.fetchall()
    
    async def get_user(self, uid: int) -> Optional[Dict]:
        cols = ['user_id','username','full_name','plan','plan_until','welcome_bonus',
                'risk_level','total_payments','referral_code','referred_by',
                'total_referrals','referral_earnings','created_at','last_active']
        row = await self.fetchone("SELECT * FROM users WHERE user_id=?", (uid,))
        return dict(zip(cols, row)) if row else None
    
    async def upsert_user(self, uid: int, username: str = "", full_name: str = ""):
        now = time.time()
        await self.execute("""
            INSERT INTO users(user_id, username, full_name, last_active)
            VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
            username=COALESCE(NULLIF(?, ''), users.username),
            full_name=COALESCE(NULLIF(?, ''), users.full_name),
            last_active=?
        """, (uid, username, full_name, now, username, full_name, now))
        await self.execute("INSERT OR IGNORE INTO user_state(user_id) VALUES(?)", (uid,))
    
    async def get_plan(self, uid: int) -> str:
        user = await self.get_user(uid)
        if not user: return "free"
        if user['plan'] in ('vip','pro','elite') and time.time() < user['plan_until']:
            return user['plan']
        return "free"
    
    async def is_premium(self, uid: int) -> bool:
        return await self.get_plan(uid) != "free"
    
    async def get_ai_count(self, uid: int) -> int:
        today = TehranTime.now().strftime('%Y-%m-%d')
        row = await self.fetchone("SELECT last_reset, daily_ai_count FROM user_state WHERE user_id=?", (uid,))
        if not row:
            await self.execute("INSERT OR IGNORE INTO user_state(user_id, last_reset, daily_ai_count) VALUES(?,?,0)", (uid, today))
            return 0
        if row[0] != today:
            await self.execute("UPDATE user_state SET daily_ai_count=0, last_reset=? WHERE user_id=?", (today, uid))
            return 0
        return row[1]
    
    async def inc_ai_count(self, uid: int) -> int:
        today = TehranTime.now().strftime('%Y-%m-%d')
        await self.execute("UPDATE user_state SET daily_ai_count=daily_ai_count+1, last_reset=? WHERE user_id=?", (today, uid))
        row = await self.fetchone("SELECT daily_ai_count FROM user_state WHERE user_id=?", (uid,))
        return row[0] if row else 0
    
    async def get_ai_limit(self, uid: int) -> int:
        limits = {"free": config.FREE_DAILY_AI_LIMIT, "vip": config.VIP_DAILY_AI_LIMIT, 
                  "pro": config.PRO_DAILY_AI_LIMIT, "elite": 999999}
        return limits.get(await self.get_plan(uid), config.FREE_DAILY_AI_LIMIT)
    
    async def set_plan(self, uid: int, plan: str, days: int = 30):
        until = time.time() + (days * 86400)
        await self.execute("UPDATE users SET plan=?, plan_until=? WHERE user_id=?", (plan, until, uid))
        await self.log(uid, f"plan_upgraded_{plan}")
    
    async def log(self, uid: int, action: str, details: str = ""):
        await self.execute("INSERT INTO logs(user_id, action, details) VALUES(?,?,?)", (uid, action, details))
    
    async def get_stats(self) -> Dict:
        total = await self.fetchone("SELECT COUNT(*) FROM users")
        premium = await self.fetchone("SELECT COUNT(*) FROM users WHERE plan!='free' AND plan_until > ?", (time.time(),))
        revenue = await self.fetchone("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved'")
        today = await self.fetchone("SELECT COUNT(*) FROM users WHERE date(last_active, 'unixepoch') = date('now')")
        return {
            "total_users": total[0] if total else 0,
            "premium_users": premium[0] if premium else 0,
            "total_revenue": revenue[0] if revenue else 0,
            "today_active": today[0] if today else 0
        }

# ═══════════════════════════════════════════════════════════
# 🤖 GROQ AI
# ═══════════════════════════════════════════════════════════

class GroqAI:
    """مدیریت Groq AI"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.requests = []
        self.tokens = 0
        self.day = ""
    
    async def ask(self, prompt: str, context: str = "") -> str:
        now = time.time()
        self.requests = [t for t in self.requests if now - t < 60]
        
        today = TehranTime.now().strftime('%Y-%m-%d')
        if today != self.day:
            self.tokens = 0
            self.day = today
        
        if len(self.requests) >= config.GROQ_RPM:
            await asyncio.sleep(2)
        
        system = """شما یک تحلیلگر حرفه‌ای کریپتو به زبان فارسی هستید.
همیشه فارسی و با شکلک پاسخ بده. تحلیل دقیق، عملی و با ذکر حد ضرر و هدف بده.
هرگز وعده سود قطعی نده. ریسک‌ها را شفاف بگو."""
        
        messages = [
            {"role": "system", "content": system},
        ]
        if context:
            messages.append({"role": "system", "content": f"داده‌های بازار:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        try:
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(None, lambda: self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            ))
            
            self.requests.append(now)
            if resp.usage:
                self.tokens += resp.usage.total_tokens
            
            return resp.choices[0].message.content.strip()
        except GroqRateLimitError:
            await asyncio.sleep(5)
            return f"{E.WARNING} سیستم در حال حاضر مشغول است. لطفاً چند ثانیه دیگر تلاش کنید."
        except Exception as e:
            return f"{E.CROSS} خطا در ارتباط با AI: {str(e)[:100]}"

# ═══════════════════════════════════════════════════════════
# 📈 COINEX API
# ═══════════════════════════════════════════════════════════

class CoinExAPI:
    """ارتباط با صرافی CoinEx"""
    
    BASE = "https://api.coinex.com/v2"
    
    def __init__(self, key: str = "", secret: str = ""):
        self.key = key
        self.secret = secret
    
    def _sign(self, method: str, path: str, body: str = "", ts: str = "") -> str:
        if not self.secret: return ""
        return hmac.new(self.secret.encode(), f"{method}{path}{ts}{body}".encode(), hashlib.sha256).hexdigest()
    
    async def _req(self, method: str, endpoint: str, params: Dict = None, body: Dict = None) -> Dict:
        url = self.BASE + endpoint
        path = endpoint
        if params:
            qs = "&".join(f"{k}={v}" for k,v in sorted(params.items()))
            url += "?" + qs
            path += "?" + qs
        
        headers = {"Content-Type": "application/json"}
        if self.key and self.secret:
            ts = str(int(time.time() * 1000))
            headers.update({
                "X-COINEX-KEY": self.key,
                "X-COINEX-SIGN": self._sign(method, path, "", ts),
                "X-COINEX-TIMESTAMP": ts,
                "X-COINEX-WINDOWTIME": "5000"
            })
        
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers, timeout=15) as resp:
                        return await resp.json()
                else:
                    async with session.post(url, headers=headers, json=body, timeout=15) as resp:
                        return await resp.json()
        except:
            return {"code": -1, "message": "Network error"}
    
    async def ticker(self, symbol: str = "BTCUSDT") -> Dict:
        return await self._req("GET", "/spot/ticker", {"market": symbol})
    
    async def klines(self, symbol: str = "BTCUSDT", period: str = "1hour", limit: int = 100) -> Dict:
        return await self._req("GET", "/spot/kline", {"market": symbol, "period": period, "limit": str(limit)})

# ═══════════════════════════════════════════════════════════
# 📊 TECHNICAL ANALYZER
# ═══════════════════════════════════════════════════════════

class TechnicalAnalyzer:
    """تحلیلگر تکنیکال"""
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1: return 50.0
        deltas = np.diff(prices)
        gains = np.maximum(deltas, 0)
        losses = np.maximum(-deltas, 0)
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period-1) + gains[i]) / period
            avg_loss = (avg_loss * (period-1) + losses[i]) / period
        if avg_loss == 0: return 100.0
        return float(100 - 100/(1 + avg_gain/avg_loss))
    
    @staticmethod
    def macd(prices: List[float]) -> Tuple[float, float, float]:
        if len(prices) < 35: return (0,0,0)
        def ema(data, p):
            if len(data) < p: return data[-1] if data else 0
            m = 2/(p+1)
            e = sum(data[:p])/p
            for x in data[p:]: e = (x-e)*m + e
            return e
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = ema12 - ema26
        # Simplified signal line
        signal_line = macd_line * 0.9
        return (float(macd_line), float(signal_line), float(macd_line - signal_line))
    
    @staticmethod
    def support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
        if len(prices) < window: return (min(prices), max(prices))
        recent = prices[-window:]
        return (float(min(recent)), float(max(recent)))
    
    @staticmethod
    def fibonacci(high: float, low: float) -> List[float]:
        diff = high - low
        ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        return [low + diff * r if diff > 0 else high - abs(diff) * r for r in ratios]
    
    @staticmethod
    def trend(prices: List[float]) -> str:
        if len(prices) < 30: return "خنثی"
        short = np.mean(prices[-10:])
        long = np.mean(prices[-30:])
        if short > long * 1.02: return "صعودی 📈"
        elif short < long * 0.98: return "نزولی 📉"
        return "خنثی ➡️"

# ═══════════════════════════════════════════════════════════
# 🎮 BOT HANDLERS
# ═══════════════════════════════════════════════════════════

class PaymentStates(StatesGroup):
    waiting_for_ai_question = State()
    waiting_for_receipt = State()
    waiting_for_custom_symbol = State()
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()

class BotHandlers:
    """هندلرهای ربات"""
    
    def __init__(self, db: Database, ai: GroqAI, ex: CoinExAPI, ta: TechnicalAnalyzer):
        self.db = db
        self.ai = ai
        self.ex = ex
        self.ta = ta
        self.router = Router()
        self._register()
    
    def _register(self):
        
        @self.router.message(CommandStart())
        async def start(msg: Message, state: FSMContext):
            uid = msg.from_user.id
            name = msg.from_user.full_name or "کاربر"
            uname = msg.from_user.username or ""
            
            await self.db.upsert_user(uid, uname, name)
            
            # Welcome bonus
            user = await self.db.get_user(uid)
            if user and not user['welcome_bonus']:
                await self.db.execute(
                    "UPDATE users SET plan='vip', plan_until=?, welcome_bonus=1 WHERE user_id=?",
                    (time.time() + config.WELCOME_BONUS_DAYS * 86400, uid)
                )
            
            # Referral
            parts = msg.text.split() if msg.text else []
            if len(parts) > 1 and parts[1].startswith("ref_"):
                try:
                    ref_id = int(parts[1].replace("ref_", ""))
                    if ref_id != uid and user and not user['referred_by']:
                        await self.db.execute("UPDATE users SET referred_by=? WHERE user_id=?", (ref_id, uid))
                        await self.db.execute("UPDATE users SET total_referrals=total_referrals+1 WHERE user_id=?", (ref_id,))
                except: pass
            
            plan = await self.db.get_plan(uid)
            days = 0
            if user and user['plan_until']:
                days = max(0, int((user['plan_until'] - time.time()) / 86400))
            
            now = TehranTime.now()
            time_str = TehranTime.format(now, "full")
            season = TehranTime.get_season(now)
            session = TehranTime.trading_session(now)
            
            plan_icon = {"free": "🆓", "vip": "👑", "pro": "💎", "elite": "👑💎"}
            plan_name = {"free": "رایگان", "vip": "VIP", "pro": "PRO", "elite": "ELITE"}
            
            welcome = f"""
{E.ROCKET}{E.FIRE}{E.ROCKET} *CryptoPulse-AI* {E.ROCKET}{E.FIRE}{E.ROCKET}

{E.ROBOT} سلام *{name}* عزیز!
{E.WAVE} به پیشرفته‌ترین ربات تحلیل کریپتو خوش اومدی!

{E.CLOCK} *زمان تهران:* {time_str}
{E.GLOBE} *فصل:* {season} | *سشن:* {session}

{E.DIAMOND}━━━━━━━━━━━━━━━━{E.DIAMOND}
{plan_icon.get(plan, '🆓')} *پلن:* {plan_name.get(plan, 'رایگان')}
{E.CALENDAR} *اعتبار:* {days} روز
{E.DIAMOND}━━━━━━━━━━━━━━━━{E.DIAMOND}

{E.POINT_DOWN} *منوی اصلی:*
"""
            
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.SEARCH} تحلیل بازار", callback_data="market")
            kb.button(text=f"{E.BRAIN} پرسش از AI", callback_data="ask_ai")
            kb.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="tech_menu")
            kb.button(text=f"{E.BELL} هشدار قیمت", callback_data="alerts")
            kb.button(text=f"{E.STAR} واچ‌لیست", callback_data="watchlist")
            kb.button(text=f"{E.CLOCK} زمان و تاریخ", callback_data="time_info")
            kb.button(text=f"{E.CROWN} ارتقا VIP", callback_data="upgrade")
            kb.button(text=f"{E.ROBOT} درباره ما", callback_data="about")
            kb.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="support")
            kb.adjust(2, 2, 2, 2, 1)
            
            await msg.answer(welcome, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
            await self.db.log(uid, "start")
        
        @self.router.callback_query(F.data == "main_menu")
        async def main_menu(cb: CallbackQuery):
            uid = cb.from_user.id
            plan = await self.db.get_plan(uid)
            
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.SEARCH} تحلیل بازار", callback_data="market")
            kb.button(text=f"{E.BRAIN} پرسش از AI", callback_data="ask_ai")
            kb.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="tech_menu")
            kb.button(text=f"{E.BELL} هشدار قیمت", callback_data="alerts")
            kb.button(text=f"{E.STAR} واچ‌لیست", callback_data="watchlist")
            kb.button(text=f"{E.CLOCK} زمان و تاریخ", callback_data="time_info")
            if plan == "free":
                kb.button(text=f"{E.CROWN} ارتقا VIP", callback_data="upgrade")
            kb.button(text=f"{E.ROBOT} درباره ما", callback_data="about")
            kb.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="support")
            kb.adjust(2, 2, 2, 2, 1)
            
            await cb.message.edit_text(
                f"{E.HOME} *منوی اصلی*\n\n{E.POINT_DOWN} گزینه مورد نظر را انتخاب کنید:",
                reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML
            )
            await cb.answer()
        
        @self.router.callback_query(F.data == "market")
        async def market(cb: CallbackQuery):
            await cb.answer("در حال دریافت...")
            
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
            text = f"{E.GLOBE} *خلاصه بازار* | {TehranTime.format(TehranTime.now(), 'time')}\n\n"
            
            for sym in symbols:
                try:
                    data = await self.ex.ticker(sym)
                    if data.get('code') == 0:
                        d = data['data']
                        p = float(d.get('last', 0))
                        c = float(d.get('change_percentage', 0))
                        em = E.CHART_UP if c > 0 else E.CHART_DOWN
                        text += f"{em} *{sym.replace('USDT','')}:* {p:.2f} ({c:+.2f}%)\n"
                except:
                    text += f"{E.CROSS} {sym}: خطا\n"
            
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data == "ask_ai")
        async def ask_ai(cb: CallbackQuery, state: FSMContext):
            uid = cb.from_user.id
            cnt = await self.db.get_ai_count(uid)
            limit = await self.db.get_ai_limit(uid)
            
            if cnt >= limit:
                await cb.message.edit_text(
                    f"{E.WARNING} *محدودیت AI*\n\n{E.HOURGLASS} {cnt} از {limit} سوال استفاده شده.\n{E.LOCK} برای بیشتر، VIP بخرید.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f"{E.CROWN} خرید VIP", callback_data="upgrade")],
                        [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
                    ]), parse_mode=ParseMode.HTML
                )
                return
            
            await state.set_state(PaymentStates.waiting_for_ai_question)
            
            await cb.message.edit_text(
                f"{E.BRAIN} *سوال خود را بپرسید*\n\n{E.HOURGLASS} باقی‌مانده: {limit - cnt} از {limit}\n\n{E.POINT_DOWN} سوال را به صورت متن بفرستید:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
                ]), parse_mode=ParseMode.HTML
            )
        
        @self.router.message(StateFilter(PaymentStates.waiting_for_ai_question))
        async def handle_ai(msg: Message, state: FSMContext):
            uid = msg.from_user.id
            cnt = await self.db.get_ai_count(uid)
            limit = await self.db.get_ai_limit(uid)
            
            if cnt >= limit:
                await msg.answer(f"{E.WARNING} محدودیت تمام شده. لطفاً VIP بخرید.")
                await state.clear()
                return
            
            await msg.bot.send_chat_action(msg.chat.id, ChatAction.TYPING)
            
            ctx = ""
            if any(w in msg.text.lower() for w in ['بیت','btc','bitcoin']):
                try:
                    d = await self.ex.ticker("BTCUSDT")
                    if d.get('code') == 0:
                        t = d['data']
                        ctx = f"BTC: {t.get('last')} USDT | 24h: {t.get('change_percentage')}%"
                except: pass
            
            answer = await self.ai.ask(msg.text, ctx)
            await self.db.inc_ai_count(uid)
            await self.db.execute("INSERT INTO ai_history(user_id, question, answer) VALUES(?,?,?)", (uid, msg.text, answer))
            
            new_cnt = await self.db.get_ai_count(uid)
            
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.BRAIN} سوال جدید", callback_data="ask_ai")
            kb.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
            
            await msg.answer(f"{answer}\n\n{E.HOURGLASS} {new_cnt}/{limit}", reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
            await state.clear()
        
        @self.router.callback_query(F.data == "tech_menu")
        async def tech_menu(cb: CallbackQuery):
            kb = InlineKeyboardBuilder()
            for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]:
                kb.button(text=f"{E.CHART} {sym.replace('USDT','')}", callback_data=f"analyze_{sym}")
            kb.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_analysis")
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            kb.adjust(2, 2, 1)
            
            await cb.message.edit_text(
                f"{E.CHART} *تحلیل تکنیکال*\n\n{E.POINT_DOWN} نماد را انتخاب کنید:",
                reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML
            )
        
        @self.router.callback_query(F.data.startswith("analyze_"))
        async def analyze(cb: CallbackQuery):
            sym = cb.data.replace("analyze_", "")
            await cb.answer(f"تحلیل {sym}...")
            
            try:
                tick = await self.ex.ticker(sym)
                if tick.get('code') != 0:
                    raise Exception("No data")
                
                d = tick['data']
                price = float(d.get('last', 0))
                change = float(d.get('change_percentage', 0))
                
                kl = await self.ex.klines(sym, "1hour", 100)
                prices, highs, lows = [], [], []
                if kl.get('code') == 0:
                    for c in kl['data']:
                        prices.append(float(c['close']))
                        highs.append(float(c['high']))
                        lows.append(float(c['low']))
                
                if not prices:
                    raise Exception("No kline data")
                
                rsi = self.ta.rsi(prices)
                macd_val, macd_sig, macd_hist = self.ta.macd(prices)
                sup, res = self.ta.support_resistance(prices)
                fib = self.ta.fibonacci(max(highs), min(lows))
                trend = self.ta.trend(prices)
                
                rsi_text = "🟢 اشباع فروش" if rsi < 30 else "🔴 اشباع خرید" if rsi > 70 else "🟡 خنثی"
                change_em = E.CHART_UP if change > 0 else E.CHART_DOWN
                
                text = f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل {sym}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت:* {price:.4f} USDT
{change_em} *تغییر ۲۴h:* {change:+.2f}%

{E.THERMOMETER} *RSI:* {rsi:.1f} ({rsi_text})
{E.WAVE} *MACD:* {macd_val:.4f}
{E.MOUNTAIN} *روند:* {trend}

{E.SHIELD} *حمایت:* {sup:.4f}
{E.SWORD} *مقاومت:* {res:.4f}

{E.CRYSTAL} *فیبوناچی:*
{E.POINT_RIGHT} ۰٪: {fib[0]:.4f}
{E.POINT_RIGHT} ۳۸.۲٪: {fib[2]:.4f}
{E.POINT_RIGHT} ۵۰٪: {fib[3]:.4f}
{E.POINT_RIGHT} ۶۱.۸٪: {fib[4]:.4f}
{E.POINT_RIGHT} ۱۰۰٪: {fib[6]:.4f}

{E.CLOCK} *زمان:* {TehranTime.format(TehranTime.now(), 'full')}
"""
                
                # AI Analysis
                ai_prompt = f"تحلیل کوتاه {sym} با قیمت {price} و RSI={rsi:.1f} و روند {trend}. سیگنال بده."
                ai_resp = await self.ai.ask(ai_prompt)
                text += f"\n\n{E.ROBOT} *تحلیل AI:*\n{ai_resp}"
                
                kb = InlineKeyboardBuilder()
                kb.button(text=f"{E.BELL} هشدار برای {sym.replace('USDT','')}", callback_data=f"alert_{sym}")
                kb.button(text=f"{E.STAR} افزودن به واچ‌لیست", callback_data=f"addwatch_{sym}")
                kb.button(text=f"{E.BACK} بازگشت", callback_data="tech_menu")
                kb.adjust(1, 1)
                
                await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
                
            except Exception as e:
                await cb.message.edit_text(
                    f"{E.CROSS} خطا در تحلیل: {str(e)[:100]}",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="tech_menu")]
                    ])
                )
        
        @self.router.callback_query(F.data == "time_info")
        async def time_info(cb: CallbackQuery):
            now = TehranTime.now()
            candles = TehranTime.candle_closes()
            
            text = f"""
{E.CLOCK} *اطلاعات زمان تهران*

{E.CALENDAR} *تاریخ:* {TehranTime.format(now, 'date')}
{E.CLOCK} *ساعت:* {TehranTime.format(now, 'time')}
{E.GLOBE} *فصل:* {TehranTime.get_season(now)}
{E.CHART} *سشن:* {TehranTime.trading_session(now)}

{E.HOURGLASS} *بسته شدن کندل‌ها:*
{E.POINT_RIGHT} ۱ دقیقه: {candles.get('1m','...')}
{E.POINT_RIGHT} ۵ دقیقه: {candles.get('5m','...')}
{E.POINT_RIGHT} ۱۵ دقیقه: {candles.get('15m','...')}
{E.POINT_RIGHT} ۱ ساعت: {candles.get('1h','...')}
{E.POINT_RIGHT} ۴ ساعت: {candles.get('4h','...')}
{E.POINT_RIGHT} روزانه: {candles.get('1d','...')}

{E.INFO} *جمعه:* {'بله 🕌' if TehranTime.is_weekend(now) else 'خیر'}
"""
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data == "upgrade")
        async def upgrade(cb: CallbackQuery):
            text = f"""
{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های VIP* {E.CROWN}{E.CROWN}{E.CROWN}

{E.CROWN} *VIP:* ۱۹۹,۰۰۰ تومان
{E.POINT_RIGHT} ۵۰ تحلیل AI در روز
{E.POINT_RIGHT} هشدار نامحدود
{E.POINT_RIGHT} واچ‌لیست ۲۰ تایی
{E.POINT_RIGHT} سیگنال‌های VIP

{E.DIAMOND} *PRO:* ۳۹۹,۰۰۰ تومان
{E.POINT_RIGHT} ۲۰۰ تحلیل AI
{E.POINT_RIGHT} همه امکانات VIP
{E.POINT_RIGHT} کپی تریدینگ

{E.CROWN} *ELITE:* ۹۹۹,۰۰۰ تومان
{E.POINT_RIGHT} تحلیل نامحدود
{E.POINT_RIGHT} مشاوره خصوصی

{E.GIFT} *هدیه:* ۳ روز VIP رایگان برای کاربران جدید!
"""
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.CROWN} VIP - ۱۹۹", callback_data="buy_vip")
            kb.button(text=f"{E.DIAMOND} PRO - ۳۹۹", callback_data="buy_pro")
            kb.button(text=f"{E.CROWN} ELITE - ۹۹۹", callback_data="buy_elite")
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            kb.adjust(1)
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data.startswith("buy_"))
        async def buy(cb: CallbackQuery):
            plan = cb.data.replace("buy_", "")
            prices = {"vip": 199000, "pro": 399000, "elite": 999000}
            names = {"vip": "VIP 👑", "pro": "PRO 💎", "elite": "ELITE 👑💎"}
            
            text = f"""
{E.CARD} *پرداخت {names.get(plan, plan)}*

{E.MONEY} *مبلغ:* {prices[plan]:,} تومان

{E.BANK} *شماره کارت:*
`6037-9919-XXXX-XXXX`

{E.POINT_DOWN} پس از پرداخت، روی دکمه زیر کلیک کنید و رسید را ارسال کنید.

{E.WARNING} حتماً آیدی تلگرام خود را در توضیحات بنویسید.
"""
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.CHECK} پرداخت کردم ✅", callback_data=f"paid_{plan}")
            kb.button(text=f"{E.BACK} بازگشت", callback_data="upgrade")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data.startswith("paid_"))
        async def paid(cb: CallbackQuery, state: FSMContext):
            plan = cb.data.replace("paid_", "")
            await state.set_state(PaymentStates.waiting_for_receipt)
            await state.update_data(plan=plan)
            
            await cb.message.edit_text(
                f"{E.ENVELOPE} *لطفاً رسید پرداخت را ارسال کنید.*\n\n{E.POINT_DOWN} عکس یا اسکرین‌شات رسید را بفرستید.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="upgrade")]
                ]), parse_mode=ParseMode.HTML
            )
        
        @self.router.message(StateFilter(PaymentStates.waiting_for_receipt), F.photo)
        async def receipt(msg: Message, state: FSMContext):
            data = await state.get_data()
            plan = data.get('plan', 'vip')
            prices = {"vip": 199000, "pro": 399000, "elite": 999000}
            
            await self.db.execute(
                "INSERT INTO payments(user_id, plan, amount, receipt_id) VALUES(?,?,?,?)",
                (msg.from_user.id, plan, prices[plan], msg.photo[-1].file_id)
            )
            
            # Notify admin
            for aid in config.ADMIN_IDS:
                try:
                    await msg.bot.send_message(aid, f"🔔 پرداخت جدید\nکاربر: {msg.from_user.id}\nپلن: {plan}\nمبلغ: {prices[plan]:,} تومان")
                    await msg.bot.send_photo(aid, msg.photo[-1].file_id)
                except: pass
            
            await msg.answer(
                f"{E.CHECK} *رسید دریافت شد!*\n\n{E.HOURGLASS} در حال بررسی...\n{E.CLOCK} زمان تایید: ۵-۱۰ دقیقه\n\n{E.ENVELOPE} در صورت تایید، اشتراک شما فعال خواهد شد.",
                parse_mode=ParseMode.HTML
            )
            await state.clear()
        
        @self.router.callback_query(F.data == "watchlist")
        async def watchlist(cb: CallbackQuery):
            uid = cb.from_user.id
            rows = await self.db.fetchall("SELECT symbol FROM watchlists WHERE user_id=? ORDER BY added_at DESC", (uid,))
            
            if not rows:
                text = f"{E.STAR} *واچ‌لیست*\n\n{E.INFO} هیچ نمادی اضافه نکردید."
            else:
                text = f"{E.STAR} *واچ‌لیست شما*\n\n"
                for i, r in enumerate(rows, 1):
                    text += f"{E.POINT_RIGHT} {i}. {r[0]}\n"
            
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data.startswith("addwatch_"))
        async def add_watch(cb: CallbackQuery):
            sym = cb.data.replace("addwatch_", "")
            uid = cb.from_user.id
            
            try:
                await self.db.execute("INSERT OR IGNORE INTO watchlists(user_id, symbol) VALUES(?,?)", (uid, sym))
                await cb.answer(f"{E.CHECK} {sym} به واچ‌لیست اضافه شد!", show_alert=True)
            except:
                await cb.answer(f"{E.CROSS} خطا!", show_alert=True)
        
        @self.router.callback_query(F.data == "alerts")
        async def alerts(cb: CallbackQuery):
            uid = cb.from_user.id
            rows = await self.db.fetchall("SELECT symbol, target_price, alert_type FROM alerts WHERE user_id=? AND active=1", (uid,))
            
            if not rows:
                text = f"{E.BELL} *هشدارها*\n\n{E.INFO} هیچ هشدار فعالی ندارید."
            else:
                text = f"{E.BELL} *هشدارهای فعال*\n\n"
                for r in rows:
                    t = "بالای" if r[2] == 'above' else "پایین"
                    text += f"{E.POINT_RIGHT} {r[0]}: {t} {r[1]}\n"
            
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.PLUS} هشدار جدید", callback_data="new_alert")
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data == "about")
        async def about(cb: CallbackQuery):
            text = f"""
{E.ROBOT} *CryptoPulse-AI v3.1*
{E.LIGHTNING} پیشرفته‌ترین ربات تحلیل کریپتو

{E.BRAIN} *امکانات:*
{E.POINT_RIGHT} هوش مصنوعی Groq
{E.POINT_RIGHT} صرافی CoinEx
{E.POINT_RIGHT} تحلیل تکنیکال کامل
{E.POINT_RIGHT} RSI, MACD, فیبوناچی
{E.POINT_RIGHT} پرایس اکشن
{E.POINT_RIGHT} هشدار هوشمند

{E.CROWN} *سازنده:* {config.CREATOR_USERNAME}
{E.PHONE} *کانال:* {config.CHANNEL_USERNAME}

{E.CLOCK} *زمان:* {TehranTime.format(TehranTime.now(), 'full')}
"""
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.PHONE} کانال تلگرام", url=f"https://t.me/{config.CHANNEL_USERNAME.replace('@','')}")
            kb.button(text=f"{E.ENVELOPE} ارتباط با ما", url=f"https://t.me/{config.CREATOR_USERNAME.replace('@','')}")
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)
        
        @self.router.callback_query(F.data == "support")
        async def support(cb: CallbackQuery):
            text = f"""
{E.ENVELOPE} *پشتیبانی*

{E.POINT_RIGHT} آیدی: {config.CREATOR_USERNAME}
{E.POINT_RIGHT} کانال: {config.CHANNEL_USERNAME}

{E.CLOCK} *ساعات پاسخگویی:*
۸ صبح تا ۱۲ شب

{E.LIGHTNING} *VIP:* کمتر از ۱ ساعت
{E.HOURGLASS} *عادی:* ۲-۴ ساعت
"""
            kb = InlineKeyboardBuilder()
            kb.button(text=f"{E.ENVELOPE} پیام به پشتیبان", url=f"https://t.me/{config.CREATOR_USERNAME.replace('@','')}")
            kb.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
            
            await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode=ParseMode.HTML)

# ═══════════════════════════════════════════════════════════
# 🚀 MAIN APP
# ═══════════════════════════════════════════════════════════

# Initialize
db = Database(config.DATABASE_URL)
ai = GroqAI(config.GROQ_API_KEY)
exchange = CoinExAPI(config.COINEX_KEY, config.COINEX_SECRET)
analyzer = TechnicalAnalyzer()
handlers = BotHandlers(db, ai, exchange, analyzer)

# FastAPI
app = FastAPI(title="CryptoPulse-AI", version="3.1.0")
bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(handlers.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.init()
    logging.info("Database initialized")
    
    if config.WEBHOOK_URL:
        await bot.set_webhook(
            url=f"{config.WEBHOOK_URL}/webhook",
            secret_token=config.WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        logging.info(f"Webhook set: {config.WEBHOOK_URL}/webhook")
    
    # Alert checker
    async def check_alerts():
        while True:
            try:
                alerts = await db.fetchall("SELECT id, user_id, symbol, target_price, alert_type FROM alerts WHERE active=1 AND triggered=0")
                for a in alerts:
                    aid, uid, sym, tp, at = a
                    data = await exchange.ticker(sym)
                    if data.get('code') == 0:
                        price = float(data['data']['last'])
                        triggered = (at == 'above' and price >= tp) or (at == 'below' and price <= tp)
                        if triggered:
                            try:
                                await bot.send_message(uid, f"{E.BELL} *هشدار!*\n\n{E.POINT_RIGHT} {sym} به {price:.4f} رسید!\n{E.TARGET} هدف: {tp}\n{E.CLOCK} {TehranTime.format(TehranTime.now(), 'full')}", parse_mode=ParseMode.HTML)
                            except: pass
                            await db.execute("UPDATE alerts SET triggered=1 WHERE id=?", (aid,))
                await asyncio.sleep(60)
            except Exception as e:
                logging.error(f"Alert checker error: {e}")
                await asyncio.sleep(60)
    
    asyncio.create_task(check_alerts())
    
    logging.info(f"{E.ROCKET} CryptoPulse-AI v3.1 Started!")
    yield
    
    # Shutdown
    await bot.delete_webhook()
    logging.info(f"{E.WAVE} Bot stopped")

app.router.lifespan_context = lifespan

@app.post("/webhook")
async def webhook(request: Request):
    """تلگرام Webhook"""
    try:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != config.WEBHOOK_SECRET:
            raise HTTPException(403, "Invalid secret")
        
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return JSONResponse({"status": "error", "message": str(e)[:100]}, status_code=500)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "time": TehranTime.format(TehranTime.now(), "full"),
        "timestamp": time.time()
    }

@app.get("/stats")
async def stats(request: Request):
    token = request.headers.get("Authorization", "")
    if token != config.WEBHOOK_SECRET:
        raise HTTPException(403)
    return await db.get_stats()

# ═══════════════════════════════════════════════════════════
# 📝 RAILWAY FILES
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)

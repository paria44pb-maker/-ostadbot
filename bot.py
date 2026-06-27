#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💎 VIP PLATINUM BOT v50.0 - ULTIMATE PROFESSIONAL EDITION
ربات حرفه‌ای تحلیل کریپتو با هوش مصنوعی Groq و قیمت‌های CoinEx
نسخه کامل با تمام قابلیت‌های پول‌ساز و مدیریت حرفه‌ای
"""

import os
import sys
import time
import hmac
import json
import base64
import hashlib
import asyncio
import logging
import sqlite3
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
from collections import defaultdict
from functools import wraps

import aiohttp
import httpx
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, ChatMember
)
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ============================================================
# TOKEN - مستقیم در کد
# ============================================================
BOT_TOKEN = "7225279768:AAHB8ZQdgzhFoeV8tPryyReJ-Gq_Y8pI90U"

# ============================================================
# CONFIGURATION
# ============================================================
class Config:
    # Bot
    BOT_TOKEN: str = BOT_TOKEN
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", secrets.token_hex(16))
    
    # APIs
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    COINEX_KEY: str = os.getenv("COINEX_KEY", "")
    COINEX_SECRET: str = os.getenv("COINEX_SECRET", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "vip_bot.db")
    
    # Admin
    ADMIN_IDS: List[int] = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "7225279768").split(",") if x.strip().isdigit()]
    OWNER_ID: int = int(os.getenv("OWNER_ID", "7225279768"))
    OWNER_USERNAME: str = os.getenv("OWNER_USERNAME", "Amir92aa")
    
    # Channel
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
    
    # Limits
    FREE_DAILY_AI_LIMIT: int = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
    VIP_DAILY_AI_LIMIT: int = int(os.getenv("VIP_DAILY_AI_LIMIT", "50"))
    PRO_DAILY_AI_LIMIT: int = int(os.getenv("PRO_DAILY_AI_LIMIT", "200"))
    RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "2"))
    MAX_WATCHLIST: int = int(os.getenv("MAX_WATCHLIST", "20"))
    
    # Pricing (تومان)
    VIP_PRICE: int = int(os.getenv("VIP_PRICE", "199000"))
    PRO_PRICE: int = int(os.getenv("PRO_PRICE", "499000"))
    ELITE_PRICE: int = int(os.getenv("ELITE_PRICE", "999000"))
    
    # Duration (days)
    VIP_DURATION: int = int(os.getenv("VIP_DURATION", "30"))
    PRO_DURATION: int = int(os.getenv("PRO_DURATION", "30"))
    ELITE_DURATION: int = int(os.getenv("ELITE_DURATION", "30"))
    
    # Free trial
    FREE_TRIAL_DAYS: int = int(os.getenv("FREE_TRIAL_DAYS", "3"))
    
    # Card info
    CARD_NUMBER: str = os.getenv("CARD_NUMBER", "6063731196254479")
    CARD_OWNER: str = os.getenv("CARD_OWNER", "فرهاد بهمرد")
    
    # Symbols
    COINEX_SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT",
        "BNB/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT",
        "MATIC/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "TRX/USDT",
        "NEAR/USDT", "APT/USDT", "ARB/USDT", "OP/USDT", "PEPE/USDT"
    ]
    
    # Timeframes
    TIMEFRAMES: List[str] = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]

cfg = Config()

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('vip_bot')
logger.setLevel(logging.INFO)

# ============================================================
# PERSIAN TIME
# ============================================================
TEHRAN_TZ = ZoneInfo("Asia/Tehran")

class Persian:
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    
    @classmethod
    def now(cls):
        return datetime.now(TEHRAN_TZ)
    
    @classmethod
    def shamsi(cls):
        import jdatetime
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    
    @classmethod
    def time(cls):
        return cls.now().strftime('%H:%M:%S')
    
    @classmethod
    def full(cls):
        return f"{cls.DAYS[cls.now().weekday()]} {cls.shamsi()} ساعت {cls.time()}"
    
    @classmethod
    def greet(cls):
        h = cls.now().hour
        e = random.choice(['😊', '🤗', '😎', '🥰', '💖', '✨', '💎'])
        if 5 <= h < 9: return f"صبح بخیر پلاتینیومی {e} 🌄"
        elif 12 <= h < 14: return f"ظهر بخیر دوست من {e} ☀️"
        elif 16 <= h < 18: return f"عصر بخیر تریدر حرفه‌ای {e} 🌇"
        elif 20 <= h <= 23 or 1 <= h < 3: return f"شب خوش VIP {e} 🌙"
        return f"وقت بخیر {e} ⏰"

p = Persian()

# ============================================================
# DATABASE
# ============================================================
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'fa',
                risk_level TEXT DEFAULT 'medium',
                plan TEXT DEFAULT 'free',
                plan_until INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                referred_by INTEGER,
                created_at INTEGER,
                updated_at INTEGER
            )
        ''')
        
        # User state
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                last_ai_at INTEGER DEFAULT 0,
                daily_ai_count INTEGER DEFAULT 0,
                last_reset_day TEXT DEFAULT '',
                total_ai_used INTEGER DEFAULT 0
            )
        ''')
        
        # Watchlist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT,
                target_price REAL,
                alert_type TEXT,
                active INTEGER DEFAULT 1,
                created_at INTEGER,
                triggered_at INTEGER,
                UNIQUE(user_id, symbol)
            )
        ''')
        
        # Alerts
        cur.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT,
                target_price REAL,
                alert_type TEXT,
                status TEXT DEFAULT 'pending',
                created_at INTEGER,
                triggered_at INTEGER
            )
        ''')
        
        # Payments
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan TEXT,
                amount INTEGER,
                tracking_code TEXT,
                status TEXT DEFAULT 'pending',
                reference TEXT,
                created_at INTEGER,
                verified_at INTEGER,
                verified_by INTEGER
            )
        ''')
        
        # Referrals
        cur.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                reward_given INTEGER DEFAULT 0,
                created_at INTEGER,
                UNIQUE(referrer_id, referred_id)
            )
        ''')
        
        # Signals
        cur.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                signal_type TEXT,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                confidence INTEGER,
                analysis TEXT,
                created_at INTEGER,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Performance
        cur.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                signal_id INTEGER,
                entry_price REAL,
                exit_price REAL,
                profit_percent REAL,
                closed_at INTEGER
            )
        ''')
        
        # Logs
        cur.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                data TEXT,
                ip TEXT,
                created_at INTEGER
            )
        ''')
        
        # Price cache
        cur.execute('''
            CREATE TABLE IF NOT EXISTS price_cache (
                symbol TEXT PRIMARY KEY,
                price REAL,
                change REAL,
                volume REAL,
                high REAL,
                low REAL,
                updated_at INTEGER
            )
        ''')
        
        # Coupons
        cur.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                expires_at INTEGER,
                created_at INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    # ========== USERS ==========
    def add_user(self, user_id: int, username: str = "", full_name: str = "", referred_by: int = None):
        now = int(time.time())
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, created_at, updated_at, referred_by) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, full_name, now, now, referred_by)
        )
        # Also add user_state
        cur.execute(
            "INSERT OR IGNORE INTO user_state (user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES (?, ?, ?, ?)",
            (user_id, 0, 0, p.now().date().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs):
        conn = self._get_conn()
        cur = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        cur.execute(f"UPDATE users SET {set_clause}, updated_at = ? WHERE user_id = ?", 
                   list(kwargs.values()) + [int(time.time()), user_id])
        conn.commit()
        conn.close()
    
    def get_plan(self, user_id: int) -> str:
        user = self.get_user(user_id)
        if not user:
            return "free"
        plan = user.get('plan', 'free')
        plan_until = user.get('plan_until', 0)
        if plan in ('vip', 'pro', 'elite') and int(time.time()) < plan_until:
            return plan
        if plan != 'free':
            self.update_user(user_id, plan='free', plan_until=0)
        return 'free'
    
    def is_premium(self, user_id: int) -> bool:
        return self.get_plan(user_id) != 'free'
    
    def activate_plan(self, user_id: int, plan: str, days: int):
        until = int(time.time()) + (days * 86400)
        self.update_user(user_id, plan=plan, plan_until=until)
    
    # ========== USER STATE ==========
    def get_ai_count(self, user_id: int) -> int:
        today = p.now().date().isoformat()
        conn = self._get_conn()
        cur = conn.cursor()
        # Reset if needed
        cur.execute("SELECT last_reset_day, daily_ai_count FROM user_state WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO user_state (user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES (?, ?, ?, ?)",
                (user_id, 0, 0, today)
            )
            conn.commit()
            conn.close()
            return 0
        if row[0] != today:
            cur.execute("UPDATE user_state SET daily_ai_count = 0, last_reset_day = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            conn.close()
            return 0
        count = row[1] if row[1] else 0
        conn.close()
        return count
    
    def increment_ai_count(self, user_id: int) -> int:
        today = p.now().date().isoformat()
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT last_reset_day, daily_ai_count FROM user_state WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row or row[0] != today:
            cur.execute(
                "INSERT OR REPLACE INTO user_state (user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES (?, ?, ?, ?)",
                (user_id, int(time.time()), 1, today)
            )
            conn.commit()
            conn.close()
            return 1
        new_count = (row[1] or 0) + 1
        cur.execute(
            "UPDATE user_state SET daily_ai_count = ?, last_ai_at = ? WHERE user_id = ?",
            (new_count, int(time.time()), user_id)
        )
        conn.commit()
        conn.close()
        return new_count
    
    def get_ai_limit(self, user_id: int) -> int:
        plan = self.get_plan(user_id)
        limits = {
            'free': cfg.FREE_DAILY_AI_LIMIT,
            'vip': cfg.VIP_DAILY_AI_LIMIT,
            'pro': cfg.PRO_DAILY_AI_LIMIT,
            'elite': 999999
        }
        return limits.get(plan, cfg.FREE_DAILY_AI_LIMIT)
    
    # ========== WATCHLIST ==========
    def add_watch(self, user_id: int, symbol: str, target_price: float, alert_type: str = "above"):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO watchlist (user_id, symbol, target_price, alert_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, symbol.upper(), target_price, alert_type, int(time.time()))
        )
        conn.commit()
        conn.close()
    
    def remove_watch(self, user_id: int, symbol: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM watchlist WHERE user_id = ? AND symbol = ?", (user_id, symbol.upper()))
        conn.commit()
        conn.close()
    
    def get_watchlist(self, user_id: int) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM watchlist WHERE user_id = ? AND active = 1", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_watchlists(self) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM watchlist WHERE active = 1")
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ========== PAYMENTS ==========
    def add_payment(self, user_id: int, plan: str, amount: int, tracking_code: str) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (user_id, plan, amount, tracking_code, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, plan, amount, tracking_code, int(time.time()))
        )
        payment_id = cur.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def get_pending_payments(self) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at ASC")
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def verify_payment(self, payment_id: int, admin_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE payments SET status = 'verified', verified_at = ?, verified_by = ? WHERE id = ?",
            (int(time.time()), admin_id, payment_id)
        )
        # Get user_id and plan
        cur.execute("SELECT user_id, plan FROM payments WHERE id = ?", (payment_id,))
        row = cur.fetchone()
        if row:
            user_id, plan = row[0], row[1]
            durations = {'vip': cfg.VIP_DURATION, 'pro': cfg.PRO_DURATION, 'elite': cfg.ELITE_DURATION}
            days = durations.get(plan, 30)
            self.activate_plan(user_id, plan, days)
        conn.commit()
        conn.close()
    
    def reject_payment(self, payment_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE payments SET status = 'rejected' WHERE id = ?", (payment_id,))
        conn.commit()
        conn.close()
    
    # ========== REFERRALS ==========
    def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO referrals (referrer_id, referred_id, created_at) VALUES (?, ?, ?)",
                (referrer_id, referred_id, int(time.time()))
            )
            conn.commit()
            # Give reward
            self.update_user(referrer_id, balance=sqlite3.Row(cur.execute("SELECT balance FROM users WHERE user_id = ?", (referrer_id,)).fetchone())['balance'] + 5)
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def get_referral_count(self, user_id: int) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count
    
    # ========== PRICE CACHE ==========
    def update_price_cache(self, symbol: str, price: float, change: float, volume: float = 0, high: float = 0, low: float = 0):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO price_cache (symbol, price, change, volume, high, low, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (symbol, price, change, volume, high, low, int(time.time()))
        )
        conn.commit()
        conn.close()
    
    def get_price_cache(self, symbol: str) -> Optional[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM price_cache WHERE symbol = ?", (symbol,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ========== LOGS ==========
    def log_action(self, user_id: int, action: str, data: str = "", ip: str = ""):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (user_id, action, data, ip, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, action, data, ip, int(time.time()))
        )
        conn.commit()
        conn.close()
    
    # ========== STATS ==========
    def get_stats(self) -> Dict:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'")
        premium_users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM payments WHERE status = 'verified'")
        total_payments = cur.fetchone()[0]
        cur.execute("SELECT SUM(amount) FROM payments WHERE status = 'verified'")
        total_revenue = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM watchlist WHERE active = 1")
        total_watches = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM alerts WHERE status = 'pending'")
        pending_alerts = cur.fetchone()[0]
        conn.close()
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'total_payments': total_payments,
            'total_revenue': total_revenue,
            'total_watches': total_watches,
            'pending_alerts': pending_alerts
        }

db = Database(cfg.DATABASE_URL)

# ============================================================
# AI ENGINE (GROQ)
# ============================================================
class GroqAI:
    def __init__(self):
        self.api_key = cfg.GROQ_API_KEY
        self.enabled = bool(self.api_key)
        self._client = httpx.AsyncClient(timeout=60.0)
        self._last_request = 0
        self._min_interval = 1.0
        self._cache = {}
        self._cache_ttl = 300
    
    async def _wait(self):
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = time.time()
    
    async def analyze(self, prompt: str) -> Optional[str]:
        if not self.enabled:
            return None
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        if cache_key in self._cache:
            cached, ts = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached
        
        await self._wait()
        
        try:
            response = await self._client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "تو یک تحلیلگر حرفه‌ای کریپتو هستی. فارسی روان و دقیق پاسخ بده."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 800
                }
            )
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                self._cache[cache_key] = (result, time.time())
                return result
            else:
                logger.error(f"Groq error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Groq exception: {e}")
            return None

ai = GroqAI()

# ============================================================
# COINEX API
# ============================================================
class CoinExAPI:
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 30
    
    def _sign(self, method: str, path: str, body: str = "", timestamp: str = ""):
        if not cfg.COINEX_SECRET:
            return ""
        msg = f"{method.upper()}{path}{timestamp}{body}"
        return hmac.new(cfg.COINEX_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    
    async def _fetch_ticker(self, symbol: str) -> Optional[Dict]:
        try:
            url = f"https://api.coinex.com/v2/spot/ticker?market={symbol}"
            headers = {}
            if cfg.COINEX_KEY and cfg.COINEX_SECRET:
                ts = str(int(time.time() * 1000))
                path = f"/v2/spot/ticker?market={symbol}"
                headers = {
                    "X-COINEX-KEY": cfg.COINEX_KEY,
                    "X-COINEX-SIGN": self._sign("GET", path, "", ts),
                    "X-COINEX-TIMESTAMP": ts,
                    "X-COINEX-WINDOWTIME": "5000",
                }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == 0:
                            ticker = data.get("data", {}).get("ticker", {})
                            return {
                                "symbol": symbol,
                                "price": float(ticker.get("last", 0)),
                                "change": float(ticker.get("change", 0)),
                                "high": float(ticker.get("high", 0)),
                                "low": float(ticker.get("low", 0)),
                                "volume": float(ticker.get("vol", 0)),
                            }
        except Exception as e:
            logger.error(f"CoinEx error for {symbol}: {e}")
        return None
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        cache_key = f"price_{symbol}"
        if cache_key in self._cache:
            data, ts = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return data
        
        result = await self._fetch_ticker(symbol)
        if result:
            self._cache[cache_key] = (result, time.time())
            db.update_price_cache(symbol, result['price'], result['change'], result['volume'], result['high'], result['low'])
        return result
    
    async def get_all_prices(self) -> List[Dict]:
        results = []
        for sym in cfg.COINEX_SYMBOLS:
            data = await self.get_price(sym)
            if data:
                results.append(data)
        return results
    
    async def get_movers(self, n: int = 20) -> Dict:
        prices = await self.get_all_prices()
        if not prices:
            return {'up': [], 'down': []}
        sorted_prices = sorted(prices, key=lambda x: x['change'], reverse=True)
        return {
            'up': sorted_prices[:n],
            'down': sorted_prices[-n:][::-1]
        }

coinex = CoinExAPI()

# ============================================================
# FSM STATES
# ============================================================
class FormStates(StatesGroup):
    # AI Chat
    ai_chat = State()
    
    # Watchlist
    watch_symbol = State()
    watch_target = State()
    watch_type = State()
    
    # Payment
    payment_tracking = State()
    
    # Admin
    admin_broadcast = State()
    admin_verify = State()
    admin_reject = State()
    admin_add_coins = State()

# ============================================================
# BOT INITIALIZATION
# ============================================================
bot = Bot(
    token=cfg.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ============================================================
# KEYBOARDS
# ============================================================
def main_keyboard(user_id: int):
    plan = db.get_plan(user_id)
    plan_emoji = "💎" if plan == 'elite' else "⭐" if plan == 'pro' else "💎" if plan == 'vip' else "🆓"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="prices"),
        InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai_analyze")
    )
    builder.row(
        InlineKeyboardButton(text="👀 واچ‌لیست", callback_data="watchlist"),
        InlineKeyboardButton(text="🔔 هشدار قیمت", callback_data="set_alert")
    )
    builder.row(
        InlineKeyboardButton(text="💰 خرید اشتراک", callback_data="buy_plan"),
        InlineKeyboardButton(text=f"{plan_emoji} پلن: {plan}", callback_data="profile")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 دعوت از دوستان", callback_data="referral"),
        InlineKeyboardButton(text="📈 بهترین‌ها", callback_data="movers")
    )
    if user_id in cfg.ADMIN_IDS:
        builder.row(
            InlineKeyboardButton(text="🔧 پنل ادمین", callback_data="admin_panel")
        )
    return builder.as_markup()

def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📨 ارسال همگانی", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="💳 تأیید پرداخت", callback_data="admin_verify")
    )
    builder.row(
        InlineKeyboardButton(text="📊 گزارش عملکرد", callback_data="admin_stats"),
        InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin_users")
    )
    builder.row(
        InlineKeyboardButton(text="💰 افزودن سکه", callback_data="admin_add_coins"),
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")
    )
    return builder.as_markup()

def plan_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"💎 VIP - {cfg.VIP_PRICE:,} تومان", callback_data="buy_vip"),
        InlineKeyboardButton(text=f"⭐ Pro - {cfg.PRO_PRICE:,} تومان", callback_data="buy_pro")
    )
    builder.row(
        InlineKeyboardButton(text=f"💎 Elite - {cfg.ELITE_PRICE:,} تومان", callback_data="buy_elite"),
        InlineKeyboardButton(text="🔄 تمدید", callback_data="renew_plan")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")
    )
    return builder.as_markup()

# ============================================================
# CORE FUNCTIONS
# ============================================================
async def check_membership(user_id: int) -> bool:
    """Check if user is member of required channel"""
    try:
        member = await bot.get_chat_member(chat_id=cfg.CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def safe_send(chat_id: int, text: str, reply_markup=None, parse_mode=ParseMode.HTML):
    try:
        return await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Send error: {e}")
        return None

def format_price(price: float) -> str:
    return f"${price:,.2f}"

def format_change(change: float) -> str:
    emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
    return f"{emoji} {change:+.2f}%"

# ============================================================
# COMMAND HANDLERS
# ============================================================
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username or "", user.full_name or "")
    
    # Check referral
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref="):
        try:
            ref_id = int(args[1].split("=")[1])
            if ref_id != user.id:
                if db.add_referral(ref_id, user.id):
                    await bot.send_message(ref_id, f"🎁 یک کاربر جدید با لینک شما عضو شد! +۵ سکه")
        except:
            pass
    
    # Check membership
    if not await check_membership(user.id):
        channel_link = f"https://t.me/{cfg.CHANNEL_USERNAME.lstrip('@')}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 عضویت در کانال", url=channel_link)],
            [InlineKeyboardButton(text="✅ عضو شدم", callback_data="check_membership")]
        ])
        await message.answer(
            f"⚠️ {user.first_name} عزیز\n\n"
            f"لطفاً ابتدا در کانال {cfg.CHANNEL_USERNAME} عضو شوید.\n"
            f"سپس روی دکمه «عضو شدم» کلیک کنید.",
            reply_markup=keyboard
        )
        return
    
    plan = db.get_plan(user.id)
    welcome = f"""💎 <b>VIP PLATINUM v50.0</b> 💎

{p.greet()} {p.full()}

🔥 به قدرتمندترین ربات تحلیل کریپتو خوش آمدید!

🔹 <b>قابلیت‌ها:</b>
📊 قیمت لحظه‌ای ۲۰ ارز
🤖 تحلیل هوشمند با AI
👀 واچ‌لیست شخصی
🔔 هشدار قیمت هوشمند
📈 تحلیل روزانه و هفتگی
💰 خرید اشتراک VIP/Pro/Elite

👤 <b>وضعیت شما:</b> {plan.upper()}
🪙 <b>سکه:</b> {db.get_user(user.id).get('balance', 0) if db.get_user(user.id) else 0}

🔹 <b>پلن‌ها:</b>
🆓 رایگان: {cfg.FREE_DAILY_AI_LIMIT} سوال AI در روز
💎 VIP: {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز
⭐ Pro: {cfg.PRO_PRICE:,} تومان / {cfg.PRO_DURATION} روز
💎 Elite: {cfg.ELITE_PRICE:,} تومان / {cfg.ELITE_DURATION} روز

💡 از دکمه‌های زیر استفاده کنید:
"""
    await message.answer(welcome, reply_markup=main_keyboard(user.id))

@router.callback_query(F.data == "check_membership")
async def check_membership_callback(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    if await check_membership(user.id):
        await cmd_start(callback.message)
        await callback.message.delete()
    else:
        channel_link = f"https://t.me/{cfg.CHANNEL_USERNAME.lstrip('@')}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 عضویت در کانال", url=channel_link)],
            [InlineKeyboardButton(text="✅ عضو شدم", callback_data="check_membership")]
        ])
        await callback.message.edit_text(
            "❌ شما هنوز در کانال عضو نشده‌اید!\n\nلطفاً ابتدا عضو شوید.",
            reply_markup=keyboard
        )

@router.message(Command("time"))
async def cmd_time(message: Message):
    await message.answer(f"🕐 <b>زمان تهران</b>\n{p.full()}")

@router.message(Command("me"))
async def cmd_me(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ ابتدا /start را بزنید.")
        return
    plan = db.get_plan(message.from_user.id)
    ai_count = db.get_ai_count(message.from_user.id)
    ai_limit = db.get_ai_limit(message.from_user.id)
    ref_count = db.get_referral_count(message.from_user.id)
    
    text = f"""👤 <b>پروفایل شما</b>

🆔 آیدی: {message.from_user.id}
👤 نام: {message.from_user.full_name}
📛 یوزرنیم: @{message.from_user.username or 'ندارد'}

💎 پلن: <b>{plan.upper()}</b>
📅 انقضا: {datetime.fromtimestamp(user.get('plan_until', 0), TEHRAN_TZ).strftime('%Y/%m/%d') if user.get('plan_until', 0) > 0 else 'نامحدود'}

🤖 AI امروز: {ai_count} / {ai_limit}
🪙 سکه: {user.get('balance', 0)}
🎁 تعداد دعوت: {ref_count}

📅 تاریخ عضویت: {datetime.fromtimestamp(user.get('created_at', 0), TEHRAN_TZ).strftime('%Y/%m/%d')}
🕐 زمان تهران: {p.full()}
"""
    await message.answer(text, reply_markup=main_keyboard(message.from_user.id))

@router.message(Command("price"))
async def cmd_price(message: Message):
    parts = message.text.split()
    symbol = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
    if not symbol.endswith("/USDT"):
        symbol = f"{symbol}/USDT"
    
    await message.answer(f"📊 در حال دریافت قیمت {symbol}...")
    data = await coinex.get_price(symbol)
    if data:
        text = f"""📊 <b>قیمت {symbol}</b>

💰 قیمت: <b>{format_price(data['price'])}</b>
📈 تغییر: {format_change(data['change'])}
📊 بالاترین: {format_price(data['high'])}
📉 پایین‌ترین: {format_price(data['low'])}
📦 حجم: {data['volume']:,.0f}

🕐 {p.full()}
"""
        await message.answer(text)
    else:
        await message.answer("❌ خطا در دریافت قیمت. لطفاً مجدداً تلاش کنید.")

@router.message(Command("ai"))
async def cmd_ai(message: Message, state: FSMContext):
    prompt = message.text.replace("/ai", "").strip()
    if not prompt:
        await message.answer(
            "🤖 <b>تحلیل هوشمند</b>\n\n"
            "لطفاً سوال یا تحلیل خود را بنویسید.\n"
            "مثال: <code>/ai بیت‌کوین رو با اندیکاتورها تحلیل کن</code>"
        )
        return
    
    user_id = message.from_user.id
    plan = db.get_plan(user_id)
    ai_count = db.get_ai_count(user_id)
    ai_limit = db.get_ai_limit(user_id)
    
    # Check AI limit
    if ai_count >= ai_limit and plan == 'free':
        await message.answer(
            f"⚠️ سقف AI رایگان امروز ({cfg.FREE_DAILY_AI_LIMIT}) پر شده.\n\n"
            f"برای دسترسی بیشتر، پلن VIP تهیه کنید:\n"
            f"💎 VIP: {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز"
        )
        return
    
    # Check rate limit
    if not await rate_limit_ok(user_id):
        await message.answer(f"⏳ لطفاً {cfg.RATE_LIMIT_SECONDS} ثانیه بعد دوباره تلاش کنید.")
        return
    
    await message.answer("🤖 در حال تحلیل... لطفاً صبر کنید.")
    
    # Build user profile
    user = db.get_user(user_id)
    profile = f"risk={user.get('risk_level', 'medium')}, plan={plan}"
    
    result = await ai.analyze(prompt)
    if result:
        db.increment_ai_count(user_id)
        await message.answer(result[:4000])
        db.log_action(user_id, "ai_analysis", prompt[:100])
    else:
        await message.answer("❌ خطا در تحلیل. لطفاً مجدداً تلاش کنید.")

@router.message(Command("watch"))
async def cmd_watch(message: Message, state: FSMContext):
    user_id = message.from_user.id
    plan = db.get_plan(user_id)
    
    if plan == 'free':
        await message.answer(
            "⛔ این قابلیت فقط برای کاربران VIP است.\n\n"
            f"💎 VIP: {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز"
        )
        return
    
    watches = db.get_watchlist(user_id)
    if len(watches) >= cfg.MAX_WATCHLIST and plan != 'elite':
        await message.answer(f"⚠️ حداکثر {cfg.MAX_WATCHLIST} ارز در واچ‌لیست مجاز است.")
        return
    
    await state.set_state(FormStates.watch_symbol)
    await message.answer(
        "👀 <b>افزودن به واچ‌لیست</b>\n\n"
        "نام ارز را وارد کنید.\n"
        "مثال: <code>BTC</code> یا <code>ETH</code>"
    )

@router.message(FormStates.watch_symbol)
async def watch_symbol(message: Message, state: FSMContext):
    symbol = message.text.upper().strip()
    if symbol not in [s.split('/')[0] for s in cfg.COINEX_SYMBOLS]:
        await message.answer(
            "❌ ارز نامعتبر.\n\n"
            "ارزهای پشتیبانی شده:\n" + ", ".join([s.split('/')[0] for s in cfg.COINEX_SYMBOLS])
        )
        return
    await state.update_data(symbol=symbol)
    await state.set_state(FormStates.watch_target)
    await message.answer(f"💰 قیمت هدف برای {symbol} را وارد کنید (عدد):")

@router.message(FormStates.watch_target)
async def watch_target(message: Message, state: FSMContext):
    try:
        target = float(message.text.replace(',', ''))
    except:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
        return
    await state.update_data(target=target)
    await state.set_state(FormStates.watch_type)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬆️ بالاتر از", callback_data="watch_above"),
         InlineKeyboardButton(text="⬇️ پایین‌تر از", callback_data="watch_below")]
    ])
    await message.answer("📈 نوع هشدار را انتخاب کنید:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("watch_"))
async def watch_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    alert_type = "above" if callback.data == "watch_above" else "below"
    data = await state.get_data()
    symbol = data.get('symbol')
    target = data.get('target')
    
    db.add_watch(callback.from_user.id, symbol, target, alert_type)
    await state.clear()
    await callback.message.edit_text(
        f"✅ هشدار برای {symbol} با هدف {alert_type} ${target:.2f} ثبت شد.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👀 مشاهده واچ‌لیست", callback_data="watchlist")]
        ])
    )

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    text = f"""💰 <b>خرید اشتراک VIP</b>

💎 <b>پلن‌ها:</b>

🆓 <b>رایگان</b>
• {cfg.FREE_DAILY_AI_LIMIT} سوال AI در روز
• ۱ ارز در واچ‌لیست

💎 <b>VIP - {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز</b>
• {cfg.VIP_DAILY_AI_LIMIT} سوال AI در روز
• {cfg.MAX_WATCHLIST} ارز در واچ‌لیست
• هشدار قیمت
• تحلیل روزانه

⭐ <b>Pro - {cfg.PRO_PRICE:,} تومان / {cfg.PRO_DURATION} روز</b>
• {cfg.PRO_DAILY_AI_LIMIT} سوال AI در روز
• واچ‌لیست نامحدود
• هشدار پیشرفته
• تحلیل روزانه و هفتگی
• پشتیبانی ویژه

💎 <b>Elite - {cfg.ELITE_PRICE:,} تومان / {cfg.ELITE_DURATION} روز</b>
• AI نامحدود
• همه امکانات
• تحلیل اختصاصی
• پشتیبانی ۲۴/۷

💳 <b>نحوه پرداخت:</b>
کارت به کارت به شماره:
<code>{cfg.CARD_NUMBER}</code>
به نام: <b>{cfg.CARD_OWNER}</b>

✅ پس از واریز، کد پیگیری را با دستور <code>/pay [کد]</code> ارسال کنید.
"""
    await message.answer(text, reply_markup=plan_keyboard())

@router.message(Command("pay"))
async def cmd_pay(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ لطفاً کد پیگیری را همراه با دستور ارسال کنید:\n"
            "<code>/pay 123456789</code>"
        )
        return
    
    tracking = parts[1].strip()
    db.add_payment(message.from_user.id, "vip", cfg.VIP_PRICE, tracking)
    await message.answer(
        f"✅ کد پیگیری {tracking} ثبت شد.\n\n"
        "⏳ پرداخت شما در حال بررسی است.\n"
        "پس از تأیید ادمین، اشتراک VIP فعال خواهد شد."
    )
    
    # Notify admins
    for admin_id in cfg.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💳 <b>درخواست پرداخت جدید</b>\n\n"
                f"🆔 کاربر: {message.from_user.id}\n"
                f"👤 نام: {message.from_user.full_name}\n"
                f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
                f"📎 کد پیگیری: {tracking}\n"
                f"💰 مبلغ: {cfg.VIP_PRICE:,} تومان\n\n"
                f"✅ برای تأیید: <code>/verify {tracking}</code>"
            )
        except:
            pass

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز.")
        return
    await message.answer("🔧 <b>پنل ادمین</b>", reply_markup=admin_keyboard())

# ============================================================
# CALLBACK HANDLERS
# ============================================================
@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        f"💎 VIP PLATINUM\n\n{p.greet()} {p.full()}",
        reply_markup=main_keyboard(callback.from_user.id)
    )

@router.callback_query(F.data == "prices")
async def cb_prices(callback: CallbackQuery):
    await callback.answer("📊 دریافت قیمت‌ها...")
    prices = await coinex.get_all_prices()
    if not prices:
        await callback.message.edit_text("❌ خطا در دریافت قیمت‌ها")
        return
    
    text = "📊 <b>قیمت لحظه‌ای ارزها</b>\n\n"
    for p in prices[:10]:
        text += f"{p['symbol']}: <b>{format_price(p['price'])}</b> {format_change(p['change'])}\n"
    
    text += f"\n🕐 {p.full()}"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="prices")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "ai_analyze")
async def cb_ai_analyze(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🤖 <b>تحلیل هوشمند</b>\n\n"
        "سوال یا تحلیل خود را به صورت متن بنویسید.\n"
        "مثال: <code>بیت‌کوین رو با اندیکاتورها تحلیل کن</code>\n\n"
        "💡 از دستور <code>/ai</code> نیز استفاده کنید.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@router.callback_query(F.data == "watchlist")
async def cb_watchlist(callback: CallbackQuery):
    await callback.answer()
    watches = db.get_watchlist(callback.from_user.id)
    if not watches:
        await callback.message.edit_text(
            "👀 <b>واچ‌لیست شما خالی است.</b>\n\n"
            "برای افزودن ارز، از دستور <code>/watch</code> استفاده کنید.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ افزودن", callback_data="set_alert")],
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
            ])
        )
        return
    
    text = "👀 <b>واچ‌لیست شما</b>\n\n"
    for w in watches:
        emoji = "⬆️" if w['alert_type'] == 'above' else "⬇️"
        text += f"• {w['symbol']}: {emoji} ${w['target_price']:.2f}\n"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن", callback_data="set_alert")],
        [InlineKeyboardButton(text="❌ پاک کردن", callback_data="clear_watchlist")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "set_alert")
async def cb_set_alert(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    plan = db.get_plan(user_id)
    
    if plan == 'free':
        await callback.message.edit_text(
            "⛔ این قابلیت فقط برای کاربران VIP است.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_plan")],
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
            ])
        )
        return
    
    await state.set_state(FormStates.watch_symbol)
    await callback.message.edit_text(
        "👀 <b>افزودن هشدار قیمت</b>\n\n"
        "نام ارز را وارد کنید.\n"
        "مثال: <code>BTC</code> یا <code>ETH</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@router.callback_query(F.data == "clear_watchlist")
async def cb_clear_watchlist(callback: CallbackQuery):
    await callback.answer()
    # Delete all watchlist items for user
    conn = sqlite3.connect(cfg.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("DELETE FROM watchlist WHERE user_id = ?", (callback.from_user.id,))
    conn.commit()
    conn.close()
    await callback.message.edit_text(
        "✅ واچ‌لیست شما پاک شد.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@router.callback_query(F.data == "buy_plan")
async def cb_buy_plan(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💰 <b>خرید اشتراک</b>\n\n"
        "لطفاً پلن مورد نظر را انتخاب کنید:",
        reply_markup=plan_keyboard()
    )

@router.callback_query(F.data.startswith("buy_"))
async def cb_buy_specific(callback: CallbackQuery):
    await callback.answer()
    plan_map = {
        'buy_vip': ('VIP', cfg.VIP_PRICE, cfg.VIP_DURATION),
        'buy_pro': ('Pro', cfg.PRO_PRICE, cfg.PRO_DURATION),
        'buy_elite': ('Elite', cfg.ELITE_PRICE, cfg.ELITE_DURATION)
    }
    key = callback.data
    if key not in plan_map:
        return
    
    plan_name, price, days = plan_map[key]
    text = f"""💰 <b>خرید اشتراک {plan_name}</b>

💎 مبلغ: <b>{price:,} تومان</b>
📅 مدت: <b>{days} روز</b>
✨ ویژگی‌ها: AI پیشرفته، واچ‌لیست، هشدار، تحلیل روزانه

💳 <b>نحوه پرداخت:</b>
کارت به کارت به شماره:
<code>{cfg.CARD_NUMBER}</code>
به نام: <b>{cfg.CARD_OWNER}</b>

✅ پس از واریز، کد پیگیری را با دستور <code>/pay [کد]</code> ارسال کنید.
"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="buy_plan")]
    ]))

@router.callback_query(F.data == "renew_plan")
async def cb_renew_plan(callback: CallbackQuery):
    await callback.answer()
    user = db.get_user(callback.from_user.id)
    plan = db.get_plan(callback.from_user.id)
    
    if plan == 'free':
        await callback.message.edit_text(
            "❌ شما پلن فعالی ندارید.\n"
            "لطفاً یک پلن خریداری کنید.",
            reply_markup=plan_keyboard()
        )
        return
    
    prices = {'vip': cfg.VIP_PRICE, 'pro': cfg.PRO_PRICE, 'elite': cfg.ELITE_PRICE}
    durations = {'vip': cfg.VIP_DURATION, 'pro': cfg.PRO_DURATION, 'elite': cfg.ELITE_DURATION}
    
    price = prices.get(plan, cfg.VIP_PRICE)
    days = durations.get(plan, cfg.VIP_DURATION)
    
    text = f"""🔄 <b>تمدید اشتراک {plan.upper()}</b>

💎 مبلغ: <b>{price:,} تومان</b>
📅 مدت: <b>{days} روز</b>

💳 <b>نحوه پرداخت:</b>
کارت به کارت به شماره:
<code>{cfg.CARD_NUMBER}</code>
به نام: <b>{cfg.CARD_OWNER}</b>

✅ پس از واریز، کد پیگیری را با دستور <code>/pay [کد]</code> ارسال کنید.
"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="buy_plan")]
    ]))

@router.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery):
    await callback.answer()
    await cmd_me(callback.message)

@router.callback_query(F.data == "referral")
async def cb_referral(callback: CallbackQuery):
    await callback.answer()
    bot_username = (await bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref={callback.from_user.id}"
    ref_count = db.get_referral_count(callback.from_user.id)
    
    text = f"""🎁 <b>سیستم دعوت دوستان</b>

🔗 لینک دعوت شما:
<code>{ref_link}</code>

👥 تعداد دعوت‌ها: <b>{ref_count}</b>

✨ <b>پاداش:</b>
• هر دعوت: +۵ سکه به شما
• دوست شما: +۱۰ سکه

📤 این لینک را برای دوستان خود ارسال کنید.
"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 کپی لینک", callback_data="copy_ref")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "copy_ref")
async def cb_copy_ref(callback: CallbackQuery):
    await callback.answer("✅ لینک کپی شد!", show_alert=True)
    bot_username = (await bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref={callback.from_user.id}"
    await callback.message.answer(f"🔗 لینک دعوت شما:\n<code>{ref_link}</code>")

@router.callback_query(F.data == "movers")
async def cb_movers(callback: CallbackQuery):
    await callback.answer("📈 دریافت بهترین‌ها...")
    movers = await coinex.get_movers(10)
    
    if not movers['up'] and not movers['down']:
        await callback.message.edit_text("❌ خطا در دریافت داده")
        return
    
    text = "📈 <b>بهترین و بدترین ارزها</b>\n\n"
    
    text += "🟢 <b>بیشترین رشد:</b>\n"
    for item in movers['up'][:5]:
        text += f"• {item['symbol']}: {format_change(item['change'])} ({format_price(item['price'])})\n"
    
    text += "\n🔴 <b>بیشترین ریزش:</b>\n"
    for item in movers['down'][:5]:
        text += f"• {item['symbol']}: {format_change(item['change'])} ({format_price(item['price'])})\n"
    
    text += f"\n🕐 {p.full()}"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="movers")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

# ============================================================
# ADMIN CALLBACKS
# ============================================================
@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text("🔧 <b>پنل ادمین</b>", reply_markup=admin_keyboard())

@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    await state.set_state(FormStates.admin_broadcast)
    await callback.message.edit_text(
        "📨 <b>ارسال همگانی</b>\n\n"
        "متن پیام خود را وارد کنید.\n\n"
        "⚠️ پیام به <b>همه کاربران</b> ارسال خواهد شد.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 انصراف", callback_data="admin_panel")]
        ])
    )

@router.message(FormStates.admin_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        await state.clear()
        return
    
    # Get all users
    conn = sqlite3.connect(cfg.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn.close()
    
    await message.answer(f"📤 در حال ارسال به {len(users)} کاربر...")
    
    success = 0
    fail = 0
    for user_id in users:
        try:
            await bot.send_message(user_id[0], message.text, parse_mode=ParseMode.HTML)
            success += 1
        except:
            fail += 1
        await asyncio.sleep(0.05)  # Rate limit
    
    await message.answer(
        f"✅ ارسال همگانی انجام شد.\n"
        f"📤 موفق: {success}\n"
        f"📤 ناموفق: {fail}"
    )
    await state.clear()

@router.callback_query(F.data == "admin_verify")
async def cb_admin_verify(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    
    pending = db.get_pending_payments()
    if not pending:
        await callback.message.edit_text(
            "✅ هیچ درخواست پرداختی در انتظار تأیید نیست.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
            ])
        )
        return
    
    text = "💳 <b>درخواست‌های پرداخت</b>\n\n"
    for p in pending[:10]:
        text += f"🆔 {p['id']} | کاربر: {p['user_id']}\n"
        text += f"📎 کد: {p['tracking_code']}\n"
        text += f"💰 {p['amount']:,} تومان | پلن: {p['plan']}\n"
        text += f"📅 {datetime.fromtimestamp(p['created_at'], TEHRAN_TZ).strftime('%Y/%m/%d %H:%M')}\n\n"
    
    text += "\n✅ برای تأیید: <code>/verify [id]</code>\n"
    text += "❌ برای رد: <code>/reject [id]</code>"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
    ]))

@router.message(Command("verify"))
async def admin_verify_payment(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ <code>/verify [payment_id]</code>")
        return
    
    try:
        payment_id = int(parts[1])
    except:
        await message.answer("❌ آیدی نامعتبر")
        return
    
    # Check if payment exists
    conn = sqlite3.connect(cfg.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT user_id, plan FROM payments WHERE id = ? AND status = 'pending'", (payment_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        await message.answer("❌ پرداخت یافت نشد یا قبلاً تأیید شده است.")
        return
    
    user_id, plan = row
    db.verify_payment(payment_id, message.from_user.id)
    
    await message.answer(f"✅ پرداخت {payment_id} تأیید شد.\nاشتراک {plan.upper()} کاربر {user_id} فعال شد.")
    
    # Notify user
    try:
        await bot.send_message(
            user_id,
            f"🎉 <b>تبریک!</b>\n\n"
            f"اشتراک {plan.upper()} شما با موفقیت فعال شد.\n"
            f"📅 مدت: ۳۰ روز\n\n"
            f"💎 از تمام قابلیت‌های ویژه استفاده کنید."
        )
    except:
        pass

@router.message(Command("reject"))
async def admin_reject_payment(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ <code>/reject [payment_id]</code>")
        return
    
    try:
        payment_id = int(parts[1])
    except:
        await message.answer("❌ آیدی نامعتبر")
        return
    
    db.reject_payment(payment_id)
    await message.answer(f"✅ پرداخت {payment_id} رد شد.")

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    
    stats = db.get_stats()
    
    text = f"""📊 <b>گزارش عملکرد</b>

👥 کل کاربران: <b>{stats['total_users']}</b>
💎 کاربران پریمیوم: <b>{stats['premium_users']}</b>
💰 کل پرداخت‌ها: <b>{stats['total_payments']}</b>
📈 درآمد کل: <b>{stats['total_revenue']:,} تومان</b>
👀 واچ‌لیست‌ها: <b>{stats['total_watches']}</b>
⏳ پرداخت‌های در انتظار: <b>{stats['pending_alerts']}</b>

🕐 {p.full()}
"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
    ]))

@router.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    
    conn = sqlite3.connect(cfg.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, full_name, plan, plan_until FROM users ORDER BY created_at DESC LIMIT 20")
    users = cur.fetchall()
    conn.close()
    
    text = "📝 <b>۲۰ کاربر اخیر</b>\n\n"
    for u in users:
        plan_status = "✅" if u[4] > int(time.time()) else "❌"
        text += f"🆔 {u[0]} | {u[1] or u[2] or 'نامشخص'}\n"
        text += f"💎 {plan_status} {u[3].upper()}\n\n"
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
    ]))

@router.callback_query(F.data == "admin_add_coins")
async def cb_admin_add_coins(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    await state.set_state(FormStates.admin_add_coins)
    await callback.message.edit_text(
        "💰 <b>افزودن سکه به کاربر</b>\n\n"
        "لطفاً به صورت زیر ارسال کنید:\n"
        "<code>افزودن سکه [user_id] [تعداد]</code>\n\n"
        "مثال: <code>افزودن سکه 123456789 50</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 انصراف", callback_data="admin_panel")]
        ])
    )

@router.message(FormStates.admin_add_coins)
async def process_add_coins(message: Message, state: FSMContext):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        await state.clear()
        return
    
    parts = message.text.split()
    if len(parts) != 3 or parts[0] != "افزودن" or parts[1] != "سکه":
        await message.answer(
            "❌ فرمت صحیح:\n"
            "<code>افزودن سکه [user_id] [تعداد]</code>"
        )
        return
    
    try:
        user_id = int(parts[2])
        amount = int(parts[1])
    except:
        await message.answer("❌ آیدی یا تعداد نامعتبر")
        return
    
    db.update_user(user_id, balance=db.get_user(user_id).get('balance', 0) + amount)
    await message.answer(f"✅ {amount} سکه به کاربر {user_id} اضافه شد.")
    await state.clear()

# ============================================================
# MESSAGE HANDLERS
# ============================================================
@router.message()
async def handle_payment_proof(message: Message):
    """Handle payment proof messages"""
    text = (message.text or "").lower()
    keywords = ["رسید", "شماره پیگیری", "واریز", "پرداخت", "کارت به کارت"]
    
    if any(kw in text for kw in keywords):
        await message.answer(
            "✅ رسید شما دریافت شد.\n"
            "⏳ برای تأیید نهایی، ادمین بررسی می‌کند.\n\n"
            "📢 پس از تأیید، اشتراک VIP شما فعال خواهد شد."
        )
        
        # Notify admins
        for admin_id in cfg.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"💳 <b>درخواست پرداخت VIP</b>\n\n"
                    f"🆔 کاربر: {message.from_user.id}\n"
                    f"👤 نام: {message.from_user.full_name}\n"
                    f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n\n"
                    f"📝 پیام:\n{message.text[:500]}\n\n"
                    f"✅ برای تأیید: <code>/verify [id]</code>\n"
                    f"❌ برای رد: <code>/reject [id]</code>"
                )
            except Exception as e:
                logger.error(f"Error sending to admin: {e}")
        return
    
    # Default response
    await message.answer(
        "💎 از دکمه‌های منو استفاده کنید.\n\n"
        "📝 برای کمک: /start"
    )

# ============================================================
# PRICE ALERT CHECKER
# ============================================================
async def price_alert_checker():
    """Background task to check price alerts"""
    while True:
        try:
            watches = db.get_all_watchlists()
            if watches:
                for watch in watches:
                    symbol = watch['symbol']
                    if not symbol.endswith("/USDT"):
                        symbol = f"{symbol}/USDT"
                    
                    price_data = await coinex.get_price(symbol)
                    if not price_data:
                        continue
                    
                    current_price = price_data['price']
                    target = watch['target_price']
                    alert_type = watch['alert_type']
                    
                    triggered = False
                    if alert_type == 'above' and current_price >= target:
                        triggered = True
                    elif alert_type == 'below' and current_price <= target:
                        triggered = True
                    
                    if triggered:
                        # Deactivate alert
                        conn = sqlite3.connect(cfg.DATABASE_URL)
                        cur = conn.cursor()
                        cur.execute("UPDATE watchlist SET active = 0, triggered_at = ? WHERE id = ?", 
                                   (int(time.time()), watch['id']))
                        conn.commit()
                        conn.close()
                        
                        # Notify user
                        try:
                            await bot.send_message(
                                watch['user_id'],
                                f"🔔 <b>هشدار قیمت</b>\n\n"
                                f"📊 {watch['symbol']} به قیمت <b>${current_price:.2f}</b> رسید.\n"
                                f"🎯 هدف شما: {alert_type} ${target:.2f}\n"
                                f"📈 تغییر: {format_change(price_data['change'])}\n\n"
                                f"🕐 {p.full()}"
                            )
                        except:
                            pass
        except Exception as e:
            logger.error(f"Alert checker error: {e}")
        await asyncio.sleep(60)  # Check every minute

# ============================================================
# RATE LIMIT HELPER
# ============================================================
async def rate_limit_ok(user_id: int) -> bool:
    conn = sqlite3.connect(cfg.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT last_ai_at FROM user_state WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    last = row[0] if row else 0
    return (int(time.time()) - int(last)) >= cfg.RATE_LIMIT_SECONDS

# ============================================================
# FASTAPI SETUP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks
    asyncio.create_task(price_alert_checker())
    asyncio.create_task(daily_channel_post())
    
    # Set webhook
    if cfg.WEBHOOK_URL:
        try:
            await bot.set_webhook(
                url=f"{cfg.WEBHOOK_URL}/webhook",
                secret_token=cfg.WEBHOOK_SECRET,
                drop_pending_updates=True,
                max_connections=100
            )
            logger.info(f"✅ Webhook set to {cfg.WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
    else:
        logger.warning("⚠️ WEBHOOK_URL not set, webhook disabled")
    
    logger.info("🚀 VIP PLATINUM BOT v50.0 started successfully!")
    yield
    
    # Cleanup
    try:
        await bot.delete_webhook()
        await bot.session.close()
    except:
        pass
    logger.info("🛑 Bot stopped")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    if x_telegram_bot_api_secret_token != cfg.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")
    
    body = await request.json()
    update = types.Update(**body)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "time": p.full(),
        "version": "50.0",
        "users": db.get_stats()['total_users']
    }

# ============================================================
# DAILY CHANNEL POST
# ============================================================
async def daily_channel_post():
    """Send daily report to channel"""
    while True:
        try:
            # Wait until 23:00 Tehran time
            now = datetime.now(TEHRAN_TZ)
            if now.hour == 23 and now.minute == 0:
                stats = db.get_stats()
                movers = await coinex.get_movers(5)
                
                text = f"""📊 <b>گزارش روزانه بازار</b>

🕐 {p.full()}

📈 <b>آمار ربات:</b>
👥 کاربران: {stats['total_users']}
💎 کاربران VIP: {stats['premium_users']}
💰 درآمد کل: {stats['total_revenue']:,} تومان

🔝 <b>بهترین ارزهای امروز:</b>
"""
                for item in movers['up'][:3]:
                    text += f"• {item['symbol']}: {format_change(item['change'])}\n"
                
                text += f"\n🔻 <b>بدترین ارزهای امروز:</b>\n"
                for item in movers['down'][:3]:
                    text += f"• {item['symbol']}: {format_change(item['change'])}\n"
                
                text += f"\n💎 <b>پلن‌های VIP:</b>\n"
                text += f"VIP: {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز\n"
                text += f"Pro: {cfg.PRO_PRICE:,} تومان / {cfg.PRO_DURATION} روز\n"
                text += f"Elite: {cfg.ELITE_PRICE:,} تومان / {cfg.ELITE_DURATION} روز\n"
                text += f"\n📢 {cfg.CHANNEL_USERNAME}"
                
                await bot.send_message(chat_id=cfg.CHANNEL_USERNAME, text=text, parse_mode=ParseMode.HTML)
                logger.info("📤 Daily report sent to channel")
        except Exception as e:
            logger.error(f"Daily channel post error: {e}")
        await asyncio.sleep(60)  # Check every minute

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    # If no webhook URL, run in polling mode
    if not cfg.WEBHOOK_URL:
        logger.info("🚀 Starting in polling mode...")
        asyncio.run(async_polling())
    else:
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))

async def async_polling():
    """Run bot in polling mode (for local testing)"""
    asyncio.create_task(price_alert_checker())
    asyncio.create_task(daily_channel_post())
    await dp.start_polling(bot)

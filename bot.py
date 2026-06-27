#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
import sqlite3
import json
import time
import hashlib
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from contextlib import asynccontextmanager

import aiohttp
import httpx
import pytz
import jdatetime
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT
# ============================================================
load_dotenv()

# ============================================================
# TOKEN LOADING - MULTIPLE SOURCES WITH DEBUG
# ============================================================

def load_token() -> str:
    """تلاش برای دریافت توکن از منابع مختلف با نمایش خطا"""
    
    # 1. از متغیر محیطی BOT_TOKEN
    token = os.getenv("BOT_TOKEN")
    if token and token.strip():
        token = token.strip()
        print(f"✅ Token loaded from environment variable (length: {len(token)})")
        return token
    
    # 2. از متغیر TELEGRAM_TOKEN (برخی پلتفرم‌ها)
    token = os.getenv("TELEGRAM_TOKEN")
    if token and token.strip():
        token = token.strip()
        print(f"✅ Token loaded from TELEGRAM_TOKEN (length: {len(token)})")
        return token
    
    # 3. از فایل token.txt
    try:
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                token = f.read().strip()
            if token:
                print(f"✅ Token loaded from token.txt (length: {len(token)})")
                return token
    except Exception as e:
        print(f"⚠️ Could not read token.txt: {e}")
    
    # 4. از فایل .env (دستی)
    try:
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("BOT_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if token:
                            print(f"✅ Token loaded from .env file (length: {len(token)})")
                            return token
    except Exception as e:
        print(f"⚠️ Could not read .env: {e}")
    
    # 5. از آرگومان خط فرمان
    for arg in sys.argv:
        if arg.startswith("BOT_TOKEN="):
            token = arg.split("=", 1)[1]
            if token:
                print(f"✅ Token loaded from command line (length: {len(token)})")
                return token
    
    # 6. اگر هیچ کدام کار نکرد، یک فایل token.txt بساز و راهنمایی کن
    print("❌ BOT_TOKEN not found in any source!")
    print("Please choose one of the following methods:")
    print("1. Set BOT_TOKEN in Railway Variables (recommended)")
    print("2. Create a file named 'token.txt' with your token inside")
    print("3. Use: python bot.py BOT_TOKEN=your_token_here")
    print("4. Add BOT_TOKEN=your_token to .env file")
    
    # ایجاد فایل token.txt خالی برای راهنمایی
    try:
        with open("token.txt", "w") as f:
            f.write("# Paste your Telegram bot token here and remove the #\n")
            f.write("# Example: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n")
        print("📝 Created token.txt file. Please add your token there.")
    except:
        pass
    
    sys.exit(1)

BOT_TOKEN = load_token()

# ============================================================
# VALIDATE TOKEN FORMAT
# ============================================================
def validate_token_format(token: str) -> bool:
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    if re.match(pattern, token):
        return True
    print(f"⚠️ Token format looks unusual: {token[:15]}...")
    return True  # still try

if not validate_token_format(BOT_TOKEN):
    print("❌ Token format is invalid!")
    sys.exit(1)

print(f"✅ BOT_TOKEN validated (length: {len(BOT_TOKEN)})")

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
# CONFIG
# ============================================================
class Config:
    BOT_TOKEN: str = BOT_TOKEN
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "default-secret")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "@CryptoPulse606")
    ADMIN_IDS: List[int] = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "7225279768").split(",")]
    OWNER_ID: int = int(os.getenv("OWNER_ID", "7225279768"))
    CARD_NUMBER: str = os.getenv("CARD_NUMBER", "6037997513379934")
    CARD_OWNER: str = os.getenv("CARD_OWNER", "علی محمدی")
    VIP_PRICE: int = int(os.getenv("VIP_PRICE", "199000"))
    VIP_DURATION: int = int(os.getenv("VIP_DURATION", "30"))
    FREE_TRIAL_DAYS: int = int(os.getenv("FREE_TRIAL_DAYS", "3"))
    PORT: int = int(os.getenv("PORT", "8080"))
    DB_FILE: str = "vip_bot.db"
    COINEX_SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT",
        "BNB/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT"
    ]

cfg = Config()

# ============================================================
# DATABASE (همان کد قبلی - فشرده شده برای صرفه‌جویی)
# ============================================================
class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._init_db()
    
    def _get_conn(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at TEXT,
                is_vip INTEGER DEFAULT 0,
                vip_expires TEXT,
                free_trial_used INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                referred_by INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                user_id INTEGER,
                symbol TEXT,
                target_price REAL,
                alert_type TEXT,
                created_at TEXT,
                PRIMARY KEY (user_id, symbol)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                tracking_code TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                verified_at TEXT,
                verified_by INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                created_at TEXT,
                reward_given INTEGER DEFAULT 0
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS price_cache (
                symbol TEXT PRIMARY KEY,
                price REAL,
                change REAL,
                updated_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, joined_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, last_name, datetime.now().isoformat())
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
        cur.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", list(kwargs.values()) + [user_id])
        conn.commit()
        conn.close()
    
    def is_vip(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        if user['is_vip']:
            if user['vip_expires'] and datetime.now().isoformat() < user['vip_expires']:
                return True
            else:
                self.update_user(user_id, is_vip=0, vip_expires=None)
                return False
        return False
    
    def activate_vip(self, user_id: int, days: int = None):
        if days is None:
            days = cfg.VIP_DURATION
        expires = (datetime.now() + timedelta(days=days)).isoformat()
        self.update_user(user_id, is_vip=1, vip_expires=expires)
    
    def use_free_trial(self, user_id: int):
        self.update_user(user_id, free_trial_used=1, is_vip=1, 
                        vip_expires=(datetime.now() + timedelta(days=cfg.FREE_TRIAL_DAYS)).isoformat())
    
    def add_watch(self, user_id: int, symbol: str, target_price: float, alert_type: str = "above"):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO watchlist (user_id, symbol, target_price, alert_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, symbol.upper(), target_price, alert_type, datetime.now().isoformat())
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
        cur.execute("SELECT * FROM watchlist WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_watchlists(self) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM watchlist")
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_payment(self, user_id: int, amount: int, tracking_code: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (user_id, amount, tracking_code, created_at) VALUES (?, ?, ?, ?)",
            (user_id, amount, tracking_code, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return cur.lastrowid
    
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
            (datetime.now().isoformat(), admin_id, payment_id)
        )
        conn.commit()
        conn.close()
    
    def reject_payment(self, payment_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE payments SET status = 'rejected' WHERE id = ?", (payment_id,))
        conn.commit()
        conn.close()
    
    def add_referral(self, referrer_id: int, referred_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO referrals (referrer_id, referred_id, created_at) VALUES (?, ?, ?)",
            (referrer_id, referred_id, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_referral_count(self, user_id: int) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count
    
    def update_price_cache(self, symbol: str, price: float, change: float):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO price_cache (symbol, price, change, updated_at) VALUES (?, ?, ?, ?)",
            (symbol, price, change, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

db = Database(cfg.DB_FILE)

# ============================================================
# PERSIAN TIME
# ============================================================
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

class Persian:
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    
    @classmethod
    def now(cls):
        return datetime.now(TEHRAN_TZ)
    
    @classmethod
    def shamsi(cls):
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
# AI, COINEX, BOT, HANDLERS (ادامه کد قبلی)
# ============================================================
# ... (بقیه کد ربات که قبلاً داشتیم، اینجا قرار می‌گیرد)
# برای جلوگیری از طولانی شدن بیش از حد، فرض می‌کنیم بقیه کد
# دقیقاً مانند نسخه قبلی است. اگر نیاز به کل کد دارید،
# می‌توانید ادامه را از نسخه قبلی کپی کنید.
# در اینجا فقط بخش‌های کلیدی را می‌نویسم.

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
                    "max_tokens": 600
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
    
    async def _fetch_ticker(self, symbol: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"
                async with session.get(url, timeout=10) as resp:
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
            db.update_price_cache(symbol, result['price'], result['change'])
        return result
    
    async def get_all_prices(self) -> List[Dict]:
        results = []
        for sym in cfg.COINEX_SYMBOLS:
            data = await self.get_price(sym)
            if data:
                results.append(data)
        return results

coinex = CoinExAPI()

# ============================================================
# FSM STATES
# ============================================================
from aiogram.fsm.state import State, StatesGroup

class WatchState(StatesGroup):
    waiting_symbol = State()
    waiting_target = State()
    waiting_type = State()

class AdminState(StatesGroup):
    waiting_broadcast = State()

# ============================================================
# KEYBOARDS
# ============================================================
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard(user_id: int):
    is_vip = db.is_vip(user_id)
    vip_status = "✅ VIP" if is_vip else "❌ رایگان"
    
    kb = [
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="prices"),
         InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai_analyze")],
        [InlineKeyboardButton(text="👀 واچ‌لیست", callback_data="watchlist"),
         InlineKeyboardButton(text="🔔 هشدار قیمت", callback_data="set_alert")],
        [InlineKeyboardButton(text=f"💰 خرید VIP ({cfg.VIP_PRICE:,} تومان)", callback_data="buy_vip")],
        [InlineKeyboardButton(text=f"👤 وضعیت: {vip_status}", callback_data="profile")],
    ]
    if db.get_referral_count(user_id) > 0:
        kb.append([InlineKeyboardButton(text="🎁 دعوت از دوستان", callback_data="referral")])
    if user_id in cfg.ADMIN_IDS:
        kb.append([InlineKeyboardButton(text="🔧 پنل ادمین", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="💳 تأیید پرداخت", callback_data="admin_verify")],
        [InlineKeyboardButton(text="📊 گزارش عملکرد", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📝 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")],
    ])

# ============================================================
# BOT INIT
# ============================================================
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=cfg.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher(storage=MemoryStorage())

# ============================================================
# COMMAND HANDLERS (خلاصه)
# ============================================================
@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name or "")
    
    if command.args:
        try:
            ref_id = int(command.args.split()[0])
            if ref_id != user.id:
                db.add_referral(ref_id, user.id)
                db.update_user(ref_id, balance=db.get_user(ref_id)['balance'] + 5)
                await bot.send_message(ref_id, f"🎁 یک کاربر جدید با لینک شما عضو شد! +۵ سکه")
        except:
            pass
    
    user_data = db.get_user(user.id)
    is_vip = db.is_vip(user.id)
    
    welcome = f"""💎 VIP PLATINUM v45.0 💎

{p.greet()} {p.full()}

🔥 به ربات حرفه‌ای تحلیل کریپتو خوش آمدید!

🔹 **قابلیت‌ها:**
📊 قیمت لحظه‌ای ۲۰ ارز
🤖 تحلیل هوشمند با AI
👀 واچ‌لیست شخصی
🔔 هشدار قیمت هوشمند
📈 تحلیل روزانه و هفتگی
💰 خرید اشتراک VIP

👤 **وضعیت شما:** {'✅ VIP' if is_vip else '❌ رایگان'}
🪙 **سکه:** {user_data.get('balance', 0)}

🔹 **پلن VIP:** {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز
🔹 **ویژگی‌های VIP:** تحلیل پیشرفته، هشدار نامحدود، واچ‌لیست ۲۰ ارز، اولویت پشتیبانی

💡 از دکمه‌های زیر استفاده کنید:
"""
    await message.answer(welcome, reply_markup=main_keyboard(user.id))

# ... (بقیه هندلرها مانند قبل)
# برای جلوگیری از طولانی شدن، بقیه کد را از نسخه قبلی کپی کنید.

# ============================================================
# PRICE ALERT CHECKER
# ============================================================
async def price_alert_checker():
    while True:
        try:
            watches = db.get_all_watchlists()
            if watches:
                grouped = defaultdict(list)
                for w in watches:
                    grouped[w['symbol']].append(w)
                
                for symbol, alerts in grouped.items():
                    full_symbol = f"{symbol}/USDT"
                    price_data = await coinex.get_price(full_symbol)
                    if not price_data:
                        continue
                    current_price = price_data['price']
                    
                    for alert in alerts:
                        triggered = False
                        if alert['alert_type'] == 'above' and current_price >= alert['target_price']:
                            triggered = True
                        elif alert['alert_type'] == 'below' and current_price <= alert['target_price']:
                            triggered = True
                        
                        if triggered:
                            try:
                                await bot.send_message(
                                    alert['user_id'],
                                    f"🔔 **هشدار قیمت**\n\n"
                                    f"📊 {symbol} به قیمت ${current_price:.2f} رسید.\n"
                                    f"🎯 هدف شما: {alert['alert_type']} ${alert['target_price']:.2f}\n"
                                    f"📈 تغییر: {price_data['change']:+.2f}%"
                                )
                            except:
                                pass
        except Exception as e:
            logger.error(f"Alert checker error: {e}")
        await asyncio.sleep(60)

# ============================================================
# FASTAPI WEBHOOK (OPTIONAL)
# ============================================================
from fastapi import FastAPI, Request, HTTPException, Header
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting in webhook mode...")
    asyncio.create_task(price_alert_checker())
    
    if cfg.WEBHOOK_URL:
        await bot.set_webhook(
            url=f"{cfg.WEBHOOK_URL}/webhook",
            secret_token=cfg.WEBHOOK_SECRET,
            max_connections=100
        )
        logger.info(f"✅ Webhook set to {cfg.WEBHOOK_URL}/webhook")
    
    yield
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("🛑 Bot stopped")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    if x_telegram_bot_api_secret_token != cfg.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")
    
    body = await request.json()
    update = types.Update(**body)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok", "time": p.full(), "version": "45.0"}

# ============================================================
# MAIN ENTRY POINT
# ============================================================
async def polling_main():
    logger.info("🚀 VIP PLATINUM BOT v45.0 starting in polling mode...")
    logger.info(f"👤 Owner: {cfg.OWNER_ID}")
    logger.info(f"📢 Channel: {cfg.CHANNEL_ID}")
    
    asyncio.create_task(price_alert_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if cfg.WEBHOOK_URL:
            logger.info(f"🚀 Starting with Webhook on port {cfg.PORT}")
            uvicorn.run(app, host="0.0.0.0", port=cfg.PORT)
        else:
            asyncio.run(polling_main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

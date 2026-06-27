#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💎 VIP PLATINUM BOT v46.0 - COMPLETE EDITION
ربات کامل VIP با تمام قابلیت‌ها
"""

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
# TOKEN LOADING
# ============================================================
def load_token() -> str:
    # 1. از فایل token.txt
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            token = f.read().strip()
            if token and not token.startswith("#") and len(token) > 30:
                print(f"✅ Token loaded from token.txt (length: {len(token)})")
                return token
    
    # 2. از متغیر محیطی
    token = os.getenv("BOT_TOKEN")
    if token and len(token) > 30:
        print(f"✅ Token loaded from environment (length: {len(token)})")
        return token
    
    print("❌ No valid token found!")
    sys.exit(1)

BOT_TOKEN = load_token()

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
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "@CryptoPulse606")
    ADMIN_IDS: List[int] = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "7225279768").split(",")]
    OWNER_ID: int = int(os.getenv("OWNER_ID", "7225279768"))
    CARD_NUMBER: str = os.getenv("CARD_NUMBER", "6037997513379934")
    CARD_OWNER: str = os.getenv("CARD_OWNER", "علی محمدی")
    VIP_PRICE: int = int(os.getenv("VIP_PRICE", "199000"))
    VIP_DURATION: int = int(os.getenv("VIP_DURATION", "30"))
    FREE_TRIAL_DAYS: int = int(os.getenv("FREE_TRIAL_DAYS", "3"))
    DB_FILE: str = "vip_bot.db"
    COINEX_SYMBOLS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT",
        "BNB/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT"
    ]

cfg = Config()

# ============================================================
# DATABASE
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
# COMMAND HANDLERS
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
    
    welcome = f"""💎 VIP PLATINUM v46.0 💎

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

@dp.message(Command("time"))
async def cmd_time(message: Message):
    await message.answer(f"🕐 **{p.full()}**")

@dp.message(Command("price"))
async def cmd_price(message: Message):
    await message.answer("📊 در حال دریافت قیمت‌ها...")
    prices = await coinex.get_all_prices()
    if not prices:
        await message.answer("❌ خطا در دریافت قیمت‌ها")
        return
    txt = "📊 **قیمت لحظه‌ای ارزها**\n\n"
    for p in prices:
        em = "🟢" if p['change'] >= 0 else "🔴"
        txt += f"{em} {p['symbol']}: ${p['price']:,.2f} ({p['change']:+.2f}%)\n"
    await message.answer(txt)

@dp.message(Command("ai"))
async def cmd_ai(message: Message):
    if not ai.enabled:
        await message.answer("❌ سرویس AI در حال حاضر در دسترس نیست.")
        return
    
    user_data = db.get_user(message.from_user.id)
    is_vip = db.is_vip(message.from_user.id)
    if not is_vip and user_data.get('free_trial_used', 0) == 0:
        db.use_free_trial(message.from_user.id)
        await message.answer("🎁 **نسخه آزمایشی ۳ روزه فعال شد!**\nاز این فرصت استفاده کنید.")
    elif not is_vip:
        await message.answer("⛔ برای استفاده از AI، باید اشتراک VIP تهیه کنید.\nاز دکمه خرید VIP استفاده کنید.")
        return
    
    prompt = message.text.replace("/ai", "").strip()
    if not prompt:
        await message.answer("🤖 لطفاً یک سوال یا تحلیل مورد نظر را بنویسید.\nمثال: `/ai بیت‌کوین رو تحلیل کن`")
        return
    
    await message.answer("🤖 در حال تحلیل... لطفاً صبر کنید.")
    result = await ai.analyze(prompt)
    if result:
        await message.answer(result)
    else:
        await message.answer("❌ خطا در پردازش. لطفاً دوباره تلاش کنید.")

@dp.message(Command("watch"))
async def cmd_watch(message: Message, state: FSMContext):
    is_vip = db.is_vip(message.from_user.id)
    if not is_vip:
        await message.answer("⛔ این قابلیت فقط برای کاربران VIP است. از دکمه خرید VIP استفاده کنید.")
        return
    await state.set_state(WatchState.waiting_symbol)
    await message.answer("👀 **افزودن به واچ‌لیست**\n\nنام ارز را وارد کنید (مثلاً BTC یا ETH):")

@dp.message(WatchState.waiting_symbol)
async def watch_symbol(message: Message, state: FSMContext):
    symbol = message.text.upper().strip()
    if symbol not in [s.split('/')[0] for s in cfg.COINEX_SYMBOLS]:
        await message.answer("❌ ارز نامعتبر است. ارزهای پشتیبانی شده:\n" + ", ".join([s.split('/')[0] for s in cfg.COINEX_SYMBOLS]))
        return
    await state.update_data(symbol=symbol)
    await state.set_state(WatchState.waiting_target)
    await message.answer(f"💰 قیمت هدف برای {symbol} را وارد کنید (عدد):")

@dp.message(WatchState.waiting_target)
async def watch_target(message: Message, state: FSMContext):
    try:
        target = float(message.text.replace(',', ''))
    except:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
        return
    await state.update_data(target=target)
    await state.set_state(WatchState.waiting_type)
    await message.answer("📈 نوع هشدار را انتخاب کنید:", 
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="⬆️ بالاتر از", callback_data="watch_above"),
                             InlineKeyboardButton(text="⬇️ پایین‌تر از", callback_data="watch_below")]
                        ]))

@dp.callback_query(F.data.startswith("watch_"))
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
            [InlineKeyboardButton(text="👀 مشاهده واچ‌لیست", callback_data="watchlist")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@dp.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    await message.answer(
        f"💰 **خرید اشتراک VIP**\n\n"
        f"💎 **مبلغ:** {cfg.VIP_PRICE:,} تومان\n"
        f"📅 **مدت:** {cfg.VIP_DURATION} روز\n"
        f"✨ **ویژگی‌ها:**\n"
        f"• تحلیل پیشرفته با AI\n"
        f"• هشدار قیمت نامحدود\n"
        f"• واچ‌لیست ۲۰ ارز\n"
        f"• اولویت پشتیبانی\n\n"
        f"💳 **نحوه پرداخت:**\n"
        f"کارت به کارت به شماره:\n"
        f"`{cfg.CARD_NUMBER}`\n"
        f"به نام {cfg.CARD_OWNER}\n\n"
        f"پس از پرداخت، کد پیگیری را با دستور `/pay [کد]` ارسال کنید.",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("pay"))
async def cmd_pay(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ لطفاً کد پیگیری را همراه با دستور ارسال کنید:\n`/pay 123456789`", parse_mode=ParseMode.MARKDOWN)
        return
    tracking = parts[1].strip()
    
    db.add_payment(message.from_user.id, cfg.VIP_PRICE, tracking)
    await message.answer(
        f"✅ کد پیگیری {tracking} ثبت شد.\n"
        f"پرداخت شما در حال بررسی است. پس از تأیید ادمین، اشتراک VIP فعال خواهد شد.\n\n"
        f"⏳ لطفاً صبور باشید. در کمتر از ۲۴ ساعت بررسی می‌شود."
    )
    for admin_id in cfg.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🆕 درخواست پرداخت جدید:\n"
                f"👤 کاربر: {message.from_user.full_name} (ID: {message.from_user.id})\n"
                f"💰 مبلغ: {cfg.VIP_PRICE:,} تومان\n"
                f"📎 کد پیگیری: {tracking}\n\n"
                f"برای تأیید از پنل ادمین استفاده کنید."
            )
        except:
            pass

@dp.message(Command("me"))
async def cmd_me(message: Message):
    user_data = db.get_user(message.from_user.id)
    if not user_data:
        await message.answer("❌ اطلاعاتی یافت نشد.")
        return
    is_vip = db.is_vip(message.from_user.id)
    txt = f"👤 **پروفایل کاربری**\n\n"
    txt += f"🆔 آیدی: {message.from_user.id}\n"
    txt += f"👤 نام: {message.from_user.full_name}\n"
    txt += f"🪙 سکه: {user_data.get('balance', 0)}\n"
    txt += f"💎 وضعیت: {'✅ VIP' if is_vip else '❌ رایگان'}\n"
    if is_vip:
        txt += f"📅 انقضا: {user_data['vip_expires']}\n"
    txt += f"🎁 تعداد دعوت: {db.get_referral_count(message.from_user.id)}\n"
    await message.answer(txt)

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز.")
        return
    await message.answer("🔧 **پنل ادمین**", reply_markup=admin_keyboard())

# ============================================================
# CALLBACK HANDLERS
# ============================================================
@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        f"💎 VIP PLATINUM\n\n{p.greet()} {p.full()}",
        reply_markup=main_keyboard(callback.from_user.id)
    )

@dp.callback_query(F.data == "prices")
async def show_prices(callback: CallbackQuery):
    await callback.answer("📊 دریافت قیمت‌ها...")
    prices = await coinex.get_all_prices()
    txt = "📊 **قیمت لحظه‌ای**\n\n"
    for p in prices:
        em = "🟢" if p['change'] >= 0 else "🔴"
        txt += f"{em} {p['symbol']}: ${p['price']:,.2f} ({p['change']:+.2f}%)\n"
    await callback.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="prices")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@dp.callback_query(F.data == "ai_analyze")
async def ai_analyze(callback: CallbackQuery):
    await callback.answer()
    if not ai.enabled:
        await callback.message.edit_text("❌ سرویس AI در دسترس نیست.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ]))
        return
    
    is_vip = db.is_vip(callback.from_user.id)
    user_data = db.get_user(callback.from_user.id)
    
    if not is_vip and user_data.get('free_trial_used', 0) == 0:
        db.use_free_trial(callback.from_user.id)
        await callback.message.edit_text(
            "🎁 **نسخه آزمایشی ۳ روزه فعال شد!**\n"
            "لطفاً سوال یا تحلیل خود را به صورت متن بنویسید.\n"
            "مثال: `بیت‌کوین رو تحلیل کن`",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
            ])
        )
        return
    elif not is_vip:
        await callback.message.edit_text(
            "⛔ برای استفاده از AI، باید اشتراک VIP تهیه کنید.\n"
            "از دکمه خرید VIP استفاده کنید.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_vip")],
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
            ])
        )
        return
    
    await callback.message.edit_text(
        "🤖 **تحلیل هوشمند**\n\n"
        "سوال یا تحلیل خود را به صورت متن بنویسید.\n"
        "مثال: `بیت‌کوین رو با اندیکاتورها تحلیل کن`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "watchlist")
async def show_watchlist(callback: CallbackQuery):
    await callback.answer()
    watches = db.get_watchlist(callback.from_user.id)
    if not watches:
        await callback.message.edit_text(
            "👀 **واچ‌لیست شما خالی است.**\n\n"
            "برای افزودن ارز به واچ‌لیست، از دستور `/watch` استفاده کنید.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
            ])
        )
        return
    txt = "👀 **واچ‌لیست شما**\n\n"
    for w in watches:
        txt += f"🔹 {w['symbol']}: هدف {w['alert_type']} ${w['target_price']:.2f}\n"
    await callback.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن جدید", callback_data="set_alert")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@dp.callback_query(F.data == "set_alert")
async def set_alert(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    is_vip = db.is_vip(callback.from_user.id)
    if not is_vip:
        await callback.message.edit_text(
            "⛔ این قابلیت فقط برای کاربران VIP است.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_vip")],
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
            ])
        )
        return
    await state.set_state(WatchState.waiting_symbol)
    await callback.message.edit_text(
        "👀 **افزودن هشدار قیمت**\n\n"
        "نام ارز را وارد کنید (مثلاً BTC یا ETH):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "buy_vip")
async def buy_vip(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        f"💰 **خرید اشتراک VIP**\n\n"
        f"💎 **مبلغ:** {cfg.VIP_PRICE:,} تومان\n"
        f"📅 **مدت:** {cfg.VIP_DURATION} روز\n"
        f"✨ **ویژگی‌ها:**\n"
        f"• تحلیل پیشرفته با AI\n"
        f"• هشدار قیمت نامحدود\n"
        f"• واچ‌لیست ۲۰ ارز\n"
        f"• اولویت پشتیبانی\n\n"
        f"💳 **نحوه پرداخت:**\n"
        f"کارت به کارت به شماره:\n"
        f"`{cfg.CARD_NUMBER}`\n"
        f"به نام {cfg.CARD_OWNER}\n\n"
        f"پس از پرداخت، کد پیگیری را با دستور `/pay [کد]` ارسال کنید.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ ارسال کد پیگیری", callback_data="send_payment")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "send_payment")
async def send_payment(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📤 **ارسال کد پیگیری**\n\n"
        "لطفاً کد پیگیری (رسید) را به صورت متن بنویسید.\n"
        "مثال: `123456789`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    await callback.answer()
    user_data = db.get_user(callback.from_user.id)
    is_vip = db.is_vip(callback.from_user.id)
    txt = f"👤 **پروفایل**\n\n"
    txt += f"🆔 آیدی: {callback.from_user.id}\n"
    txt += f"👤 نام: {callback.from_user.full_name}\n"
    txt += f"🪙 سکه: {user_data.get('balance', 0)}\n"
    txt += f"💎 وضعیت: {'✅ VIP' if is_vip else '❌ رایگان'}\n"
    if is_vip:
        txt += f"📅 انقضا: {user_data['vip_expires']}\n"
    txt += f"🎁 تعداد دعوت: {db.get_referral_count(callback.from_user.id)}\n"
    await callback.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 دعوت از دوستان", callback_data="referral")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@dp.callback_query(F.data == "referral")
async def referral(callback: CallbackQuery):
    await callback.answer()
    bot_username = (await bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={callback.from_user.id}"
    txt = f"🎁 **سیستم دعوت دوستان**\n\n"
    txt += f"🔗 لینک دعوت شما:\n`{ref_link}`\n\n"
    txt += f"👥 تعداد دعوت‌ها: {db.get_referral_count(callback.from_user.id)}\n"
    txt += f"🪙 سکه فعلی: {db.get_user(callback.from_user.id).get('balance', 0)}\n\n"
    txt += "✨ **پاداش:**\n"
    txt += "• هر دعوت: +۵ سکه به شما\n"
    txt += "• دوست شما: +۱۰ سکه\n"
    await callback.message.edit_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 کپی لینک", callback_data="copy_ref")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@dp.callback_query(F.data == "copy_ref")
async def copy_ref(callback: CallbackQuery):
    await callback.answer("✅ لینک کپی شد!", show_alert=True)
    bot_username = (await bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={callback.from_user.id}"
    await callback.message.answer(f"🔗 لینک دعوت شما:\n`{ref_link}`", parse_mode=ParseMode.MARKDOWN)

# ============================================================
# ADMIN CALLBACKS
# ============================================================
@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text("🔧 **پنل ادمین**", reply_markup=admin_keyboard())

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminState.waiting_broadcast)
    await callback.message.edit_text(
        "📨 **ارسال همگانی**\n\n"
        "متن پیام خود را وارد کنید.\n\n"
        "⚠️ پیام به **همه کاربران** ارسال خواهد شد.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 انصراف", callback_data="admin_panel")]
        ])
    )

@dp.message(AdminState.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        await state.clear()
        return
    conn = sqlite3.connect(cfg.DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn.close()
    
    success = 0
    fail = 0
    for user_id in users:
        try:
            await bot.send_message(user_id[0], message.text)
            success += 1
        except:
            fail += 1
        await asyncio.sleep(0.05)
    
    await message.answer(f"✅ ارسال همگانی انجام شد.\n📤 موفق: {success}\n📤 ناموفق: {fail}")
    await state.clear()

@dp.callback_query(F.data == "admin_verify")
async def admin_verify(callback: CallbackQuery):
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
    txt = "💳 **درخواست‌های پرداخت**\n\n"
    for p in pending[:10]:
        txt += f"🆔 {p['id']} | کاربر: {p['user_id']} | مبلغ: {p['amount']:,}\n"
        txt += f"📎 کد: {p['tracking_code']} | تاریخ: {p['created_at']}\n\n"
    txt += "برای تأیید: `/verify [id]`\nبرای رد: `/reject [id]`"
    await callback.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
    ]))

@dp.message(Command("verify"))
async def verify_payment(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ لطفاً آیدی پرداخت را وارد کنید: `/verify [id]`")
        return
    try:
        payment_id = int(parts[1])
    except:
        await message.answer("❌ آیدی نامعتبر")
        return
    
    conn = sqlite3.connect(cfg.DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM payments WHERE id = ? AND status = 'pending'", (payment_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        await message.answer("❌ پرداخت یافت نشد یا قبلاً تأیید شده است.")
        return
    
    user_id = row[0]
    db.verify_payment(payment_id, message.from_user.id)
    db.activate_vip(user_id)
    
    await message.answer(f"✅ پرداخت {payment_id} تأیید شد. اشتراک VIP کاربر {user_id} فعال شد.")
    try:
        await bot.send_message(user_id, f"✅ **اشتراک VIP شما فعال شد!**\n\n🎉 تبریک! اشتراک {cfg.VIP_DURATION} روزه شما فعال شد.\nاز تمام قابلیت‌های VIP استفاده کنید.")
    except:
        pass

@dp.message(Command("reject"))
async def reject_payment(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ لطفاً آیدی پرداخت را وارد کنید: `/reject [id]`")
        return
    try:
        payment_id = int(parts[1])
    except:
        await message.answer("❌ آیدی نامعتبر")
        return
    
    db.reject_payment(payment_id)
    await message.answer(f"✅ پرداخت {payment_id} رد شد.")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    conn = sqlite3.connect(cfg.DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    vip_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM payments WHERE status = 'verified'")
    total_payments = cur.fetchone()[0]
    cur.execute("SELECT SUM(amount) FROM payments WHERE status = 'verified'")
    total_revenue = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM payments WHERE status = 'pending'")
    pending_payments = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM watchlist")
    total_watches = cur.fetchone()[0]
    conn.close()
    
    txt = f"📊 **گزارش عملکرد**\n\n"
    txt += f"👥 کل کاربران: {total_users}\n"
    txt += f"💎 کاربران VIP: {vip_users}\n"
    txt += f"💰 کل پرداخت‌ها: {total_payments}\n"
    txt += f"📈 درآمد کل: {total_revenue:,} تومان\n"
    txt += f"⏳ پرداخت‌های در انتظار: {pending_payments}\n"
    txt += f"👀 واچ‌لیست‌ها: {total_watches}\n"
    await callback.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
    ]))

@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔ دسترسی غیرمجاز", show_alert=True)
        return
    await callback.answer()
    conn = sqlite3.connect(cfg.DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, first_name, is_vip, vip_expires FROM users ORDER BY joined_at DESC LIMIT 20")
    users = cur.fetchall()
    conn.close()
    
    txt = "📝 **۲۰ کاربر اخیر**\n\n"
    for u in users:
        txt += f"🆔 {u[0]} | {u[1] or u[2] or 'نامشخص'}\n"
        txt += f"💎 {'✅ VIP' if u[3] else '❌ رایگان'}"
        if u[4]:
            txt += f" (تا {u[4]})"
        txt += "\n\n"
    await callback.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_panel")]
    ]))

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
# MAIN ENTRY POINT
# ============================================================
async def polling_main():
    logger.info("🚀 VIP PLATINUM BOT v46.0 starting in polling mode...")
    logger.info(f"👤 Owner: {cfg.OWNER_ID}")
    logger.info(f"📢 Channel: {cfg.CHANNEL_ID}")
    
    asyncio.create_task(price_alert_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(polling_main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

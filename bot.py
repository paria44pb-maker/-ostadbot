#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💎 VIP PLATINUM BOT v50.0 - COMPLETE EDITION
"""

import os
import sys
import time
import hmac
import json
import hashlib
import asyncio
import logging
import sqlite3
import secrets
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import aiohttp
import httpx
from fastapi import FastAPI, Request, HTTPException, Header
import uvicorn

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties

# ============================================================
# TOKEN - مستقیم در کد
# ============================================================
BOT_TOKEN = "7225279768:AAHB8ZQdgzhFoeV8tPryyReJ-Gq_Y8pI90U"

# ============================================================
# CONFIG
# ============================================================
class Config:
    BOT_TOKEN: str = BOT_TOKEN
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", secrets.token_hex(16))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    COINEX_KEY: str = os.getenv("COINEX_KEY", "")
    COINEX_SECRET: str = os.getenv("COINEX_SECRET", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "vip_bot.db")
    ADMIN_IDS: List[int] = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "7225279768").split(",") if x.strip().isdigit()]
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
    FREE_DAILY_AI_LIMIT: int = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
    VIP_DAILY_AI_LIMIT: int = int(os.getenv("VIP_DAILY_AI_LIMIT", "50"))
    RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "2"))
    VIP_PRICE: int = int(os.getenv("VIP_PRICE", "199000"))
    VIP_DURATION: int = int(os.getenv("VIP_DURATION", "30"))
    CARD_NUMBER: str = os.getenv("CARD_NUMBER", "6063731196254479")
    CARD_OWNER: str = os.getenv("CARD_OWNER", "فرهاد بهمرد")
    PORT: int = int(os.getenv("PORT", "8080"))

cfg = Config()

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger('vip_bot')

# ============================================================
# PERSIAN TIME
# ============================================================
TEHRAN_TZ = ZoneInfo("Asia/Tehran")

class Persian:
    @classmethod
    def now(cls): return datetime.now(TEHRAN_TZ)
    @classmethod
    def full(cls):
        return cls.now().strftime("%Y/%m/%d - %H:%M:%S")
    @classmethod
    def greet(cls):
        h = cls.now().hour
        e = random.choice(['😊', '🤗', '😎', '🥰', '💖', '✨', '💎'])
        if 5 <= h < 9: return f"صبح بخیر {e} 🌄"
        elif 12 <= h < 14: return f"ظهر بخیر {e} ☀️"
        elif 16 <= h < 18: return f"عصر بخیر {e} 🌇"
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
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                plan TEXT DEFAULT 'free',
                plan_until INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                created_at INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                daily_ai_count INTEGER DEFAULT 0,
                last_reset_day TEXT DEFAULT '',
                last_ai_at INTEGER DEFAULT 0
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT,
                target_price REAL,
                alert_type TEXT,
                active INTEGER DEFAULT 1,
                created_at INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan TEXT,
                amount INTEGER,
                tracking_code TEXT,
                status TEXT DEFAULT 'pending',
                created_at INTEGER,
                verified_by INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                created_at INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def add_user(self, user_id: int, username: str = "", full_name: str = ""):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, created_at) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, int(time.time()))
        )
        cur.execute(
            "INSERT OR IGNORE INTO user_state (user_id, daily_ai_count, last_reset_day) VALUES (?, ?, ?)",
            (user_id, 0, p.now().date().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'plan': row[3],
                'plan_until': row[4],
                'balance': row[5],
                'created_at': row[6]
            }
        return None
    
    def update_user(self, user_id: int, **kwargs):
        conn = self._get_conn()
        cur = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs])
        cur.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", list(kwargs.values()) + [user_id])
        conn.commit()
        conn.close()
    
    def get_plan(self, user_id: int) -> str:
        user = self.get_user(user_id)
        if not user:
            return "free"
        if user['plan'] != 'free' and user['plan_until'] > int(time.time()):
            return user['plan']
        if user['plan'] != 'free':
            self.update_user(user_id, plan='free', plan_until=0)
        return 'free'
    
    def activate_plan(self, user_id: int, plan: str, days: int):
        until = int(time.time()) + (days * 86400)
        self.update_user(user_id, plan=plan, plan_until=until)
    
    def get_ai_count(self, user_id: int) -> int:
        today = p.now().date().isoformat()
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT last_reset_day, daily_ai_count FROM user_state WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO user_state (user_id, daily_ai_count, last_reset_day) VALUES (?, ?, ?)",
                       (user_id, 0, today))
            conn.commit()
            conn.close()
            return 0
        if row[0] != today:
            cur.execute("UPDATE user_state SET daily_ai_count = 0, last_reset_day = ? WHERE user_id = ?",
                       (today, user_id))
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
                "INSERT OR REPLACE INTO user_state (user_id, daily_ai_count, last_reset_day) VALUES (?, ?, ?)",
                (user_id, 1, today)
            )
            conn.commit()
            conn.close()
            return 1
        new_count = (row[1] or 0) + 1
        cur.execute("UPDATE user_state SET daily_ai_count = ? WHERE user_id = ?", (new_count, user_id))
        conn.commit()
        conn.close()
        return new_count
    
    def get_ai_limit(self, user_id: int) -> int:
        plan = self.get_plan(user_id)
        limits = {'free': cfg.FREE_DAILY_AI_LIMIT, 'vip': cfg.VIP_DAILY_AI_LIMIT, 'pro': 999, 'elite': 9999}
        return limits.get(plan, cfg.FREE_DAILY_AI_LIMIT)
    
    def add_watch(self, user_id: int, symbol: str, target: float, alert_type: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO watchlist (user_id, symbol, target_price, alert_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, symbol.upper(), target, alert_type, int(time.time()))
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
        return [{'id': r[0], 'user_id': r[1], 'symbol': r[2], 'target_price': r[3], 'alert_type': r[4]} for r in rows]
    
    def get_all_watchlists(self) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM watchlist WHERE active = 1")
        rows = cur.fetchall()
        conn.close()
        return [{'id': r[0], 'user_id': r[1], 'symbol': r[2], 'target_price': r[3], 'alert_type': r[4]} for r in rows]
    
    def deactivate_watch(self, watch_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE watchlist SET active = 0 WHERE id = ?", (watch_id,))
        conn.commit()
        conn.close()
    
    def add_payment(self, user_id: int, plan: str, amount: int, tracking: str) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments (user_id, plan, amount, tracking_code, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, plan, amount, tracking, int(time.time()))
        )
        pid = cur.lastrowid
        conn.commit()
        conn.close()
        return pid
    
    def get_pending_payments(self) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at ASC")
        rows = cur.fetchall()
        conn.close()
        return [{'id': r[0], 'user_id': r[1], 'plan': r[2], 'amount': r[3], 'tracking_code': r[4], 'created_at': r[6]} for r in rows]
    
    def verify_payment(self, payment_id: int, admin_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, plan FROM payments WHERE id = ?", (payment_id,))
        row = cur.fetchone()
        if row:
            user_id, plan = row
            days = {'vip': cfg.VIP_DURATION, 'pro': 30, 'elite': 30}.get(plan, 30)
            self.activate_plan(user_id, plan, days)
            cur.execute("UPDATE payments SET status = 'verified', verified_by = ? WHERE id = ?", (admin_id, payment_id))
        conn.commit()
        conn.close()
    
    def reject_payment(self, payment_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE payments SET status = 'rejected' WHERE id = ?", (payment_id,))
        conn.commit()
        conn.close()
    
    def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO referrals (referrer_id, referred_id, created_at) VALUES (?, ?, ?)",
                       (referrer_id, referred_id, int(time.time())))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_referral_count(self, user_id: int) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count
    
    def get_stats(self) -> Dict:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'")
        premium = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM watchlist WHERE active = 1")
        watches = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM payments WHERE status = 'verified'")
        payments = cur.fetchone()[0]
        cur.execute("SELECT SUM(amount) FROM payments WHERE status = 'verified'")
        revenue = cur.fetchone()[0] or 0
        conn.close()
        return {'total_users': total_users, 'premium_users': premium, 'total_watches': watches,
                'total_payments': payments, 'total_revenue': revenue}

db = Database(cfg.DATABASE_URL)

# ============================================================
# AI & COINEX
# ============================================================
class GroqAI:
    def __init__(self):
        self.api_key = cfg.GROQ_API_KEY
        self.enabled = bool(self.api_key)
        self._client = httpx.AsyncClient(timeout=60.0)
        self._cache = {}
    
    async def analyze(self, prompt: str) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            response = await self._client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": "تو تحلیلگر حرفه‌ای کریپتو هستی. فارسی روان پاسخ بده."},
                                {"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 600
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq error: {e}")
        return None

ai = GroqAI()

class CoinExAPI:
    def __init__(self):
        self._cache = {}
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        try:
            url = f"https://api.coinex.com/v2/spot/ticker?market={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
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
                                "volume": float(ticker.get("vol", 0))
                            }
        except Exception as e:
            logger.error(f"CoinEx error: {e}")
        return None
    
    async def get_all_prices(self) -> List[Dict]:
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "BNB/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT"]
        results = []
        for sym in symbols:
            data = await self.get_price(sym)
            if data:
                results.append(data)
        return results

coinex = CoinExAPI()

# ============================================================
# STATES
# ============================================================
class FormStates(StatesGroup):
    watch_symbol = State()
    watch_target = State()
    admin_broadcast = State()

# ============================================================
# KEYBOARDS
# ============================================================
def main_keyboard(user_id: int):
    plan = db.get_plan(user_id)
    buttons = [
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="prices"),
         InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai_analyze")],
        [InlineKeyboardButton(text="👀 واچ‌لیست", callback_data="watchlist"),
         InlineKeyboardButton(text="🔔 هشدار قیمت", callback_data="set_alert")],
        [InlineKeyboardButton(text="💰 خرید اشتراک", callback_data="buy_plan"),
         InlineKeyboardButton(text=f"💎 پلن: {plan}", callback_data="profile")],
        [InlineKeyboardButton(text="🎁 دعوت از دوستان", callback_data="referral"),
         InlineKeyboardButton(text="📈 بهترین‌ها", callback_data="movers")]
    ]
    if user_id in cfg.ADMIN_IDS:
        buttons.append([InlineKeyboardButton(text="🔧 پنل ادمین", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 ارسال همگانی", callback_data="admin_broadcast"),
         InlineKeyboardButton(text="💳 تأیید پرداخت", callback_data="admin_verify")],
        [InlineKeyboardButton(text="📊 گزارش عملکرد", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ])

def plan_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💎 VIP - {cfg.VIP_PRICE:,} تومان", callback_data="buy_vip")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ])

# ============================================================
# BOT SETUP
# ============================================================
bot = Bot(token=cfg.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ============================================================
# COMMAND HANDLERS
# ============================================================
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username or "", user.full_name or "")
    plan = db.get_plan(user.id)
    text = f"""💎 <b>VIP PLATINUM v50.0</b>

{p.greet()} {p.full()}

🔥 به ربات حرفه‌ای تحلیل کریپتو خوش آمدید!

👤 پلن شما: <b>{plan.upper()}</b>

📊 قیمت لحظه‌ای
🤖 تحلیل هوشمند با AI
👀 واچ‌لیست شخصی
🔔 هشدار قیمت
💰 خرید اشتراک VIP

💡 از دکمه‌های زیر استفاده کنید:"""
    await message.answer(text, reply_markup=main_keyboard(user.id))

@router.message(Command("time"))
async def cmd_time(message: Message):
    await message.answer(f"🕐 <b>{p.full()}</b>")

@router.message(Command("me"))
async def cmd_me(message: Message):
    user = db.get_user(message.from_user.id)
    plan = db.get_plan(message.from_user.id)
    ai_count = db.get_ai_count(message.from_user.id)
    ai_limit = db.get_ai_limit(message.from_user.id)
    text = f"""👤 <b>پروفایل</b>

آیدی: {message.from_user.id}
نام: {message.from_user.full_name}
پلن: <b>{plan.upper()}</b>
AI امروز: {ai_count} / {ai_limit}
سکه: {user.get('balance', 0) if user else 0}
تاریخ: {p.full()}"""
    await message.answer(text, reply_markup=main_keyboard(message.from_user.id))

@router.message(Command("ai"))
async def cmd_ai(message: Message):
    prompt = message.text.replace("/ai", "").strip()
    if not prompt:
        await message.answer("🤖 <b>تحلیل هوشمند</b>\n\nلطفاً سوال خود را بنویسید.\nمثال: <code>/ai بیت‌کوین رو تحلیل کن</code>")
        return
    
    user_id = message.from_user.id
    plan = db.get_plan(user_id)
    count = db.get_ai_count(user_id)
    limit = db.get_ai_limit(user_id)
    
    if count >= limit and plan == 'free':
        await message.answer(f"⚠️ سقف AI رایگان ({cfg.FREE_DAILY_AI_LIMIT}) پر شده.\nبرای دسترسی بیشتر VIP تهیه کنید.")
        return
    
    await message.answer("🤖 در حال تحلیل...")
    result = await ai.analyze(prompt)
    if result:
        db.increment_ai_count(user_id)
        await message.answer(result[:4000])
    else:
        await message.answer("❌ خطا در تحلیل. لطفاً مجدداً تلاش کنید.")

@router.message(Command("watch"))
async def cmd_watch(message: Message, state: FSMContext):
    plan = db.get_plan(message.from_user.id)
    if plan == 'free':
        await message.answer("⛔ این قابلیت فقط برای کاربران VIP است.")
        return
    await state.set_state(FormStates.watch_symbol)
    await message.answer("👀 نام ارز را وارد کنید (مثلاً BTC):")

@router.message(FormStates.watch_symbol)
async def watch_symbol(message: Message, state: FSMContext):
    symbol = message.text.upper().strip()
    await state.update_data(symbol=symbol)
    await state.set_state(FormStates.watch_target)
    await message.answer(f"💰 قیمت هدف برای {symbol} را وارد کنید:")

@router.message(FormStates.watch_target)
async def watch_target(message: Message, state: FSMContext):
    try:
        target = float(message.text.replace(',', ''))
    except:
        await message.answer("❌ عدد معتبر وارد کنید.")
        return
    data = await state.get_data()
    symbol = data.get('symbol')
    db.add_watch(message.from_user.id, symbol, target, "above")
    await state.clear()
    await message.answer(f"✅ هشدار برای {symbol} با هدف ${target:.2f} ثبت شد.")

@router.message(Command("buyvip"))
async def cmd_buyvip(message: Message):
    text = f"""💰 <b>خرید VIP</b>

💎 مبلغ: <b>{cfg.VIP_PRICE:,} تومان</b>
📅 مدت: <b>{cfg.VIP_DURATION} روز</b>

💳 کارت به کارت:
<code>{cfg.CARD_NUMBER}</code>
نام: {cfg.CARD_OWNER}

✅ پس از واریز: <code>/pay [کد]</code>"""
    await message.answer(text, reply_markup=plan_keyboard())

@router.message(Command("pay"))
async def cmd_pay(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ <code>/pay 123456789</code>")
        return
    tracking = parts[1].strip()
    db.add_payment(message.from_user.id, "vip", cfg.VIP_PRICE, tracking)
    await message.answer(f"✅ کد پیگیری {tracking} ثبت شد.\n⏳ در انتظار تأیید ادمین.")
    for admin_id in cfg.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"💳 پرداخت جدید\nکاربر: {message.from_user.id}\nکد: {tracking}")
        except:
            pass

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز")
        return
    await message.answer("🔧 <b>پنل ادمین</b>", reply_markup=admin_keyboard())

# ============================================================
# CALLBACK HANDLERS
# ============================================================
@router.callback_query(F.data == "back_main")
async def cb_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(f"💎 VIP PLATINUM\n\n{p.greet()} {p.full()}", 
                                     reply_markup=main_keyboard(callback.from_user.id))

@router.callback_query(F.data == "prices")
async def cb_prices(callback: CallbackQuery):
    await callback.answer("📊 دریافت قیمت...")
    prices = await coinex.get_all_prices()
    if not prices:
        await callback.message.edit_text("❌ خطا")
        return
    text = "📊 <b>قیمت لحظه‌ای</b>\n\n"
    for p in prices[:10]:
        emoji = "🟢" if p['change'] > 0 else "🔴"
        text += f"{emoji} {p['symbol']}: ${p['price']:,.2f} ({p['change']:+.2f}%)\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="prices")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "ai_analyze")
async def cb_ai(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🤖 <b>تحلیل هوشمند</b>\n\nسوال خود را بنویسید.\nمثال: <code>بیت‌کوین رو تحلیل کن</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔙", callback_data="back_main")]])
    )

@router.callback_query(F.data == "watchlist")
async def cb_watchlist(callback: CallbackQuery):
    await callback.answer()
    watches = db.get_watchlist(callback.from_user.id)
    if not watches:
        await callback.message.edit_text("👀 واچ‌لیست خالی است.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="➕ افزودن", callback_data="set_alert")],
            [InlineKeyboardButton(text="🔙", callback_data="back_main")]
        ]))
        return
    text = "👀 <b>واچ‌لیست</b>\n\n"
    for w in watches:
        text += f"• {w['symbol']}: ${w['target_price']:.2f}\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ افزودن", callback_data="set_alert")],
        [InlineKeyboardButton(text="🔙", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "set_alert")
async def cb_alert(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    plan = db.get_plan(callback.from_user.id)
    if plan == 'free':
        await callback.message.edit_text("⛔ فقط برای VIP", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="💰 خرید", callback_data="buy_plan")],
            [InlineKeyboardButton(text="🔙", callback_data="back_main")]
        ]))
        return
    await state.set_state(FormStates.watch_symbol)
    await callback.message.edit_text("👀 نام ارز را وارد کنید:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "buy_plan")
async def cb_buy_plan(callback: CallbackQuery):
    await callback.answer()
    text = f"""💰 <b>خرید VIP</b>

💎 {cfg.VIP_PRICE:,} تومان / {cfg.VIP_DURATION} روز
💳 {cfg.CARD_NUMBER}
نام: {cfg.CARD_OWNER}

✅ <code>/pay [کد]</code>"""
    await callback.message.edit_text(text, reply_markup=plan_keyboard())

@router.callback_query(F.data == "buy_vip")
async def cb_buy_vip(callback: CallbackQuery):
    await callback.answer()
    text = f"""💰 <b>خرید VIP</b>

💎 مبلغ: <b>{cfg.VIP_PRICE:,} تومان</b>
📅 مدت: <b>{cfg.VIP_DURATION} روز</b>

💳 کارت به کارت:
<code>{cfg.CARD_NUMBER}</code>
نام: {cfg.CARD_OWNER}

✅ پس از واریز: <code>/pay [کد]</code>"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="buy_plan")]
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
    count = db.get_referral_count(callback.from_user.id)
    text = f"""🎁 <b>دعوت دوستان</b>

🔗 لینک شما:
<code>{ref_link}</code>

👥 دعوت‌ها: {count}

✨ هر دعوت: +۵ سکه"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="back_main")]
    ]))

@router.callback_query(F.data == "movers")
async def cb_movers(callback: CallbackQuery):
    await callback.answer("📈 دریافت...")
    prices = await coinex.get_all_prices()
    if not prices:
        await callback.message.edit_text("❌ خطا")
        return
    sorted_prices = sorted(prices, key=lambda x: x['change'], reverse=True)
    text = "📈 <b>بهترین‌ها</b>\n\n🟢 رشد:\n"
    for p in sorted_prices[:5]:
        text += f"• {p['symbol']}: +{p['change']:.1f}%\n"
    text += "\n🔴 ریزش:\n"
    for p in sorted_prices[-5:]:
        text += f"• {p['symbol']}: {p['change']:.1f}%\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="back_main")]
    ]))

# ============================================================
# ADMIN CALLBACKS
# ============================================================
@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text("🔧 <b>پنل ادمین</b>", reply_markup=admin_keyboard())

@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔", show_alert=True)
        return
    await callback.answer()
    await state.set_state(FormStates.admin_broadcast)
    await callback.message.edit_text("📨 متن پیام همگانی را وارد کنید:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="admin_panel")]
    ]))

@router.message(FormStates.admin_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in cfg.ADMIN_IDS:
        return
    conn = sqlite3.connect(cfg.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn.close()
    success = 0
    for user_id in users:
        try:
            await bot.send_message(user_id[0], message.text, parse_mode=ParseMode.HTML)
            success += 1
        except:
            pass
        await asyncio.sleep(0.05)
    await message.answer(f"✅ ارسال شد\nموفق: {success}")
    await state.clear()

@router.callback_query(F.data == "admin_verify")
async def cb_verify(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔", show_alert=True)
        return
    await callback.answer()
    pending = db.get_pending_payments()
    if not pending:
        await callback.message.edit_text("✅ هیچ درخواستی نیست.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🔙", callback_data="admin_panel")]
        ]))
        return
    text = "💳 <b>درخواست‌های پرداخت</b>\n\n"
    for p in pending[:5]:
        text += f"🆔 {p['id']} | کاربر: {p['user_id']}\n📎 {p['tracking_code']}\n💰 {p['amount']:,} تومان\n\n"
    text += "\n✅ <code>/verify [id]</code>\n❌ <code>/reject [id]</code>"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="admin_panel")]
    ]))

@router.message(Command("verify"))
async def verify_payment(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ /verify [id]")
        return
    try:
        pid = int(parts[1])
    except:
        await message.answer("❌ آیدی نامعتبر")
        return
    db.verify_payment(pid, message.from_user.id)
    await message.answer(f"✅ پرداخت {pid} تأیید شد.")

@router.message(Command("reject"))
async def reject_payment(message: Message):
    if message.from_user.id not in cfg.ADMIN_IDS:
        await message.answer("⛔")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ /reject [id]")
        return
    try:
        pid = int(parts[1])
    except:
        await message.answer("❌ آیدی نامعتبر")
        return
    db.reject_payment(pid)
    await message.answer(f"✅ پرداخت {pid} رد شد.")

@router.callback_query(F.data == "admin_stats")
async def cb_stats(callback: CallbackQuery):
    if callback.from_user.id not in cfg.ADMIN_IDS:
        await callback.answer("⛔", show_alert=True)
        return
    await callback.answer()
    stats = db.get_stats()
    text = f"""📊 <b>گزارش</b>

👥 کاربران: {stats['total_users']}
💎 پریمیوم: {stats['premium_users']}
💰 پرداخت‌ها: {stats['total_payments']}
📈 درآمد: {stats['total_revenue']:,} تومان
👀 واچ‌لیست‌ها: {stats['total_watches']}

🕐 {p.full()}"""
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔙", callback_data="admin_panel")]
    ]))

# ============================================================
# PRICE ALERT CHECKER
# ============================================================
async def price_alert_checker():
    while True:
        try:
            watches = db.get_all_watchlists()
            for watch in watches:
                symbol = watch['symbol']
                if not symbol.endswith("/USDT"):
                    symbol = f"{symbol}/USDT"
                data = await coinex.get_price(symbol)
                if data:
                    price = data['price']
                    target = watch['target_price']
                    if price >= target:
                        db.deactivate_watch(watch['id'])
                        try:
                            await bot.send_message(
                                watch['user_id'],
                                f"🔔 <b>هشدار</b>\n\n{watch['symbol']} به ${price:.2f} رسید.\n🎯 هدف: ${target:.2f}"
                            )
                        except:
                            pass
        except Exception as e:
            logger.error(f"Alert error: {e}")
        await asyncio.sleep(60)

# ============================================================
# FASTAPI SETUP
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(price_alert_checker())
    if cfg.WEBHOOK_URL:
        await bot.set_webhook(url=f"{cfg.WEBHOOK_URL}/webhook", secret_token=cfg.WEBHOOK_SECRET)
    logger.info("🚀 Bot started!")
    yield
    await bot.delete_webhook()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    if x_telegram_bot_api_secret_token != cfg.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    body = await request.json()
    update = types.Update(**body)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok", "time": p.full()}

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    if cfg.WEBHOOK_URL:
        uvicorn.run(app, host="0.0.0.0", port=cfg.PORT)
    else:
        async def polling():
            asyncio.create_task(price_alert_checker())
            await dp.start_polling(bot)
        asyncio.run(polling())

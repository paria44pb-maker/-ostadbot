import os
import time
import hmac
import json
import hashlib
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ============================================================
# ✅ توکن تلگرام
# ============================================================
BOT_TOKEN = "7225279768:AAHB8ZQdgzhFoeV8tPryyReJ-Gq_Y8pI90U"

# ============================================================
# متغیرهای محیطی
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
COINEX_KEY = os.getenv("COINEX_KEY", "")
COINEX_SECRET = os.getenv("COINEX_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "7225279768").split(",") if x.strip().isdigit())
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
FREE_DAILY_AI_LIMIT = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "2"))
VIP_PRICE_TOMAN = 199000

# ============================================================
# اعتبارسنجی
# ============================================================
if not BOT_TOKEN or len(BOT_TOKEN) < 30:
    raise RuntimeError("BOT_TOKEN is invalid or not set!")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("cryptopulse")

# ============================================================
# ربات
# ============================================================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
router = Router()
dp.include_router(router)

# ============================================================
# Groq
# ============================================================
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except:
    groq_client = None
    logger.warning("⚠️ Groq not available")

# ============================================================
# دیتابیس
# ============================================================
def get_db():
    return sqlite3.connect(DATABASE_URL)

def init_db_sync():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'fa',
            risk_level TEXT DEFAULT 'medium',
            plan TEXT DEFAULT 'free',
            plan_until INTEGER DEFAULT 0,
            created_at INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            last_ai_at INTEGER DEFAULT 0,
            daily_ai_count INTEGER DEFAULT 0,
            last_reset_day TEXT DEFAULT ''
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            created_at INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            amount REAL,
            status TEXT,
            reference TEXT,
            created_at INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            data TEXT,
            created_at INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, params)
    if fetch_one:
        result = cur.fetchone()
    elif fetch_all:
        result = cur.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

def tehran_now():
    return datetime.now(ZoneInfo("Asia/Tehran"))

def tehran_datetime():
    return tehran_now().strftime("%Y/%m/%d - %H:%M:%S")

# ============================================================
# HELPERS
# ============================================================
async def get_user(user_id):
    return await asyncio.to_thread(execute_query, "SELECT * FROM users WHERE user_id=?", (user_id,), fetch_one=True)

async def upsert_user(user_id, username, full_name):
    await asyncio.to_thread(
        execute_query,
        "INSERT INTO users(user_id, username, full_name, created_at) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name",
        (user_id, username, full_name, int(time.time()))
    )
    await asyncio.to_thread(
        execute_query,
        "INSERT OR IGNORE INTO user_state(user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES(?,?,?,?)",
        (user_id, 0, 0, tehran_now().date().isoformat())
    )

async def is_premium(user_row):
    if not user_row:
        return False
    return user_row[4] in ("vip", "pro", "elite") and int(time.time()) < int(user_row[5] or 0)

async def get_ai_count(user_id):
    row = await asyncio.to_thread(execute_query, "SELECT daily_ai_count FROM user_state WHERE user_id=?", (user_id,), fetch_one=True)
    return row[0] if row else 0

async def increase_ai_count(user_id):
    today = tehran_now().date().isoformat()
    row = await asyncio.to_thread(execute_query, "SELECT last_reset_day FROM user_state WHERE user_id=?", (user_id,), fetch_one=True)
    if not row or row[0] != today:
        await asyncio.to_thread(execute_query, "UPDATE user_state SET daily_ai_count=0,last_reset_day=? WHERE user_id=?", (today, user_id))
    await asyncio.to_thread(execute_query, "UPDATE user_state SET daily_ai_count = daily_ai_count + 1, last_ai_at=? WHERE user_id=?", (int(time.time()), user_id))

async def rate_limit_ok(user_id):
    row = await asyncio.to_thread(execute_query, "SELECT last_ai_at FROM user_state WHERE user_id=?", (user_id,), fetch_one=True)
    last = row[0] if row else 0
    return (int(time.time()) - int(last)) >= RATE_LIMIT_SECONDS

async def coinex_get_ticker(symbol="BTCUSDT"):
    url = f"https://api.coinex.com/v2/spot/ticker?market={symbol}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=15) as resp:
            return await resp.json()

async def ask_groq(prompt: str):
    if not groq_client:
        return "❌ سرویس AI در دسترس نیست."
    loop = asyncio.get_running_loop()
    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
    res = await loop.run_in_executor(None, _call)
    return res.choices[0].message.content.strip()

# ============================================================
# KEYBOARDS
# ============================================================
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="price")],
        [InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai")],
        [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_vip")],
        [InlineKeyboardButton(text="👤 پروفایل", callback_data="profile")],
    ])

# ============================================================
# HANDLERS
# ============================================================
@router.message(CommandStart())
async def start(message: types.Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
    user = await get_user(message.from_user.id)
    plan = user[4] if user else "free"
    text = (
        f"👋 سلام {message.from_user.full_name}!\n\n"
        f"🕐 زمان تهران: {tehran_datetime()}\n"
        f"💎 پلن شما: {plan}\n\n"
        f"🔹 دستورات:\n"
        f"/price [نماد] - قیمت لحظه‌ای\n"
        f"/ai [سوال] - تحلیل هوشمند\n"
        f"/time - زمان تهران\n"
        f"/me - پروفایل\n"
        f"/buyvip - خرید VIP\n\n"
        f"📢 کانال: {CHANNEL_USERNAME}"
    )
    await message.answer(text, reply_markup=main_keyboard())

@router.message(Command("time"))
async def time_cmd(message: types.Message):
    await message.answer(f"🕐 {tehran_datetime()}")

@router.message(Command("me"))
async def me(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ /start را بزنید.")
    premium = await is_premium(user)
    ai_count = await get_ai_count(message.from_user.id)
    text = (
        f"👤 پروفایل\n\n"
        f"نام: {user[2]}\n"
        f"پلن: {user[4]}\n"
        f"پریمیوم: {'بله' if premium else 'خیر'}\n"
        f"AI امروز: {ai_count}\n"
        f"زمان: {tehran_datetime()}"
    )
    await message.answer(text)

@router.message(Command("price"))
async def price(message: types.Message):
    symbol = message.text.split(maxsplit=1)[1].strip().upper() if len(message.text.split()) > 1 else "BTCUSDT"
    try:
        data = await coinex_get_ticker(symbol)
        if data and "data" in data:
            ticker = data["data"]
            text = f"📊 {symbol}\n💰 ${ticker.get('price', 'N/A')}\n📈 تغییر: {ticker.get('change', 'N/A')}%"
        else:
            text = "❌ خطا"
        await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")

@router.message(Command("ai"))
async def ai_cmd(message: types.Message):
    text = message.text.partition(" ")[2].strip()
    if not text:
        return await message.answer("❌ /ai سوال خود را بنویسید")
    
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ /start را بزنید.")
    
    premium = await is_premium(user)
    count = await get_ai_count(message.from_user.id)
    
    if not premium and count >= FREE_DAILY_AI_LIMIT:
        return await message.answer(f"⚠️ سقف AI امروز ({FREE_DAILY_AI_LIMIT}) پر شده.")
    
    if not await rate_limit_ok(message.from_user.id):
        return await message.answer(f"⏳ {RATE_LIMIT_SECONDS} ثانیه صبر کنید.")
    
    await message.answer("🤖 در حال تحلیل...")
    try:
        answer = await ask_groq(text)
        await increase_ai_count(message.from_user.id)
        await message.answer(answer[:3900])
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")

@router.message(Command("buyvip"))
async def buyvip(message: types.Message):
    text = (
        f"💰 خرید VIP\n\n"
        f"💎 مبلغ: {VIP_PRICE_TOMAN:,} تومان\n"
        f"📅 مدت: ۳۰ روز\n\n"
        f"💳 کارت: <code>6063731196254479</code>\n"
        f"نام: فرهاد بهمرد\n\n"
        f"✅ رسید را ارسال کنید تا تأیید شود."
    )
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 ارسال رسید", callback_data="send_receipt")]
    ]))

# ============================================================
# CALLBACKS
# ============================================================
@router.callback_query(lambda c: c.data == "price")
async def cb_price(callback: types.CallbackQuery):
    await callback.answer("📊 دریافت قیمت...")
    try:
        data = await coinex_get_ticker("BTCUSDT")
        if data and "data" in data:
            ticker = data["data"]
            text = f"📊 قیمت لحظه‌ای\n\nBTC/USDT: ${ticker.get('price', 'N/A')}\nتغییر: {ticker.get('change', 'N/A')}%"
        else:
            text = "❌ خطا"
        await callback.message.edit_text(text, reply_markup=main_keyboard())
    except Exception as e:
        await callback.message.answer(f"❌ خطا: {e}")

@router.callback_query(lambda c: c.data == "ai")
async def cb_ai(callback: types.CallbackQuery):
    await callback.answer("🤖 تحلیل AI...")
    await callback.message.edit_text(
        "🤖 سوال خود را بنویسید.\nمثال: بیت‌کوین رو تحلیل کن",
        reply_markup=main_keyboard()
    )

@router.callback_query(lambda c: c.data == "buy_vip")
async def cb_buy_vip(callback: types.CallbackQuery):
    await callback.answer("💰 خرید VIP...")
    text = (
        f"💰 خرید VIP\n\n"
        f"💎 مبلغ: {VIP_PRICE_TOMAN:,} تومان\n"
        f"📅 مدت: ۳۰ روز\n\n"
        f"💳 کارت: <code>6063731196254479</code>\n"
        f"نام: فرهاد بهمرد\n\n"
        f"✅ رسید را ارسال کنید."
    )
    await callback.message.edit_text(text, reply_markup=main_keyboard())

@router.callback_query(lambda c: c.data == "profile")
async def cb_profile(callback: types.CallbackQuery):
    await callback.answer("👤 پروفایل...")
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("❌ /start را بزنید.")
        return
    premium = await is_premium(user)
    ai_count = await get_ai_count(callback.from_user.id)
    text = (
        f"👤 پروفایل\n\n"
        f"نام: {user[2]}\n"
        f"پلن: {user[4]}\n"
        f"پریمیوم: {'✅ بله' if premium else '❌ خیر'}\n"
        f"AI امروز: {ai_count}\n"
        f"زمان: {tehran_datetime()}"
    )
    await callback.message.edit_text(text, reply_markup=main_keyboard())

@router.callback_query(lambda c: c.data == "send_receipt")
async def cb_send_receipt(callback: types.CallbackQuery):
    await callback.answer("📤 رسید خود را ارسال کنید...")
    await callback.message.edit_text(
        "📤 لطفاً رسید یا شماره پیگیری را به صورت متن ارسال کنید.",
        reply_markup=main_keyboard()
    )

# ============================================================
# پرداخت
# ============================================================
@router.message()
async def handle_payment(message: types.Message):
    text = (message.text or "").lower()
    if any(kw in text for kw in ["رسید", "شماره پیگیری", "واریز", "پرداخت"]):
        await message.answer(
            "✅ رسید دریافت شد.\n"
            "⏳ ادمین بررسی می‌کند.\n"
            "📢 پس از تأیید، VIP فعال می‌شود."
        )
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"💳 درخواست VIP\n"
                        f"کاربر: {message.from_user.id}\n"
                        f"نام: {message.from_user.full_name}\n"
                        f"پیام: {message.text[:300]}"
                    )
                except:
                    pass

# ============================================================
# MAIN (Polling Mode)
# ============================================================
async def main():
    logger.info("🚀 Starting bot in polling mode...")
    await asyncio.to_thread(init_db_sync)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

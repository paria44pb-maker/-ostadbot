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
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ============================================================
# ✅ Groq
# ============================================================
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False
    print("⚠️ Groq library not installed.")

# ============================================================
# ✅ توکن تلگرام
# ============================================================
BOT_TOKEN = "7225279768:AAHB8ZQdgzhFoeV8tPryyReJ-Gq_Y8pI90U"

# ============================================================
# متغیرهای محیطی
# ============================================================
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
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
# برنامه FastAPI و ربات
# ============================================================
app = FastAPI()

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
router = Router()
dp.include_router(router)

# ============================================================
# راه‌اندازی Groq
# ============================================================
groq_client = None
if GROQ_AVAILABLE and GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Groq client initialized")
    except Exception as e:
        logger.error(f"❌ Groq initialization failed: {e}")

# ============================================================
# دیتابیس با sqlite3 (همراه با قفل)
# ============================================================
DB_LOCK = asyncio.Lock()

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
        CREATE TABLE IF NOT EXISTS alerts (
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
    cur.execute('''
        CREATE TABLE IF NOT EXISTS channel_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT,
            content TEXT,
            created_at INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

async def init_db():
    await asyncio.to_thread(init_db_sync)

def tehran_now():
    return datetime.now(ZoneInfo("Asia/Tehran"))

def tehran_datetime():
    return tehran_now().strftime("%Y/%m/%d - %H:%M:%S")

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

async def log_action(user_id, action, data=""):
    query = "INSERT INTO logs(user_id, action, data, created_at) VALUES(?,?,?,?)"
    await asyncio.to_thread(execute_query, query, (user_id, action, data, int(time.time())))

async def get_user(user_id):
    query = "SELECT * FROM users WHERE user_id=?"
    return await asyncio.to_thread(execute_query, query, (user_id,), fetch_one=True)

async def upsert_user(user_id, username, full_name):
    query1 = """
        INSERT INTO users(user_id, username, full_name, created_at) VALUES(?,?,?,?) 
        ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name
    """
    query2 = """
        INSERT OR IGNORE INTO user_state(user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES(?,?,?,?)
    """
    await asyncio.to_thread(execute_query, query1, (user_id, username, full_name, int(time.time())))
    await asyncio.to_thread(execute_query, query2, (user_id, 0, 0, tehran_now().date().isoformat()))

async def set_plan(user_id, plan, days=30, amount=VIP_PRICE_TOMAN, reference="manual"):
    until = int((tehran_now() + timedelta(days=days)).timestamp())
    query1 = "UPDATE users SET plan=?, plan_until=? WHERE user_id=?"
    query2 = "INSERT INTO payments(user_id, plan, amount, status, reference, created_at) VALUES(?,?,?,?,?,?)"
    await asyncio.to_thread(execute_query, query1, (plan, until, user_id))
    await asyncio.to_thread(execute_query, query2, (user_id, plan, amount, "paid", reference, int(time.time())))

async def is_premium(user_row):
    if not user_row:
        return False
    return user_row[4] in ("vip", "pro", "elite") and int(time.time()) < int(user_row[5] or 0)

async def reset_daily_if_needed(user_id):
    today = tehran_now().date().isoformat()
    query1 = "SELECT last_reset_day FROM user_state WHERE user_id=?"
    row = await asyncio.to_thread(execute_query, query1, (user_id,), fetch_one=True)
    if not row:
        query2 = "INSERT OR IGNORE INTO user_state(user_id,last_ai_at,daily_ai_count,last_reset_day) VALUES(?,?,?,?)"
        await asyncio.to_thread(execute_query, query2, (user_id, 0, 0, today))
    elif row[0] != today:
        query3 = "UPDATE user_state SET daily_ai_count=0,last_reset_day=? WHERE user_id=?"
        await asyncio.to_thread(execute_query, query3, (today, user_id))

async def increase_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    query = "UPDATE user_state SET daily_ai_count = daily_ai_count + 1, last_ai_at=? WHERE user_id=?"
    await asyncio.to_thread(execute_query, query, (int(time.time()), user_id))

async def get_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    query = "SELECT daily_ai_count FROM user_state WHERE user_id=?"
    row = await asyncio.to_thread(execute_query, query, (user_id,), fetch_one=True)
    return row[0] if row else 0

def coinex_sign(method: str, path: str, body: str = "", timestamp: str = ""):
    msg = f"{method.upper()}{path}{timestamp}{body}"
    return hmac.new(COINEX_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()

async def coinex_get_ticker(symbol="BTCUSDT"):
    url = f"https://api.coinex.com/v2/spot/ticker?market={symbol}"
    headers = {}
    if COINEX_KEY and COINEX_SECRET:
        ts = str(int(time.time() * 1000))
        path = f"/v2/spot/ticker?market={symbol}"
        headers = {
            "X-COINEX-KEY": COINEX_KEY,
            "X-COINEX-SIGN": coinex_sign("GET", path, "", ts),
            "X-COINEX-TIMESTAMP": ts,
            "X-COINEX-WINDOWTIME": "5000",
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=15) as resp:
            return await resp.json()

async def ask_groq(prompt: str, user_profile: str = ""):
    if not groq_client:
        return "❌ سرویس AI در دسترس نیست. لطفاً بعداً تلاش کنید."
    system = (
        "You are a professional Persian crypto assistant. "
        "Be concise, practical, risk-aware, and never promise guaranteed profit."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Profile: {user_profile}\n\nQuestion: {prompt}"}
    ]
    loop = asyncio.get_running_loop()
    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
        )
    res = await loop.run_in_executor(None, _call)
    return res.choices[0].message.content.strip()

async def rate_limit_ok(user_id):
    query = "SELECT last_ai_at FROM user_state WHERE user_id=?"
    row = await asyncio.to_thread(execute_query, query, (user_id,), fetch_one=True)
    last = row[0] if row else 0
    return (int(time.time()) - int(last)) >= RATE_LIMIT_SECONDS

async def channel_post(text: str):
    try:
        await bot.send_message(chat_id=CHANNEL_USERNAME, text=text)
    except Exception as e:
        logger.error(f"Channel post error: {e}")

# ============================================================
# کیبوردها
# ============================================================
def vip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 خرید VIP ماهانه ۱۹۹٬۰۰۰ تومان", callback_data="buy_vip")],
        [InlineKeyboardButton(text="📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
    ])

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="price_btc")],
        [InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai_analyze")],
        [InlineKeyboardButton(text="👀 واچ‌لیست", callback_data="watchlist")],
        [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_vip")],
        [InlineKeyboardButton(text="👤 پروفایل", callback_data="profile")],
    ])

# ============================================================
# CALLBACK HANDLERS
# ============================================================
@router.callback_query(lambda c: c.data == "buy_vip")
async def buy_vip_callback(callback: types.CallbackQuery):
    text = (
        f"💰 <b>خرید اشتراک VIP</b>\n\n"
        f"💎 مبلغ: <b>{VIP_PRICE_TOMAN:,}</b> تومان\n"
        f"📅 مدت: ۳۰ روز\n\n"
        f"💳 کارت به کارت:\n"
        f"نام: <b>فرهاد بهمرد</b>\n"
        f"کارت: <code>6063731196254479</code>\n\n"
        f"✅ بعد از واریز، رسید یا شماره پیگیری را ارسال کن."
    )
    await callback.message.answer(text, reply_markup=vip_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "price_btc")
async def price_btc_callback(callback: types.CallbackQuery):
    await callback.answer("📊 دریافت قیمت...")
    try:
        data = await coinex_get_ticker("BTCUSDT")
        text = f"📊 <b>قیمت لحظه‌ای</b>\n\n"
        if data and "data" in data:
            ticker = data["data"]
            text += f"BTC/USDT: ${ticker.get('price', 'N/A')}\n"
            text += f"تغییر: {ticker.get('change', 'N/A')}%\n"
            text += f"بالاترین: ${ticker.get('high', 'N/A')}\n"
            text += f"پایین‌ترین: ${ticker.get('low', 'N/A')}"
        else:
            text += "❌ خطا در دریافت قیمت"
        await callback.message.edit_text(text, reply_markup=main_keyboard())
    except Exception as e:
        await callback.message.answer(f"❌ خطا: {e}")

@router.callback_query(lambda c: c.data == "ai_analyze")
async def ai_analyze_callback(callback: types.CallbackQuery):
    await callback.answer("🤖 تحلیل AI...")
    await callback.message.edit_text(
        "🤖 <b>تحلیل هوشمند</b>\n\n"
        "لطفاً سوال یا تحلیل خود را به صورت متن بنویسید.\n"
        "مثال: `بیت‌کوین رو با اندیکاتورها تحلیل کن`",
        reply_markup=main_keyboard()
    )

@router.callback_query(lambda c: c.data == "watchlist")
async def watchlist_callback(callback: types.CallbackQuery):
    await callback.answer("👀 واچ‌لیست...")
    query = "SELECT symbol FROM watchlists WHERE user_id=?"
    rows = await asyncio.to_thread(execute_query, query, (callback.from_user.id,), fetch_all=True)
    if rows:
        text = "👀 <b>واچ‌لیست شما</b>\n\n"
        for row in rows:
            text += f"• {row[0]}\n"
    else:
        text = "👀 <b>واچ‌لیست شما خالی است.</b>\n\nبرای افزودن از دستور /watch استفاده کنید."
    await callback.message.edit_text(text, reply_markup=main_keyboard())

@router.callback_query(lambda c: c.data == "profile")
async def profile_callback(callback: types.CallbackQuery):
    await callback.answer("👤 پروفایل...")
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("❌ کاربر یافت نشد. لطفاً /start را بزنید.")
        return
    premium = await is_premium(user)
    ai_count = await get_ai_count(callback.from_user.id)
    text = (
        f"👤 <b>پروفایل شما</b>\n\n"
        f"🆔 آیدی: {callback.from_user.id}\n"
        f"👤 نام: {user[2]}\n"
        f"💎 پلن: <b>{user[4]}</b>\n"
        f"🌟 پریمیوم: <b>{'✅ بله' if premium else '❌ خیر'}</b>\n"
        f"🤖 AI امروز: <b>{ai_count}</b>\n"
        f"📅 زمان تهران: <b>{tehran_datetime()}</b>"
    )
    await callback.message.edit_text(text, reply_markup=main_keyboard())

# ============================================================
# COMMAND HANDLERS
# ============================================================
@router.message(CommandStart())
async def start(message: types.Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
    user = await get_user(message.from_user.id)
    plan = user[4] if user else "free"
    text = (
        f"👋 سلام {message.from_user.full_name}!\n\n"
        f"🕐 زمان تهران: <b>{tehran_datetime()}</b>\n"
        f"💎 پلن شما: <b>{plan}</b>\n\n"
        f"🔹 <b>دستورات موجود:</b>\n"
        f"/ai [سوال] - تحلیل هوشمند\n"
        f"/price [نماد] - قیمت لحظه‌ای\n"
        f"/watch [نماد] - افزودن به واچ‌لیست\n"
        f"/time - زمان تهران\n"
        f"/subscribe - خرید اشتراک\n"
        f"/me - پروفایل\n"
        f"/buyvip - خرید VIP\n"
        f"/admin - پنل ادمین\n\n"
        f"📢 کانال: {CHANNEL_USERNAME}"
    )
    await message.answer(text, reply_markup=main_keyboard())
    await log_action(message.from_user.id, "start")

@router.message(Command("time"))
async def time_cmd(message: types.Message):
    await message.answer(f"🕐 <b>زمان تهران</b>\n{tehran_datetime()}")

@router.message(Command("me"))
async def me(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ ابتدا /start را بزنید.")
    premium = await is_premium(user)
    ai_count = await get_ai_count(message.from_user.id)
    text = (
        f"👤 <b>پروفایل شما</b>\n\n"
        f"🆔 آیدی: {message.from_user.id}\n"
        f"👤 نام: {user[2]}\n"
        f"💎 پلن: <b>{user[4]}</b>\n"
        f"🌟 پریمیوم: <b>{'✅ بله' if premium else '❌ خیر'}</b>\n"
        f"🤖 AI امروز: <b>{ai_count}</b>\n"
        f"📅 زمان تهران: <b>{tehran_datetime()}</b>\n\n"
        f"📢 کانال: {CHANNEL_USERNAME}"
    )
    await message.answer(text, reply_markup=main_keyboard())

@router.message(Command("price"))
async def price(message: types.Message):
    symbol = message.text.split(maxsplit=1)[1].strip().upper() if len(message.text.split()) > 1 else "BTCUSDT"
    try:
        data = await coinex_get_ticker(symbol)
        if data and "data" in data:
            ticker = data["data"]
            text = f"📊 <b>قیمت {symbol}</b>\n\n"
            text += f"💰 قیمت: ${ticker.get('price', 'N/A')}\n"
            text += f"📈 تغییر: {ticker.get('change', 'N/A')}%\n"
            text += f"📊 بالاترین: ${ticker.get('high', 'N/A')}\n"
            text += f"📉 پایین‌ترین: ${ticker.get('low', 'N/A')}"
        else:
            text = f"❌ خطا: داده‌ای برای {symbol} یافت نشد."
        await message.answer(text)
    except Exception as e:
        logger.exception("price error")
        await message.answer(f"❌ خطا در دریافت قیمت: {e}")

@router.message(Command("watch"))
async def watch(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("❌ نمونه: /watch BTCUSDT")
    symbol = parts[1].upper()
    query = "INSERT INTO watchlists(user_id, symbol, created_at) VALUES(?,?,?)"
    await asyncio.to_thread(execute_query, query, (message.from_user.id, symbol, int(time.time())))
    await message.answer(f"✅ {symbol} به واچ‌لیست اضافه شد.")
    await log_action(message.from_user.id, "watch", symbol)

@router.message(Command("subscribe"))
async def subscribe(message: types.Message):
    parts = message.text.split()
    plan = parts[1].lower() if len(parts) > 1 else "vip"
    if plan not in ("vip", "pro", "elite"):
        return await message.answer("❌ پلن معتبر: vip / pro / elite")
    await message.answer(
        f"💎 برای فعال‌سازی <b>{plan.upper()}</b>، روی دکمه زیر بزنید.",
        reply_markup=vip_keyboard()
    )

@router.message(Command("buyvip"))
async def buyvip(message: types.Message):
    text = (
        f"💰 <b>خرید اشتراک VIP</b>\n\n"
        f"💎 مبلغ: <b>{VIP_PRICE_TOMAN:,}</b> تومان\n"
        f"📅 مدت: ۳۰ روز\n\n"
        f"💳 کارت به کارت:\n"
        f"نام: <b>فرهاد بهمرد</b>\n"
        f"کارت: <code>6063731196254479</code>\n\n"
        f"✅ بعد از واریز، رسید یا شماره پیگیری را ارسال کن."
    )
    await message.answer(text, reply_markup=vip_keyboard())

@router.message(Command("ai"))
async def ai_cmd(message: types.Message):
    text = message.text.partition(" ")[2].strip()
    if not text:
        return await message.answer("❌ نمونه: /ai بیت‌کوین رو تحلیل کن")
    
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ ابتدا /start را بزنید.")
    
    premium = await is_premium(user)
    count = await get_ai_count(message.from_user.id)
    
    if not groq_client:
        return await message.answer("❌ سرویس AI در دسترس نیست. لطفاً بعداً تلاش کنید.")
    
    if not premium and count >= FREE_DAILY_AI_LIMIT:
        return await message.answer(
            f"⚠️ سقف AI رایگان امروز ({FREE_DAILY_AI_LIMIT}) پر شده.\n"
            f"برای دسترسی بیشتر پلن VIP تهیه کنید."
        )
    
    if not await rate_limit_ok(message.from_user.id):
        return await message.answer(f"⏳ لطفاً {RATE_LIMIT_SECONDS} ثانیه بعد دوباره تلاش کن.")
    
    profile = f"risk={user[3]}, plan={user[4]}, premium={premium}"
    try:
        await message.answer("🤖 در حال تحلیل...")
        answer = await ask_groq(text, profile)
        await increase_ai_count(message.from_user.id)
        await message.answer(answer[:3900])
        await log_action(message.from_user.id, "ai", text[:200])
    except Exception as e:
        logger.exception("groq error")
        await message.answer(f"❌ AI فعلاً در دسترس نیست: {e}")

@router.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ دسترسی غیرمجاز.")
    
    query1 = "SELECT COUNT(*) FROM users"
    query2 = "SELECT COUNT(*) FROM payments WHERE status='paid'"
    query3 = "SELECT COUNT(*) FROM watchlists"
    
    users = (await asyncio.to_thread(execute_query, query1, (), fetch_one=True))[0]
    payments = (await asyncio.to_thread(execute_query, query2, (), fetch_one=True))[0]
    watchs = (await asyncio.to_thread(execute_query, query3, (), fetch_one=True))[0]
    
    text = (
        f"🔧 <b>پنل ادمین</b>\n\n"
        f"👥 کاربران: {users}\n"
        f"💰 پرداخت‌ها: {payments}\n"
        f"👀 واچ‌لیست‌ها: {watchs}\n"
        f"🕐 زمان تهران: {tehran_datetime()}\n\n"
        f"📢 کانال: {CHANNEL_USERNAME}"
    )
    await message.answer(text)

# ============================================================
# پرداخت خودکار با رسید
# ============================================================
@router.message()
async def handle_payment_proof(message: types.Message):
    text = (message.text or "").lower()
    keywords = ["رسید", "شماره پیگیری", "واریز", "پرداخت", "کارت به کارت"]
    if any(kw in text for kw in keywords):
        await message.answer(
            "✅ رسید شما دریافت شد.\n"
            "⏳ برای تأیید نهایی، ادمین بررسی می‌کند.\n"
            "📢 پس از تأیید، اشتراک VIP شما فعال خواهد شد."
        )
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"💳 <b>درخواست پرداخت VIP</b>\n\n"
                        f"🆔 کاربر: {message.from_user.id}\n"
                        f"👤 نام: {message.from_user.full_name}\n"
                        f"📛 یوزرنیم: @{message.from_user.username or 'none'}\n\n"
                        f"📝 پیام:\n{message.text[:500]}\n\n"
                        f"✅ برای تأیید: /verify {message.from_user.id}\n"
                        f"❌ برای رد: /reject {message.from_user.id}"
                    )
                except Exception as e:
                    logger.error(f"Error sending to admin: {e}")

# ============================================================
# دستورات تأیید ادمین
# ============================================================
@router.message(Command("verify"))
async def verify_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ دسترسی غیرمجاز.")
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("❌ /verify [user_id]")
    try:
        user_id = int(parts[1])
    except:
        return await message.answer("❌ آیدی نامعتبر.")
    await set_plan(user_id, "vip", 30, VIP_PRICE_TOMAN, f"admin_{message.from_user.id}")
    await message.answer(f"✅ کاربر {user_id} به VIP تبدیل شد.")
    try:
        await bot.send_message(
            user_id,
            f"🎉 <b>تبریک!</b>\n\n"
            f"اشتراک VIP شما با موفقیت فعال شد.\n"
            f"📅 مدت: ۳۰ روز\n"
            f"💎 از تمام قابلیت‌های ویژه استفاده کنید."
        )
    except:
        pass

@router.message(Command("reject"))
async def reject_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ دسترسی غیرمجاز.")
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("❌ /reject [user_id]")
    try:
        user_id = int(parts[1])
    except:
        return await message.answer("❌ آیدی نامعتبر.")
    await message.answer(f"✅ درخواست کاربر {user_id} رد شد.")
    try:
        await bot.send_message(
            user_id,
            f"❌ متأسفانه درخواست VIP شما تأیید نشد.\n"
            f"لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید."
        )
    except:
        pass

# ============================================================
# WEBHOOK
# ============================================================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok", "tehran_time": tehran_datetime(), "channel": CHANNEL_USERNAME}

# ============================================================
# ارسال روزانه به کانال
# ============================================================
async def daily_channel_post():
    while True:
        try:
            text = (
                f"📊 <b>گزارش روزانه CryptoPulse</b>\n\n"
                f"🕐 زمان تهران: {tehran_datetime()}\n"
                f"✅ ربات فعال است\n"
                f"💎 VIP ماهانه: {VIP_PRICE_TOMAN:,} تومان\n\n"
                f"📢 {CHANNEL_USERNAME}"
            )
            await channel_post(text)
        except Exception as e:
            logger.warning(f"channel post error: {e}")
        await asyncio.sleep(24 * 3600)

# ============================================================
# STARTUP & SHUTDOWN
# ============================================================
@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Starting bot...")
    await init_db()
    
    if WEBHOOK_URL:
        try:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"✅ Webhook set to {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
    else:
        logger.warning("⚠️ WEBHOOK_URL not set")
    
    asyncio.create_task(daily_channel_post())
    logger.info("✅ Bot started successfully!")

@app.on_event("shutdown")
async def on_shutdown():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
    except:
        pass
    logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))

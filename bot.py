import os
import time
import hmac
import json
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
import aiosqlite
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
COINEX_KEY = os.getenv("COINEX_KEY", "")
COINEX_SECRET = os.getenv("COINEX_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit())
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
FREE_DAILY_AI_LIMIT = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "2"))
VIP_PRICE_TOMAN = 199000

if not BOT_TOKEN or not WEBHOOK_URL or not GROQ_API_KEY:
    raise RuntimeError("BOT_TOKEN, WEBHOOK_URL, GROQ_API_KEY are required")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("cryptopulse")

app = FastAPI()
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)
groq_client = Groq(api_key=GROQ_API_KEY)

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    language TEXT DEFAULT 'fa',
    risk_level TEXT DEFAULT 'medium',
    plan TEXT DEFAULT 'free',
    plan_until INTEGER DEFAULT 0,
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS user_state (
    user_id INTEGER PRIMARY KEY,
    last_ai_at INTEGER DEFAULT 0,
    daily_ai_count INTEGER DEFAULT 0,
    last_reset_day TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symbol TEXT,
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symbol TEXT,
    target_price REAL,
    alert_type TEXT,
    active INTEGER DEFAULT 1,
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    plan TEXT,
    amount REAL,
    status TEXT,
    reference TEXT,
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    data TEXT,
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS channel_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_type TEXT,
    content TEXT,
    created_at INTEGER
);
"""

def tehran_now():
    return datetime.now(ZoneInfo("Asia/Tehran"))

def tehran_datetime():
    return tehran_now().strftime("%Y/%m/%d - %H:%M:%S")

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.executescript(CREATE_TABLES)
        await conn.commit()

async def log_action(user_id, action, data=""):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute(
            "INSERT INTO logs(user_id, action, data, created_at) VALUES(?,?,?,?)",
            (user_id, action, data, int(time.time()))
        )
        await conn.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()

async def upsert_user(user_id, username, full_name):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute(
            "INSERT INTO users(user_id, username, full_name, created_at) VALUES(?,?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name",
            (user_id, username, full_name, int(time.time()))
        )
        await conn.execute(
            "INSERT OR IGNORE INTO user_state(user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES(?,?,?,?)",
            (user_id, 0, 0, tehran_now().date().isoformat())
        )
        await conn.commit()

async def set_plan(user_id, plan, days=30, amount=VIP_PRICE_TOMAN, reference="manual"):
    until = int((tehran_now() + timedelta(days=days)).timestamp())
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute("UPDATE users SET plan=?, plan_until=? WHERE user_id=?", (plan, until, user_id))
        await conn.execute(
            "INSERT INTO payments(user_id, plan, amount, status, reference, created_at) VALUES(?,?,?,?,?,?)",
            (user_id, plan, amount, "paid", reference, int(time.time()))
        )
        await conn.commit()

async def is_premium(user_row):
    if not user_row:
        return False
    return user_row[4] in ("vip", "pro", "elite") and int(time.time()) < int(user_row[5] or 0)

async def reset_daily_if_needed(user_id):
    today = tehran_now().date().isoformat()
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT last_reset_day FROM user_state WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row:
            await conn.execute(
                "INSERT OR IGNORE INTO user_state(user_id,last_ai_at,daily_ai_count,last_reset_day) VALUES(?,?,?,?)",
                (user_id, 0, 0, today)
            )
        elif row[0] != today:
            await conn.execute("UPDATE user_state SET daily_ai_count=0,last_reset_day=? WHERE user_id=?", (today, user_id))
        await conn.commit()

async def increase_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute(
            "UPDATE user_state SET daily_ai_count = daily_ai_count + 1, last_ai_at=? WHERE user_id=?",
            (int(time.time()), user_id)
        )
        await conn.commit()

async def get_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT daily_ai_count FROM user_state WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
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
    system = (
        "You are a professional Persian crypto assistant. "
        "Be concise, practical, risk-aware, and never promise guaranteed profit."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Profile: {user_profile}

Question: {prompt}"}
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
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT last_ai_at FROM user_state WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        last = row[0] if row else 0
        return (int(time.time()) - int(last)) >= RATE_LIMIT_SECONDS

async def channel_post(text: str):
    await bot.send_message(chat_id=CHANNEL_USERNAME, text=text)

def vip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="خرید VIP ماهانه ۱۹۹٬۰۰۰ تومان", callback_data="buy_vip")],
        [InlineKeyboardButton(text="عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
    ])

@router.callback_query(lambda c: c.data == "buy_vip")
async def buy_vip_callback(callback: types.CallbackQuery):
    text = (
        f"برای فعال‌سازی VIP، مبلغ <b>{VIP_PRICE_TOMAN:,}</b> تومان را به کارت زیر واریز کن:

"
        f"نام: <b>فرهاد بهمرد</b>
"
        f"کارت: <code>6063731196254479</code>

"
        f"بعد از واریز، <b>رسید</b> یا <b>شماره پیگیری</b> را همینجا ارسال کن."
    )
    await callback.message.answer(text, reply_markup=vip_keyboard())
    await callback.answer()

@router.message(CommandStart())
async def start(message: types.Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
    user = await get_user(message.from_user.id)
    plan = user[4] if user else "free"
    await message.answer(
        f"سلام {message.from_user.full_name} 👋
"
        f"زمان تهران: <b>{tehran_datetime()}</b>
"
        f"پلن شما: <b>{plan}</b>
"
        f"اشتراک VIP ماهانه: <b>{VIP_PRICE_TOMAN:,} تومان</b>

"
        f"دستورها:
"
        f"/ai سوال
"
        f"/price BTCUSDT
"
        f"/watch BTCUSDT
"
        f"/time
"
        f"/subscribe vip
"
        f"/me
"
        f"/buyvip"
    )
    await log_action(message.from_user.id, "start")

@router.message(Command("time"))
async def time_cmd(message: types.Message):
    await message.answer(f"زمان فعلی تهران:
<b>{tehran_datetime()}</b>")

@router.message(Command("me"))
async def me(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("ابتدا /start")
    premium = await is_premium(user)
    ai_count = await get_ai_count(message.from_user.id)
    await message.answer(
        f"کاربر: <b>{user[2]}</b>
"
        f"پلن: <b>{user[4]}</b>
"
        f"پریمیوم: <b>{'بله' if premium else 'خیر'}</b>
"
        f"AI امروز: <b>{ai_count}</b>
"
        f"زمان تهران: <b>{tehran_datetime()}</b>
"
        f"کانال: <b>{CHANNEL_USERNAME}</b>"
    )

@router.message(Command("price"))
async def price(message: types.Message):
    symbol = message.text.split(maxsplit=1)[1].strip().upper() if len(message.text.split()) > 1 else "BTCUSDT"
    try:
        data = await coinex_get_ticker(symbol)
        await message.answer(f"<b>{symbol}</b>
<code>{json.dumps(data, ensure_ascii=False, indent=2)[:3500]}</code>")
    except Exception as e:
        logger.exception("price error")
        await message.answer(f"خطا در دریافت قیمت: {e}")

@router.message(Command("watch"))
async def watch(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("نمونه: /watch BTCUSDT")
    symbol = parts[1].upper()
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute(
            "INSERT INTO watchlists(user_id, symbol, created_at) VALUES(?,?,?)",
            (message.from_user.id, symbol, int(time.time()))
        )
        await conn.commit()
    await message.answer(f"{symbol} به واچ‌لیست اضافه شد.")
    await log_action(message.from_user.id, "watch", symbol)

@router.message(Command("subscribe"))
async def subscribe(message: types.Message):
    parts = message.text.split()
    plan = parts[1].lower() if len(parts) > 1 else "vip"
    if plan not in ("vip", "pro", "elite"):
        return await message.answer("پلن معتبر: vip / pro / elite")
    await message.answer(
        f"برای فعال‌سازی {plan.upper()}، روی /buyvip بزن یا از دکمه زیر استفاده کن.",
        reply_markup=vip_keyboard()
    )

@router.message(Command("buyvip"))
async def buyvip(message: types.Message):
    await message.answer(
        f"برای فعال‌سازی VIP، مبلغ <b>{VIP_PRICE_TOMAN:,}</b> تومان را به کارت زیر واریز کن:

"
        f"نام: <b>فرهاد بهمرد</b>
"
        f"کارت: <code>6063731196254479</code>

"
        f"بعد از واریز، رسید یا شماره پیگیری را ارسال کن.",
        reply_markup=vip_keyboard()
    )

@router.message(Command("ai"))
async def ai_cmd(message: types.Message):
    text = message.text.partition(" ")[2].strip()
    if not text:
        return await message.answer("نمونه: /ai روی XRP چه نظری داری؟")
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("ابتدا /start")
    premium = await is_premium(user)
    count = await get_ai_count(message.from_user.id)
    if not premium and count >= FREE_DAILY_AI_LIMIT:
        return await message.answer("سقف AI رایگان امروز پر شده. برای دسترسی بیشتر پلن VIP لازم است.")
    if not await rate_limit_ok(message.from_user.id):
        return await message.answer("لطفاً چند ثانیه بعد دوباره تلاش کن.")
    profile = f"risk={user[3]}, plan={user[4]}, premium={premium}"
    try:
        answer = await ask_groq(text, profile)
        await increase_ai_count(message.from_user.id)
        await message.answer(answer[:3900])
        await log_action(message.from_user.id, "ai", text[:200])
    except Exception as e:
        logger.exception("groq error")
        await message.answer(f"AI فعلاً در دسترس نیست: {e}")

@router.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("دسترسی نداری.")
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        cur = await conn.execute("SELECT COUNT(*) FROM payments")
        payments = (await cur.fetchone())[0]
        cur = await conn.execute("SELECT COUNT(*) FROM watchlists")
        watchs = (await cur.fetchone())[0]
    await message.answer(
        f"ادمین فعال است.
"
        f"Users: {users}
Payments: {payments}
Watchlists: {watchs}
"
        f"زمان تهران: {tehran_datetime()}"
    )

@router.message()
async def handle_payment_proof(message: types.Message):
    text = (message.text or "").lower()
    if "رسید" in text or "شماره پیگیری" in text or "واریز" in text:
        await message.answer(
            "رسید دریافت شد. برای تأیید نهایی، ادمین بررسی می‌کند."
        )
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"پرداخت احتمالی VIP از کاربر {message.from_user.id}
"
                        f"نام: {message.from_user.full_name}
"
                        f"یوزرنیم: @{message.from_user.username or 'none'}
"
                        f"متن: {message.text}"
                    )
                except Exception:
                    pass

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

async def daily_channel_post():
    while True:
        try:
            text = (
                f"📊 گزارش روزانه CryptoPulse
"
                f"⏰ زمان تهران: {tehran_datetime()}
"
                f"✅ ربات فعال است
"
                f"💎 VIP ماهانه: {VIP_PRICE_TOMAN:,} تومان
"
                f"{CHANNEL_USERNAME}"
            )
            await channel_post(text)
        except Exception as e:
            logger.warning(f"channel post error: {e}")
        await asyncio.sleep(24 * 3600)

@app.on_event("startup")
async def on_startup():
    await init_db()
    await bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET, drop_pending_updates=True)
    asyncio.create_task(daily_channel_post())
    logger.info("Webhook set")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()

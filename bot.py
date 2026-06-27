import os
import time
import hmac
import json
import base64
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta, timezone

import aiohttp
import aiosqlite
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.methods import SetWebhook
from groq import Groq

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
COINEX_KEY = os.getenv("COINEX_KEY", "")
COINEX_SECRET = os.getenv("COINEX_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit())
FREE_DAILY_AI_LIMIT = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "2"))

if not BOT_TOKEN or not WEBHOOK_URL or not GROQ_API_KEY:
    raise RuntimeError("BOT_TOKEN, WEBHOOK_URL, GROQ_API_KEY are required")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("vip_bot")

# =========================
# APP OBJECTS
# =========================
app = FastAPI()
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)
groq_client = Groq(api_key=GROQ_API_KEY)

# =========================
# DB
# =========================
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
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    data TEXT,
    created_at INTEGER
);
"""

DB_LOCK = asyncio.Lock()

async def db():
    return await aiosqlite.connect(DATABASE_URL)

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.executescript(CREATE_TABLES)
        await conn.commit()

async def log_action(user_id, action, data=""):
    async with DB_LOCK:
        async with aiosqlite.connect(DATABASE_URL) as conn:
            await conn.execute(
                "INSERT INTO logs(user_id, action, data, created_at) VALUES(?,?,?,?)",
                (user_id, action, data, int(time.time()))
            )
            await conn.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row

async def upsert_user(user_id, username, full_name):
    now = int(time.time())
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute("""
        INSERT INTO users(user_id, username, full_name, created_at)
        VALUES(?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name
        """, (user_id, username, full_name, now))
        await conn.execute("""
        INSERT INTO user_state(user_id, last_ai_at, daily_ai_count, last_reset_day)
        VALUES(?,?,?,?)
        ON CONFLICT(user_id) DO NOTHING
        """, (user_id, 0, 0, datetime.now(timezone.utc).date().isoformat()))
        await conn.commit()

async def set_plan(user_id, plan, days=30):
    until = int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute("UPDATE users SET plan=?, plan_until=? WHERE user_id=?", (plan, until, user_id))
        await conn.execute("INSERT INTO payments(user_id, plan, amount, status, created_at) VALUES(?,?,?,?,?)",
                           (user_id, plan, 0, "manual", int(time.time())))
        await conn.commit()

async def is_premium(user_row):
    if not user_row:
        return False
    plan_until = user_row[5]
    plan = user_row[4]
    return plan in ("vip", "pro", "elite") and int(time.time()) < int(plan_until or 0)

async def reset_daily_if_needed(user_id):
    today = datetime.now(timezone.utc).date().isoformat()
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT last_reset_day FROM user_state WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row:
            await conn.execute("INSERT OR IGNORE INTO user_state(user_id,last_ai_at,daily_ai_count,last_reset_day) VALUES(?,?,?,?)",
                               (user_id, 0, 0, today))
        elif row[0] != today:
            await conn.execute("UPDATE user_state SET daily_ai_count=0,last_reset_day=? WHERE user_id=?", (today, user_id))
        await conn.commit()

async def increase_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute("UPDATE user_state SET daily_ai_count = daily_ai_count + 1, last_ai_at=? WHERE user_id=?",
                           (int(time.time()), user_id))
        await conn.commit()

async def get_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT daily_ai_count FROM user_state WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0

# =========================
# COINEX
# =========================
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

# =========================
# GROQ
# =========================
async def ask_groq(prompt: str, user_profile: str = ""):
    system = (
        "You are a professional Persian crypto trading assistant. "
        "Be concise, practical, risk-aware, and avoid guarantees. "
        "Give structured, high-value analysis."
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

# =========================
# HELPERS
# =========================
def premium_text():
    return (
        "پلن‌ها:
"
        "• Free: 5 سوال AI در روز + هشدار محدود
"
        "• VIP: تحلیل بیشتر + واچ‌لیست + هشدار فوری
"
        "• Pro: AI عمیق + گزارش روزانه + سیگنال‌های بیشتر
"
    )

async def rate_limit_ok(user_id):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT last_ai_at FROM user_state WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        last = row[0] if row else 0
        return (int(time.time()) - int(last)) >= RATE_LIMIT_SECONDS

# =========================
# COMMANDS
# =========================
@router.message(CommandStart())
async def start(message: Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
    user = await get_user(message.from_user.id)
    plan = user[4] if user else "free"
    await message.answer(
        f"سلام {message.from_user.full_name} 👋
"
        f"پلن شما: <b>{plan}</b>

"
        f"این ربات تحلیل، هشدار و ابزار پول‌سازی دارد.
"
        f"{premium_text()}
"
        f"دستورها:
"
        f"/ai سوال
"
        f"/price BTCUSDT
"
        f"/watch BTCUSDT
"
        f"/subscribe vip
"
        f"/me
"
    )
    await log_action(message.from_user.id, "start")

@router.message(Command("me"))
async def me(message: Message):
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
        f"استایل ریسک: <b>{user[3]}</b>
"
        f"AI امروز: <b>{ai_count}</b>
"
    )

@router.message(Command("price"))
async def price(message: Message):
    symbol = (message.text.split(maxsplit=1)[1].strip().upper() if len(message.text.split()) > 1 else "BTCUSDT")
    try:
        data = await coinex_get_ticker(symbol)
        await message.answer(f"داده CoinEx برای <b>{symbol}</b>:
<code>{json.dumps(data, ensure_ascii=False, indent=2)[:3500]}</code>")
        await log_action(message.from_user.id, "price", symbol)
    except Exception as e:
        logger.exception("price error")
        await message.answer(f"خطا در دریافت قیمت: {e}")

@router.message(Command("watch"))
async def watch(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("نمونه: /watch BTCUSDT")
    symbol = parts[1].upper()
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.execute("INSERT INTO watchlists(user_id, symbol, created_at) VALUES(?,?,?)",
                           (message.from_user.id, symbol, int(time.time())))
        await conn.commit()
    await message.answer(f"{symbol} به واچ‌لیست شما اضافه شد.")
    await log_action(message.from_user.id, "watch", symbol)

@router.message(Command("subscribe"))
async def subscribe(message: Message):
    parts = message.text.split()
    plan = parts[1].lower() if len(parts) > 1 else "vip"
    if plan not in ("vip", "pro", "elite"):
        return await message.answer("پلن معتبر: vip / pro / elite")
    await set_plan(message.from_user.id, plan, 30)
    await message.answer(f"پلن شما به <b>{plan}</b> برای 30 روز فعال شد.")
    await log_action(message.from_user.id, "subscribe", plan)

@router.message(Command("ai"))
async def ai_cmd(message: Message):
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

# =========================
# ADMIN
# =========================
@router.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("دسترسی نداری.")
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        cur = await conn.execute("SELECT COUNT(*) FROM payments")
        pays = (await cur.fetchone())[0]
    await message.answer(f"ادمین:
Users: {users}
Payments: {pays}

/usevip USER_ID
/stat")

@router.message(Command("usevip"))
async def usevip(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("دسترسی نداری.")
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.answer("نمونه: /usevip 123456")
    uid = int(parts[1])
    await set_plan(uid, "vip", 30)
    await message.answer(f"کاربر {uid} به VIP ارتقا یافت.")

# =========================
# ALERT WORKER
# =========================
async def alert_worker():
    while True:
        try:
            async with aiosqlite.connect(DATABASE_URL) as conn:
                cur = await conn.execute("SELECT id, user_id, symbol, target_price, alert_type FROM alerts WHERE active=1")
                rows = await cur.fetchall()
            for a_id, user_id, symbol, target_price, alert_type in rows:
                try:
                    data = await coinex_get_ticker(symbol)
                    await bot.send_message(user_id, f"هشدار {symbol}: بررسی قیمت انجام شد.
<code>{json.dumps(data, ensure_ascii=False)[:1500]}</code>")
                except Exception as e:
                    logger.warning(f"alert failed for {user_id}: {e}")
            await asyncio.sleep(60)
        except Exception as e:
            logger.exception(f"worker error {e}")
            await asyncio.sleep(10)

# =========================
# WEBHOOK
# =========================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = await request.json()
    update = aiogram.types.Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await init_db()
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )
    asyncio.create_task(alert_worker())
    logger.info("Bot started")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()

# =========================
# MAIN
# =========================
# Run with: uvicorn bot:app --host 0.0.0.0 --port 8000

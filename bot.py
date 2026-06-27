import os
import time
import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
import aiosqlite
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

try:
    from groq import Groq
except Exception:
    Groq = None

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit())
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
FREE_DAILY_AI_LIMIT = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "2"))
VIP_PRICE_TOMAN = 199000
OWNER_NAME = "فرهاد بهمرد"
OWNER_CARD = "6063731196254479"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("cryptopulse")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)
dp.callback_query.middleware(CallbackAnswerMiddleware())

groq_client = Groq(api_key=GROQ_API_KEY) if Groq and GROQ_API_KEY else None

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
"""

def tehran_now():
    return datetime.now(ZoneInfo("Asia/Tehran"))

def tehran_datetime():
    return tehran_now().strftime("%Y/%m/%d - %H:%M:%S")

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.executescript(CREATE_TABLES)
        await conn.commit()

async def q(sql, params=(), one=False):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute(sql, params)
        if one:
            return await cur.fetchone()
        await conn.commit()

async def log_action(user_id, action, data=""):
    await q(
        "INSERT INTO logs(user_id, action, data, created_at) VALUES(?,?,?,?)",
        (user_id, action, data, int(time.time()))
    )

async def get_user(user_id):
    return await q("SELECT * FROM users WHERE user_id=?", (user_id,), one=True)

async def upsert_user(user_id, username, full_name):
    await q(
        "INSERT INTO users(user_id, username, full_name, created_at) VALUES(?,?,?,?) "
        "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name",
        (user_id, username, full_name, int(time.time()))
    )
    await q(
        "INSERT OR IGNORE INTO user_state(user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES(?,?,?,?)",
        (user_id, 0, 0, tehran_now().date().isoformat())
    )

async def is_premium(user_row):
    return bool(user_row and user_row[5] in ("vip", "pro", "elite") and int(time.time()) < int(user_row[6] or 0))

async def reset_daily_if_needed(user_id):
    today = tehran_now().date().isoformat()
    row = await q("SELECT last_reset_day FROM user_state WHERE user_id=?", (user_id,), one=True)
    if not row:
        await q(
            "INSERT OR IGNORE INTO user_state(user_id,last_ai_at,daily_ai_count,last_reset_day) VALUES(?,?,?,?)",
            (user_id, 0, 0, today)
        )
    elif row[0] != today:
        await q("UPDATE user_state SET daily_ai_count=0,last_reset_day=? WHERE user_id=?", (today, user_id))

async def get_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    row = await q("SELECT daily_ai_count FROM user_state WHERE user_id=?", (user_id,), one=True)
    return row[0] if row else 0

async def increase_ai_count(user_id):
    await reset_daily_if_needed(user_id)
    await q("UPDATE user_state SET daily_ai_count = daily_ai_count + 1, last_ai_at=? WHERE user_id=?", (int(time.time()), user_id))

async def rate_limit_ok(user_id):
    row = await q("SELECT last_ai_at FROM user_state WHERE user_id=?", (user_id,), one=True)
    last = row[0] if row else 0
    return (int(time.time()) - int(last)) >= RATE_LIMIT_SECONDS

async def coinex_get_ticker(symbol="BTCUSDT"):
    url = f"https://api.coinex.com/v2/spot/ticker?market={symbol}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=15) as resp:
            return await resp.json()

async def ask_groq(prompt: str, profile: str = ""):
    if not groq_client:
        return "❌ سرویس AI در دسترس نیست."
    loop = asyncio.get_running_loop()
    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a concise Persian crypto assistant."},
                {"role": "user", "content": f"Profile: {profile}

{prompt}"}
            ],
            temperature=0.3,
        )
    res = await loop.run_in_executor(None, _call)
    return res.choices[0].message.content.strip()

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="price")],
        [InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai")],
        [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_vip")],
        [InlineKeyboardButton(text="👤 پروفایل", callback_data="profile")],
    ])

@router.message(CommandStart())
async def start(message: types.Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
    user = await get_user(message.from_user.id)
    await message.answer(
        f"👋 سلام {message.from_user.full_name}!

"
        f"🕐 زمان تهران: {tehran_datetime()}
"
        f"💎 پلن شما: {user[5] if user else 'free'}
"
        f"📢 کانال: {CHANNEL_USERNAME}
"
        f"💰 VIP: {VIP_PRICE_TOMAN:,} تومان

"
        f"/price BTCUSDT
"
        f"/ai بیت‌کوین را تحلیل کن
"
        f"/buyvip
"
        f"/me",
        reply_markup=main_keyboard()
    )

@router.message(Command("time"))
async def time_cmd(message: types.Message):
    await message.answer(f"🕐 {tehran_datetime()}")

@router.message(Command("me"))
async def me(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ ابتدا /start را بزنید.")
    premium = await is_premium(user)
    ai_count = await get_ai_count(message.from_user.id)
    await message.answer(
        f"👤 پروفایل

"
        f"نام: {user[2]}
"
        f"پلن: {user[5]}
"
        f"پریمیوم: {'بله' if premium else 'خیر'}
"
        f"AI امروز: {ai_count}
"
        f"زمان: {tehran_datetime()}"
    )

@router.message(Command("price"))
async def price(message: types.Message):
    symbol = message.text.split(maxsplit=1)[1].strip().upper() if len(message.text.split()) > 1 else "BTCUSDT"
    try:
        data = await coinex_get_ticker(symbol)
        ticker = (data.get("data") or {})
        await message.answer(
            f"📊 {symbol}
"
            f"آخرین: {ticker.get('last', 'N/A')}
"
            f"باز: {ticker.get('open', 'N/A')}
"
            f"بسته: {ticker.get('close', 'N/A')}
"
            f"بالا: {ticker.get('high', 'N/A')}
"
            f"پایین: {ticker.get('low', 'N/A')}"
        )
    except Exception as e:
        await message.answer(f"❌ خطا در قیمت: {e}")

@router.message(Command("buyvip"))
async def buyvip(message: types.Message):
    await message.answer(
        f"💰 خرید VIP ماهانه

"
        f"مبلغ: <b>{VIP_PRICE_TOMAN:,} تومان</b>
"
        f"نام: <b>{OWNER_NAME}</b>
"
        f"کارت: <code>{OWNER_CARD}</code>

"
        f"✅ رسید را ارسال کن.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 ارسال رسید", callback_data="send_receipt")]
        ])
    )

@router.message(Command("ai"))
async def ai_cmd(message: types.Message):
    prompt = message.text.partition(" ")[2].strip()
    if not prompt:
        return await message.answer("مثال: /ai بیت‌کوین را تحلیل کن")
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ ابتدا /start را بزنید.")
    premium = await is_premium(user)
    count = await get_ai_count(message.from_user.id)
    if not premium and count >= FREE_DAILY_AI_LIMIT:
        return await message.answer("⚠️ سقف AI رایگان امروز پر شده.")
    if not await rate_limit_ok(message.from_user.id):
        return await message.answer("⏳ چند ثانیه صبر کن.")
    await message.answer("🤖 در حال تحلیل...")
    answer = await ask_groq(prompt, f"plan={user[5]}, premium={premium}, risk={user[4]}")
    await increase_ai_count(message.from_user.id)
    await message.answer(answer[:3900])

@router.callback_query(F.data == "price")
async def cb_price(callback: types.CallbackQuery):
    try:
        data = await coinex_get_ticker("BTCUSDT")
        ticker = (data.get("data") or {})
        await callback.message.answer(
            f"📊 BTCUSDT
"
            f"آخرین: {ticker.get('last', 'N/A')}
"
            f"باز: {ticker.get('open', 'N/A')}
"
            f"بسته: {ticker.get('close', 'N/A')}"
        )
    except Exception as e:
        await callback.message.answer(f"❌ خطا: {e}")
    await callback.answer()

@router.callback_query(F.data == "ai")
async def cb_ai(callback: types.CallbackQuery):
    await callback.message.answer("🤖 از /ai استفاده کن و سوالت را بنویس.")
    await callback.answer()

@router.callback_query(F.data == "profile")
async def cb_profile(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("❌ ابتدا /start را بزنید.")
        return await callback.answer()
    premium = await is_premium(user)
    count = await get_ai_count(callback.from_user.id)
    await callback.message.answer(
        f"👤 پروفایل

"
        f"نام: {user[2]}
"
        f"پلن: {user[5]}
"
        f"پریمیوم: {'بله' if premium else 'خیر'}
"
        f"AI امروز: {count}"
    )
    await callback.answer()

@router.callback_query(F.data == "buy_vip")
async def cb_buy_vip(callback: types.CallbackQuery):
    await callback.message.answer(
        f"💰 خرید VIP ماهانه

"
        f"مبلغ: <b>{VIP_PRICE_TOMAN:,} تومان</b>
"
        f"نام: <b>{OWNER_NAME}</b>
"
        f"کارت: <code>{OWNER_CARD}</code>

"
        f"✅ رسید را ارسال کن."
    )
    await callback.answer()

@router.callback_query(F.data == "send_receipt")
async def cb_send_receipt(callback: types.CallbackQuery):
    await callback.message.answer("📤 لطفاً رسید یا شماره پیگیری را به صورت متن ارسال کن.")
    await callback.answer()

@router.message()
async def payment_listener(message: types.Message):
    text = (message.text or "").lower()
    if any(x in text for x in ["رسید", "واریز", "شماره پیگیری", "پرداخت"]):
        await message.answer("✅ رسید دریافت شد. ادمین بررسی می‌کند.")
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"💳 درخواست VIP
کاربر: {message.from_user.full_name}
ID: {message.from_user.id}
متن: {message.text[:300]}"
                )
            except Exception:
                pass

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

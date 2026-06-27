import time
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import upsert_user, get_user, is_premium, q, tehran_now
from services.coinex_service import get_ticker
from services.groq_service import ask_groq
from services.payment_service import vip_text, vip_keyboard
from config import FREE_DAILY_AI_LIMIT, RATE_LIMIT_SECONDS, CHANNEL_USERNAME

router = Router()

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="price")],
        [InlineKeyboardButton(text="🤖 تحلیل AI", callback_data="ai")],
        [InlineKeyboardButton(text="💰 خرید VIP", callback_data="buy_vip")],
        [InlineKeyboardButton(text="👤 پروفایل", callback_data="profile")],
    ])

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
    await q(
        "UPDATE user_state SET daily_ai_count = daily_ai_count + 1, last_ai_at=? WHERE user_id=?",
        (int(time.time()), user_id)
    )

async def rate_limit_ok(user_id):
    row = await q("SELECT last_ai_at FROM user_state WHERE user_id=?", (user_id,), one=True)
    last = row[0] if row else 0
    return (int(time.time()) - int(last)) >= RATE_LIMIT_SECONDS

@router.message(CommandStart())
async def start(message: types.Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name or "")
    user = await get_user(message.from_user.id)
    await message.answer(
        f"👋 سلام {message.from_user.full_name}!

"
        f"🕐 زمان تهران: <b>{tehran_now().strftime('%Y/%m/%d - %H:%M:%S')}</b>
"
        f"💎 پلن شما: <b>{user[5] if user else 'free'}</b>
"
        f"📢 کانال: {CHANNEL_USERNAME}

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
    await message.answer(f"🕐 {tehran_now().strftime('%Y/%m/%d - %H:%M:%S')}")

@router.message(Command("me"))
async def me(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ ابتدا /start را بزنید.")
    premium = await is_premium(user)
    ai_count = await get_ai_count(message.from_user.id)
    await message.answer(
        f"👤 پروفایل

نام: {user[2]}
پلن: {user[5]}
پریمیوم: {'بله' if premium else 'خیر'}
AI امروز: {ai_count}"
    )

@router.message(Command("price"))
async def price(message: types.Message):
    symbol = message.text.split(maxsplit=1)[1].strip().upper() if len(message.text.split()) > 1 else "BTCUSDT"
    data = await get_ticker(symbol)
    ticker = data.get("data") or {}
    await message.answer(
        f"📊 {symbol}
"
        f"آخرین: {ticker.get('last', 'N/A')}
"
        f"باز: {ticker.get('open', 'N/A')}
"
        f"بسته: {ticker.get('close', 'N/A')}
"
        f"بیشترین: {ticker.get('high', 'N/A')}
"
        f"کمترین: {ticker.get('low', 'N/A')}"
    )

@router.message(Command("buyvip"))
async def buyvip(message: types.Message):
    await message.answer(vip_text(), reply_markup=vip_keyboard())

@router.message(Command("ai"))
async def ai_cmd(message: types.Message):
    prompt = message.text.partition(" ")[2].strip()
    if not prompt:
        return await message.answer("مثال: /ai بیت‌کوین را تحلیل کن")
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ ابتدا /s

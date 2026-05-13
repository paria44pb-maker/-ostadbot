import os
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx

from nobitex_api import get_balance, place_order, get_market_price

# تنظیمات اولیه
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("توکن تلگرام در متغیر محیطی TELEGRAM_BOT_TOKEN تعریف نشده است!")

app = FastAPI()

# لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# مدل پیام تلگرام
class TelegramUpdate(BaseModel):
    update_id: int
    message: dict = None
    edited_message: dict = None
    callback_query: dict = None

# توابع کمکی
async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            logging.error(f"ارسال پیام به {chat_id} ناموفق: {resp.text}")
        else:
            logging.info(f"پیام به {chat_id} ارسال شد.")

def ai_analysis():
    # نمونه تحلیل AI ساده
    return "📈 سیگنال فعلی: روند بازار مثبت و خرید پیشنهاد می‌شود."

# مدیریت دستورات ربات
async def handle_command(chat_id: int, text: str):
    lower_text = text.strip().lower()

    if lower_text == "/start":
        await send_message(chat_id, "سلام! من ربات ترید شما هستم. برای راهنمایی /help را ارسال کن.")
    elif lower_text == "/help":
        help_msg = (
            "دستورات من:\n"
            "/balance - مشاهده موجودی کیف پول\n"
            "/price - مشاهده قیمت بیت‌کوین\n"
            "/buy <مقدار> - خرید بیت‌کوین\n"
            "/sell <مقدار> - فروش بیت‌کوین\n"
            "/ai - دریافت سیگنال بازار"
        )
        await send_message(chat_id, help_msg)
    elif lower_text == "/balance":
        balances = get_balance()
        if balances:
            msg = "موجودی‌های شما:\n" + "\n".join(f"{cur}: {amt}" for cur, amt in balances.items())
        else:
            msg = "خطا در دریافت موجودی."
        await send_message(chat_id, msg)
    elif lower_text.startswith("/price"):
        price = get_market_price("BTCUSDT")
        if price is not None:
            msg = f"قیمت لحظه‌ای بیت‌کوین: {price:.2f} USDT"
        else:
            msg = "خطا در دریافت قیمت."
        await send_message(chat_id, msg)
    elif lower_text.startswith("/buy"):
        parts = text.split()
        if len(parts) != 2 or not parts[1].replace('.', '', 1).isdigit():
            await send_message(chat_id, "لطفاً دستور را به شکل صحیح بفرستید: /buy مقدار")
            return
        amount = float(parts[1])
        result = place_order("buy", "BTCUSDT", amount)
        if result:
            await send_message(chat_id, f"سفارش خرید به مقدار {amount} BTC ثبت شد.\nنتیجه:\n{result}")
        else:
            await send_message(chat_id, "خطا در ثبت سفارش خرید.")
    elif lower_text.startswith("/sell"):
        parts = text.split()
        if len(parts) != 2 or not parts[1].replace('.', '', 1).isdigit():
            await send_message(chat_id, "لطفاً دستور را به شکل صحیح بفرستید: /sell مقدار")
            return
        amount = float(parts[1])
        result = place_order("sell", "BTCUSDT", amount)
        if result:
            await send_message(chat_id, f"سفارش فروش به مقدار {amount} BTC ثبت شد.\nنتیجه:\n{result}")
        else:
            await send_message(chat_id, "خطا در ثبت سفارش فروش.")
    elif lower_text == "/ai":
        signal = ai_analysis()
        await send_message(chat_id, signal)
    else:
        await send_message(chat_id, "دستور ناشناخته، لطفاً /help را برای راهنمایی ارسال کنید.")

# اینجا نقطه ورود وب‌هوک تلگرام
@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    message = update.message or update.edited_message
    if message is None:
        logging.info("پیام خالی دریافت شد.")
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    logging.info(f"پیام دریافت شد از {chat_id}: {text}")

    await handle_command(chat_id, text)
    return {"ok": True}

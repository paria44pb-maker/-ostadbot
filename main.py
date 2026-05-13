import os
import logging
import requests
import sqlite3
from datetime import datetime

from fastapi import FastAPI, Request
from dotenv import load_dotenv

# =========================
# بارگذاری متغیرهای محیطی
# =========================
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("متغیر محیطی TELEGRAM_BOT_TOKEN تعریف نشده است")

if not NOBITEX_API_KEY:
    raise ValueError("متغیر محیطی NOBITEX_API_KEY تعریف نشده است")

# =========================
# پیکربندی FastAPI و Logger
# =========================
app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# =========================
# ثابت‌ها و آدرس‌ها
# =========================
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
NOBITEX_BASE_URL = "https://api.nobitex.ir"
NOBITEX_HEADERS = {
    "Authorization": f"Token {NOBITEX_API_KEY}",
    "Content-Type": "application/json"
}

# =========================
# دیتابیس SQLite
# =========================
DB_NAME = "bot.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    joined_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    side TEXT,
    symbol TEXT,
    amount REAL,
    created_at TEXT
)
""")

conn.commit()

# =========================
# ارسال پیام به تلگرام
# =========================
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"خطا در ارسال پیام به تلگرام: {e}")

# =========================
# ذخیره کاربر در دیتابیس
# =========================
def save_user(chat_id, username, first_name):
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (chat_id, username, first_name, joined_at)
    VALUES (?, ?, ?, ?)
    """, (
        chat_id,
        username,
        first_name,
        datetime.utcnow().isoformat()
    ))
    conn.commit()

# =========================
# دریافت قیمت لحظه‌ای از نوبیتکس
# =========================
def get_market_price(symbol="BTCUSDT"):
    try:
        src = symbol.replace("USDT", "").lower()
        url = f"{NOBITEX_BASE_URL}/market/stats"
        response = requests.post(url, json={"srcCurrency": src, "dstCurrency": "usdt"})
        response.raise_for_status()
        data = response.json()
        stats = data.get("stats", {})
        pair = f"{src}-usdt"
        if pair not in stats:
            return None
        return stats[pair]["latest"]
    except Exception as e:
        logger.error(f"خطا در دریافت قیمت: {e}")
        return None

# =========================
# دریافت موجودی کیف پول‌ها
# =========================
def get_balance():
    try:
        url = f"{NOBITEX_BASE_URL}/users/wallets/list"
        response = requests.get(url, headers=NOBITEX_HEADERS)
        response.raise_for_status()
        data = response.json()
        wallets = data.get("wallets", [])
        balances = []
        for wallet in wallets:
            balance = float(wallet.get("balance", 0))
            if balance > 0:
                balances.append(f"{wallet.get('currency').upper()}: {balance}")
        if not balances:
            return "موجودی کیف پول‌ها خالی است."
        return "\n".join(balances)
    except Exception as e:
        logger.error(f"خطا در دریافت موجودی: {e}")
        return "خطا در دریافت موجودی کیف پول‌ها."

# =========================
# ثبت سفارش خرید/فروش
# =========================
def place_order(side, symbol, amount):
    try:
        src = symbol.replace("USDT", "").lower()
        url = f"{NOBITEX_BASE_URL}/market/orders/add"
        payload = {
            "type": side,
            "srcCurrency": src,
            "dstCurrency": "usdt",
            "amount": str(amount),
            "execution": "market"
        }
        response = requests.post(url, headers=NOBITEX_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"خطا در ثبت سفارش: {e}")
        return None

# =========================
# تحلیل ساده AI بازار
# =========================
def ai_analysis(symbol="BTCUSDT"):
    price = get_market_price(symbol)
    if not price:
        return "تحلیل بازار در دسترس نیست."
    price = float(price)
    if price > 100000:
        signal = "خرید پیشنهادی 🚀"
    else:
        signal = "نگهداری ⏳"
    return f"""
📊 تحلیل هوشمند بازار

نماد: {symbol}
قیمت فعلی: {price}
سیگنال: {signal}
سطح ریسک: متوسط
"""

# =========================
# پردازش دستورات خرید و فروش
# =========================
def handle_trade(text, side, chat_id):
    parts = text.split()
    if len(parts) != 3:
        return f"فرمت درست:\n/{side} BTCUSDT 0.001"
    _, symbol, amount_str = parts
    try:
        amount = float(amount_str)
    except ValueError:
        return "مقدار وارد شده معتبر نیست."
    result = place_order(side, symbol, amount)
    if not result:
        return "خطا در ثبت سفارش."
    cursor.execute("""
    INSERT INTO trades (chat_id, side, symbol, amount, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (chat_id, side, symbol, amount, datetime.utcnow().isoformat()))
    conn.commit()
    return f"""
✅ سفارش شما ثبت شد

نوع سفارش: {side.upper()}
نماد: {symbol}
مقدار: {amount}
"""

# =========================
# مدیریت دستورات ربات
# =========================
def handle_command(text, chat_id):
    text = text.strip()
    if text == "/start":
        return """
🎉 ربات هوشمند ترید راه‌اندازی شد.

دستورات قابل استفاده:
/balance - نمایش موجودی کیف پول
/price SYMBOL - قیمت لحظه‌ای نماد (مثلاً /price BTCUSDT)
/buy SYMBOL AMOUNT - خرید
/sell SYMBOL AMOUNT - فروش
/ai SYMBOL - تحلیل هوشمند بازار
/help - راهنما
"""
    elif text == "/help":
        return """
راهنما:

/balance - مشاهده موجودی کیف پول
/price SYMBOL - دریافت قیمت لحظه‌ای نماد
/buy SYMBOL AMOUNT - ثبت سفارش خرید
/sell SYMBOL AMOUNT - ثبت سفارش فروش
/ai SYMBOL - تحلیل هوشمند بازار
"""
    elif text == "/balance":
        return get_balance()
    elif text.startswith("/price"):
        parts = text.split()
        if len(parts) != 2:
            return "فرمت دستور:\n/price BTCUSDT"
        symbol = parts[1]
        price = get_market_price(symbol)
        if not price:
            return "قیمت دریافت نشد."
        return f"💰 قیمت {symbol}: {price} USDT"
    elif text.startswith("/buy"):
        return handle_trade(text, "buy", chat_id)
    elif text.startswith("/sell"):
        return handle_trade(text, "sell", chat_id)
    elif text.startswith("/ai"):
        parts = text.split()
        if len(parts) != 2:
            return "فرمت دستور:\n/ai BTCUSDT"
        symbol = parts[1]
        return ai_analysis(symbol)
    else:
        return "دستور ناشناخته است."

# =========================
# مسیر Webhook تلگرام
# =========================
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(data)
        message = data.get("message")
        if not message:
            return {"ok": True}

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")
        username = chat.get("username", "")
        first_name = chat.get("first_name", "")

        logger.info(f"پیام از {chat_id}: {text}")

        save_user(chat_id, username, first_name)

        response_text = handle_command(text, chat_id)

        send_message(chat_id, response_text)

        return {"ok": True}

    except Exception as e:
        logger.error(f"خطا در webhook: {e}")
        return {"ok": False}

# =========================
# مسیر ریشه برای مانیتورینگ
# =========================
@app.get("/")
async def root():
    return {
        "status": "running",
        "bot": "active",
        "server": "online"
    }

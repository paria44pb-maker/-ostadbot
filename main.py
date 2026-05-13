import os
import logging
import requests
import sqlite3
from datetime import datetime

from fastapi import FastAPI, Request
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found")

if not NOBITEX_API_KEY:
    raise ValueError("NOBITEX_API_KEY not found")

# =========================
# APP
# =========================

app = FastAPI()

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =========================
# TELEGRAM
# =========================

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# =========================
# NOBITEX
# =========================

NOBITEX_BASE_URL = "https://api.nobitex.ir"

NOBITEX_HEADERS = {
    "Authorization": f"Token {NOBITEX_API_KEY}",
    "Content-Type": "application/json"
}

# =========================
# DATABASE
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
# TELEGRAM SEND MESSAGE
# =========================

def send_message(chat_id, text):

    url = f"{TELEGRAM_API}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        logger.error(f"Telegram send error: {response.text}")

# =========================
# SAVE USER
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
# GET MARKET PRICE
# =========================

def get_market_price(symbol="BTCUSDT"):

    try:

        src = symbol.replace("USDT", "").lower()

        url = f"{NOBITEX_BASE_URL}/market/stats"

        payload = {
            "srcCurrency": src,
            "dstCurrency": "usdt"
        }

        response = requests.post(
            url,
            json=payload
        )

        data = response.json()

        stats = data.get("stats", {})

        pair = f"{src}-usdt"

        if pair not in stats:
            return None

        latest = stats[pair]["latest"]

        return latest

    except Exception as e:
        logger.error(f"Price error: {e}")
        return None

# =========================
# GET BALANCE
# =========================

def get_balance():

    try:

        url = f"{NOBITEX_BASE_URL}/users/wallets/list"

        response = requests.get(
            url,
            headers=NOBITEX_HEADERS
        )

        data = response.json()

        if response.status_code != 200:
            logger.error(data)
            return "خطا در دریافت موجودی"

        wallets = data.get("wallets", [])

        result = []

        for wallet in wallets:

            balance = float(wallet["balance"])

            if balance > 0:

                currency = wallet["currency"].upper()

                result.append(
                    f"{currency}: {balance}"
                )

        if not result:
            return "موجودی خالی است"

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Balance error: {e}")
        return "خطا در دریافت موجودی"

# =========================
# PLACE ORDER
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

        response = requests.post(
            url,
            headers=NOBITEX_HEADERS,
            json=payload
        )

        data = response.json()

        logger.info(data)

        return data

    except Exception as e:
        logger.error(f"Order error: {e}")
        return None

# =========================
# AI ANALYSIS
# =========================

def ai_analysis(symbol="BTCUSDT"):

    price = get_market_price(symbol)

    if not price:
        return "تحلیل در دسترس نیست"

    price = float(price)

    if price > 100000:
        signal = "BUY 🚀"
    else:
        signal = "HOLD ⏳"

    return f"""
📊 AI Market Analysis

Symbol: {symbol}

Current Price: {price}

Signal: {signal}

Risk Level: Medium
"""

# =========================
# TRADE COMMAND
# =========================

def handle_trade(text, side, chat_id):

    parts = text.split()

    if len(parts) != 3:
        return f"""
فرمت صحیح:

/{side} BTCUSDT 0.001
"""

    _, symbol, amount_text = parts

    try:
        amount = float(amount_text)

    except:
        return "مقدار وارد شده نامعتبر است"

    result = place_order(side, symbol, amount)

    if not result:
        return "خطا در ثبت سفارش"

    cursor.execute("""
    INSERT INTO trades
    (chat_id, side, symbol, amount, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        chat_id,
        side,
        symbol,
        amount,
        datetime.utcnow().isoformat()
    ))

    conn.commit()

    return f"""
✅ سفارش ثبت شد

Type: {side.upper()}
Symbol: {symbol}
Amount: {amount}
"""

# =========================
# COMMAND HANDLER
# =========================

def handle_command(text, chat_id):

    text = text.strip()

    # START

    if text == "/start":

        return """
🤖 ربات ترید هوشمند فعال شد

دستورات:

/balance
/price BTCUSDT
/buy BTCUSDT 0.001
/sell BTCUSDT 0.001
/ai BTCUSDT
/help
"""

    # HELP

    elif text == "/help":

        return """
📚 راهنما

/balance
نمایش موجودی

/price BTCUSDT
قیمت لحظه‌ای

/buy BTCUSDT 0.001
خرید

/sell BTCUSDT 0.001
فروش

/ai BTCUSDT
تحلیل هوشمند بازار
"""

    # BALANCE

    elif text == "/balance":

        return get_balance()

    # PRICE

    elif text.startswith("/price"):

        parts = text.split()

        if len(parts) != 2:
            return "/price BTCUSDT"

        symbol = parts[1]

        price = get_market_price(symbol)

        if not price:
            return "قیمت دریافت نشد"

        return f"""
💰 Price

Symbol: {symbol}

Price: {price} USDT
"""

    # BUY

    elif text.startswith("/buy"):

        return handle_trade(text, "buy", chat_id)

    # SELL

    elif text.startswith("/sell"):

        return handle_trade(text, "sell", chat_id)

    # AI

    elif text.startswith("/ai"):

        parts = text.split()

        if len(parts) != 2:
            return "/ai BTCUSDT"

        symbol = parts[1]

        return ai_analysis(symbol)

    # UNKNOWN

    else:

        return "دستور ناشناخته است"

# =========================
# WEBHOOK
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

        logger.info(
            f"Message from {chat_id}: {text}"
        )

        # SAVE USER

        save_user(
            chat_id,
            username,
            first_name
        )

        # HANDLE COMMAND

        response = handle_command(
            text,
            chat_id
        )

        # SEND MESSAGE

        send_message(
            chat_id,
            response
        )

        return {"ok": True}

    except Exception as e:

        logger.error(f"Webhook error: {e}")

        return {"ok": False}

# =========================
# ROOT
# =========================

@app.get("/")
async def root():

    return {
        "status": "running",
        "bot": "active",
        "server": "online"
    }
